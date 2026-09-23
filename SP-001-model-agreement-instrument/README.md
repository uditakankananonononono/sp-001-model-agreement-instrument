# SP-001 - Model Agreement as a Scientific Instrument

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
