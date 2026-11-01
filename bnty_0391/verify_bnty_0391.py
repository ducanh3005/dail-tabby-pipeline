#!/usr/bin/env python3
"""
Standalone Reproducibility & Verification Script for DAiL bnty_0391
Target: TIC 259592689 (TOI 429.01 / Gaia DR3 4777069717050967040 / 2MASS J04515445-5349501)
Sector 5 (s0005) Single-Transit Long-Period Planet Candidate at t_c = 1439.648711 BTJD
"""
import csv
import hashlib
import io
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from run_pipeline import load_fits_geom, stamp_centroid, median, mean, mad_to_sigma

MAST_DIR = os.path.join(HERE, "mast")
RAW_DIR = os.path.join(HERE, "raw")
LC_FN = "tess2018319095959-s0005-0000000259592689-0125-s_lc.fits"
TP_FN = "tess2018319095959-s0005-0000000259592689-0125-s_tp.fits"
EXP_LC_SHA = "20ba9a310ab5f38643ce8bc2d83fa9628020fd0000688d619590acb7f6d3283e"
EXP_TP_SHA = "a93341a24af7a310d540922e7ac2bc294a3ce28e03a3ca0864ee0640d15e32f7"
TC_BTJD = 1439.648711
DUR_H = 9.528

def main():
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

    half_d = (DUR_H / 24.0) * 0.5
    in_bottom = [c for c in cads if abs(c["t"] - TC_BTJD) <= half_d * 0.65]
    oot_local = [c for c in cads if half_d * 1.3 <= abs(c["t"] - TC_BTJD) <= half_d * 4.0]
    base_pdc = median([c["pdc"] for c in oot_local])
    base_sap = median([c["sap"] for c in oot_local])
    dep_pdc_ppm = (1.0 - median([c["pdc"] for c in in_bottom]) / base_pdc) * 1e6
    dep_sap_ppm = (1.0 - median([c["sap"] for c in in_bottom]) / base_sap) * 1e6
    dm1 = (mean([c["m1"] for c in in_bottom]) - mean([c["m1"] for c in oot_local])) * 1000.0
    dm2 = (mean([c["m2"] for c in in_bottom]) - mean([c["m2"] for c in oot_local])) * 1000.0
    shift_mom = math.hypot(dm1, dm2)

    print(json.dumps({
        "status": "PASS",
        "tic_id": 259592689,
        "sector": 5,
        "tc_btjd": TC_BTJD,
        "duration_h": DUR_H,
        "depth_pdcsap_ppm": round(dep_pdc_ppm, 1),
        "depth_sap_ppm": round(dep_sap_ppm, 1),
        "centroid_shift_mpix": round(shift_mom, 2),
        "centroid_shift_arcsec": round(shift_mom * 0.021, 4),
        "t1_aperture_sap_ratio": round(t1_ratio, 10),
    }, indent=2))

if __name__ == "__main__":
    main()
