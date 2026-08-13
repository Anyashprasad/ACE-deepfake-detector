from __future__ import annotations


def build_ace_edge(tf, image_size=224, dropout=0.2, backbone_weights="imagenet"):
    global_image = tf.keras.Input((image_size, image_size, 3), name="global_image")
    local_image = tf.keras.Input((image_size, image_size, 3), name="local_image")
    local_valid = tf.keras.Input((1,), name="local_valid")
    backbone = tf.keras.applications.MobileNetV3Large(
        input_shape=(image_size, image_size, 3), include_top=False,
        weights=backbone_weights, include_preprocessing=False,
    )
    pool = tf.keras.layers.GlobalAveragePooling2D()
    global_features = pool(backbone(global_image))
    local_features = pool(backbone(local_image))
    gated_local = tf.keras.layers.Multiply()([local_features, local_valid])
    shared = tf.keras.layers.Dropout(dropout)(tf.keras.layers.Concatenate()([global_features, gated_local]))
    # Explicit float32 heads keep logits/probabilities stable under mixed_float16.
    class_logits = tf.keras.layers.Dense(3, dtype="float32", name="class_logits")(shared)
    class_probs = tf.keras.layers.Activation("softmax", dtype="float32", name="class_probs")(class_logits)
    locality = tf.keras.layers.Dense(1, activation="sigmoid", dtype="float32", name="locality")(shared)
    reliability = tf.keras.layers.Dense(1, activation="sigmoid", dtype="float32", name="reliability")(shared)
    return tf.keras.Model({"global_image": global_image, "local_image": local_image, "local_valid": local_valid}, {"class_probs": class_probs, "locality": locality,
                                   "reliability": reliability}, name="ace_edge")
