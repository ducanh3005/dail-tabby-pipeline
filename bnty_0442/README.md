# DAiL `bnty_0442` — Multi-Survey Archival Confirmation of a New Variable Star

- **Hunter**: `ducanh3005`
- **Pipeline Version**: `multisurvey-var-confirm-v1.0.0` (`2026-11-05`)
- **Repository Path**: `https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/bnty_0442`
- **Archival Policy**: 100% public archival records only (`ESA Gaia DR3 I/358/veb & DataLink Epoch Photometry`, `NASA TESS QLP FITS Light Curves via MAST`, `Palomar ZTF DR via IRSA`, `MAST TIC v8.2`, `VizieR B/vsx/vsx, II/366/catv2021, J/ApJS/213/9, II/264/asas3, I/239/hip_main, J/ApJS/258/16, B/gcvs/gcvs_cat`); zero AAVSO data/contact and zero telescope booking.

---

## 1. Executive Summary & Target Selection

We confirm two single-survey eclipsing variable-star candidates across **three independent public time-domain surveys** (`ESA Gaia DR3`, `NASA TESS QLP`, and `Palomar ZTF DR`), reporting the phase-fold in each survey separately with depths/amplitudes and point counts in primary eclipse, secondary eclipse, and quadrature maximum, and assigning the variability to each target versus its neighbours within $r \le 60''$ via rigorous flux-dilution bounds:

1. **Primary Target (`ASASSN-V J092057.16+543942.3` / `Gaia DR3 1023231501066579840` / `TIC 137675945` / `2MASS J09205715+5439422`)**:
   - **Coordinates (ICRS J2000)**: $\text{RA} = 140.2381666^\circ$, $\text{Dec} = +54.6617504^\circ$ ($G = 13.3758$, $G_{\text{BP}} = 13.8208$, $G_{\text{RP}} = 12.7136$, $T = 12.7981$, $T_{\text{eff}} = 5309\text{ K}$, $\varpi = 2.2090\text{ mas}$).
   - **Claimed Discovery Period**: $P_{\text{claimed}} = 0.71746200\text{ d}$ (`ASAS-SN` / `VSX`; `Gaia DR3 I/358/veb` catalog period $P_{\text{Gaia}} = 0.71746361 \pm 0.00002272\text{ d}$; joint 3-survey refined period $P_{\text{joint}} = 0.71745737\text{ d}$, $T_0 = \text{BJD } 2458878.352785$).
2. **Secondary Target (`Gaia DR3 2014878564261767680` / `TIC 435354753` / `2MASS J23072975+6106266`)**:
   - **Coordinates (ICRS J2000)**: $\text{RA} = 346.8739511^\circ$, $\text{Dec} = +61.1073977^\circ$ ($G = 13.8698$, $G_{\text{BP}} = 14.3679$, $G_{\text{RP}} = 13.1798$, $T = 13.2562$, $T_{\text{eff}} = 7025\text{ K}$, $\varpi = 0.6137\text{ mas}$).
   - **Single-Survey Discovery & Multi-Survey Period De-Aliasing**: Found exclusively in `Gaia DR3 I/358/veb` (sole entry in VSX; 0 entries in ASAS-SN, ZTF, CSS, ASAS-3, Hipparcos, TESS-EB, or GCVS). Because Gaia DR3 caught only two deep eclipses separated by $\Delta t = 659.2140\text{ d}$ (`BJD 2457225.0233` and `2457884.2373`), `I/358/veb` assigned cycle count $N = 615 \implies P_{\text{Gaia,cat}} = 1.07195519 \pm 0.00002675\text{ d}$. Combining `Gaia DR3` (`47` transits), `TESS QLP` (`S17, S24, S57, S58` — `23,883` cadences), and `ZTF DR` (`3,216` epochs) over a 9.5-year baseline (`961` cycles) uniquely resolves the cycle count to $N = 183 \implies P_{\text{true}} = \frac{615}{183} P_{\text{Gaia,cat}} = 3.60205010\text{ d}$ ($T_0 = \text{BJD } 2458766.723845$, observed simultaneously by TESS S17 and ZTF `zr`).

---

## 2. Separate Phase-Fold Results Across Public Surveys

### 2.1 Target 1 (`TIC 137675945` / `Gaia DR3 1023231501066579840`, $P = 0.71745737\text{ d}$, $T_0 = \text{BJD } 2458878.352785$)

| Survey Leg & Band / Sector | Status | $N_{\text{total}}$ | $N_{\text{ecl,1}}$ (Core) | $N_{\text{ecl,2}}$ | $N_{\text{max}}$ | Baseline Mag / Norm Flux | Primary Depth Peak (`%` / `mag`) | Primary Depth Core (`%` / `mag`) | Secondary Depth Peak (`%` / `mag`) | Secondary Depth Core (`%` / `mag`) |
|---|---|---|---|---|---|---|---|---|---|---|
| **Leg 1: Gaia DR3 `G`** | `found` | `37` | `3` (`1`) | `7` | `12` | `13.3490 mag` | `25.55%` / `0.3203 mag` | `25.55%` / `0.3203 mag` | `20.90%` / `0.2546 mag` | `20.90%` / `0.2546 mag` |
| **Leg 1: Gaia DR3 `BP`** | `found` | `36` | `2` (`1`) | `7` | `12` | `13.8208 mag` | `26.02%` / `0.3272 mag` | `26.02%` / `0.3272 mag` | `20.89%` / `0.2544 mag` | `20.89%` / `0.2544 mag` |
| **Leg 1: Gaia DR3 `RP`** | `found` | `36` | `2` (`1`) | `7` | `12` | `12.7136 mag` | `24.10%` / `0.2994 mag` | `24.10%` / `0.2994 mag` | `19.83%` / `0.2399 mag` | `19.83%` / `0.2399 mag` |
| **Leg 2: TESS QLP `S21+S47` Combined (`SAP`)** | `found` | `4,051` | `618` (`246`) | `625` | `1,282` | `1.00870` | `30.25%` / `0.3911 mag` | `23.50%` / `0.2908 mag` | `27.14%` / `0.3437 mag` | `21.38%` / `0.2612 mag` |
| **Leg 2: TESS QLP `S21` (`SAP`)** | `found` | `1,093` | `164` (`65`) | `172` | `347` | `1.00918` | `28.56%` / `0.3652 mag` | `24.21%` / `0.3009 mag` | `25.25%` / `0.3160 mag` | `21.74%` / `0.2662 mag` |
| **Leg 2: TESS QLP `S47` (`SAP`)** | `found` | `2,958` | `454` (`181`) | `453` | `935` | `1.00850` | `30.25%` / `0.3910 mag` | `23.38%` / `0.2891 mag` | `27.14%` / `0.3437 mag` | `21.25%` / `0.2594 mag` |
| **Leg 3: ZTF DR `zg+zr` Combined** | `found` | `2,314` | `372` (`136`) | `339` | `711` | `1.01659` | `31.36%` / `0.4085 mag` | `23.33%` / `0.2884 mag` | `32.05%` / `0.4195 mag` | `21.35%` / `0.2608 mag` |
| **Leg 3: ZTF DR `zg` Band** | `found` | `953` | `139` (`42`) | `130` | `320` | `13.9143 mag` | `31.17%` / `0.4056 mag` | `24.24%` / `0.3014 mag` | `31.19%` / `0.4059 mag` | `20.87%` / `0.2541 mag` |
| **Leg 3: ZTF DR `zr` Band** | `found` | `1,361` | `233` (`94`) | `209` | `391` | `13.2348 mag` | `30.01%` / `0.3875 mag` | `23.19%` / `0.2864 mag` | `32.15%` / `0.4211 mag` | `21.58%` / `0.2639 mag` |
| **Leg 4: Catalina CSS (`J/ApJS/213/9`)** | `none` | `0` | — | — | — | — | — | — | — | — |
| **Leg 5: ASAS-3 (`II/264/asas3`)** | `none` | `0` | — | — | — | — | — | — | — | — |
| **Leg 6: Hipparcos (`I/239/hip_main`)** | `none` | `0` | — | — | — | — | — | — | — | — |
| **Leg 7: TESS-EB (`J/ApJS/258/16`)** | `none` | `0` | — | — | — | — | — | — | — | — |
| **Leg 8: GCVS (`B/gcvs/gcvs_cat`)** | `none` | `0` | — | — | — | — | — | — | — | — |

### 2.2 Target 2 (`TIC 435354753` / `Gaia DR3 2014878564261767680`, $P_{\text{true}} = 3.60205010\text{ d}$, $T_0 = \text{BJD } 2458766.723845$)

| Survey Leg & Band / Sector | Status | $N_{\text{total}}$ | $N_{\text{ecl,1}}$ (Core) | $N_{\text{ecl,2}}$ | $N_{\text{max}}$ | Baseline Mag / Norm Flux | Primary Depth Peak (`%` / `mag`) | Primary Depth Core (`%` / `mag`) | OOE Scatter (`%`) |
|---|---|---|---|---|---|---|---|---|---|
| **Leg 1: Gaia DR3 `G`** | `found` | `47` | `3` (`3`) | `4` | `21` | `13.8585 mag` | `36.81%` / `0.4985 mag` | `36.40%` / `0.4913 mag` | `0.21%` |
| **Leg 1: Gaia DR3 `BP`** | `found` | `47` | `3` (`3`) | `4` | `21` | `14.3669 mag` | `39.15%` / `0.5393 mag` | `37.90%` / `0.5172 mag` | `0.73%` |
| **Leg 1: Gaia DR3 `RP`** | `found` | `47` | `3` (`3`) | `4` | `21` | `13.1782 mag` | `35.12%` / `0.4699 mag` | `33.24%` / `0.4388 mag` | `0.55%` |
| **Leg 2: TESS QLP `S17+S24+S57+S58` (`SAP`)** | `found` | `23,883` | `1,775` (`712`) | `1,531` | `7,683` | `1.00135` | `46.02%` / `0.6695 mag` | `38.85%` / `0.5341 mag` | `2.12%` |
| **Leg 3: ZTF DR `zg+zr` Combined** | `found` | `3,216` | `227` (`93`) | `353` | `1,051` | `1.00091` | `43.72%` / `0.6241 mag` | `39.14%` / `0.5392 mag` | `1.38%` |
| **Leg 3: ZTF DR `zg` Band** | `found` | `1,391` | `109` (`44`) | `92` | `425` | `14.5375 mag` | `43.74%` / `0.6245 mag` | `40.11%` / `0.5565 mag` | `1.48%` |
| **Leg 3: ZTF DR `zr` Band** | `found` | `1,825` | `118` (`49`) | `261` | `626` | `13.8164 mag` | `42.63%` / `0.6034 mag` | `38.60%` / `0.5295 mag` | `1.28%` |

---

## 3. Neighbour Flux-Dilution Bounds (`MAST TIC v8.2` & `Gaia DR3 I/355/gaiadr3`, $r \le 60''$)

1. **Target 1 (`TIC 137675945` / `Gaia DR3 1023231501066579840`)**:
   - **Within $r \le 15''$ (covering both the $0.2''$ Gaia DR3 window and $2.0''$ ZTF PSF)**: **0 neighbours** ($0.0000\%$ flux dilution).
   - **Within $r \le 20''$ (central $21''$ TESS pixel)**: Only 1 faint neighbour (`TIC 137675946` / `Gaia DR3 1023230745152335616` at $\text{sep} = 17.784''$, $T = 16.1637$, $G = 17.1176$, $\Delta T = +3.3656\text{ mag}$, $F_{\text{nbr}}/F_{\text{target}} = 4.5057\%$ in $T$, $3.1863\%$ in $G$), capping maximum possible blended depth at **$4.3114\%$ in $T$**.
   - **All 6 Neighbours within $r \le 60''$ Combined**: Total flux ratio $\sum F_{\text{nbr}}/F_{\text{target}} = 7.8316\%$ in $T$ ($6.7601\%$ in $G$), capping maximum possible blended eclipse depth (even under a simultaneous 100% total eclipse of all 6 neighbours) at **$7.2628\%$ in $T$ ($6.3321\%$ in $G$)** — smaller by **$4.16\times$** than the observed $30.25\%$ TESS primary eclipse ($4.03\times$ smaller than the $25.55\%$ Gaia $G$ eclipse, and infinite margin in the unblended ZTF/Gaia apertures).
2. **Target 2 (`TIC 435354753` / `Gaia DR3 2014878564261767680`)**:
   - **Within $r \le 8.0''$ (covering the $0.2''$ Gaia DR3 window and $2.0''$ ZTF PSF)**: **0 neighbours** ($0.0000\%$ flux dilution), where ZTF (`zg` $43.74\%$, `zr` $42.63\%$) and Gaia ($G$ $36.81\%$) completely resolve the target.
   - **Within $r \le 15''$ ($5$ faint neighbours)**: Maximum combined blended depth $= \mathbf{12.0652\%}$ in $G$ vs **$36.8145\%$** observed ($3.05\times$ hard bound kill).
   - **Within $r \le 20''$ (central $21''$ TESS pixel)**: Maximum combined blended depth $= \mathbf{13.7506\%}$ in $T$ vs **$46.0233\%$** observed ($3.35\times$ hard bound kill).

---

## 4. Reproducibility & Verification

```bash
python bnty_0442/fold_multisurvey_0442.py
python bnty_0442/verify_bnty_0442.py
```
