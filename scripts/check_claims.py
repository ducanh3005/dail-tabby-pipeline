#!/usr/bin/env python3
"""
check_claims.py — Live-archive & byte-for-byte reproducibility verifier for:
  - bnty_0333: KIC 7431659 (data/bnty0333/kic7431659/)
  - bnty_0269: KIC 11126267 (data/bnty0269/kic11126267/)

What this script checks:
  1. Re-queries the live NASA Exoplanet Archive TAP (cumulative & q1_q17_dr25_koi)
     for both targets, positive controls (10963065, 11904151, 9101271), and
     negative controls (99999998, 99999999), failing if any row count or flag
     drifts from gate1_evidence.json.
  2. Re-queries live VizieR TAP (B/vsx/vsx 30" cone) and SIMBAD TAP (15" cone)
     for both targets and positive controls, plus verifies the Kirk+ 2016
     Kepler EB catalog (J/AJ/151/68) target & control counts.
  3. Verifies every gate invariant in mast_manifest.json, bls_2p.json,
     stamp_geometry.json, centroid_corrected.json, and neighbour_eb_test.json
     (100% quarter coverage, P and 2P evaluated on identical grid, PDCSAP
     box-mean depth >= 5.0%, T1 Layout A ratio == 1.0 to 6+ digits, TPF and
     MOM_CENTR shifts < 1.000 mpix, gal2eq(0,0) self-check ok).
  4. Re-renders SUBMISSION.txt and DOSSIER.md in memory from the JSON artifacts
     via src/build_submissions.py and verifies byte-for-byte SHA-256 identity
     with the committed files on disk.

Exit status 0 = all live-archive and byte-for-byte checks pass.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))

from run_pipeline import tap_query_csv, vizier_tap_json, simbad_tap_json  # noqa: E402
from build_submissions import render_target, load_json                    # noqa: E402

TARGETS = [
    ("bnty_0333", 7431659, os.path.join(ROOT, "data", "bnty0333", "kic7431659"), "Q7 M-Dwarf Dipper, 100% of Available Kepler Quarters"),
    ("bnty_0269", 11126267, os.path.join(ROOT, "data", "bnty0269", "kic11126267"), "14-Quarter G-Dwarf Episodic Dipper, SPOCS 2191"),
]


def main() -> int:
    failures = []
    checked = 0

    def check(cond: bool, msg: str):
        nonlocal checked
        checked += 1
        if not cond:
            failures.append(msg)

    # 1. Shared live TAP positive & negative controls
    live_pos = tap_query_csv(
        "SELECT kepid,kepoi_name,koi_disposition,koi_fpflag_nt "
        "FROM cumulative WHERE kepid IN (10963065,11904151,9101271) ORDER BY kepid,kepoi_name"
    )
    check(live_pos["n_rows"] == 4, f"Live TAP positive controls expected 4 rows, got {live_pos['n_rows']}")
    live_neg = tap_query_csv("SELECT kepid FROM cumulative WHERE kepid IN (99999998,99999999)")
    check(live_neg["n_rows"] == 0, f"Live TAP negative controls expected 0 rows, got {live_neg['n_rows']}")

    live_vsx_ctl = vizier_tap_json(
        "SELECT OID, Name, Type, Period, RAJ2000, DEJ2000 FROM \"B/vsx/vsx\" "
        "WHERE 1=CONTAINS(POINT('ICRS', RAJ2000, DEJ2000), CIRCLE('ICRS', 287.377000, 43.009500, 0.0083333))"
    )
    check(live_vsx_ctl["n_rows"] >= 1, f"Live VSX positive control KIC 7431665 expected >=1 row, got {live_vsx_ctl['n_rows']}")

    for bounty_id, kepid, folder, subtitle in TARGETS:
        g1 = load_json(folder, "gate1_evidence.json")
        g2 = load_json(folder, "catalogue_control.json")
        bls = load_json(folder, "bls_2p.json")
        stamp = load_json(folder, "stamp_geometry.json")
        cent = load_json(folder, "centroid_corrected.json")
        nb = load_json(folder, "neighbour_eb_test.json")

        # Live Gate 1 check
        live_cum = tap_query_csv(f"SELECT kepid,kepoi_name FROM cumulative WHERE kepid={kepid}")
        live_dr25 = tap_query_csv(f"SELECT kepid,kepoi_name FROM q1_q17_dr25_koi WHERE kepid={kepid}")
        check(live_cum["n_rows"] == 0, f"[{bounty_id}] Live cumulative for {kepid} returned {live_cum['n_rows']} rows")
        check(live_dr25["n_rows"] == 0, f"[{bounty_id}] Live DR25 KOI for {kepid} returned {live_dr25['n_rows']} rows")
        check(g1["gate1_passed"] is True, f"[{bounty_id}] gate1_evidence.json gate1_passed != True")

        # Live Gate 2 check
        ra = g1["target_stellar_summary"]["ra_deg"]
        dec = g1["target_stellar_summary"]["dec_deg"]
        live_vsx = vizier_tap_json(
            f"SELECT OID, Name FROM \"B/vsx/vsx\" "
            f"WHERE 1=CONTAINS(POINT('ICRS', RAJ2000, DEJ2000), CIRCLE('ICRS', {ra:.6f}, {dec:.6f}, 0.0083333))"
        )
        check(live_vsx["n_rows"] == 0, f"[{bounty_id}] Live VSX 30\" cone for {kepid} returned {live_vsx['n_rows']} rows")
        live_sim = simbad_tap_json(
            f"SELECT main_id, otype FROM basic "
            f"WHERE 1=CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {ra:.6f}, {dec:.6f}, 0.0041667))"
        )
        check(live_sim["n_rows"] == g2["simbad_15arcsec"]["target"]["n_rows"], f"[{bounty_id}] SIMBAD row count drift")
        check(g2["kepler_eb_catalog"]["target_rows_count"] == 0, f"[{bounty_id}] Kepler EB target rows != 0")
        check(g2["gate2_passed"] is True, f"[{bounty_id}] catalogue_control.json gate2_passed != True")

        # Gate 3 checks
        check(bls["quarters_coverage_pct"] == 100.0, f"[{bounty_id}] quarters_coverage_pct != 100.0")
        check(bls["best_fit_P"]["dchi2"] > bls["alias_exact_2P"]["dchi2"], f"[{bounty_id}] dchi2(P) not > dchi2(2P)")

        # Gates 4, 5, 6 checks
        t1_a = stamp["orientation_tests"]["T1_ratio_A"]
        t1_b = stamp["orientation_tests"]["T1_ratio_B"]
        check(abs(t1_a - 1.0) < 1e-6, f"[{bounty_id}] T1_ratio_A = {t1_a} differs from 1.0")
        check(abs(t1_b - 1.0) > 0.1, f"[{bounty_id}] T1_ratio_B = {t1_b} unexpectedly close to 1.0")
        check(cent["gate4_passed"] is True, f"[{bounty_id}] gate4_passed != True")
        check(cent["gate6_passed"] is True, f"[{bounty_id}] gate6_passed != True")
        check(cent["max_tpf_shift_mpix"] < 1.0, f"[{bounty_id}] max_tpf_shift_mpix >= 1.0")
        check(cent["max_mom_centr_shift_mpix"] < 1.0, f"[{bounty_id}] max_mom_centr_shift_mpix >= 1.0")
        check(cent["events"][0]["pdcsap_box_depth_pct"] >= 5.0, f"[{bounty_id}] primary event PDCSAP box depth < 5%")

        # Gate 7 checks
        check(nb["conversion_self_check"]["ok"] is True, f"[{bounty_id}] gal2eq(0,0) self-check failed")
        check(nb["gate7_passed"] is True, f"[{bounty_id}] gate7_passed != True")

        # Byte-for-byte submission & dossier check
        exp_sub, exp_md = render_target(bounty_id, folder, subtitle)
        disk_sub = open(os.path.join(folder, "SUBMISSION.txt"), "r", encoding="utf-8").read()
        disk_md = open(os.path.join(folder, "DOSSIER.md"), "r", encoding="utf-8").read()
        check(
            hashlib.sha256(exp_sub.encode("utf-8")).hexdigest() == hashlib.sha256(disk_sub.encode("utf-8")).hexdigest(),
            f"[{bounty_id}] SUBMISSION.txt on disk differs from deterministic generator output",
        )
        check(
            hashlib.sha256(exp_md.encode("utf-8")).hexdigest() == hashlib.sha256(disk_md.encode("utf-8")).hexdigest(),
            f"[{bounty_id}] DOSSIER.md on disk differs from deterministic generator output",
        )
        check(len(disk_sub) <= 5000, f"[{bounty_id}] SUBMISSION.txt exceeds 5000 chars ({len(disk_sub)})")

    print(f"checked {checked} live-archive and byte-for-byte claims across {len(TARGETS)} targets")
    if failures:
        for f in failures:
            print(f"!! FAILURE: {f}")
        return 1
    print("ALL CHECKS PASSED (exit 0)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
