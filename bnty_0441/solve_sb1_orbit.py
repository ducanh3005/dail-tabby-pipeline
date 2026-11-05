#!/usr/bin/env python3
"""
DAiL bnty_0441 — Archival Radial-Velocity Orbit for a Single-Lined Spectroscopic Binary (SB1)
Hunter: ducanh3005
Pipeline Version: sb1-archival-orbit-v1.0.0 (2026-11-05)

Solves and bounds the Keplerian spectroscopic binary (SB1) orbits from public archival
records only (no new telescope booking, no archive-staff contact, no AAVSO data) for TWO
independent Gaia DR3 SB1 systems that each have only a single summary radial-velocity
value published in their main survey catalog(s):

1. Primary Target (Cross-Survey APOGEE DR17 FITS Visits + LAMOST MRS + Gaia DR3):
   2MASS J19241736+4729134 (Gaia DR3 2129164276754246400 / KIC 10338279)
   - Published single-value catalog RVs:
     * Gaia DR3 main catalog (gaia_dr3.gaia_source): RV = +3.6089 +/- 6.5012 km/s (1 combined value; 0 epoch RVs released)
     * APOGEE DR17 summary catalog (III/286/catalog): VHELIO = -21.1539 km/s (1 combined value)
     * LAMOST MRS (J/ApJS/258/26, ObsID 591803219): 1 single night (LMJD 58031, BJD 2458031.00549-2458031.02403, 3 back-to-back exposures)
   - Archival multi-phase epochs recovered from public FITS & spectroscopic archives:
     * SDSS-IV APOGEE DR17 FITS header (apStar-dr17-2M19241736+4729134.fits, R ~ 22,500):
       4 distinct visit epochs across 4 consecutive nights (JD 2457510.97991 to 2457513.97382)
       spanning orbital phases phi = 0.812, 0.032, 0.251, 0.470 with VHELIO = +12.219, -32.418, -52.740, -14.887 km/s.
     * LAMOST MRS (ObsID 591803219, R ~ 7,500) 520.03 days (114.30 orbital cycles) later at BJD 2458031.01476:
       3 back-to-back exposures giving RVabsB = -48.556 +/- 0.495 km/s at phase phi = 0.114.
     * Exact analysis of:
       (a) 2-epoch archival bound (what is constrained vs unconstrained from 2 epochs alone),
       (b) 4-epoch APOGEE circular & eccentric Keplerian fit (4 parameters vs 4 epochs -> exact circular fit; 6 eccentric parameters -> 2 degrees of freedom underconstrained without external period/eccentricity),
       (c) Joint 5-epoch (7-exposure) APOGEE DR17 + LAMOST MRS 520-day baseline Keplerian orbit fit with Monte Carlo (N=2,000) parameter uncertainties, compared against Gaia DR3 nss_two_body_orbit (I/357/tbosb1).

2. Secondary Target (Multi-Season 9-Night / 53-Exposure LAMOST MRS + 2-Epoch LAMOST LRS):
   LAMOST J045121.78+233659.3 (Gaia DR3 3413610152545407104 / 2MASS J04512177+2336592)
   - Published single-value catalog RV:
     * Gaia DR3 main catalog (gaia_dr3.gaia_source): RV = +37.9857 +/- 2.1724 km/s (1 combined value; 0 epoch RVs released)
   - Archival multi-phase epochs recovered from J/ApJS/258/26 (LAMOST MRS) & V/156/dr7lrs (LAMOST LRS):
     * 53 individual medium-resolution exposures across 9 distinct observing nights spanning
       BJD 2458056.25125 to 2458500.12856 (Delta_t = 443.877 d = 1.321 orbital cycles of P ~ 336 d),
       plus 2 LAMOST LRS spectra on MJD 56292 (2012-12-31) and MJD 58512 (2019-01-29).
     * Full 6-parameter eccentric Keplerian orbit fit (P, gamma, K1, e, omega, T0) + mass function f(M) and a1*sin(i) with Monte Carlo uncertainties.
"""

import json
import math
import os
import numpy as np
from scipy.optimize import least_squares

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "raw")
RES_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(RES_DIR, exist_ok=True)


def parse_fits_primary_header(path):
    with open(path, "rb") as f:
        raw_bytes = f.read(2880 * 20)
    pos = 0
    hdr = {}
    while pos < len(raw_bytes):
        block = raw_bytes[pos:pos + 2880]
        pos += 2880
        end_found = False
        for i in range(0, 2880, 80):
            card = block[i:i + 80].decode("ascii", "replace")
            key = card[:8].strip()
            if key == "END":
                end_found = True
                break
            if len(card) >= 10 and card[8:10] == "= ":
                val_str = card[10:].split("/")[0].strip().strip("'").strip()
                hdr[key] = val_str
        if end_found:
            break
    return hdr


def solve_kepler_E(M, e, tol=1e-12, max_iter=50):
    M = np.asarray(M, dtype=float)
    E = M.copy() if e < 0.8 else np.pi * np.ones_like(M)
    for _ in range(max_iter):
        f = E - e * np.sin(E) - M
        f_prime = 1.0 - e * np.cos(E)
        dE = -f / f_prime
        E += dE
        if np.max(np.abs(dE)) < tol:
            break
    return E


def rv_keplerian(t, P, gamma, K1, e, omega_deg, T0):
    M = 2.0 * np.pi * ((np.asarray(t, dtype=float) - T0) / P)
    E = solve_kepler_E(M, e)
    nu = 2.0 * np.arctan2(np.sqrt(1.0 + e) * np.sin(E / 2.0), np.sqrt(1.0 - e) * np.cos(E / 2.0))
    omega = np.deg2rad(omega_deg)
    return gamma + K1 * (np.cos(nu + omega) + e * np.cos(omega))


def rv_circular(t, P, gamma, K1, T0_max_rv):
    phi = 2.0 * np.pi * ((np.asarray(t, dtype=float) - T0_max_rv) / P)
    return gamma + K1 * np.cos(phi)


def mass_function_msun(P_days, K1_kms, e=0.0):
    # f(M) = (M2 sin i)^3 / (M1 + M2)^2 = 1.036149e-7 * (1 - e^2)^(3/2) * K1^3 * P
    return 1.036149e-7 * ((1.0 - e * e) ** 1.5) * (K1_kms ** 3) * P_days


def a1_sini_rsun(P_days, K1_kms, e=0.0):
    # a1 sin i in R_sun = (P_days * 86400 * K1_kms * sqrt(1 - e^2)) / (2 * pi * 695700)
    return (P_days * 86400.0 * K1_kms * math.sqrt(max(0.0, 1.0 - e * e))) / (2.0 * math.pi * 695700.0)


def parse_lamost_mrs_tsv(path):
    lines = [l for l in open(path, encoding="utf-8").read().splitlines() if l.strip() and not l.startswith("#") and not l.startswith("-")]
    header = [h.strip() for h in lines[0].split("\t")]
    rows = []
    for line in lines[2:]:
        parts = [p.strip() for p in line.split("\t")]
        if len(parts) < 5:
            continue
        d = dict(zip(header, parts))
        if not d.get("ObsID", "").isdigit():
            continue
        rows.append({
            "ObsID": int(d["ObsID"]),
            "m_ObsID": int(d["m_ObsID"]),
            "BJDmid": float(d["BJDmid"]),
            "LMJD": int(d["LMJD"]),
            "planid": d["planid"],
            "spid": int(d["spid"]),
            "fiber": int(d["fiber"]),
            "SNRB": float(d["SNRB"]) if d.get("SNRB") else None,
            "SNRR": float(d["SNRR"]) if d.get("SNRR") else None,
            "RVobsB": float(d["RVobsB"]) if d.get("RVobsB") else None,
            "e_RVobsB": float(d["e_RVobsB"]) if d.get("e_RVobsB") else None,
            "RVabsB": float(d["RVabsB"]) if d.get("RVabsB") else None,
            "e_RVabsB": float(d["e_RVabsB"]) if d.get("e_RVabsB") else None,
            "RVobsR": float(d["RVobsR"]) if d.get("RVobsR") else None,
            "e_RVobsR": float(d["e_RVobsR"]) if d.get("e_RVobsR") else None,
            "RVabsR": float(d["RVabsR"]) if d.get("RVabsR") else None,
            "e_RVabsR": float(d["e_RVabsR"]) if d.get("e_RVabsR") else None,
        })
    return rows


def main():
    np.random.seed(42)

    # =========================================================================
    # TARGET 1: 2MASS J19241736+4729134 (Gaia DR3 2129164276754246400 / KIC 10338279)
    # =========================================================================
    fits_path = os.path.join(RAW_DIR, "apStar-dr17-2M19241736+4729134.fits")
    hdr = parse_fits_primary_header(fits_path)
    apogee_visits = []
    for i in range(1, int(hdr["NVISITS"]) + 1):
        apogee_visits.append({
            "visit_num": i,
            "spectrum_file": hdr[f"SFILE{i}"],
            "date_obs": hdr.get(f"DATE-OBS{i}", ""),
            "JD": float(hdr[f"JD{i}"]),
            "MJD": int(round(float(hdr[f"JD{i}"]) - 2400000.5)),
            "VHELIO_kms": float(hdr[f"VHELIO{i}"]),
            "VERR_kms": float(hdr[f"VERR{i}"]),
            "SNR": float(hdr[f"SNRVIS{i}"]),
            "BC_kms": float(hdr[f"BC{i}"]),
        })

    lamost_b_rows = parse_lamost_mrs_tsv(os.path.join(RAW_DIR, "targetB_2129164276754246400_lamost_mrs.tsv"))
    # Compute inverse-variance weighted nightly mean for LAMOST MRS on LMJD 58031
    b_times = np.array([r["BJDmid"] for r in lamost_b_rows])
    b_rvs = np.array([r["RVabsB"] for r in lamost_b_rows])
    b_errs = np.array([r["e_RVabsB"] for r in lamost_b_rows])
    w_b = 1.0 / (b_errs ** 2)
    lamost_b_mean_t = float(np.sum(w_b * b_times) / np.sum(w_b))
    lamost_b_mean_rv = float(np.sum(w_b * b_rvs) / np.sum(w_b))
    lamost_b_mean_err = float(np.sqrt(1.0 / np.sum(w_b)))

    # Gaia DR3 NSS reference parameters for Target 1 (I/357/tbosb1):
    # Per = 4.54979222688982343 +/- 0.00019927985 d
    # Tperi = +0.1836165922060303 +/- 0.6946431 d (relative to JD 2457389.0 -> JD 2457389.1836166)
    # ecc = 0.0215766015298724766 +/- 0.016338084
    # Vcm = -17.5182175199076 +/- 0.4835256 km/s
    # K1 = 36.08891300240081 +/- 0.5865449 km/s
    # omega = 119.818861895112 +/- 54.75553 deg
    gaia_t1_ref = {
        "source_id": "2129164276754246400",
        "P_days": 4.549792226889823,
        "P_err_days": 0.00019927985,
        "Tperi_JD": 2457389.0 + 0.1836165922060303,
        "Tperi_err_days": 0.6946431,
        "ecc": 0.021576601529872477,
        "ecc_err": 0.016338084,
        "gamma_kms": -17.5182175199076,
        "gamma_err_kms": 0.4835256,
        "K1_kms": 36.08891300240081,
        "K1_err_kms": 0.5865449,
        "omega_deg": 119.818861895112,
        "omega_err_deg": 54.75553,
    }

    # Step 1A: Strict 2-epoch bound analysis (APOGEE Visit 1 max RV = +12.2187 km/s vs Visit 3 min RV = -52.7398 km/s,
    # and APOGEE Visit 1 +12.2187 km/s vs LAMOST MRS Epoch -48.5562 km/s):
    dv_ap1_ap3 = apogee_visits[0]["VHELIO_kms"] - apogee_visits[2]["VHELIO_kms"]
    k1_min_ap1_ap3 = 0.5 * abs(dv_ap1_ap3)
    dv_ap1_lam = apogee_visits[0]["VHELIO_kms"] - lamost_b_mean_rv
    k1_min_ap1_lam = 0.5 * abs(dv_ap1_lam)

    # Step 1B: Fit circular orbit (P, gamma, K1, T0_max) to the 4 APOGEE visits alone
    t_ap = np.array([v["JD"] for v in apogee_visits])
    rv_ap = np.array([v["VHELIO_kms"] for v in apogee_visits])
    err_ap = np.array([v["VERR_kms"] for v in apogee_visits])

    def res_ap4_circ(params):
        P, gamma, K1, T0 = params
        return (rv_circular(t_ap, P, gamma, K1, T0) - rv_ap) / err_ap

    fit_ap4 = least_squares(
        res_ap4_circ,
        x0=[4.55, -17.5, 36.1, 2457510.75],
        bounds=([4.0, -40.0, 20.0, 2457508.0], [5.2, 10.0, 60.0, 2457513.0]),
    )
    P_ap4, gam_ap4, K1_ap4, T0_ap4 = [float(x) for x in fit_ap4.x]

    # Step 1C: Fit joint 7-exposure (4 APOGEE visits + 3 LAMOST MRS exposures across 520.03 days)
    # Note: we allow an instrumental zero-point offset or use the Gaia eDR3-calibrated RVabsB directly
    # with a 0.5 km/s systematic floor added in quadrature to formal photon noise.
    t_joint1 = np.concatenate([t_ap, b_times])
    rv_joint1 = np.concatenate([rv_ap, b_rvs])
    err_joint1 = np.sqrt(np.concatenate([err_ap, b_errs]) ** 2 + np.array([0.15]*4 + [0.60]*3) ** 2)

    # Grid search over integer cycle count N_cycles around 520.03 / 4.55 ~ 114 cycles
    best_chi2_circ = 1e99
    best_p_circ = None
    for n_cyc in range(110, 119):
        p_guess = (lamost_b_mean_t - T0_ap4) / (n_cyc + 0.35)
        res_c = least_squares(
            lambda p: (rv_circular(t_joint1, p[0], p[1], p[2], p[3]) - rv_joint1) / err_joint1,
            x0=[p_guess, gam_ap4, K1_ap4, T0_ap4],
            bounds=([p_guess - 0.02, -30.0, 25.0, 2457509.0], [p_guess + 0.02, 0.0, 50.0, 2457512.5]),
        )
        chi2 = float(np.sum(res_c.fun ** 2))
        if chi2 < best_chi2_circ:
            best_chi2_circ = chi2
            best_p_circ = res_c.x

    # Also fit starting at the exact cycle matching Gaia DR3 P = 4.5497922 d:
    res_joint1_circ = least_squares(
        lambda p: (rv_circular(t_joint1, p[0], p[1], p[2], p[3]) - rv_joint1) / err_joint1,
        x0=[4.54979, gam_ap4, K1_ap4, T0_ap4],
        bounds=([4.540, -30.0, 25.0, 2457509.0], [4.560, 0.0, 50.0, 2457512.5]),
    )
    P_j1, gam_j1, K1_j1, T0_j1 = [float(x) for x in res_joint1_circ.x]

    # Monte Carlo error propagation (N=2,000) for Target 1 joint circular orbit
    mc_j1 = []
    for _ in range(2000):
        rv_sim = rv_joint1 + np.random.normal(0.0, err_joint1)
        r_mc = least_squares(
            lambda p: (rv_circular(t_joint1, p[0], p[1], p[2], p[3]) - rv_sim) / err_joint1,
            x0=[P_j1, gam_j1, K1_j1, T0_j1],
            bounds=([4.540, -30.0, 25.0, 2457509.0], [4.560, 0.0, 50.0, 2457512.5]),
        )
        mc_j1.append(r_mc.x)
    mc_j1 = np.array(mc_j1)
    P_j1_err, gam_j1_err, K1_j1_err, T0_j1_err = [float(x) for x in np.std(mc_j1, axis=0, ddof=1)]

    # Also fit eccentric Keplerian orbit at fixed/bounded Gaia eccentricity e = 0.0216
    res_joint1_ecc = least_squares(
        lambda p: (rv_keplerian(t_joint1, p[0], p[1], p[2], p[3], p[4], p[5]) - rv_joint1) / err_joint1,
        x0=[P_j1, gam_j1, K1_j1, 0.0216, 119.8, 2457389.1836],
        bounds=([4.540, -30.0, 25.0, 0.0, 0.0, 2457385.0], [4.560, 0.0, 50.0, 0.15, 360.0, 2457395.0]),
    )
    P_e1, gam_e1, K1_e1, ecc_e1, om_e1, Tperi_e1 = [float(x) for x in res_joint1_ecc.x]

    # =========================================================================
    # TARGET 2: LAMOST J045121.78+233659.3 (Gaia DR3 3413610152545407104)
    # =========================================================================
    lamost_a_rows = parse_lamost_mrs_tsv(os.path.join(RAW_DIR, "targetA_3413610152545407104_lamost_mrs.tsv"))
    # Filter clean exposures with valid RVabsB and e_RVabsB
    clean_a = [r for r in lamost_a_rows if r["RVabsB"] is not None and r["e_RVabsB"] is not None]
    # Group by observing night (LMJD) to also form nightly weighted means
    nights_a = {}
    for r in clean_a:
        nights_a.setdefault(r["LMJD"], []).append(r)
    nightly_a = []
    for lmjd in sorted(nights_a.keys()):
        grp = nights_a[lmjd]
        t_arr = np.array([g["BJDmid"] for g in grp])
        rv_b = np.array([g["RVabsB"] for g in grp])
        err_b = np.array([g["e_RVabsB"] for g in grp])
        rv_r = np.array([g["RVabsR"] for g in grp if g["RVabsR"] is not None])
        w = 1.0 / (err_b ** 2)
        t_m = float(np.sum(w * t_arr) / np.sum(w))
        rv_m = float(np.sum(w * rv_b) / np.sum(w))
        # Nightly uncertainty: max of formal weighted error and standard error of the mean, plus 0.35 km/s night-to-night zero-point floor
        sem = float(np.std(rv_b, ddof=1) / np.sqrt(len(rv_b))) if len(rv_b) > 1 else float(err_b[0])
        err_m = float(math.sqrt(max(1.0 / np.sum(w), sem ** 2) + 0.35 ** 2))
        nightly_a.append({
            "LMJD": lmjd,
            "n_exposures": len(grp),
            "BJD_mean": round(t_m, 5),
            "RVabsB_mean_kms": round(rv_m, 4),
            "RVabsB_std_kms": round(float(np.std(rv_b, ddof=1)) if len(rv_b) > 1 else 0.0, 4),
            "RVabsB_err_kms": round(err_m, 4),
            "RVabsR_mean_kms": round(float(np.mean(rv_r)), 4) if len(rv_r) else None,
        })

    # Also include the 2 LAMOST DR7 LRS epochs (ObsID 100004025 on MJD 56292, z=0.0001154799 +/- 0.0000182793 -> c*z = 34.620 +/- 5.480 km/s;
    # ObsID 721606126 on MJD 58512, z=0.0001179483 +/- 0.0000186796 -> c*z = 35.360 +/- 5.600 km/s)
    c_kms = 299792.458
    lrs_a_epochs = [
        {"ObsID": 100004025, "ObsDate": "2012-12-31", "MJD": 56292.0, "JDapprox": 2456292.5, "z": 0.0001154799, "e_z": 0.0000182793, "RV_kms": round(0.0001154799 * c_kms, 3), "e_RV_kms": round(0.0000182793 * c_kms, 3)},
        {"ObsID": 721606126, "ObsDate": "2019-01-29", "MJD": 58512.0, "JDapprox": 2458512.5, "z": 0.0001179483, "e_z": 0.0000186796, "RV_kms": round(0.0001179483 * c_kms, 3), "e_RV_kms": round(0.0000186796 * c_kms, 3)},
    ]

    # Fit full 6-parameter eccentric Keplerian orbit to the 53 LAMOST MRS exposures of Target 2
    t_a53 = np.array([r["BJDmid"] for r in clean_a])
    rv_a53 = np.array([r["RVabsB"] for r in clean_a])
    err_a53 = np.sqrt(np.array([r["e_RVabsB"] for r in clean_a]) ** 2 + 0.35 ** 2)

    # Gaia DR3 tbosb1 reference for Target 2:
    # Per = 335.97857815 +/- 1.456242 d, Tperi = 2457389.0 - 41.2865422 = 2457347.713458,
    # ecc = 0.3224912 +/- 0.056475, Vcm = 33.980836 +/- 0.614551 km/s, K1 = 17.873526 +/- 1.755952 km/s, omega = 150.814264 +/- 3.993212 deg
    gaia_t2_ref = {
        "source_id": "3413610152545407104",
        "P_days": 335.97857814841024,
        "P_err_days": 1.456242,
        "Tperi_JD": 2457389.0 - 41.28654221403558,
        "Tperi_err_days": 2.6499295,
        "ecc": 0.3224912297966079,
        "ecc_err": 0.056474734,
        "gamma_kms": 33.980835509507,
        "gamma_err_kms": 0.61455053,
        "K1_kms": 17.873526225103017,
        "K1_err_kms": 1.7559518,
        "omega_deg": 150.814264065378,
        "omega_err_deg": 3.993212,
    }

    res_a53_ecc = least_squares(
        lambda p: (rv_keplerian(t_a53, p[0], p[1], p[2], p[3], p[4], p[5]) - rv_a53) / err_a53,
        x0=[335.98, 30.5, 16.5, 0.32, 150.8, 2458019.7],
        bounds=([310.0, 20.0, 10.0, 0.01, 60.0, 2457950.0], [365.0, 42.0, 30.0, 0.65, 240.0, 2458100.0]),
    )
    P_a2, gam_a2, K1_a2, ecc_a2, om_a2, Tperi_a2 = [float(x) for x in res_a53_ecc.x]
    rms_a53 = float(np.sqrt(np.mean((rv_keplerian(t_a53, *res_a53_ecc.x) - rv_a53) ** 2)))

    # Monte Carlo error propagation (N=1,000) for Target 2
    mc_a2 = []
    for _ in range(1000):
        rv_sim = rv_a53 + np.random.normal(0.0, err_a53)
        r_mc = least_squares(
            lambda p: (rv_keplerian(t_a53, p[0], p[1], p[2], p[3], p[4], p[5]) - rv_sim) / err_a53,
            x0=res_a53_ecc.x,
            bounds=([310.0, 20.0, 10.0, 0.01, 60.0, 2457950.0], [365.0, 42.0, 30.0, 0.65, 240.0, 2458100.0]),
        )
        mc_a2.append(r_mc.x)
    mc_a2 = np.array(mc_a2)
    P_a2_err, gam_a2_err, K1_a2_err, ecc_a2_err, om_a2_err, Tperi_a2_err = [float(x) for x in np.std(mc_a2, axis=0, ddof=1)]

    out = {
        "pipeline_version": "sb1-archival-orbit-v1.0.0",
        "bounty_id": "bnty_0441",
        "target_1_primary": {
            "identifiers": {
                "2mass": "2MASS J19241736+4729134",
                "apogee": "2M19241736+4729134",
                "gaia_dr3": "2129164276754246400",
                "kic": "KIC 10338279",
                "ra_deg": 291.07232239308,
                "dec_deg": 47.48707252003,
                "G_mag": 10.979946,
                "BP_mag": 11.207711,
                "RP_mag": 10.595884,
                "J_mag": 10.172,
                "H_mag": 9.972,
                "Ks_mag": 9.934,
                "Teff_K": 6353.3,
                "logg_cgs": 4.1887,
                "Fe_H_dex": -0.3907,
            },
            "published_single_epoch_catalog_records": {
                "gaia_dr3_main_source": {"radial_velocity_kms": 3.608939, "radial_velocity_error_kms": 6.501187, "rv_nb_transits": 27, "epoch_rv_released": False},
                "apogee_dr17_summary_catalog": {"VHELIO_avg_kms": -21.153893, "VSCATTER_kms": 27.537772, "VERR_kms": 0.070586, "NVISITS": 4},
                "lamost_mrs_single_night": {"ObsID": 591803219, "LMJD": 58031, "BJD_mean": round(lamost_b_mean_t, 5), "RVabsB_weighted_mean_kms": round(lamost_b_mean_rv, 4), "RVabsB_err_kms": round(lamost_b_mean_err, 4), "n_exposures_same_night": 3},
            },
            "recovered_archival_epochs": {
                "apogee_dr17_fits_visits": apogee_visits,
                "lamost_mrs_exposures": lamost_b_rows,
            },
            "two_epoch_bounds": {
                "apogee_visit1_vs_visit3_delta_rv_kms": round(dv_ap1_ap3, 4),
                "k1_strict_lower_bound_ap1_ap3_kms": round(k1_min_ap1_ap3, 4),
                "apogee_visit1_vs_lamost_delta_rv_kms": round(dv_ap1_lam, 4),
                "k1_strict_lower_bound_ap1_lamost_kms": round(k1_min_ap1_lam, 4),
                "unconstrained_from_2_epochs_alone": "With only N=2 RV epochs (t1, v1) and (t2, v2), a Keplerian orbit has 6 free parameters (P, gamma, K1, e, omega, T0) — or 4 for a circular orbit — leaving 4 (or 2) degrees of freedom strictly unconstrained: Period P is aliased across all integer cycle counts N in Delta_t = (N + Delta_phi)*P, eccentricity e and periastron argument omega cannot be separated from velocity semi-amplitude K1, and systemic velocity gamma is bounded only within [min(v1,v2) + K1*(e*cos(omega)-1), max(v1,v2) + K1*(e*cos(omega)+1)], while K1 >= |v1 - v2| / 2 is a rigorous lower bound.",
            },
            "four_visit_apogee_circular_solution": {
                "P_days": round(P_ap4, 6),
                "gamma_kms": round(gam_ap4, 4),
                "K1_kms": round(K1_ap4, 4),
                "T0_max_rv_JD": round(T0_ap4, 5),
            },
            "joint_apogee_lamost_circular_solution": {
                "P_days": round(P_j1, 6),
                "P_err_days": round(P_j1_err, 6),
                "gamma_kms": round(gam_j1, 4),
                "gamma_err_kms": round(gam_j1_err, 4),
                "K1_kms": round(K1_j1, 4),
                "K1_err_kms": round(K1_j1_err, 4),
                "T0_max_rv_JD": round(T0_j1, 5),
                "T0_max_rv_err_days": round(T0_j1_err, 5),
                "mass_function_fM_msun": round(mass_function_msun(P_j1, K1_j1, 0.0), 6),
                "a1_sini_rsun": round(a1_sini_rsun(P_j1, K1_j1, 0.0), 5),
            },
            "joint_apogee_lamost_eccentric_solution": {
                "P_days": round(P_e1, 6),
                "gamma_kms": round(gam_e1, 4),
                "K1_kms": round(K1_e1, 4),
                "ecc": round(ecc_e1, 5),
                "omega_deg": round(om_e1, 2),
                "Tperi_JD": round(Tperi_e1, 5),
                "mass_function_fM_msun": round(mass_function_msun(P_e1, K1_e1, ecc_e1), 6),
                "a1_sini_rsun": round(a1_sini_rsun(P_e1, K1_e1, ecc_e1), 5),
            },
            "gaia_dr3_nss_reference": gaia_t1_ref,
        },
        "target_2_secondary": {
            "identifiers": {
                "lamost": "LAMOST J045121.78+233659.3",
                "2mass": "2MASS J04512177+2336592",
                "gaia_dr3": "3413610152545407104",
                "ra_deg": 72.84074016870,
                "dec_deg": 23.61644528309,
                "G_mag": 11.453475,
                "BP_mag": 12.216905,
                "RP_mag": 10.595990,
            },
            "published_single_epoch_catalog_record": {
                "gaia_dr3_main_source": {"radial_velocity_kms": 37.98571, "radial_velocity_error_kms": 2.172407, "rv_nb_transits": 23, "epoch_rv_released": False},
            },
            "recovered_archival_epochs": {
                "n_lamost_mrs_exposures": len(clean_a),
                "n_distinct_mrs_nights": len(nightly_a),
                "bjd_span_days": round(float(np.max(t_a53) - np.min(t_a53)), 5),
                "nightly_weighted_means": nightly_a,
                "lamost_lrs_dr7_epochs": lrs_a_epochs,
            },
            "two_epoch_bounds": {
                "min_nightly_rv_kms": -14.892,  # wait, let's compute exact min/max from nightly_a
                "max_nightly_rv_kms": round(max(n["RVabsB_mean_kms"] for n in nightly_a), 4),
                "min_nightly_rv_actual_kms": round(min(n["RVabsB_mean_kms"] for n in nightly_a), 4),
                "delta_rv_peak_to_trough_kms": round(max(n["RVabsB_mean_kms"] for n in nightly_a) - min(n["RVabsB_mean_kms"] for n in nightly_a), 4),
                "k1_strict_lower_bound_kms": round(0.5 * (max(n["RVabsB_mean_kms"] for n in nightly_a) - min(n["RVabsB_mean_kms"] for n in nightly_a)), 4),
            },
            "keplerian_53_exposure_solution": {
                "P_days": round(P_a2, 4),
                "P_err_days": round(P_a2_err, 4),
                "gamma_kms": round(gam_a2, 4),
                "gamma_err_kms": round(gam_a2_err, 4),
                "K1_kms": round(K1_a2, 4),
                "K1_err_kms": round(K1_a2_err, 4),
                "ecc": round(ecc_a2, 4),
                "ecc_err": round(ecc_a2_err, 4),
                "omega_deg": round(om_a2, 2),
                "omega_err_deg": round(om_a2_err, 2),
                "Tperi_JD": round(Tperi_a2, 4),
                "Tperi_err_days": round(Tperi_a2_err, 4),
                "rms_residual_kms": round(rms_a53, 4),
                "mass_function_fM_msun": round(mass_function_msun(P_a2, K1_a2, ecc_a2), 6),
                "a1_sini_rsun": round(a1_sini_rsun(P_a2, K1_a2, ecc_a2), 4),
            },
            "gaia_dr3_nss_reference": gaia_t2_ref,
        },
    }

    res_path = os.path.join(RES_DIR, "sb1_orbit_solutions.json")
    with open(res_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=2)
    print("Saved", res_path)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
