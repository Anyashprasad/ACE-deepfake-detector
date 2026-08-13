from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

MIB = 1024 * 1024
CLASS_TO_ID = {"likely_real": 0, "ai_generated": 1, "face_manipulated": 2}
FORBIDDEN_DEVELOPMENT_SOURCES = {"sdfvd"}


@dataclass(frozen=True)
class SizeReport:
    parameters: int
    fp32_mib: float


def learned_size_report(model, learned_artifacts=()) -> SizeReport:
    parameters = int(sum(int(v.shape.num_elements()) for v in model.weights))
    extra_bytes = sum(Path(path).stat().st_size for path in learned_artifacts)
    return SizeReport(parameters=parameters, fp32_mib=(parameters * 4 + extra_bytes) / MIB)


def enforce_size_limit(model, max_fp32_mib: float = 50.0, learned_artifacts=()) -> SizeReport:
    report = learned_size_report(model, learned_artifacts)
    if report.fp32_mib > max_fp32_mib:
        raise RuntimeError(
            f"Learned stack is {report.fp32_mib:.2f} MiB FP32, above "
            f"the {max_fp32_mib:.2f} MiB contract."
        )
    return report


def ensure_under_directory(path: str, root: str = "/kaggle/input") -> None:
    candidate = Path(path)
    try:
        candidate.relative_to(Path(root))
    except ValueError as exc:
        raise ValueError(f"Input {path!r} must remain under mounted {root}") from exc
