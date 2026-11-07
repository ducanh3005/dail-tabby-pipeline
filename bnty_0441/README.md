# DAiL `bnty_0441` & `bnty_0507` — Archival Radial-Velocity Orbit for a Single-Lined Spectroscopic Binary (SB1)

- **Hunter**: `ducanh3005`
- **Pipeline Version**: `sb1-archival-orbit-v1.1.0` (`2026-11-07`)
- **Repository Path**: `https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/bnty_0441`
- **Archival Policy**: 100% public archival spectroscopic records only (`SDSS-IV APOGEE DR17 SAS FITS`, `LAMOST DR7/MRS VizieR J/ApJS/258/26 & V/156/dr7lrs`, `Gaia DR3 I/355/gaiadr3 & I/357/tbosb1`); zero new telescope booking, zero archive-staff contact, zero AAVSO data/contact, and zero individual stellar masses quoted from photometry alone.

---

## 1. Executive Summary & Target Selection

We present complete archival multi-epoch radial-velocity (RV) recoveries and Keplerian orbital solutions for **two independent known single-lined spectroscopic binaries (`SB1`)** whose main catalog entries report only a single combined RV value (or a single observing night):

1. **Primary Target (`2MASS J19241736+4729134` / `Gaia DR3 2129164276754246400` / `KIC 10338279`)**:
   - **Coordinates & Stellar vs RV-Template Parameters (ICRS J2000)**: $\text{RA} = 291.07232239^\circ$, $\text{Dec} = +47.48707252^\circ$ ($G = 10.9800$, $J = 10.172$, $K_s = 9.934$). Calibrated APOGEE DR17 ASPCAP stellar parameters (`raw/targetB_2129164276754246400_apogee_dr17.tsv`): **$T_{\text{eff,ASPCAP}} = 6151.9\text{ K}$, $\log g_{\text{ASPCAP}} = 3.648$, catalog $[\text{Fe/H}] = -0.3871$** (whereas the FITS primary header `RV_TEFF = 6353.3 K`, `RV_LOGG = 4.1887`, `RV_FEH = -0.3907` are uncalibrated cross-correlation RV-template grid values).
   - **Single-Value Published Catalog Records**:
     - `Gaia DR3 (gaia_dr3.gaia_source)`: $\text{RV} = +3.6089 \pm 6.5012\text{ km/s}$ (`rv_nb_transits = 27`, `epoch_rv_released = False` — 1 combined catalog value).
     - `APOGEE DR17 Summary Catalog (III/286/catalog)`: $\text{VHELIO} = -21.1539\text{ km/s}$ ($\text{VSCATTER} = 27.5378\text{ km/s}$, $\text{VERR} = 0.0706\text{ km/s}$ — 1 combined catalog value).
     - `LAMOST MRS (J/ApJS/258/26, ObsID 591803219)`: 1 single observing night (`LMJD = 58031`, $\text{BJD}_{\text{mean}} = 2458031.01260$, 3 consecutive 20-min exposures spanning 26.7 min with weighted mean $\text{RV}_{\text{abs,B}} = -48.4912 \pm 0.4963\text{ km/s}$).
   - **Multi-Phase Archival Epochs Recovered (`raw/apStar-dr17-2M19241736+4729134.fits` & `raw/targetB_2129164276754246400_lamost_mrs.tsv`)**:
     - Direct extraction of the SDSS-IV APOGEE DR17 FITS primary header (`R ~ 22,500`, H-band) recovers **4 distinct nightly visit epochs (`JD 2457510.97991` to `2457513.97382`)** sampling phases $\phi = 0.1006, 0.3203, 0.5399, 0.7587$ (at $P = 4.549125\text{ d}$), plus a **5th independent epoch in LAMOST MRS (`ObsID 591803219`)** $520.033\text{ d}$ ($114.316$ cycles at $P = 4.549125\text{ d}$) later at phase $\phi = 0.4156$.
   - **4-Visit-Only Fit & Cycle-Count Alias Ladder Disclosure (`n_cyc = 110..118`)**:
     - **4-Visit APOGEE Fit (`DOF = 0`, $\chi^2 = 0$)**: Fitting 4 circular parameters $(P, \gamma, K_1, T_0)$ to 4 APOGEE visits ($P = 4.458256\text{ d}$, $\gamma = -17.9154\text{ km/s}$, $K_1 = 35.9616\text{ km/s}$, $T_0 = 2457510.5703$, $\chi^2 = 0.0$) has **zero degrees of freedom (`DOF = 0`) and carries no independent statistical period constraint alone**.
     - **520-Day Cycle-Count Alias Ladder**: Across the $520.03\text{-d}$ gap between APOGEE and the single LAMOST night, the 7 archival exposures alone admit discrete integer-cycle aliases spanning **$\sim 4.39\text{ to }4.55\text{ d}$** ($\Delta P_{\text{alias}} \approx 0.039\text{ d}$ per cycle step across $n_{\text{cyc}} = 110..118$). On an unconstrained grid search over $n_{\text{cyc}} = 110..118$, the lowest $\chi^2$ occurs at **$n_{\text{cyc}} = 116$ ($P = 4.464095\text{ d}$, $\chi^2 = 3.86$ on the post-trough branch; $P = 4.470775\text{ d}$, $\chi^2 = 3.79$ on the pre-trough branch)**, whereas **$n_{\text{cyc}} = 114$ gives $P = 4.549125\text{ d}$ ($\chi^2 = 11.37$)**. We state plainly that **$P = 4.549125\text{ d}$ is the Gaia-consistent alias adopted using Gaia DR3's published period ($P = 4.549792\text{ d}$) as the cycle-count prior**; $\pm 0.000213\text{ d}$ is the local within-alias precision for fixed $n_{\text{cyc}} = 114$, while the alias-aware archival bound from the 7 exposures alone is **$P \in [4.395, 4.549]\text{ d}$** (specifically $P = 4.464\text{ d}$ unconstrained vs $P = 4.5491\text{ d}$ Gaia-prior).

2. **Secondary Target (`LAMOST J045121.78+233659.3` / `Gaia DR3 3413610152545407104` / `2MASS J04512177+2336592`)**:
   - **Coordinates (ICRS J2000)**: $\text{RA} = 72.84074017^\circ$, $\text{Dec} = +23.61644528^\circ$ ($G = 11.4535$, $G_{\text{BP}} = 12.2169$, $G_{\text{RP}} = 10.5960$).
   - **Single-Value Published Catalog Record**:
     - `Gaia DR3 (gaia_dr3.gaia_source)`: $\text{RV} = +37.9857 \pm 2.1724\text{ km/s}$ (`rv_nb_transits = 23`, `epoch_rv_released = False`).
   - **Multi-Phase Archival Epochs Recovered (`raw/targetA_3413610152545407104_lamost_mrs.tsv` & `raw/targetA_3413610152545407104_lamost_lrs_dr7.tsv`)**:
     - **66 individual LAMOST MRS exposures across 9 distinct observing nights** (`BJD 2458056.25125` to `2458500.12856`, $\Delta t = 443.87731\text{ d}$, which spans **$1.3211$ orbital cycles using Gaia $P = 335.9786\text{ d}$** or **$1.3255$ orbital cycles using our fitted $P = 334.8825\text{ d}$**), plus **2 LAMOST DR7 LRS spectra** (`ObsID 100004025` on `MJD 56292`, $\text{RV} = +34.62 \pm 5.48\text{ km/s}$; `ObsID 721606126` on `MJD 58512`, $\text{RV} = +35.36 \pm 5.60\text{ km/s}$).

---

## 2. Archival Observation Log & Target 1 Alias Ladder

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

#### Target 1 Cycle-Count Alias Ladder (`n_cyc = 110..118` across $\Delta t = 520.033\text{ d}$)

| Cycle Count $n_{\text{cyc}}$ | Pre-Trough Branch $P$ ($\text{d}$) | $\gamma$ ($\text{km/s}$) | $K_1$ ($\text{km/s}$) | $\chi^2$ (Pre-Trough) | Post-Trough Branch $P$ ($\text{d}$) | $\chi^2$ (Post-Trough) | Notes |
|---|---|---|---|---|---|---|---|
| `110` | `4.714487` | `-15.4767` | `37.6779` | `55.93` | `4.706435` | `3.99` | — |
| `111` | `4.672029` | `-15.8904` | `37.3731` | `41.61` | `4.664180` | `3.97` | — |
| `112` | `4.630330` | `-16.2930` | `37.0814` | `29.29` | `4.622676` | `3.95` | — |
| `113` | `4.589368` | `-16.6849` | `36.8024` | `19.15` | `4.581902` | `3.92` | — |
| **`114` (Gaia-Prior Alias)** | **`4.549125`** | **`-17.0665`** | **`36.5357`** | **`11.37`** | `4.541840` | `3.90` | **Matches Gaia DR3 $P = 4.549792\text{ d}$** |
| `115` | `4.509582` | `-17.4380` | `36.2811` | `6.16` | `4.502472` | `3.88` | — |
| **`116` (Unconstrained Best)** | **`4.470775`** | **`-17.8002`** | **`36.0410`** | **`3.79`** | **`4.463799` (`~4.464`)** | **`3.86`** | **Unconstrained minimum $\chi^2$** |
| `117` | `4.432523` | `-18.1526` | `35.8061` | `4.27` | `4.425799` | `3.84` | — |
| `118` | `4.394973` | `-18.4962` | `35.5851` | `8.05` | `4.388446` | `3.82` | — |

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
1. **Strictly Constrained Lower Bound on $K_1$**: $K_1 \ge |v_1 - v_2| / 2$.
   - Target 1: $|\text{VHELIO}_1 - \text{VHELIO}_3| = 64.9585\text{ km/s} \implies K_1 \ge 32.4793\text{ km/s}$ ($|\text{VHELIO}_1 - \text{RV}_{\text{LAMOST}}| = 60.7099\text{ km/s} \implies K_1 \ge 30.3550\text{ km/s}$).
   - Target 2: $|\text{RV}_{\text{LMJD 58500}} - \text{RV}_{\text{LMJD 58056}}| = |44.0984 - 14.8828| = 29.2156\text{ km/s} \implies K_1 \ge 14.6078\text{ km/s}$.
2. **Strictly Bounded Interval on Systemic Velocity $\gamma$**: $\gamma \in [\max(v_1, v_2) - K_1,\; \min(v_1, v_2) + K_1]$.
3. **Parameters Unconstrained from 2 Epochs Alone**: Period $P$ (aliased across integer cycle counts $n$), eccentricity $e$ and periastron argument $\omega$, and individual component masses $(M_1, M_2)$ and inclination $i$.

### 3.2 Solved Keplerian Orbits (Multi-Epoch Archival Fits vs Gaia DR3 `nss_two_body_orbit`)

| Parameter | Target 1 (`2MASS J19241736+4729134`) Unconstrained Best Alias ($n_{\text{cyc}}=116$) | Target 1 Gaia-Prior Alias ($n_{\text{cyc}}=114$) | Target 1 Gaia DR3 `tbosb1` Ref | Target 2 (`LAMOST J045121.78+233659.3`) 66-Exp LAMOST MRS Eccentric Fit | Target 2 Gaia DR3 `tbosb1` Ref |
|---|---|---|---|---|---|
| **Period $P$ ($\text{d}$)** | `4.464095` / `4.470775` (alias range `4.395–4.549`) | `4.549125 +/- 0.000213` (within-alias) | `4.549792 +/- 0.000199` | `334.8825 +/- 0.6596` | `335.9786 +/- 1.4562` |
| **Systemic Velocity $\gamma$ ($\text{km/s}$)** | `-17.8002` | `-17.0665 +/- 0.0862` | `-17.5182 +/- 0.4835` | `+32.0939 +/- 2.0575` | `+33.9808 +/- 0.6146` |
| **Semi-Amplitude $K_1$ ($\text{km/s}$)** | `36.0410` | `36.5357 +/- 0.1303` | `36.0889 +/- 0.5865` | `20.5891 +/- 2.6548` | `17.8735 +/- 1.7560` |
| **Eccentricity $e$** | `0.0 (fixed)` | `0.0 (fixed)` (`0.02015` ecc fit) | `0.02158 +/- 0.01634` | `0.3273 +/- 0.0450` | `0.3225 +/- 0.0565` |
| **Argument of Periastron $\omega$ ($^\circ$)** | — | `149.32` (ecc fit) | `119.82 +/- 54.76` | `159.19 +/- 6.64` | `150.81 +/- 3.99` |
| **Reference Epoch $T_0$ / $T_{\text{peri}}$ (`JD`)** | `2457510.56368` ($T_{\max}$) | `2457510.52237 +/- 0.00225` ($T_{\max}$) | `2457389.18362 +/- 0.69464` | `2458014.3821 +/- 9.3785` ($T_{\text{peri}}$) | `2457347.7135 +/- 2.6499` |
| **Fit $\chi^2$** | `3.79` (pre) / `3.86` (post) | `11.37` | — | `RMS = 0.4660 km/s` | — |
| **Mass Function $f(M)$ ($M_\odot$)** | `0.021686` | `0.022988` | `0.022131` | `0.255528` | `0.168731` |
| **Projected Axis $a_1 \sin i$ ($R_\odot$)** | `3.18460` | `3.28517` | `3.24461` | `128.7791` | `112.4418` |

---

## 4. Reproducibility & Verification

Run the orbit solver and deterministic verification suite from the repository root:
```bash
python bnty_0441/solve_sb1_orbit.py
python bnty_0441/verify_bnty_0441.py
```
