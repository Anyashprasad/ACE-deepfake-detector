import argparse, hashlib, json, os, random, subprocess, time
from pathlib import Path
import numpy as np
from .contracts import enforce_size_limit
from .data import assert_all_splits_independent, build_dataset, load_manifest, raw_manifest_digest, verify_manifest_content
from .metrics import dangerous_false_real_rate, multiclass_brier, unseen_generator_metrics
from .model import build_ace_edge


def require_dual_t4(tf):
    devices = tf.config.list_physical_devices("GPU")
    names = [str(tf.config.experimental.get_device_details(d).get("device_name", "")) for d in devices]
    if len(devices) != 2 or not all("T4" in n.upper() for n in names):
        raise RuntimeError(f"Exactly two NVIDIA T4 GPUs required; found {names}")
    return names


def is_chief():
    task = json.loads(os.environ.get("TF_CONFIG", "{}")).get("task", {})
    return not task or (task.get("type") in (None, "chief") and task.get("index", 0) == 0)


def directory_bytes(root):
    return sum(path.stat().st_size for path in Path(root).rglob("*") if path.is_file())


def gpu_snapshot():
    command = ["nvidia-smi", "--query-gpu=name,utilization.gpu,memory.used,memory.total",
               "--format=csv,noheader,nounits"]
    return subprocess.run(command, capture_output=True, text=True, check=True).stdout.strip().splitlines()


class Telemetry:
    def __init__(self, tf, output, examples_per_epoch):
        self.tf, self.output, self.examples = tf, Path(output), examples_per_epoch
        self.rows, self.started = [], None
    def callback(self):
        parent = self
        class C(self.tf.keras.callbacks.Callback):
            def on_epoch_begin(self, epoch, logs=None): parent.started = time.perf_counter()
            def on_epoch_end(self, epoch, logs=None):
                seconds = time.perf_counter() - parent.started
                parent.rows.append({"epoch": epoch, "seconds": seconds,
                    "examples_per_second": parent.examples / seconds, "gpu": gpu_snapshot(),
                    "peak_memory_bytes": [parent.tf.config.experimental.get_memory_info(f"GPU:{i}")["peak"] for i in range(2)]})
                parent.output.write_text(json.dumps(parent.rows, indent=2))
        return C()


def benchmark_strategy(tf, strategy, batch_size, image_size, warmup_steps, measured_steps):
    with strategy.scope():
        model = build_ace_edge(tf, image_size, backbone_weights=None)
        optimizer = tf.keras.optimizers.SGD()
    dataset = tf.data.Dataset.range(batch_size * (warmup_steps + measured_steps)).batch(batch_size, drop_remainder=True)
    distributed = strategy.experimental_distribute_dataset(dataset)
    @tf.function
    def distributed_step(indices):
        def step(local_indices):
            local_batch = tf.shape(local_indices)[0]
            inputs={"global_image":tf.zeros([local_batch,image_size,image_size,3]),
                    "local_image":tf.zeros([local_batch,image_size,image_size,3]),
                    "local_valid":tf.ones([local_batch,1])}
            with tf.GradientTape() as tape:
                loss = tf.reduce_mean(model(inputs, training=True)["class_probs"][:, 0])
            optimizer.apply_gradients(zip(tape.gradient(loss, model.trainable_weights), model.trainable_weights))
            return loss
        return strategy.run(step, args=(indices,))
    iterator=iter(distributed)
    for _ in range(warmup_steps):
        tf.nest.map_structure(lambda value: value.numpy(), distributed_step(next(iterator)))
    throughputs=[]
    for _ in range(measured_steps):
        started=time.perf_counter()
        tf.nest.map_structure(lambda value: value.numpy(), distributed_step(next(iterator)))
        throughputs.append(batch_size/(time.perf_counter()-started))
    return throughputs


def bootstrap_speedup_interval(one_steps, dual_steps, seed, draws=10000):
    rng=np.random.default_rng(seed); one=np.asarray(one_steps); dual=np.asarray(dual_steps)
    ratios=np.empty(draws,dtype=np.float64)
    for index in range(draws):
        one_median=np.median(rng.choice(one,size=len(one),replace=True))
        dual_median=np.median(rng.choice(dual,size=len(dual),replace=True))
        ratios[index]=dual_median/one_median
    return {"median":float(np.median(dual)/np.median(one)),
            "ci95_low":float(np.quantile(ratios,.025)),"ci95_high":float(np.quantile(ratios,.975))}


def decode_sample_ids(raw_ids):
    return np.array([item.decode("utf-8") if isinstance(item, bytes) else str(item) for item in raw_ids])


def distributed_predict(tf, strategy, model, dataset, expected_ids):
    @tf.function
    def step(batch):
        ids, images, targets = batch; out = model(images, training=False)
        return ids, targets["class_probs"], out["class_probs"]
    columns = [[], [], []]
    for batch in strategy.experimental_distribute_dataset(dataset):
        values = strategy.run(step, args=(batch,))
        for index, value in enumerate(values):
            columns[index].append(tf.concat(strategy.experimental_local_results(value), 0).numpy())
    raw_ids = np.concatenate(columns[0])
    ids = decode_sample_ids(raw_ids)
    if len(ids) != len(set(ids)) or set(ids) != set(expected_ids):
        raise RuntimeError("Distributed validation coverage/collision audit failed")
    return ids, *(np.concatenate(items) for items in columns[1:])


def prediction_rows(ids, truth, probabilities):
    probabilities = require_finite_class_probabilities(probabilities, "prediction")
    labels = ("likely_real", "ai_generated", "face_manipulated")
    rows = []
    for sample_id, class_id, probs in zip(ids, truth, probabilities):
        values = [float(value) for value in probs]
        rows.append({
            "sample_id": str(sample_id),
            "class_id": int(class_id),
            "predicted_class": labels[int(np.argmax(values))],
            "p_likely_real": values[0],
            "p_ai_generated": values[1],
            "p_face_manipulated": values[2],
            "probabilities": values,
        })
    return rows


def require_finite_class_probabilities(probabilities, context):
    """Reject invalid model output before calibration or report generation."""
    values = np.asarray(probabilities, dtype=np.float64)
    if values.ndim != 2 or values.shape[1] != 3:
        raise RuntimeError(
            f"{context} class probabilities must have shape (N, 3); found {values.shape}"
        )
    if not np.isfinite(values).all():
        invalid = int(values.size - np.isfinite(values).sum())
        raise RuntimeError(
            f"{context} class probabilities contain {invalid} non-finite values; "
            "refusing to calibrate or publish invalid metrics"
        )
    if ((values < 0.0) | (values > 1.0)).any():
        raise RuntimeError(f"{context} class probabilities fall outside [0, 1]")
    if not np.allclose(values.sum(axis=1), 1.0, rtol=1e-5, atol=1e-6):
        raise RuntimeError(f"{context} class probabilities do not sum to one")
    return values


def validation_ai_threshold(truth, probabilities, target_real_recall):
    """Choose an AI score threshold using validation reals only, never unseen data."""
    if not 0.0 < target_real_recall < 1.0:
        raise ValueError("target_real_recall must be strictly between zero and one")
    values = require_finite_class_probabilities(probabilities, "validation")
    real_scores = values[np.asarray(truth) == 0, 1]
    if not len(real_scores):
        raise RuntimeError("Validation set has no likely_real examples for threshold calibration")
    # Prediction uses score >= threshold. Move one representable value above
    # the selected real score so ties cannot silently violate the recall target.
    selected = np.quantile(real_scores, target_real_recall, method="higher")
    return float(np.nextafter(selected, np.inf))


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--config", required=True)
    config=json.loads(Path(parser.parse_args().config).read_text()); os.environ.setdefault("TF_DETERMINISTIC_OPS","1")
    import tensorflow as tf
    names=require_dual_t4(tf)
    if not is_chief(): raise RuntimeError("This MirroredStrategy entrypoint permits chief-only execution/writes")
    if config["benchmark_warmup_steps"] < 15 or config["benchmark_steps"] < 100 or config["benchmark_repetitions"] < 3:
        raise ValueError("Benchmark requires >=15 warmup, >=100 measured steps, and >=3 repetitions")
    if config["global_batch_size"] % 2: raise ValueError("Global batch must divide across replicas")
    seed=config["seed"]; random.seed(seed); np.random.seed(seed); tf.keras.utils.set_random_seed(seed)
    tf.keras.mixed_precision.set_global_policy("mixed_float16")
    train=load_manifest(config["train_manifest"],"train")
    val=load_manifest(config["validation_manifest"],"validation")
    unseen=load_manifest(config["unseen_generator_manifest"],"unseen_generator_test")
    assert_all_splits_independent({"train":train,"validation":val,"unseen_generator_test":unseen})
    manifest_paths={"train":config["train_manifest"],"validation":config["validation_manifest"],"unseen":config["unseen_generator_manifest"]}
    raw_hashes={name:raw_manifest_digest(path) for name,path in manifest_paths.items()}
    integrity={"train":verify_manifest_content(train,raw_hashes["train"]),
               "validation":verify_manifest_content(val,raw_hashes["validation"]),
               "unseen":verify_manifest_content(unseen,raw_hashes["unseen"])}
    if config["reliability_loss_weight"] != 0:
        raise RuntimeError("Baseline reliability loss must remain disabled until augmentation-consistency targets are computed online")
    out=Path(config["output_dir"]); out.mkdir(parents=True,exist_ok=True)
    benchmark_path=Path(config["benchmark_report"])
    benchmark=json.loads(benchmark_path.read_text())
    if benchmark.get("trial_scope") != "fresh_process" or not benchmark.get("counterbalanced"):
        raise RuntimeError("Training requires a fresh-process counterbalanced benchmark report")
    if benchmark["ci95_low"] < config["minimum_dual_gpu_speedup"]:
        raise RuntimeError(f"Dual T4 speedup CI lower bound {benchmark['ci95_low']:.2f} below gate")
    (out/"benchmark.json").write_text(json.dumps(benchmark,indent=2))
    dual=tf.distribute.MirroredStrategy()
    if dual.num_replicas_in_sync != 2:
        raise RuntimeError(f"Training expected 2 replicas, found {dual.num_replicas_in_sync}")
    include_binary_head = config.get("include_binary_head", False)
    with dual.scope():
        model=build_ace_edge(tf,config["image_size"],config["dropout"],config["backbone_weights"],
                             training_augmentation=config.get("training_augmentation", False),
                             include_binary_head=include_binary_head)
        size=enforce_size_limit(model,config["max_fp32_mib"])
        lr=config["learning_rate"]*config["global_batch_size"]/config["reference_batch_size"]
        losses={"class_probs":tf.keras.losses.CategoricalCrossentropy(label_smoothing=config["label_smoothing"])}
        if include_binary_head:
            losses["binary_prob"]=tf.keras.losses.BinaryCrossentropy()
        model.compile(optimizer=tf.keras.optimizers.AdamW(lr,weight_decay=config["weight_decay"]),loss=losses)
    train_ds=build_dataset(tf,train,config["image_size"],config["global_batch_size"],True,seed,
                           training_augmentation=config.get("training_augmentation",False),
                           include_binary_target=include_binary_head)
    val_ds=build_dataset(tf,val,config["image_size"],config["global_batch_size"],False,seed,
                         include_binary_target=include_binary_head)
    telemetry=Telemetry(tf,out/"telemetry.json",config["steps_per_epoch"]*config["global_batch_size"])
    best=out/"best.weights.h5"
    history = model.fit(train_ds,validation_data=val_ds,steps_per_epoch=config["steps_per_epoch"],epochs=config["epochs"],
      callbacks=[tf.keras.callbacks.TerminateOnNaN(),
                 tf.keras.callbacks.ModelCheckpoint(best,monitor="val_loss",mode="min",save_best_only=True,save_weights_only=True),
                 telemetry.callback()])
    if not history.history.get("val_loss") or not np.isfinite(history.history["val_loss"]).any():
        raise RuntimeError("Training produced no finite validation loss; refusing to evaluate or export")
    model.load_weights(best)
    pred_ds=build_dataset(tf,val,config["image_size"],config["global_batch_size"],False,seed,include_ids=True)
    ids,ys,probs=distributed_predict(tf,dual,model,pred_ds,val["sample_id"].astype(str)); truth=ys.argmax(1)
    rows=prediction_rows(ids,truth,probs)
    (out/"validation_predictions.jsonl").write_text("\n".join(json.dumps(row) for row in rows))
    target_real_recall=float(config.get("target_validation_real_recall", .95))
    ai_threshold=validation_ai_threshold(truth,probs,target_real_recall)
    unseen_ds=build_dataset(tf,unseen,config["image_size"],config["global_batch_size"],False,seed,include_ids=True)
    uids,uys,uprobs=distributed_predict(tf,dual,model,unseen_ds,unseen["sample_id"].astype(str)); utruth=uys.argmax(1)
    unseen_rows=prediction_rows(uids,utruth,uprobs)
    (out/"unseen_generator_predictions.jsonl").write_text("\n".join(json.dumps(row) for row in unseen_rows))
    unseen_metrics=unseen_generator_metrics(utruth,uprobs,unseen.set_index("sample_id").loc[uids,"generator_or_method"].to_numpy(),ai_threshold)
    report={"raw_manifest_sha256":raw_hashes,"integrity":integrity,
      "devices":names,"benchmark":benchmark,
      "replica_collision_audit":{"expected":len(val),"gathered":len(ids),"unique":len(set(ids))},
      "parameters":size.parameters,"fp32_mib":size.fp32_mib,"dangerous_false_real_rate":dangerous_false_real_rate(truth,probs),
      "brier":multiclass_brier(truth,probs),"abstention_release_ready":False,
      "operating_point":{"ai_threshold":ai_threshold,"target_validation_real_recall":target_real_recall},
      "unseen_generator":{**unseen_metrics,"dangerous_false_real_rate":dangerous_false_real_rate(utruth,uprobs),"brier":multiclass_brier(utruth,uprobs)}}
    (out/"validation_metrics.json").write_text(json.dumps(report,indent=2)); model.export(out/"saved_model")
    if directory_bytes(out)>config["max_output_gib"]*1024**3: raise RuntimeError("Output exceeds storage contract")

if __name__=="__main__": main()
