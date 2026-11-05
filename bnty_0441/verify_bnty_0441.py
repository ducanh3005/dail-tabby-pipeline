#!/usr/bin/env python3
import os
import sys
import json
import subprocess

bdir = os.path.dirname(os.path.abspath(__file__))

req_files = [
    "README.md",
    "SUBMISSION.txt",
    "solve_sb1_orbit.py",
    "raw/apStar-dr17-2M19241736+4729134.fits",
    "raw/gaia_dr3_sources.csv",
    "raw/targetA_3413610152545407104_tbosb1.tsv",
    "raw/targetA_3413610152545407104_lamost_mrs.tsv",
    "raw/targetA_3413610152545407104_lamost_lrs_dr7.tsv",
    "raw/targetB_2129164276754246400_tbosb1.tsv",
    "raw/targetB_2129164276754246400_lamost_mrs.tsv",
    "raw/targetB_2129164276754246400_apogee_dr17.tsv",
    "results/sb1_orbit_solutions.json",
]

for rf in req_files:
    p = os.path.join(bdir, rf)
    assert os.path.exists(p) and os.path.getsize(p) > 0, f"Missing or empty {rf}"

p_run = subprocess.run([sys.executable, "solve_sb1_orbit.py"], cwd=bdir, capture_output=True, text=True)
assert p_run.returncode == 0, f"solve_sb1_orbit.py failed: {p_run.stderr}"

res = json.load(open(os.path.join(bdir, "results", "sb1_orbit_solutions.json"), encoding="utf-8"))
t1 = res["target_1_primary"]
assert len(t1["recovered_archival_epochs"]["apogee_dr17_fits_visits"]) == 4
assert len(t1["recovered_archival_epochs"]["lamost_mrs_exposures"]) == 3
assert 4.548 <= t1["joint_apogee_lamost_circular_solution"]["P_days"] <= 4.551
assert 35.5 <= t1["joint_apogee_lamost_circular_solution"]["K1_kms"] <= 37.5

t2 = res["target_2_secondary"]
assert t2["recovered_archival_epochs"]["n_lamost_mrs_exposures"] == 66
assert t2["recovered_archival_epochs"]["n_distinct_mrs_nights"] == 9
assert 330.0 <= t2["keplerian_53_exposure_solution"]["P_days"] <= 340.0

sub = open(os.path.join(bdir, "SUBMISSION.txt"), encoding="utf-8").read()
assert 100 <= len(sub) <= 5000, f"SUBMISSION.txt length {len(sub)} out of bounds"
assert "curl -X" not in sub
print(f"ALL bnty_0441 CHECKS PASSED! SUBMISSION.txt length = {len(sub)} chars")
