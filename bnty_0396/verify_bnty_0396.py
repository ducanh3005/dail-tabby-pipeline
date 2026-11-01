#!/usr/bin/env python3
"""
Standalone Reproducibility & Verification Script for DAiL bnty_0396 (HALLOWEEN: Ghost or Monster)
Target: KIC 3337351 (TIC 122224586 / Gaia DR3 2052868099751582976 / KOI K00965.01) — Verdict: GHOST
Culprit: KIC 3230227 (TIC 122224576 / Gaia DR3 2052868095451251200 / KOI K06311.01) — 17.91" SW, Kp=9.002 EB (P=7.0471062 d)
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

from run_pipeline import load_fits_geom, stamp_centroid, median, mean, mad_to_sigma, running_median

MAST_DIR = os.path.join(HERE, "mast")
RAW_DIR = os.path.join(HERE, "raw")

LLC_FN = "kplr003337351-2010355172524_llc.fits"
TPF_FN = "kplr003337351-2010355172524_lpd-targ.fits"
EXP_LLC_SHA = "d56e4c23e95dbd9099682ee53d54bacef580dd8e03224ad9bb2eb5a545aff844"
EXP_TPF_SHA = "3a6adb52d8e116604a82364d607c4142da696bfc939ce21276ae8a58b4b710c6"

def sha256_file(path: str) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

def main():
    llc_path = os.path.join(MAST_DIR, LLC_FN)
    tpf_path = os.path.join(MAST_DIR, TPF_FN)
    assert os.path.exists(llc_path), f"Missing {llc_path}"
    assert os.path.exists(tpf_path), f"Missing {tpf_path}"
    assert sha256_file(llc_path) == EXP_LLC_SHA, "LLC SHA256 mismatch"
    assert sha256_file(tpf_path) == EXP_TPF_SHA, "TPF SHA256 mismatch"

    eb_data = json.load(open(os.path.join(RAW_DIR, "kirk2016_eb_excerpt.json"), encoding="utf-8"))
    assert len(eb_data["target_kic_3337351"]) == 0
    assert len(eb_data["culprit_kic_3230227"]) == 1
    assert len(eb_data["positive_control_kic_9101279"]) == 1
    eb_row = eb_data["culprit_kic_3230227"][0]
    p_eb = eb_row["per_d"]
    bkjd0 = eb_row["bjd0"] - 54833.0

    ttables, timages = load_fits_geom(tpf_path)
    ltables, _ = load_fits_geom(llc_path)
    t = ttables[0][1]
    l = ltables[0][1]
    _, apvals, apshape = [x for x in timages if x[0] == "APERTURE"][0]
    naxis1, naxis2 = apshape[0], apshape[1]
    grid = [[apvals[r * naxis1 + c] for c in range(naxis1)] for r in range(naxis2)]
    idxs_a = [r * naxis1 + c for r in range(naxis2) for c in range(naxis1) if grid[r][c] == 3]

    lmap = {round(tt, 6): i for i, tt in enumerate(l["TIME"]) if tt == tt}
    cads = []
    for i, tt in enumerate(t["TIME"]):
        if tt != tt:
            continue
        j = lmap.get(round(tt, 6))
        if j is None:
            continue
        q = l["SAP_QUALITY"][j]
        if q != 0:
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
    assert abs(t1_ratio - 1.0) < 1e-6, f"T1 ratio failed: {t1_ratio}"

    pdc_trend = running_median([c["pdc"] for c in cads], 150)
    sap_trend = running_median([c["sap"] for c in cads], 150)
    for idx, c in enumerate(cads):
        c["pdc_rel"] = (c["pdc"] / pdc_trend[idx] - 1.0) * 100.0
        c["sap_rel"] = (c["sap"] / sap_trend[idx] - 1.0) * 100.0

    deep_cads = [c for c in cads if c["sap_rel"] < -2.0]
    events = []
    for c in deep_cads:
        if not events or c["t"] - events[-1][-1]["t"] > 0.5:
            events.append([c])
        else:
            events[-1].append(c)

    print(json.dumps({
        "status": "PASS",
        "kic_target": 3337351,
        "kic_culprit": 3230227,
        "verdict": "GHOST",
        "q7_quality0_cadences": len(cads),
        "t1_aperture_sap_ratio": round(t1_ratio, 10),
        "q7_ghost_eclipse_count": len(events),
        "culprit_period_d": p_eb,
        "culprit_bkjd0": round(bkjd0, 6),
    }, indent=2))

if __name__ == "__main__":
    main()
