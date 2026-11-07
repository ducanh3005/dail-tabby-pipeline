# DAiL `bnty_0392` & `bnty_0502` — Unexplained Variable Star in ZTF (`ZTF18aaxioyg` / `Gaia DR3 2068537514833439104` / `TIC 193573083`)

Reproducibility bundle for DAiL bounty **`bnty_0392`** (*"DISCOVERY: Unexplained variable star in ZTF or ASAS-SN"*) and **`bnty_0502`** (*"FIX: bnty_0392 YSO disclosure + dipper case"*).
- **Complete Repro Bundle URL:** `https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/bnty_0392`

## 1. Target Identification, Cygnus-Plane Location & Class II YSO IR Colors
- **ZTF Object ID:** `ZTF18aaxioyg`
- **Gaia DR3 ID:** `Gaia DR3 2068537514833439104` (`sep = 0.1367"`)
- **TESS Input Catalog ID:** `TIC 193573083` (`Tmag = 15.2969`, `Teff = 4272 K`, `R_* = 1.2647 R_sun`, `M_* = 0.67 M_sun`)
- **Coordinates (J2000 & Galactic):** `RA = 306.046612°`, `Dec = +42.285800°` (`20h24m11.19s +42°17'08.9"`), Galactic **`l = 80.0250°`, `b = +2.7260°`** in the Cygnus Galactic plane at **`d = 972.6 ± 33.9 pc`** (`parallax = 1.0281 ± 0.0358 mas`, near the outer Cygnus X / Cygnus OB2 star-forming complex), `ruwe = 1.0525`, `non_single_star = 0`, `phot_variable_flag = "NOT_AVAILABLE"`.
- **2MASS & AllWISE Magnitudes and Class II YSO Colors (`mast_tic_cone.json`):**
  - `2MASS J20241119+4217091`: `J = 13.608`, `H = 12.641`, `K = 11.975` -> **`J - H = 0.967 mag`**, **`H - K = 0.666 mag`**.
  - `AllWISE J202411.21+421709.2`: `W1 = 10.949`, `W2 = 10.242`, `W3 = 8.239`, `W4 = 6.911` -> **`W1 - W2 = 0.707 mag`**, **`W2 - W3 = 2.003 mag`**, **`W1 - W4 = 4.038 mag`** (placing the host inside the Koenig & Leisawitz 2014 Class II YSO / dusty circumstellar disk color locus).

## 2. Full ALeRCE Broker Classifier Disclosure (`alerce_ztf18aaxioyg_raw.json`)
- **Stochastic & Full Light-Curve Classifiers Rank `YSO` #1 (`0.740–0.990` across 11 versions):**
  - `lc_classifier (lc_classifier_1.1.13)`: `YSO = 0.7401` (rank 1)
  - `LC_classifier_BHRF_forced_phot(beta) (1.1.1)`: `YSO = 0.7490` (rank 1)
  - `LC_classifier_BHRF_forced_phot(beta) (1.1.4)`: `YSO = 0.7677` (rank 1)
  - `LC_classifier_BHRF_forced_phot(beta) (2.0.0)`: `YSO = 0.7915` (rank 1)
  - `LC_classifier_BHRF_forced_phot(beta) (1.1.5)`: `YSO = 0.8128` (rank 1)
  - `lc_classifier_BHRF_forced_phot (2.1.0)`: `YSO = 0.8394` (rank 1)
  - `LC_classifier_ATAT_forced_phot(beta) (0.3.1)`: `YSO = 0.8775` (rank 1)
  - `lc_classifier_BHRF_forced_phot_stochastic (2.1.0)`: `YSO = 0.8780` (rank 1)
  - `lc_classifier (hierarchical_rf_1.1.0)`: `YSO = 0.8928` (rank 1)
  - `lc_classifier_stochastic (hierarchical_rf_1.1.0)`: `YSO = 0.9600` (rank 1)
  - `LC_classifier_ATAT_forced_phot(beta) (0.3.4)`: `YSO = 0.9736` (rank 1)
  - `LC_classifier_ATAT_forced_phot(beta) (0.3.6)`: `YSO = 0.9828` (rank 1)
  - `LC_classifier_ATAT_forced_phot(beta) (1.0.0)`: `YSO = 0.9896` (rank 1)
- **Conflicting Rank-1 Classifications in Other ALeRCE Branches:**
  - Two forced-photometry beta classifiers rank **`CV/Nova` #1**: `ATAT (0.2.0)` (`CV/Nova = 0.5796` rank 1 vs `YSO = 0.4147` rank 2) and `BHRF (1.0.7)` (`CV/Nova = 0.2191` rank 1 vs `YSO = 0.1240` rank 2).
  - Periodic sub-classifiers rank **`EA` (`0.266`)** and **`CEP` (`0.326`)** #1; transient sub-classifiers rank **`SNII` (`0.334`)** / **`SNIIn` (`0.320`)** #1; stamp classifiers rank **`VS` (`0.411–0.921`)** and **`AGN` (`0.658–0.728`)** #1.

## 3. Why `ZTF18aaxioyg` Remains Unexplained Rather Than a Standard Classical YSO "Dipper"
While the Cygnus location (`d = 972.6 pc`, `b = +2.73°`), Class II WISE excess (`W1 - W2 = 0.707`, `W2 - W3 = 2.003`, `W1 - W4 = 4.038`), and ALeRCE stochastic probabilities (`0.74–0.99`) establish a dusty young star environment, four quantitative properties computed in `verify_bnty_0392.py` demonstrate why its light curve does **not** fit the standard classical T Tauri inner-disk "dipper" mechanism (Cody et al. 2014; Ansdell et al. 2016; Bredall et al. 2020) and remains an uncataloged, anomalous variable:
1. **Bimodal `1.78 mag` Excursion Combining `73.9%` Fades with `+71.6%` Brightening Bursts (`Gskew = +0.385/+0.399`):** Classical dippers exhibit `0.1–0.8 mag` (`10–50%` flux) occultation dips downward from a flat photospheric ceiling (`M > +0.5`, `Gskew > +0.8`). Across `717` clean (`254` strict) ZTF epochs, `ZTF18aaxioyg` spans **`1.7751 mag` (`zg`) and `1.7779 mag` (`zr`) peak-to-peak**, combining deep **`+1.4571 mag` (`73.87%` flux loss)** fades below the strict median (`18.4515` vs `16.9944`) with **`-0.5866 mag` (`+71.6%` flux surge)** brightening bursts above the `all_clean` median (`16.6764` vs `17.2630` in `zg`; `15.4186` vs `15.9930` = `-0.5744 mag` in `zr`), yielding a hybrid burst+occultation symmetry (`Gskew_1 = +0.3847`, `Gskew_2 = +0.3995`) that bridges dipper and EXor/accretion-burst regimes.
2. **Super-Rayleigh Selective Dimming (`Δzg / Δzr = 1.435–1.475`) Coupled with Reddening-During-Outburst Color Inversion:** Across the `49` same-night `zg + zr` pairs (median baseline `zg - zr = 1.0851 mag`), the three deepest simultaneous fades (`MJD 60092.34`, `60449.45`, `59470.25`) exhibit selective extinction ratios **`Δzg / Δzr = 1.464`, `1.435`, and `1.475`** (`zg - zr = 1.5469, 1.4832, 1.4573 mag`). This is significantly steeper than both standard `R_V = 3.1` ISM dust (`A_g / A_r = 1.31`) and evolved large-grain Class II inner-disk dippers (`Δg / Δr ≈ 1.05–1.25`), implying sub-micron (`a < 0.15 um`) Rayleigh-scattering condensations. Conversely, during the `MJD 59883.17` brightening burst (`zg = 16.6968`, `zr = 15.5644`), the star **reddens while brightening** (`Δzg = -0.2976 mag` vs `Δzr = -0.3449 mag`, `zg - zr = 1.1324 mag`, `+0.0473 mag` redder than median), contradicting both hot accretion spots (which turn strongly bluer when brighter) and dust-screen clearing (which must also turn bluer when brighter).
3. **Absence of Inner-Disk Corotation Periodicity & Dominant Long-Timescale (`100–365 d`) MHPS Power:** Classical dippers are quasi-periodic at the inner-disk Keplerian corotation period (`P ≈ 2–10 d`). `ZTF18aaxioyg` shows no true rotational/corotation period (`Period_band_1 = 0.0556 d` and `Period_band_2 = 0.9959 d` are pure `1 d` diurnal aliases with `Psi_eta = 1.90 / 1.64`), while its Mexican-Hat Power Spectrum (`MHPS_ratio = 3.79` in `zg`, `4.10` in `zr`; `MHPS_low_365_2 = 30.77` vs `MHPS_high_30_2 = 9.29`) is dominated by `100–365 d` outer-disk warps superposed with fast `GP_DRW_tau = 1.55–2.67 d` collapses (`>1.0 mag` in `48 h`).
4. **Completely Uncataloged in Gaia DR3, SIMBAD, VSX, and Cygnus YSO Surveys:** Despite `924` ZTF epochs, `Gaia DR3 2068537514833439104` has `phot_variable_flag = "NOT_AVAILABLE"` (while `5` neighboring stars within `120"` are flagged `VARIABLE`), and has no classification in SIMBAD, VSX, or published Cygnus YSO dipper catalogs.

## 4. Reproducing the Vetting Results
```bash
python bnty_0392/verify_bnty_0392.py
```
