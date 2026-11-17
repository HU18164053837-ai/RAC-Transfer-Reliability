# RAC-Transfer-Reliability

Private research archive for **Beyond Average Coverage: Interval Cost and Source Exclusion in Machine-Learning Predictions of Recycled Aggregate Concrete Strength**, prepared for European Journal of Environmental and Civil Engineering (EJECE).

The study quantifies interval cost and publication-source service scope in recycled aggregate concrete strength predictions. It uses established methods, not a new algorithm. The main cohort has 1,736 compiled records, 115 canonical publications and 99 source–recipe association components. Two repeated five-fold evaluations produce 3,472 dependent prediction events. The scientific decision remains CONDITIONAL GO within internal cross-source evidence.

At nominal 90%, source-equal coverage rises from 85.31% to 92.37% with source balancing, while mean full width rises from 26.60 to 33.11 MPa; paired interval scores do not establish a clear advantage. At the 80% quota the joint selector retains approximately 80.13% of events, with RMSE 7.93 MPa and ten publications wholly absent after pooling (14/15 individually). Similar average errors can conceal different source service allocations. A decline in fixed-original-denominator service under nested rejection is algebraic, not claimed as an innovation.

## Contents

- data/raw and data/derived: actual compiler versions and already-used modelling inputs, with source attribution.
- results: Phase 1 groups, stress-test split/eligibility records and results.
- phase2: fixed model/calibration/selection code, labelled matrices, row predictions, split/OOF ledgers and uncertainty outputs.
- phase3: source-service/score calculations, source evidence, bounded independent-data search records and frozen supplements.
- phase4: figure source data, three main tables and presentation code. figures: unchanged five main figures and Fig. S1 in SVG/PDF/PNG/TIFF.
- supplementary: SI document, verified reference records and canonical electronic-file index.
- configs and reproducibility: frozen model/seed/environment details, lineage, executable checks and reproduction instructions.
- checksums: every tracked scientific file's SHA-256, upstream mapping and path-adaptation records.

Stage paths are preserved to avoid pretending that display-only code is a full analysis. Duplicate large inputs are replaced with explicit shared-file maps. No cached environments, credentials, publisher full texts, old-paper manuscripts/models, submission cover letters or duplicate delivery ZIPs are included.

## Quick reproduction without training

Use Python 3.12.14 and install `python -m pip install -r reproducibility/requirements.txt`. Then run:

```text
python scripts/verify_integrity.py
python scripts/verify_saved_results.py
python scripts/regenerate_figures.py
```

The first checks every file hash, the second verifies raw-to-matrix content, component/split isolation and recalculates main interval/selection metrics from saved predictions, and the third regenerates all five main figures plus S1 into reproduced/figures. None fits a model or resamples uncertainty. See [REPRODUCE.md](reproducibility/REPRODUCE.md) for the full sequence, environment, import checks, tolerances and resource limits. The recorded test outcome is in reproducibility/test_results/.

## Evidence and release boundaries

Seven priority sources retain unknown original row-level methods/mappings. Historical cross-corpus tests are stress tests, not new external confirmation. Source-balanced empirical coverage is not a proven guarantee for unseen sources. Service indicators do not quantify engineering safety failure. Frozen CI tables are conditional on the corpus and saved fits; two repeats are not independent experiments.

Both compiler releases list CC BY 4.0; attribution and change notices are in [LICENSES](LICENSES/README.md). This does not license every underlying publication or automatically assign an open-source licence to author code. No new repository DOI, public Release, Pages site or public-access permission has been created. This private owner-identifying URL is not an anonymous reviewer code link. EJECE v1.0 manuscript/SI availability statements have not been edited; proposed wording is delivered separately for author review.
