#!/usr/bin/env python3
"""
verify_bnty_0424.py — Automated verifier for DAiL bnty_0424
(TIC 158499577: joint TESS + SuperWASP period fit)
"""

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "raw")
RES_FILE = os.path.join(BASE_DIR, "results", "joint_ephemeris_results.json")
SUB_FILE = os.path.join(BASE_DIR, "SUBMISSION.txt")


def main():
    required_raw = [
        "tess2019058134432-s0009-0000000158499577-0139-s_lc.fits",
        "tess2021065132309-s0036-0000000158499577-0207-s_lc.fits",
        "1SWASP_J105638.34-363449.0.fits",
        "1SWASP_J105638.34-363449.0.csv",
        "1SWASP_J105633.25-363457.2_control.fits",
        "nea_superwasp_metadata.json",
    ]
    for fn in required_raw:
        p = os.path.join(RAW_DIR, fn)
        assert os.path.isfile(p) and os.path.getsize(p) > 50, f"Missing or empty raw file: {p}"

    assert os.path.isfile(RES_FILE), f"Missing results file: {RES_FILE}"
    with open(RES_FILE, "r", encoding="utf-8") as fh:
        res = json.load(fh)

    eph = res["adopted_joint_ephemeris"]
    assert 11.767200 <= eph["P_d"] <= 11.767230, f"Unexpected P_d: {eph['P_d']}"
    assert 0 < eph["sigma_P_adopted_d"] <= 0.000020, f"Unexpected sigma_P: {eph['sigma_P_adopted_d']}"
    assert 2286.3715 <= eph["T0_pri_btjd"] <= 2286.3725, f"Unexpected T0: {eph['T0_pri_btjd']}"
    assert 0.5138 <= eph["phi_sec"] <= 0.5144, f"Unexpected phi_sec: {eph['phi_sec']}"

    agr = res["dataset_agreement_checks"]
    assert agr["tess_vs_swasp_anchored_tdb"]["agrees_within_2sigma"] is True
    assert agr["tess_vs_swasp_anchored_utc"]["agrees_within_2sigma"] is True
    assert agr["tess_vs_swasp_internal_oc"]["agrees_within_2sigma"] is True
    assert agr["secondary_phase_apsidal_check"]["agrees_within_2sigma"] is True

    preds = res["predictions_nov_dec_2026"]
    assert len(preds) == 4
    expected_cycles = [176, 177, 178, 179]
    for p, exp_c in zip(preds, expected_cycles):
        assert p["cycle"] == exp_c
        assert 0 < p["sigma_adopted_min"] < 5.0

    assert len(res["eclipse_timing_table_and_residuals"]) == 20

    assert os.path.isfile(SUB_FILE), f"Missing submission file: {SUB_FILE}"
    with open(SUB_FILE, "r", encoding="utf-8") as fh:
        sub_txt = fh.read()
    assert 1500 <= len(sub_txt) <= 5000, f"SUBMISSION.txt length {len(sub_txt)} out of [1500, 5000] bounds"

    print(f"ALL bnty_0424 CHECKS PASSED! SUBMISSION.txt length = {len(sub_txt)} chars")
    return 0


if __name__ == "__main__":
    sys.exit(main())
