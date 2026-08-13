"""Repair the v3 Tiny GenImage aliases/splits without rehashing image bytes."""

from pathlib import Path
import json
import pandas as pd

SPLITS = ("train", "validation", "internal_test", "unseen_generator_test")
HELD = {"sd_1_5", "midjourney", "vqdm"}
ALIASES = {
    "0424sdv5": "sd_1_5", "imagenetmidjourney": "midjourney",
    "imagenetglide": "glide", "biggan": "biggan", "0424wukong": "wukong",
    "0508adm": "adm", "vqdm": "vqdm",
}


def main(source: Path, target: Path) -> None:
    frames = [pd.read_csv(source / f"{split}.csv", low_memory=False) for split in SPLITS]
    data = pd.concat(frames, ignore_index=True)
    tiny = data.source_dataset.eq("tiny_genimage")
    data.loc[tiny, "generator_or_method"] = data.loc[tiny, "generator_or_method"].map(ALIASES)
    if data.loc[tiny, "generator_or_method"].isna().any():
        raise RuntimeError("Unknown Tiny GenImage generator alias")
    held = tiny & data.generator_or_method.isin(HELD)
    data.loc[held, "split"] = "unseen_generator_test"
    # Dataset layout encodes official train/val in each immutable mounted path.
    eligible = tiny & ~data.generator_or_method.isin(HELD)
    data.loc[eligible, "split"] = data.loc[eligible, "path"].map(
        lambda path: "validation" if "/val/" in path.lower() or "/validation/" in path.lower() else "train"
    )
    duplicate = data.duplicated("sha256", keep=False)
    removed = int(duplicate.sum())
    data = data.loc[~duplicate].copy()
    target.mkdir(parents=True, exist_ok=True)
    counts = {}
    for split in SPLITS:
        subset = data.loc[data.split.eq(split)]
        counts[split] = len(subset)
        subset.to_csv(target / f"{split}.csv", index=False)
    report = {"counts": counts, "total": len(data), "removed_exact_duplicate_rows": removed,
              "repair_source": "manifest-builder-v3"}
    (target / "build_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    args = parser.parse_args()
    main(args.source, args.target)
