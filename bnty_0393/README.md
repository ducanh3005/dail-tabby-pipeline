# DAiL `bnty_0393` — Asteroid Precovery in Archival Survey Images

Reproducible verification pipeline and archival FITS stamp evidence for **DAiL `bnty_0393`** (*"DISCOVERY: Asteroid precovery in archival survey images"*).

## Summary of Vetted Archival Precovery Survivors

1. **Primary 6-Epoch Linked Archival ZTF Precovery Tracklet (`ZTF20aaekknk` + `ZTF20aaelvhs` + `ZTF20aaemjtd`, `2020-01-07 08:40:12 .. 11:36:46 UTC`, `MJD 58855.361250 .. 58855.483866`)**:
   - **Why Unreported / Fragmented in Archival Survey Images:** Moving at `13.0710"/hr` (`vx = -12.1910"/hr, vy = -4.7149"/hr`), the object traversed **`38.47"`** across `176.57 minutes` (`2.943 hours`), exceeding ZTF's `1.5"` fixed-position alert association gate and splitting into 3 separate transient OIDs (`ZTF20aaekknk` with `3` `zr` detections, `ZTF20aaelvhs` with `1` `zg` detection, and `ZTF20aaemjtd` with `2` `zg` detections).
   - **Astrometric & Keplerian Orbit Fit:**
     - Short-arc 3-epoch `zr` fit (`dt = 2.75 min`, `disp = 0.444"`): `rate = 9.4085"/hr`, `PA = 245.72°`, **`RMS = 0.0176"`** (`[0.0182", 0.0238", 0.0056"]`).
     - Full 6-epoch linked `zr + zg` fit (`dt = 176.57 min`, `disp = 38.47"`): `rate = 13.0710"/hr`, `PA = 248.86°`, **`RMS = 0.0869"`** (`[0.060", 0.061", 0.098", 0.141", 0.028", 0.088"]`), color `zg - zr = +0.714 mag`.
     - Bound heliocentric Keplerian elements (`JD 2458855.861250`, $\Delta = 1.309\text{ AU}$, $r_h = 2.1099\text{ AU}$, $v_{\text{helio}} = 21.186\text{ km/s}$): $a = 2.2627\text{ AU}$, $e = 0.1215$, $i = 3.506^\circ$, $\Omega = 288.00^\circ$, $\omega = 143.01^\circ$, $q = 1.9878\text{ AU}$, $Q = 2.5376\text{ AU}$, $P = 3.404\text{ yr}$.
   - **Archival FITS Cutout Evidence (`fits_stamps/`):** 18 FITS stamps (`6 epochs x {science, template, difference}`, `63x63` px, `1.01"/px`) verifying `SNR_ap = 48.24..58.24` in `science` and `46.15..55.38` in `difference`, with `SNR_ap = 0.26..1.46` (`0` stationary background source) in the co-added archival `template` FITS and `Gaia DR3` (`0` stars within `13.8"`).
   - **Minor Planet Center (`MPC get-obs`) Verification:** Official MPC Observation Database (`https://data.minorplanetcenter.net/api/get-obs`) returns `3,497` historical optical observations (`70` from Palomar `I41` on other dates as positive controls) while proving **`0` observations (`on_date_2020_01_07 = 0`, `on_date_I41 = 0`) were ever reported to the Minor Planet Center on `2020-01-07` (`MJD 58855`)**.

2. **Companion Archival Precovery Tracklets (`0` Observations Reported to MPC on Observation Date):**
   - **`ZTF18adcbjub`** (`2018-12-31 02:18:05 .. 02:46:25 UTC`, `MJD 58483.095891 .. 58483.115567`, `N = 3`, `dt = 28.33 min`, `disp = 1.118"`, `rate = 2.3512"/hr`, `PA = 65.68°`, `RMS = 0.0401"`, `science SNR_ap = 29.20..38.71`, `template SNR_ap = 1.04..1.95`, `MPC get-obs on 2018-12-31 = 0` vs `2,331` positive-control observations).
   - **`ZTF20aaekknm` + `ZTF20aaelvhv` + `ZTF20aaemjte`** (`2020-01-07 08:40:12 .. 11:34:49 UTC`, `MJD 58855.361250 .. 58855.482512`, `N = 4` linked detections across 3 fragmented OIDs, `dt = 174.62 min`, `disp = 35.25"`, `rate = 12.11"/hr`, `RMS = 0.052"`, `MPC get-obs on 2020-01-07 = 0` vs `3,893` positive-control observations).

3. **Uncataloged Archival Detections (`ssdistnr = -999.0`, `ssnamenr = "null"`, `0` SkyBoT Match within `50"`):**
   - **`ZTF20aaelvhz`** (`MJD 58855.459919`, `RA = 154.084677°, Dec = +8.064526°`, `ssdistnr = -999.0`, `nearest SkyBoT = 157.80"`) and **`ZTF20aaelvhu`** (`MJD 58855.459919`, `RA = 154.307594°, Dec = +8.198671°`, `ssdistnr = -999.0`, `nearest SkyBoT = 51.03"`).

## Reproduction

```bash
python verify_bnty_0393.py
```
