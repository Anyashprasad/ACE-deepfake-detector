"""One isolated ACE Edge throughput trial; invoked in a fresh process."""

import argparse
import json
import time
from pathlib import Path

import numpy as np

from .model import build_ace_edge


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=("one", "dual"), required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())

    import tensorflow as tf
    tf.keras.mixed_precision.set_global_policy("mixed_float16")
    physical = tf.config.list_physical_devices("GPU")
    expected = 1 if args.arm == "one" else 2
    if len(physical) != expected:
        raise RuntimeError(f"{args.arm} arm expected {expected} visible GPU(s), found {len(physical)}")
    strategy = (tf.distribute.OneDeviceStrategy("/GPU:0") if expected == 1
                else tf.distribute.MirroredStrategy())
    if strategy.num_replicas_in_sync != expected:
        raise RuntimeError(f"{args.arm} arm expected {expected} replicas, found {strategy.num_replicas_in_sync}")

    batch_size = config["global_batch_size"]
    image_size = config["image_size"]
    warmup_steps = config["benchmark_warmup_steps"]
    measured_steps = config["benchmark_steps"]
    with strategy.scope():
        model = build_ace_edge(tf, image_size, backbone_weights=None)
        base = tf.keras.optimizers.AdamW(
            learning_rate=config["learning_rate"] * batch_size / config["reference_batch_size"],
            weight_decay=config["weight_decay"],
        )
        optimizer = tf.keras.mixed_precision.LossScaleOptimizer(base)
        # Keras 3 otherwise creates AdamW moment and dynamic-loss-scale state on
        # the first apply_gradients call. Under MirroredStrategy that lazy build
        # happens inside replica_1's tf.function trace and can leave an unresolved
        # Placeholder in a slot initializer. Materialize every optimizer variable
        # once, in cross-replica strategy scope, before tracing distributed_step.
        variables = model.trainable_variables
        base.build(variables)
        optimizer.build(variables)
        optimizer_variable_count = len(optimizer.variables)
        if optimizer_variable_count <= 1:
            raise RuntimeError("Optimizer slots were not materialized before distributed tracing")

    dataset = tf.data.Dataset.range(batch_size * (warmup_steps + measured_steps)).batch(
        batch_size, drop_remainder=True)
    distributed = strategy.experimental_distribute_dataset(dataset)

    @tf.function
    def distributed_step(indices):
        def step(local_indices):
            local_batch = tf.shape(local_indices)[0]
            inputs = {
                "global_image": tf.zeros([local_batch, image_size, image_size, 3]),
                "local_image": tf.zeros([local_batch, image_size, image_size, 3]),
                "local_valid": tf.ones([local_batch, 1]),
            }
            with tf.GradientTape() as tape:
                loss = tf.reduce_mean(model(inputs, training=True)["class_probs"][:, 0])
                scaled_loss = optimizer.scale_loss(loss)
            gradients = tape.gradient(scaled_loss, model.trainable_weights)
            optimizer.apply_gradients(zip(gradients, model.trainable_weights))
            return loss
        per_replica = strategy.run(step, args=(indices,))
        return strategy.reduce(tf.distribute.ReduceOp.MEAN, per_replica, axis=None)

    iterator = iter(distributed)
    for _ in range(warmup_steps):
        distributed_step(next(iterator)).numpy()
    throughputs = []
    timestamps = []
    for _ in range(measured_steps):
        started = time.perf_counter()
        distributed_step(next(iterator)).numpy()
        throughputs.append(batch_size / (time.perf_counter() - started))
        timestamps.append(time.time())
    result = {
        "arm": args.arm,
        "replicas": strategy.num_replicas_in_sync,
        "step_throughputs": throughputs,
        "median_examples_s": float(np.median(throughputs)),
        "timestamps": timestamps,
        "optimizer_variable_count": optimizer_variable_count,
    }
    Path(args.output).write_text(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
