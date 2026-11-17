# RAC-956 active research status

Last update: 2026-10-24. This file records the user's current direction; historical audit and optimization plans remain provenance only.

**Active title:** Feature Representation and Explanation Stability in Cross-Study Prediction of Recycled Aggregate Concrete Compressive Strength.

**Active main line:** Feature representation → Cross-study generalization → Explainability → Explanation stability.

- Freeze cs_v1: 980 candidates, A=603/B=119/C=258, 722 modeling rows; 563 development and 159 fixed holdout.
- Stage 2 complete: six families, three representations, 990 existing Optuna trials. Preserve all valid results; do not repeat the search.
- Stage 3 results/reports: `reports/stage3/`; source tables, exact SHAP, material-block checks, models and publication drafts: `results/modeling/stage3/`.
- Do not resume exhaustive source-paper auditing or change inclusion rules to improve scores.
- Stage 4 complete: the 159-row holdout was evaluated in one locked prediction batch on 2026-10-23. It is consumed and must not guide further model development. Source/group/recipe overlap with development was zero; this is an internal source-disjoint holdout, not newly collected external data.
- Final XGBoost Raw/Physics/Hybrid R²: -0.100/0.066/0.046; RMSE: 20.065/18.487/18.678 MPa. Every learned model had higher MAE than Dummy. All paired representation RMSE intervals included zero. Preserve these unfavorable results without retuning.
- Manuscript v1.0, five main figures, five supplementary figures and 22 tables: `manuscript/v1.0/`. Integration, final evaluation, literature comparison and remaining issues: `reports/stage4/`. Next activity is scientific manuscript review and author/repository metadata completion.
- NSGA-II is not a required part of the main paper and was not executed in Stage 3.
- Pre-submission v1.1 complete: manuscript/v1.1 and reports/revision_v1.1. Two added training-background configurations on the same30development outer models retained Binder first in30/30each; no fits/HPO/holdout predictions. Independent original-game check and isolated raw-to-freeze byte reproduction passed. Overall submission readiness is CONDITIONAL_PASS pending author declarations, public archive and final journal confirmation/formatting; full-text access limits for Miao2024/Hassan2026 remain explicit.
- Do not presume higher R², Hybrid superiority, severe explanation instability, or causal materials mechanisms. Include all planned null and unfavorable findings.
- Submission Master v1.2 production complete: manuscript/v1.2, reports/submission_v1.2 and deliverables/RAC956_Submission_Master_v1.2_Complete.zip. Science Lock, actual image embedding (5 main + 5 SI), overlap audit and GitHub-ready packaging PASS; overall CONDITIONAL_PASS pending author/declaration/license confirmation, actual repository/archive links and final portal/metadata-layout clearance. No GitHub publication, model fit, HPO or new holdout prediction performed. Current official 2026 publisher format is single-column with numerical citations.

- 2026-10-29: User authorized GitHub Desktop creation and private upload. Repository: https://github.com/HU18164053837-ai/RAC-Feature-Representation-Explanation-Stability; main bbc95a0cbaaef4440c7eaa291ecc1f786e8513d9. All 799 original candidate files match Git blobs byte for byte; .gitattributes added solely to disable line-ending conversion. Private upload is complete; no public archive DOI or submission readiness is implied. Original v1.2 deliverable ZIPs remain unchanged.
