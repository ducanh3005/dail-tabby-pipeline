# DAiL `bnty_0424` — TIC 158499577 (HD 94871): Joint TESS + SuperWASP Period Fit

- **Hunter:** `ducanh3005`
- **Pipeline Version:** `v1.0.0` (`2026-11-04`)
- **Reproduce:**
  ```bash
  python3 bnty_0424/fit_joint_ephemeris.py
  python3 bnty_0424/verify_bnty_0424.py
  ```

## Contents
- `raw/tess2019058134432-s0009-0000000158499577-0139-s_lc.fits` — MAST TESS SPOC 2-min Sector 9 light curve (`18,187` rows, `16,077` `QUALITY=0`).
- `raw/tess2021065132309-s0036-0000000158499577-0207-s_lc.fits` — MAST TESS SPOC 2-min Sector 36 light curve (`18,066` rows, `15,532` `QUALITY=0`).
- `raw/1SWASP_J105638.34-363449.0.fits` & `.csv` — SuperWASP DR1 (2006–2008) time series (`6,789` points, `tile162048`, CERIT-SC / NASA Exoplanet Archive).
- `raw/1SWASP_J105633.25-363457.2_control.fits` & `.csv` — Nearby SuperWASP control star (`61.8"` WSW, `TIC 158499578`).
- `fit_joint_ephemeris.py` — Self-contained FITS reader + 20-eclipse O–C timing extractor + simultaneous unbinned 38,398-cadence template fitter.
- `results/joint_ephemeris_results.json` — Full machine-readable fit parameters, covariance uncertainties, dataset agreement checks, post-hoc scan peak refutation, O–C table, and Nov–Dec 2026 eclipse predictions.
- `verify_bnty_0424.py` — Automated verification script.
- `SUBMISSION.txt` — Concise submission report (< 5,000 chars).
