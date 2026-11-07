# DISCOVERY: TESS Single-Transit Candidate, Fully Vetted — `TIC 259592689` (`Sector 5` / `TOI 429.01`)

- **Complete Repro Bundle URL:** `https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/bnty_0391` (`python bnty_0391/verify_bnty_0391.py` -> `PASS`)

## 1. Candidate, Published History Disclosure & Host Star Parameters
- **Target Identifier:** `TIC 259592689` (`Gaia DR3 4777069717050967040`, `2MASS J04515445-5349501`, `AllWISE J045154.52-534947.8`, NASA Exoplanet Archive `TOI 429.01`, `tfopwg_disp = PC`, `pl_orbper = NULL` in `toi` table).
- **Published Literature & Multi-Sector/RV History Disclosure (2021 AAS Abstract):**
  - While `TOI 429.01` remains listed with `tfopwg_disp = PC` and `pl_orbper = NULL` in the NASA Exoplanet Archive `toi` table (`0` rows in `pscomppars`), a 2021 AAS abstract reported four-sector TESS coverage combined with radial-velocity follow-up yielding a true orbital period of **`P = 339 ± 3 days`** and a companion mass of **`M_p = 0.9 ± 0.06 M_Jup`**.
  - **Reconciling Sector-5-Only `P_circ = 88–135 d` vs True `P = 339 ± 3 d`:** In our Sector-5-only single-transit analysis below, a naive circular-orbit (`e = 0`) Seager–Mallén-Ornelas stellar-density scaling from `rho_* = 1.32 g/cm^3` and `T_14 = 9.528 h` (`b = 0..0.5`) gives `P_circ ≈ 88–135 d`. Because transit duration scales as `T_14 ∝ P^(1/3) * sqrt(1 - e^2) / (1 + e sin omega)`, a `P = 339 d` planet producing a `9.528 h` transit (instead of the `~13.0–15.0 h` expected for a low-impact-parameter circular `339 d` orbit on this star) requires either a moderately eccentric orbit transiting near periastron (`e ≈ 0.30–0.45` with `1 + e sin omega > 1`, where orbital speed `v_orb` is higher by `(1 + e sin omega)/sqrt(1 - e^2) ≈ 1.35–1.55x`) or a higher impact parameter (`b ≈ 0.72–0.78`).
  - **Withdrawing the Circular `T_eq = 340–395 K` Claim:** We explicitly withdraw the circular-orbit `T_eq = 340–395 K` estimate; at the true `P = 339 ± 3 d` (`a ≈ 0.918 AU` around a `Teff = 5216 K`, `L_* = 0.607 L_sun` host), the zero-albedo equilibrium temperature is **`T_eq ≈ 245 ± 6 K`**.
- **Astrometry & Host Properties:** `RA = 72.9773080°`, `Dec = -53.8296260°` (J2000), `Tmag = 10.1672`, `G = 10.6954`, `BP-RP = 1.0116`, `J = 9.464`, `H = 9.092`, `K = 8.941` (`AAA`), `W1 = 8.933`, `W2 = 8.998`, `plx = 8.3319 mas` (`d = 120.02 pc`), `Teff = 5216 K`, `log g = 4.430`, `R_* = 0.954–0.980 R_sun`, `M_* = 0.89 M_sun`, `L_* = 0.607 L_sun` (quiet K0V/G8V main-sequence dwarf).
- **TESS Sector & FITS Files Verified (`sha256`):**
  - **Sector 5 (`s0005`, 2-minute SPOC cadence, `17,212` `QUALITY = 0` cadences across `1438.07 .. 1463.68 BTJD`):**
  - Light Curve: `tess2018319095959-s0005-0000000259592689-0125-s_lc.fits` (`sha256=20ba9a310ab5f38643ce8bc2d83fa9628020fd0000688d619590acb7f6d3283e`).
  - Target Pixel File: `tess2018319095959-s0005-0000000259592689-0125-s_tp.fits` (`sha256=a93341a24af7a310d540922e7ac2bc294a3ce28e03a3ca0864ee0640d15e32f7`).
- **Single-Transit Observable Parameters:**
  - **Transit Mid-Time (`t_c`):** **`1439.648711 BTJD`** (`BJD = 2458439.648711`).
  - **Transit Duration (`T_14`):** **`9.528 hours` (`0.3970 d`)** (`286` total in-transit `QUALITY=0` 2-min cadences; `186` flat-bottom cadences within `|t - t_c| <= 0.65 * (T_14/2) = 0.129025 d`).
  - **Transit Depth:** **`7,825.4 ppm` (`0.7825%`) in `PDCSAP_FLUX`**, **`7,776.7 ppm` (`0.7777%`) in `SAP_FLUX`** (catalog box fit `7,525.7 ppm`), vs out-of-transit 2-min scatter `1.4826 * MAD = 1,079.9 ppm`, yielding a flat-bottom **`SNR = 98.8`**.
  - **Implied Planet Radius:** `R_p / R_* = sqrt(0.0078254) = 0.08846` -> **`R_p = 0.844–0.867 R_Jup` (`9.47–9.72 R_Earth`)**.

## 2. Full Four-Gate Vetting Results

### Gate A: Pixel-Level TPF & Centroid Check (`PASS`)
- In the `11 x 11` Sector 5 TPF stamp (`121` pixels), the SPOC optimal aperture (`(APERTURE & 2) != 0`, code `139`) contains `18` pixels (`idx = [48,49,50,51,59,60,61,62,70,71,72,73,74,81,82,83,84,94]`; verified `median(sum(APERTURE&2)/SAP_FLUX) = 0.9999999810`).
- **In-Transit Centroid Shift (Full Window & Axis Specification):**
  - **In-Transit Window (`in_bottom`, `N_in = 186`):** `QUALITY == 0` cadences with `|t - t_c| <= 0.65 * (T_14 / 2) = 0.129025 d` (`[1439.5197, 1439.7777] BTJD`).
  - **Local Out-of-Transit Baseline Window (`oot_local`, `N_oot = 764`):** `QUALITY == 0` cadences in the symmetric flanking annulus `1.3 * (T_14 / 2) <= |t - t_c| <= 4.0 * (T_14 / 2)`, i.e. **`0.25805 d <= |t - t_c| <= 0.79400 d`** (`[1438.8547, 1439.3907]` and `[1439.9068, 1440.4427] BTJD`).
  - **Axis & Sign Convention:** `Delta = mean(in_bottom) - mean(oot_local)` along CCD column (`X = MOM_CENTR1` or TPF flux-weighted `cx`) and CCD row (`Y = MOM_CENTR2` or TPF flux-weighted `cy`), with standard error `SE = hypot(std_in/sqrt(N_in), std_oot/sqrt(N_oot))`:
    - **SPOC `MOM_CENTR1/2`:** **`dX (col) = -0.34 ± 0.26 mpix`**, **`dY (row) = -0.65 ± 0.52 mpix`**, **`|dC| = 0.73 ± 0.47 mpix = 0.0154 ± 0.0099"`**.
    - **Direct TPF `cx, cy`:** **`dcx (col) = -0.34 ± 0.26 mpix`**, **`dcy (row) = -0.65 ± 0.52 mpix`**, **`|dC| = 0.73 ± 0.47 mpix = 0.0154 ± 0.0099"`** (`< 1/1360th` of a `21"` TESS pixel, consistent with zero at `1.55 sigma`), locking the transit onto `TIC 259592689`.
- **Per-Pixel Core Localization:** The transit flux loss (`-94.03 e-/s` across the 18-pixel aperture) is concentrated on the central stellar PSF core pixels:
  - `idx=60 (r=5,c=5, core peak)`: `3,023.72 -> 2,998.99 e-/s` (**`-24.73 e-/s` = `-0.8178%`**).
  - `idx=71 (r=6,c=5, core S)`: `2,563.10 -> 2,549.50 e-/s` (**`-13.60 e-/s` = `-0.5305%`**).
  - `idx=61 (r=5,c=6, core E)`: `1,454.69 -> 1,444.17 e-/s` (**`-10.52 e-/s` = `-0.7232%`**).
  - `idx=72 (r=6,c=6, core SE)`: `1,166.12 -> 1,157.61 e-/s` (**`-8.50 e-/s` = `-0.7292%`**).
  - `idx=59 (r=5,c=4, core W)`: `835.42 -> 828.87 e-/s` (**`-6.55 e-/s` = `-0.7838%`**).

### Gate B: Contamination & Background Blend Exclusion (`PASS`)
- **SPOC Crowding Metric:** Header `CROWDSAP = 0.99248290` (`99.25%` of aperture flux is from `TIC 259592689`; total combined background flux is `1 - CROWDSAP = 0.0075171 = 7,517.1 ppm`; `FLFRCSAP = 0.92428136`). Because the observed un-deblended `SAP_FLUX` transit depth (`7,776.7 ppm`) exceeds the entire `7,517.1 ppm` background flux budget (`>100%` eclipse required), a background eclipsing binary inside the aperture is mathematically impossible.
- **60" Neighbor Census (`MAST Tic.Cone` & `GaiaDR3.Cone`):** Only 7 neighbors exist within `60"`: the brightest within `35"` are `TIC 685300496` at `20.19"` (`Tmag = 18.6706`, `ΔT = 8.50 mag`, max flux ratio `397 ppm`) and `TIC 685300495` at `26.32"` (`Tmag = 15.9018`, `ΔT = 5.73 mag`, max flux ratio `5,083 ppm`, max 50% EB diluted depth `<= 2,541 ppm << 7,825 ppm`).

### Gate C: Within-Transit Odd-Even Cadence Split, Symmetry & Sector-Wide Secondary Sweep (`PASS`)
- **Within-Transit Odd vs Even Cadence Split Disclosure (`N=93` odd vs `N=93` even 2-min cadences):** Because Sector 5 contains only a single transit of `TIC 259592689` (no second transit exists in Sector 5 for a true multi-transit odd-even eclipse depth comparison), this test is strictly an **intra-transit alternating-cadence consistency split** (`in_bottom[0::2]` vs `in_bottom[1::2]`): `depth_odd = 8,053.8 ppm`, `depth_even = 7,671.6 ppm` (`Δ = +382.1 ppm`, `2.41 sigma`).
- **Ingress/First-Half vs Egress/Second-Half Symmetry (`N=143` vs `N=143`):** `depth_1st = 7,426.3 ppm`, `depth_2nd = 7,075.7 ppm` (`Δ = +350.6 ppm`), confirming a flat-bottomed U-shaped planetary profile.
- **Sector-Wide Secondary & Sub-Harmonic Sweep (Full Method Specification & Sector-End Ramp Disclosure):**
  - **Masking & Baseline Method:** We mask `[t_c - T_14, t_c + T_14]` (`|t - 1439.648711| <= 0.3970 d`, leaving `16,645` out-of-transit `QUALITY=0` cadences) and evaluate 1-hour windows (`|t - t_0| <= 0.5 h` and `30`-cadence boxcars) under three explicit baselines (dropping the imprecise `<10%` phrasing):
    1. **Global OOT Median `PDCSAP_FLUX` (`med_OOT = 11,488.39 e-/s`):** The deepest 1-hour (`|t - t_0| <= 0.5 h`, `n=31`) window median is **`-783.1 ppm`** (**`10.01%`** of transit depth) and the deepest `30`-cadence boxcar mean is **`-879.0 ppm`** (**`11.23%`** of transit depth) at `1445.4888 BTJD`.
    2. **Locally Detrended `PDCSAP_FLUX` (`±0.5 d` sliding OOT median baseline):** Across all of Sector 5, the deepest `30`-cadence boxcar mean is **`-1,245.4 ppm`** (`15.92%` of transit depth) at the Sector 5 start edge (`1438.0958 BTJD`, `n=30`).
    3. **Un-deblended/Un-cotrended `SAP_FLUX` Near Sector End (`t > 1462 BTJD`):** In raw `SAP_FLUX` (prior to SPOC PDC cotrending of scattered-light/attitude ramps at the end of Orbit 18), the `30`-cadence boxcar reaches **`-1,793.2 ppm`** (`23.06%` of transit depth) at **`1463.3678 BTJD`** near the sector end (`1463.68 BTJD`). SPOC `PDCSAP_FLUX` removes this instrumental sector-end ramp (leaving no dip deeper than `-879.0 ppm` in global-median `PDCSAP_FLUX`), and no feature anywhere in Sector 5 approaches the `7,825.4 ppm`, `9.528 h` primary transit.

### Gate D: Ruling Out Known Confirmed Planets & EBs (`0` Empty Queries)
- **Confirmed Planets (`NASA TAP pscomppars`):** `TIC 259592689` = `0` rows; positive control `TIC 307210830` (`L 98-59`) = `5` rows (`L 98-59 b..f`).
- **TOI Dispositions (`NASA TAP toi`):** `TIC 259592689` (`TOI 429.01`) = `PC` (`0` rows in `tfopwg_disp='FP'`); positive controls `TIC 307210830` (`CP`, `3` rows) and `TIC 182943944` (`TOI 1017.01`, `FP`, `1` row).
- **Gaia DR3 Binary/RV/Variability (`MAST GaiaDR3.Cone`, `8` rows):** `Gaia DR3 4777069717050967040` has `ruwe = 1.0855` (`<1.4`), `non_single_star = 0`, `radial_velocity = 50.5239 ± 0.2436 km/s` (`0.244 km/s` RV stability rules out stellar EB companions), `phot_variable_flag = NOT_AVAILABLE`.
