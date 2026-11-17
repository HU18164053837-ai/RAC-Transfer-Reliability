### Table 1 Data and evidence scope

| Item | Scope and evidence |
| --- | --- |
| Main cohort | 1,736 mixture records; all original flags retained |
| Inputs and target | 11 numeric inputs; 28-day MPa label; 150 mm cube equivalence is a compiler claim |
| Publication identity | 115 canonical publication sources; database references [2] and [75] share one DOI |
| Association unit | 99 connected components; source identity plus eight-field near-recipe links |
| Repeated evaluation | 2 × 5 outer component folds; 3,472 prediction events; 1,736 unique records |
| Unresolved metadata | 7 priority sources, 247 records; original row-level confirmation incomplete for all seven |
| Risk sensitivity | 4 flagged components, 254 records removed in an existing one-repeat analysis |
| Independent confirmation | 6 candidates screened; 0 admitted records in the bounded search |
| Historical corpus | 980 raw candidates; 722 frozen records; 586 in six-input stress cohort |

### Table 2 Interval reliability and cost

A. Coverage and mean full width

| Interval | Sample coverage (%) | Source-equal coverage (%) | Full width (MPa) |
| --- | --- | --- | --- |
| Pooled | 87.13 [82.84, 90.60] | 85.31 [80.10, 89.64] | 26.60 [26.06, 27.06] |
| Source-balanced | 93.69 [90.88, 95.88] | 92.37 [88.54, 95.43] | 33.11 [32.22, 34.13] |
| Adaptive | 92.25 [88.66, 94.89] | 92.17 [88.70, 95.05] | 34.93 [33.41, 36.53] |
| Adaptive budget | 85.17 [80.77, 88.85] | 83.65 [78.58, 87.90] | 25.72 [24.80, 26.67] |
| Group maximum | 98.44 [97.14, 99.34] | 97.81 [95.49, 99.33] | 49.46 [47.83, 51.11] |

B. Interval score

| Interval | Sample-weighted IS (MPa) | Source-equal IS (MPa) |
| --- | --- | --- |
| Pooled | 38.70 | 42.99 |
| Source-balanced | 40.15 [36.55, 45.74] | 43.64 [37.90, 51.97] |
| Adaptive | 41.79 [38.37, 46.67] | 43.50 [39.13, 49.51] |
| Adaptive budget | 38.72 [33.95, 45.32] | 41.68 [35.01, 50.42] |
| Group maximum | 51.43 [48.95, 55.07] | 52.94 [49.56, 58.76] |

Brackets give frozen 95% component-bootstrap intervals. Pooled score bounds were not available in the frozen outputs and are not newly estimated; its score entries are point estimates. All data are retained. Adaptive budget is calibration-width matched; group maximum is a different-target reference. IS denotes interval score, for which lower is better. Coverage and width bounds use seed 2026110899; non-pooled score bounds use seed 2026110833. No absence of a score bound implies zero uncertainty.

### Table 3 Selection and original-source service

A. Retention and accepted-event error

| Quota (%) | Rule | Sample retained (%) | Sources retained (%) | Absent sources | RMSE (MPa) | MAE (MPa) |
| --- | --- | --- | --- | --- | --- | --- |
| 100 | None | 100.00 | 100.00 | 0 | 8.84 | 7.00 |
| 90 | Random mean | 90.12 | 100.00 | 0.00 | 8.84 | 7.00 |
| 90 | Tree SD | 90.12 | 96.52 | 4 | 8.26 | 6.65 |
| 90 | Distance | 90.12 | 95.65 | 5 | 8.30 | 6.73 |
| 90 | Scale / width | 90.12 | 100.00 | 0 | 8.39 | 6.73 |
| 90 | Joint | 90.12 | 96.52 | 4 | 8.24 | 6.67 |
| 80 | Random mean | 80.13 | 100.00 | 0.00 | 8.84 | 7.00 |
| 80 | Tree SD | 80.13 | 95.65 | 5 | 7.91 | 6.40 |
| 80 | Distance | 80.13 | 89.57 | 12 | 7.92 | 6.47 |
| 80 | Scale / width | 80.13 | 94.78 | 6 | 8.09 | 6.52 |
| 80 | Joint | 80.13 | 91.30 | 10 | 7.93 | 6.47 |

B. Coverage and successful service

| Quota (%) | Rule | Sample coverage (%) | Survivor-source coverage (%) | Zero-if-absent (%) | Original-source service (%) |
| --- | --- | --- | --- | --- | --- |
| 100 | None | 85.17 | 83.65 | 83.65 | 83.65 |
| 90 | Random mean | 85.16 | 83.64 | 83.64 | 75.38 |
| 90 | Tree SD | 85.52 | 84.99 | 82.03 | 74.07 |
| 90 | Distance | 85.87 | 85.27 | 81.56 | 73.90 |
| 90 | Scale / width | 84.60 | 82.84 | 82.84 | 71.79 |
| 90 | Joint | 85.62 | 84.20 | 81.27 | 73.30 |
| 80 | Random mean | 85.14 | 83.64 | 83.64 | 66.97 |
| 80 | Tree SD | 86.02 | 84.40 | 80.73 | 66.80 |
| 80 | Distance | 86.70 | 85.82 | 76.86 | 66.18 |
| 80 | Scale / width | 84.08 | 82.64 | 78.33 | 63.27 |
| 80 | Joint | 86.20 | 85.52 | 78.08 | 65.35 |

Quota-mode selection with adaptive budget intervals; both repeats pooled. Random rows are means over 100 fixed permutations, so absent-source counts can be fractional. All other rows describe their frozen score ordering. Sample coverage is conditional on accepted events; survivor coverage is conditional on publications with accepted events. Zero-if-absent includes all 115 sources. Original-source service is mean_s(C_s/N_s), not an error or safety-failure probability. Per-repeat loss and retained-source worst-case results are in the supplement. Pairwise uncertainty is reported in the text and Fig. 5 rather than inferred from rounded point estimates.
