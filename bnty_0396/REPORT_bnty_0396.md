# HALLOWEEN: Ghost or Monster — Verdict: **GHOST** (`KIC 3337351` / `TIC 122224586` / `Gaia DR3 2052868099751582976`)

## 1. Target Star & Apparent Signal
- **Target Identifier:** `KIC 3337351` (`TIC 122224586`, `Gaia DR3 2052868099751582976`, `2MASS J19202785+3824165`, `KOI K00965.01`).
- **Astrometry & Photometry:** `RA = 290.11569°`, `Dec = +38.40419°` (J2000), `Kp = 13.361` (blended KIC) / `G = 15.9917`, `Tmag = 15.5236`, `V = 16.387`, `J = 14.943`, `H = 14.563`, `K = 14.477` (`ph_qual = AAA`), `Teff = 5837 K`, `log g = 4.539`, `plx = 0.4508 mas`.
- **Apparent Signal in Kepler Light Curve:** In NASA Exoplanet Archive DR25 TCE (`q1_q17_dr25_tce`) and MAST Q7 long-cadence photometry (`kplr003337351-2010355172524_llc.fits`, `sha256=d56e4c23e95dbd9099682ee53d54bacef580dd8e03224ad9bb2eb5a545aff844`), `KIC 3337351` exhibits periodic V-shaped eclipses every **`P = 7.047120 d`** (`tce_time0bk = 139.79720 BKJD`, `tce_duration = 5.479 h`, `tce_model_snr = 679.5`, `158` transits across Q1–Q17) with a catalog depth of **`58,970 ppm` (`5.897%`)** in SAP flux and **`8.398% – 11.210%`** in Q7 `PDCSAP_FLUX` (vs Q7 out-of-transit scatter `1.4826 * MAD = 0.1000%` SAP / `0.1195%` PDCSAP across `3,611` `SAP_QUALITY = 0` cadences).

## 2. Classification Verdict: **GHOST** (Off-Target Blooming Eclipsing Binary PSF Contamination)
The `5.9%` SAP (`11.2%` PDCSAP) periodic eclipse in `KIC 3337351` is **100% an instrumental Ghost** caused by PSF wing and bleed-column contamination from **`KIC 3230227` (`TIC 122224576` / `Gaia DR3 2052868095451251200` / `2MASS J19202701+3823595` / `AllWISE J192027.02+382359.4` / `KOI K06311.01`)**, a `Kp = 9.002` (`G = 8.9111`, `Tmag = 8.8073`, `J = 8.587`, `W1 = 8.495`, `Teff = 8200 K`, `plx = 2.7165 mas`) eccentric eclipsing binary located **`17.91"` (`4.50` Kepler pixels) South-West** at `RA = 290.11240°`, `Dec = +38.39985°` (`55.4x` brighter in Kepler bandpass, or `679x` brighter in true unblended Gaia `G` flux!).

## 3. Exact Physical & Instrumental Mechanism (Pixel-Level Proof on Q7 TPF)
We analyzed the raw Q7 Target Pixel File (`kplr003337351-2010355172524_lpd-targ.fits`, `sha256=3a6adb52d8e116604a82364d607c4142da696bfc939ce21276ae8a58b4b710c6`), which is an `8 x 9` pixel stamp (`72` pixels total) where `KIC 3337351`'s optimal aperture (`APERTURE == 3`) occupies `11` pixels in columns `3, 4, 5` (flat indices `[20, 21, 27, 28, 29, 35, 36, 37, 44, 45, 52]`; verified `median(sum(APERTURE==3)/SAP_FLUX) = 1.0000000036`):

1. **Saturated Culprit Bleed Column inside the Stamp (`col = 0..1`, `APERTURE == 1`):**
   - Columns `0` and `1` (the SW edge of `KIC 3337351`'s stamp, pointing directly toward `KIC 3230227` `17.91"` SW) carry **`145,317.89` to `205,381.48 e-/s` per pixel** from `KIC 3230227`'s saturated CCD bloom column (`>197,000 e-/s` saturation plateau in `idx=24,32,33,40,41,48,56,64`).
   - During Q7 Eclipse Event 1 (`t_peak = 640.16695 BKJD`), the unsaturated bloom-tip pixels `(row 2, col 0, idx=16)` and `(row 3, col 1, idx=25)` drop from `145,317.89 -> 105,818.88 e-/s` (**`-39,499.02 e-/s` = `-27.181%`**) and `42,343.17 -> 30,938.41 e-/s` (**`-11,404.77 e-/s` = `-26.934%`**).
2. **Spatial Attenuation Gradient Across `KIC 3337351`'s Optimal Aperture (`APERTURE == 3`, `col = 3 -> 4 -> 5`):**
   - As `KIC 3230227`'s PSF wings decay eastward across `KIC 3337351`'s aperture, the fractional eclipse depth drops monotonically with distance from the culprit:
     - **Western aperture edge (`col = 3`, closest to `KIC 3230227`):** `idx=27 (r=3,c=3)` drops `9,208.94 -> 8,731.22 e-/s` (**`-477.72 e-/s` / `-5.188%`**); `idx=35 (r=4,c=3)` drops `10,211.29 -> 9,663.23 e-/s` (**`-548.06 e-/s` / `-5.367%`**).
     - **Central aperture column (`col = 4`, on target):** `idx=20 (r=2,c=4)` drops `-4.205%` (`-48.77 e-/s`); `idx=28 (r=3,c=4)` drops `-3.400%` (`-110.14 e-/s`); `idx=36 (r=4,c=4)` drops `-3.944%` (`-68.97 e-/s`).
     - **Eastern aperture edge (`col = 5`, farthest from culprit, dominated by true target star):** `idx=29 (r=3,c=5)` drops only **`-1.361%`** (`1,014.31 -> 1,000.50 e-/s`, `-13.80 e-/s`); `idx=37 (r=4,c=5)` drops only **`-1.585%`** (`1,012.12 -> 996.08 e-/s`, `-16.04 e-/s`).
   - Why `PDCSAP_FLUX` is `1.8x` deeper than `SAP_FLUX` (`11.210%` vs `6.283%`): PDC subtracts the static crowding fraction (`1 - CROWDSAP`) assuming constant neighbor flux; when the neighbor itself eclipses, dividing the absolute flux drop by the de-blended faint target baseline artificially magnifies the fractional depth!
3. **In-Transit Centroid Shift (`+3.8` to `+8.6 mpix` Eastward) & `3.78"` Sky Offset:**
   - Because the western side (`col = 3`) of `APERTURE == 3` dims by `-5.37%` while the eastern side (`col = 5`) dims by `-1.36%`, the flux-weighted centroid shifts **eastward (`+dx`)** during every single eclipse:
     - `Event 1 (640.16695 BKJD, N=73, phase_eb=+0.00368)`: `SAP=-4.587%`, `PDCSAP=-8.398%`, `TPF shift=(+3.7,-0.8)->3.8 mpix`, `MOM_CENTR shift=(+2.3,-1.1)->2.5 mpix`.
     - `Event 2 (647.19580 BKJD, N=74, phase_eb=+0.00109)`: `SAP=-6.283%`, `PDCSAP=-11.210%`, `TPF shift=(+6.9,-0.9)->6.9 mpix`, `MOM_CENTR shift=(+4.1,-1.8)->4.5 mpix`.
     - `Event 3 (654.22463 BKJD, N=75, phase_eb=-0.00150)`: `SAP=-5.845%`, `PDCSAP=-10.253%`, `TPF shift=(+8.0,-0.8)->8.0 mpix`, `MOM_CENTR shift=(+4.8,-1.9)->5.2 mpix`.
     - `Event 4 (661.27388 BKJD, N=76, phase_eb=-0.00120)`: `SAP=-6.151%`, `PDCSAP=-9.185%`, `TPF shift=(+8.4,-1.4)->8.6 mpix`, `MOM_CENTR shift=(+5.0,-2.6)->5.6 mpix`.
     - `Event 5 (668.32311 BKJD, N=77, phase_eb=-0.00089)`: `SAP=-5.760%`, `PDCSAP=-9.345%`, `TPF shift=(+7.2,-0.9)->7.2 mpix`, `MOM_CENTR shift=(+4.5,-2.1)->5.0 mpix`.
   - NASA DR25 DV difference-image centroid offset (`tce_dicco_msky = 3.7796" ± 0.088"`, `42.8 sigma`) independently locks the transit source off-target.

## 4. Catalog Cross-Checks with Positive Controls (`0` Empty Queries)
- **Kirk+ 2016 Kepler EB Catalog (`J/AJ/151/68`, `2,876` rows):** `KIC 3337351` = `0` rows; culprit `KIC 3230227` = `1` row (`P_eb = 7.0471062 ± 0.0000175 d`, `BJD0 = 2454958.702238`, `morph = -1.0`); positive control `KIC 9101279` (`V1504 Cyg`) = `1` row (`P = 0.0695506 d`). Ephemeris match between `KIC 3337351` (`P = 7.0471035 d`) and `KIC 3230227` (`P = 7.0471062 d`) is `|dP/P| = 3.8e-7` (`0.23 s/orbit`) with `|phase_eb| <= 0.0037` across all Q7 events.
- **NASA Exoplanet Archive `cumulative` KOI & `q1_q17_dr25_tce` (`TAP/sync`):** `KIC 3337351` (`K00965.01`, `FALSE POSITIVE`, flags `ss=1, co=1, ec=1`, `EPHEM_MATCH`); `KIC 3230227` (`K06311.01`, `FALSE POSITIVE`, `CENT_SATURATED`); positive control `KIC 10963065` (`K01612.01`, `CONFIRMED`, `P = 2.465024 d`).
- **STScI MAST `Mast.Catalogs.Tic.Cone` (`Gaia DR3` + `TIC v8.2`, `r = 30"`) & IRSA TAP (`2MASS fp_psc` + `AllWISE allwise_p3as_psd`, `r = 30"`):** Returned `15` TIC/Gaia sources, `6` 2MASS sources, and `3` AllWISE sources, confirming both target `TIC 122224586` (`d = 1.83"`) and culprit `TIC 122224576` (`d = 17.91"`).
- **Reproducibility Bundle:** `https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/bnty_0396` (`python bnty_0396/verify_bnty_0396.py` -> `status: PASS`).
