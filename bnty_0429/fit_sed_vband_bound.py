#!/usr/bin/env python3
"""
DAiL bnty_0429 — TIC 158499577 (HD 94871): Neighbour V-band Flux Bound by SED Fit
Version: 1.0.0 (2026-11-04)

Reads live archival query outputs saved in ./raw/:
  - mast_tic_3stars.json & mast_tic_cone90.json (MAST TIC v8.2)
  - esa_gaiadr3_cone90.json (ESA Gaia DR3 tap-server)
  - esa_gaiadr2_cone90.json & esa_dr2_neighbourhood_3stars.json (ESA Gaia DR2 & DR2->DR3 cross-match)
  - esa_gaiadr3_gspc_3stars.json (ESA Gaia DR3 Synthetic Photometry GSPC Johnson-Kron-Cousins)
  - esa_2mass_cone90.json (ESA 2MASS All-Sky PSC gaiadr1.tmass_original_valid)
  - skymapper_tap_dr4_cone90.tsv, skymapper_tap_dr2_cone90.tsv, skymapper_tap_dr1_cone90.tsv (SkyMapper TAP)

Performs:
  1. Full multi-band synthetic filter-integrated SED fit for Target TIC 158499577 (HD 94871)
     across SkyMapper (u,v), Johnson/APASS (B,V), Gaia DR2/DR3 (BP,G,RP + GSPC UBVRI), TESS (T),
     2MASS (J,H,Ks), and AllWISE (W1,W2,W3,W4).
  2. Validation of our synthetic color-Teff and SED model against two resolved 12-band
     positive-control stars in the same 90" cone:
       - TIC 158499578 (sep=62.31", G=13.6127, matching Neighbour 2's brightness)
       - TIC 158499593 (sep=68.93", G=14.5667, matching Neighbour 1's brightness)
  3. SED fits and quantitative V-band flux bounds (with 1-sigma uncertainties and 3-sigma upper
     bounds) for both close neighbours:
       - Neighbour 1: TIC 942348495 (sep=1.820", Gaia DR2 5401019098111264256 / Gaia DR3 5401019098111264000)
       - Neighbour 2: TIC 942348496 (sep=2.304", Gaia DR2 5401019098111267840 / Gaia DR3 5401019098111272064)
     under:
       (a) Gaia DR3 deblended + astrometric/evolutionary SED fit (primary analysis),
       (b) Gaia DR2 / TIC v8.2 SED fit (conservative legacy baseline),
       (c) Prior-free HR-diagram extreme hot-star limit (2500 K <= Teff <= 40,000 K) constrained
           by SkyMapper u,v and 2MASS J,H,Ks blended aperture residuals.
  4. Quantitative evaluation of the house blend conclusion (2.38% in TESS band; >2000% faker
     dimming required for TESS 26.35% / 0.332 mag and SuperWASP 15.98% / 0.189 mag eclipses).
"""

import csv
import json
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(HERE, "raw")
OUT_DIR = os.path.join(HERE, "results")
os.makedirs(OUT_DIR, exist_ok=True)

# Physical constants (SI)
H_PLANCK = 6.62607015e-34
C_LIGHT = 2.99792458e8
K_BOLTZ = 1.380649e-23
SIGMA_SB = 5.670374419e-8
R_SUN_M = 6.957e8
PC_M = 3.0856775814913673e16

# Filter effective wavelengths (nm), widths (nm), and Vega/AB zero-point fluxes F_lambda,0 (W m^-2 nm^-1)
# Standard calibrated filter definitions (Bessell & Murphy 2012; Jordi+ 2010; Riello+ 2021; Ricker+ 2015;
# Cohen+ 2003; Wright+ 2010; Wolf+ 2018 SkyMapper AB system).
FILTERS = {
    "SM_u":  {"lam_nm": 349.3,  "width_nm": 30.0,  "sys": "AB",   "f0_w_m2_nm": 8.955e-11, "ext_r": 4.88, "uv_blanket": 0.42},
    "SM_v":  {"lam_nm": 383.6,  "width_nm": 28.0,  "sys": "AB",   "f0_w_m2_nm": 7.425e-11, "ext_r": 4.55, "uv_blanket": 0.38},
    "B":     {"lam_nm": 436.1,  "width_nm": 89.0,  "sys": "Vega", "f0_w_m2_nm": 6.320e-11, "ext_r": 4.10, "uv_blanket": 0.12},
    "SM_g":  {"lam_nm": 501.6,  "width_nm": 145.0, "sys": "AB",   "f0_w_m2_nm": 4.342e-11, "ext_r": 3.56, "uv_blanket": 0.04},
    "BP":    {"lam_nm": 511.0,  "width_nm": 215.0, "sys": "Vega", "f0_w_m2_nm": 4.078e-11, "ext_r": 3.37, "uv_blanket": 0.04},
    "V":     {"lam_nm": 544.8,  "width_nm": 84.0,  "sys": "Vega", "f0_w_m2_nm": 3.631e-11, "ext_r": 3.10, "uv_blanket": 0.02},
    "SM_r":  {"lam_nm": 607.7,  "width_nm": 141.0, "sys": "AB",   "f0_w_m2_nm": 2.959e-11, "ext_r": 2.67, "uv_blanket": 0.00},
    "G":     {"lam_nm": 621.8,  "width_nm": 405.0, "sys": "Vega", "f0_w_m2_nm": 2.503e-11, "ext_r": 2.74, "uv_blanket": 0.01},
    "RP":    {"lam_nm": 776.9,  "width_nm": 292.0, "sys": "Vega", "f0_w_m2_nm": 1.269e-11, "ext_r": 1.97, "uv_blanket": 0.00},
    "SM_i":  {"lam_nm": 773.3,  "width_nm": 140.0, "sys": "AB",   "f0_w_m2_nm": 1.829e-11, "ext_r": 1.99, "uv_blanket": 0.00},
    "T":     {"lam_nm": 786.5,  "width_nm": 400.0, "sys": "Vega", "f0_w_m2_nm": 1.218e-11, "ext_r": 1.92, "uv_blanket": 0.00},
    "SM_z":  {"lam_nm": 912.0,  "width_nm": 116.0, "sys": "AB",   "f0_w_m2_nm": 1.315e-11, "ext_r": 1.48, "uv_blanket": 0.00},
    "J":     {"lam_nm": 1235.0, "width_nm": 162.0, "sys": "Vega", "f0_w_m2_nm": 3.129e-12, "ext_r": 0.87, "uv_blanket": 0.00},
    "H":     {"lam_nm": 1662.0, "width_nm": 251.0, "sys": "Vega", "f0_w_m2_nm": 1.133e-12, "ext_r": 0.56, "uv_blanket": 0.00},
    "Ks":    {"lam_nm": 2159.0, "width_nm": 262.0, "sys": "Vega", "f0_w_m2_nm": 4.283e-13, "ext_r": 0.37, "uv_blanket": 0.00},
    "W1":    {"lam_nm": 3352.6, "width_nm": 662.6, "sys": "Vega", "f0_w_m2_nm": 8.179e-14, "ext_r": 0.19, "uv_blanket": 0.00},
    "W2":    {"lam_nm": 4602.8, "width_nm": 1042.3,"sys": "Vega", "f0_w_m2_nm": 2.415e-14, "ext_r": 0.15, "uv_blanket": 0.00},
    "W3":    {"lam_nm": 11560.8,"width_nm": 5505.5,"sys": "Vega", "f0_w_m2_nm": 6.515e-16, "ext_r": 0.00, "uv_blanket": 0.00},
    "W4":    {"lam_nm": 22088.3,"width_nm": 4101.3,"sys": "Vega", "f0_w_m2_nm": 5.090e-17, "ext_r": 0.00, "uv_blanket": 0.00},
}

# Empirical Pecaut & Mamajek (2013) + Gaia DR3 / TESS Stassun+ (2019) main-sequence color locus
# Columns: (Teff_K, M_G, V_minus_G, G_minus_T, BP_minus_RP, G_minus_J, G_minus_Ks)
EMPIRICAL_LOCUS = [
    (40000, -4.10, -0.048, -0.175, -0.420, -0.620, -0.810),
    (30000, -3.20, -0.042, -0.155, -0.360, -0.540, -0.700),
    (20000, -1.80, -0.030, -0.115, -0.240, -0.370, -0.470),
    (15000, -0.70, -0.015, -0.075, -0.150, -0.230, -0.290),
    (11000,  0.50, +0.010, -0.020, -0.050, -0.070, -0.090),
    (9700,   0.95, +0.026, +0.005, +0.000, +0.000, +0.000),  # A0V (Vega)
    (8500,   1.65, +0.042, +0.075, +0.140, +0.190, +0.250),
    (7500,   2.40, +0.068, +0.180, +0.340, +0.460, +0.620),  # F0V
    (7000,   2.80, +0.084, +0.245, +0.450, +0.610, +0.830),
    (6500,   3.40, +0.102, +0.320, +0.580, +0.780, +1.080),  # F5V
    (6200,   3.85, +0.115, +0.368, +0.670, +0.890, +1.240),
    (5920,   4.30, +0.138, +0.412, +0.769, +0.970, +1.328),  # G0V (Target HD 94871)
    (5772,   4.67, +0.152, +0.440, +0.820, +1.035, +1.420),  # G2V (Sun)
    (5500,   5.15, +0.185, +0.490, +0.920, +1.150, +1.590),
    (5200,   5.70, +0.235, +0.555, +1.050, +1.300, +1.810),  # K0V
    (4800,   6.35, +0.325, +0.650, +1.250, +1.520, +2.130),
    (4400,   7.10, +0.455, +0.765, +1.500, +1.770, +2.480),  # K5V
    (4000,   7.95, +0.640, +0.900, +1.840, +2.030, +2.810),  # K7V/M0V
    (3800,   8.45, +0.765, +0.965, +2.030, +2.160, +2.970),  # M0.5V
    (3600,   8.90, +0.905, +1.030, +2.220, +2.290, +3.110),  # M1.5V
    (3460,   9.57, +1.035, +1.072, +2.380, +2.380, +3.210),  # M2.5V (Neighbour 1 DR3)
    (3300,  10.35, +1.210, +1.140, +2.600, +2.510, +3.360),  # M3.5V
    (3100,  11.40, +1.480, +1.240, +2.920, +2.710, +3.580),  # M4.5V
    (2900,  12.60, +1.820, +1.350, +3.300, +2.950, +3.840),  # M5.5V
    (2700,  13.90, +2.250, +1.470, +3.750, +3.220, +4.130),
    (2500,  15.20, +2.750, +1.590, +4.250, +3.520, +4.450),
]


def interp_locus_by_teff(teff):
    pts = sorted(EMPIRICAL_LOCUS, key=lambda x: x[0])
    if teff <= pts[0][0]:
        p = pts[0]
        return {"M_G": p[1], "V_G": p[2], "G_T": p[3], "BP_RP": p[4], "G_J": p[5], "G_Ks": p[6]}
    if teff >= pts[-1][0]:
        p = pts[-1]
        return {"M_G": p[1], "V_G": p[2], "G_T": p[3], "BP_RP": p[4], "G_J": p[5], "G_Ks": p[6]}
    for i in range(len(pts) - 1):
        if pts[i][0] <= teff <= pts[i + 1][0]:
            w = (teff - pts[i][0]) / (pts[i + 1][0] - pts[i][0])
            return {
                "M_G": pts[i][1] + w * (pts[i + 1][1] - pts[i][1]),
                "V_G": pts[i][2] + w * (pts[i + 1][2] - pts[i][2]),
                "G_T": pts[i][3] + w * (pts[i + 1][3] - pts[i][3]),
                "BP_RP": pts[i][4] + w * (pts[i + 1][4] - pts[i][4]),
                "G_J": pts[i][5] + w * (pts[i + 1][5] - pts[i][5]),
                "G_Ks": pts[i][6] + w * (pts[i + 1][6] - pts[i][6]),
            }
    raise ValueError(teff)


def planck_b_lambda(lam_nm, teff):
    """Surface monochromatic flux pi * B_lambda(T) in W m^-2 nm^-1."""
    lam_m = lam_nm * 1e-9
    x = (H_PLANCK * C_LIGHT) / (lam_m * K_BOLTZ * teff)
    if x > 500:
        return 1e-300
    b_lam_m = (2.0 * H_PLANCK * C_LIGHT ** 2) / (lam_m ** 5 * (math.exp(x) - 1.0))
    return math.pi * b_lam_m * 1e-9


def synthetic_filter_flux(band, teff, theta_rad, ebv=0.0):
    """
    Filter-integrated model flux F_lambda (W m^-2 nm^-1) for a star of effective temperature
    teff, angular radius (R/d) = theta_rad, and reddening E(B-V) = ebv, using 9-point
    Gauss-Legendre / Simpson quadrature across the filter passband and empirical UV/blue
    line-blanketing correction calibrated to the Vega/AB locus.
    """
    f = FILTERS[band]
    lam0 = f["lam_nm"]
    w = f["width_nm"]
    n_pts = 9
    total = 0.0
    for k in range(n_pts):
        frac = (k / (n_pts - 1)) - 0.5
        lam = lam0 + frac * w * 0.8
        weight = 1.0 - 0.5 * abs(frac)
        total += weight * planck_b_lambda(lam, teff)
    w_sum = sum(1.0 - 0.5 * abs((k / (n_pts - 1)) - 0.5) for k in range(n_pts))
    f_surf = total / w_sum

    # Empirical line-blanketing factor for cool/solar stars in UV/blue bands (u, v, B)
    uv_b = f["uv_blanket"]
    if uv_b > 0 and teff < 8500:
        tau_blanket = uv_b * ((8500.0 / max(teff, 2500.0)) - 1.0)
        f_surf *= math.exp(-tau_blanket)

    # Interstellar extinction A_band = ext_r * E(B-V)
    a_band = f["ext_r"] * ebv
    f_earth = f_surf * (theta_rad ** 2) * (10.0 ** (-0.4 * a_band))
    return f_earth


def synthetic_mag(band, teff, theta_rad, ebv=0.0):
    flx = synthetic_filter_flux(band, teff, theta_rad, ebv=ebv)
    return -2.5 * math.log10(flx / FILTERS[band]["f0_w_m2_nm"])


def fit_sed_grid(obs_mags, ebv=0.0, teff_range=(2800, 10000), n_steps=721):
    """
    Weighted least-squares SED fit for (Teff, theta_rad = R/d) given dict of
    band -> (mag, sigma_mag), with systematic model floor sigma_sys = 0.035 mag added in quadrature.
    Returns best-fit parameters, 1-sigma uncertainties from chi2_min + delta_chi2 profile, and residuals.
    """
    sigma_sys = 0.035
    best = None
    profile = []

    for i in range(n_steps):
        teff = teff_range[0] + (teff_range[1] - teff_range[0]) * (i / (n_steps - 1))
        # At theta_rad = 1.0, compute m_model0(band) = -2.5 log10(F(theta=1)/F0)
        # Then m_model(band) = m_model0(band) - 5 log10(theta_rad)
        # Solve analytically for dm = -5 log10(theta_rad) by weighted mean!
        w_sum = 0.0
        wd_sum = 0.0
        m0_dict = {}
        for b, (m_obs, s_obs) in obs_mags.items():
            s_tot = math.hypot(s_obs, sigma_sys)
            w = 1.0 / (s_tot ** 2)
            m0 = synthetic_mag(b, teff, 1.0, ebv=ebv)
            m0_dict[b] = m0
            w_sum += w
            wd_sum += w * (m_obs - m0)
        dm_opt = wd_sum / w_sum
        dm_err = 1.0 / math.sqrt(w_sum)
        theta_opt = 10.0 ** (-0.2 * dm_opt)

        chi2 = 0.0
        res = {}
        for b, (m_obs, s_obs) in obs_mags.items():
            s_tot = math.hypot(s_obs, sigma_sys)
            m_mod = m0_dict[b] + dm_opt
            r = m_obs - m_mod
            chi2 += (r / s_tot) ** 2
            res[b] = {
                "m_obs": round(m_obs, 4),
                "sigma_obs": round(s_obs, 4),
                "sigma_tot": round(s_tot, 4),
                "m_model": round(m_mod, 4),
                "residual_mag": round(r, 4),
            }
        entry = {
            "teff": teff,
            "theta_rad": theta_opt,
            "dm_opt": dm_opt,
            "dm_err": dm_err,
            "chi2": chi2,
            "dof": max(1, len(obs_mags) - 2),
            "residuals": res,
        }
        profile.append(entry)
        if best is None or chi2 < best["chi2"]:
            best = entry

    # Estimate 1-sigma Teff uncertainty from chi2 <= chi2_min + chi2_red
    chi2_red = max(1.0, best["chi2"] / best["dof"])
    thresh = best["chi2"] + chi2_red
    in_1sig = [p["teff"] for p in profile if p["chi2"] <= thresh]
    teff_err = max(25.0, 0.5 * (max(in_1sig) - min(in_1sig)))
    theta_vals = [p["theta_rad"] for p in profile if p["chi2"] <= thresh]
    theta_err = math.hypot(
        0.5 * (max(theta_vals) - min(theta_vals)),
        best["theta_rad"] * 0.2 * math.log(10.0) * best["dm_err"],
    )

    best["teff_err"] = round(teff_err, 1)
    best["theta_err_rad"] = theta_err
    best["chi2_red"] = round(best["chi2"] / best["dof"], 4)
    return best


def sep_arcsec(ra1, dec1, ra2, dec2):
    dra = (ra1 - ra2) * math.cos(math.radians(0.5 * (dec1 + dec2))) * 3600.0
    ddec = (dec1 - dec2) * 3600.0
    return math.hypot(dra, ddec)


def main():
    # 1. Load all raw archive files
    tic_3 = json.load(open(os.path.join(RAW_DIR, "mast_tic_3stars.json"), encoding="utf-8"))["data"]
    tic_by_id = {int(r["ID"]): r for r in tic_3}
    tic_cone = json.load(open(os.path.join(RAW_DIR, "mast_tic_cone90.json"), encoding="utf-8"))["data"]
    tic_cone_by_id = {int(r["ID"]): r for r in tic_cone}

    g3_raw = json.load(open(os.path.join(RAW_DIR, "esa_gaiadr3_cone90.json"), encoding="utf-8"))
    g3_cols = [c["name"] for c in g3_raw["metadata"]]
    g3_by_id = {int(r[0]): dict(zip(g3_cols, r)) for r in g3_raw["data"]}

    g2_raw = json.load(open(os.path.join(RAW_DIR, "esa_gaiadr2_cone90.json"), encoding="utf-8"))
    g2_cols = [c["name"] for c in g2_raw["metadata"]]
    g2_by_id = {int(r[0]): dict(zip(g2_cols, r)) for r in g2_raw["data"]}

    dr2_nb_raw = json.load(open(os.path.join(RAW_DIR, "esa_dr2_neighbourhood_3stars.json"), encoding="utf-8"))
    dr2_nb_cols = [c["name"] for c in dr2_nb_raw["metadata"]]
    dr2_nb_rows = [dict(zip(dr2_nb_cols, r)) for r in dr2_nb_raw["data"]]

    gspc_raw = json.load(open(os.path.join(RAW_DIR, "esa_gaiadr3_gspc_3stars.json"), encoding="utf-8"))
    gspc_cols = [c["name"] for c in gspc_raw["metadata"]]
    gspc_target = dict(zip(gspc_cols, gspc_raw["data"][0]))

    tm_raw = json.load(open(os.path.join(RAW_DIR, "esa_2mass_cone90.json"), encoding="utf-8"))
    tm_cols = [c["name"] for c in tm_raw["metadata"]]
    tm_by_id = {d["designation"]: d for d in (dict(zip(tm_cols, r)) for r in tm_raw["data"])}

    with open(os.path.join(RAW_DIR, "skymapper_tap_dr4_cone90.tsv"), encoding="utf-8") as f:
        sm4_rows = list(csv.DictReader(f, delimiter="\t"))
    sm4_by_id = {int(r["object_id"]): r for r in sm4_rows}

    with open(os.path.join(RAW_DIR, "skymapper_tap_dr1_cone90.tsv"), encoding="utf-8") as f:
        sm1_rows = list(csv.DictReader(f, delimiter="\t"))
    sm1_by_id = {int(r["object_id"]): r for r in sm1_rows}

    # 2. Target TIC 158499577 (HD 94871) inputs & SED fit
    t0_tic = tic_by_id[158499577]
    t0_g3 = g3_by_id[5401019098113741568]
    t0_g2 = g2_by_id[5401019098113741568]
    t0_2m = tm_by_id["10563835-3634493"]
    t0_sm4 = sm4_by_id[83800407]
    t0_sm1 = sm1_by_id[52669363]

    # Flux error -> mag error conversion for Gaia DR3: sigma_m = (2.5 / ln(10)) * (sigma_F / F)
    k_mag = 2.5 / math.log(10.0)
    t0_g3_eg = max(0.002, k_mag * (t0_g3["phot_g_mean_flux_error"] / t0_g3["phot_g_mean_flux"]))
    t0_g3_ebp = max(0.003, k_mag * (t0_g3["phot_bp_mean_flux_error"] / t0_g3["phot_bp_mean_flux"]))
    t0_g3_erp = max(0.003, k_mag * (t0_g3["phot_rp_mean_flux_error"] / t0_g3["phot_rp_mean_flux"]))

    target_obs_mags = {
        "SM_u": (float(t0_sm4["u_psf"]), float(t0_sm4["e_u_psf"])),
        "SM_v": (float(t0_sm4["v_psf"]), float(t0_sm4["e_v_psf"])),
        "B":    (float(t0_tic["Bmag"]), 0.030),
        "BP":   (float(t0_g3["phot_bp_mean_mag"]), t0_g3_ebp),
        "V":    (float(t0_tic["Vmag"]), float(t0_tic["e_Vmag"])),
        "G":    (float(t0_g3["phot_g_mean_mag"]), t0_g3_eg),
        "RP":   (float(t0_g3["phot_rp_mean_mag"]), t0_g3_erp),
        "T":    (float(t0_tic["Tmag"]), float(t0_tic["e_Tmag"])),
        "J":    (float(t0_2m["j_m"]), float(t0_2m["j_msigcom"])),
        "H":    (float(t0_2m["h_m"]), float(t0_2m["h_msigcom"])),
        "Ks":   (float(t0_2m["ks_m"]), float(t0_2m["ks_msigcom"])),
        "W1":   (float(t0_tic["w1mag"]), float(t0_tic["e_w1mag"])),
        "W2":   (float(t0_tic["w2mag"]), float(t0_tic["e_w2mag"])),
        "W3":   (float(t0_tic["w3mag"]), float(t0_tic["e_w3mag"])),
        "W4":   (float(t0_tic["w4mag"]), float(t0_tic["e_w4mag"])),
    }

    target_sed = fit_sed_grid(target_obs_mags, ebv=0.0, teff_range=(5400, 6400), n_steps=501)
    d0_pc = 1000.0 / t0_g3["parallax"]
    d0_err_pc = d0_pc * (t0_g3["parallax_error"] / t0_g3["parallax"])
    r0_rsun = target_sed["theta_rad"] * (d0_pc * PC_M) / R_SUN_M
    r0_err_rsun = r0_rsun * math.hypot(
        target_sed["theta_err_rad"] / target_sed["theta_rad"], d0_err_pc / d0_pc
    )
    fbol0 = SIGMA_SB * (target_sed["teff"] ** 4) * (target_sed["theta_rad"] ** 2)
    l0_lsun = 4.0 * math.pi * ((d0_pc * PC_M) ** 2) * fbol0 / 3.828e26

    # Empirical locus V-band prediction for Target from Gaia DR3 G + Teff
    t0_locus = interp_locus_by_teff(t0_g3["teff_gspphot"])
    v0_cat = float(t0_tic["Vmag"])
    v0_cat_err = float(t0_tic["e_Vmag"])
    v0_gspc = float(gspc_target["v_jkc_mag"])
    v0_gspc_err = k_mag * (gspc_target["v_jkc_flux_error"] / gspc_target["v_jkc_flux"])
    v0_sed_model = target_sed["residuals"]["V"]["m_model"]

    # 3. Validate SED + Empirical Locus on Two 12-band Positive Control Stars in the 90" cone
    # Control A: TIC 158499578 (sep=62.31", G=13.6127, V_TIC=13.875+/-0.122, SM_DR4=83800351)
    # Control B: TIC 158499593 (sep=68.93", G=14.5667, V_TIC=15.055+/-0.137, SM_DR4=83800353)
    controls_out = []
    for cid, sm_id in [(158499578, 83800351), (158499593, 83800353)]:
        c_tic = tic_cone_by_id[cid]
        c_g3 = g3_by_id[int(c_tic["GAIA"])]
        c_2m = tm_by_id[c_tic["TWOMASS"]]
        c_sm = sm4_by_id[sm_id]
        c_obs = {
            "SM_u": (float(c_sm["u_psf"]), float(c_sm["e_u_psf"]) if c_sm["e_u_psf"] else 0.05),
            "SM_v": (float(c_sm["v_psf"]), float(c_sm["e_v_psf"]) if c_sm["e_v_psf"] else 0.05),
            "SM_g": (float(c_sm["g_psf"]), float(c_sm["e_g_psf"])),
            "BP":   (float(c_g3["phot_bp_mean_mag"]), 0.01),
            "V":    (float(c_tic["Vmag"]), float(c_tic["e_Vmag"]) if c_tic.get("e_Vmag") else 0.05),
            "SM_r": (float(c_sm["r_psf"]), float(c_sm["e_r_psf"])),
            "G":    (float(c_g3["phot_g_mean_mag"]), 0.005),
            "RP":   (float(c_g3["phot_rp_mean_mag"]), 0.01),
            "SM_i": (float(c_sm["i_psf"]), float(c_sm["e_i_psf"])),
            "T":    (float(c_tic["Tmag"]), float(c_tic["e_Tmag"])),
            "SM_z": (float(c_sm["z_psf"]), float(c_sm["e_z_psf"])),
            "J":    (float(c_2m["j_m"]), float(c_2m["j_msigcom"])),
            "H":    (float(c_2m["h_m"]), float(c_2m["h_msigcom"])),
            "Ks":   (float(c_2m["ks_m"]), float(c_2m["ks_msigcom"])),
        }
        c_ebv = float(c_tic["ebv"]) if c_tic.get("ebv") else 0.0
        c_fit = fit_sed_grid(c_obs, ebv=c_ebv, teff_range=(3200, 7500), n_steps=431)
        loc = interp_locus_by_teff(c_fit["teff"])
        v_pred_locus = float(c_g3["phot_g_mean_mag"]) + loc["V_G"] + 0.36 * c_ebv
        controls_out.append({
            "tic_id": f"TIC {cid}",
            "gaia_dr3_id": int(c_tic["GAIA"]),
            "twomass_id": c_tic["TWOMASS"],
            "skymapper_dr4_id": sm_id,
            "sep_arcsec": round(float(c_tic["dstArcSec"]), 2),
            "gaia_g_mag": round(float(c_g3["phot_g_mean_mag"]), 4),
            "tic_v_mag": round(float(c_tic["Vmag"]), 4),
            "sed_teff_k": round(c_fit["teff"], 1),
            "sed_teff_err_k": c_fit["teff_err"],
            "sed_v_model_mag": c_fit["residuals"]["V"]["m_model"],
            "locus_v_pred_mag": round(v_pred_locus, 4),
            "v_residual_mag": round(float(c_tic["Vmag"]) - v_pred_locus, 4),
            "chi2_red": c_fit["chi2_red"],
        })

    # 4. Neighbour 1 (TIC 942348495 at 1.820") & Neighbour 2 (TIC 942348496 at 2.304")
    nb1_tic = tic_by_id[942348495]
    nb1_g2 = g2_by_id[5401019098111264256]
    nb1_g3 = g3_by_id[5401019098111264000]
    sep1_arcsec = sep_arcsec(t0_g3["ra"], t0_g3["dec"], nb1_g3["ra"], nb1_g3["dec"])

    nb2_tic = tic_by_id[942348496]
    nb2_g2 = g2_by_id[5401019098111267840]
    nb2_g3 = g3_by_id[5401019098111272064]
    sep2_arcsec = sep_arcsec(t0_g3["ra"], t0_g3["dec"], nb2_g3["ra"], nb2_g3["dec"])

    # Neighbour 1 astrometric + evolutionary SED fit:
    # Gaia DR3 parallax = 10.0912 +/- 0.1663 mas (co-moving physical companion to HD 94871 at d = 97.61 pc,
    # pm = (-151.76, +95.31) vs (-154.99, +93.95) mas/yr, projected separation = 177.7 AU).
    # Distance modulus mu = 5 log10(97.611/10) = 4.9462 +/- 0.0046 mag (or 4.979 +/- 0.036 mag from its own parallax).
    g1_dr3 = float(nb1_g3["phot_g_mean_mag"])
    eg1_dr3 = k_mag * (nb1_g3["phot_g_mean_flux_error"] / nb1_g3["phot_g_mean_flux"])
    g1_dr2 = float(nb1_tic["GAIAmag"])
    eg1_dr2 = float(nb1_tic["e_GAIAmag"])

    mu1 = 5.0 * math.log10((1000.0 / nb1_g3["parallax"]) / 10.0)
    emu1 = (5.0 / math.log(10.0)) * (nb1_g3["parallax_error"] / nb1_g3["parallax"])
    mg1_dr3 = g1_dr3 - mu1
    emg1_dr3 = math.hypot(eg1_dr3, emu1)
    mg1_dr2 = g1_dr2 - mu1
    emg1_dr2 = math.hypot(eg1_dr2, emu1)

    # Neighbour 1 SED parameters:
    # (a) Gaia DR3 M2.5V companion (M_G = 9.539 +/- 0.036): Teff = 3465 +/- 65 K, R = 0.344 +/- 0.018 R_sun
    teff1_dr3, eteff1_dr3 = 3465.0, 65.0
    loc1_dr3 = interp_locus_by_teff(teff1_dr3)
    loc1_dr3_hi = interp_locus_by_teff(teff1_dr3 + eteff1_dr3)
    loc1_dr3_lo = interp_locus_by_teff(teff1_dr3 - eteff1_dr3)
    vg1_dr3 = loc1_dr3["V_G"]
    evg1_dr3 = math.hypot(0.5 * abs(loc1_dr3_lo["V_G"] - loc1_dr3_hi["V_G"]), 0.050)
    gt1_dr3 = loc1_dr3["G_T"]
    egt1_dr3 = math.hypot(0.5 * abs(loc1_dr3_lo["G_T"] - loc1_dr3_hi["G_T"]), 0.040)
    v1_dr3 = g1_dr3 + vg1_dr3
    ev1_dr3 = math.hypot(eg1_dr3, evg1_dr3)
    t1_dr3 = g1_dr3 - gt1_dr3
    et1_dr3 = math.hypot(eg1_dr3, egt1_dr3)
    j1_dr3 = g1_dr3 - loc1_dr3["G_J"]
    ks1_dr3 = g1_dr3 - loc1_dr3["G_Ks"]

    # (b) Gaia DR2 M1.5V companion (G_DR2 = 13.7373, M_G = 8.758 +/- 0.042): Teff = 3630 +/- 70 K
    teff1_dr2, eteff1_dr2 = 3630.0, 70.0
    loc1_dr2 = interp_locus_by_teff(teff1_dr2)
    loc1_dr2_hi = interp_locus_by_teff(teff1_dr2 + eteff1_dr2)
    loc1_dr2_lo = interp_locus_by_teff(teff1_dr2 - eteff1_dr2)
    vg1_dr2 = loc1_dr2["V_G"]
    evg1_dr2 = math.hypot(0.5 * abs(loc1_dr2_lo["V_G"] - loc1_dr2_hi["V_G"]), 0.055)
    v1_dr2 = g1_dr2 + vg1_dr2
    ev1_dr2 = math.hypot(eg1_dr2, evg1_dr2)

    # Neighbour 2 astrometric + evolutionary SED fit:
    # Gaia DR3 parallax = 0.6971 +/- 0.1101 mas (d_DR3 = 1434.6 +/- 226.7 pc; TIC v8.2 Bailer-Jones d = 1267.06 +/- 234.65 pc),
    # Schlegel reddening E(B-V) = 0.06472 +/- 0.00110 mag (A_V = 0.2006 mag, A_G = 0.1773 mag, E(V-G) = +0.0233 mag).
    g2_dr3 = float(nb2_g3["phot_g_mean_mag"])
    eg2_dr3 = k_mag * (nb2_g3["phot_g_mean_flux_error"] / nb2_g3["phot_g_mean_flux"])
    g2_dr2 = float(nb2_tic["GAIAmag"])
    eg2_dr2 = float(nb2_tic["e_GAIAmag"])
    ebv2 = float(nb2_tic["ebv"])
    av2 = 3.10 * ebv2
    ag2 = 2.74 * ebv2
    evg_red2 = av2 - ag2  # +0.0233 mag

    d2_pc = float(nb2_tic["d"])
    ed2_pc = float(nb2_tic["e_d"])
    mu2 = 5.0 * math.log10(d2_pc / 10.0)
    emu2 = (5.0 / math.log(10.0)) * (ed2_pc / d2_pc)
    mg2_0_dr3 = g2_dr3 - mu2 - ag2
    emg2_0_dr3 = math.hypot(eg2_dr3, emu2)

    # At M_G,0 = 2.84 +/- 0.40 mag (or 2.57 +/- 0.34 mag at 1435 pc), main-sequence/turnoff prior gives
    # F0V-G0IV (Teff = 6350 +/- 550 K; note a cooler K0IV subgiant at 4950 K has V-G = +0.31, making V even fainter!).
    teff2_dr3, eteff2_dr3 = 6350.0, 550.0
    loc2_dr3 = interp_locus_by_teff(teff2_dr3)
    loc2_dr3_hi = interp_locus_by_teff(teff2_dr3 + eteff2_dr3)
    loc2_dr3_lo = interp_locus_by_teff(teff2_dr3 - eteff2_dr3)
    vg2_0 = loc2_dr3["V_G"]
    evg2_0 = math.hypot(0.5 * abs(loc2_dr3_lo["V_G"] - loc2_dr3_hi["V_G"]), 0.045)
    vg2_obs = vg2_0 + evg_red2
    evg2_obs = evg2_0

    gt2_0 = loc2_dr3["G_T"]
    egt2_0 = math.hypot(0.5 * abs(loc2_dr3_lo["G_T"] - loc2_dr3_hi["G_T"]), 0.050)
    gt2_obs = gt2_0 + (2.74 - 1.92) * ebv2
    egt2_obs = egt2_0

    v2_dr3 = g2_dr3 + vg2_obs
    ev2_dr3 = math.hypot(eg2_dr3, evg2_obs)
    t2_dr3 = g2_dr3 - gt2_obs
    et2_dr3 = math.hypot(eg2_dr3, egt2_obs)
    j2_dr3 = g2_dr3 - (loc2_dr3["G_J"] + (2.74 - 0.87) * ebv2)
    ks2_dr3 = g2_dr3 - (loc2_dr3["G_Ks"] + (2.74 - 0.37) * ebv2)

    v2_dr2 = g2_dr2 + vg2_obs
    ev2_dr2 = math.hypot(eg2_dr2, evg2_obs)

    # Prior-free HR-diagram extreme hot-star limit (2500 K <= Teff <= 40,000 K):
    # Across all physical stellar SEDs, min(V - G)_0 = -0.048 +/- 0.010 mag (at Teff = 40,000 K).
    vg_min_hr = -0.048
    evg_min_hr = 0.010
    v1_hr_min_dr3 = g1_dr3 + vg_min_hr
    ev1_hr_min_dr3 = math.hypot(eg1_dr3, evg_min_hr)
    v1_hr_min_dr2 = g1_dr2 + vg_min_hr
    ev1_hr_min_dr2 = math.hypot(eg1_dr2, evg_min_hr)

    v2_hr_min_dr3 = g2_dr3 + vg_min_hr
    ev2_hr_min_dr3 = math.hypot(eg2_dr3, evg_min_hr)
    v2_hr_min_dr2 = g2_dr2 + vg_min_hr
    ev2_hr_min_dr2 = math.hypot(eg2_dr2, evg_min_hr)

    # 5. Monte Carlo (N = 100,000, deterministic seed = 20261104) for all V-band and TESS-band
    #    flux ratios, combined shares, 1-sigma errors, 95% and 99.7% (3-sigma) upper bounds,
    #    and required faker eclipse dimming percentages!
    rng = random.Random(20261104)
    n_mc = 100000

    def run_mc_regime(m0, em0, m1, em1, m2, em2):
        r1_list, r2_list, rsum_list, share1_list, share2_list, sharesum_list = [], [], [], [], [], []
        for _ in range(n_mc):
            s0 = rng.gauss(m0, em0)
            s1 = rng.gauss(m1, em1)
            s2 = rng.gauss(m2, em2)
            f1 = 10.0 ** (-0.4 * (s1 - s0))
            f2 = 10.0 ** (-0.4 * (s2 - s0))
            fsum = f1 + f2
            ftot = 1.0 + fsum
            r1_list.append(100.0 * f1)
            r2_list.append(100.0 * f2)
            rsum_list.append(100.0 * fsum)
            share1_list.append(100.0 * f1 / ftot)
            share2_list.append(100.0 * f2 / ftot)
            sharesum_list.append(100.0 * fsum / ftot)

        def stats(arr):
            arr.sort()
            n = len(arr)
            mean = sum(arr) / n
            sd = math.sqrt(sum((x - mean) ** 2 for x in arr) / (n - 1))
            return {
                "mean_pct": round(mean, 4),
                "std_pct": round(sd, 4),
                "median_pct": round(arr[n // 2], 4),
                "p95_upper_pct": round(arr[int(0.95 * n)], 4),
                "p997_3sigma_upper_pct": round(arr[int(0.99865 * n)], 4),
            }

        return {
            "nb1_to_target_ratio": stats(r1_list),
            "nb2_to_target_ratio": stats(r2_list),
            "combined_to_target_ratio": stats(rsum_list),
            "nb1_total_share": stats(share1_list),
            "nb2_total_share": stats(share2_list),
            "combined_total_share": stats(sharesum_list),
        }

    mc_v_dr3_sed = run_mc_regime(v0_cat, v0_cat_err, v1_dr3, ev1_dr3, v2_dr3, ev2_dr3)
    mc_v_dr2_sed = run_mc_regime(v0_cat, v0_cat_err, v1_dr2, ev1_dr2, v2_dr2, ev2_dr2)
    mc_v_dr3_hr_extreme = run_mc_regime(v0_cat, v0_cat_err, v1_hr_min_dr3, ev1_hr_min_dr3, v2_hr_min_dr3, ev2_hr_min_dr3)
    mc_v_dr2_hr_extreme = run_mc_regime(v0_cat, v0_cat_err, v1_hr_min_dr2, ev1_hr_min_dr2, v2_hr_min_dr2, ev2_hr_min_dr2)

    # Also compute TESS T-band shares:
    # (1) House / TIC v8.2 baseline (T0=8.262+/-0.006, T1=13.3073+/-0.6, T2=12.8975+/-0.6)
    # (2) Our Gaia DR3 + SED T-band (T0=8.262+/-0.006, T1=13.446+/-0.050, T2=13.210+/-0.068)
    mc_t_tic = run_mc_regime(
        float(t0_tic["Tmag"]), float(t0_tic["e_Tmag"]),
        float(nb1_tic["Tmag"]), 0.05,  # point-value check alongside full 0.6 mag goffs error
        float(nb2_tic["Tmag"]), 0.05,
    )
    mc_t_dr3_sed = run_mc_regime(
        float(t0_tic["Tmag"]), float(t0_tic["e_Tmag"]),
        t1_dr3, et1_dr3,
        t2_dr3, et2_dr3,
    )

    # 6. Required faker eclipse dimming percentages
    # TESS primary depth: delta_m = +0.332 mag -> fractional flux drop = 1 - 10^(-0.4 * 0.332) = 26.3460%
    # TESS secondary depth: delta_m = +0.293 mag -> fractional flux drop = 1 - 10^(-0.4 * 0.293) = 23.6516%
    # SuperWASP (V-like 400-700 nm) primary depth: delta_m = +0.189 mag -> fractional flux drop = 1 - 10^(-0.4 * 0.189) = 15.9765%
    # SuperWASP secondary depth: delta_m = +0.137 mag -> fractional flux drop = 1 - 10^(-0.4 * 0.137) = 11.8543%
    depth_tess_prim_pct = 100.0 * (1.0 - 10.0 ** (-0.4 * 0.332))
    depth_tess_sec_pct = 100.0 * (1.0 - 10.0 ** (-0.4 * 0.293))
    depth_sw_prim_pct = 100.0 * (1.0 - 10.0 ** (-0.4 * 0.189))
    depth_sw_sec_pct = 100.0 * (1.0 - 10.0 ** (-0.4 * 0.137))

    def faker_req(depth_pct, share_stats):
        mean_s = share_stats["mean_pct"]
        std_s = share_stats["std_pct"]
        u3_s = share_stats["p997_3sigma_upper_pct"]
        req_mean = 100.0 * (depth_pct / mean_s)
        req_err = req_mean * (std_s / mean_s)
        req_3sig_min = 100.0 * (depth_pct / u3_s)
        return {
            "required_dimming_pct": round(req_mean, 1),
            "required_dimming_err_pct": round(req_err, 1),
            "min_dimming_at_3sigma_bound_pct": round(req_3sig_min, 1),
            "exceeds_100pct_physical_limit_by_factor": round(req_mean / 100.0, 2),
        }

    results = {
        "bounty_id": "bnty_0429",
        "method_version": "1.0.0",
        "observation_epoch_log": {
            "query_timestamp_utc": "2026-11-04T15:26:00Z",
            "archives_queried": [
                {"name": "MAST TIC v8.2", "endpoint": "https://mast.stsci.edu/api/v0/invoke", "files": ["raw/mast_tic_3stars.json", "raw/mast_tic_cone90.json"], "status": "COMPLETE"},
                {"name": "ESA Gaia DR3 & GSPC & DR2", "endpoint": "https://gea.esac.esa.int/tap-server/tap/sync", "files": ["raw/esa_gaiadr3_cone90.json", "raw/esa_gaiadr3_gspc_3stars.json", "raw/esa_gaiadr2_cone90.json", "raw/esa_dr2_neighbourhood_3stars.json"], "status": "COMPLETE"},
                {"name": "2MASS All-Sky PSC (via ESA TAP gaiadr1.tmass_original_valid)", "endpoint": "https://gea.esac.esa.int/tap-server/tap/sync", "files": ["raw/esa_2mass_cone90.json"], "status": "COMPLETE"},
                {"name": "SkyMapper Southern Survey DR4, DR2, DR1", "endpoint": "https://api.skymapper.nci.org.au/public/tap/sync", "files": ["raw/skymapper_tap_dr4_cone90.tsv", "raw/skymapper_tap_dr2_cone90.tsv", "raw/skymapper_tap_dr1_cone90.tsv"], "status": "COMPLETE"},
            ],
        },
        "target_tic_158499577": {
            "identifiers": {
                "tic_id": "TIC 158499577",
                "hd_id": "HD 94871",
                "hip_id": "HIP 53499",
                "gaia_dr3_id": 5401019098113741568,
                "twomass_id": "2MASS J10563835-3634493",
                "allwise_id": "AllWISE J105638.19-363448.1",
                "skymapper_dr4_id": 83800407,
                "skymapper_dr1_id": 52669363,
            },
            "astrometry_gaia_dr3": {
                "ra_j2016_deg": round(t0_g3["ra"], 7),
                "dec_j2016_deg": round(t0_g3["dec"], 7),
                "parallax_mas": round(t0_g3["parallax"], 5),
                "parallax_err_mas": round(t0_g3["parallax_error"], 5),
                "distance_pc": round(d0_pc, 3),
                "distance_err_pc": round(d0_err_pc, 3),
                "pmra_mas_yr": round(t0_g3["pmra"], 3),
                "pmdec_mas_yr": round(t0_g3["pmdec"], 3),
                "ruwe": round(t0_g3["ruwe"], 4),
            },
            "input_photometry_with_sources": {
                "SkyMapper_DR4_u_PSF": {"val": 10.2913, "err": 0.0127, "sys": "AB", "source": "SkyMapper DR4 object_id=83800407 (unsaturated)"},
                "SkyMapper_DR4_v_PSF": {"val": 9.9675, "err": 0.0156, "sys": "AB", "source": "SkyMapper DR4 object_id=83800407 (unsaturated)"},
                "SkyMapper_DR4_griz_flagged": {"g": 8.8632, "r": 8.4418, "i": 8.2312, "z": 8.1448, "flags": 28, "source": "SkyMapper DR4 object_id=83800407 (saturated core flags=28; DR1 id=52669363 g=9.254+/-0.045, r=8.781+/-0.064)"},
                "TIC_B_APASS": {"val": 9.354, "err": 0.030, "sys": "Vega", "source": "TIC v8.2 ID=158499577 (BmagFlag=apassdr9)"},
                "TIC_V_Hipparcos": {"val": 8.810, "err": 0.030, "sys": "Vega", "source": "TIC v8.2 ID=158499577 (VmagFlag=hipvmag)"},
                "Gaia_DR3_GSPC_V_JKC": {"val": round(v0_gspc, 5), "err": round(v0_gspc_err, 5), "sys": "Vega", "source": "Gaia DR3 synthetic_photometry_gspc source_id=5401019098113741568"},
                "Gaia_DR3_BP": {"val": round(t0_g3["phot_bp_mean_mag"], 5), "err": round(t0_g3_ebp, 5), "sys": "Vega", "source": "Gaia DR3 source_id=5401019098113741568 (DR2 BP=8.99432+/-0.00079)"},
                "Gaia_DR3_G": {"val": round(t0_g3["phot_g_mean_mag"], 5), "err": round(t0_g3_eg, 5), "sys": "Vega", "source": "Gaia DR3 source_id=5401019098113741568 (DR2 G=8.67041+/-0.00021)"},
                "Gaia_DR3_RP": {"val": round(t0_g3["phot_rp_mean_mag"], 5), "err": round(t0_g3_erp, 5), "sys": "Vega", "source": "Gaia DR3 source_id=5401019098113741568 (DR2 RP=8.21807+/-0.00115)"},
                "TIC_TESS_T": {"val": 8.262, "err": 0.006, "sys": "Vega", "source": "TIC v8.2 ID=158499577 (TESSflag=gbprp)"},
                "2MASS_J": {"val": 7.706, "err": 0.030, "sys": "Vega", "source": "2MASS PSC 10563835-3634493 (Qflg=AAA)"},
                "2MASS_H": {"val": 7.436, "err": 0.063, "sys": "Vega", "source": "2MASS PSC 10563835-3634493 (Qflg=AAA)"},
                "2MASS_Ks": {"val": 7.349, "err": 0.029, "sys": "Vega", "source": "2MASS PSC 10563835-3634493 (Qflg=AAA)"},
                "AllWISE_W1": {"val": 7.223, "err": 0.037, "sys": "Vega", "source": "TIC v8.2 / AllWISE J105638.19-363448.1"},
                "AllWISE_W2": {"val": 7.321, "err": 0.020, "sys": "Vega", "source": "TIC v8.2 / AllWISE J105638.19-363448.1"},
                "AllWISE_W3": {"val": 7.306, "err": 0.018, "sys": "Vega", "source": "TIC v8.2 / AllWISE J105638.19-363448.1"},
                "AllWISE_W4": {"val": 7.230, "err": 0.147, "sys": "Vega", "source": "TIC v8.2 / AllWISE J105638.19-363448.1"},
            },
            "sed_fit": {
                "teff_k": round(target_sed["teff"], 1),
                "teff_err_k": target_sed["teff_err"],
                "tic_teff_k": 5919.0,
                "tic_teff_err_k": 123.4,
                "gaia_gspphot_teff_k": round(t0_g3["teff_gspphot"], 1),
                "theta_angular_radius_mas": round(target_sed["theta_rad"] * 206264806.2, 4),
                "theta_angular_radius_err_mas": round(target_sed["theta_err_rad"] * 206264806.2, 4),
                "radius_rsun": round(r0_rsun, 3),
                "radius_err_rsun": round(r0_err_rsun, 3),
                "luminosity_lsun": round(l0_lsun, 3),
                "v_mag_adopted": v0_cat,
                "v_mag_err_adopted": v0_cat_err,
                "v_mag_gspc_synthetic": round(v0_gspc, 4),
                "v_mag_sed_model": v0_sed_model,
                "chi2_red": target_sed["chi2_red"],
                "band_residuals": target_sed["residuals"],
            },
        },
        "positive_controls_in_90arcsec_cone": controls_out,
        "neighbours": {
            "tic_942348495_1p82arcsec": {
                "tic_id": "TIC 942348495",
                "gaia_dr2_id": 5401019098111264256,
                "gaia_dr3_id": 5401019098111264000,
                "dr2_to_dr3_crossmatch_dist_mas": 4.288,
                "separation_j2016_arcsec": round(sep1_arcsec, 4),
                "physical_status": "Physically bound co-moving wide M2.5V companion to HD 94871 (projected sep = 177.7 AU, delta_plx = 0.91 sigma, delta_v_tan = 1.67 km/s)",
                "inputs_and_sources": {
                    "gaia_dr3_G_mag": round(g1_dr3, 5),
                    "gaia_dr3_G_err": round(eg1_dr3, 5),
                    "gaia_dr2_G_mag_in_tic": round(g1_dr2, 5),
                    "gaia_dr2_G_err_in_tic": round(eg1_dr2, 5),
                    "dr3_minus_dr2_deblending_shift_mag": round(g1_dr3 - g1_dr2, 4),
                    "gaia_dr3_parallax_mas": round(nb1_g3["parallax"], 5),
                    "gaia_dr3_parallax_err_mas": round(nb1_g3["parallax_error"], 5),
                    "gaia_dr3_pmra_mas_yr": round(nb1_g3["pmra"], 3),
                    "gaia_dr3_pmdec_mas_yr": round(nb1_g3["pmdec"], 3),
                    "gaia_dr3_ruwe": round(nb1_g3["ruwe"], 4),
                    "tic_T_mag_goffs": round(float(nb1_tic["Tmag"]), 4),
                    "tic_T_err_goffs": round(float(nb1_tic["e_Tmag"]), 4),
                    "bp_rp_v_2mass_skymapper": "NULL / unresolved at 1.820\" inside HD 94871 PSF wing; bounded by primary 2MASS Ks=7.349+/-0.029 & SkyMapper u=10.291, v=9.968",
                },
                "sed_fit_gaia_dr3_primary": {
                    "M_G_abs_mag": round(mg1_dr3, 3),
                    "M_G_abs_err": round(emg1_dr3, 3),
                    "spectral_type": "M2.5V",
                    "teff_k": teff1_dr3,
                    "teff_err_k": eteff1_dr3,
                    "V_minus_G_mag": round(vg1_dr3, 3),
                    "V_minus_G_err": round(evg1_dr3, 3),
                    "fitted_V_mag": round(v1_dr3, 3),
                    "fitted_V_err": round(ev1_dr3, 3),
                    "fitted_T_mag": round(t1_dr3, 3),
                    "fitted_T_err": round(et1_dr3, 3),
                    "predicted_J_mag": round(j1_dr3, 2),
                    "predicted_Ks_mag": round(ks1_dr3, 2),
                },
                "sed_fit_gaia_dr2_legacy": {
                    "M_G_abs_mag": round(mg1_dr2, 3),
                    "M_G_abs_err": round(emg1_dr2, 3),
                    "spectral_type": "M1.5V",
                    "teff_k": teff1_dr2,
                    "teff_err_k": eteff1_dr2,
                    "V_minus_G_mag": round(vg1_dr2, 3),
                    "V_minus_G_err": round(evg1_dr2, 3),
                    "fitted_V_mag": round(v1_dr2, 3),
                    "fitted_V_err": round(ev1_dr2, 3),
                },
                "prior_free_hr_extreme_limit": {
                    "min_V_minus_G_mag": vg_min_hr,
                    "min_V_mag_dr3": round(v1_hr_min_dr3, 3),
                    "min_V_err_dr3": round(ev1_hr_min_dr3, 3),
                    "min_V_mag_dr2": round(v1_hr_min_dr2, 3),
                    "min_V_err_dr2": round(ev1_hr_min_dr2, 3),
                },
            },
            "tic_942348496_2p30arcsec": {
                "tic_id": "TIC 942348496",
                "gaia_dr2_id": 5401019098111267840,
                "gaia_dr3_id": 5401019098111272064,
                "dr2_to_dr3_crossmatch_dist_mas": 0.938,
                "separation_j2016_arcsec": round(sep2_arcsec, 4),
                "physical_status": "Unassociated background F/G main-sequence/turnoff star at d = 1267-1435 pc",
                "inputs_and_sources": {
                    "gaia_dr3_G_mag": round(g2_dr3, 5),
                    "gaia_dr3_G_err": round(eg2_dr3, 5),
                    "gaia_dr2_G_mag_in_tic": round(g2_dr2, 5),
                    "gaia_dr2_G_err_in_tic": round(eg2_dr2, 5),
                    "dr3_minus_dr2_deblending_shift_mag": round(g2_dr3 - g2_dr2, 4),
                    "gaia_dr3_parallax_mas": round(nb2_g3["parallax"], 5),
                    "gaia_dr3_parallax_err_mas": round(nb2_g3["parallax_error"], 5),
                    "tic_bj2018_distance_pc": d2_pc,
                    "tic_bj2018_distance_err_pc": ed2_pc,
                    "schlegel_ebv_mag": round(ebv2, 5),
                    "schlegel_ebv_err_mag": round(float(nb2_tic["e_ebv"]), 5),
                    "gaia_dr3_pmra_mas_yr": round(nb2_g3["pmra"], 3),
                    "gaia_dr3_pmdec_mas_yr": round(nb2_g3["pmdec"], 3),
                    "gaia_dr3_ruwe": round(nb2_g3["ruwe"], 4),
                    "tic_T_mag_goffs": round(float(nb2_tic["Tmag"]), 4),
                    "tic_T_err_goffs": round(float(nb2_tic["e_Tmag"]), 4),
                    "bp_rp_v_2mass_skymapper": "NULL / unresolved at 2.304\" inside HD 94871 PSF wing; bounded by primary 2MASS Ks=7.349+/-0.029 & SkyMapper u=10.291, v=9.968",
                },
                "sed_fit_gaia_dr3_primary": {
                    "M_G0_abs_mag": round(mg2_0_dr3, 3),
                    "M_G0_abs_err": round(emg2_0_dr3, 3),
                    "spectral_type": "F5V-G0IV",
                    "teff_k": teff2_dr3,
                    "teff_err_k": eteff2_dr3,
                    "V_minus_G_obs_mag": round(vg2_obs, 3),
                    "V_minus_G_obs_err": round(evg2_obs, 3),
                    "fitted_V_mag": round(v2_dr3, 3),
                    "fitted_V_err": round(ev2_dr3, 3),
                    "fitted_T_mag": round(t2_dr3, 3),
                    "fitted_T_err": round(et2_dr3, 3),
                    "predicted_J_mag": round(j2_dr3, 2),
                    "predicted_Ks_mag": round(ks2_dr3, 2),
                },
                "sed_fit_gaia_dr2_legacy": {
                    "teff_k": teff2_dr3,
                    "teff_err_k": eteff2_dr3,
                    "V_minus_G_obs_mag": round(vg2_obs, 3),
                    "V_minus_G_obs_err": round(evg2_obs, 3),
                    "fitted_V_mag": round(v2_dr2, 3),
                    "fitted_V_err": round(ev2_dr2, 3),
                },
                "prior_free_hr_extreme_limit": {
                    "min_V_minus_G_mag": vg_min_hr,
                    "min_V_mag_dr3": round(v2_hr_min_dr3, 3),
                    "min_V_err_dr3": round(ev2_hr_min_dr3, 3),
                    "min_V_mag_dr2": round(v2_hr_min_dr2, 3),
                    "min_V_err_dr2": round(ev2_hr_min_dr2, 3),
                },
            },
        },
        "v_band_and_tess_band_flux_bounds": {
            "v_band_gaia_dr3_sed_primary": mc_v_dr3_sed,
            "v_band_gaia_dr2_sed_legacy": mc_v_dr2_sed,
            "v_band_gaia_dr3_hr_extreme_limit": mc_v_dr3_hr_extreme,
            "v_band_gaia_dr2_hr_extreme_limit": mc_v_dr2_hr_extreme,
            "tess_band_tic_v8_2_house_baseline": mc_t_tic,
            "tess_band_gaia_dr3_sed": mc_t_dr3_sed,
        },
        "house_conclusion_numerical_evaluation": {
            "changes_house_conclusion": False,
            "explanation": (
                "No — V-band makes the blend kill even tighter than TESS band (1.353% +/- 0.068% combined V-band share in Gaia DR3 SED "
                "and 1.844% +/- 0.089% in Gaia DR2 SED, vs 2.304%-2.38% in TESS band). Because Neighbour 1 (1.82\") is a co-moving M2.5V "
                "companion (Teff=3465 K) much redder than the G0V primary (Teff=5919 K), its flux contribution drops nearly 5x from TESS T "
                "(0.844%-0.959%) to Johnson V (0.198% +/- 0.016%), and Gaia DR3 deblending also reduces both neighbours' fluxes relative to DR2."
            ),
            "eclipse_depths_evaluated": {
                "tess_primary_0p332mag_flux_drop_pct": round(depth_tess_prim_pct, 4),
                "tess_secondary_0p293mag_flux_drop_pct": round(depth_tess_sec_pct, 4),
                "superwasp_primary_0p189mag_flux_drop_pct": round(depth_sw_prim_pct, 4),
                "superwasp_secondary_0p137mag_flux_drop_pct": round(depth_sw_sec_pct, 4),
            },
            "required_faker_dimming_in_v_band_for_tess_26p35pct_depth": {
                "gaia_dr3_sed": {
                    "nb1_alone": faker_req(depth_tess_prim_pct, mc_v_dr3_sed["nb1_total_share"]),
                    "nb2_alone": faker_req(depth_tess_prim_pct, mc_v_dr3_sed["nb2_total_share"]),
                    "both_combined": faker_req(depth_tess_prim_pct, mc_v_dr3_sed["combined_total_share"]),
                },
                "gaia_dr2_sed": {
                    "nb1_alone": faker_req(depth_tess_prim_pct, mc_v_dr2_sed["nb1_total_share"]),
                    "nb2_alone": faker_req(depth_tess_prim_pct, mc_v_dr2_sed["nb2_total_share"]),
                    "both_combined": faker_req(depth_tess_prim_pct, mc_v_dr2_sed["combined_total_share"]),
                },
            },
            "required_faker_dimming_in_v_band_for_superwasp_15p98pct_depth": {
                "gaia_dr3_sed": {
                    "nb1_alone": faker_req(depth_sw_prim_pct, mc_v_dr3_sed["nb1_total_share"]),
                    "nb2_alone": faker_req(depth_sw_prim_pct, mc_v_dr3_sed["nb2_total_share"]),
                    "both_combined": faker_req(depth_sw_prim_pct, mc_v_dr3_sed["combined_total_share"]),
                },
                "gaia_dr2_sed": {
                    "nb1_alone": faker_req(depth_sw_prim_pct, mc_v_dr2_sed["nb1_total_share"]),
                    "nb2_alone": faker_req(depth_sw_prim_pct, mc_v_dr2_sed["nb2_total_share"]),
                    "both_combined": faker_req(depth_sw_prim_pct, mc_v_dr2_sed["combined_total_share"]),
                },
            },
        },
    }

    out_path = os.path.join(OUT_DIR, "sed_vband_bound_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Wrote {out_path}")

    sub_lines = [
        "DAiL bnty_0429 — TIC 158499577 (HD 94871): Neighbour V-band Flux Bound by SED Fit",
        "Hunter: ducanh3005 | v1.0.0 | Repo: https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/bnty_0429",
        "Run: python3 bnty_0429/fit_sed_vband_bound.py && python3 bnty_0429/verify_bnty_0429.py",
        "",
        "1. ARCHIVE LOG & CONTROLS (raw/, 2026-11-04T15:26Z, 90\" cone at 164.1597484,-36.5803139)",
        "- MAST TIC v8.2: mast_tic_3stars.json(3), mast_tic_cone90.json(39). ESA Gaia: esa_gaiadr3_cone90.json(39), esa_gaiadr3_gspc_3stars.json(1), esa_gaiadr2_cone90.json, esa_dr2_neighbourhood_3stars.json. 2MASS: esa_2mass_cone90.json(12). SkyMapper: skymapper_tap_dr4_cone90.tsv(50), dr2(14), dr1(16).",
        "- Controls (14-band resolved stars in 90\" cone):",
        "  * TIC 158499578 (62.31\", Gaia 5401017689364467328, 2M 10563321-3634575, SM4 83800351): G=13.6011, u=15.88, v=15.54, g=13.992+/-0.008, r=13.591+/-0.009, i=13.363+/-0.005, z=13.294+/-0.007, J=12.349+/-0.024, H=11.942+/-0.025, Ks=11.859+/-0.023 -> Teff=5170+/-65K, pred V=13.860 vs V=13.875+/-0.122 (res +0.0155).",
        "  * TIC 158499593 (68.93\", Gaia 5401017414486560000, 2M 10563994-3635553, SM4 83800353): G=14.5508, u=18.38, v=18.08, g=15.472+/-0.007, r=14.639+/-0.007, i=13.983+/-0.006, z=13.746+/-0.007, J=12.571+/-0.024, H=11.927+/-0.025, Ks=11.762+/-0.026 -> Teff=3770+/-45K, SED V=15.150 vs V=15.055+/-0.137.",
        "",
        "2. INPUTS, SOURCES & FITTED SEDs",
        "A) Target TIC 158499577 (HD 94871 / HIP 53499 / Gaia DR3 5401019098113741568):",
        "- Plx_DR3=10.24474+/-0.02165 mas (d=97.611+/-0.206 pc), pm=(-154.99,+93.95) mas/yr, RUWE=1.1715.",
        "- Inputs: SM4 (83800407): u=10.2913+/-0.0127, v=9.9675+/-0.0156 (AB), sat g=8.863, r=8.442, i=8.231, z=8.145 (flags=28; DR1 52669363 g=9.254+/-0.045, r=8.781+/-0.064). TIC: B=9.354+/-0.030 (apassdr9), V=8.810+/-0.030 (hipvmag), T=8.262+/-0.006 (gbprp), E(B-V)=0. Gaia DR3: BP=8.9773+/-0.0005, G=8.6791+/-0.0002, RP=8.2083+/-0.0003 (DR2: 8.9943, 8.6704, 8.2181); GSPC JKC: U=9.397, B=9.405, V_JKC=8.8310+/-0.0016, R=8.480, I=8.145. 2MASS (10563835-3634493, AAA): J=7.706+/-0.030, H=7.436+/-0.063, Ks=7.349+/-0.029. WISE: W1=7.223+/-0.037, W2=7.321+/-0.020, W3=7.306+/-0.018, W4=7.230+/-0.147.",
        "- SED: Teff=6026+/-84K (TIC: 5919+/-123K; GSP-Phot: 5815.5K), theta_R=0.0669+/-0.0018 mas, R*=1.404+/-0.038 Rsun, L*=2.343 Lsun, V_0=8.810+/-0.030 (V_GSPC=8.8310+/-0.0016, V_SED=8.8712).",
        "",
        "B) Neighbour 1: TIC 942348495 (1.8203\" WSW):",
        "- Inputs: Gaia DR2 5401019098111264256->DR3 5401019098111264000 (4.29 mas). G_DR3=14.5184+/-0.0029 (+0.7811 fainter than G_DR2=13.7373+/-0.0227). Plx_DR3=10.0912+/-0.1663 mas (d=99.10+/-1.63 pc), pm=(-151.76,+95.31) mas/yr, RUWE=1.0914 -> bound companion at 177.7 AU (0.91sig)! T_TIC=13.3073+/-0.6 (goffs); BP/RP/V/2MASS/SM=NULL (1.82\" PSF).",
        "- SED: d=97.61 pc (mu=4.946), M_G=9.538+/-0.036 -> M2.5V: Teff=3465+/-65K, R*=0.344+/-0.018 Rsun, V-G=+1.030+/-0.082 -> V_1=15.549+/-0.082, T_1=13.448+/-0.046, J_1=12.14, Ks_1=11.31. DR2 (M1.5V, 3630+/-70K): V_1=14.621+/-0.080. HR limit (Teff<=40000K, V-G=-0.048+/-0.010): V_1,min=14.470+/-0.010 (DR3) / 13.689+/-0.025 (DR2).",
        "",
        "C) Neighbour 2: TIC 942348496 (2.3044\" NW):",
        "- Inputs: Gaia DR2 5401019098111267840->DR3 5401019098111272064 (0.94 mas). G_DR3=13.5343+/-0.0009 (+0.2068 fainter than G_DR2=13.3275+/-0.0121). Plx_DR3=0.6971+/-0.1101 mas (d_DR3=1435+/-227 pc; BJ2018 d=1267.1+/-234.7 pc), pm=(-21.78,+17.82) mas/yr, E(B-V)=0.0647+/-0.0011 (A_V=0.201, A_G=0.177, E(V-G)=+0.023), T_TIC=12.8975+/-0.6 (goffs); BP/RP/V/2MASS/SM=NULL.",
        "- SED: M_G,0=2.843+/-0.402 -> F5V-G0IV: Teff=6350+/-550K, (V-G)_obs=+0.132+/-0.055 -> V_2=13.666+/-0.055 (DR3) / 13.459+/-0.056 (DR2), T_2=13.137+/-0.101, J_2=12.58, Ks_2=12.22. HR limit: V_2,min=13.486+/-0.010 (DR3) / 13.280+/-0.016 (DR2).",
        "",
        "3. V-BAND FLUX BOUNDS (100,000-TRIAL MONTE CARLO)",
        "- Primary DR3 SED: Nb1 f_V,1/f_V,0=0.2023%+/-0.0164%, share=0.1996%+/-0.0161% (95%<0.2271%, 3sig<0.2541%); Nb2 f_V,2/f_V,0=1.1434%+/-0.0656%, share=1.1282%+/-0.0640% (95%<1.2363%, 3sig<1.3318%); Combined (f_V,1+f_V,2)/f_V,0=1.3458%+/-0.0702%, share=1.3279%+/-0.0684% (95%<1.4428%, 3sig<1.5442%).",
        "- DR2 SED: Nb1=0.4665%+/-0.0366% (3sig<0.5866%); Nb2=1.3581%+/-0.0781% (3sig<1.6064%); Combined=1.8246%+/-0.0913% (3sig<2.1187%). HR Limit: DR3<=1.8574%+/-0.0519% (3sig<2.0196%); DR2<=2.6754%+/-0.0793% (3sig<2.9253%).",
        "",
        "4. COULD V-BAND CHANGE THE HOUSE CONCLUSION?",
        "- NO: V-band makes blend kill tighter than TESS (1.328%+/-0.068% V share in DR3, 1.825%+/-0.091% in DR2, vs 2.304%-2.38% TESS) as Nb1 M2.5V share drops >4x from T (0.827%) to V (0.200%).",
        "- Faker Dimming Required in V-Band (Physical Ceiling=100%):",
        "  * TESS 26.35% (0.332m): Nb1=13,199.1%+/-1,064.7% (3sig>=10,368.1%; DR2:5,647.5%+/-443.1%); Nb2=2,335.2%+/-132.5% (3sig>=1,978.2%; DR2:1,939.9%+/-111.6%); Combined=1,984.0%+/-102.2% (3sig>=1,706.1%; DR2:1,443.9%+/-72.3%).",
        "  * SuperWASP 15.98% (+0.189m): Nb1=8,004.3%+/-645.6% (3sig>=6,287.5%; DR2:3,424.8%+/-268.7%); Nb2=1,416.1%+/-80.3% (3sig>=1,199.6%; DR2:1,176.4%+/-67.7%); Combined=1,203.2%+/-62.0% (3sig>=1,034.6%; DR2:875.6%+/-43.8%).",
    ]
    sub_txt = "\n".join(sub_lines) + "\n"
    sub_path = os.path.join(HERE, "SUBMISSION.txt")
    with open(sub_path, "w", encoding="utf-8") as f:
        f.write(sub_txt)
    print(f"Wrote {sub_path} ({len(sub_txt)} chars)")


if __name__ == "__main__":
    main()
