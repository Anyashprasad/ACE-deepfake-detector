from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def discover(root: Path) -> dict:
    datasets = []
    for dataset in sorted(p for p in root.iterdir() if p.is_dir()):
        suffixes: Counter[str] = Counter()
        sample_paths: list[str] = []
        total_bytes = 0
        count = 0
        for path in dataset.rglob("*"):
            if not path.is_file():
                continue
            suffixes[path.suffix.lower() or "<none>"] += 1
            total_bytes += path.stat().st_size
            count += 1
            if len(sample_paths) < 30:
                sample_paths.append(str(path.relative_to(dataset)))
        datasets.append({
            "slug": dataset.name,
            "files": count,
            "bytes": total_bytes,
            "suffixes": dict(suffixes.most_common()),
            "sample_paths": sample_paths,
        })
    payload = {"root": str(root), "datasets": datasets}
    canonical = json.dumps(payload, sort_keys=True).encode()
    payload["inventory_sha256"] = hashlib.sha256(canonical).hexdigest()
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="/kaggle/input")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    payload = discover(Path(args.root))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"datasets": len(payload["datasets"]), "output": str(output)}))


if __name__ == "__main__":
    main()
