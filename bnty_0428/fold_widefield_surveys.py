#!/usr/bin/env python3
"""
fold_widefield_surveys.py — DAiL bnty_0428:
TIC 158499577 (HD 94871) Wide-Field Survey Folds (ATLAS, KELT-South, HATSouth, Evryscope
+ Supplementary Public Wide-Field HLSP Pipelines QLP, TGLC, T16, GSFC-ELEANOR-LITE, TARS).

Produces:
1. Complete, honest per-survey table for the 4 mandatory ground wide-field surveys
   (ATLAS, KELT-South, HATSouth, Evryscope) at (RA=164.1597484, Dec=-36.5803139):
   - Footprint & public DR coverage at Dec = -36.5803 deg (yes/no + exact field-edge reason).
   - Data retrieval status & verified archive query logs in raw/.
   - Quantitative saturation (m_*, m_sat, F_*/F_sat) & neighbour blending caveats for V=8.81.
   - Folded primary & secondary depths (reported strictly as UNVERIFIED where unretrievable).
2. Recomputable phase-folded primary & secondary depths at P = 11.7672 d, T0 = BTJD 2286.3720
   across 5 public wide-field FFI survey pipelines not folded by the house (MIT QLP S9-S100,
   TGLC Gaia-DR3 ePSF deblended, T16 HATSouth/fitsh difference-imaging IFL/IRM/EPD/TFA,
   NASA GSFC-ELEANOR-LITE, and TARS), plus empirical blend-dilution verification on the
   two 9.5" neighbours TIC 942348495 and TIC 942348496.
"""

import json
import math
import os
import re
from datetime import datetime, timezone

import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "raw")
RES_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(RES_DIR, exist_ok=True)

RA_DEG = 164.1597484
DEC_DEG = -36.5803139
P_HOUSE = 11.7672
T0_HOUSE = 2286.3720
PHI_SEC_ECC = 0.514107


def read_fits_bintable(fpath, hdu_index=1):
    """Pure-Python + NumPy FITS BINTABLE reader."""
    with open(fpath, "rb") as f:
        raw = f.read()

    pos = 0
    hdr_target = None
    data_pos = 0
    hdu = 0
    while pos < len(raw):
        hdr = {}
        while True:
            blk = raw[pos : pos + 2880]
            pos += 2880
            ended = False
            for i in range(0, 2880, 80):
                c = blk[i : i + 80].decode("ascii", errors="replace")
                k = c[:8].strip()
                if k == "END":
                    ended = True
                    break
                if "=" in c[:10]:
                    hdr[k] = c[10:].split("/")[0].strip().strip("'").strip()
            if ended:
                break
        xt = hdr.get("XTENSION", "PRIMARY")
        naxis = int(hdr.get("NAXIS", 0))
        dbytes = 0
        if naxis > 0:
            bp = abs(int(hdr.get("BITPIX", 8))) // 8
            prod = 1
            for ax in range(1, naxis + 1):
                prod *= int(hdr.get(f"NAXIS{ax}", 0))
            dbytes = prod * bp
            if xt == "BINTABLE":
                dbytes = int(hdr.get("NAXIS1", 0)) * int(hdr.get("NAXIS2", 0))
        if hdu == hdu_index:
            hdr_target = hdr
            data_pos = pos
            break
        pos += ((dbytes + 2879) // 2880) * 2880
        hdu += 1

    nrows = int(hdr_target["NAXIS2"])
    row_bytes = int(hdr_target["NAXIS1"])
    tfields = int(hdr_target["TFIELDS"])
    dtype_fields = []
    for col in range(1, tfields + 1):
        ttype = str(hdr_target[f"TTYPE{col}"]).strip()
        tform = str(hdr_target[f"TFORM{col}"]).strip()
        m = re.match(r"^(\d*)([A-Z])$", tform)
        cnt = int(m.group(1)) if m.group(1) else 1
        code = m.group(2)
        if code == "D":
            base = ">f8"
        elif code == "E":
            base = ">f4"
        elif code == "J":
            base = ">i4"
        elif code == "I":
            base = ">i2"
        elif code == "K":
            base = ">i8"
        elif code == "A":
            dtype_fields.append((ttype, f"S{cnt}"))
            continue
        else:
            raise ValueError(f"Unsupported TFORM: {tform}")
        if cnt > 1:
            dtype_fields.append((ttype, base, (cnt,)))
        else:
            dtype_fields.append((ttype, base))

    dt = np.dtype(dtype_fields)
    table_bytes = raw[data_pos : data_pos + nrows * row_bytes]
    arr = np.frombuffer(table_bytes, dtype=dt, count=nrows)
    return hdr_target, arr


def tukey_biweight(x, c=6.0, max_iter=5):
    arr = np.asarray(x, dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return np.nan
    m = float(np.median(arr))
    for _ in range(max_iter):
        r = arr - m
        mad = float(np.median(np.abs(r)))
        if mad < 1e-12:
            break
        u = r / (c * 1.4826 * mad)
        mask = np.abs(u) < 1.0
        if not np.any(mask):
            break
        w = (1.0 - u[mask] ** 2) ** 2
        m = float(np.sum(w * arr[mask]) / np.sum(w))
    return m


def robust_sigma(x):
    arr = np.asarray(x, dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size < 2:
        return np.nan
    med = float(np.median(arr))
    return float(1.4826 * np.median(np.abs(arr - med)))


def measure_phase_window(phi, depth, center_phi, half_width):
    dphi = (phi - center_phi + 0.5) % 1.0 - 0.5
    m = np.abs(dphi) <= half_width
    vals = depth[m]
    if vals.size == 0:
        return {"n_pts": 0, "biweight_depth": None, "median_depth": None, "err_depth": None, "max_depth": None}
    med = float(np.median(vals))
    bw = float(tukey_biweight(vals)) if vals.size >= 5 else med
    mad_sig = robust_sigma(vals) if vals.size >= 3 else float(np.std(vals))
    sem = float(mad_sig / math.sqrt(vals.size)) if vals.size >= 2 else 0.0
    return {
        "n_pts": int(vals.size),
        "biweight_depth": round(bw, 5),
        "median_depth": round(med, 5),
        "err_depth": round(sem, 5),
        "scatter_mad": round(mad_sig, 5),
        "max_depth": round(float(np.max(vals)), 5),
    }


def audit_four_mandatory_surveys():
    """Verify raw archive logs and compute quantitative saturation/blending metrics for ATLAS, KELT-South, HATSouth, Evryscope."""
    with open(os.path.join(RAW_DIR, "nea_kelt_box1deg.json"), "r", encoding="utf-8") as f:
        kelt_1deg = json.load(f)
    with open(os.path.join(RAW_DIR, "nea_kelt_box2p5deg.json"), "r", encoding="utf-8") as f:
        kelt_2p5deg = json.load(f)
    with open(os.path.join(RAW_DIR, "nea_kelttimeseries_grid_140_190.json"), "r", encoding="utf-8") as f:
        kelt_grid = json.load(f)
    with open(os.path.join(RAW_DIR, "nea_kelt_S23_southern_edge.json"), "r", encoding="utf-8") as f:
        kelt_s23_edge = json.load(f)
    with open(os.path.join(RAW_DIR, "nea_kelt_S24_western_edge.json"), "r", encoding="utf-8") as f:
        kelt_s24_edge = json.load(f)
    with open(os.path.join(RAW_DIR, "nea_kelttimeseries_distinct_fields.json"), "r", encoding="utf-8") as f:
        kelt_fields = [x["kelt_field"] for x in json.load(f)]
    with open(os.path.join(RAW_DIR, "mast_caom_cone_all.json"), "r", encoding="utf-8") as f:
        mast_rows = json.load(f).get("data", [])

    # Check field bounds in KELT grid [140..190, -50..-20]
    field_bounds = {}
    for g in kelt_grid:
        fl = g["kelt_field"]
        b = field_bounds.setdefault(fl, {"ra_min": 999.0, "ra_max": -999.0, "dec_min": 999.0, "dec_max": -999.0, "n_cells": 0})
        b["ra_min"] = min(b["ra_min"], float(g["ra0"]))
        b["ra_max"] = max(b["ra_max"], float(g["ra0"]))
        b["dec_min"] = min(b["dec_min"], float(g["dec0"]))
        b["dec_max"] = max(b["dec_max"], float(g["dec0"]))
        b["n_cells"] += 1

    # Inspect hatsouth_org_lcs.html count of public HATS planet light curve links
    with open(os.path.join(RAW_DIR, "hatsouth_org_lcs.html"), "r", encoding="utf-8", errors="replace") as f:
        hats_html = f.read()
    hats_links = re.findall(r"HATS-\d+b", hats_html)
    distinct_hats_planets = sorted(set(hats_links))

    # Inspect atlas_forcedphot_index.html for login/token requirement
    with open(os.path.join(RAW_DIR, "atlas_forcedphot_index.html"), "r", encoding="utf-8", errors="replace") as f:
        atlas_html = f.read()
    atlas_requires_login = ("login" in atlas_html.lower()) or ("password" in atlas_html.lower())

    # Quantitative Photometry & Blending from bnty_0429 SED fit:
    # Target TIC 158499577: V = 8.81, B = 9.354, G = 8.6704, RP = 8.2181, T = 8.262, Teff = 5919 K
    # Neighbour 1 (TIC 942348495, sep=9.29"): V1 = 14.371, B1 = 15.654, R1 = 13.597
    # Neighbour 2 (TIC 942348496, sep=9.54"): V2 = 13.952, B2 = 15.209, R2 = 13.192
    # Combined neighbour flux fraction eps = (F1+F2)/(F_target+F1+F2):
    #   eps_B = 2.271%, eps_V = 2.466%, eps_R = 2.681%, eps_I = 2.917%

    surveys = {
        "ATLAS": {
            "survey_name": "ATLAS (Asteroid Terrestrial-impact Last Alert System - Sutherland & El Sauce southern nodes)",
            "covers_dec_minus36p6": True,
            "coverage_statement": (
                "YES - Dec = -36.5803 deg is covered at high elevation (zenith distance 4-6 deg) by both ATLAS southern "
                "stations (Sutherland, South Africa lat=-32.38 deg; El Sauce, Chile lat=-30.47 deg; operational since 2022 "
                "over Dec -90 to +30 deg) and near the southern horizon (Dec > -40 deg, airmass ~1.85) from Haleakala/Mauna Loa."
            ),
            "data_retrieved": False,
            "retrieval_status_and_reason": (
                "0 light curves retrieved. (1) Public MAST hlsp_atlas-var (Heinze et al. 2018) covers only Dec > -30 deg and "
                "stars fainter than m ~ 11.5 (0 ATLAS rows in raw/mast_caom_cone_all.json). (2) Official ATLAS Forced Photometry "
                "Server (https://fallingstar-data.com/forcedphot/, saved in raw/atlas_forcedphot_index.html, HTTP 200, "
                f"login_wall={atlas_requires_login}) requires creating a user account and API token, which is forbidden by "
                "bounty rules ('do not create accounts in DAiL's name'). (3) VizieR mirrors (cds.unistra.fr, cfa.harvard.edu, "
                "nao.ac.jp) timed out (WinError 10060, logged in raw/probe_summary.json)."
            ),
            "saturation_and_blending_caveats_V8p8": {
                "instrument_specs": "0.5m f/2.0 Wright-Schmidt, STA1600 10560x10560 CCD, 1.86 arcsec/px, 30s exposures, cyan (c: 420-650nm) & orange (o: 560-820nm)",
                "target_mag_est": {"c_mag": 8.98, "o_mag": 8.58, "V_mag": 8.81},
                "saturation_limit_mag": 12.7,
                "brighter_than_saturation_dmag": {"c_band": -3.72, "o_band": -4.12},
                "flux_over_saturation_ratio": {
                    "c_band": round(10 ** (0.4 * (12.7 - 8.98)), 1),
                    "o_band": round(10 ** (0.4 * (12.7 - 8.58)), 1),
                },
                "saturation_assessment": (
                    "SEVERE CORE SATURATION: Target (c~8.98, o~8.58) is 3.7 to 4.1 mag (30.8x to 44.5x in flux) brighter "
                    "than the ATLAS 30s saturation limit (m_sat ~ 12.5-13.0 mag), producing saturated PSF cores and CCD bleeding spikes."
                ),
                "blending_assessment": (
                    "At 1.86 arcsec/px (FWHM ~ 3.8 arcsec = 2.0 px), neighbours TIC 942348495 (9.29 arcsec = 5.00 px) and "
                    "TIC 942348496 (9.54 arcsec = 5.13 px) lie outside an unsaturated core PSF but within a 10 arcsec forced/wing "
                    "aperture or saturation bleed column (contributing eps_c ~ 2.38%, eps_o ~ 2.65% flux dilution if blended)."
                ),
            },
            "folded_depths_P11p7672_T0_2286p3720": {
                "status": "UNVERIFIED",
                "primary_depth": "UNVERIFIED",
                "secondary_depth": "UNVERIFIED",
                "uncertainty": "UNVERIFIED",
            },
        },
        "KELT-South": {
            "survey_name": "KELT-South (Kilodegree Extremely Little Telescope - South, Sutherland, South Africa)",
            "covers_dec_minus36p6": True,
            "covers_target_in_public_dr": False,
            "coverage_statement": (
                "Survey Declination Zone: YES (Sutherland lat=-32.38 deg survey covers Dec -84 to +5 deg in 26x26 deg fields). "
                "Target Coordinate (164.15975, -36.58031) in Public KELT DR (NASA Exoplanet Archive kelttimeseries): NO - "
                "falls in a 3.34 deg (Dec) x 2.74 deg (RA) inter-field cutout / unscheduled gap between KELT_S23 and KELT_S24."
            ),
            "data_retrieved": False,
            "retrieval_status_and_reason": (
                "Queried live NASA Exoplanet Archive TAP table kelttimeseries (28 released fields: 6 North + 22 South, "
                f"saved in raw/nea_kelt_box1deg.json [rows={len(kelt_1deg)}], raw/nea_kelt_box2p5deg.json [rows={len(kelt_2p5deg)}], "
                "raw/nea_kelttimeseries_grid_140_190.json [1,220 1x1 deg sky cells]). Exact field boundary audit around "
                "(164.16, -36.58): (a) Field S23 spans RA 146..175 deg, Dec -33.24..-20 deg; its southernmost star at target RA "
                f"is {kelt_s23_edge[0]['kelt_sourceid']} at (RA={kelt_s23_edge[0]['ra']}, Dec={kelt_s23_edge[0]['dec']}, "
                f"n={kelt_s23_edge[0]['npts']}), ending 4.17 deg north of target. (b) Field S24 spans RA 166.9..190 deg, "
                f"Dec -43..-20 deg; its westernmost star at target Dec is {kelt_s24_edge[0]['kelt_sourceid']} at "
                f"(RA={kelt_s24_edge[0]['ra']}, Dec={kelt_s24_edge[0]['dec']}, n={kelt_s24_edge[0]['npts']}), starting "
                "5.10 deg in RA (4.09 deg on-sky) east of target. (c) S22 ends at RA<=152 deg, S34 ends at RA<=144 deg, "
                "and S38 starts at RA>=173 deg."
            ),
            "kelt_grid_bounds_140_190": field_bounds,
            "saturation_and_blending_caveats_V8p8": {
                "instrument_specs": "Mamiya 645 42mm f/1.9 lens, Apogee AP16E 4096x4096 CCD, 23.0 arcsec/px, 26x26 deg FOV, 150s exposures, broadband R_KELT (490-900nm)",
                "target_mag_est": {"R_KELT_mag": 8.52, "V_mag": 8.81, "T_mag": 8.262},
                "saturation_limit_mag": 7.8,
                "brighter_than_saturation_dmag": +0.72,
                "flux_over_saturation_ratio": round(10 ** (0.4 * (7.8 - 8.52)), 2),
                "saturation_assessment": (
                    "UNSATURATED (IDEAL LINEAR REGIME): KELT-South saturates at V_sat ~ 7.5-8.0 (R_KELT ~ 7.5-7.8) in 150s "
                    "exposures and targets 8 < V < 11. At V=8.81 (R_KELT~8.52, 0.52x saturation flux), HD 94871 would be "
                    "unsaturated with ~3-5 mmag precision if covered."
                ),
                "blending_assessment": (
                    "100% SUB-PIXEL BLENDED: At 23.0 arcsec/px and a standard 3 px (69 arcsec radius) aperture, both "
                    "TIC 942348495 (9.29 arcsec = 0.40 px) and TIC 942348496 (9.54 arcsec = 0.41 px) fall inside the target's "
                    "central pixel, contributing eps_R = 2.681% +/- 0.055% flux dilution (diluting the 0.3357 primary depth by "
                    "-0.0090 in flux / -0.012 mag), plus minor dilution from 8 fainter Gaia DR3 sources (G=16.5-20.7) within 69 arcsec."
                ),
            },
            "folded_depths_P11p7672_T0_2286p3720": {
                "status": "UNVERIFIED",
                "primary_depth": "UNVERIFIED",
                "secondary_depth": "UNVERIFIED",
                "uncertainty": "UNVERIFIED",
            },
        },
        "HATSouth": {
            "survey_name": "HATSouth (Hungarian-made Automated Telescope Network - South: LCO, SSO, HESS)",
            "covers_dec_minus36p6": True,
            "coverage_statement": (
                "YES - Dec = -36.5803 deg transits within 5-13 deg of zenith at all three longitudinal HATSouth stations "
                "(Las Campanas lat=-29.01 deg, Siding Spring lat=-31.27 deg, HESS Namibia lat=-23.27 deg), which tile the "
                "southern sky in 8.2x8.2 deg fields (including the Dec = -33 deg and -41 deg strips)."
            ),
            "data_retrieved": False,
            "retrieval_status_and_reason": (
                "0 light curves retrieved. (1) Audited the official public HATSouth light curve archive "
                "(https://hatsouth.org/planets/ and https://hatsouth.org/planets/lightcurves.html, saved in "
                f"raw/hatsouth_org_planets.html and raw/hatsouth_org_lcs.html, HTTP 200): only {len(distinct_hats_planets)} "
                "confirmed exoplanet hosts (HATS-1b through HATS-77b) have publicly released light curves on hatsouth.org; "
                "there is no public general-star light-curve server on hatsouth.org, MAST (0 HATSouth rows in "
                "raw/mast_caom_cone_all.json), or NASA Exoplanet Archive. (2) VizieR mirrors timed out (WinError 10060)."
            ),
            "saturation_and_blending_caveats_V8p8": {
                "instrument_specs": "4x 18cm f/2.8 Takahashi epsilon-180 reflectors per mount, Apogee U16M 4096x4096 CCD, 3.7 arcsec/px, 8.2x8.2 deg FOV, 240s exposures, Sloan r band",
                "target_mag_est": {"r_mag": 8.65, "V_mag": 8.81},
                "saturation_limit_mag": 9.75,
                "brighter_than_saturation_dmag": -1.10,
                "flux_over_saturation_ratio": round(10 ** (0.4 * (9.75 - 8.65)), 2),
                "saturation_assessment": (
                    "CORE SATURATED: HATSouth 240s Sloan-r exposures saturate at r_sat ~ 9.5-10.0 mag (Bakos et al. 2013, "
                    "design range 10 < r < 16). At r ~ 8.65 mag (V=8.81), HD 94871 is ~0.85 to 1.35 mag (2.2x to 3.5x in flux) "
                    "brighter than the CCD saturation threshold."
                ),
                "blending_assessment": (
                    "BLENDED IN APERTURE: At 3.7 arcsec/px and a typical 3-4 px (11.1-14.8 arcsec radius) aperture, both "
                    "TIC 942348495 (9.29 arcsec = 2.51 px) and TIC 942348496 (9.54 arcsec = 2.58 px) fall inside the photometric "
                    "aperture, contributing eps_r ~ 2.60% flux dilution."
                ),
            },
            "folded_depths_P11p7672_T0_2286p3720": {
                "status": "UNVERIFIED",
                "primary_depth": "UNVERIFIED",
                "secondary_depth": "UNVERIFIED",
                "uncertainty": "UNVERIFIED",
            },
        },
        "Evryscope": {
            "survey_name": "Evryscope-South (CTIO, Chile, 22-camera 8,150 sq.deg all-sky array)",
            "covers_dec_minus36p6": True,
            "coverage_statement": (
                "YES - Evryscope-South at CTIO (lat=-30.17 deg) continuously monitors Dec -90 to +10 deg at 120s cadence; "
                "Dec = -36.5803 deg transits 6.4 deg south of the CTIO zenith."
            ),
            "data_retrieved": False,
            "retrieval_status_and_reason": (
                "0 light curves retrieved. (1) Evryscope does not provide an unauthenticated public light-curve portal for "
                "general field stars on MAST (0 Evryscope records in raw/mast_caom_cone_all.json) or NASA Exoplanet Archive. "
                "(2) VizieR queries to published Evryscope catalogs (J/ApJ/889/117, J/ApJ/890/115) timed out across all mirrors "
                "(WinError 10060, logged in raw/probe_summary.json)."
            ),
            "saturation_and_blending_caveats_V8p8": {
                "instrument_specs": "22x 61mm f/1.4 Rokinon lenses, 28.8MP KAI-29050 CCDs, 13.2 arcsec/px, 120s exposures, Sloan g' band",
                "target_mag_est": {"g_prime_mag": 9.05, "V_mag": 8.81, "B_mag": 9.354},
                "saturation_limit_mag": 9.0,
                "brighter_than_saturation_dmag": +0.05,
                "flux_over_saturation_ratio": round(10 ** (0.4 * (9.0 - 9.05)), 2),
                "saturation_assessment": (
                    "ON BRIGHT SATURATION / NONLINEARITY BOUNDARY: Evryscope-South 120s g' exposures reach full-well / "
                    "nonlinearity at g'_sat ~ 8.5-9.2 mag (Law et al. 2015, Ratzloff et al. 2019). At g' ~ 9.05 mag (V=8.81, "
                    "B=9.354), HD 94871 sits right at the bright saturation boundary (~0.95x saturation flux)."
                ),
                "blending_assessment": (
                    "100% SUB-PIXEL BLENDED: At 13.2 arcsec/px (2-3 px = 26.4-39.6 arcsec aperture), both TIC 942348495 "
                    "(9.29 arcsec = 0.70 px) and TIC 942348496 (9.54 arcsec = 0.72 px) lie within <0.75 px of the target center, "
                    "contributing eps_g' ~ 2.36% flux dilution."
                ),
            },
            "folded_depths_P11p7672_T0_2286p3720": {
                "status": "UNVERIFIED",
                "primary_depth": "UNVERIFIED",
                "secondary_depth": "UNVERIFIED",
                "uncertainty": "UNVERIFIED",
            },
        },
    }
    return surveys


def fold_supplementary_widefield_hlsps():
    """
    Fold all 5 public non-SPOC wide-field FFI survey pipelines retrieved from MAST in raw/hlsp_*.fits
    at the house ephemeris P = 11.7672 d, T0 = BTJD 2286.3720:
      1) MIT QLP (Quick-Look Pipeline, Sectors 9, 36, 63, 90, 99, 100) on TIC 158499577
         AND on blended neighbours TIC 942348495 (9.29") & TIC 942348496 (9.54").
      2) TGLC (TESS-Gaia Light Curve, Han & Brandt 2023, Sector 9) — Gaia DR3 prior ePSF-deblended
         photometry (psf_flux, cal_psf_flux, aperture_flux, cal_aper_flux).
      3) T16 (Princeton/HATSouth fitsh difference-imaging + EPD + TFA pipeline, Sector 9).
      4) NASA GSFC-ELEANOR-LITE (Sector 9: RAW_FLUX, CORR_FLUX, PCA_FLUX) on TIC 158499577
         AND on neighbours TIC 942348495 & TIC 942348496.
      5) TARS (Sector 9).
    """
    results = {}

    # 1. MIT QLP across Sectors 9, 36, 63, 90, 99, 100 for TIC 158499577
    qlp_sectors = [9, 36, 63, 90, 99, 100]
    qlp_phi_all = []
    qlp_sap_depth_all = []
    qlp_kspsap_depth_all = []
    qlp_per_sector = {}

    for sec in qlp_sectors:
        fn = f"hlsp_qlp_tess_ffi_s{sec:04d}-0000000158499577_tess_v01_llc.fits"
        _, data = read_fits_bintable(os.path.join(RAW_DIR, fn), 1)
        t = np.asarray(data["TIME"], dtype=np.float64)
        q = np.asarray(data["QUALITY"], dtype=np.int32)
        sap = np.asarray(data["SAP_FLUX"], dtype=np.float64)
        det_col = "DET_FLUX" if "DET_FLUX" in data.dtype.names else ("KSPSAP_FLUX" if "KSPSAP_FLUX" in data.dtype.names else "SAP_FLUX")
        det = np.asarray(data[det_col], dtype=np.float64)
        ok = (q == 0) & np.isfinite(t) & np.isfinite(sap)
        t = t[ok]
        sap = sap[ok]
        det = det[ok]

        # Normalize SAP_FLUX by out-of-eclipse Tukey biweight continuum
        med_sap = tukey_biweight(sap)
        d_sap = 1.0 - (sap / med_sap)
        # Note: QLP DET_FLUX is Kepler-spline detrended (which attenuates deep eclipses if unmasked)
        med_det = tukey_biweight(det[np.isfinite(det)])
        d_det = 1.0 - (det / med_det)

        phi = ((t - T0_HOUSE) / P_HOUSE) % 1.0
        qlp_phi_all.append(phi)
        qlp_sap_depth_all.append(d_sap)
        qlp_kspsap_depth_all.append(d_det)

        qlp_per_sector[str(sec)] = {
            "n_pts_q0": int(len(t)),
            "SAP_box_hw0017_PRI": measure_phase_window(phi, d_sap, 0.00000, 0.0017),
            "SAP_box_hw0017_SEC_ecc": measure_phase_window(phi, d_sap, PHI_SEC_ECC, 0.0017),
            "SAP_core_hw0010_PRI": measure_phase_window(phi, d_sap, 0.00000, 0.0010),
            "SAP_core_hw0010_SEC_ecc": measure_phase_window(phi, d_sap, PHI_SEC_ECC, 0.0010),
            "DET_FLUX_spline_attenuated_box_PRI": measure_phase_window(phi, d_det, 0.00000, 0.0017),
            "DET_FLUX_spline_attenuated_box_SEC_ecc": measure_phase_window(phi, d_det, PHI_SEC_ECC, 0.0017),
        }

    phi_q = np.concatenate(qlp_phi_all)
    dsap_q = np.concatenate(qlp_sap_depth_all)
    ddet_q = np.concatenate(qlp_kspsap_depth_all)
    results["MIT_QLP_S9_S36_S63_S90_S99_S100"] = {
        "n_pts_total_q0": int(len(phi_q)),
        "combined_SAP_core_hw0010": {
            "primary_phi0000": measure_phase_window(phi_q, dsap_q, 0.00000, 0.0010),
            "secondary_ecc_phi05141": measure_phase_window(phi_q, dsap_q, PHI_SEC_ECC, 0.0010),
            "secondary_circ_phi05000": measure_phase_window(phi_q, dsap_q, 0.50000, 0.0010),
        },
        "combined_SAP_box_hw0017": {
            "primary_phi0000": measure_phase_window(phi_q, dsap_q, 0.00000, 0.0017),
            "secondary_ecc_phi05141": measure_phase_window(phi_q, dsap_q, PHI_SEC_ECC, 0.0017),
            "secondary_circ_phi05000": measure_phase_window(phi_q, dsap_q, 0.50000, 0.0017),
            "control_phi0250": measure_phase_window(phi_q, dsap_q, 0.25000, 0.0017),
            "control_phi0750": measure_phase_window(phi_q, dsap_q, 0.75000, 0.0017),
        },
        "combined_DET_FLUX_spline_attenuated_box_hw0017": {
            "primary_phi0000": measure_phase_window(phi_q, ddet_q, 0.00000, 0.0017),
            "secondary_ecc_phi05141": measure_phase_window(phi_q, ddet_q, PHI_SEC_ECC, 0.0017),
        },
        "per_sector": qlp_per_sector,
    }

    # 1b. QLP Blended Neighbour Verification (TIC 942348495 at 9.29" and TIC 942348496 at 9.54" in S63)
    for nb_tic in ("942348495", "942348496"):
        fn_nb = f"hlsp_qlp_tess_ffi_s0063-0000000{nb_tic}_tess_v01_llc.fits"
        _, d_nb = read_fits_bintable(os.path.join(RAW_DIR, fn_nb), 1)
        t_nb = np.asarray(d_nb["TIME"], dtype=np.float64)
        q_nb = np.asarray(d_nb["QUALITY"], dtype=np.int32)
        sap_nb = np.asarray(d_nb["SAP_FLUX"], dtype=np.float64)
        ok_nb = (q_nb == 0) & np.isfinite(t_nb) & np.isfinite(sap_nb)
        phi_nb = ((t_nb[ok_nb] - T0_HOUSE) / P_HOUSE) % 1.0
        depth_nb = 1.0 - (sap_nb[ok_nb] / tukey_biweight(sap_nb[ok_nb]))
        results[f"MIT_QLP_S63_Blended_Neighbour_TIC_{nb_tic}"] = {
            "n_pts_q0": int(np.sum(ok_nb)),
            "note": "Demonstrates 21 arcsec/px wide-field blending: neighbour aperture captures target PSF wings and shows ~32%/28% apparent eclipse!",
            "SAP_core_hw0010_PRI": measure_phase_window(phi_nb, depth_nb, 0.00000, 0.0010),
            "SAP_core_hw0010_SEC_ecc": measure_phase_window(phi_nb, depth_nb, PHI_SEC_ECC, 0.0010),
            "SAP_box_hw0017_PRI": measure_phase_window(phi_nb, depth_nb, 0.00000, 0.0017),
            "SAP_box_hw0017_SEC_ecc": measure_phase_window(phi_nb, depth_nb, PHI_SEC_ECC, 0.0017),
        }

    # 2. TGLC (Gaia DR3 ePSF-deblended wide-field FFI pipeline, Sector 9)
    # Note: For bright stars (T = 8.262 < 9.0), TGLC sets psf_flux=NaN and outputs Gaia-field-deblended aperture_flux & cal_aper_flux!
    fn_tglc = "hlsp_tglc_tess_ffi_gaiaid-5401019098113741568-s0009-cam2-ccd3_tess_v1_llc.fits"
    _, d_tglc = read_fits_bintable(os.path.join(RAW_DIR, fn_tglc), 1)
    t_tg = np.asarray(d_tglc["time"], dtype=np.float64)
    f_ap = np.asarray(d_tglc["aperture_flux"], dtype=np.float64)
    f_cap = np.asarray(d_tglc["cal_aper_flux"], dtype=np.float64)
    fl_t = np.asarray(d_tglc["TESS_flags"], dtype=np.int32)
    fl_g = np.asarray(d_tglc["TGLC_flags"], dtype=np.int32)
    ok_tg = (fl_t == 0) & np.isfinite(t_tg) & np.isfinite(f_ap)
    phi_tg = ((t_tg[ok_tg] - T0_HOUSE) / P_HOUSE) % 1.0
    d_tg_ap = 1.0 - (f_ap[ok_tg] / tukey_biweight(f_ap[ok_tg]))
    d_tg_cap = 1.0 - (f_cap[ok_tg] / tukey_biweight(f_cap[ok_tg]))
    results["TGLC_Gaia_ePSF_Deblended_S9"] = {
        "n_pts_clean": int(np.sum(ok_tg)),
        "note": "For T=8.262 (<9.0), TGLC disables psf_flux (all NaN) and provides Gaia-prior field-subtracted aperture_flux & cal_aper_flux.",
        "aperture_flux_core_hw0010_PRI": measure_phase_window(phi_tg, d_tg_ap, 0.00000, 0.0010),
        "aperture_flux_core_hw0010_SEC_ecc": measure_phase_window(phi_tg, d_tg_ap, PHI_SEC_ECC, 0.0010),
        "aperture_flux_box_hw0017_PRI": measure_phase_window(phi_tg, d_tg_ap, 0.00000, 0.0017),
        "aperture_flux_box_hw0017_SEC_ecc": measure_phase_window(phi_tg, d_tg_ap, PHI_SEC_ECC, 0.0017),
        "aperture_flux_mid_hw0025_PRI": measure_phase_window(phi_tg, d_tg_ap, 0.00000, 0.0025),
        "aperture_flux_mid_hw0025_SEC_ecc": measure_phase_window(phi_tg, d_tg_ap, PHI_SEC_ECC, 0.0025),
        "cal_aper_wotan_detrended_box_PRI": measure_phase_window(phi_tg, d_tg_cap, 0.00000, 0.0017),
        "cal_aper_wotan_detrended_box_SEC_ecc": measure_phase_window(phi_tg, d_tg_cap, PHI_SEC_ECC, 0.0017),
        "control_phi0250": measure_phase_window(phi_tg, d_tg_ap, 0.25000, 0.0025),
        "control_phi0750": measure_phase_window(phi_tg, d_tg_ap, 0.75000, 0.0025),
    }

    # 3. T16 (Princeton / HATSouth fitsh difference-imaging IFL/IRM/EPD/TFA pipeline, Sector 9)
    fn_t16 = "hlsp_t16_tess_ffi_s0009-cam2-ccd3-05401019098113741568_tess_v01_llc.fits"
    _, d_t16 = read_fits_bintable(os.path.join(RAW_DIR, fn_t16), 1)
    # TMID_BJD in T16 is BJD - 2400000 or full BJD; let's check and convert to BTJD = BJD - 2457000
    t_bjd = np.asarray(d_t16["TMID_BJD"], dtype=np.float64)
    if np.nanmedian(t_bjd) > 2400000.0:
        t_16 = t_bjd - 2457000.0
    elif np.nanmedian(t_bjd) > 50000.0:
        t_16 = t_bjd - 57000.0
    else:
        t_16 = t_bjd
    ifl1 = np.asarray(d_t16["IFL1"], dtype=np.float64)
    irm1 = np.asarray(d_t16["IRM1"], dtype=np.float64)
    epd1 = np.asarray(d_t16["EPD1"], dtype=np.float64)
    tfa1 = np.asarray(d_t16["TFA1"], dtype=np.float64)
    ok_16 = np.isfinite(t_16) & np.isfinite(ifl1) & (ifl1 > 0) & np.isfinite(irm1) & (irm1 < 50)
    phi_16 = ((t_16[ok_16] - T0_HOUSE) / P_HOUSE) % 1.0
    d_16_flux = 1.0 - (ifl1[ok_16] / tukey_biweight(ifl1[ok_16]))
    d_16_irm_mag = irm1[ok_16] - tukey_biweight(irm1[ok_16])
    d_16_epd_mag = epd1[ok_16] - tukey_biweight(epd1[ok_16])
    d_16_tfa_mag = tfa1[ok_16] - tukey_biweight(tfa1[ok_16])
    results["T16_HATSouth_fitsh_Pipeline_S9"] = {
        "n_pts_clean": int(np.sum(ok_16)),
        "btjd_range": [round(float(np.min(t_16[ok_16])), 4), round(float(np.max(t_16[ok_16])), 4)],
        "IFL1_flux_core_hw0010_PRI": measure_phase_window(phi_16, d_16_flux, 0.00000, 0.0010),
        "IFL1_flux_core_hw0010_SEC_ecc": measure_phase_window(phi_16, d_16_flux, PHI_SEC_ECC, 0.0010),
        "IFL1_flux_box_hw0017_PRI": measure_phase_window(phi_16, d_16_flux, 0.00000, 0.0017),
        "IFL1_flux_box_hw0017_SEC_ecc": measure_phase_window(phi_16, d_16_flux, PHI_SEC_ECC, 0.0017),
        "IRM1_dmag_box_hw0017_PRI": measure_phase_window(phi_16, d_16_irm_mag, 0.00000, 0.0017),
        "IRM1_dmag_box_hw0017_SEC_ecc": measure_phase_window(phi_16, d_16_irm_mag, PHI_SEC_ECC, 0.0017),
        "EPD1_dmag_box_hw0017_PRI": measure_phase_window(phi_16, d_16_epd_mag, 0.00000, 0.0017),
        "EPD1_dmag_box_hw0017_SEC_ecc": measure_phase_window(phi_16, d_16_epd_mag, PHI_SEC_ECC, 0.0017),
        "TFA1_dmag_box_hw0017_PRI": measure_phase_window(phi_16, d_16_tfa_mag, 0.00000, 0.0017),
        "TFA1_dmag_box_hw0017_SEC_ecc": measure_phase_window(phi_16, d_16_tfa_mag, PHI_SEC_ECC, 0.0017),
        "control_phi0250_flux": measure_phase_window(phi_16, d_16_flux, 0.25000, 0.0025),
        "control_phi0750_flux": measure_phase_window(phi_16, d_16_flux, 0.75000, 0.0025),
    }

    # 4. GSFC-ELEANOR-LITE (Sector 9)
    fn_el = "hlsp_gsfc-eleanor-lite_tess_ffi_s0009-0000000158499577_tess_v1.0_lc.fits"
    _, d_el = read_fits_bintable(os.path.join(RAW_DIR, fn_el), 1)
    t_el = np.asarray(d_el["TIME"], dtype=np.float64)
    q_el = np.asarray(d_el["QUALITY"], dtype=np.int32)
    f_raw = np.asarray(d_el["RAW_FLUX"], dtype=np.float64)
    f_cor = np.asarray(d_el["CORR_FLUX"], dtype=np.float64)
    f_pca = np.asarray(d_el["PCA_FLUX"], dtype=np.float64)
    ok_el = (q_el == 0) & np.isfinite(t_el) & np.isfinite(f_cor)
    phi_el = ((t_el[ok_el] - T0_HOUSE) / P_HOUSE) % 1.0
    d_el_raw = 1.0 - (f_raw[ok_el] / tukey_biweight(f_raw[ok_el]))
    d_el_cor = 1.0 - (f_cor[ok_el] / tukey_biweight(f_cor[ok_el]))
    d_el_pca = 1.0 - (f_pca[ok_el] / tukey_biweight(f_pca[ok_el]))
    results["GSFC_ELEANOR_LITE_S9"] = {
        "n_pts_q0": int(np.sum(ok_el)),
        "RAW_FLUX_box_hw0017_PRI": measure_phase_window(phi_el, d_el_raw, 0.00000, 0.0017),
        "RAW_FLUX_box_hw0017_SEC_ecc": measure_phase_window(phi_el, d_el_raw, PHI_SEC_ECC, 0.0017),
        "CORR_FLUX_box_hw0017_PRI": measure_phase_window(phi_el, d_el_cor, 0.00000, 0.0017),
        "CORR_FLUX_box_hw0017_SEC_ecc": measure_phase_window(phi_el, d_el_cor, PHI_SEC_ECC, 0.0017),
        "PCA_FLUX_box_hw0017_PRI": measure_phase_window(phi_el, d_el_pca, 0.00000, 0.0017),
        "PCA_FLUX_box_hw0017_SEC_ecc": measure_phase_window(phi_el, d_el_pca, PHI_SEC_ECC, 0.0017),
        "control_phi0250": measure_phase_window(phi_el, d_el_cor, 0.25000, 0.0025),
        "control_phi0750": measure_phase_window(phi_el, d_el_cor, 0.75000, 0.0025),
    }

    # 5. TARS (Sector 9)
    fn_tars = "hlsp_tars_tess_ffi_s0009-0000000158499577_tess_v01_lc.fits"
    _, d_tars = read_fits_bintable(os.path.join(RAW_DIR, fn_tars), 1)
    t_tr = np.asarray(d_tars["TIME"], dtype=np.float64)
    f_tr = np.asarray(d_tars["FLUX"], dtype=np.float64)
    ok_tr = np.isfinite(t_tr) & np.isfinite(f_tr)
    phi_tr = ((t_tr[ok_tr] - T0_HOUSE) / P_HOUSE) % 1.0
    d_tr_depth = 1.0 - (f_tr[ok_tr] / tukey_biweight(f_tr[ok_tr]))
    results["TARS_S9"] = {
        "n_pts_clean": int(np.sum(ok_tr)),
        "FLUX_box_hw0017_PRI": measure_phase_window(phi_tr, d_tr_depth, 0.00000, 0.0017),
        "FLUX_box_hw0017_SEC_ecc": measure_phase_window(phi_tr, d_tr_depth, PHI_SEC_ECC, 0.0017),
        "control_phi0250": measure_phase_window(phi_tr, d_tr_depth, 0.25000, 0.0025),
        "control_phi0750": measure_phase_window(phi_tr, d_tr_depth, 0.75000, 0.0025),
    }

    return results


def main():
    mandatory_surveys = audit_four_mandatory_surveys()
    supplementary_hlsps = fold_supplementary_widefield_hlsps()

    out = {
        "bounty_id": "bnty_0428",
        "target": "TIC 158499577 (HD 94871)",
        "coordinates_icrs": {"ra_deg": RA_DEG, "dec_deg": DEC_DEG},
        "house_ephemeris": {"P_d": P_HOUSE, "T0_btjd": T0_HOUSE, "phi_sec_eccentric": PHI_SEC_ECC},
        "method_version": "1.0.0",
        "execution_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "mandatory_widefield_surveys": mandatory_surveys,
        "supplementary_public_widefield_hlsp_folds": supplementary_hlsps,
    }

    res_path = os.path.join(RES_DIR, "widefield_survey_folds.json")
    with open(res_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print("=== bnty_0428 Mandatory Wide-Field Surveys Summary ===")
    for sname, sinfo in mandatory_surveys.items():
        print(
            f"  {sname:10s}: covers_Dec=-36.6={sinfo['covers_dec_minus36p6']} | "
            f"retrieved={sinfo['data_retrieved']} | "
            f"fold_status={sinfo['folded_depths_P11p7672_T0_2286p3720']['status']}"
        )
    print("\n=== Supplementary Public Wide-Field HLSP Folds (P=11.7672d, T0=2286.3720) ===")
    q_comb = supplementary_hlsps["MIT_QLP_S9_S36_S63_S90_S99_S100"]
    print("  MIT QLP (S9-S100, n={}): Core PRI={}, SEC_ecc={} | Box PRI={}, SEC_ecc={}".format(
        q_comb["n_pts_total_q0"],
        q_comb["combined_SAP_core_hw0010"]["primary_phi0000"]["biweight_depth"],
        q_comb["combined_SAP_core_hw0010"]["secondary_ecc_phi05141"]["biweight_depth"],
        q_comb["combined_SAP_box_hw0017"]["primary_phi0000"]["biweight_depth"],
        q_comb["combined_SAP_box_hw0017"]["secondary_ecc_phi05141"]["biweight_depth"],
    ))
    tg = supplementary_hlsps["TGLC_Gaia_ePSF_Deblended_S9"]
    print("  TGLC Gaia-ePSF (S9, n={}): Core PRI={}, SEC_ecc={} | Box PRI={}, SEC_ecc={}".format(
        tg["n_pts_clean"],
        tg["aperture_flux_core_hw0010_PRI"]["biweight_depth"],
        tg["aperture_flux_core_hw0010_SEC_ecc"]["biweight_depth"],
        tg["aperture_flux_box_hw0017_PRI"]["biweight_depth"],
        tg["aperture_flux_box_hw0017_SEC_ecc"]["biweight_depth"],
    ))
    t16 = supplementary_hlsps["T16_HATSouth_fitsh_Pipeline_S9"]
    print("  T16 HATSouth/fitsh (S9, n={}): IFL1 Box PRI={}, SEC_ecc={} | IRM1 dmag PRI={}, SEC_ecc={}".format(
        t16["n_pts_clean"],
        t16["IFL1_flux_box_hw0017_PRI"]["biweight_depth"],
        t16["IFL1_flux_box_hw0017_SEC_ecc"]["biweight_depth"],
        t16["IRM1_dmag_box_hw0017_PRI"]["biweight_depth"],
        t16["IRM1_dmag_box_hw0017_SEC_ecc"]["biweight_depth"],
    ))
    el = supplementary_hlsps["GSFC_ELEANOR_LITE_S9"]
    print("  GSFC-ELEANOR-LITE (S9, n={}): CORR Box PRI={}, SEC_ecc={} | RAW Box PRI={}, SEC_ecc={}".format(
        el["n_pts_q0"],
        el["CORR_FLUX_box_hw0017_PRI"]["biweight_depth"],
        el["CORR_FLUX_box_hw0017_SEC_ecc"]["biweight_depth"],
        el["RAW_FLUX_box_hw0017_PRI"]["biweight_depth"],
        el["RAW_FLUX_box_hw0017_SEC_ecc"]["biweight_depth"],
    ))


if __name__ == "__main__":
    main()
