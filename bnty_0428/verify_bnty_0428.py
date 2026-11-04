#!/usr/bin/env python3
"""
verify_bnty_0428.py — Automated verifier for DAiL bnty_0428
(TIC 158499577: other wide-field survey folds: ATLAS, KELT-South, HATSouth, Evryscope)
"""

import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "raw")
RES_FILE = os.path.join(BASE_DIR, "results", "widefield_survey_folds.json")
SUB_FILE = os.path.join(BASE_DIR, "SUBMISSION.txt")


def main():
    required_raw = [
        "atlas_forcedphot_index.html",
        "hatsouth_org_planets.html",
        "hatsouth_org_lcs.html",
        "mast_caom_cone_all.json",
        "nea_kelt_box1deg.json",
        "nea_kelt_box2p5deg.json",
        "nea_kelttimeseries_grid_140_190.json",
        "nea_kelt_S23_southern_edge.json",
        "nea_kelt_S24_western_edge.json",
        "hlsp_qlp_tess_ffi_s0009-0000000158499577_tess_v01_llc.fits",
        "hlsp_qlp_tess_ffi_s0036-0000000158499577_tess_v01_llc.fits",
        "hlsp_qlp_tess_ffi_s0063-0000000158499577_tess_v01_llc.fits",
        "hlsp_qlp_tess_ffi_s0090-0000000158499577_tess_v01_llc.fits",
        "hlsp_qlp_tess_ffi_s0099-0000000158499577_tess_v01_llc.fits",
        "hlsp_qlp_tess_ffi_s0100-0000000158499577_tess_v01_llc.fits",
        "hlsp_t16_tess_ffi_s0009-cam2-ccd3-05401019098113741568_tess_v01_llc.fits",
        "hlsp_tglc_tess_ffi_gaiaid-5401019098113741568-s0009-cam2-ccd3_tess_v1_llc.fits",
        "hlsp_gsfc-eleanor-lite_tess_ffi_s0009-0000000158499577_tess_v1.0_lc.fits",
    ]
    for fn in required_raw:
        p = os.path.join(RAW_DIR, fn)
        assert os.path.isfile(p) and os.path.getsize(p) > 2, f"Missing raw file: {p}"

    assert os.path.isfile(RES_FILE), f"Missing results file: {RES_FILE}"
    with open(RES_FILE, "r", encoding="utf-8") as f:
        res = json.load(f)

    # Verify all 4 mandatory surveys are present and reported UNVERIFIED
    ms = res["mandatory_widefield_surveys"]
    for sname in ("ATLAS", "KELT-South", "HATSouth", "Evryscope"):
        assert sname in ms, f"Missing mandatory survey: {sname}"
        assert ms[sname]["covers_dec_minus36p6"] is True
        assert ms[sname]["folded_depths_P11p7672_T0_2286p3720"]["status"] == "UNVERIFIED"
        assert ms[sname]["folded_depths_P11p7672_T0_2286p3720"]["primary_depth"] == "UNVERIFIED"
        assert ms[sname]["folded_depths_P11p7672_T0_2286p3720"]["secondary_depth"] == "UNVERIFIED"

    # Verify supplementary public wide-field HLSP folds
    sup = res["supplementary_public_widefield_hlsp_folds"]
    qlp = sup["MIT_QLP_S9_S36_S63_S90_S99_S100"]
    assert 0.330 <= qlp["combined_SAP_core_hw0010"]["primary_phi0000"]["biweight_depth"] <= 0.345
    assert 0.290 <= qlp["combined_SAP_core_hw0010"]["secondary_ecc_phi05141"]["biweight_depth"] <= 0.305
    assert abs(qlp["combined_SAP_box_hw0017"]["control_phi0250"]["biweight_depth"]) < 0.001

    t16 = sup["T16_HATSouth_fitsh_Pipeline_S9"]
    assert 0.310 <= t16["IFL1_flux_box_hw0017_PRI"]["biweight_depth"] <= 0.330
    assert 0.380 <= t16["IRM1_dmag_box_hw0017_PRI"]["biweight_depth"] <= 0.430

    assert os.path.isfile(SUB_FILE), f"Missing submission file: {SUB_FILE}"
    with open(SUB_FILE, "r", encoding="utf-8") as f:
        sub_txt = f.read()
    assert 1500 <= len(sub_txt) <= 5000, f"SUBMISSION.txt length {len(sub_txt)} out of [1500, 5000] bounds"

    print(f"ALL bnty_0428 CHECKS PASSED! SUBMISSION.txt length = {len(sub_txt)} chars")
    return 0


if __name__ == "__main__":
    sys.exit(main())
