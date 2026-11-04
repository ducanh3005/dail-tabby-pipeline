# DAiL `bnty_0426` — TIC 158499577 (HD 94871): Independent Re-Fold, Different Code

- **Hunter:** `ducanh3005`
- **Pipeline Version:** `v1.0.0` (`2026-11-04`)
- **Reproduce:**
  ```bash
  python3 bnty_0426/independent_refold.py
  python3 bnty_0426/verify_bnty_0426.py
  ```

## Contents
- `raw/tess2019058134432-s0009-0000000158499577-0139-s_lc.fits` — MAST TESS SPOC 2-min Sector 9 light curve.
- `raw/tess2021065132309-s0036-0000000158499577-0207-s_lc.fits` — MAST TESS SPOC 2-min Sector 36 light curve.
- `raw/1SWASP_J105638.34-363449.0.fits` & `.csv` — SuperWASP DR1 (2006–2008) time series (`6,789` pts).
- `raw/1SWASP_J105633.25-363457.2_control.fits` & `.csv` — Nearby SuperWASP control star (`61.8"` WSW).
- `independent_refold.py` — Independent Tukey-biweight detrender + Lafler–Kinman String-Length / Stellingwerf PDM period-finder + multi-aperture/multi-window fold engine.
- `results/independent_refold_results.json` — Complete machine-readable folded depths, per-event depths (all 8 TESS events + all 19 SuperWASP event windows with $\ge 3$ points), quadrature controls, and quantified discrepancies vs house numbers.
- `verify_bnty_0426.py` — Automated verifier.
- `SUBMISSION.txt` — Concise submission report (< 5,000 chars).
