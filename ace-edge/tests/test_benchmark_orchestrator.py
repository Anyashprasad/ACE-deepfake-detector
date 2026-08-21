import unittest
import inspect
import tempfile
from pathlib import Path

from ace_edge.benchmark_orchestrator import bootstrap_trial_ratio, prepare_output_directory
from ace_edge import benchmark_worker


class BenchmarkStatisticsTests(unittest.TestCase):
    def test_prepare_output_directory_removes_stale_evidence_only(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            for name in ("benchmark.json", "benchmark.json.tmp", "trial-00-one.json", "trial-99-dual.json"):
                (output / name).write_text("stale")
            (output / "telemetry.json").write_text("keep")
            prepare_output_directory(output)
            self.assertEqual([path.name for path in output.iterdir()], ["telemetry.json"])

    def test_optimizer_slots_are_built_before_distributed_step_trace(self):
        source = inspect.getsource(benchmark_worker.main)
        base_at = source.index("base.build(variables)")
        build_at = source.index("optimizer.build(variables)")
        trace_at = source.index("@tf.function")
        self.assertLess(base_at, build_at)
        self.assertLess(build_at, trace_at)
        self.assertIn('"optimizer_variable_count": optimizer_variable_count', source)

    def test_trial_level_bootstrap_is_deterministic_and_passes_clear_scaling(self):
        one = [100, 101, 99, 100, 102, 98, 101, 99, 100, 100]
        dual = [150, 152, 149, 151, 153, 148, 152, 149, 151, 150]
        first = bootstrap_trial_ratio(one, dual, seed=2401, draws=1000)
        second = bootstrap_trial_ratio(one, dual, seed=2401, draws=1000)
        self.assertEqual(first, second)
        self.assertGreater(first["ci95_low"], 1.35)

    def test_rejects_too_few_or_unpaired_trials(self):
        with self.assertRaises(ValueError):
            bootstrap_trial_ratio([100] * 7, [150] * 7, seed=1)
        with self.assertRaises(ValueError):
            bootstrap_trial_ratio([100] * 10, [150] * 9, seed=1)


if __name__ == "__main__":
    unittest.main()
