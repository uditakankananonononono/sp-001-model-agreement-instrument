# SP-001 - Model Agreement as a Scientific Instrument

## Summary (from `SP-001-model-agreement-instrument/README.md`)


**Status:** SUCCESS against the preregistered gate.

Five diverse classifiers were evaluated with 20x repeated stratified 5-fold cross-validation on the public UCI Wisconsin Diagnostic Breast Cancer dataset. Cross-model disagreement isolated an error-prone subset: the top disagreement quintile had 18.08x the held-out error rate of the remaining predictions (cluster-bootstrap 95% CI 7.56-85.31). Abstaining on that quintile reduced error by 77.5%, from 3.04% to 0.68%, while retaining 80% coverage.

This is a methodological proof of concept, not a clinical diagnostic tool. External validation is required.

## Reproduce

```bash
python3 code/run_analysis.py
```

## Contents
- `protocol/`: gate locked before outcome analysis
- `code/`: complete analysis
- `data/raw/`: original public data and description
- `data/processed/`: held-out predictions
- `results/`: metrics and figure data
- `figures/`: publication-quality plots
- `report/`: full technical report (PDF and Markdown)
- `paper/`: concise research paper

## Contents

- `SP-001-model-agreement-instrument/` - migrated unchanged from `science-program/projects/SP-001-model-agreement-instrument` (18 files)

## Provenance

Split out of the `science-program` repository (source commit `028a7141ed5f951a7b6e6517d4e72768d414a560`) on 2026-09-23. Every file is byte-identical to the source; `MIGRATION_MANIFEST.tsv` lists sha256, original path and new path for each of the 18 files.

Part of Udita Phookan's computational science program: every experiment locks its question, validation design, success gate and failure policy before outcome analysis, and negative results are preserved. Program-wide ledgers and standards live in the `science-program-ledger` repository.
