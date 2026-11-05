# DAiL `bnty_0439` — Fermi-LAT 4FGL-DR4 Unassociated Sources: Vetted Counterparts, Quantified

- **Hunter:** `ducanh3005`
- **Method Version:** `v1.0.0` (`2026-11-04`)
- **Repository Path:** [`https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/bnty_0439`](https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/bnty_0439)
- **Offline Reproduction (zero API keys, zero network):**
  ```bash
  python3 bnty_0439/vet_fermi_counterparts.py
  python3 bnty_0439/verify_bnty_0439.py
  ```

---

## 1. Scope, Prior-Bounty Exclusion & Epoch/Observation Log

We select **4 tight-ellipse ($a_{95} \in [82.4'', 123.5'']$), high-latitude ($|b| \in [17.53^\circ, 61.19^\circ]$) Fermi-LAT 4FGL-DR4 unassociated sources (`cl1 == ""`)** from `raw/unassociated_4fgl_dr4.json` (`IX/72/4fgldr4`, Ballet et al. 2023), strictly excluding all 16 sources claimed or analyzed in earlier DAiL Fermi bounties (`bnty_0276`, `bnty_0314`, `bnty_0348`: `J0226.9+7744`, `J0843.7-6933`, `J1058.4-6625`, `J1225.9+2951`, `J1250.9-4943`, `J1338.0-4159`, `J1441.4-1934`, `J1514.8+4448`, `J1613.1-3840`, `J1754.1-4333`, `J1842.1+2737`, `J1910.8+2856`, `J1916.8-3025`, `J1927.5+0154`, `J2108.7-0408`, `J2112.5-3043`).

| Source (`4FGL-DR4`) | RA (J2000) | Dec (J2000) | $b_{\text{gal}}$ | $a_{95} \times b_{95}$ (`PA`) | $\sigma_{4\text{FGL}}$ ($F_{1\text{–}100\text{ GeV}}$) | Query Timestamp (UTC) | Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`4FGL J2240.3-5241`** | $340.0858^\circ$ | $-52.6862^\circ$ | $-54.71^\circ$ | $90.00'' \times 85.68''$ ($+86.8^\circ$) | $11.51\sigma$ ($5.02\times 10^{-10}$) | `2026-11-04T17:46:30Z` | **SURVIVING HSP BLAZAR (`3HSP J224017.1-524113` / `5XMM` / `SUMSS` / `WISEA`, $z=0.2223$)** |
| **`4FGL J1410.7+7405`** | $212.6869^\circ$ | $+74.0899^\circ$ | $+41.91^\circ$ | $90.00'' \times 87.84''$ ($-86.3^\circ$) | $23.28\sigma$ ($3.77\times 10^{-10}$) | `2026-11-04T17:47:15Z` | **SURVIVING HSP BLAZAR (`3HSP J141046.0+740511` / `2SXPS` / `VLA` / `WISEA`, $z=0.4290$)** |
| **`4FGL J0251.1-1830`** | $42.7835^\circ$ | $-18.5093^\circ$ | $-61.19^\circ$ | $123.48'' \times 123.12''$ ($-41.5^\circ$) | $10.47\sigma$ ($1.29\times 10^{-10}$) | `2026-11-04T17:53:10Z` | **SURVIVING HSP BLAZAR (`3HSP J025111.5-183112` / `NVSS` / `2SXPS` / `WISEA`, $z=0.5000$)** |
| **`4FGL J1539.4-3323`** | $234.8511^\circ$ | $-33.3987^\circ$ | $+17.53^\circ$ | $82.44'' \times 77.40''$ ($+27.5^\circ$) | $39.63\sigma$ ($2.48\times 10^{-9}$) | `2026-11-04T17:45:40Z` | **QUANTIFIED BLAZAR NULL ($35/35$ TIC/WISE stars killed; radio/X-ray limits stated; MSP candidate)** |

---

## 2. Versioned Methods (`v1.0.0`)

1. **95% Error Ellipse Geometry:**
   For target center $(\alpha_0, \delta_0)$ and candidate $(\alpha, \delta)$, sky offsets $\Delta\alpha^* = (\alpha - \alpha_0)\cos\delta_0$ and $\Delta\delta = \delta - \delta_0$ are rotated by $\theta = \text{PA}_{95}$ (east of north):
   $$x = \Delta\alpha^*\sin\theta + \Delta\delta\cos\theta, \qquad y = \Delta\alpha^*\cos\theta - \Delta\delta\sin\theta, \qquad r_{\text{ell}} = \sqrt{(x/a_{95})^2 + (y/b_{95})^2} \le 1.0$$
2. **Poisson Chance-Coincidence Bounds ($P_{\text{chance}}$):**
   From the local background surface density $\Sigma = \max(N_{\text{cone}}, 1) / (\pi R_{\text{cone}}^2)$ measured in the committed $3.0'$ (`MAST TIC`/`NED`) or $5.0'$ (`HEASARC`) cone queries:
   $$P_{\text{chance}}(\le \theta_{\text{sep}}) = 1 - \exp\!\left(-\Sigma \pi \theta_{\text{sep}}^2\right), \qquad P_{\text{chance}}(\text{in } 95\%\text{ ell}) = 1 - \exp\!\left(-\Sigma \pi a_{95} b_{95}\right)$$
3. **Quantitative Alternative-Kill Thresholds:**
   - **Galactic Foreground Star Kill (Astrometry):** Killed if Gaia DR3 parallax significance $\varpi / \sigma_\varpi \ge 3.0\sigma$ or total proper motion $\mu_{\text{tot}} = \sqrt{\mu_{\alpha^*}^2 + \mu_\delta^2} \ge 5.0\text{ mas yr}^{-1}$.
   - **Stellar Photosphere Kill (Mid-IR Color):** Killed as a blazar candidate if AllWISE $W1 - W2 < 0.50\text{ mag}$ (outside the Massaro/D'Abrusco WIBRaLS blazar strip $W1 - W2 \in [0.50, 2.20]$, $W2 - W3 \in [1.20, 4.50]$) or undetected in WISE ($W1 > 17.1\text{ mag}$, $W2 > 15.7\text{ mag}$ $5\sigma$ AllWISE limits) without radio/X-ray emission.
   - **Faint Spur / Radio-Quiet X-Ray Kill:** Secondary X-ray detections inside the ellipse are killed if X-ray $\text{SNR} < 3.0$ or radio flux density violates $S_{1.4\text{ GHz}} < 2.5\text{ mJy}$ (`NVSS`) / $S_{843\text{ MHz}} < 6.0\text{ mJy}$ (`SUMSS`) while a bright radio-loud X-ray blazar co-exists at smaller $r_{\text{ell}}$.
4. **Non-Detections vs. `UNUSABLE` Checks:**
   - **Quantified Non-Detections:** `NVSS` ($\delta \ge -40^\circ$): $S_{1.4\text{ GHz}} < 2.5\text{ mJy}$ ($5\sigma$); `SUMSS` ($\delta \le -30^\circ$): $S_{843\text{ MHz}} < 6.0\text{ mJy}$ ($5\sigma$); `VLSSr` ($\delta \ge -30^\circ$): $S_{74\text{ MHz}} < 0.50\text{ Jy}$; `Swift 2SXPS`: $F_{0.3\text{–}10\text{ keV}} < 6.5\times 10^{-14}\text{ erg cm}^{-2}\text{ s}^{-1}$; `ROSAT 2RXS`: $F_{0.1\text{–}2.4\text{ keV}} < 1.0\times 10^{-13}\text{ erg cm}^{-2}\text{ s}^{-1}$.
   - **`UNUSABLE` Checks:** `NVSS` at $\delta = -52.69^\circ < -40^\circ$ (`UNUSABLE`); `SUMSS` at $\delta > -30^\circ$ (`UNUSABLE`); `FIRST` outside $[-11.5^\circ, +64.5^\circ]$ (`UNUSABLE`); `Chandra CSC` (`UNUSABLE`, no pointing); `CDS SIMBAD` & `VizieR` mirrors (`UNUSABLE`, TCP timeout `WinError 10060` during `2026-11-04T17:40Z`; never counted as a non-detection).

---

## 3. Per-Source Vetting Summary & Complete In-Ellipse Counterpart Tables

All 73 in-ellipse rows across `MAST TIC v8.2` (`Gaia DR3` + `AllWISE` + `2MASS`) and `HEASARC` (`xmmssc`, `swift2sxps`, `nvss`, `sumss`, `milliquas`), plus all 197 in-ellipse `NED` rows, are stored in [`results/fermi_vetted_counterparts.json`](results/fermi_vetted_counterparts.json) and [`results/in_ellipse_counterparts.csv`](results/in_ellipse_counterparts.csv).

### 3.1. `4FGL J2240.3-5241` (`13` TIC/Gaia/WISE, `28` NED, `5` HEASARC in 95% Ellipse)
- **Surviving Counterpart (`r_ell = 0.278–0.294`, $\theta_{\text{sep}} = 25.03''\text{–}26.42''$):**
  - `5XMM J224017.8-524114` (`xmmssc`, $\theta=25.03''$, $r_{\text{ell}}=0.2782$, $F_{0.2\text{–}12\text{ keV}} = (1.797 \pm 0.209)\times 10^{-13}\text{ erg cm}^{-2}\text{ s}^{-1}$, $\text{SNR}=8.60\sigma$, $P_{\text{chance,sep}}=0.08015$) + `XRT J224017.55-524112.3` ($\theta=27.70''$) + `SWIFT J224017.5-524117` ($\theta=28.89''$) + `3FHL J2240.3-5240` ($\theta=33.12''$).
  - `SUMSS J224017-524111` (`sumss`, $\theta=25.49''$, $r_{\text{ell}}=0.2832$, $S_{843\text{ MHz}} = 19.4 \pm 1.0\text{ mJy}$, $P_{\text{chance,sep}}=0.00719 < 0.01$) + `SPT-S J224016-5241.3` ($\theta=35.64''$).
  - `3HSPJ224017.1-524113` (`milliquas`, $\theta=26.27''$, $r_{\text{ell}}=0.2920$, $R=16.61, B=18.33$, `RACD J224017.7-524113`, $P_{\text{chance,sep}}=0.00764 < 0.01$).
  - `TIC 161175075` / `Gaia DR3 6507562240186836992` / `WISEA J224017.71-524113.8` ($\theta=26.26''$, $r_{\text{ell}}=0.2920$, $W1=13.797$, **$W1-W2 = 0.577\text{ mag}$, $W2-W3 = 2.085\text{ mag}$**, spectroscopic redshift $z = 0.222300$, $P_{\text{chance,sep,blazar}} = 0.02106 < 0.05$).
  - **What would kill this surviving candidate:** VLBI 8.4 GHz core flux density $S_{\text{core}} < 1.0\text{ mJy}$, Gaia DR3 parallax $\varpi/\sigma_\varpi \ge 3.0\sigma$, or optical spectroscopy refuting $z=0.2223$ with $z=0$ stellar absorption lines.
- **Alternative-Kills on the Other 12 In-Ellipse TIC/Gaia Sources & 2 Faint 5XMM Sources:**
  - `5XMM J224015.6-524035` ($\theta=57.01''$, $r_{\text{ell}}=0.6473$): Killed by X-ray $\text{SNR} = 1.08/1.40 = 0.77 < 3.0\sigma$ and radio non-detection ($S_{843\text{ MHz}} < 6.0\text{ mJy}$).
  - `5XMM J224023.2-523953` ($\theta=80.96''$, $r_{\text{ell}}=0.9395$): Killed by low X-ray $\text{SNR} = 4.52/1.88 = 2.41 < 3.0\sigma$, outer ellipse location ($P_{\text{chance,sep}} = 0.5827$), and radio non-detection ($S_{843\text{ MHz}} < 6.0\text{ mJy}$).
  - All other 12 in-ellipse `MAST TIC` sources (`TIC 2055420395` at $23.62''$ with $\mu_{\text{tot}}=8.46\text{ mas/yr}$; `TIC 2055420407` at $32.11''$ with $\mu_{\text{tot}}=5.38\text{ mas/yr}$; `TIC 161175071` at $44.59''$ with $W1-W2=0.059 < 0.50$; `TIC 161175073` at $49.81''$ with $\varpi/\sigma_\varpi=7.61\sigma$, $W1-W2=-0.136$; `TIC 2055420393` at $51.46''$ with $\mu_{\text{tot}}=5.82\text{ mas/yr}$; `TIC 2055420394` at $60.12''$; `TIC 2055420408` at $62.95''$ with $\mu_{\text{tot}}=16.95\text{ mas/yr}$; `TIC 2055420399` at $66.05''$; `TIC 161175069` at $80.41''$ with $\varpi/\sigma_\varpi=3.83\sigma$, $W1-W2=0.275$; `TIC 2055420398` at $80.48''$ with $\mu_{\text{tot}}=62.25\text{ mas/yr}$; `TIC 2055420397` at $80.64''$; `TIC 161175078` at $81.00''$ with $W1-W2=-0.065$) are killed by $\varpi/\sigma_\varpi \ge 3.0\sigma$, $\mu_{\text{tot}} \ge 5.0\text{ mas/yr}$, or $W1-W2 < 0.50\text{ mag}$ ($W1 > 17.1\text{ mag}$).

### 3.2. `4FGL J1410.7+7405` (`6` TIC/Gaia/WISE, `27` NED, `3` HEASARC in 95% Ellipse)
- **Surviving Counterpart (`r_ell = 0.145–0.161`, $\theta_{\text{sep}} = 12.72''\text{–}14.15''$):**
  - `2SXPS J141045.6+740511` (`swift2sxps`, $\theta=12.72''$, $r_{\text{ell}}=0.1445$, rate $(4.482 \pm 0.901)\times 10^{-3}\text{ ct/s}$, $\text{SNR}=4.97\sigma$, $F_{0.3\text{–}10\text{ keV}} = 1.914\times 10^{-13}\text{ erg cm}^{-2}\text{ s}^{-1}$, $P_{\text{chance,sep}}=0.00538 < 0.01$) + `XRT J141045.6+740509.8` ($\theta=14.15''$).
  - `3HSPJ141046.0+740511` (`milliquas`, $\theta=13.51''$, $r_{\text{ell}}=0.1532$, $R=19.89, B=19.94$, radio counterpart `VLA J141046.08+740510.9`, $P_{\text{chance,sep}}=0.00203 < 0.01$).
  - `WISEA J141046.00+740511.2` / `TIC 1001569279` / `Gaia DR3 1711934622285213312` ($\theta=13.51''$, $r_{\text{ell}}=0.1530$, $\varpi = -0.244 \pm 0.333\text{ mas}$ [$\text{SNR}=-0.73$], $\mu_{\text{tot}} = 0.70\text{ mas/yr} < 5.0$, NED redshift $z = 0.429000$, $P_{\text{chance,sep,blazar}} = 0.00563 < 0.01$).
  - **What would kill this surviving candidate:** VLA 1.4/5 GHz core flux $S_{\text{radio}} < 0.5\text{ mJy}$, Gaia parallax $\varpi/\sigma_\varpi \ge 3.0\sigma$, or optical spectroscopy showing $z=0$ stellar absorption.
- **Alternative-Kills on the Other 5 In-Ellipse TIC/Gaia Sources & 1 Faint 2SXPS Source:**
  - `TIC 198514152` (`Gaia DR3 1711934622285215232` / `WISEA J141042.92+740534.5`, $\theta=13.69''$, $r_{\text{ell}}=0.1540$): Killed by **three** independent metrics: $\varpi = 3.8075 \pm 0.1164\text{ mas}$ (**$32.71\sigma \ge 3.0\sigma$**), $\mu_{\text{tot}} = 28.69\text{ mas/yr} \ge 5.0\text{ mas/yr}$, and $W1-W2 = 0.167\text{ mag} < 0.50\text{ mag}$.
  - `TIC 1001569320` ($\theta=45.57''$, $\mu_{\text{tot}}=14.57\text{ mas/yr} \ge 5.0$), `TIC 1001569281` ($\theta=71.99''$, $W1>17.1$), `TIC 1001569278` ($\theta=74.64''$, $W1>17.1$), `TIC 1001569282` ($\theta=79.39''$, $\mu_{\text{tot}}=20.73\text{ mas/yr} \ge 5.0$).
  - `2SXPS J141051.5+740414` ($\theta=74.79''$, $r_{\text{ell}}=0.8477$): Killed by X-ray $\text{SNR} = 1.645/0.618 = 2.66 < 3.0\sigma$, radio non-detection ($S_{1.4\text{ GHz}} < 2.5\text{ mJy}$), and $P_{\text{chance,sep}} = 0.1701 > 0.05$.

### 3.3. `4FGL J0251.1-1830` (`8` TIC/Gaia/WISE, `77` NED, `3` HEASARC in 95% Ellipse)
- **Surviving Counterpart (`r_ell = 0.503–0.521`, $\theta_{\text{sep}} = 62.06''\text{–}64.31''$):**
  - `NVSS J025111-183112` (`nvss`, $\theta=62.06''$, $r_{\text{ell}}=0.5027$, $S_{1.4\text{ GHz}} = 13.3 \pm 0.6\text{ mJy}$ [$22.2\sigma$], $P_{\text{chance,sep}}=0.04190 < 0.05$).
  - `3HSPJ025111.5-183112` (`milliquas`, $\theta=63.27''$, $r_{\text{ell}}=0.5124$, $R=18.94, B=19.58$, `VLA J025111.53-183112.3`, $z=0.500$, $P_{\text{chance,sep}}=0.04350 < 0.05$).
  - `2SXPS J025111.4-183114` (`swift2sxps`, $\theta=63.72''$, $r_{\text{ell}}=0.5161$, rate $(1.960 \pm 0.212)\times 10^{-2}\text{ ct/s}$ [$9.24\sigma$], $P_{\text{chance,sep}}=0.04411 < 0.05$) + `XRT J025111.7-183111.1` ($\theta=64.31''$).
  - `WISEA J025111.52-183112.7` (`NED UvS`, $\theta=63.27''$, $z=0.500000$) + `TIC 651805436` / `Gaia DR3 5129198825629823232` ($\theta=63.33''$, $r_{\text{ell}}=0.5129$, $\varpi = 0.524 \pm 0.625\text{ mas}$ [$\text{SNR}=0.84 < 3.0$], $\mu_{\text{tot}} = 1.15\text{ mas/yr} < 5.0$).
  - **What would kill this surviving candidate:** Gaia parallax $\varpi/\sigma_\varpi \ge 3.0\sigma$, proper motion $\mu_{\text{tot}} \ge 5.0\text{ mas/yr}$, or optical spectroscopy refuting $z=0.500$ with $z=0$ stellar lines.
- **Alternative-Kills on the Other 7 In-Ellipse TIC/Gaia Sources:**
  - `TIC 274016147` ($\theta=55.35''$, $\varpi/\sigma_\varpi=5.15\sigma$, $\mu_{\text{tot}}=5.72\text{ mas/yr}$, $W1-W2=-0.090$), `TIC 651805435` ($\theta=58.25''$, $\varpi/\sigma_\varpi=3.66\sigma$, $\mu_{\text{tot}}=5.00\text{ mas/yr}$), `TIC 274016146` ($\theta=69.34''$, $W1>17.1$), `TIC 651805437` ($\theta=79.85''$, $\mu_{\text{tot}}=10.57\text{ mas/yr}$), `TIC 274016150` ($\theta=103.81''$, $W1-W2=0.134 < 0.50$), `TIC 651805441` ($\theta=107.94''$, $\mu_{\text{tot}}=7.47\text{ mas/yr}$), `TIC 274016151` ($\theta=113.73''$, $\varpi/\sigma_\varpi=4.15\sigma$, $W1-W2=-0.056$).

### 3.4. `4FGL J1539.4-3323` (`35` TIC/Gaia/WISE, `65` NED, `0` Non-Fermi HEASARC in 95% Ellipse) — Quantified Blazar Null
- **Exhaustive Vetting of All 35 In-Ellipse TIC/Gaia/WISE Sources & 65 NED Infrared Sources:**
  - **WISE Blazar-Strip Check (`0 / 35` pass):** Among the 16 WISE-detected sources inside the $82.44'' \times 77.40''$ 95% ellipse (`TIC 8157608` at $2.68''$ with $W1-W2=-0.026$, $\varpi/\sigma_\varpi=3.77\sigma$; `TIC 8157605` at $14.94''$ with $W1-W2=-0.037$; `TIC 8157602` at $18.98''$ with $W1-W2=+0.013$, $\mu_{\text{tot}}=23.28\text{ mas/yr}$; ... up to `TIC 8157584` at $76.51''$ with $W1-W2=+0.042$), the maximum color is $W1-W2 = +0.152\text{ mag}$ (`TIC 8157613` at $59.69''$, $\mu_{\text{tot}}=6.76\text{ mas/yr} \ge 5.0$), **killing all 35 sources against the $W1-W2 \ge 0.50\text{ mag}$ blazar floor** (and killing the 19 WISE-undetected stars via $W1 > 17.1\text{ mag}$ + stellar $\varpi/\mu$).
  - **Quantified Multi-Wavelength Non-Detection Limits in the 95% Ellipse:**
    - `NVSS` ($1.4\text{ GHz}$): **$0$ in 95% ellipse** ($3$ in $5'$ cone; nearest at $129.7''$) $\rightarrow$ **$S_{1.4\text{ GHz}} < 2.5\text{ mJy}$ ($5\sigma$)**.
    - `SUMSS` ($843\text{ MHz}$): **$0$ in 95% ellipse** ($1$ in $5'$ cone at $231.2''$) $\rightarrow$ **$S_{843\text{ MHz}} < 6.0\text{ mJy}$ ($5\sigma$)**.
    - `Swift 2SXPS` ($0.3\text{–}10\text{ keV}$): **$0$ in 95% ellipse** ($5$ in $5'$ cone) $\rightarrow$ **$F_{0.3\text{–}10\text{ keV}} < 6.5\times 10^{-14}\text{ erg cm}^{-2}\text{ s}^{-1}$**.
    - `ROSAT 2RXS` ($0.1\text{–}2.4\text{ keV}$): **$0$ in 95% ellipse** $\rightarrow$ **$F_{0.1\text{–}2.4\text{ keV}} < 1.0\times 10^{-13}\text{ erg cm}^{-2}\text{ s}^{-1}$**.
    - `Milliquas` / `WIBRaLS` / `Roma-BZCAT` / `ATNF Pulsar`: **$0$ in 95% ellipse** (`FIRST`, `XMM`, `Chandra CSC`: `UNUSABLE`).
    - *(Physical note: `4FGL J1539.4-3323`'s curved `LogParabola` spectrum at $39.63\sigma$ and complete radio-loud blazar null make it a prime radio-faint millisecond pulsar candidate requiring deep MeerKAT/Parkes timing at $S_{1.4\text{ GHz}} < 0.1\text{ mJy}$.)*
