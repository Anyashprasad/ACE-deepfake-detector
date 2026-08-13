from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
from PIL import Image

from .contracts import CLASS_TO_ID, FORBIDDEN_DEVELOPMENT_SOURCES, ensure_under_directory

REQUIRED_COLUMNS = {
    "sample_id", "path", "local_path", "local_valid", "sha256", "phash", "phash_version",
    "local_sha256", "local_phash", "local_phash_version", "class_name", "source_dataset", "split",
    "family_id", "generator_or_method", "locality_target", "reliability_target", "reliability_basis",
}
HELDOUT_GENERATORS = {"sd_1_5", "midjourney", "vqdm"}
PHASH_VERSION = "ahash64-v1"


def canonical_generator(value: str) -> str:
    compact = "".join(ch for ch in value.lower() if ch.isalnum())
    aliases = {"sd15": "sd_1_5", "stablediffusion15": "sd_1_5",
               "midjourney": "midjourney", "vqdm": "vqdm"}
    return aliases.get(compact, compact)


def phash_distance(left: str, right: str) -> int:
    return (int(left, 16) ^ int(right, 16)).bit_count()


def file_sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def perceptual_hash(path: str) -> str:
    with Image.open(path) as image:
        pixels = list(image.convert("L").resize((8, 8), Image.Resampling.LANCZOS).getdata())
    mean = sum(pixels) / len(pixels)
    value = sum((pixel >= mean) << (63 - index) for index, pixel in enumerate(pixels))
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
    right_hashes = list(validation["phash"]) + list(validation["local_phash"])
    for left_hash in list(train["phash"]) + list(train["local_phash"]):
        if any(phash_distance(left_hash, right_hash) <= 4 for right_hash in right_hashes):
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
                  training: bool, seed: int, num_parallel_calls=-1, cache=False, include_ids=False):
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
        image = tf.image.resize(image, [image_size, image_size], antialias=True)
        return tf.cast(image, tf.float32) / 127.5 - 1.0

    def decode(sample_id, path, local_path, local_valid, label, local, reliable):
        targets = {
            "class_probs": tf.one_hot(label, 3, dtype=tf.float32),
            "locality": tf.reshape(tf.cast(local, tf.float32), [1]),
            "reliability": tf.reshape(tf.cast(reliable, tf.float32), [1]),
        }
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
