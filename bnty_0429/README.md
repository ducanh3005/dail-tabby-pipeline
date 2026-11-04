# DAiL `bnty_0429` — `TIC 158499577` (`HD 94871`): Neighbour V-Band Flux Bound by SED Fit

- **Hunter:** `ducanh3005`
- **Method Version:** `1.0.0` (`2026-11-04`)
- **Target:** `TIC 158499577` (`HD 94871` / `HIP 53499` / `Gaia DR3 5401019098113741568` / `2MASS J10563835-3634493` / `SkyMapper DR4 83800407`)
- **Close Neighbours:**
  - `TIC 942348495` (`sep = 1.8203"`, `Gaia DR2 5401019098111264256` $\to$ `Gaia DR3 5401019098111264000`)
  - `TIC 942348496` (`sep = 2.3044"`, `Gaia DR2 5401019098111267840` $\to$ `Gaia DR3 5401019098111272064`)

## Reproduction (Zero API Keys Required)

```bash
python3 bnty_0429/fit_sed_vband_bound.py
python3 bnty_0429/verify_bnty_0429.py
```

## Directory Contents
- `raw/mast_tic_3stars.json`, `raw/mast_tic_cone90.json` — Raw MAST TIC v8.2 queries.
- `raw/esa_gaiadr3_cone90.json`, `raw/esa_gaiadr3_gspc_3stars.json`, `raw/esa_gaiadr2_cone90.json`, `raw/esa_dr2_neighbourhood_3stars.json` — Raw ESA Gaia DR3/DR2/GSPC TAP queries.
- `raw/esa_2mass_cone90.json` — Raw 2MASS All-Sky PSC query (`gaiadr1.tmass_original_valid`).
- `raw/skymapper_tap_dr4_cone90.tsv`, `raw/skymapper_tap_dr2_cone90.tsv`, `raw/skymapper_tap_dr1_cone90.tsv` — Raw SkyMapper TAP DR4/DR2/DR1 queries.
- `fit_sed_vband_bound.py` — Multi-band SED fitting and 100,000-trial Monte Carlo V-band flux bound calculator.
- `verify_bnty_0429.py` — Automated verification script asserting all numerical claims and positive controls.
- `results/sed_vband_bound_results.json` — Full machine-readable output.
- `SUBMISSION.txt` — Filed DAiL submission text.
