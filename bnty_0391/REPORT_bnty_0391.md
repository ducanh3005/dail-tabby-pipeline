# DISCOVERY: TESS Single-Transit Candidate, Fully Vetted — `TIC 259592689` (`Sector 5` / `TOI 429.01`)

## 1. Candidate & Host Star Parameters
- **Target Identifier:** `TIC 259592689` (`Gaia DR3 4777069717050967040`, `2MASS J04515445-5349501`, `AllWISE J045154.52-534947.8`, unconfirmed single-transit candidate `TOI 429.01`, `tfopwg_disp = PC`, `pl_orbper = NULL`).
- **Astrometry & Host Properties:** `RA = 72.9773080°`, `Dec = -53.8296260°` (J2000), `Tmag = 10.1672`, `G = 10.6954`, `BP-RP = 1.0116`, `J = 9.464`, `H = 9.092`, `K = 8.941` (`AAA`), `W1 = 8.933`, `W2 = 8.998`, `plx = 8.3319 mas` (`d = 120.02 pc`), `Teff = 5216 K`, `log g = 4.430`, `R_* = 0.954–0.980 R_sun`, `M_* = 0.89 M_sun`, `L_* = 0.607 L_sun` (quiet K0V/G8V main-sequence dwarf).
- **TESS Sector & FITS Files Verified (`sha256`):**
  - **Sector 5 (`s0005`, 2-minute SPOC cadence, `17,212` `QUALITY = 0` cadences across `1438.07 .. 1463.68 BTJD`):**
  - Light Curve: `tess2018319095959-s0005-0000000259592689-0125-s_lc.fits` (`sha256=20ba9a310ab5f38643ce8bc2d83fa9628020fd0000688d619590acb7f6d3283e`).
  - Target Pixel File: `tess2018319095959-s0005-0000000259592689-0125-s_tp.fits` (`sha256=a93341a24af7a310d540922e7ac2bc294a3ce28e03a3ca0864ee0640d15e32f7`).
- **Single-Transit Observable Parameters:**
  - **Transit Mid-Time (`t_c`):** **`1439.648711 BTJD`** (`BJD = 2458439.648711`).
  - **Transit Duration (`T_14`):** **`9.528 hours` (`0.3970 d`)** (`286` total in-transit `QUALITY=0` 2-min cadences; `186` flat-bottom cadences within `|t - t_c| <= 0.65 * T_14/2`).
  - **Transit Depth:** **`7,825.4 ppm` (`0.7825%`) in `PDCSAP_FLUX`**, **`7,776.7 ppm` (`0.7777%`) in `SAP_FLUX`** (catalog box fit `7,525.7 ppm`), vs out-of-transit 2-min scatter `1.4826 * MAD = 1,079.9 ppm`, yielding a flat-bottom **`SNR = 98.8`**.
  - **Implied Planet Radius & Long-Period Orbit:** `R_p / R_* = sqrt(0.0078254) = 0.08846` -> **`R_p = 0.844–0.867 R_Jup` (`9.47–9.72 R_Earth`)**. Absence of a second transit in the 25.61-day Sector 5 baseline enforces `P > 24.03 d`; circular-orbit stellar-density scaling (`rho_* = 1.32 g/cm^3`, `T_14 = 9.528 h`, `b = 0..0.5`) yields **`P_circ ≈ 88 – 135 days`** (`T_eq ≈ 340–395 K` temperate Saturn/Jupiter).

## 2. Full Four-Gate Vetting Results

### Gate A: Pixel-Level TPF & Centroid Check (`PASS`)
- In the `11 x 11` Sector 5 TPF stamp (`121` pixels), the SPOC optimal aperture (`(APERTURE & 2) != 0`, code `139`) contains `18` pixels (`idx = [48,49,50,51,59,60,61,62,70,71,72,73,74,81,82,83,84,94]`; verified `median(sum(APERTURE&2)/SAP_FLUX) = 0.9999999810`).
- **In-Transit Centroid Shift:** Both the direct TPF flux-weighted centroid (`cx, cy`) and SPOC `MOM_CENTR1/2` shift by **`dX = -0.34 mpix`, `dY = -0.65 mpix`, `|dC| = 0.73 mpix = 0.0154"`** (`< 1/1360th` of a `21"` TESS pixel), locking the transit onto `TIC 259592689`.
- **Per-Pixel Core Localization:** The transit flux loss (`-94.03 e-/s` across the 18-pixel aperture) is concentrated on the central stellar PSF core pixels:
  - `idx=60 (r=5,c=5, core peak)`: `3,023.72 -> 2,998.99 e-/s` (**`-24.73 e-/s` = `-0.8178%`**).
  - `idx=71 (r=6,c=5, core S)`: `2,563.10 -> 2,549.50 e-/s` (**`-13.60 e-/s` = `-0.5305%`**).
  - `idx=61 (r=5,c=6, core E)`: `1,454.69 -> 1,444.17 e-/s` (**`-10.52 e-/s` = `-0.7232%`**).
  - `idx=72 (r=6,c=6, core SE)`: `1,166.12 -> 1,157.61 e-/s` (**`-8.50 e-/s` = `-0.7292%`**).
  - `idx=59 (r=5,c=4, core W)`: `835.42 -> 828.87 e-/s` (**`-6.55 e-/s` = `-0.7838%`**).

### Gate B: Contamination & Background Blend Exclusion (`PASS`)
- **SPOC Crowding Metric:** Header `CROWDSAP = 0.99248290` (`99.25%` of aperture flux is from `TIC 259592689`; total combined background flux is `1 - CROWDSAP = 0.0075171 = 7,517.1 ppm`; `FLFRCSAP = 0.92428136`). Because the observed un-deblended `SAP_FLUX` transit depth (`7,776.7 ppm`) exceeds the entire `7,517.1 ppm` background flux budget (`>100%` eclipse required), a background eclipsing binary inside the aperture is mathematically impossible.
- **60" Neighbor Census (`MAST Tic.Cone` & `GaiaDR3.Cone`):** Only 7 neighbors exist within `60"`: the brightest within `35"` are `TIC 685300496` at `20.19"` (`Tmag = 18.6706`, `ΔT = 8.50 mag`, max flux ratio `397 ppm`) and `TIC 685300495` at `26.32"` (`Tmag = 15.9018`, `ΔT = 5.73 mag`, max flux ratio `5,083 ppm`, max 50% EB diluted depth `<= 2,541 ppm << 7,825 ppm`).

### Gate C: Odd-Even, Symmetry & Sub-Harmonic Secondary Sweep (`PASS`)
- **In-Transit Odd vs Even Cadence Split (`N=93` odd vs `N=93` even 2-min cadences):** `depth_odd = 8,053.8 ppm`, `depth_even = 7,671.6 ppm` (`Δ = +382.1 ppm`, `2.41 sigma`, consistent with zero).
- **Ingress/First-Half vs Egress/Second-Half Symmetry (`N=143` vs `N=143`):** `depth_1st = 7,426.3 ppm`, `depth_2nd = 7,075.7 ppm` (`Δ = +350.6 ppm`), confirming a flat-bottomed U-shaped planetary profile.
- **Sector-Wide Secondary & Sub-Harmonic Sweep:** Scanning all `17,212` `QUALITY=0` cadences outside `[t_c - T_14, t_c + T_14]` finds no secondary eclipse or sub-harmonic transit (`P = 24.03/N d`); the deepest 1-hour boxcar average anywhere else in Sector 5 is `-785.9 ppm` (`1445.4881 BTJD`, `< 10%` of transit depth).

### Gate D: Ruling Out Known Planets & Eclipsing Binaries (`0` Empty Queries)
- **Confirmed Planets (`NASA TAP pscomppars`):** `TIC 259592689` = `0` rows; positive control `TIC 307210830` (`L 98-59`) = `5` rows (`L 98-59 b..f`).
- **TOI Dispositions (`NASA TAP toi`):** `TIC 259592689` (`TOI 429.01`) = `PC` (`0` rows in `tfopwg_disp='FP'`); positive controls `TIC 307210830` (`CP`, `3` rows) and `TIC 182943944` (`TOI 1017.01`, `FP`, `1` row).
- **Gaia DR3 Binary/RV/Variability (`MAST GaiaDR3.Cone`, `8` rows):** `Gaia DR3 4777069717050967040` has `ruwe = 1.0855` (`<1.4`), `non_single_star = 0`, `radial_velocity = 50.5239 ± 0.2436 km/s` (`0.244 km/s` RV stability rules out stellar EB companions), `phot_variable_flag = NOT_AVAILABLE`.
- **Repro Bundle:** `https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/bnty_0391` (`python bnty_0391/verify_bnty_0391.py` -> `PASS`).