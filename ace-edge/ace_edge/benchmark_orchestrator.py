"""Run isolated, counterbalanced 1-vs-2 GPU throughput trials."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np


def bootstrap_trial_ratio(one_medians, dual_medians, seed, draws=10000):
    one, dual = np.asarray(one_medians), np.asarray(dual_medians)
    if len(one) != len(dual) or len(one) < 8:
        raise ValueError("At least 8 paired independent trials are required")
    ratios = dual / one
    rng = np.random.default_rng(seed)
    boot = np.array([np.median(rng.choice(ratios, size=len(ratios), replace=True)) for _ in range(draws)])
    return {"median": float(np.median(ratios)), "ci95_low": float(np.quantile(boot, .025)),
            "ci95_high": float(np.quantile(boot, .975)), "paired_trial_ratios": ratios.tolist()}


def prepare_output_directory(output):
    """Remove evidence from earlier attempts before starting a fresh benchmark."""
    output.mkdir(parents=True, exist_ok=True)
    for stale in [output / "benchmark.json", output / "benchmark.json.tmp", *output.glob("trial-*.json")]:
        stale.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    output = Path(args.output)
    prepare_output_directory(output)
    repetitions = config["benchmark_repetitions"]
    orders = [("one", "dual") if index % 2 == 0 else ("dual", "one") for index in range(repetitions)]
    trials = []
    for trial_index, order in enumerate(orders):
        record = {"trial": trial_index, "order": list(order)}
        for arm in order:
            destination = output / f"trial-{trial_index:02d}-{arm}.json"
            destination.unlink(missing_ok=True)
            environment = os.environ.copy()
            environment["CUDA_VISIBLE_DEVICES"] = "0" if arm == "one" else "0,1"
            subprocess.run([sys.executable, "-m", "ace_edge.benchmark_worker", "--arm", arm,
                            "--config", args.config, "--output", str(destination)],
                           env=environment, check=True)
            if not destination.is_file():
                raise RuntimeError(f"Benchmark worker produced no fresh result: {destination.name}")
            record[arm] = json.loads(destination.read_text())
        trials.append(record)
    one = [trial["one"]["median_examples_s"] for trial in trials]
    dual = [trial["dual"]["median_examples_s"] for trial in trials]
    summary = bootstrap_trial_ratio(one, dual, config["seed"], config["benchmark_bootstrap_draws"])
    summary.update({"gate": config["minimum_dual_gpu_speedup"], "repetitions": repetitions,
                    "trial_scope": "fresh_process", "counterbalanced": True, "trials": trials})
    report = output / "benchmark.json"
    temporary_report = output / "benchmark.json.tmp"
    temporary_report.write_text(json.dumps(summary, indent=2))
    os.replace(temporary_report, report)
    if summary["ci95_low"] < config["minimum_dual_gpu_speedup"]:
        raise RuntimeError(f"Dual T4 CI lower bound {summary['ci95_low']:.3f} below gate")


if __name__ == "__main__":
    main()
