---
name: fleet-research
description: Plan, implement and audit reproducible AI experiments, notebooks and GPU training runs. Use for baselines, ablations, dataset splits, evaluation, statistical claims, checkpointing and limited-compute experiments.
---

# Research experiments

1. Separate the scientific question, the implementable method and the evidence needed for the claim. Write a falsifiable hypothesis and primary metric before examining the test set.
2. Record data source, license, version, sampling unit, split procedure and exclusions. Prevent train/test overlap, entity leakage, tuning on test data and duplicates across combined datasets.
3. Compare against a credible baseline under the same data, preprocessing, evaluation and compute conditions. Label quoted paper results separately from locally reproduced results; never treat incompatible tables as a controlled comparison.
4. Isolate the proposed mechanism with an ablation. Include uncertainty, effect sizes, sample counts and a suitable paired or independent analysis. Define multiplicity and exploratory analyses honestly.
5. Record code commit, dirty state, environment lock, seed, configuration, dataset hashes, device and evaluation script. Keep reusable logic in modules; notebooks should explain and orchestrate.
6. Before GPU use, run CPU/data smoke checks, validate a tiny batch, estimate memory/runtime and prepare resumable checkpoints, logs and a bounded run command. Use project-specific budget and retry limits; do not create a spend limit or claim authorization that was not provided.
7. Make checkpoints and metrics durable before a session ends. Resume an interrupted run when valid; do not silently restart and multiply cost.
8. Keep training, validation and final evaluation separate. Never modify the protocol after seeing results without recording the change. Report negative results and failed runs.
9. Distinguish implemented, executed, measured and hypothesized. Publication venue or acceptance cannot be inferred from working code or one favorable metric.

For experiments spanning multiple datasets, report per-dataset and aggregate results with weighting and domain-shift assumptions. For constrained generation, distinguish empirical validity from a formal guarantee and name the constraints actually checked.
