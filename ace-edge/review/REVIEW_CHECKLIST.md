# ACE Edge review checklist

## Before any significant GPU run

- [ ] Canonical output order is exactly `likely_real`, `ai_generated`,
  `face_manipulated`; `inconclusive` is an abstention decision, never a fourth
  softmax class.
- [ ] Every manifest row has `sample_id`, `split`, `class_name`, `sha256`, and
  `phash`. FF++ rows also carry `family_id` and `manipulation_method`; generated
  images carry `generator`.
- [ ] `family_id` is disjoint across train, validation, calibration, internal test,
  and external test.
- [ ] Frozen generator families `sd15`, `midjourney`, and `vqdm` occur only in test
  roles, never train or calibration.
- [ ] SDFVD occurs only as `external_test`, never in fitting, early stopping,
  calibration, threshold selection, or model selection.
- [ ] Exact SHA-256 duplicates do not cross splits.
- [ ] Perceptual hashes do not cross splits within the declared Hamming threshold.
- [ ] The manifest bytes and frozen split-assignment bytes are hashed and recorded in
  the run config before training.
- [ ] Production run evidence reports exactly two NVIDIA T4 devices and two replicas.
- [ ] Global batch size is divisible by two; each replica sees unique sample IDs per
  step; the learning-rate record states the verified global batch.
- [ ] Mixed precision is enabled while logits/output and loss calculation are FP32.
- [ ] One-GPU and two-GPU fixed-work benchmarks use identical samples and settings;
  the minimum acceptable speedup is explicit before the production run.
- [ ] Training and validation code pass an independent review before GPU quota is
  consumed.

## Validation evidence

- [ ] Validation predictions are gathered across both replicas and contain exactly
  one row for every frozen validation `sample_id`.
- [ ] There are no duplicate or unexpected prediction IDs.
- [ ] Each probability is finite and in `[0,1]`; row sums are within tolerance of 1.
- [ ] `predicted_class` equals the argmax under the canonical label order.
- [ ] Dataset metrics are recomputed from gathered predictions, not averaged from
  per-replica metric objects.
- [ ] Calibration and abstention parameters are learned from calibration only and
  frozen before all held-out tests.

## Model-size accounting

- [ ] Every learned artifact needed for inference is listed with path, SHA-256,
  byte size, and role (classifier, detector, calibrator, or other learned module).
- [ ] Reported sizes equal files on disk when paths are locally available.
- [ ] FP32 complete stack is at most 52,428,800 bytes (50 MiB).
- [ ] INT8 complete stack is at most 15,728,640 bytes (15 MiB).
- [ ] Non-learned runtime libraries are separately reported and never used to hide
  learned detector/calibrator weights.

## Public release gate

- [ ] Numeric thresholds are committed before external-test evaluation; the checker
  does not invent what “materially” means after seeing results.
- [ ] Research-v1 freezes AUROC >= 0.70 for both held-out synthetic tasks, recall >=
  0.50 for both synthetic classes, dangerous false-REAL <= 0.20, selective coverage
  >= 0.70, and absolute false-REAL reduction from abstention >= 0.10. These are
  minimum credibility gates, not claims of production safety.
- [ ] Research-v1 freezes INT8 balanced-accuracy loss <= 0.03, SDFVD balanced
  accuracy gain >= 0.10 (therefore >= 0.60 versus ACE 2.4), and SDFVD fake-recall
  gain >= 0.30 (therefore >= 0.30 versus ACE 2.4).
- [ ] Held-out AI-generator and face-manipulation AUC clear their frozen thresholds.
- [ ] AI-generated and face-manipulated recall are non-degenerate.
- [ ] Dangerous false-REAL rate clears its threshold.
- [ ] Selective abstention reduces dangerous false-REAL error by the frozen minimum.
- [ ] INT8 degradation from FP32 is below the frozen tolerance.
- [ ] SDFVD balanced accuracy and fake recall improve over ACE 2.4 by frozen margins.
- [ ] Any failed gate blocks oracle deployment; code and a negative report may still
  be published.

Metric contract: `dangerous_false_real` is the fraction of all synthetic examples
that are emitted as likely-real (abstentions are not counted as likely-real).
`selective_coverage` is the fraction of all examples receiving a non-inconclusive
decision. `abstention_false_real_reduction` is the absolute difference between the
forced-decision false-REAL rate and selective false-REAL rate on the same frozen
examples. AUC is always calculated from continuous pre-abstention evidence, never
from hard labels.

## Current blockers found 2026-08-13

1. The repository contains no ACE Edge manifest, contract, run config, gathered
   validation predictions, or frozen numeric gate file yet.
2. `git status` fails because Git LFS cannot clean
   `.git/lfs/tmp/1770283758` (`Access is denied`). Branch/commit verification is not
   trustworthy until this is repaired.
3. “Materially above chance” and “materially improving ACE 2.4” have no numeric
   thresholds in the approved prose plan. They must be frozen before SDFVD is run.
4. A dual-T4 implementation claim is insufficient without runtime evidence for two
   T4 device names, two replicas, disjoint sampler IDs, global prediction gathering,
   and measured one-vs-two-GPU scaling.
5. The first executable training draft evaluated and exported the final epoch rather
   than reloading its best checkpoint, and it did not save sample-ID-keyed gathered
   predictions. Both are release-blocking until corrected.
6. Source-balanced sampling, a fixed-work one-versus-two-GPU benchmark, raw manifest
   byte hashes, per-GPU telemetry, sampler-collision evidence, and a documented
   non-leaking reliability target were absent from the first executable draft.
