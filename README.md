# DAiL Tabby-Class Anomalous Dipper Pipeline (`bnty_0333` & `bnty_0269`)

Pure-Python standard-library verification pipeline, raw MAST FITS payloads, live TAP/VizieR/SIMBAD
catalogue evidence with positive controls, empirical TPF stamp-orientation proofs, layout-free
`MOM_CENTR` cross-checks, like-for-like `P` vs `2P` BLS alias tests, neighbour EB light-curve
exclusions, deterministic submission generators, and live-archive claim checker.

## Targets

| Bounty | Target | Coordinates (ICRS) | Quarters Analyzed | Primary Dip (PDCSAP / SAP) | TPF Layout A `T1` | Max Shift (TPF / `MOM_CENTR`) | Dossier |
|---|---|---|---|---|---|---|---|
| `bnty_0333` | **KIC 7431659** (`2MASS J19092969+4301384`) | `287.373720, +43.027359` | `1/1` (`Q7`, `4,226` cadences) | `5.283%` box (`5.361%` pk) / `5.119%` box (`5.203%` pk) | `1.0000000661` | `0.439 mpix` / `0.775 mpix` | [`data/bnty0333/kic7431659/DOSSIER.md`](data/bnty0333/kic7431659/DOSSIER.md) |
| `bnty_0269` | **KIC 11126267** (`SPOCS 2191`) | `285.599240, +48.723270` | `14/14` (`Q1-Q17`, `51,502` cadences) | `14.340%` box (`19.323%` pk) / `14.313%` box (`19.284%` pk) | `1.0000000181` | `0.769 mpix` / `0.306 mpix` | [`data/bnty0269/kic11126267/DOSSIER.md`](data/bnty0269/kic11126267/DOSSIER.md) |

## Reproduce From a Fresh Clone (Zero Third-Party Dependencies, No API Key)

```bash
python3 src/fetch_mast_payloads.py   # verify/download raw MAST llc.fits & lpd-targ.fits
python3 src/run_pipeline.py          # run 7-gate battery -> write JSON evidence files
python3 src/build_submissions.py     # deterministically render SUBMISSION.txt & DOSSIER.md
python3 scripts/check_claims.py      # re-query live archives & verify byte-for-byte agreement
```
