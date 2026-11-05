#!/usr/bin/env python3
"""
Verification suite for DAiL bnty_0439:
Fermi-LAT 4FGL-DR4 Unassociated Sources — Vetted Counterparts, Quantified.
"""
import csv
import json
import os
import shutil
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "raw")
RES_DIR = os.path.join(BASE_DIR, "results")

PREVIOUSLY_CLAIMED_DAIL = {
    "J0226.9+7744", "J0843.7-6933", "J1058.4-6625", "J1225.9+2951",
    "J1250.9-4943", "J1338.0-4159", "J1441.4-1934", "J1514.8+4448",
    "J1613.1-3840", "J1754.1-4333", "J1842.1+2737", "J1910.8+2856",
    "J1916.8-3025", "J1927.5+0154", "J2108.7-0408", "J2112.5-3043",
}

EXPECTED_SOURCES = ["J2240.3-5241", "J1410.7+7405", "J0251.1-1830", "J1539.4-3323"]
HEASARC_CATS = [
    "fermilpsc", "swift2sxps", "rass2rxs", "xmmssc", "csc",
    "nvss", "sumss", "first", "vlssr", "milliquas", "wibrals", "romabzcat", "atnfpulsar"
]

def main():
    src_unassoc = os.path.join(os.path.dirname(BASE_DIR), "bnty_0348", "raw", "unassociated.json")
    dst_unassoc = os.path.join(RAW_DIR, "unassociated_4fgl_dr4.json")
    if not os.path.exists(dst_unassoc) and os.path.exists(src_unassoc):
        shutil.copyfile(src_unassoc, dst_unassoc)

    assert os.path.exists(dst_unassoc), "Missing raw/unassociated_4fgl_dr4.json"
    unassoc = {x["name"]: x for x in json.load(open(dst_unassoc, encoding="utf-8"))}

    for s in EXPECTED_SOURCES:
        assert s not in PREVIOUSLY_CLAIMED_DAIL, f"{s} was previously claimed in DAiL!"
        assert s in unassoc, f"{s} missing from 4FGL-DR4 unassociated list"
        assert unassoc[s]["cl1"].strip() == "", f"{s} has non-empty class {unassoc[s]['cl1']}"
        assert os.path.getsize(os.path.join(RAW_DIR, f"{s}_mast_tic_3arcmin.json")) > 100
        assert os.path.getsize(os.path.join(RAW_DIR, f"{s}_ned_3arcmin.txt")) > 100
        for cat in HEASARC_CATS:
            p = os.path.join(RAW_DIR, f"{s}_heasarc_{cat}.txt")
            assert os.path.exists(p) and os.path.getsize(p) > 10, f"Missing raw HEASARC {p}"

    dossier_path = os.path.join(RES_DIR, "fermi_vetted_counterparts.json")
    csv1_path = os.path.join(RES_DIR, "in_ellipse_counterparts.csv")
    csv2_path = os.path.join(RES_DIR, "source_summary_table.csv")
    assert os.path.exists(dossier_path), "Missing results/fermi_vetted_counterparts.json"
    assert os.path.exists(csv1_path), "Missing results/in_ellipse_counterparts.csv"
    assert os.path.exists(csv2_path), "Missing results/source_summary_table.csv"

    dossier = json.load(open(dossier_path, encoding="utf-8"))
    assert len(dossier["sources"]) == 4

    s0, s1, s2, s3 = dossier["sources"]
    assert s0["counts"]["mast_tic_in_ellipse"] == 13 and s0["counts"]["ned_in_ellipse"] == 28
    assert s1["counts"]["mast_tic_in_ellipse"] == 6 and s1["counts"]["ned_in_ellipse"] == 27
    assert s2["counts"]["mast_tic_in_ellipse"] == 8 and s2["counts"]["ned_in_ellipse"] == 77
    assert s3["counts"]["mast_tic_in_ellipse"] == 35 and s3["counts"]["ned_in_ellipse"] == 65

    rows_cp = list(csv.DictReader(open(csv1_path, encoding="utf-8")))
    assert len(rows_cp) == 73, f"Expected 73 in-ellipse rows, got {len(rows_cp)}"

    sub_path = os.path.join(BASE_DIR, "SUBMISSION.txt")
    assert os.path.exists(sub_path), "Missing SUBMISSION.txt"
    sub_txt = open(sub_path, encoding="utf-8").read()
    assert 1500 <= len(sub_txt) <= 5000, f"SUBMISSION.txt length {len(sub_txt)} out of [1500, 5000]"

    for req in [
        "4FGL J2240.3-5241", "4FGL J1410.7+7405", "4FGL J0251.1-1830", "4FGL J1539.4-3323",
        "WISEA J224017.71-524113.8", "SUMSS J224017-524111", "5XMM J224017.8-524114", "3HSPJ224017.1-524113",
        "2SXPS J141045.6+740511", "3HSPJ141046.0+740511", "WISEA J141046.00+740511.2",
        "NVSS J025111-183112", "2SXPS J025111.4-183114", "3HSPJ025111.5-183112",
        "UNUSABLE", "0.00719", "0.00538", "0.04190",
    ]:
        assert req in sub_txt, f"Missing required string in SUBMISSION.txt: {req}"

    print(f"ALL bnty_0439 CHECKS PASSED! 61 raw files verified, 73 in-ellipse counterparts vetted, SUBMISSION.txt = {len(sub_txt)} chars")
    return 0

if __name__ == "__main__":
    sys.exit(main())
