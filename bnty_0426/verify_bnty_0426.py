#!/usr/bin/env python3
"""
verify_bnty_0426.py — Automated verifier for DAiL bnty_0426
(TIC 158499577: independent re-fold, different code)
"""

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "raw")
RES_FILE = os.path.join(BASE_DIR, "results", "independent_refold_results.json")
SUB_FILE = os.path.join(BASE_DIR, "SUBMISSION.txt")


def main():
    required_raw = [
        "tess2019058134432-s0009-0000000158499577-0139-s_lc.fits",
        "tess2021065132309-s0036-0000000158499577-0207-s_lc.fits",
        "1SWASP_J105638.34-363449.0.fits",
        "1SWASP_J105638.34-363449.0.csv",
        "1SWASP_J105633.25-363457.2_control.fits",
    ]
    for fn in required_raw:
        p = os.path.join(RAW_DIR, fn)
        assert os.path.isfile(p) and os.path.getsize(p) > 50, f"Missing raw file: {p}"

    assert os.path.isfile(RES_FILE), f"Missing results file: {RES_FILE}"
    with open(RES_FILE, "r", encoding="utf-8") as fh:
        res = json.load(fh)

    assert res["house_ephemeris_folded"]["P_d"] == 11.7672
    assert res["house_ephemeris_folded"]["T0_btjd"] == 2286.372

    tf = res["folded_depths_per_dataset"]["TESS_SPOC_S9_S36"]["PDCSAP_biweight_detrended"]
    assert 0.330 <= tf["core_bottom_hw0008"]["primary_phi0000"]["median_depth"] <= 0.340
    assert 0.290 <= tf["core_bottom_hw0008"]["secondary_ecc_phi05141"]["median_depth"] <= 0.300
    assert abs(tf["core_bottom_hw0008"]["control_phi0250"]["median_depth"]) < 0.002
    assert abs(tf["core_bottom_hw0008"]["control_phi0750"]["median_depth"]) < 0.002

    sf = res["folded_depths_per_dataset"]["SuperWASP_DR1_2006_2008"]["TAMFLUX2_biweight_detrended_clean"]
    assert 0.34 <= sf["core_bottom_hw0025"]["primary_phi0000"]["median_dmag"] <= 0.42
    assert 0.29 <= sf["core_bottom_hw0025"]["secondary_ecc_phi05141"]["median_dmag"] <= 0.36
    assert abs(sf["house_match_full_dur_hw0108"]["control_phi0250"]["median_dmag"]) < 0.015
    assert abs(sf["house_match_full_dur_hw0108"]["control_phi0750"]["median_dmag"]) < 0.015

    assert len(res["per_event_depths"]["TESS_all_8_events"]) == 8
    assert len(res["per_event_depths"]["SuperWASP_all_windows_ge3_pts"]) == 19

    assert os.path.isfile(SUB_FILE), f"Missing submission file: {SUB_FILE}"
    with open(SUB_FILE, "r", encoding="utf-8") as fh:
        sub_txt = fh.read()
    assert 1500 <= len(sub_txt) <= 5000, f"SUBMISSION.txt length {len(sub_txt)} out of [1500, 5000] bounds"

    print(f"ALL bnty_0426 CHECKS PASSED! SUBMISSION.txt length = {len(sub_txt)} chars")
    return 0


if __name__ == "__main__":
    sys.exit(main())
