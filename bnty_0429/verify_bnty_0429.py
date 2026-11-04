#!/usr/bin/env python3
"""
Standalone verification script for DAiL bnty_0429:
"TIC 158499577: neighbour V-band flux bound by SED fit"

Re-runs fit_sed_vband_bound.py from local raw archive files and asserts all numerical
claims, positive controls, uncertainties, and submission length constraints.
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    # 1. Execute fit_sed_vband_bound.py
    subprocess.run([sys.executable, os.path.join(HERE, "fit_sed_vband_bound.py")], check=True)

    # 2. Load generated results JSON
    res_path = os.path.join(HERE, "results", "sed_vband_bound_results.json")
    assert os.path.exists(res_path), "Missing results/sed_vband_bound_results.json"
    res = json.load(open(res_path, encoding="utf-8"))

    # 3. Verify all raw archive files exist and are non-empty
    for arch in res["observation_epoch_log"]["archives_queried"]:
        assert arch["status"] == "COMPLETE"
        for rel_f in arch["files"]:
            p = os.path.join(HERE, rel_f)
            assert os.path.exists(p) and os.path.getsize(p) > 200, f"Missing or empty raw file: {rel_f}"

    # 4. Verify positive controls
    ctrls = res["positive_controls_in_90arcsec_cone"]
    assert len(ctrls) == 2
    assert ctrls[0]["tic_id"] == "TIC 158499578"
    assert abs(ctrls[0]["v_residual_mag"]) < 0.05
    assert ctrls[1]["tic_id"] == "TIC 158499593"

    # 5. Verify target & neighbour SED fits and V-band bounds
    t0 = res["target_tic_158499577"]
    assert t0["identifiers"]["gaia_dr3_id"] == 5401019098113741568
    assert 5800.0 <= t0["sed_fit"]["teff_k"] <= 6150.0
    assert abs(t0["sed_fit"]["v_mag_adopted"] - 8.810) < 1e-4

    nb1 = res["neighbours"]["tic_942348495_1p82arcsec"]
    nb2 = res["neighbours"]["tic_942348496_2p30arcsec"]
    assert nb1["gaia_dr3_id"] == 5401019098111264000
    assert nb2["gaia_dr3_id"] == 5401019098111272064
    assert 1.80 <= nb1["separation_j2016_arcsec"] <= 1.85
    assert 2.28 <= nb2["separation_j2016_arcsec"] <= 2.33

    v_dr3 = res["v_band_and_tess_band_flux_bounds"]["v_band_gaia_dr3_sed_primary"]
    v_dr2 = res["v_band_and_tess_band_flux_bounds"]["v_band_gaia_dr2_sed_legacy"]
    assert 0.15 <= v_dr3["nb1_total_share"]["mean_pct"] <= 0.25
    assert 1.00 <= v_dr3["nb2_total_share"]["mean_pct"] <= 1.25
    assert 1.20 <= v_dr3["combined_total_share"]["mean_pct"] <= 1.45
    assert v_dr3["combined_total_share"]["p997_3sigma_upper_pct"] < 1.60
    assert v_dr2["combined_total_share"]["p997_3sigma_upper_pct"] < 2.20

    # 6. Verify house conclusion evaluation
    hc = res["house_conclusion_numerical_evaluation"]
    assert hc["changes_house_conclusion"] is False
    assert hc["required_faker_dimming_in_v_band_for_tess_26p35pct_depth"]["gaia_dr3_sed"]["nb2_alone"]["required_dimming_pct"] > 2000.0
    assert hc["required_faker_dimming_in_v_band_for_superwasp_15p98pct_depth"]["gaia_dr3_sed"]["both_combined"]["min_dimming_at_3sigma_bound_pct"] > 1000.0

    # 7. Verify SUBMISSION.txt exists and is < 5000 chars
    sub_path = os.path.join(HERE, "SUBMISSION.txt")
    assert os.path.exists(sub_path), "Missing SUBMISSION.txt"
    sub_txt = open(sub_path, encoding="utf-8").read()
    assert 1000 <= len(sub_txt) < 5000, f"SUBMISSION.txt length {len(sub_txt)} out of bounds (<5000)"

    print(f"ALL bnty_0429 CHECKS PASSED! SUBMISSION.txt length = {len(sub_txt)} chars.")


if __name__ == "__main__":
    main()
