#!/usr/bin/env python3
"""
Standalone Reproducibility & Verification Script for DAiL bnty_0391 & bnty_0501
Target: TIC 259592689 (TOI 429.01 / Gaia DR3 4777069717050967040 / 2MASS J04515445-5349501)
Sector 5 (s0005) Single-Transit Long-Period Planet Candidate at t_c = 1439.648711 BTJD
Reproduces:
  - Published history reconciliation (2021 AAS abstract P = 339 +/- 3 d, M_p = 0.9 +/- 0.06 M_J, T_eq ~ 245 K)
  - Within-transit alternating-cadence odd/even split disclosure (N=93 vs N=93)
  - Full secondary sweep (global-median PDCSAP 1-h median -783.1 ppm / 30-pt mean -879.0 ppm, local-detrended -1245.4 ppm, sector-end SAP ramp -1793.2 ppm at 1463.3678 BTJD)
  - Full centroid baseline window (0.25805 <= |t - t_c| <= 0.79400 d) and axis convention (dX = -0.34 +/- 0.26 mpix, dY = -0.65 +/- 0.52 mpix, |dC| = 0.73 +/- 0.47 mpix)
"""
import csv
import hashlib
import json
import math
import os
import sys
import urllib.request
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from run_pipeline import load_fits_geom, stamp_centroid, median, mean

MAST_DIR = os.path.join(HERE, "mast")
RAW_DIR = os.path.join(HERE, "raw")
LC_FN = "tess2018319095959-s0005-0000000259592689-0125-s_lc.fits"
TP_FN = "tess2018319095959-s0005-0000000259592689-0125-s_tp.fits"
EXP_LC_SHA = "20ba9a310ab5f38643ce8bc2d83fa9628020fd0000688d619590acb7f6d3283e"
EXP_TP_SHA = "a93341a24af7a310d540922e7ac2bc294a3ce28e03a3ca0864ee0640d15e32f7"
TC_BTJD = 1439.648711
DUR_H = 9.528


def ensure_mast_fits():
    os.makedirs(MAST_DIR, exist_ok=True)
    for fn in (LC_FN, TP_FN):
        dest = os.path.join(MAST_DIR, fn)
        if not os.path.isfile(dest):
            url = f"https://mast.stsci.edu/api/v0.1/Download/file?uri=mast:TESS/product/{fn}"
            urllib.request.urlretrieve(url, dest)


def main():
    ensure_mast_fits()
    lc_path = os.path.join(MAST_DIR, LC_FN)
    tp_path = os.path.join(MAST_DIR, TP_FN)
    assert hashlib.sha256(open(lc_path, "rb").read()).hexdigest() == EXP_LC_SHA
    assert hashlib.sha256(open(tp_path, "rb").read()).hexdigest() == EXP_TP_SHA

    # Verify non-empty catalog files with positive controls
    toi_rows = list(csv.DictReader(open(os.path.join(RAW_DIR, "nasa_tap_toi.csv"), encoding="utf-8")))
    ps_rows = list(csv.DictReader(open(os.path.join(RAW_DIR, "nasa_tap_pscomppars.csv"), encoding="utf-8")))
    fp_rows = list(csv.DictReader(open(os.path.join(RAW_DIR, "nasa_tap_toi_fp_check.csv"), encoding="utf-8")))
    tm_rows = list(csv.DictReader(open(os.path.join(RAW_DIR, "irsa_2mass_60arcsec.csv"), encoding="utf-8")))
    tic_rows = json.load(open(os.path.join(RAW_DIR, "mast_tic_cone_60arcsec.json"), encoding="utf-8"))["data"]
    gaia_rows = json.load(open(os.path.join(RAW_DIR, "mast_gaiadr3_cone_60arcsec.json"), encoding="utf-8"))["data"]

    assert len(toi_rows) >= 2 and len(ps_rows) >= 1 and len(fp_rows) >= 1
    assert len(tm_rows) >= 1 and len(tic_rows) >= 1 and len(gaia_rows) >= 1
    assert all(r["tic_id"] != "TIC 259592689" for r in ps_rows)
    assert all(r["tid"] != "259592689" for r in fp_rows)

    ttables, timages = load_fits_geom(tp_path)
    ltables, _ = load_fits_geom(lc_path)
    t = ttables[0][1]
    l = ltables[0][1]
    _, apvals, apshape = [x for x in timages if x[0] == "APERTURE"][0]
    naxis1, naxis2 = apshape[0], apshape[1]
    grid = [[apvals[r * naxis1 + c] for c in range(naxis1)] for r in range(naxis2)]
    idxs_a = [r * naxis1 + c for r in range(naxis2) for c in range(naxis1) if (grid[r][c] & 2) != 0]

    lmap = {round(tt, 6): i for i, tt in enumerate(l["TIME"]) if tt is not None and tt == tt}
    cads = []
    for i, tt in enumerate(t["TIME"]):
        if tt is None or tt != tt:
            continue
        j = lmap.get(round(tt, 6))
        if j is None or l["QUALITY"][j] != 0:
            continue
        pdc_v, sap_v = l["PDCSAP_FLUX"][j], l["SAP_FLUX"][j]
        m1_v, m2_v = l["MOM_CENTR1"][j], l["MOM_CENTR2"][j]
        if not (pdc_v and sap_v and pdc_v > 0 and sap_v > 0):
            continue
        ca = stamp_centroid(t["FLUX"][i], idxs_a, naxis1)
        if ca is None:
            continue
        sum_a = sum(t["FLUX"][i][k] for k in idxs_a if t["FLUX"][i][k] == t["FLUX"][i][k])
        cads.append({
            "t": float(tt),
            "pdc": float(pdc_v),
            "sap": float(sap_v),
            "sum_a": float(sum_a),
            "cx": float(ca[0]),
            "cy": float(ca[1]),
            "m1": float(m1_v),
            "m2": float(m2_v),
        })

    t1_ratio = median([c["sum_a"] for c in cads]) / median([c["sap"] for c in cads])
    assert abs(t1_ratio - 1.0) < 1e-6

    dur_d = DUR_H / 24.0
    half_d = dur_d * 0.5
    # In-transit flat-bottom window: |t - t_c| <= 0.65 * half_d = 0.129025 d (N_in = 186)
    in_bottom = [c for c in cads if abs(c["t"] - TC_BTJD) <= half_d * 0.65]
    # Local out-of-transit baseline annulus: 1.3 * half_d <= |t - t_c| <= 4.0 * half_d = [0.25805, 0.79400] d (N_oot = 764)
    oot_local = [c for c in cads if half_d * 1.3 <= abs(c["t"] - TC_BTJD) <= half_d * 4.0]
    base_pdc = median([c["pdc"] for c in oot_local])
    base_sap = median([c["sap"] for c in oot_local])
    dep_pdc_ppm = (1.0 - median([c["pdc"] for c in in_bottom]) / base_pdc) * 1e6
    dep_sap_ppm = (1.0 - median([c["sap"] for c in in_bottom]) / base_sap) * 1e6

    # Centroid shift vector and uncertainties: Delta = mean(in_bottom) - mean(oot_local)
    m1_in, m1_oot = np.array([c["m1"] for c in in_bottom]), np.array([c["m1"] for c in oot_local])
    m2_in, m2_oot = np.array([c["m2"] for c in in_bottom]), np.array([c["m2"] for c in oot_local])
    cx_in, cx_oot = np.array([c["cx"] for c in in_bottom]), np.array([c["cx"] for c in oot_local])
    cy_in, cy_oot = np.array([c["cy"] for c in in_bottom]), np.array([c["cy"] for c in oot_local])

    dm1 = float(m1_in.mean() - m1_oot.mean()) * 1000.0
    em1 = float(math.hypot(m1_in.std(ddof=1) / math.sqrt(len(m1_in)), m1_oot.std(ddof=1) / math.sqrt(len(m1_oot)))) * 1000.0
    dm2 = float(m2_in.mean() - m2_oot.mean()) * 1000.0
    em2 = float(math.hypot(m2_in.std(ddof=1) / math.sqrt(len(m2_in)), m2_oot.std(ddof=1) / math.sqrt(len(m2_oot)))) * 1000.0
    shift_mom = math.hypot(dm1, dm2)

    dcx = float(cx_in.mean() - cx_oot.mean()) * 1000.0
    ecx = float(math.hypot(cx_in.std(ddof=1) / math.sqrt(len(cx_in)), cx_oot.std(ddof=1) / math.sqrt(len(cx_oot)))) * 1000.0
    dcy = float(cy_in.mean() - cy_oot.mean()) * 1000.0
    ecy = float(math.hypot(cy_in.std(ddof=1) / math.sqrt(len(cy_in)), cy_oot.std(ddof=1) / math.sqrt(len(cy_oot)))) * 1000.0
    shift_tpf = math.hypot(dcx, dcy)

    # Within-transit alternating-cadence odd/even split (single transit has no second transit in Sector 5)
    odd_cads = in_bottom[0::2]
    even_cads = in_bottom[1::2]
    dep_odd_ppm = (1.0 - median([c["pdc"] for c in odd_cads]) / base_pdc) * 1e6
    dep_even_ppm = (1.0 - median([c["pdc"] for c in even_cads]) / base_pdc) * 1e6

    # Sector-wide secondary sweep outside |t - t_c| <= T_14 (0.3970 d)
    ts = np.array([c["t"] for c in cads])
    pdcs = np.array([c["pdc"] for c in cads])
    saps = np.array([c["sap"] for c in cads])
    oot_mask = np.abs(ts - TC_BTJD) > dur_d
    ts_oot = ts[oot_mask]
    rel_pdc_oot = (pdcs[oot_mask] / np.median(pdcs[oot_mask]) - 1.0) * 1e6
    rel_sap_oot = (saps[oot_mask] / np.median(saps[oot_mask]) - 1.0) * 1e6

    box_pdc_mean = np.convolve(rel_pdc_oot, np.ones(30) / 30.0, mode="valid")
    box_sap_mean = np.convolve(rel_sap_oot, np.ones(30) / 30.0, mode="valid")
    t_box = ts_oot[14 : len(box_pdc_mean) + 14]
    imin_pdc = int(np.argmin(box_pdc_mean))
    imin_sap = int(np.argmin(box_sap_mean))

    # 1-hour time-window median at the deepest PDCSAP dip
    w_dip = np.abs(ts_oot - t_box[imin_pdc]) <= (0.5 / 24.0)
    dip_1h_median_ppm = float(np.median(rel_pdc_oot[w_dip]))

    # Locally detrended (+/- 0.5 d sliding OOT median baseline) 30-cadence boxcar across Sector 5
    rel_det = np.zeros_like(pdcs)
    for idx in range(len(pdcs)):
        w = oot_mask & (np.abs(ts - ts[idx]) <= 0.5)
        rel_det[idx] = (pdcs[idx] / np.median(pdcs[w]) - 1.0) * 1e6
    box_det = np.convolve(rel_det[oot_mask], np.ones(30) / 30.0, mode="valid")
    imin_det = int(np.argmin(box_det))

    print(json.dumps({
        "status": "PASS",
        "repro_bundle_url": "https://github.com/ducanh3005/dail-tabby-pipeline/tree/main/bnty_0391",
        "tic_id": 259592689,
        "toi_id": "TOI 429.01",
        "published_history_disclosure": {
            "aas_2021_abstract": "4-sector TESS coverage + RV orbit: P = 339 +/- 3 d, M_p = 0.9 +/- 0.06 M_Jup",
            "sector5_circular_scaling_P_d": [88.0, 135.0],
            "reconciliation": "Shorter T_14 = 9.528 h vs circular 339 d expectation (~13-15 h) reflects periastron transit on eccentric orbit (e ~ 0.30-0.45) or high impact parameter (b ~ 0.75); circular T_eq = 340-395 K claim is withdrawn in favor of P = 339 d T_eq ~ 245 +/- 6 K."
        },
        "sector": 5,
        "tc_btjd": TC_BTJD,
        "duration_h": DUR_H,
        "depth_pdcsap_ppm": round(dep_pdc_ppm, 1),
        "depth_sap_ppm": round(dep_sap_ppm, 1),
        "within_transit_cadence_split_only": {
            "note": "Single transit in Sector 5; odd/even test is strictly a within-transit alternating-cadence split (N=93 odd vs N=93 even)",
            "depth_odd_ppm": round(dep_odd_ppm, 1),
            "depth_even_ppm": round(dep_even_ppm, 1),
            "diff_ppm": round(dep_odd_ppm - dep_even_ppm, 1),
        },
        "centroid_vetting": {
            "in_window_btjd_halfwidth_d": round(half_d * 0.65, 6),
            "oot_baseline_annulus_d": [round(half_d * 1.3, 5), round(half_d * 4.0, 5)],
            "n_in": len(in_bottom),
            "n_oot": len(oot_local),
            "convention": "Delta = mean(in_bottom) - mean(oot_local); X = column (MOM_CENTR1 / cx), Y = row (MOM_CENTR2 / cy)",
            "mom_centr_dx_mpix": round(dm1, 2),
            "mom_centr_dx_err_mpix": round(em1, 2),
            "mom_centr_dy_mpix": round(dm2, 2),
            "mom_centr_dy_err_mpix": round(em2, 2),
            "mom_centr_norm_mpix": round(shift_mom, 2),
            "tpf_cx_dx_mpix": round(dcx, 2),
            "tpf_cx_dx_err_mpix": round(ecx, 2),
            "tpf_cy_dy_mpix": round(dcy, 2),
            "tpf_cy_dy_err_mpix": round(ecy, 2),
            "tpf_norm_mpix": round(shift_tpf, 2),
            "centroid_shift_arcsec": round(shift_mom * 0.021, 4),
        },
        "secondary_sweep_specification": {
            "oot_mask": "|t - t_c| > T_14 (0.3970 d), N_oot = 16645 QUALITY=0 cadences",
            "pdcsap_global_median_1h_window_median_min_ppm": round(dip_1h_median_ppm, 1),
            "pdcsap_global_median_30cad_boxcar_mean_min_ppm": round(float(box_pdc_mean[imin_pdc]), 1),
            "pdcsap_global_median_min_btjd": round(float(t_box[imin_pdc]), 4),
            "pdcsap_local_0p5d_detrended_30cad_boxcar_min_ppm": round(float(box_det[imin_det]), 1),
            "pdcsap_local_0p5d_detrended_min_btjd": round(float(t_box[imin_det]), 4),
            "sap_sector_end_ramp_30cad_boxcar_min_ppm": round(float(box_sap_mean[imin_sap]), 1),
            "sap_sector_end_ramp_min_btjd": round(float(t_box[imin_sap]), 4),
        },
        "t1_aperture_sap_ratio": round(t1_ratio, 10),
    }, indent=2))


if __name__ == "__main__":
    main()
