from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

LABELS = ("likely_real", "ai_generated", "face_manipulated")
SPLITS = {"train", "validation", "calibration", "internal_test", "external_test"}
FIT_SPLITS = {"train", "validation", "calibration"}
HELD_OUT_GENERATORS = {"sd15", "midjourney", "vqdm"}
MIB = 1024 * 1024


class ReviewError(ValueError):
    pass


def _norm(value: Any) -> str:
    return str(value or "").strip().lower().replace(" ", "").replace("_", "").replace("-", "").replace(".", "")


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_rows(path: str | Path) -> list[dict[str, str]]:
    path = Path(path)
    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_contract(contract: dict[str, Any]) -> None:
    if tuple(contract.get("class_order", ())) != LABELS:
        raise ReviewError(f"class_order must be exactly {LABELS}")
    if contract.get("inconclusive_semantics") != "abstention":
        raise ReviewError("inconclusive must be an abstention decision, not a learned class")
    if contract.get("probability_semantics") != "softmax_p_class":
        raise ReviewError("probability_semantics must be softmax_p_class")


def hamming_hex(left: str, right: str) -> int:
    if len(left) != len(right) or not left:
        raise ReviewError("pHash values must be nonempty equal-length hexadecimal strings")
    try:
        return (int(left, 16) ^ int(right, 16)).bit_count()
    except ValueError as exc:
        raise ReviewError("pHash values must be hexadecimal") from exc


class _BKNode:
    def __init__(self, sample_id: str, value: str) -> None:
        self.sample_id, self.value = sample_id, value
        self.children: dict[int, "_BKNode"] = {}

    def add(self, sample_id: str, value: str) -> None:
        distance = hamming_hex(value, self.value)
        child = self.children.get(distance)
        if child is None:
            self.children[distance] = _BKNode(sample_id, value)
        else:
            child.add(sample_id, value)

    def find(self, value: str, radius: int) -> tuple[str, int] | None:
        distance = hamming_hex(value, self.value)
        if distance <= radius:
            return self.sample_id, distance
        for edge, child in self.children.items():
            if distance - radius <= edge <= distance + radius:
                match = child.find(value, radius)
                if match:
                    return match
        return None


def validate_manifest(rows: list[dict[str, Any]], phash_distance: int = 4) -> None:
    if not rows:
        raise ReviewError("manifest is empty")
    required = {"sample_id", "split", "class_name", "sha256", "phash", "dataset"}
    for index, row in enumerate(rows, 2):
        missing = sorted(key for key in required if not str(row.get(key, "")).strip())
        if missing:
            raise ReviewError(f"manifest row {index} missing {missing}")
        if row["split"] not in SPLITS:
            raise ReviewError(f"unknown split {row['split']!r} at row {index}")
        if row["class_name"] not in LABELS:
            raise ReviewError(f"unknown class_name {row['class_name']!r} at row {index}")
        if _norm(row.get("generator")) in HELD_OUT_GENERATORS and row["split"] in FIT_SPLITS:
            raise ReviewError(f"held-out generator entered fitting split at row {index}")
        if _norm(row.get("dataset")) == "sdfvd" and row["split"] != "external_test":
            raise ReviewError(f"SDFVD must be external_test only (row {index})")

    ids: set[str] = set()
    hashes: dict[str, str] = {}
    families: dict[str, str] = {}
    by_split: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for row in rows:
        sample_id, split = row["sample_id"], row["split"]
        if sample_id in ids:
            raise ReviewError(f"duplicate sample_id {sample_id}")
        ids.add(sample_id)
        digest = row["sha256"].lower()
        if digest in hashes and hashes[digest] != split:
            raise ReviewError(f"exact duplicate crosses splits: {sample_id}")
        hashes[digest] = split
        family = str(row.get("family_id", "")).strip()
        if family:
            if family in families and families[family] != split:
                raise ReviewError(f"family {family} crosses splits")
            families[family] = split
        by_split[split].append((sample_id, row["phash"].lower()))

    # BK-tree avoids a quadratic all-pairs scan for the 50k+ image manifests.
    tree: _BKNode | None = None
    prior_split_by_id: dict[str, str] = {}
    for split in sorted(by_split):
        pending: list[tuple[str, str]] = []
        for sample_id, value in by_split[split]:
            if tree:
                match = tree.find(value, phash_distance)
                if match:
                    other_id, distance = match
                    raise ReviewError(
                        f"perceptual duplicate crosses {prior_split_by_id[other_id]}/{split}: "
                        f"{other_id}, {sample_id} (distance={distance})"
                    )
            pending.append((sample_id, value))
        # Same-split neighbors are legal and are inserted only after the split query.
        for sample_id, value in pending:
            if tree is None:
                tree = _BKNode(sample_id, value)
            else:
                tree.add(sample_id, value)
            prior_split_by_id[sample_id] = split


def validate_run_config(config: dict[str, Any], manifest_path: str | Path) -> None:
    if config.get("manifest_sha256") != sha256_file(manifest_path):
        raise ReviewError("run config manifest_sha256 does not match manifest bytes")
    devices = config.get("devices", [])
    if len(devices) != 2 or any("T4" not in str(device).upper() for device in devices):
        raise ReviewError("production run must report exactly two NVIDIA T4 devices")
    if config.get("replicas") != 2:
        raise ReviewError("production run must use exactly two replicas")
    global_batch = config.get("global_batch_size")
    if not isinstance(global_batch, int) or global_batch <= 0 or global_batch % 2:
        raise ReviewError("global_batch_size must be a positive multiple of two")
    if config.get("per_replica_batch_size") != global_batch // 2:
        raise ReviewError("per_replica_batch_size must equal global_batch_size / 2")
    if config.get("mixed_precision") != "fp16" or config.get("output_dtype") != "fp32" or config.get("loss_dtype") != "fp32":
        raise ReviewError("require FP16 mixed precision with FP32 output and loss")
    benchmark = config.get("throughput_benchmark", {})
    one, two, minimum = benchmark.get("one_gpu_examples_s"), benchmark.get("two_gpu_examples_s"), benchmark.get("minimum_speedup")
    if not all(isinstance(value, (int, float)) and value > 0 for value in (one, two, minimum)):
        raise ReviewError("one/two GPU throughput and predeclared minimum speedup are required")
    if two / one < minimum:
        raise ReviewError(f"dual-GPU speedup {two / one:.3f} is below frozen minimum {minimum:.3f}")
    sampler = config.get("sampler_audit", {})
    if sampler.get("replicas") != 2 or sampler.get("steps_checked", 0) <= 0 or sampler.get("cross_replica_collisions") != 0:
        raise ReviewError("runtime sampler audit must prove two replicas and zero cross-replica collisions")
    learning_rate = config.get("learning_rate", {})
    if learning_rate.get("scaled_from_global_batch") != global_batch or not isinstance(learning_rate.get("effective"), (int, float)):
        raise ReviewError("learning-rate evidence must bind the effective LR to verified global batch")
    for metric in ("gpu_utilization", "examples_per_second", "peak_memory_bytes", "epoch_duration_seconds"):
        if metric not in config:
            raise ReviewError(f"missing runtime evidence: {metric}")


def validate_predictions(rows: list[dict[str, Any]], predictions: list[dict[str, Any]], split: str = "validation") -> None:
    expected = {row["sample_id"]: row for row in rows if row["split"] == split}
    if not expected:
        raise ReviewError(f"manifest contains no {split} samples")
    seen: set[str] = set()
    for index, prediction in enumerate(predictions, 2):
        sample_id = prediction.get("sample_id", "")
        if sample_id in seen:
            raise ReviewError(f"duplicate prediction for {sample_id}")
        if sample_id not in expected:
            raise ReviewError(f"unexpected prediction ID {sample_id}")
        seen.add(sample_id)
        probabilities = []
        for label in LABELS:
            try:
                value = float(prediction[f"p_{label}"])
            except (KeyError, ValueError, TypeError) as exc:
                raise ReviewError(f"invalid probability for {sample_id}/{label}") from exc
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise ReviewError(f"probability outside [0,1] for {sample_id}/{label}")
            probabilities.append(value)
        if not math.isclose(sum(probabilities), 1.0, abs_tol=1e-4):
            raise ReviewError(f"probabilities do not sum to one for {sample_id}")
        predicted = LABELS[max(range(len(LABELS)), key=probabilities.__getitem__)]
        if prediction.get("predicted_class") != predicted:
            raise ReviewError(f"predicted_class is not canonical argmax for {sample_id}")
    missing = sorted(set(expected) - seen)
    if missing:
        raise ReviewError(f"missing {len(missing)} gathered predictions; first={missing[0]}")


def validate_artifacts(spec: dict[str, Any]) -> None:
    if spec.get("learned_stack_complete") is not True:
        raise ReviewError("artifact report must attest learned_stack_complete=true")
    artifacts = spec.get("learned_artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ReviewError("learned_artifacts must enumerate the complete learned inference stack")
    totals: dict[str, int] = defaultdict(int)
    for item in artifacts:
        for field in ("name", "format", "role", "bytes", "sha256"):
            if field not in item:
                raise ReviewError(f"artifact missing {field}")
        size = item["bytes"]
        if not isinstance(size, int) or size <= 0:
            raise ReviewError(f"invalid artifact size for {item['name']}")
        artifact_path = item.get("path")
        if artifact_path and Path(artifact_path).exists():
            if Path(artifact_path).stat().st_size != size or sha256_file(artifact_path) != item["sha256"]:
                raise ReviewError(f"artifact evidence mismatch for {item['name']}")
        totals[str(item["format"]).lower()] += size
    if totals.get("fp32", 0) <= 0 or totals["fp32"] > 50 * MIB:
        raise ReviewError(f"complete FP32 learned stack is {totals.get('fp32', 0)} bytes; limit is {50 * MIB}")
    if "int8" in totals and totals["int8"] > 15 * MIB:
        raise ReviewError(f"complete INT8 learned stack is {totals['int8']} bytes; target is {15 * MIB}")


def validate_release(metrics: dict[str, Any], gates: dict[str, Any]) -> None:
    if gates.get("frozen_before_external_evaluation") is not True:
        raise ReviewError("release thresholds must attest they were frozen before external evaluation")
    required = {
        "heldout_ai_auc_min": "heldout_ai_auc",
        "heldout_face_auc_min": "heldout_face_auc",
        "ai_recall_min": "ai_recall",
        "face_recall_min": "face_recall",
        "dangerous_false_real_max": "dangerous_false_real",
        "selective_coverage_min": "selective_coverage",
        "abstention_false_real_reduction_min": "abstention_false_real_reduction",
        "int8_balanced_accuracy_drop_max": "int8_balanced_accuracy_drop",
        "sdfvd_balanced_accuracy_gain_min": "sdfvd_balanced_accuracy_gain_vs_ace24",
        "sdfvd_fake_recall_gain_min": "sdfvd_fake_recall_gain_vs_ace24",
    }
    failures = []
    for gate, metric in required.items():
        if gate not in gates or metric not in metrics:
            raise ReviewError(f"missing frozen gate/metric pair: {gate}/{metric}")
        if gate.endswith("_max"):
            passed = metrics[metric] <= gates[gate]
        else:
            passed = metrics[metric] >= gates[gate]
        if not passed:
            failures.append(f"{metric}={metrics[metric]} vs {gate}={gates[gate]}")
    if failures:
        raise ReviewError("public release blocked: " + "; ".join(failures))


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("preflight", "release"):
        command = sub.add_parser(name)
        command.add_argument("--manifest", required=True)
        command.add_argument("--contract", required=True)
        command.add_argument("--run-config", required=True)
        command.add_argument("--phash-distance", type=int, default=4)
        if name == "release":
            command.add_argument("--predictions", required=True)
            command.add_argument("--artifacts", required=True)
            command.add_argument("--metrics", required=True)
            command.add_argument("--gates", required=True)
    args = parser.parse_args(argv)
    rows = load_rows(args.manifest)
    validate_contract(load_json(args.contract))
    validate_manifest(rows, args.phash_distance)
    validate_run_config(load_json(args.run_config), args.manifest)
    if args.command == "release":
        validate_predictions(rows, load_rows(args.predictions))
        validate_artifacts(load_json(args.artifacts))
        validate_release(load_json(args.metrics), load_json(args.gates))
    print(f"ACE Edge {args.command} review: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
