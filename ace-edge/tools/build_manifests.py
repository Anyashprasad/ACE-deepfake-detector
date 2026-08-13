"""Build frozen ACE Edge manifests from mounted Kaggle datasets."""

from pathlib import Path
import csv, hashlib, json, re
from PIL import Image

ROOT = Path("/kaggle/input")
OUT = Path("/kaggle/working/ace-edge-manifests")
IMG = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
HELD = {"sd_1_5", "midjourney", "vqdm"}


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def ahash(path):
    with Image.open(path) as image:
        pixels = list(image.convert("L").resize((8, 8), Image.Resampling.LANCZOS).getdata())
    mean = sum(pixels) / 64
    return f"{sum((value >= mean) << (63 - index) for index, value in enumerate(pixels)):016x}"


def canon(value):
    compact = re.sub(r"[^a-z0-9]", "", value.lower())
    return {"sd15": "sd_1_5", "stablediffusion15": "sd_1_5"}.get(compact, compact)


def row(path, class_name, source, split, family, generator):
    content_sha = sha(path)
    perceptual_hash = ahash(path)
    return {
        "sample_id": hashlib.sha256(str(path).encode()).hexdigest()[:24],
        "path": str(path), "local_path": str(path), "local_valid": 0,
        "sha256": content_sha, "phash": perceptual_hash, "phash_version": "ahash64-v1",
        "local_sha256": content_sha, "local_phash": perceptual_hash,
        "local_phash_version": "ahash64-v1", "class_name": class_name,
        "source_dataset": source, "split": split, "family_id": family,
        "generator_or_method": generator, "locality_target": 0,
        "reliability_target": 0, "reliability_basis": "disabled_baseline",
    }


def dataset_root(slug):
    matches = [path for path in ROOT.rglob(slug) if path.is_dir()]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one {slug} mount, found {[str(path) for path in matches]}")
    return matches[0]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    candidates = list(ROOT.rglob("manifest.csv"))
    manifest = None
    for candidate in candidates:
        with candidate.open(encoding="utf-8-sig") as probe:
            header = next(csv.reader(probe), [])
        if {"sample_id", "family_id", "sha256", "phash", "class_name"} <= set(header):
            manifest = candidate
            break
    if manifest is None:
        raise RuntimeError(f"FF++ manifest not mounted; manifests={[str(p) for p in candidates]}")
    ffpp = manifest.parent
    with manifest.open(encoding="utf-8-sig") as stream:
        for source_row in csv.DictReader(stream):
            relative = source_row.get("crop_relpath") or source_row["path"].split("/ace-edge-ffpp-compact/", 1)[-1]
            rows.append(row(ffpp / Path(relative), source_row["class_name"], "ffpp_c23_compact",
                            source_row["split"], source_row["family_id"],
                            source_row.get("generator_or_method") or source_row.get("manipulation_method", "original")))

    tiny = dataset_root("tiny-genimage")
    for image in tiny.rglob("*"):
        if image.suffix.lower() not in IMG:
            continue
        relative = image.relative_to(tiny).as_posix()
        generator = canon(relative.split("/")[0].lower().replace("imagenet_ai_0419_", "").replace("imagenet_ai_", ""))
        class_name = "ai_generated" if "/ai/" in f"/{relative.lower()}/" else "likely_real"
        if generator in HELD:
            split = "unseen_generator_test"
        elif "/val/" in f"/{relative.lower()}/" or "/validation/" in f"/{relative.lower()}/":
            split = "validation"
        else:
            split = "train"
        rows.append(row(image, class_name, "tiny_genimage", split, "", generator))

    faces = dataset_root("140k-real-and-fake-faces")
    for image in faces.rglob("*"):
        relative = image.relative_to(faces).as_posix().lower()
        if image.suffix.lower() not in IMG or "/train/" not in f"/{relative}/":
            continue
        class_name = "ai_generated" if "/fake/" in f"/{relative}/" else "likely_real"
        rows.append(row(image, class_name, "140k_faces", "train", "",
                        "stylegan" if class_name == "ai_generated" else "real"))

    fields = list(rows[0])
    counts = {}
    for split in ("train", "validation", "internal_test", "unseen_generator_test"):
        subset = [item for item in rows if item["split"] == split]
        counts[split] = len(subset)
        with (OUT / f"{split}.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader(); writer.writerows(subset)
    report = {"counts": counts, "total": len(rows)}
    (OUT / "build_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report))


if __name__ == "__main__":
    main()
