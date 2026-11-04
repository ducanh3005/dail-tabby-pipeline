# DAiL `bnty_0425` — TIC 158499577 (`HD 94871`): TESS FFI Re-Extraction in Unsearched Sectors

**Hunter:** `ducanh3005`  
**Method Version:** `1.0.0`  
**Target:** `TIC 158499577` (`HD 94871`, `Gaia DR3 5401019098113741568`, `RA = 164.1597484°`, `Dec = -36.5803139°`, $T = 8.262$, $V = 8.81$)  
**House Ephemeris Folded:** $P = 11.7672\text{ d}$, $T_0 = \text{BTJD } 2286.3720$  
**Reproducibility Command:**
```bash
python3 bnty_0425/extract_ffi_sectors.py && python3 bnty_0425/verify_bnty_0425.py
```

---

## 1. Fail-Visible TESS Sector Manifest (Sectors 1–100)

Queried MAST TESSCut (`https://mast.stsci.edu/tesscut/api/v0.1/sector?ra=164.1597484&dec=-36.5803139`, saved in `raw/tesscut_sectors.json`) and `Mast.Caom.Cone`. Every TESS sector from 1 to 100 is explicitly accounted for:

| Sector Range | Status | Camera / CCD | Cadence | Total / Clean (`Q=0`) Frames | BTJD Span | Notes |
|---|---|---|---|---|---|---|
| **S0001–S0008** | `no-usable-FFI` | — | — | 0 | — | Target ($\lambda=179.48^\circ, \beta=-39.77^\circ$) outside Camera 2 FOV |
| **S0009** | `usable-FFI (House 2-min baseline)` | Cam 2 CCD 3 | 1800 s | 1,154 / 977 | 1544.703–1568.453 | House 2-min SPOC sector; 30-min FFI extracted as cross-check (`ffi_lc_s0009.csv`), excluded from unsearched FFI fold |
| **S0010–S0035** | `no-usable-FFI` | — | — | 0 | — | Target outside TESS FOV |
| **S0036** | `usable-FFI (House 2-min baseline)` | Cam 2 CCD 3 | 600 s | 3,477 / 3,076 | 2282.168–2305.988 | House 2-min SPOC sector; 10-min FFI extracted as cross-check (`ffi_lc_s0036.csv`), excluded from unsearched FFI fold |
| **S0037–S0062** | `no-usable-FFI` | — | — | 0 | — | Target outside TESS FOV |
| **S0063** | **`usable-FFI (UNSEARCHED)`** | Cam 2 CCD 4 | **200 s** | **11,190 / 10,629** | **3014.374–3040.901** | Extracted (`ffi_lc_s0063.csv`); **5 new transits** ($E=+62..+64$) |
| **S0064–S0089** | `no-usable-FFI` | — | — | 0 | — | Target outside TESS FOV |
| **S0090** | **`usable-FFI (UNSEARCHED)`** | Cam 2 CCD 4 | **200 s** | **11,574 / 10,295** | **3747.166–3773.240** | Extracted (`ffi_lc_s0090.csv`); **4 new transits** ($E=+124..+126$) |
| **S0091–S0098** | `no-usable-FFI` | — | — | 0 | — | Target outside TESS FOV |
| **S0099** | **`usable-FFI (UNSEARCHED)`** | Cam 2 CCD 2 | **200 s** | **8,629 / 8,339** | **4046.119–4073.771** | Extracted (`ffi_lc_s0099.csv`); **3 new transits** ($E=+150..+151$; $E=+150$ SEC at BTJD 4057.504 in mid-sector downlink gap) |
| **S0100** | **`usable-FFI (UNSEARCHED)`** | Cam 2 CCD 4 | **200 s** | **11,174 / 9,096** | **4074.486–4098.864** | Extracted (`ffi_lc_s0100.csv`); **4 new transits** ($E=+152..+154$; $E=+153$ PRI at BTJD 4086.755 in mid-sector downlink gap) |

---

## 2. Stated Aperture Photometry & Detrending Method

All extractions run directly on the $11\times 11$ MAST TESSCut astrocut FITS files (`raw/tesscut_s*.fits`, SHA-256 verified in `raw/tesscut_fits_manifest_sha256.json`):
1. **Quality & Scattered-Light Filtering:** Keep cadences with `QUALITY == 0`, finite central $5\times 5$ stamp flux, and residual sky within $\pm 8\,\text{MAD}$ of the sector median.
2. **Stated Target Apertures (3 parallel apertures exported per CSV):**
   - **Primary Stated Aperture (`depth_thresh_ap`):** Contiguous pixels within $r \le 2.5\text{ px}$ of the sector peak pixel $(r_{\text{pk}}, c_{\text{pk}})$ exceeding $\text{med\_img} > \text{sky}_{\text{med}} + 20\,\sigma_{\text{sky}}$ ($N_{\text{ap}} = 21, 19, 14, 19\text{ px}$ in S63, S90, S99, S100; $17, 19\text{ px}$ in S9, S36).
   - **Fixed $3\times 3$ Core Box (`depth_3x3_ap`, 9 px)** and **Tight 5-Pixel Cross (`depth_cross5_ap`, 5 px):** Extracted in parallel to verify robustness against the faint neighbours `TIC 942348495` ($9.29''$) and `TIC 942348496` ($9.54''$).
3. **Background Subtraction:** Per-cadence median residual sky estimated from the 46 outer annulus pixels ($r \ge 3.2\text{ px}$ and $\le 55\text{th}$ percentile of the median stamp).
4. **Detrending:** Iterative dip-masked $1.5\text{-day}$ sliding Tukey-biweight continuum filter ($c = 6.0$, 3 mask iterations at $3.5\,\text{MAD}$) so eclipse dips are never attenuated by the continuum fit. Out-of-transit 200-s scatter is $404.2\text{ ppm}$ (S63), $444.3\text{ ppm}$ (S90), $479.7\text{ ppm}$ (S99), and $436.2\text{ ppm}$ (S100).

---

## 3. Folded Depths per Sector at House Ephemeris ($P = 11.7672\text{ d}$, $T_0 = \text{BTJD } 2286.3720$)

Secondary minimum occurs at eccentric phase $\phi_{\text{sec}} = 0.51411$ ($+3.98\text{ h}$ after circular $\phi = 0.50000$).

| Sector | Cadence (s) | Clean Pts | CorePRI ($|\Delta\phi|\le 0.0010$) | CoreSEC ($\phi=0.51411$) | BoxPRI ($|\Delta\phi|\le 0.0017$) | BoxSEC ($\phi=0.51411$) | CircSEC ($\phi=0.50000$) | Ctrl $\phi=0.25$ | Ctrl $\phi=0.75$ |
|---|---|---|---|---|---|---|---|---|---|
| **S63 (New FFI)** | 200 | 10,629 | **0.32565 ± 0.00046** ($n=31$) | **0.28830 ± 0.00047** ($n=19$) | **0.32118 ± 0.00096** ($n=52$) | **0.28452 ± 0.00100** ($n=32$) | +0.00017 ± 0.00009 | -0.00001 ± 0.00005 | +0.00007 ± 0.00006 |
| **S90 (New FFI)** | 200 | 10,295 | **0.32783 ± 0.00050** ($n=20$) | **0.29083 ± 0.00045** ($n=20$) | **0.32329 ± 0.00115** ($n=34$) | **0.28695 ± 0.00098** ($n=34$) | -0.00006 ± 0.00006 | +0.00017 ± 0.00008 | +0.00000 ± 0.00008 |
| **S99 (New FFI)** | 200 | 8,339 | **0.33072 ± 0.00091** ($n=20$) | **0.29091 ± 0.00075** ($n=10$) | **0.32661 ± 0.00117** ($n=34$) | **0.28692 ± 0.00142** ($n=17$) | -0.00014 ± 0.00007 | -0.00009 ± 0.00005 | -0.00006 ± 0.00008 |
| **S100 (New FFI)** | 200 | 9,096 | **0.32623 ± 0.00050** ($n=20$) | **0.28922 ± 0.00060** ($n=19$) | **0.32174 ± 0.00119** ($n=34$) | **0.28504 ± 0.00119** ($n=34$) | +0.00079 ± 0.00016 | +0.00002 ± 0.00008 | -0.00008 ± 0.00007 |
| **Combined Unsearched (S63+90+99+100)** | **200** | **38,359** | **0.32719 ± 0.00030** ($n=91$) | **0.28967 ± 0.00032** ($n=68$) | **0.32296 ± 0.00049** ($n=154$) | **0.28571 ± 0.00054** ($n=117$) | +0.00009 ± 0.00005 | +0.00002 ± 0.00003 | -0.00002 ± 0.00004 |
| *S09 (FFI X-check)* | 1800 | 977 | 0.32736 ($n=1$) | 0.28584 ± 0.00157 ($n=3$) | 0.31793 ± 0.00666 ($n=2$) | 0.28493 ± 0.00165 ($n=4$) | -0.00003 ± 0.00011 | +0.00014 ± 0.00006 | -0.00020 ± 0.00013 |
| *S36 (FFI X-check)* | 600 | 3,076 | 0.32691 ± 0.00106 ($n=7$) | 0.29005 ± 0.00101 ($n=7$) | 0.32189 ± 0.00227 ($n=12$) | 0.28657 ± 0.00177 ($n=11$) | +0.00038 ± 0.00019 | -0.00008 ± 0.00008 | +0.00011 ± 0.00013 |

---

## 4. All 16 New Transits Discovered in Unsearched FFI Sectors (S63, S90, S99, S100)

| # | Sector | Epoch $E$ | Type | $T_{\text{obs}}$ (BTJD) | $O-C_{\text{house}}$ (min) | $O-C_{\text{joint}}$ (min) | $N_{\text{win}}$ | Core Depth (Thresh / $3\times 3$ / Cross5) | Box Depth | Peak Depth | Centroid Shift (mpix / arcsec) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | S63 | $+62$ | PRIMARY | `3015.94038` | $+2.85$ | $+1.26$ | 121 | `0.32628` / `0.32768` / `0.32742` | `0.32252` | `0.32839` | $14.12\text{ mpix}$ ($0.297''$) |
| 2 | S63 | $+62$ | SECONDARY | `3021.98924` | $+1.79$ | $+0.19$ | 121 | `0.28822` / `0.28941` / `0.28931` | `0.28552` | `0.29021` | $6.22\text{ mpix}$ ($0.131''$) |
| 3 | S63 | $+63$ | PRIMARY | `3027.70686` | $+1.81$ | $+0.20$ | 101 | `0.32502` / `0.32588` / `0.32556` | `0.32320` | `0.32765` | $12.94\text{ mpix}$ ($0.272''$) |
| 4 | S63 | $+63$ | SECONDARY | `3033.75390` | $-1.87$ | $-3.50$ | 113 | `0.28894` / `0.29083` / `0.29294` | `0.28678` | `0.29088` | $7.86\text{ mpix}$ ($0.165''$) |
| 5 | S63 | $+64$ | PRIMARY | `3039.47248` | $-0.46$ | $-2.09$ | 118 | `0.32686` / `0.32822` / `0.32875` | `0.32324` | `0.32858` | $15.49\text{ mpix}$ ($0.325''$) |
| 6 | S90 | $+124$ | SECONDARY | `3751.55688` | $+3.57$ | $+0.45$ | 121 | `0.29130` / `0.29167` / `0.29146` | `0.28821` | `0.29333` | $4.88\text{ mpix}$ ($0.102''$) |
| 7 | S90 | $+125$ | PRIMARY | `3757.27283` | $+1.20$ | $-1.93$ | 121 | `0.32870` / `0.32867` / `0.32758` | `0.32468` | `0.33047` | $15.34\text{ mpix}$ ($0.322''$) |
| 8 | S90 | $+125$ | SECONDARY | `3763.32490` | $+4.75$ | $+1.60$ | 121 | `0.29130` / `0.29174` / `0.29133` | `0.28900` | `0.29315` | $8.67\text{ mpix}$ ($0.182''$) |
| 9 | S90 | $+126$ | PRIMARY | `3769.04084` | $+2.36$ | $-0.80$ | 121 | `0.32832` / `0.32807` / `0.32840` | `0.32538` | `0.33094` | $31.75\text{ mpix}$ ($0.667''$) |
| 10 | S99 | $+150$ | PRIMARY | `4051.45463` | $+3.78$ | $+0.04$ | 121 | `0.32923` / `0.32875` / `0.32808` | `0.32575` | `0.33146` | $32.86\text{ mpix}$ ($0.690''$) |
| 11 | S99 | $+151$ | PRIMARY | `4063.22013` | $+1.34$ | $-2.42$ | 121 | `0.33369` / `0.32879` / `0.32780` | `0.33117` | `0.33608` | $50.02\text{ mpix}$ ($1.050''$) |
| 12 | S99 | $+151$ | SECONDARY | `4069.27091` | $+3.04$ | $-0.73$ | 121 | `0.29151` / `0.29127` / `0.29066` | `0.28892` | `0.29332` | $8.10\text{ mpix}$ ($0.170''$) |
| 13 | S100 | $+152$ | PRIMARY | `4074.98665` | $+0.35$ | $-3.44$ | 121 | `0.32702` / `0.32792` / `0.32753` | `0.32281` | `0.32906` | $26.24\text{ mpix}$ ($0.551''$) |
| 14 | S100 | $+152$ | SECONDARY | `4081.03740` | $+2.02$ | $-1.79$ | 121 | `0.28961` / `0.28938` / `0.28661` | `0.28590` | `0.29203` | $13.99\text{ mpix}$ ($0.294''$) |
| 15 | S100 | $+153$ | SECONDARY | `4092.80244` | $-1.10$ | $-4.92$ | 115 | `0.28978` / `0.29094` / `0.29211` | `0.28618` | `0.29222` | $20.16\text{ mpix}$ ($0.423''$) |
| 16 | S100 | $+154$ | PRIMARY | `4098.52351` | $+3.90$ | $+0.06$ | 121 | `0.32696` / `0.32758` / `0.32677` | `0.32215` | `0.32862` | $44.88\text{ mpix}$ ($0.942''$) |
