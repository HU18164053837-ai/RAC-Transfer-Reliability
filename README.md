# RAC-Transfer-Reliability

Public research data and code repository supporting the RAC prediction reliability study.

## Project overview

This empirical study evaluates prediction-interval cost and the distribution of prediction service across publication sources in recycled aggregate concrete strength modelling. It uses established prediction, conformal-calibration and rejection methods; it is not a new-algorithm study. The main corpus comprises 1,736 mixture records, 115 canonical publications and 99 publication–recipe association components. Two repeated five-fold evaluations yield 3,472 dependent prediction events.

At nominal 90%, source-equal coverage rises from 85.31% to 92.37% with source balancing, while mean full width rises from 26.60 to 33.11 MPa; paired interval scores do not establish a clear advantage. At the 80% quota the joint selector retains approximately 80.13% of events, with RMSE 7.93 MPa and ten publications wholly absent after pooling (14/15 individually). Similar average errors can conceal different source service allocations. A decline in fixed-original-denominator service under nested rejection is algebraic, not claimed as an innovation.

## Associated manuscript

**Beyond Average Coverage: Interval Cost and Source Exclusion in Machine-Learning Predictions of Recycled Aggregate Concrete Strength**

Target journal: European Journal of Environmental and Civil Engineering (EJECE). This repository supports the manuscript's reported analyses. No acceptance, journal publication, separate archival DOI or formal GitHub Release is claimed.

## Data sources and attribution

- Main compilation: Zhang, M.; Liu, J.; Chen, Y.; Wang, Y.; Kang, B.; Lu, D. (2026), *Databases for synergistic multi-performance optimization of recycled aggregate concrete using explainable machine learning and NSGA-III*, Mendeley Data version 1, https://doi.org/10.17632/3xvfyycp8d.1 .
- Historical comparison compilation: Fan, H.; Zhang, S. (2026), *Design of Mechanical Strength, Creep, and Triaxial Shear of Recycled Aggregate Concrete - Data-Driven Method Database*, Mendeley Data version 2, https://doi.org/10.17632/wc898ff5pj.2 .

Both source dataset records state CC BY 4.0. The actual analysis workbooks, source mappings and already-used derived inputs are included with checksums. The historical corpus is used for stress testing; it is not a new independent confirmation cohort. See [data provenance](data/raw/SOURCES.md) and [raw-to-matrix lineage](reproducibility/DATA_LINEAGE.md).

## Repository contents

| Location | Material |
| --- | --- |
| `data/raw/`, `data/derived/` | Compiler workbooks, source metadata and processed modelling inputs |
| `results/` | Phase 1 components, eligibility records, splits and stress-test results |
| `phase2/` | Actual fixed-model, calibration, grouped evaluation and selection code; frozen matrices, predictions, split/OOF ledgers and uncertainty outputs |
| `phase3/` | Source-service and interval-score code/results, source diagnostics and bounded independent-data search evidence |
| `phase4/source_data/`, `phase4/tables/` | Numerical source data for manuscript figures and three main tables |
| `figures/`, `phase4/plot_figures.py`, `phase4/plot_fig1_v02.py` | Five main figures, Figure S1 and their actual plotting scripts |
| `supplementary/` | SI, verified reference records and the electronic-file index mapping each SI CSV to its canonical repository location |
| `configs/`, `reproducibility/` | Frozen model/seed configuration, dependencies, computational lineage and recorded reproduction checks |
| `checksums/` | SHA-256 inventory, original-file mapping and path-adaptation records |

Stage paths are retained so the actual analysis code remains traceable. Explicit shared-input maps avoid duplicated large prediction and split files. Publisher full texts, cached environments and submission correspondence are not part of the research archive.

## Reproducibility instructions

Install the declared dependencies in a clean Python environment, then run:

```text
python -m pip install -r reproducibility/requirements.txt
python scripts/verify_integrity.py
python scripts/verify_saved_results.py
python scripts/regenerate_figures.py
```

These checks verify file hashes, raw-to-matrix content and grouped splits, recalculate the saved-prediction metrics, and regenerate all five main figures plus Figure S1 into `reproduced/figures/`. They do not fit a model or rerun statistical resampling. The [full reproduction guide](reproducibility/REPRODUCE.md) documents execution order, the optional original full-training pathway, resources and limitations. [Recorded test results](reproducibility/test_results/README.md) report 600 operating points and 12,100 recalculated values; six regenerated PNGs matched the frozen figures in the recorded environment.

## Software environment

The recorded environment uses Python 3.12.14, NumPy 2.5.4, pandas 3.1.0, SciPy 1.18.1, scikit-learn 1.9.1 and matplotlib 3.11.2. Exact direct requirements are in [requirements.txt](reproducibility/requirements.txt); the [resolved Windows environment](reproducibility/requirements-resolved-windows.txt) records transitive versions. A [conda/pip environment file](reproducibility/environment.yml) is also supplied. Font/platform differences may affect rendered image bytes; numerical tolerances and the tested resource scope are documented in the reproduction guide.

## Data and code licensing

The two compiler datasets retain their stated CC BY 4.0 licences, attribution and processing-change notes. This does not confer redistribution rights over every underlying publication or automatically assign an open-source licence to author code. The repository is publicly accessible, but no new code licence is introduced by this README revision. Existing [licensing records](LICENSES/README.md) remain unchanged. No third-party software environment is vendored.

## Research limitations

Seven priority sources retain unknown original row-level methods or mappings. The evidence is internal and exploration-informed; historical cross-corpus results are stress tests. Source-balanced empirical coverage is not a proven guarantee for unseen sources. The two repeats share records, and frozen confidence intervals are conditional on the corpus, fitted predictions and design. Service fractions are not engineering safety probabilities. Rejection-induced decline under a fixed original denominator is algebraic rather than a claimed innovation.

## Citation and version information

Cite each original dataset using its own compiler attribution and Mendeley Data DOI above. For this study's research materials, record the Git commit used. The frozen scientific-material baseline is [`30d9e8f2c0853325dc4cb2ecde01d580105a18eb`](https://github.com/HU18164053837-ai/RAC-Transfer-Reliability/tree/30d9e8f2c0853325dc4cb2ecde01d580105a18eb). Current documentation changes can be identified in the repository's commit history. No separate archival DOI or formal Release has been created.

This repository is now public and directly accessible without a GitHub login. Its owner-identifying address is not an anonymized review link; the journal's editorial office should resolve how it is presented during double-anonymized review. Public availability and the journal's handling of reviewer anonymity are separate matters.
