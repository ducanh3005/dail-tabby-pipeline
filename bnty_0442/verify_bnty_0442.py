#!/usr/bin/env python3
import os
import sys
import json
import subprocess

bdir = os.path.dirname(os.path.abspath(__file__))

req_files = [
    "README.md",
    "SUBMISSION.txt",
    "fold_multisurvey_0442.py",
    "raw/gaia_dr3_veb_1023231501066579840.tsv",
    "raw/gaia_dr3_neighbors_1023231501066579840_60arcsec.tsv",
    "raw/mast_tic_neighbors_1023231501066579840_60arcsec.json",
    "raw/gaia_dr3_epoch_photometry_1023231501066579840.csv",
    "raw/hlsp_qlp_tess_ffi_s0021-0000000137675945_tess_v01_llc.fits",
    "raw/hlsp_qlp_tess_ffi_s0047-0000000137675945_tess_v01_llc.fits",
    "raw/ztf_dr_lightcurves_1023231501066579840.csv",
    "raw/survey_catalog_checks_1023231501066579840_60arcsec.json",
    "raw/gaia_dr3_veb_2014878564261767680.tsv",
    "raw/gaia_dr3_neighbors_60arcsec.tsv",
    "raw/mast_tic_neighbors_60arcsec.json",
    "raw/gaia_dr3_epoch_photometry_2014878564261767680.csv",
    "raw/hlsp_qlp_tess_ffi_s0017-0000000435354753_tess_v01_llc.fits",
    "raw/hlsp_qlp_tess_ffi_s0024-0000000435354753_tess_v01_llc.fits",
    "raw/hlsp_qlp_tess_ffi_s0057-0000000435354753_tess_v01_llc.fits",
    "raw/hlsp_qlp_tess_ffi_s0058-0000000435354753_tess_v01_llc.fits",
    "raw/ztf_dr_lightcurves_2014878564261767680.csv",
    "raw/survey_catalog_checks_60arcsec.json",
    "results/multisurvey_confirmation_0442.json",
]

for rf in req_files:
    p = os.path.join(bdir, rf)
    assert os.path.exists(p) and os.path.getsize(p) > 0, f"Missing or empty {rf}"

p_run = subprocess.run([sys.executable, "fold_multisurvey_0442.py"], cwd=bdir, capture_output=True, text=True)
assert p_run.returncode == 0, f"fold_multisurvey_0442.py failed: {p_run.stderr}"

res = json.load(open(os.path.join(bdir, "results", "multisurvey_confirmation_0442.json"), encoding="utf-8"))
t1 = res["target_1_primary"]
assert t1["survey_folds"]["Leg_1_Gaia_DR3_Epoch_Photometry"]["status"] == "found"
assert t1["survey_folds"]["Leg_2_TESS_QLP_MultiSector"]["status"] == "found"
assert t1["survey_folds"]["Leg_3_ZTF_DR_Ground_CCD"]["status"] == "found"
assert t1["neighbour_flux_bound"]["max_blended_depth_within_60arcsec_T_pct"] < 8.0
assert t1["neighbour_flux_bound"]["observed_primary_depth_TESS_SAP_pct"] > 25.0

t2 = res["target_2_secondary"]
assert t2["survey_folds"]["Leg_1_Gaia_DR3_Epoch_Photometry"]["status"] == "found"
assert t2["survey_folds"]["Leg_2_TESS_QLP_MultiSector"]["status"] == "found"
assert t2["survey_folds"]["Leg_3_ZTF_DR_Ground_CCD"]["status"] == "found"
assert t2["neighbour_flux_bound"]["max_blended_depth_within_20arcsec_T_pct"] < 15.0
assert t2["neighbour_flux_bound"]["observed_primary_depth_TESS_SAP_pct"] > 40.0

sub = open(os.path.join(bdir, "SUBMISSION.txt"), encoding="utf-8").read()
assert 100 <= len(sub) <= 5000, f"SUBMISSION.txt length {len(sub)} out of bounds"
assert "curl -X" not in sub
print(f"ALL bnty_0442 CHECKS PASSED! SUBMISSION.txt length = {len(sub)} chars")
