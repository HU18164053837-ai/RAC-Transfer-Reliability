# Reproduction of the frozen RAC study

## Scope and environment

Use a clean clone and Python 3.12.14. `requirements.txt` pins the actual recorded NumPy 2.5.4, pandas 3.1.0, SciPy 1.18.1, scikit-learn 1.9.1, matplotlib 3.11.2, openpyxl 3.1.5, joblib 1.6.0, threadpoolctl 3.7.0 and Pillow 13.0.0. `environment.yml` is a conda/pip alternative. On another platform, font/rendering differences can change exported graphics bytes. Numerical checks use absolute/relative tolerances of 1e-9, with source/event membership checked exactly.

```text
python -m venv .venv
# Activate the environment using the standard command for your OS.
python -m pip install -r reproducibility/requirements.txt
python scripts/verify_integrity.py
python scripts/verify_saved_results.py
python scripts/regenerate_figures.py
```

Default checks run offline after dependency installation. No external data, credentials, model file or original private workspace is required. Results are written only under reproduced/. A dependency installation requires package-index access or a lawful local wheel cache; do not silently substitute package versions. Arial is used when installed; DejaVu Sans is the fallback recorded in the original scripts.

## What is checked without training

The integrity manifest, main raw workbook-to-matrix values, publication/component membership, all saved fit/calibration/test roles, target-free recipe edges, scale OOF isolation and core-script imports are checked. Main interval metrics and every stored Phase 3 quota/threshold/selector/interval/repeat operating point are recalculated from saved row predictions using the existing frozen metric functions. Bootstrap draws are not rerun; uncertainty table hashes and source mappings are checked. All five figures and Fig. S1 are regenerated from frozen plotting CSVs; frozen figure files are never overwritten. PNG pixel identity is checked in the recorded Windows/font environment, but is not promised across arbitrary font/platform changes.

## Full computational lineage for future authorized reruns

`DATA_LINEAGE.md` describes raw-to-matrix transformations. In a disposable clone only, the original sequence is `prepare.py`, `experiment.py` (Phase 1 fits/groups), `phase2/prepare_phase2.py`, `phase2/run_experiments.py`, `phase2/analyze.py`, `phase3/prepare.py`, `phase3/supplement.py`, then `phase4/build_source_data.py` and the plot scripts. Phase 3 source evidence/closed search results are frozen; no live literature search is needed or recommended for numerical reproduction. The executable producer code is included rather than replaced with a toy model. Running those producer mains can overwrite local frozen output copies and is not part of repository acceptance testing.

Phase 1 groups/splits and the historical preprocessing subset are already frozen. The historical 722-row selection incorporates the earlier audited dataset, not a fresh outcome-based filter invented by this study. Its original mapping and raw candidate table are retained; the second-paper repository does not claim to regenerate every earlier paper's original curation from article full texts. Raw aggregate/testing metadata cannot be recovered when absent upstream. No fitted estimator binary was available; full refitting uses the actual supplied code if separately authorized.

## Resources and uncertainty

Saved-result checks and six-figure export are designed for a CPU workstation with 4–8 GB free RAM, no GPU and no cloud service. Expect minutes after installation; measured wall time is recorded in test_results. Historical full reruns were not benchmarked in this repository task: Phase 2 records 17 primary model runs plus 68 auxiliary/scale fits; 2,000 paired component resamples appear in the producer code, with fixed seeds in configs/frozen_analysis.json. Treat future full-run time as hardware dependent rather than a measured estimate. Both repeats must stay within the same component bootstrap cluster.

## Immutable outputs and limitations

Do not run producers in the original scientific workspace. The acceptance test uses a fresh local clone, records environment versions, metrics, plots and errors, and compares canonical SHA-256 hashes to the local frozen baseline. The original manuscripts, data and prior results are not changed. Scientific claims remain conditional; a successful software check does not resolve seven unknown source-row mappings or establish new-source coverage or engineering safety guarantees.
