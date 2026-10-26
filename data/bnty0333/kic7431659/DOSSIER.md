# bnty_0333 Dossier — KIC 7431659 (Q7 M-Dwarf Dipper, 100% of Available Kepler Quarters)

- **Repository**: `https://github.com/ducanh3005/dail-tabby-pipeline`
- **Target**: `KIC 7431659` (`2MASS J19092969+4301384`), RA `287.373720` deg, Dec `+43.027359` deg, `Kp = 16.248`, `Teff = 3422 K`, `R* = 0.334 R_sun`
- **Submission text SHA-256**: `d2392e97dadf4ad30d409bf4e618f7bd3b9d1a45fedb1cef0239ce25bbe6c599` (`4785` bytes)

## Exact Submission Text (`SUBMISSION.txt`)

```text
DAiL bnty_0333 — KIC 7431659 (Q7 M-Dwarf Dipper, 100% of Available Kepler Quarters)
Repo (stdlib code, JSON, claim-checker): https://github.com/ducanh3005/dail-tabby-pipeline
Star: KIC 7431659 (2MASS J19092969+4301384), RA=287.373720, Dec=+43.027359, Kp=16.248, Teff=3422K, logg=4.914, R*=0.334Rsun, M*=0.334Msun.

1. GATE 1 (NO KOI, LIVE NASA TAP + CONTROLS)
- cumulative (kepid=7431659): n_rows=0 (header only, 0 data rows); q1_q17_dr25_koi (kepid=7431659): n_rows=0.
- Controls: positive n_rows=4 [9101271:K07926.01(FALSE POSITIVE,fp_nt=1);10963065:K01612.01(CONFIRMED,fp_nt=0);11904151:K00072.01(CONFIRMED,fp_nt=0);11904151:K00072.02(CONFIRMED,fp_nt=0)]; negative (99999998,99999999) n_rows=0.
- Unclassified DR25 TCE: plnt=1, P=1.04984 d, depth=2.65e+04 ppm, SNR=110.8, dicco=0.10151".

2. GATE 2 (NOT IN KEPLER EB / VSX / SIMBAD + CONTROLS)
- Kepler EB (Kirk+ 2016 J/AJ/151/68, sha256=eeb03622ef97..., 2876 rows): KIC 7431659->0 rows. Controls: KIC 9101279->1 row (P=1.8114606 d, Kp=13.947, raw='09101279    1.8114606  0.000'...); KIC 7431665->1 row (P=281.4 d, Kp=10.974).
- AAVSO VSX (B/vsx/vsx, 30" cone at 287.373720,43.027359): n_rows=0 (data=[]). Control (30" at KIC 7431665): n_rows=1 (raw=[479117, 'KIC 7431665', 'EA:+HB', 281.4, 287.377, 43.0095]).
- SIMBAD (15" cone): n_rows=1->['2MASS J19092969+4301384', '*'] (ordinary star '*'); control KIC 8462852->n_rows=4 (['TYC 3162-665-1', '*']).

3. GATE 3 (FULL LIGHT CURVE BLS & LIKE-FOR-LIKE P vs 2P ALIAS TEST)
- Coverage: 1/1 quarters (100.0%: Q7), 4226 cadences, BKJD 630.1954..719.5480 (89.3526 d), detrended MAD sigma=2.1503%.
- Best P=1.0498580 d: dchi2=2921813.7879, SNR=199.87, depth=3.8261%, dur=0.4000 d, epoch=630.50700 BKJD, n_in=1691, odd=5.2531%, even=5.27% (delta=0.0168%).
- Exact 2P=2.0997160 d (same grid [0.04, 0.06, 0.08, 0.12, 0.16, 0.2] d, 300 bins, dip_only=True): dchi2=1216920.7957, dchi2(2P)/dchi2(P)=0.4165, SNR=48.11, depth=3.2230%, dur=0.1680 d, n_in=735; +/-1% 2P band best (2.0997160 d) dchi2=1216920.7957 (ratio=0.4165). 2P is weaker with no alternating EB depth.

4. GATES 4 & 5 (PDCSAP >= 5% BOX-MEAN, RAW SAP DIP, PEAK DEPTH & PER-CADENCE SNR)
- Q7 OOT 1.4826*MAD scatter: PDCSAP sigma_q=1.8949%, SAP sigma_q=1.8974%.
- E1_BKJD647p34 (BKJD 647.3400 [647.2977..647.3794], n=5, 2.45h): PDCSAP box=5.283% (pk=5.361%), SAP box=5.119% (pk=5.203%), sigma_loc=1.1790%, SNR_cad=2.79 (pk=2.83, loc=4.48, evt=6.23).
- E2_BKJD645p23 (BKJD 645.2350 [645.1931..645.2748], n=5, 2.45h): PDCSAP box=5.153% (pk=5.345%), SAP box=4.952% (pk=5.159%), sigma_loc=1.2769%, SNR_cad=2.72 (pk=2.82, loc=4.04, evt=6.08).
- E3_BKJD642p11 (BKJD 642.1050 [642.0669..642.1486], n=5, 2.45h): PDCSAP box=5.056% (pk=5.423%), SAP box=4.879% (pk=5.231%), sigma_loc=1.2325%, SNR_cad=2.67 (pk=2.86, loc=4.10, evt=5.97).

5. GATE 6 (STAMP GEOMETRY EVIDENCED & CENTROID SHIFT < 1.0 MILLIPIXEL)
- kplr007431659-2010355172524_lpd-targ.fits APERTURE: NAXIS1=5, NAXIS2=4, counts={'0': 1, '1': 17, '3': 2} (2 target px val=3 at [12, 13]). Orientation (4/4 votes for Layout A=A_5wide_4tall vs B_4wide_5tall): T1 sum(target)/SAP_FLUX: A=1.0000000661 vs B=0.0458392496; T2 scatter vs MOM_CENTR1: A=4.640 vs B=12.352 mpix; T3 peak idx=12 on mask=3; T4 always-NaN=1 matches mask=0 (1); POS_CORR1 r_x=0.9977 (r_y=const_row, n=3913).
- Centroid shifts (<1.000 mpix): TPF Layout A=[0.434, 0.439, 0.079] mpix (max=0.439 mpix); layout-free MOM_CENTR=[0.738, 0.492, 0.775] mpix (max=0.775 mpix). Primary E1_BKJD647p34: TPF (-0.434,0.000)->0.434 mpix; MOM_CENTR (-0.688,0.268)->0.738 mpix.

6. GATE 7 (NEIGHBOUR EXCLUSION FROM LIGHT CURVE & FOLD-DOWN ALIAS TRAP)
- gal2eq(0,0)=(266.40499,-28.93617) vs (266.405,-28.9362) [ok=True].
- KIC 7431665 (Kepler EB, sep=64.73", P_nb=281.4 d, Kp=10.974): BKJD0=172.28158 predicts eclipses at [453.6816, 735.0816] ->0 eclipses in Q7.
- KIC 7431703 (Kepler EB, sep=260.87", P_nb=0.5725258 d): dchi2=166.5901 (SNR=0.50, depth=0.0339%) = 0.08x local 0.45-0.85 d median (2123.3963), 17538.94x weaker than P.
- KIC 7431632 (AAVSO VSX OID 519915, sep=72.74", P_nb=18.972 d): dchi2=51902.2465 (SNR=7.98, depth=2.7201%) = 24.44x local 0.45-0.85 d median (2123.3963), 56.29x weaker than P.
- Fold-down alias trap: P / 2=0.5249290 d gives dchi2=42420.6186 (19.98x local median) — target signal folded by 2, not a blend.

7. ARCHIVE URLS & ZERO-KEY REPRODUCTION
- LC: https://archive.stsci.edu/missions/kepler/lightcurves/0074/007431659/kplr007431659-2010355172524_llc.fits (sha256=a0d3c63eafe81336...; 1 file(s))
- TPF: https://archive.stsci.edu/missions/kepler/target_pixel_files/0074/007431659/kplr007431659-2010355172524_lpd-targ.fits.gz (sha256=96a787f3c32ac733...)
- Run: python3 src/fetch_mast_payloads.py && python3 src/run_pipeline.py && python3 src/build_submissions.py && python3 scripts/check_claims.py
```
