# DAiL `bnty_0441` — Archival Radial-Velocity Orbit for a Single-Lined Spectroscopic Binary (SB1)

- **Hunter**: `ducanh3005`
- **Pipeline Version**: `sb1-archival-orbit-v1.0.0` (`2026-11-05`)
- **Repository Path**: `https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/bnty_0441`
- **Archival Policy**: 100% public archival spectroscopic records only (`SDSS-IV APOGEE DR17 SAS FITS`, `LAMOST DR7/MRS VizieR J/ApJS/258/26 & V/156/dr7lrs`, `Gaia DR3 I/355/gaiadr3 & I/357/tbosb1`); zero new telescope booking, zero archive-staff contact, zero AAVSO data/contact, and zero individual stellar masses quoted from photometry alone.

---

## 1. Executive Summary & Target Selection

We present complete archival multi-epoch radial-velocity (RV) recoveries and Keplerian orbital solutions for **two independent known single-lined spectroscopic binaries (`SB1`)** whose main catalog entries report only a single combined RV value (or a single observing night):

1. **Primary Target (`2MASS J19241736+4729134` / `Gaia DR3 2129164276754246400` / `KIC 10338279`)**:
   - **Coordinates (ICRS J2000)**: $\text{RA} = 291.07232239^\circ$, $\text{Dec} = +47.48707252^\circ$ ($G = 10.9800$, $J = 10.172$, $K_s = 9.934$, $T_{\text{eff}} = 6353\text{ K}$, $\log g = 4.19$).
   - **Single-Value Published Catalog Records**:
     - `Gaia DR3 (gaia_dr3.gaia_source)`: $\text{RV} = +3.6089 \pm 6.5012\text{ km/s}$ (`rv_nb_transits = 27`, `epoch_rv_released = False` — 1 combined catalog value).
     - `APOGEE DR17 Summary Catalog (III/286/catalog)`: $\text{VHELIO} = -21.1539\text{ km/s}$ ($\text{VSCATTER} = 27.5378\text{ km/s}$, $\text{VERR} = 0.0706\text{ km/s}$ — 1 combined catalog value).
     - `LAMOST MRS (J/ApJS/258/26, ObsID 591803219)`: 1 single observing night (`LMJD = 58031`, $\text{BJD}_{\text{mean}} = 2458031.01260$, 3 consecutive 20-min exposures spanning 26.7 min with weighted mean $\text{RV}_{\text{abs,B}} = -48.4912 \pm 0.4963\text{ km/s}$).
   - **Multi-Phase Archival Epochs Recovered (`raw/apStar-dr17-2M19241736+4729134.fits` & `raw/targetB_2129164276754246400_lamost_mrs.tsv`)**:
     - Direct extraction of the SDSS-IV APOGEE DR17 FITS primary header (`R ~ 22,500`, H-band) recovers **4 distinct nightly visit epochs (`JD 2457510.97991` to `2457513.97382`)** sampling phases $\phi = 0.101, 0.320, 0.540, 0.759$ across an entire $4.549	ext{-d}$ orbital cycle, plus a **5th independent epoch in LAMOST MRS (`ObsID 591803219`)** $520.033	ext{ d}$ ($114.316$ cycles) later at phase $\phi = 0.416$.

2. **Secondary Target (`LAMOST J045121.78+233659.3` / `Gaia DR3 3413610152545407104` / `2MASS J04512177+2336592`)**:
   - **Coordinates (ICRS J2000)**: $\text{RA} = 72.84074017^\circ$, $\text{Dec} = +23.61644528^\circ$ ($G = 11.4535$, $G_{\text{BP}} = 12.2169$, $G_{\text{RP}} = 10.5960$).
   - **Single-Value Published Catalog Record**:
     - `Gaia DR3 (gaia_dr3.gaia_source)`: $\text{RV} = +37.9857 \pm 2.1724\text{ km/s}$ (`rv_nb_transits = 23`, `epoch_rv_released = False`).
   - **Multi-Phase Archival Epochs Recovered (`raw/targetA_3413610152545407104_lamost_mrs.tsv` & `raw/targetA_3413610152545407104_lamost_lrs_dr7.tsv`)**:
     - **66 individual LAMOST MRS exposures across 9 distinct observing nights** (`BJD 2458056.25125` to `2458500.12856`, $\Delta t = 443.87731\text{ d} = 1.321\text{ orbital cycles}$), plus **2 LAMOST DR7 LRS spectra** (`ObsID 100004025` on `MJD 56292`, $\text{RV} = +34.62 \pm 5.48\text{ km/s}$; `ObsID 721606126` on `MJD 58512`, $\text{RV} = +35.36 \pm 5.60\text{ km/s}$).

---

## 2. Archival Observation Log

### 2.1 Target 1 (`2MASS J19241736+4729134` / `Gaia DR3 2129164276754246400`)

| Epoch / Exposure ID | Archive & Instrument | Time (`JD` / `BJD_TDB`) | `MJD` | Orbital Phase $\phi$ ($P = 4.549125\text{ d}$) | $\text{RV}_{\text{helio}}$ ($\text{km/s}$) | $\sigma_{\text{RV}}$ ($\text{km/s}$) | S/N |
|---|---|---|---|---|---|---|---|
| `apVisit-dr17-8670-57510-116.fits` (Visit 1) | SDSS-IV APOGEE DR17 (`apo25m`) | `2457510.97991` | `57510` | `0.1006` | `+12.2187` | `0.0750` | `102.21` |
| `apVisit-dr17-8670-57511-116.fits` (Visit 2) | SDSS-IV APOGEE DR17 (`apo25m`) | `2457511.97941` | `57511` | `0.3203` | `-32.4183` | `0.0721` | `106.88` |
| `apVisit-dr17-8670-57512-116.fits` (Visit 3) | SDSS-IV APOGEE DR17 (`apo25m`) | `2457512.97834` | `57512` | `0.5399` | `-52.7398` | `0.0804` | `95.84` |
| `apVisit-dr17-8670-57513-116.fits` (Visit 4) | SDSS-IV APOGEE DR17 (`apo25m`) | `2457513.97382` | `57513` | `0.7587` | `-14.8869` | `0.0605` | `132.17` |
| `ObsID 591803219` (Exp 1, `HIP9587901`) | LAMOST MRS Blue (`J/ApJS/258/26`) | `2458031.00549` | `58031` | `0.4140` | `-47.8750` | `0.7026` | `10.96` |
| `ObsID 591803219` (Exp 2, `HIP9587901`) | LAMOST MRS Blue (`J/ApJS/258/26`) | `2458031.01476` | `58031` | `0.4160` | `-50.5000` | `1.0244` | `8.30` |
| `ObsID 591803219` (Exp 3, `HIP9587901`) | LAMOST MRS Blue (`J/ApJS/258/26`) | `2458031.02403` | `58031` | `0.4181` | `-47.8750` | `0.9619` | `6.43` |
| **LAMOST Nightly Mean (`LMJD 58031`)** | LAMOST MRS Blue (`N = 3`) | `2458031.01260` | `58031` | `0.4156` | `-48.4912` | `0.4963` | — |

### 2.2 Target 2 (`LAMOST J045121.78+233659.3` / `Gaia DR3 3413610152545407104`) — Nightly Weighted Means (`N = 66` MRS Exposures + `2` LRS Epochs)

| Night (`LMJD` / `MJD`) | Archive & PlanID | $N_{\text{exp}}$ | Mean `BJD` / `JD` | Orbital Phase $\phi$ ($P = 334.8825\text{ d}$) | $\text{RV}_{\text{abs,B}}$ ($\text{km/s}$) | $\sigma_{\text{RV,B}}$ ($\text{km/s}$) | $\text{RV}_{\text{abs,R}}$ ($\text{km/s}$) |
|---|---|---|---|---|---|---|---|
| `MJD 56292` (`2012-12-31`) | LAMOST DR7 LRS (`ObsID 100004025`) | `1` | `2456292.50000` | `0.8582` | `+34.6200` | `5.4800` | — |
| `LMJD 58056` (`2017-10-29`) | LAMOST MRS (`HIP2274301`) | `5` | `2458056.30223` | `0.1252` | `+14.8828` | `0.3586` | `+15.5078` |
| `LMJD 58057` (`2017-10-30`) | LAMOST MRS (`HIP2274301`) | `5` | `2458057.30970` | `0.1282` | `+15.3054` | `0.3602` | `+15.9937` |
| `LMJD 58058` (`2017-10-31`) | LAMOST MRS (`HIP2274301`) | `6` | `2458058.31006` | `0.1312` | `+16.6698` | `0.3597` | `+17.0495` |
| `LMJD 58087` (`2017-11-29`) | LAMOST MRS (`HIP2274301`) | `13` | `2458087.20723` | `0.2175` | `+27.5960` | `0.3557` | `+28.4387` |
| `LMJD 58092` (`2017-12-04`) | LAMOST MRS (`HIP2274301`) | `15` | `2458092.19138` | `0.2323` | `+28.8584` | `0.3568` | `+29.0646` |
| `LMJD 58115` (`2017-12-27`) | LAMOST MRS (`HIP2274301`) | `10` | `2458115.14631` | `0.3009` | `+35.6332` | `0.3567` | `+35.8656` |
| `LMJD 58152` (`2018-02-02`) | LAMOST MRS (`HIP2274301`) | `3` | `2458151.96822` | `0.4109` | `+40.5221` | `0.3964` | `+41.7917` |
| `LMJD 58422` (`2018-10-30`) | LAMOST MRS (`TD045334N231856K01`) | `5` | `2458422.31404` | `0.2181` | `+27.4141` | `0.3728` | `+28.8656` |
| `LMJD 58500` (`2019-01-16`) | LAMOST MRS (`TD045334N231856K01`) | `4` | `2458500.10680` | `0.4504` | `+44.0984` | `0.3787` | `+44.7734` |
| `MJD 58512` (`2019-01-29`) | LAMOST DR7 LRS (`ObsID 721606126`) | `1` | `2458512.50000` | `0.4874` | `+35.3600` | `5.6000` | — |

---

## 3. Orbital Solutions, Bounds & Parameter Identifiability Analysis

### 3.1 What 2 Epochs Alone Constrain vs Leave Unconstrained
Given only two RV epochs $(t_1, v_1)$ and $(t_2, v_2)$ at distinct phases:
1. **Strictly Constrained Lower Bound on $K_1$**: Since $v(t) = \gamma + K_1[\cos(\nu(t)+\omega) + e\cos\omega]$ varies over an amplitude of $2K_1$, any pair of epochs establishes a model-independent lower bound:
   $$K_1 \ge \frac{|v_1 - v_2|}{2}$$
   - For Target 1: $|\text{VHELIO}_1 - \text{VHELIO}_3| = |12.2187 - (-52.7398)| = 64.9585\text{ km/s} \implies K_1 \ge 32.4793\text{ km/s}$ (and between APOGEE Visit 1 and LAMOST MRS: $|12.2187 - (-48.4912)| = 60.7099\text{ km/s} \implies K_1 \ge 30.3550\text{ km/s}$).
   - For Target 2: $|\text{RV}_{\text{LMJD 58500}} - \text{RV}_{\text{LMJD 58056}}| = |44.0984 - 14.8828| = 29.2156\text{ km/s} \implies K_1 \ge 14.6078\text{ km/s}$.
2. **Strictly Bounded Interval on Systemic Velocity $\gamma$**: For a circular orbit with semi-amplitude $K_1$, $\gamma \in [\max(v_1, v_2) - K_1,\; \min(v_1, v_2) + K_1]$.
3. **Parameters Unconstrained from 2 Epochs Alone**: A general eccentric Keplerian SB1 orbit has $6$ parameters $(P, \gamma, K_1, e, \omega, T_0)$ (or $4$ for a circular orbit), leaving $4$ (or $2$) degrees of freedom underdetermined from $N=2$ measurements:
   - **Period $P$**: Unconstrained due to integer cycle-count aliasing $\Delta t = (n \pm \Delta\phi) P$ for all $n \in \mathbb{Z}_{\ge 0}$.
   - **Eccentricity $e$ and Periastron Argument $\omega$**: Completely degenerate with $(K_1, \gamma)$ without phase coverage across both quadratures and ingress/egress slopes.
   - **Individual Component Masses $(M_1, M_2)$ and Inclination $i$**: Even with a complete SB1 radial-velocity curve, only the spectroscopic mass function $f(M) = (M_2 \sin i)^3 / (M_1 + M_2)^2$ and projected primary semi-major axis $a_1 \sin i$ are dynamically determined; individual masses are never quoted from photometry alone.

### 3.2 Solved Keplerian Orbits (Multi-Epoch Archival Fits vs Gaia DR3 `nss_two_body_orbit`)

| Parameter | Target 1 (`2MASS J19241736+4729134`) Joint APOGEE+LAMOST Circular Fit | Target 1 Joint Eccentric Fit | Target 1 Gaia DR3 `tbosb1` Ref | Target 2 (`LAMOST J045121.78+233659.3`) 66-Exp LAMOST MRS Eccentric Fit | Target 2 Gaia DR3 `tbosb1` Ref |
|---|---|---|---|---|---|
| **Period $P$ ($\text{d}$)** | `4.549125 +/- 0.000213` | `4.549270` | `4.549792 +/- 0.000199` | `334.8825 +/- 0.6596` | `335.9786 +/- 1.4562` |
| **Systemic Velocity $\gamma$ ($\text{km/s}$)** | `-17.0665 +/- 0.0862` | `-17.2458` | `-17.5182 +/- 0.4835` | `+32.0939 +/- 2.0575` | `+33.9808 +/- 0.6146` |
| **Semi-Amplitude $K_1$ ($\text{km/s}$)** | `36.5357 +/- 0.1303` | `36.2194` | `36.0889 +/- 0.5865` | `20.5891 +/- 2.6548` | `17.8735 +/- 1.7560` |
| **Eccentricity $e$** | `0.0 (fixed)` | `0.02015` | `0.02158 +/- 0.01634` | `0.3273 +/- 0.0450` | `0.3225 +/- 0.0565` |
| **Argument of Periastron $\omega$ ($^\circ$)** | — | `149.32` | `119.82 +/- 54.76` | `159.19 +/- 6.64` | `150.81 +/- 3.99` |
| **Reference Epoch $T_0$ / $T_{\text{peri}}$ (`JD`)** | `2457510.52237 +/- 0.00225` ($T_{\max}$) | `2457389.58275` ($T_{\text{peri}}$) | `2457389.18362 +/- 0.69464` | `2458014.3821 +/- 9.3785` ($T_{\text{peri}}$) | `2457347.7135 +/- 2.6499` |
| **Mass Function $f(M)$ ($M_\odot$)** | `0.022988` | `0.022383` | `0.022131` | `0.255528` | `0.168731` |
| **Projected Axis $a_1 \sin i$ ($R_\odot$)** | `3.28517` | `3.25616` | `3.24461` | `128.7791` | `112.4418` |

---

## 4. Reproducibility & Verification

Run the orbit solver and deterministic verification suite from the repository root:
```bash
python bnty_0441/solve_sb1_orbit.py
python bnty_0441/verify_bnty_0441.py
```
