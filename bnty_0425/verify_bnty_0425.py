#!/usr/bin/env python3
"""
verify_bnty_0425.py — Automated verifier for DAiL bnty_0425
(TIC 158499577: TESS FFI re-extraction in unsearched sectors)
"""

import csv
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "raw")
RES_DIR = os.path.join(BASE_DIR, "results")
RES_FILE = os.path.join(RES_DIR, "ffi_reextraction_results.json")
SUB_FILE = os.path.join(BASE_DIR, "SUBMISSION.txt")


def main():
    required_raw = [
        "tesscut_sectors.json",
        "tesscut_fits_manifest_sha256.json",
        "tesscut_s0009_tess-s0009-2-3_164.159748_-36.580314_11x11_astrocut.fits",
        "tesscut_s0036_tess-s0036-2-3_164.159748_-36.580314_11x11_astrocut.fits",
        "tesscut_s0063_tess-s0063-2-4_164.159748_-36.580314_11x11_astrocut.fits",
        "tesscut_s0090_tess-s0090-2-4_164.159748_-36.580314_11x11_astrocut.fits",
        "tesscut_s0099_tess-s0099-2-2_164.159748_-36.580314_11x11_astrocut.fits",
        "tesscut_s0100_tess-s0100-2-4_164.159748_-36.580314_11x11_astrocut.fits",
    ]
    for fn in required_raw:
        p = os.path.join(RAW_DIR, fn)
        assert os.path.isfile(p) and os.path.getsize(p) > 50, f"Missing raw file: {p}"

    assert os.path.isfile(RES_FILE), f"Missing results file: {RES_FILE}"
    with open(RES_FILE, "r", encoding="utf-8") as f:
        res = json.load(f)

    assert res["observed_sectors_all"] == [9, 36, 63, 90, 99, 100]
    assert res["house_2min_baseline_sectors"] == [9, 36]
    assert res["unsearched_ffi_sectors"] == [63, 90, 99, 100]

    # Verify extracted CSV files for all 6 sectors exist and match row counts
    for sec in [9, 36, 63, 90, 99, 100]:
        sinfo = res["per_sector_extractions"][str(sec)]
        csv_p = os.path.join(RES_DIR, sinfo["csv_file"])
        assert os.path.isfile(csv_p), f"Missing extracted FFI CSV: {csv_p}"
        with open(csv_p, "r", encoding="utf-8") as fc:
            nrows = sum(1 for _ in csv.DictReader(fc))
        assert nrows == sinfo["n_frames_clean_used"], f"Row mismatch in {csv_p}: {nrows} vs {sinfo['n_frames_clean_used']}"

    # Verify combined unsearched FFI fold depths
    cf = res["combined_unsearched_ffi_fold"]["house_ephemeris_P11p7672_T0_2286p3720"]
    assert 0.320 <= cf["core_hw0010"]["primary_phi0000"]["biweight_depth"] <= 0.335
    assert 0.285 <= cf["core_hw0010"]["secondary_ecc_phi05141"]["biweight_depth"] <= 0.296
    assert abs(cf["box_hw0017"]["control_phi0250"]["biweight_depth"]) < 0.001
    assert abs(cf["box_hw0017"]["control_phi0750"]["biweight_depth"]) < 0.001

    # Verify all 16 new transits in unsearched sectors S63, S90, S99, S100
    assert len(res["new_transits_in_unsearched_sectors"]) == 16

    assert os.path.isfile(SUB_FILE), f"Missing submission file: {SUB_FILE}"
    with open(SUB_FILE, "r", encoding="utf-8") as f:
        sub_txt = f.read()
    assert 1500 <= len(sub_txt) <= 5000, f"SUBMISSION.txt length {len(sub_txt)} out of [1500, 5000] bounds"

    print(f"ALL bnty_0425 CHECKS PASSED! SUBMISSION.txt length = {len(sub_txt)} chars")
    return 0


if __name__ == "__main__":
    sys.exit(main())
