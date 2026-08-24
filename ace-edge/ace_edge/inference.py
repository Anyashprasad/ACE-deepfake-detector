from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from . import CLASS_NAMES
from .model import build_ace_edge

RELEASE_TAG = "ace-edge-v1.0.0"
RELEASE_WEIGHTS_NAME = "ace-edge-v1.weights.h5"
RELEASE_WEIGHTS_SHA256 = "cc88d6e5a5a744a7e51645787a34f5c3c077c1d7e7ea6f53a532bdf2f02052fa"


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_release_model(tf, weights_path: str | Path, verify_checksum: bool = True):
    """Build the frozen v1 architecture and load the public release weights."""
    weights_path = Path(weights_path)
    if not weights_path.is_file():
        raise FileNotFoundError(f"ACE Edge weights not found: {weights_path}")
    if verify_checksum:
        actual = sha256_file(weights_path)
        if actual != RELEASE_WEIGHTS_SHA256:
            raise RuntimeError(
                f"ACE Edge weights SHA-256 mismatch: expected {RELEASE_WEIGHTS_SHA256}, found {actual}"
            )
    model = build_ace_edge(
        tf,
        image_size=224,
        dropout=0.2,
        backbone_weights=None,
        include_experimental_heads=False,
        training_augmentation=False,
        include_binary_head=False,
    )
    model.load_weights(weights_path)
    return model


def decode_image(tf, path: str | Path):
    image = tf.io.decode_image(
        tf.io.read_file(str(path)), channels=3, expand_animations=False
    )
    image.set_shape([None, None, 3])
    image = tf.image.resize(image, [224, 224], antialias=True)
    image = tf.clip_by_value(image, 0.0, 255.0)
    return tf.cast(image, tf.float32) / 127.5 - 1.0


def predict_image(tf, model, image_path: str | Path, local_image_path: str | Path | None = None):
    global_image = decode_image(tf, image_path)
    if local_image_path is None:
        local_image = global_image
        local_valid = 0.0
    else:
        local_image = decode_image(tf, local_image_path)
        local_valid = 1.0
    probabilities = model(
        {
            "global_image": global_image[None, ...],
            "local_image": local_image[None, ...],
            "local_valid": tf.constant([[local_valid]], dtype=tf.float32),
        },
        training=False,
    )["class_probs"][0].numpy()
    values = {name: float(probabilities[index]) for index, name in enumerate(CLASS_NAMES)}
    return {"predicted_class": max(values, key=values.get), "probabilities": values}


def main():
    parser = argparse.ArgumentParser(description="Run research-only ACE Edge v1 image inference")
    parser.add_argument("--weights", required=True, help="Path to ace-edge-v1.weights.h5")
    parser.add_argument("--image", required=True, help="Full image or face crop")
    parser.add_argument("--local-image", help="Optional detector-provided local face crop")
    parser.add_argument("--no-checksum", action="store_true", help="Skip release checksum verification")
    args = parser.parse_args()

    import tensorflow as tf

    model = load_release_model(tf, args.weights, verify_checksum=not args.no_checksum)
    print(json.dumps(predict_image(tf, model, args.image, args.local_image), indent=2))


if __name__ == "__main__":
    main()
