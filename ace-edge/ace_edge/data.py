from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import numpy as np
from PIL import Image
from scipy.fft import dctn

from .contracts import CLASS_TO_ID, FORBIDDEN_DEVELOPMENT_SOURCES, ensure_under_directory

REQUIRED_COLUMNS = {
    "sample_id", "path", "local_path", "local_valid", "sha256", "phash", "phash_version",
    "local_sha256", "local_phash", "local_phash_version", "class_name", "source_dataset", "split",
    "family_id", "generator_or_method", "locality_target", "reliability_target", "reliability_basis",
}
HELDOUT_GENERATORS = {"sd_1_5", "midjourney", "vqdm"}
PHASH_VERSION = "phash64-v1"


def canonical_generator(value: str) -> str:
    compact = "".join(ch for ch in value.lower() if ch.isalnum())
    aliases = {"sd15": "sd_1_5", "stablediffusion15": "sd_1_5",
               "midjourney": "midjourney", "vqdm": "vqdm"}
    return aliases.get(compact, compact)


def phash_distance(left: str, right: str) -> int:
    return (int(left, 16) ^ int(right, 16)).bit_count()


class _HammingBKTree:
    """Metric index for exact radius searches over 64-bit perceptual hashes."""

    def __init__(self, values):
        self.root = None
        for value in dict.fromkeys(values):
            self.add(value)

    def add(self, value):
        if self.root is None:
            self.root = [value, {}]
            return
        node = self.root
        while True:
            distance = phash_distance(value, node[0])
            child = node[1].get(distance)
            if child is None:
                node[1][distance] = [value, {}]
                return
            node = child

    def has_within(self, value, radius):
        if self.root is None:
            return False
        pending = [self.root]
        while pending:
            node = pending.pop()
            distance = phash_distance(value, node[0])
            if distance <= radius:
                return True
            low, high = distance - radius, distance + radius
            pending.extend(child for edge, child in node[1].items() if low <= edge <= high)
        return False


class _HammingRadiusFourIndex:
    """Exact radius-4 index using five disjoint bit chunks.

    Two 64-bit values at Hamming distance <=4 must share at least one of five
    chunks, so candidate generation is lossless and much faster on dense sets.
    """

    _WIDTHS = (13, 13, 13, 13, 12)

    def __init__(self, values):
        from collections import defaultdict
        remaining = 64
        self.chunks = []
        for width in self._WIDTHS:
            remaining -= width
            self.chunks.append((remaining, (1 << width) - 1))
        self.values = [int(value, 16) for value in dict.fromkeys(values)]
        self.indices = [defaultdict(list) for _ in self.chunks]
        for index, value in enumerate(self.values):
            for chunk_index, (shift, mask) in enumerate(self.chunks):
                self.indices[chunk_index][(value >> shift) & mask].append(index)

    def has_within(self, value, radius=4):
        if radius != 4:
            raise ValueError("This exact index is specialized for radius 4")
        integer = int(value, 16)
        candidates = set()
        for index, (shift, mask) in enumerate(self.chunks):
            candidates.update(self.indices[index].get((integer >> shift) & mask, ()))
        return any((integer ^ self.values[index]).bit_count() <= radius for index in candidates)


def file_sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def perceptual_hash(path: str) -> str:
    with Image.open(path) as image:
        pixels = np.asarray(image.convert("L").resize((32, 32), Image.Resampling.LANCZOS), dtype=np.float32)
    low = dctn(pixels, norm="ortho")[:8, :8].reshape(-1)
    median = np.median(low[1:])
    value = sum((coefficient >= median) << (63 - index) for index, coefficient in enumerate(low))
    return f"{value:016x}"


def verify_manifest_content(frame: pd.DataFrame, raw_manifest_sha256: str) -> dict:
    if set(frame["phash_version"]) != {PHASH_VERSION} or set(frame["local_phash_version"]) != {PHASH_VERSION}:
        raise ValueError(f"Manifest must use {PHASH_VERSION}")
    mismatches = []
    for row in frame.itertuples(index=False):
        actual_sha, actual_phash = file_sha256(row.path), perceptual_hash(row.path)
        actual_local_sha, actual_local_phash = file_sha256(row.local_path), perceptual_hash(row.local_path)
        alias_ok = (not row.local_valid and row.local_sha256 == row.sha256 and row.local_phash == row.phash)
        local_ok = (actual_local_sha.lower() == row.local_sha256.lower() and
                    actual_local_phash.lower() == row.local_phash.lower() and
                    (bool(row.local_valid) or alias_ok))
        if actual_sha.lower() != row.sha256.lower() or actual_phash.lower() != row.phash.lower() or not local_ok:
            mismatches.append(row.sample_id)
    report = {"raw_manifest_sha256": raw_manifest_sha256, "samples": len(frame),
              "verified": len(frame) - len(mismatches), "mismatches": mismatches[:100],
              "mismatch_count": len(mismatches), "phash_version": PHASH_VERSION}
    if mismatches:
        raise ValueError(f"Mounted-content integrity failed for {len(mismatches)} samples")
    return report


def load_manifest(path: str, expected_split: str) -> pd.DataFrame:
    ensure_under_directory(path)
    frame = pd.read_csv(path, keep_default_na=False)
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"Manifest {path} lacks columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError(f"Manifest {path} is empty")
    if set(frame["split"]) != {expected_split}:
        raise ValueError(f"Expected only split={expected_split!r}")
    unknown = set(frame["class_name"]) - set(CLASS_TO_ID)
    if unknown:
        raise ValueError(f"Unknown classes: {sorted(unknown)}")
    forbidden = {v.lower() for v in frame["source_dataset"]} & FORBIDDEN_DEVELOPMENT_SOURCES
    if forbidden:
        raise ValueError(f"Frozen external source present in development manifest: {forbidden}")
    normalized_generators = {canonical_generator(v) for v in frame["generator_or_method"]}
    development_splits = {"train", "validation", "calibration"}
    if expected_split in development_splits and normalized_generators & HELDOUT_GENERATORS:
        raise ValueError("Held-out generator present in fitting/calibration manifest")
    if expected_split == "unseen_generator_test":
        if not set(frame["class_name"]) <= {"likely_real", "ai_generated"}:
            raise ValueError("Unseen-generator test is binary likely-real versus AI-generated")
        synthetic = frame.loc[frame["class_name"] == "ai_generated", "generator_or_method"]
        if not {canonical_generator(v) for v in synthetic} <= HELDOUT_GENERATORS:
            raise ValueError("Synthetic unseen-generator rows must use held-out generators")
    if frame["sample_id"].duplicated().any():
        raise ValueError("sample_id must be unique within each manifest")
    missing_files = [p for column in ("path", "local_path") for p in frame[column] if not Path(p).is_file()]
    if missing_files:
        raise FileNotFoundError(f"Missing {len(missing_files)} mounted files; first={missing_files[0]}")
    frame = frame.copy()
    invalid_local = frame["local_valid"].astype(float).eq(0)
    if (frame.loc[invalid_local, "locality_target"].astype(float) != 0).any():
        raise ValueError("Missing local evidence must have locality_target=0")
    if (frame.loc[invalid_local, "local_path"] != frame.loc[invalid_local, "path"]).any():
        raise ValueError("local_valid=0 requires local_path=path as an explicit neutral fallback")
    frame["class_id"] = frame["class_name"].map(CLASS_TO_ID).astype("int32")
    return frame.sort_values("sample_id", kind="stable").reset_index(drop=True)


def assert_independent(train: pd.DataFrame, validation: pd.DataFrame) -> None:
    for column in ("sample_id", "family_id"):
        overlap = set(train[column]) & set(validation[column]) - {""}
        if overlap:
            raise ValueError(f"Train/validation {column} overlap: {len(overlap)} values")
    left_exact=set(train["sha256"])|set(train["local_sha256"])
    right_exact=set(validation["sha256"])|set(validation["local_sha256"])
    overlap = left_exact & right_exact - {""}
    if overlap:
        raise ValueError(f"Exact content leakage: {len(overlap)} hashes")
    versions = set(train["phash_version"]) | set(validation["phash_version"])
    if versions != {"phash64-v1"}:
        raise ValueError(
            "Production perceptual-leakage gating requires phash64-v1; "
            f"found {sorted(versions)}. ahash64-v1 is diagnostic-only."
        )
    right_hashes = list(validation["phash"]) + list(validation["local_phash"])
    right_tree = _HammingRadiusFourIndex(right_hashes)
    for left_hash in dict.fromkeys(list(train["phash"]) + list(train["local_phash"])):
        if right_tree.has_within(left_hash, 4):
            raise ValueError("Perceptual content leakage within Hamming distance <=4")


def assert_all_splits_independent(splits: dict[str, pd.DataFrame]) -> None:
    names = sorted(splits)
    for index, left in enumerate(names):
        for right in names[index + 1:]:
            assert_independent(splits[left], splits[right])


def manifest_digest(frame: pd.DataFrame) -> str:
    columns = sorted(frame.columns)
    return hashlib.sha256(frame[columns].to_csv(index=False).encode()).hexdigest()


def raw_manifest_digest(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_dataset(tf, frame: pd.DataFrame, image_size: int, global_batch_size: int,
                  training: bool, seed: int, num_parallel_calls=-1, cache=False, include_ids=False,
                  baseline_only=True, training_augmentation: bool = False,
                  include_binary_target: bool = False):
    paths = frame["path"].astype(str).to_numpy()
    local_paths = frame["local_path"].astype(str).to_numpy()
    local_valid = frame["local_valid"].astype("float32").to_numpy()
    labels = frame["class_id"].to_numpy("int32")
    locality = frame["locality_target"].astype("float32").to_numpy()
    reliability = frame["reliability_target"].astype("float32").to_numpy()
    sample_ids = frame["sample_id"].astype(str).to_numpy()
    tensors = (sample_ids, paths, local_paths, local_valid, labels, locality, reliability)
    if training:
        # Equal-probability source/class streams stop large corpora dominating.
        streams = []
        for _, group in frame.groupby(["source_dataset", "class_name"], sort=True):
            idx = group.index.to_numpy()
            streams.append(tf.data.Dataset.from_tensor_slices(tuple(v[idx] for v in tensors)).shuffle(
                len(idx), seed=seed, reshuffle_each_iteration=True).repeat())
        ds = tf.data.Dataset.sample_from_datasets(streams, seed=seed, stop_on_empty_dataset=False)
    else:
        ds = tf.data.Dataset.from_tensor_slices(tensors)

    autotune = tf.data.AUTOTUNE if num_parallel_calls == -1 else num_parallel_calls

    def decode_one(path):
        image = tf.io.decode_image(tf.io.read_file(path), channels=3, expand_animations=False)
        image.set_shape([None, None, 3])
        if training and training_augmentation:
            # Conservative, isolated augmentations:
            image = tf.image.random_flip_left_right(image, seed=seed)
            image = tf.image.random_brightness(image, max_delta=12, seed=seed)
            image = tf.image.random_contrast(image, lower=0.95, upper=1.05, seed=seed)
            image = tf.image.random_jpeg_quality(image, min_jpeg_quality=80, max_jpeg_quality=100, seed=seed)
        image = tf.image.resize(image, [image_size, image_size], antialias=True)
        image = tf.clip_by_value(image, 0.0, 255.0)
        return tf.cast(image, tf.float32) / 127.5 - 1.0

    def decode(sample_id, path, local_path, local_valid, label, local, reliable):
        targets = {"class_probs": tf.one_hot(label, 3, dtype=tf.float32)}
        if include_binary_target:
            is_synthetic = tf.cast(label > 0, tf.float32)
            targets["binary_prob"] = tf.reshape(is_synthetic, [1])
        if not baseline_only:
            targets.update({
                "locality": tf.reshape(tf.cast(local, tf.float32), [1]),
                "reliability": tf.reshape(tf.cast(reliability, tf.float32), [1]),
            })
        inputs = {"global_image": decode_one(path), "local_image": decode_one(local_path),
                  "local_valid": tf.reshape(local_valid, [1])}
        return (sample_id, inputs, targets) if include_ids else (inputs, targets)

    ds = ds.map(decode, num_parallel_calls=autotune, deterministic=True)
    if cache:
        ds = ds.cache()
    ds = ds.batch(global_batch_size, drop_remainder=training)
    options = tf.data.Options()
    options.experimental_distribute.auto_shard_policy = tf.data.experimental.AutoShardPolicy.DATA
    options.deterministic = True
    return ds.with_options(options).prefetch(tf.data.AUTOTUNE)
