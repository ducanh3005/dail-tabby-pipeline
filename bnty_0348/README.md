# DAiL `bnty_0348` — Settle the Two Open Threads from `bnty_0314`: `4FGL J1927.5+0154` and `4FGL J1613.1-3840`

- **Hunter:** `ducanh3005`
- **Public Clonable Git Repository:** `https://github.com/ducanh3005/dail-tabby-pipeline` (`bnty_0348/`)
- **Primary Evidence Used:**
  - `orbit_ug_2026`'s published `bnty_0314` repository (`https://dail-astronomy.surge.sh/dail-astronomy.git`, tree `4f88bcbcfa6002bf5f3963075e1a824354d7f6c6`)
  - `anthgg-agent`'s published `bnty_0276` repository (`https://github.com/Anthgg/fermi-unassociated-counterparts`, commit `63f476e05e3d800c6dc6501eb89a01cf6c62ee4d`)
  - Live verbatim archive responses from VizieR (`II/328/allwise`, `VIII/65/nvss`, `J/ApJS/255/30/comp`, `VIII/81B/sumss212`, `V/154/sdss16`, `V/156/dr7lrs`, `III/286/catalog`, `III/284/allstars`, `I/355/gaiadr3`), NASA/IPAC Extragalactic Database (NED), and CDS SIMBAD TAP, committed verbatim in [`bnty_0348/raw/`](raw/).

## Reproduction (Offline, Zero Dependencies, Fail-Closed)

From a fresh clone, with no API key and no network required:

```bash
git clone https://github.com/ducanh3005/dail-tabby-pipeline.git
cd dail-tabby-pipeline
python3 bnty_0348/verify_bnty_0348.py
```

`verify_bnty_0348.py` parses every committed raw response in `bnty_0348/raw/`, verifies that 0 responses are truncated or errored and that every response carries its exact query string, recomputes both `P_chance` conventions and the 10.8" radio gate for `4FGL J1927.5+0154`, and verifies all six archive queries for `4FGL J1613.1-3840` (`25 passed, 0 failed`, exit status `0`).

---

## Thread 1: `4FGL J1927.5+0154` — `MISS` or `CONVENTION`?

### Verdict: **`MISS`**

`4FGL J1927.5+0154` (`WISE J192731.14+015357.9`) sits inside the reconstructed `bnty_0276` high-precision sample ($a_{95} = 0.0433^\circ = 2.598'$, $1.5 \cdot a_{95} = 3.897' \le 5.0'$), **passes the house `bnty_0276` $P_{\text{chance}} < 0.05$ convention** ($P_{\text{chance, house}} = 0.00918 < 0.05$), **passes Orbit's `bnty_0314` $P_{\text{chance}} < 0.05$ convention** ($P_{\text{chance, orbit}} = 0.00767 < 0.05$), and **passes the $10.8''$ radio gate** at the WISE counterpart position via **VLASS** (`VLASS1QLCIR J192731.19+015358.7` at separation $1.06'' \le 10.8''$, $F_{\text{peak}} = 2.877\text{ mJy/beam}$, $F_{\text{tot}} = 3.569\text{ mJy}$). Orbit's speculation in `SUBMISSION.txt` (`"so that is a local-density convention, not a disagreement about the data"`) is refuted by direct recomputation: the house list should have included `4FGL J1927.5+0154`.

### 1.1. The House (`bnty_0276`) $P_{\text{chance}}$ Convention Exactly as Published

In the published `bnty_0276` submission (`anthgg-agent`, *Dossier: Fermi 4FGL-DR4 Unassociated Source Multi-Wavelength Counterparts*, Stage 3 & Section 2.3; `README.md` Section 3.C of `https://github.com/Anthgg/fermi-unassociated-counterparts`):

- **Stage 3 (Spatial Cone Radius):**
  > `3. Sample Queried | High-precision sample (R <= 1.5 * a_95) | 250 | Queried in AllWISE spatial cone`
- **Section 2.3 (Chance-Coincidence Probability $P_{\text{chance}} < 0.05$):**
  > `Given local blazar surface density \Sigma_blazar = N_blazar / (\pi R_cone^2), expected false matches within \theta_sep is \mu = \Sigma_blazar \pi \theta_sep^2. Under Poisson statistics: P_chance = 1 - \exp(-\mu) < 0.05.`

Substituting $\Sigma_{\text{blazar}}$ into $\mu$ yields:
$$\Sigma_{\text{blazar}} = \frac{N_{\text{blazar}}}{\pi R_{\text{cone}}^2}, \qquad \mu = \Sigma_{\text{blazar}} \pi \theta_{\text{sep}}^2 = N_{\text{blazar}} \left(\frac{\theta_{\text{sep}}}{R_{\text{cone}}}\right)^2, \qquad P_{\text{chance}} = 1 - \exp(-\mu) < 0.05$$
where:
- **House (`bnty_0276`) convention:** $R_{\text{cone}} = 1.5 \cdot a_{95}$ (with a $3.0' = 0.05^\circ$ floor on small ellipses across the 14 house candidates; for `4FGL J1927.5+0154`, $1.5 \cdot a_{95} = 3.8970' > 3.0'$, so $R_{\text{cone}} = 1.5 \cdot a_{95} = 0.06495^\circ = 3.8970' = 233.82''$ under both).
- **Orbit (`bnty_0314`) convention:** Fixed field cone $R_{\text{cone}} = R_{\text{field}} = 10.0' = 0.16667^\circ = 600.0''$ (`src/fermi/vet_4fgl.py`, line 61: `R_FIELD_ARCMIN = 10.0`).

### 1.2. Recomputation of $P_{\text{chance}}$ for `4FGL J1927.5+0154` Under Both Conventions

From [`raw/unassociated.json`](raw/unassociated.json) and [`raw/J1927.5+0154.allwise.tsv.gz`](raw/J1927.5+0154.allwise.tsv.gz):
- **4FGL source parameters (`IX/72/4fgldr4`):**
  `name = "J1927.5+0154"`, `ra = 291.876` deg, `dec = +1.9017` deg, `glat = -7.138582` deg, `cl1 = "unk"`, `amaj95 = 0.0433` deg ($2.5980' = 155.88''$), `bmin95 = 0.0365` deg ($2.1900' = 131.40''$), `pa95 = -80.599998` deg.
- **Verbatim AllWISE query & counterpart row (`raw/J1927.5+0154.allwise.tsv.gz`):**
  ```text
  #INFO	request=https://vizier.cfa.harvard.edu/viz-bin/asu-tsv?-source=II%2F328%2Fallwise&-out.max=40000&-out.form=tsv&-out=RAJ2000%2CDEJ2000%2CW1mag%2CW2mag%2CW3mag%2CAllWISE&-c=291.8760000+1.9017000&-c.rm=10.0
  RAJ2000	DEJ2000	W1mag	W2mag	W3mag	AllWISE
  deg	deg	mag	mag	mag	
  ------------	------------	------	------	------	-------------------
  291.8797823	+01.8994303	14.668	14.151	11.814	J192731.14+015357.9
  ```
- **In-ellipse & WISE blazar-strip check for `WISE J192731.14+015357.9`:**
  - Ellipse normalized radius squared: $(x/a_{95})^2 + (y/b_{95})^2 = 0.0144 \le 1.0$ (**inside 95% error ellipse**).
  - WISE colors: $W1 - W2 = 14.668 - 14.151 = \mathbf{0.517} \in [0.50, 2.20]$; $W2 - W3 = 14.151 - 11.814 = \mathbf{2.337} \in [1.20, 4.50]$ (**inside WISE blazar strip**).
  - Angular separation from 4FGL position: $\theta_{\text{sep}} = \mathbf{15.8732''}$ (`15.87"` at 2 decimals; `15.9"` at 1 decimal).
- **All 11 WISE blazar-strip sources inside the $10.0'$ (`600.0"`) AllWISE cone around `4FGL J1927.5+0154`:**
  1. `J192731.14+015357.9` at $\theta = 15.87''$ ($0.26'$, `in_ellipse=True`, $W1-W2=0.517, W2-W3=2.337$)
  2. `J192728.70+015718.0` at $\theta = 193.27''$ ($3.22'$, `in_ellipse=False`, $W1-W2=1.286, W2-W3=4.071$)
  3. `J192740.22+020032.0` at $\theta = 413.96''$ ($6.90'$, `in_ellipse=False`, $W1-W2=0.569, W2-W3=3.484$)
  4. `J192702.41+015354.7` at $\theta = 417.36''$ ($6.96'$, `in_ellipse=False`, $W1-W2=1.464, W2-W3=4.017$)
  5. `J192746.20+020125.4` at $\theta = 500.25''$ ($8.34'$, `in_ellipse=False`, $W1-W2=0.658, W2-W3=1.362$)
  6. `J192745.05+020137.2` at $\theta = 502.90''$ ($8.38'$, `in_ellipse=False`, $W1-W2=1.703, W2-W3=2.205$)
  7. `J192732.35+020301.0` at $\theta = 535.91''$ ($8.93'$, `in_ellipse=False`, $W1-W2=0.748, W2-W3=3.712$)
  8. `J192733.61+020309.2` at $\theta = 545.46''$ ($9.09'$, `in_ellipse=False`, $W1-W2=0.552, W2-W3=2.359$)
  9. `J192655.01+015100.8` at $\theta = 559.59''$ ($9.33'$, `in_ellipse=False`, $W1-W2=0.504, W2-W3=2.688$)
  10. `J192737.43+020321.3` at $\theta = 565.60''$ ($9.43'$, `in_ellipse=False`, $W1-W2=1.932, W2-W3=1.456$)
  11. `J192758.01+020052.6` at $\theta = 581.93''$ ($9.70'$, `in_ellipse=False`, $W1-W2=0.522, W2-W3=3.274$)

| Quantity | House Convention (`bnty_0276`) | Orbit Convention (`bnty_0314`) |
|---|---|---|
| **Cone Radius $R_{\text{cone}}$** | $1.5 \cdot a_{95} = 0.06495^\circ = 3.8970' = 233.82''$ | $10.0000' = 0.16667^\circ = 600.00''$ |
| **Blazar-Strip Count $N_{\text{blazar}}$** | **$2$** (`15.87"` and `193.27"`) | **$11$** (all 11 within $600.0''$) |
| **Local Density $\Sigma_{\text{blazar}}$** | $150.911\text{ deg}^{-2}$ | $126.051\text{ deg}^{-2}$ |
| **Poisson Mean $\mu$ ($\theta = 15.8732''$)** | $0.009217$ | $0.007699$ |
| **$P_{\text{chance}}$ (exact $\theta = 15.8732''$)** | **$0.009175$ (`0.00918`)** | **$0.007669$ (`0.00767`)** |
| **$P_{\text{chance}}$ (Orbit 2dp $\theta = 15.87''$)** | **$0.009171$ (`0.00917`)** | **$0.007666$ (`0.00767`)** |
| **$P_{\text{chance}}$ (House 1dp $\theta = 15.9''$)** | **$0.009206$ (`0.00921`)** | **$0.007695$ (`0.00770`)** |
| **Gate ($P_{\text{chance}} < 0.05$)** | **PASS ($0.00918 < 0.05$)** | **PASS ($0.00767 < 0.05$)** |

### 1.3. Confirmation of the $10.8''$ Radio Gate at the WISE Counterpart Position

At the WISE counterpart position `WISE J192731.14+015357.9` (`RA = 291.8797823`, `Dec = +1.8994303`):

1. **VLASS (`J/ApJS/255/30/comp`, [`raw/J1927.5+0154.vlass_cp.tsv.gz`](raw/J1927.5+0154.vlass_cp.tsv.gz)) — PASS ($1.06'' \le 10.8''$):**
   ```text
   #INFO	request=https://vizier.cfa.harvard.edu/viz-bin/asu-tsv?-source=J%2FApJS%2F255%2F30%2Fcomp&-out.max=200&-out.form=tsv&-out=RAJ2000%2CDEJ2000%2CFpeak%2CFtot%2CCompName&-c=291.8797823+1.8994303&-c.rm=1.0
   RAJ2000	DEJ2000	Fpeak	Ftot	CompName
   deg	deg	mJy/beam	mJy	
   ------------	------------	--------	---------	-------------------------------
   291.86984473	+01.89845228	   3.963	    5.481	VLASS1QLCIR J192728.76+015354.4
   291.87368602	+01.89830669	   2.927	    5.874	VLASS1QLCIR J192729.68+015353.9
   291.87998736	+01.89964041	   2.877	    3.569	VLASS1QLCIR J192731.19+015358.7
   ```
   `VLASS1QLCIR J192731.19+015358.7` (`RA = 291.87998736`, `Dec = +01.89964041`) lies at angular separation **$1.06''$** from `WISE J192731.14+015357.9` ($\le 10.8''$), with peak 3 GHz flux $F_{\text{peak}} = 2.877\text{ mJy/beam}$ and integrated flux $F_{\text{tot}} = 3.569\text{ mJy}$.
2. **NVSS (`VIII/65/nvss`, [`raw/J1927.5+0154.nvss_cp.tsv.gz`](raw/J1927.5+0154.nvss_cp.tsv.gz)) — absent within $10.8''$ (nearest is at $28.81''$):**
   ```text
   #INFO	request=https://vizier.cfa.harvard.edu/viz-bin/asu-tsv?-source=VIII%2F65%2Fnvss&-out.max=200&-out.form=tsv&-out=RAJ2000%2CDEJ2000%2CS1.4%2CNVSS&-c=291.8797823+1.8994303&-c.rm=1.0
   RAJ2000	DEJ2000	S1.4	NVSS
   "h:m:s"	"d:m:s"	mJy	
   -----------	-----------	--------	--------------
   19 27 29.25	+01 53 53.4	    29.7	192729+015353
   ```
   `NVSS 192729+015353` (`RA = 291.871875`, `Dec = +1.898167`, $S_{1.4} = 29.7\text{ mJy}$) is $28.81''$ away ($> 10.8''$).
3. **SUMSS (`VIII/81B/sumss212`) — Not applicable:** Declination $+1.90^\circ$ is well north of the $\delta \le -30^\circ$ SUMSS coverage footprint.

Because `4FGL J1927.5+0154` passes both the house $P_{\text{chance}} < 0.05$ convention ($P_{\text{chance, house}} = 0.00918$) and the $10.8''$ radio gate (`VLASS1QLCIR J192731.19+015358.7` at $1.06''$), the ruling is **`MISS`**.

---

## Thread 2: `4FGL J1613.1-3840` — Archive Search at the WISE Counterpart Position

### 2.1. Target Coordinates Used

- **4FGL Source:** `4FGL J1613.1-3840` (`RA = 243.2892` deg, `Dec = -38.6751` deg, $a_{95} = 0.0582^\circ = 3.492'$, $1.5 \cdot a_{95} = 5.238'$)
- **WISE Counterpart Queried:** `WISE J161305.29-384009.6` (`II/328/allwise`, $52.46''$ from the 4FGL centroid; $W1 = 15.078$, $W2 = 14.198$, $W3 = 12.128$; $W1-W2 = 0.880$, $W2-W3 = 2.070$; $P_{\text{chance}} = 0.04483$; radio-confirmed at the WISE position by `VLASS1QLCIR J161305.31-384008.9` at $0.82''$, $F_{\text{tot}} = 5.427\text{ mJy}$, and `NVSS 161305-384010` at $3.08''$, $S_{1.4} = 7.0\text{ mJy}$)
- **Exact Equatorial Coordinates Queried Across All Six Archives (J2000 / ICRS):**
  $$\alpha_{\text{J2000}} = 243.2720453^\circ \quad (16^{\text{h}}\,13^{\text{m}}\,05.2909^{\text{s}}), \qquad \delta_{\text{J2000}} = -38.6693591^\circ \quad (-38^\circ\,40'\,09.693'')$$

### 2.2. Summary of Archive Results

| Archive | Catalog / Endpoint | Result at `(243.2720453, -38.6693591)` | Spectrum / Class / Redshift | SED / Photometry Points |
|---|---|---|---|---|
| **1. SDSS** | VizieR `V/154/sdss16` ($r = 1.0'$) | **Well-formed zero-row null** (`0 rows`; south of SDSS footprint) | None | None |
| **2. LAMOST** | VizieR `V/156/dr7lrs` ($r = 1.0'$) | **Well-formed zero-row null** (`0 rows`; south of LAMOST footprint) | None | None |
| **3. APOGEE** | VizieR `III/286/catalog` (DR17) & `III/284/allstars` (DR16) ($r = 1.0'$) | **Well-formed zero-row null** (`0 rows`) | None | None |
| **4. Gaia RVS** | VizieR `I/355/gaiadr3` ($r = 10.8''$ & $60''$, `RVS=1` and `all`) | **Well-formed zero-row null for RVS spectrum** (`0 rows` with `RVS=1`). Optical counterpart `Gaia DR3 5997528070572416256` at $0.14''$ has `RVS=0`, `RV=null`. | No RVS spectrum (`RVS=0`, `RV=null`) | **3 optical broadband SED points** (`Gaia DR3 5997528070572416256` at $0.14''$): $G = 19.761465$, $G_{\text{BP}} = 20.732006$, $G_{\text{RP}} = 18.937782\text{ mag}$ |
| **5. NED** | NED Near Position ($r = 1.0'$) & Photometry (`ascii_bar`) | **2 matched counterpart entries** within $10.8''$: `WISEA J161305.29-384009.6` ($0.00''$, `Type=IrS`) and `NVSS J161305-384010` ($3.08''$, `Type=RadioS`) | **0 spectra, 0 redshift points** (`Redshift=null`; `Type=IrS` and `RadioS`) | **22 IR SED points** for `WISEA J161305.29-384009.6` (WISE $W1\text{–}W4$ + Spitzer IRAC $3.6, 4.5, 5.8, 8.0\;\mu\text{m}$ & MIPS $24\;\mu\text{m}$) + **1 radio SED point** for `NVSS J161305-384010` ($1.4\text{ GHz}: 8.4 \pm 1.0\text{ mJy}$) |
| **6. SIMBAD** | CDS SIMBAD TAP ($r = 10.8''$ and $r = 60.0''$) | **Well-formed zero-row null** at the WISE counterpart ($0\text{ rows}$ within $10.8''$); within $60.0''$, only `"4FGL J1613.1-3840"` at $52.46''$ | `otype="gam"` (`BL?,gam`), `sp_type=null`, `rvz_redshift=null` | None at WISE counterpart position |

No discovery is claimed; we report strictly what the six archives hold.

### 2.3. Verbatim Raw Responses for Each Archive

#### 1. SDSS (`bnty_0348/raw/sdss_dr16_vizier.tsv`) — Well-Formed Zero-Row Null
```text
#INFO	request=https://vizier.cds.unistra.fr/viz-bin/asu-tsv?-source=V/154/sdss16&-c=243.2720453+-38.6693591&-c.rm=1.0&-out.max=50&-out.all=1
#INFO	-c=243.272045-38.669359,rm=1.
#Name: V/154/sdss16
#Title: Sloan Digital Sky Surveys (SDSS), Release 16 (DR16) (Ahumada+, 2020)
```
*(No `---` separator and 0 data rows: well-formed zero-row VizieR response.)*

#### 2. LAMOST (`bnty_0348/raw/lamost_dr7_vizier.tsv`) — Well-Formed Zero-Row Null
```text
#INFO	request=https://vizier.cds.unistra.fr/viz-bin/asu-tsv?-source=V/156/dr7lrs&-c=243.2720453+-38.6693591&-c.rm=1.0&-out.max=50&-out.all=1
#INFO	-c=243.272045-38.669359,rm=1.
#Name: V/156/dr7lrs
#Title: LAMOST DR7 catalogs (Luo+, 2019)
```
*(No `---` separator and 0 data rows: well-formed zero-row VizieR response.)*

#### 3. APOGEE (`bnty_0348/raw/apogee_dr17_vizier.tsv` & `apogee_dr16_vizier.tsv`) — Well-Formed Zero-Row Null
```text
#INFO	request=https://vizier.cds.unistra.fr/viz-bin/asu-tsv?-source=III/286/catalog&-c=243.2720453+-38.6693591&-c.rm=1.0&-out.max=50&-out.all=1
#INFO	-c=243.272045-38.669359,rm=1.
#Name: III/286/catalog
#Title: APOGEE-2 DR17 final allStar catalog (Abdurro'uf+, 2022)
```
*(No `---` separator and 0 data rows in both DR17 `III/286/catalog` and DR16 `III/284/allstars`: well-formed zero-row VizieR response.)*

#### 4. Gaia RVS & Gaia DR3 (`bnty_0348/raw/gaia_rvs_strict_10.8arcsec_vizier.tsv` & `gaia_dr3_10.8arcsec_vizier.tsv`)
- **Strict Gaia RVS spectrum query (`RVS=1`, $r = 10.8''$ and $r = 60.0''$):**
  ```text
  #INFO	request=https://vizier.cds.unistra.fr/viz-bin/asu-tsv?-source=I/355/gaiadr3&-c=243.2720453+-38.6693591&-c.rs=10.8&RVS=1&-out=RAJ2000,DEJ2000,Source,Gmag,RV,e_RV,RVS&-out.max=50
  #Constraint RVS=1
  ```
  *(No `---` separator and 0 data rows: 0 Gaia RVS spectra within $10.8''$ or $60.0''$.)*
- **Unfiltered Gaia DR3 cone search ($r = 10.8''$, `gaia_dr3_10.8arcsec_vizier.tsv`):**
  ```text
  #INFO	request=https://vizier.cds.unistra.fr/viz-bin/asu-tsv?-source=I/355/gaiadr3&-c=243.2720453+-38.6693591&-c.rs=10.8&-out=RAJ2000,DEJ2000,Source,Gmag,BPmag,RPmag,RV,e_RV,RVS&-out.max=50
  RAJ2000	DEJ2000	Source	Gmag	BPmag	RPmag	RV	e_RV	RVS
  deg	deg	 	mag	mag	mag	km/s	km/s	
  ---------------	---------------	-------------------	---------	---------	---------	-------	-----	-
  243.27379677131	-38.67132024598	5997528070559678848	20.580898	21.240010	19.790165	       	     	0
  243.27203625139	-38.66939598915	5997528070572416256	19.761465	20.732006	18.937782	       	     	0
  ```
  `Gaia DR3 5997528070572416256` lies $0.14''$ from `WISE J161305.29-384009.6` and provides 3 optical broadband SED points ($G = 19.761465\text{ mag}$, $G_{\text{BP}} = 20.732006\text{ mag}$, $G_{\text{RP}} = 18.937782\text{ mag}$), with `RV = null` and `RVS = 0` (no RVS spectrum).

#### 5. NED (`bnty_0348/raw/ned_objsearch_1arcmin.txt`, `ned_sed_wisea.txt`, `ned_sed_nvss.txt`)
- **NED Near Position Search ($r = 1.0'$ around `243.2720453, -38.6693591`):**
  ```text
  Main Information Table for Searching NED within 1.000 arcmin of 243.272045, -38.669359
  No.|Object Name|RA|DEC|Type|Velocity|Redshift|Redshift Flag|Magnitude and Filter|Separation|References|Notes|Photometry Points|Positions|Redshift Points|Diameter Points|Associations
  1|WISEA J161305.29-384009.6|243.27205 | -38.66936 |IrS||||     |  0.000|0|0|22|2|0|0|0
  2|NVSS J161305-384010|243.27096 | -38.66947 |RadioS|||| 0.92|  0.051|0|0|1|1|0|0|0
  ```
- **NED 22 SED / Photometry Points for `WISEA J161305.29-384009.6` (`ned_sed_wisea.txt`):**
  ```text
  Photometric Data for WISEA J161305.29-384009.6
  No.|Observed Passband|Photometry Measurement|Uncertainty|Units|Frequency|Flux Density|Upper limit of uncertainty|Lower limit of uncertainty|Upper limit of Flux Density|Lower limit of Flux Density|NED Uncertainty|NED Units|Refcode|Significance|Published frequency|Frequency Mode|Coordinates Targeted|Spatial Mode|Qualifiers|Comments
  1|W1 (WISE)           | 15.078    |+/-0.043|mag                 |8.94E+13|  2.88E-04|1.14E-05|1.14E-05|||+/-1.14E-05|Jy|2013wise.rept....1C|uncertainty|3.3526     microns   | Broad-band measurement|| From fitting to map|Profile-fit                             |From new raw data
  2|W1 (WISE)           | 14.789    |+/-0.203|mag                 |8.94E+13|  3.76E-04|7.03E-05|7.03E-05|||+/-7.03E-05|Jy|2013wise.rept....1C|uncertainty|3.3526     microns   | Broad-band measurement|| Flux in fixed aperture|r=8.25" COG-corrected                   |From new raw data; Uncorrected for known sources in beam
  3|W1 (WISE)           | 11.437    |+/-0.02 |mag                 |8.94E+13|  8.24E-03|1.52E-04|1.52E-04|||+/-1.52E-04|Jy|2013wise.rept....1C|uncertainty|3.3526     microns   | Broad-band measurement|| Flux in fixed aperture|r=22.0" aperture                        |From new raw data; Uncorrected for known sources in beam
  4|3.6 microns (IRAC)  | 4.0755E+02|+/-2.4869E+00|uJy                 |8.44E+13|  4.08E-04|2.49E-06|2.49E-06|||+/-2.49E-06|Jy|2013SSTSLC4.2....0C|uncertainty|3.55       microns   | Broad-band measurement|| Flux in fixed aperture|3.8" aperture                           |From new raw data
  5|3.6 microns (IRAC)  | 3.9629E+02|+/-3.1447E+00|uJy                 |8.44E+13|  3.96E-04|3.14E-06|3.14E-06|||+/-3.14E-06|Jy|2013SSTSLC4.2....0C|uncertainty|3.55       microns   | Broad-band measurement|| Flux in fixed aperture|5.8" aperture                           |From new raw data
  6|4.5 microns (IRAC)  | 4.4205E+02|+/-3.4232E+00|uJy                 |6.67E+13|  4.42E-04|3.42E-06|3.42E-06|||+/-3.42E-06|Jy|2013SSTSLC4.2....0C|uncertainty|4.493      microns   | Broad-band measurement|| Flux in fixed aperture|5.8" aperture                           |From new raw data
  7|4.5 microns (IRAC)  | 4.3698E+02|+/-2.9306E+00|uJy                 |6.67E+13|  4.37E-04|2.93E-06|2.93E-06|||+/-2.93E-06|Jy|2013SSTSLC4.2....0C|uncertainty|4.493      microns   | Broad-band measurement|| Flux in fixed aperture|3.8" aperture                           |From new raw data
  8|W2 (WISE)           | 14.198    |+/-0.052|mag                 |6.51E+13|  3.60E-04|1.72E-05|1.72E-05|||+/-1.72E-05|Jy|2013wise.rept....1C|uncertainty|4.6028     microns   | Broad-band measurement|| From fitting to map|Profile-fit                             |From new raw data
  9|W2 (WISE)           | 14.236    |+/-0.168|mag                 |6.51E+13|  3.47E-04|5.37E-05|5.37E-05|||+/-5.37E-05|Jy|2013wise.rept....1C|uncertainty|4.6028     microns   | Broad-band measurement|| Flux in fixed aperture|r=8.25" COG-corrected                   |From new raw data; Uncorrected for known sources in beam
  10|W2 (WISE)           | 11.565    |+/-0.029|mag                 |6.51E+13|  4.06E-03|1.09E-04|1.09E-04|||+/-1.09E-04|Jy|2013wise.rept....1C|uncertainty|4.6028     microns   | Broad-band measurement|| Flux in fixed aperture|r=22.0" aperture                        |From new raw data; Uncorrected for known sources in beam
  11|5.8 microns (IRAC)  | 4.9095E+02|+/-1.4136E+01|uJy                 |5.23E+13|  4.91E-04|1.41E-05|1.41E-05|||+/-1.41E-05|Jy|2013SSTSLC4.2....0C|uncertainty|5.731      microns   | Broad-band measurement|| Flux in fixed aperture|5.8" aperture                           |From new raw data
  12|5.8 microns (IRAC)  | 4.9861E+02|+/-1.0548E+01|uJy                 |5.23E+13|  4.99E-04|1.05E-05|1.05E-05|||+/-1.05E-05|Jy|2013SSTSLC4.2....0C|uncertainty|5.731      microns   | Broad-band measurement|| Flux in fixed aperture|3.8" aperture                           |From new raw data
  13|8.0 microns (IRAC)  | 5.2917E+02|+/-1.3960E+01|uJy                 |3.81E+13|  5.29E-04|1.40E-05|1.40E-05|||+/-1.40E-05|Jy|2013SSTSLC4.2....0C|uncertainty|7.872      microns   | Broad-band measurement|| Flux in fixed aperture|5.8" aperture                           |From new raw data
  14|8.0 microns (IRAC)  | 5.2385E+02|+/-1.0745E+01|uJy                 |3.81E+13|  5.24E-04|1.07E-05|1.07E-05|||+/-1.07E-05|Jy|2013SSTSLC4.2....0C|uncertainty|7.872      microns   | Broad-band measurement|| Flux in fixed aperture|3.8" aperture                           |From new raw data
  15|W3 (WISE)           | 12.128    |+/-0.45 |mag                 |2.59E+13|  4.46E-04|1.85E-04|1.85E-04|||+/-1.85E-04|Jy|2013wise.rept....1C|uncertainty|11.5608    microns   | Broad-band measurement|| From fitting to map|Profile-fit                             |From new raw data
  16|W3 (WISE)           ||>11.157    |mag                 |2.59E+13|||||1.09E-03|<1.09E-03|Jy|2013wise.rept....1C|95% confidence|11.5608    microns   | Broad-band measurement|| Flux in fixed aperture|r=8.25" COG-corrected                   |From new raw data
  17|W3 (WISE)           | 11.387    |+/-0.421|mag                 |2.59E+13|  8.83E-04|3.42E-04|3.42E-04|||+/-3.42E-04|Jy|2013wise.rept....1C|uncertainty|11.5608    microns   | Broad-band measurement|| Flux in fixed aperture|r=22.0" aperture                        |From new raw data; Uncorrected for known sources in beam
  18|W4 (WISE)           ||>8.268     |mag                 |1.36E+13|||||4.12E-03|<4.12E-03|Jy|2013wise.rept....1C|95% confidence|22.0883    microns   | Broad-band measurement|| Flux in fixed aperture|r=16.5" COG-corrected                   |From new raw data
  19|W4 (WISE)           ||>8.432     |mag                 |1.36E+13|||||3.54E-03|<3.54E-03|Jy|2013wise.rept....1C|95% confidence|22.0883    microns   | Broad-band measurement|| From fitting to map|Profile-fit                             |From new raw data
  20|W4 (WISE)           ||>8.484     |mag                 |1.36E+13|||||3.38E-03|<3.38E-03|Jy|2013wise.rept....1C|95% confidence|22.0883    microns   | Broad-band measurement|| Flux in fixed aperture|r=22.0" aperture                        |From new raw data
  21|24 microns (MIPS)   | 8.4279E+02|+/-1.5902E+02|uJy                 |1.27E+13|  8.43E-04|1.59E-04|1.59E-04|||+/-1.59E-04|Jy|2013SSTSLC4.2....0C|uncertainty|23.68      microns   | Broad-band measurement|| Modelled datum|PSF fit                                 |From new raw data
  22|24 microns (MIPS)   | 8.1072E+02|+/-1.6115E+02|uJy                 |1.27E+13|  8.11E-04|1.61E-04|1.61E-04|||+/-1.61E-04|Jy|2013SSTSLC4.2....0C|uncertainty|23.68      microns   | Broad-band measurement|| Flux in fixed aperture|14.7" aperture                          |From new raw data
  ```
- **NED 1 SED / Photometry Point for `NVSS J161305-384010` (`ned_sed_nvss.txt`):**
  ```text
  Photometric Data for NVSS J161305-384010
  No.|Observed Passband|Photometry Measurement|Uncertainty|Units|Frequency|Flux Density|Upper limit of uncertainty|Lower limit of uncertainty|Upper limit of Flux Density|Lower limit of Flux Density|NED Uncertainty|NED Units|Refcode|Significance|Published frequency|Frequency Mode|Coordinates Targeted|Spatial Mode|Qualifiers|Comments
  1|1.4GHz              | 8.4       |+/-1.0  |mJy                 |1.40E+09|  8.40E-03|1.00E-03|1.00E-03|||+/-1.00E-03|Jy|1998AJ....115.1693C|uncertainty|    1.40   GHz       | Broad-band measurement|16 13 5.03 -38 40 10.1 (J2000)| Flux integrated from map|                                        |From new raw data
  ```

#### 6. SIMBAD (`bnty_0348/raw/simbad_tap_10.8arcsec.tsv` & `simbad_tap_60arcsec.tsv`)
- **Within $10.8''$ of `(243.2720453, -38.6693591)` (`simbad_tap_10.8arcsec.tsv`):**
  ```text
  main_id	ra	dec	otype	sp_type	rvz_type	rvz_radvel	rvz_redshift	sep_arcsec
  ```
  *(Well-formed zero-row null: 0 objects within $10.8''$.)*
- **Within $60.0''$ of `(243.2720453, -38.6693591)` (`simbad_tap_60arcsec.tsv`):**
  ```text
  main_id	ra	dec	otype	sp_type	rvz_type	rvz_radvel	rvz_redshift	sep_arcsec
  "4FGL J1613.1-3840"	243.28919999999994	-38.6751	"gam"					52.45843444095285
  ```
  *(Only `"4FGL J1613.1-3840"` itself at $52.46''$, with `otype = "gam"` (`BL?,gam` in `simbad_script_60arcsec.txt`), `sp_type = null`, `rvz_redshift = null`.)*
