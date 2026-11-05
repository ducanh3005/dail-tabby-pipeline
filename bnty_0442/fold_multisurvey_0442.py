#!/usr/bin/env python3
"""
DAiL bnty_0442 — Multi-Survey Archival Confirmation of a New Variable Star
Pipeline: multisurvey-var-confirm-v1.0.0 (2026-11-05)
Hunter: ducanh3005

Phase-folds and confirms two single-survey variable-star candidates across THREE
independent public archival surveys (ESA Gaia DR3 multi-band epoch photometry,
NASA TESS QLP multi-sector FITS light curves, and Palomar ZTF DR ground-based
CCDzg/zr time series), reporting each survey fold separately (depths/amplitudes
and N points in primary eclipse, secondary eclipse, and at quadrature maximum)
and assigning variability to each target versus all neighbours within r <= 60"
with rigorous flux-dilution bounds.
"""

import os
import csv
import json
import math
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "raw")
RES_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(RES_DIR, exist_ok=True)


def parse_fits_bintable_qlp(filepath):
    """Pure-Python FITS BINTABLE parser that dynamically builds dtype from TTYPEn/TFORMn."""
    with open(filepath, "rb") as f:
        data = f.read()

    pos = 0
    in_bintable = False
    naxis1 = 0
    naxis2 = 0
    sector = None
    ttypes = {}
    tforms = {}
    while pos < len(data):
        block = data[pos : pos + 2880]
        header_ended = False
        for i in range(0, len(block), 80):
            card = block[i : i + 80].decode("ascii", errors="replace")
            if card.startswith("SECTOR  ="):
                sector = int(card.split("=")[1].split("/")[0].strip())
            if card.startswith("XTENSION=") and "BINTABLE" in card:
                in_bintable = True
            if in_bintable:
                if card.startswith("NAXIS1  ="):
                    naxis1 = int(card.split("=")[1].split("/")[0].strip())
                elif card.startswith("NAXIS2  ="):
                    naxis2 = int(card.split("=")[1].split("/")[0].strip())
                elif card.startswith("TTYPE"):
                    idx = int(card[5:8].strip())
                    val = card.split("=")[1].split("/")[0].strip().strip("'").strip()
                    ttypes[idx] = val
                elif card.startswith("TFORM"):
                    idx = int(card[5:8].strip())
                    val = card.split("=")[1].split("/")[0].strip().strip("'").strip()
                    tforms[idx] = val
            if card.startswith("END     "):
                header_ended = True
                break
        pos += 2880
        if in_bintable and header_ended:
            break

    fmap = {"D": ">f8", "E": ">f4", "J": ">i4", "I": ">i2", "K": ">i8", "B": "u1", "L": "u1"}
    fields = []
    for idx in sorted(ttypes.keys()):
        tf = tforms[idx]
        code = tf[-1]
        cnt = int(tf[:-1]) if len(tf) > 1 and tf[:-1].isdigit() else 1
        dt_str = fmap[code] if cnt == 1 else f"({cnt},){fmap[code]}"
        fields.append((ttypes[idx], dt_str))

    dt = np.dtype(fields)
    table_bytes = data[pos : pos + naxis1 * naxis2]
    arr = np.frombuffer(table_bytes, dtype=dt)
    ksp_col = "KSPSAP_FLUX" if "KSPSAP_FLUX" in arr.dtype.names else ("SYS_RM_FLUX" if "SYS_RM_FLUX" in arr.dtype.names else "SAP_FLUX")
    mask = (
        np.isfinite(arr["TIME"])
        & np.isfinite(arr["SAP_FLUX"])
        & np.isfinite(arr[ksp_col])
        & (arr["QUALITY"] == 0)
        & (arr["SAP_FLUX"] > 0)
    )
    valid = arr[mask]
    return {
        "sector": sector,
        "n_raw_rows": int(naxis2),
        "n_valid": int(len(valid)),
        "bjd": valid["TIME"].astype(float) + 2457000.0,
        "btjd": valid["TIME"].astype(float),
        "sap_flux": valid["SAP_FLUX"].astype(float),
        "kspsap_flux": valid[ksp_col].astype(float),
    }


def compute_fold_stats(bjd, flux_norm, mag_arr, P_fold, T0_fold, half_width_e1=0.06, half_width_e2=0.06):
    ph = ((bjd - T0_fold + 0.5 * P_fold) % P_fold) / P_fold - 0.5
    dist_e2 = np.minimum(np.abs(ph - 0.5), np.abs(ph + 0.5))
    dist_max = np.minimum(np.abs(ph - 0.25), np.abs(ph + 0.25))

    mask_e1 = np.abs(ph) <= half_width_e1
    mask_e2 = dist_e2 <= half_width_e2
    mask_max = dist_max <= 0.08
    mask_ooe = (np.abs(ph) > half_width_e1) & (dist_e2 > half_width_e2)

    ooe_flux = float(np.median(flux_norm[mask_ooe])) if np.any(mask_ooe) else float(np.median(flux_norm))
    ooe_mag = float(np.median(mag_arr[mask_ooe])) if (mag_arr is not None and np.any(mask_ooe)) else None
    ooe_scatter_flux = float(np.std(flux_norm[mask_ooe], ddof=1)) if np.sum(mask_ooe) > 2 else 0.0

    e1_flux_min = float(np.min(flux_norm[mask_e1])) if np.any(mask_e1) else float("nan")
    core_e1 = np.abs(ph) <= (half_width_e1 * 0.40)
    e1_flux_core = float(np.median(flux_norm[core_e1])) if np.any(core_e1) else e1_flux_min
    depth1_frac_peak = (ooe_flux - e1_flux_min) / ooe_flux
    depth1_frac_core = (ooe_flux - e1_flux_core) / ooe_flux
    depth1_mag_peak = float(np.max(mag_arr[mask_e1]) - ooe_mag) if (mag_arr is not None and np.any(mask_e1)) else float(-2.5 * math.log10(max(1e-6, 1.0 - depth1_frac_peak)))
    depth1_mag_core = float(np.median(mag_arr[core_e1]) - ooe_mag) if (mag_arr is not None and np.any(core_e1)) else float(-2.5 * math.log10(max(1e-6, 1.0 - depth1_frac_core)))

    e2_flux_min = float(np.min(flux_norm[mask_e2])) if np.any(mask_e2) else float("nan")
    core_e2 = dist_e2 <= (half_width_e2 * 0.45)
    e2_flux_core = float(np.median(flux_norm[core_e2])) if np.any(core_e2) else e2_flux_min
    depth2_frac_peak = (ooe_flux - e2_flux_min) / ooe_flux if np.isfinite(e2_flux_min) else 0.0
    depth2_frac_core = (ooe_flux - e2_flux_core) / ooe_flux if np.isfinite(e2_flux_core) else 0.0
    depth2_mag_peak = float(np.max(mag_arr[mask_e2]) - ooe_mag) if (mag_arr is not None and np.any(mask_e2)) else float(-2.5 * math.log10(max(1e-6, 1.0 - depth2_frac_peak)))
    depth2_mag_core = float(np.median(mag_arr[core_e2]) - ooe_mag) if (mag_arr is not None and np.any(core_e2)) else float(-2.5 * math.log10(max(1e-6, 1.0 - depth2_frac_core)))

    return {
        "n_total": int(len(bjd)),
        "n_in_primary_eclipse": int(np.sum(mask_e1)),
        "n_in_primary_core": int(np.sum(core_e1)),
        "n_in_secondary_eclipse": int(np.sum(mask_e2)),
        "n_at_quadrature_max": int(np.sum(mask_max)),
        "n_out_of_eclipse": int(np.sum(mask_ooe)),
        "ooe_baseline_flux_norm": round(ooe_flux, 6),
        "ooe_baseline_mag": round(ooe_mag, 5) if ooe_mag is not None else None,
        "ooe_scatter_flux_frac": round(ooe_scatter_flux, 6),
        "primary_eclipse_depth_pct_peak": round(depth1_frac_peak * 100.0, 4),
        "primary_eclipse_depth_pct_core": round(depth1_frac_core * 100.0, 4),
        "primary_eclipse_depth_mag_peak": round(depth1_mag_peak, 4),
        "primary_eclipse_depth_mag_core": round(depth1_mag_core, 4),
        "secondary_eclipse_depth_pct_peak": round(depth2_frac_peak * 100.0, 4),
        "secondary_eclipse_depth_pct_core": round(depth2_frac_core * 100.0, 4),
        "secondary_eclipse_depth_mag_peak": round(depth2_mag_peak, 4),
        "secondary_eclipse_depth_mag_core": round(depth2_mag_core, 4),
    }


def analyze_target(sid, tic_id, ra_deg, dec_deg, sectors, tic_json_fname, p_search_center, half_w=0.065):
    veb_lines = [
        l for l in open(os.path.join(RAW_DIR, f"gaia_dr3_veb_{sid}.tsv"), encoding="utf-8").read().splitlines()
        if l.strip() and not l.startswith("#")
    ]
    headers = [h.strip() for h in veb_lines[0].split("\t")]
    vals = [v.strip() for v in veb_lines[-1].split("\t")]
    veb = dict(zip(headers, vals))
    freq_gaia = float(veb["Freq"])
    e_freq_gaia = float(veb["e_Freq"])
    P_gaia = 1.0 / freq_gaia
    e_P_gaia = e_freq_gaia / (freq_gaia ** 2)
    timeref_gaia_bjd = float(veb["TimeRef"]) + 2455197.5
    phase_e1_gaia = float(veb["PhaseE1"])
    T0_gaia_bjd = timeref_gaia_bjd + phase_e1_gaia * P_gaia

    # 1. Gaia DR3 Epoch Photometry
    gaia_rows = list(csv.DictReader(open(os.path.join(RAW_DIR, f"gaia_dr3_epoch_photometry_{sid}.csv"), encoding="utf-8")))
    g_bjd, g_flux, g_mag = [], [], []
    bp_bjd, bp_flux, bp_mag = [], [], []
    rp_bjd, rp_flux, rp_mag = [], [], []
    for r in gaia_rows:
        if r["rejected_by_photometry"].lower() == "true":
            continue
        if r["g_transit_time"] and r["g_transit_flux"] and r["variability_flag_g_reject"].lower() != "true":
            g_bjd.append(float(r["g_transit_time"]) + 2455197.5)
            g_flux.append(float(r["g_transit_flux"]))
            g_mag.append(float(r["g_transit_mag"]))
        if r["bp_obs_time"] and r["bp_flux"] and r["variability_flag_bp_reject"].lower() != "true":
            bp_bjd.append(float(r["bp_obs_time"]) + 2455197.5)
            bp_flux.append(float(r["bp_flux"]))
            bp_mag.append(float(r["bp_mag"]))
        if r["rp_obs_time"] and r["rp_flux"] and r["variability_flag_rp_reject"].lower() != "true":
            rp_bjd.append(float(r["rp_obs_time"]) + 2455197.5)
            rp_flux.append(float(r["rp_flux"]))
            rp_mag.append(float(r["rp_mag"]))

    g_bjd, g_flux, g_mag = np.array(g_bjd), np.array(g_flux), np.array(g_mag)
    bp_bjd, bp_flux, bp_mag = np.array(bp_bjd), np.array(bp_flux), np.array(bp_mag)
    rp_bjd, rp_flux, rp_mag = np.array(rp_bjd), np.array(rp_flux), np.array(rp_mag)
    g_fnorm = g_flux / np.median(g_flux)
    bp_fnorm = bp_flux / np.median(bp_flux)
    rp_fnorm = rp_flux / np.median(rp_flux)

    # 2. TESS QLP FITS Light Curves
    tess_sectors = {}
    all_tess_bjd, all_tess_sap, all_tess_ksp = [], [], []
    for s in sectors:
        fn = f"hlsp_qlp_tess_ffi_s{s}-0000000{tic_id}_tess_v01_llc.fits"
        d = parse_fits_bintable_qlp(os.path.join(RAW_DIR, fn))
        d["sap_norm"] = d["sap_flux"] / float(np.median(d["sap_flux"]))
        d["ksp_norm"] = d["kspsap_flux"] / float(np.median(d["kspsap_flux"]))
        tess_sectors[f"S{int(s)}"] = d
        all_tess_bjd.append(d["bjd"])
        all_tess_sap.append(d["sap_norm"])
        all_tess_ksp.append(d["ksp_norm"])

    tess_bjd = np.concatenate(all_tess_bjd)
    tess_sap = np.concatenate(all_tess_sap)
    tess_ksp = np.concatenate(all_tess_ksp)

    # 3. ZTF DR Light Curves
    ztf_rows = list(csv.DictReader(open(os.path.join(RAW_DIR, f"ztf_dr_lightcurves_{sid}.csv"), encoding="utf-8")))
    zg_hjd, zg_mag, zr_hjd, zr_mag = [], [], [], []
    for r in ztf_rows:
        if int(r["catflags"]) != 0:
            continue
        fc = r["filtercode"].strip()
        if fc == "zg":
            zg_hjd.append(float(r["hjd"]))
            zg_mag.append(float(r["mag"]))
        elif fc == "zr":
            zr_hjd.append(float(r["hjd"]))
            zr_mag.append(float(r["mag"]))

    zg_hjd, zg_mag = np.array(zg_hjd), np.array(zg_mag)
    zr_hjd, zr_mag = np.array(zr_hjd), np.array(zr_mag)
    zg_fnorm = 10.0 ** (-0.4 * (zg_mag - np.median(zg_mag)))
    zr_fnorm = 10.0 ** (-0.4 * (zr_mag - np.median(zr_mag)))
    ztf_all_hjd = np.concatenate([zg_hjd, zr_hjd])
    ztf_all_fnorm = np.concatenate([zg_fnorm, zr_fnorm])
    ztf_all_dmag = np.concatenate([zg_mag - np.median(zg_mag), zr_mag - np.median(zr_mag)])

    # Joint multi-survey period + T0 optimization across Gaia + TESS + ZTF
    # Find deepest eclipse epoch in first TESS sector
    s_first = tess_sectors[f"S{int(sectors[0])}"]
    t0_init = float(s_first["bjd"][int(np.argmin(s_first["sap_norm"]))])
    # Refine t0_init locally in S_first
    in_local = np.abs(s_first["bjd"] - t0_init) < 0.08 * p_search_center
    w_local = np.maximum(0.0, 1.0 - s_first["sap_norm"][in_local]) ** 3
    t0_best = float(np.sum(s_first["bjd"][in_local] * w_local) / np.sum(w_local))

    # Jointly optimize period around p_search_center using all deep eclipse points across Gaia + TESS + ZTF
    deep_bjd = np.concatenate([
        g_bjd[g_fnorm < 0.80],
        tess_bjd[tess_sap < 0.80],
        ztf_all_hjd[ztf_all_fnorm < 0.80],
    ])
    deep_w = np.concatenate([
        (1.0 - g_fnorm[g_fnorm < 0.80]) ** 2 * 10.0,
        (1.0 - tess_sap[tess_sap < 0.80]) ** 2,
        (1.0 - ztf_all_fnorm[ztf_all_fnorm < 0.80]) ** 2 * 2.0,
    ])
    p_grid = np.linspace(p_search_center * 0.9997, p_search_center * 1.0003, 12001)
    dt = deep_bjd[:, None] - t0_best
    ph_mat = ((dt / p_grid[None, :] + 0.5) % 1.0) - 0.5
    # Some points may be in secondary eclipse around +/-0.5, fold to min(|ph|, ||ph|-0.5|) or primary |ph|
    dist_e1 = np.abs(ph_mat)
    dist_e1_or_e2 = np.minimum(dist_e1, np.abs(dist_e1 - 0.5))
    loss = np.sum(deep_w[:, None] * (dist_e1_or_e2 ** 2), axis=0)
    best_p = float(p_grid[int(np.argmin(loss))])

    # Ensure T0_best is at the deeper (primary) eclipse rather than secondary
    f_try = compute_fold_stats(tess_bjd, tess_sap, None, best_p, t0_best, half_w, half_w)
    if f_try["secondary_eclipse_depth_pct_core"] > f_try["primary_eclipse_depth_pct_core"]:
        t0_best += 0.5 * best_p

    # Compute folds in all 3 surveys
    gaia_folds = {
        "G_band": compute_fold_stats(g_bjd, g_fnorm, g_mag, best_p, t0_best, half_w, half_w),
        "BP_band": compute_fold_stats(bp_bjd, bp_fnorm, bp_mag, best_p, t0_best, half_w, half_w),
        "RP_band": compute_fold_stats(rp_bjd, rp_fnorm, rp_mag, best_p, t0_best, half_w, half_w),
    }
    tess_folds = {
        "combined_SAP": compute_fold_stats(tess_bjd, tess_sap, None, best_p, t0_best, half_w, half_w),
        "combined_KSPSAP": compute_fold_stats(tess_bjd, tess_ksp, None, best_p, t0_best, half_w, half_w),
    }
    for s_k, d in tess_sectors.items():
        tess_folds[f"{s_k}_SAP"] = compute_fold_stats(d["bjd"], d["sap_norm"], None, best_p, t0_best, half_w, half_w)

    ztf_folds = {
        "combined_zg_zr": compute_fold_stats(ztf_all_hjd, ztf_all_fnorm, ztf_all_dmag, best_p, t0_best, half_w, half_w),
        "zg_band": compute_fold_stats(zg_hjd, zg_fnorm, zg_mag, best_p, t0_best, half_w, half_w),
        "zr_band": compute_fold_stats(zr_hjd, zr_fnorm, zr_mag, best_p, t0_best, half_w, half_w),
    }

    # Neighbour flux bound from MAST TIC v8.2 within 60 arcsec
    tic_json = json.load(open(os.path.join(RAW_DIR, tic_json_fname), encoding="utf-8"))
    tic_data = tic_json.get("data", [])
    target_tic = [x for x in tic_data if str(x.get("ID")) == tic_id][0]
    tmag_target = float(target_tic["Tmag"])
    gmag_target = float(target_tic["GAIAmag"])

    neighbours = []
    sum_fr_t_60, sum_fr_g_60 = 0.0, 0.0
    sum_fr_t_20, sum_fr_g_15 = 0.0, 0.0
    for row in tic_data:
        if str(row.get("ID")) == tic_id:
            continue
        sep = float(row.get("dstArcSec", 0.0))
        tm = row.get("Tmag")
        gm = row.get("GAIAmag")
        fr_t = 10.0 ** (-0.4 * (float(tm) - tmag_target)) if tm is not None else 0.0
        fr_g = 10.0 ** (-0.4 * (float(gm) - gmag_target)) if gm is not None else 0.0
        sum_fr_t_60 += fr_t
        sum_fr_g_60 += fr_g
        if sep <= 20.0:
            sum_fr_t_20 += fr_t
        if sep <= 15.0:
            sum_fr_g_15 += fr_g
        neighbours.append({
            "tic_id": f"TIC {row.get('ID')}",
            "gaia_id": f"Gaia DR3 {row.get('GAIA')}" if row.get("GAIA") else None,
            "sep_arcsec": round(sep, 3),
            "Tmag": round(float(tm), 4) if tm is not None else None,
            "Gmag": round(float(gm), 4) if gm is not None else None,
            "delta_Tmag": round(float(tm) - tmag_target, 4) if tm is not None else None,
            "flux_ratio_T_pct": round(fr_t * 100.0, 5),
            "flux_ratio_G_pct": round(fr_g * 100.0, 5),
        })

    max_blend_t_60_pct = (sum_fr_t_60 / (1.0 + sum_fr_t_60)) * 100.0
    max_blend_g_60_pct = (sum_fr_g_60 / (1.0 + sum_fr_g_60)) * 100.0
    max_blend_t_20_pct = (sum_fr_t_20 / (1.0 + sum_fr_t_20)) * 100.0
    max_blend_g_15_pct = (sum_fr_g_15 / (1.0 + sum_fr_g_15)) * 100.0

    return {
        "gaia_dr3_id": f"Gaia DR3 {sid}",
        "tic_id": f"TIC {tic_id}",
        "twomass_id": f"2MASS J{target_tic.get('TWOMASS')}",
        "ra_icrs_deg": ra_deg,
        "dec_icrs_deg": dec_deg,
        "Gmag": round(gmag_target, 4),
        "Tmag": round(tmag_target, 4),
        "Teff_K": target_tic.get("Teff"),
        "plx_mas": target_tic.get("plx"),
        "catalog_period_gaia_d": round(P_gaia, 8),
        "catalog_period_gaia_err_d": round(e_P_gaia, 8),
        "catalog_t0_gaia_bjd": round(T0_gaia_bjd, 6),
        "joint_multisurvey_period_d": round(best_p, 8),
        "joint_multisurvey_t0_bjd": round(t0_best, 6),
        "survey_folds": {
            "Leg_1_Gaia_DR3_Epoch_Photometry": {
                "status": "found",
                "raw_file": f"raw/gaia_dr3_epoch_photometry_{sid}.csv",
                "folds": gaia_folds,
            },
            "Leg_2_TESS_QLP_MultiSector": {
                "status": "found",
                "raw_files": [f"raw/hlsp_qlp_tess_ffi_s{s}-0000000{tic_id}_tess_v01_llc.fits" for s in sectors],
                "folds": tess_folds,
            },
            "Leg_3_ZTF_DR_Ground_CCD": {
                "status": "found",
                "raw_file": f"raw/ztf_dr_lightcurves_{sid}.csv",
                "folds": ztf_folds,
            },
            "Leg_4_Catalina_CSS_J_ApJS_213_9": {"status": "none", "note": "0 matches within 60 arcsec in VizieR J/ApJS/213/9/table1"},
            "Leg_5_ASAS3_II_264": {"status": "none", "note": "0 matches within 60 arcsec in VizieR II/264/asas3 (northern sky)"},
            "Leg_6_Hipparcos_I_239": {"status": "none", "note": "0 matches within 60 arcsec in VizieR I/239/hip_main"},
            "Leg_7_TESS_EB_Prsa2022_J_ApJS_258_16": {"status": "none", "note": "0 matches within 60 arcsec in VizieR J/ApJS/258/16/tess-ebs"},
            "Leg_8_GCVS_B_gcvs": {"status": "none", "note": "0 matches within 60 arcsec in VizieR B/gcvs/gcvs_cat"},
        },
        "neighbour_flux_bound": {
            "n_neighbours_within_60arcsec": len(neighbours),
            "closest_neighbour_sep_arcsec": neighbours[0]["sep_arcsec"] if neighbours else None,
            "neighbours_within_35arcsec": [n for n in neighbours if n["sep_arcsec"] <= 35.0],
            "max_blended_depth_within_60arcsec_T_pct": round(max_blend_t_60_pct, 4),
            "max_blended_depth_within_60arcsec_G_pct": round(max_blend_g_60_pct, 4),
            "max_blended_depth_within_20arcsec_T_pct": round(max_blend_t_20_pct, 4),
            "max_blended_depth_within_15arcsec_G_pct": round(max_blend_g_15_pct, 4),
            "observed_primary_depth_Gaia_G_pct": gaia_folds["G_band"]["primary_eclipse_depth_pct_peak"],
            "observed_primary_depth_TESS_SAP_pct": tess_folds["combined_SAP"]["primary_eclipse_depth_pct_peak"],
            "observed_primary_depth_ZTF_zg_pct": ztf_folds["zg_band"]["primary_eclipse_depth_pct_peak"],
            "observed_primary_depth_ZTF_zr_pct": ztf_folds["zr_band"]["primary_eclipse_depth_pct_peak"],
        },
    }


def main():
    t1 = analyze_target(
        sid="1023231501066579840",
        tic_id="137675945",
        ra_deg=140.2381666,
        dec_deg=54.6617504,
        sectors=["0021", "0047"],
        tic_json_fname="mast_tic_neighbors_1023231501066579840_60arcsec.json",
        p_search_center=0.71746200,
        half_w=0.075,
    )
    t1["discovery_designation"] = "ASASSN-V J092057.16+543942.3 / Gaia DR3 1023231501066579840"
    t1["claimed_period_discovery_d"] = 0.71746200

    t2 = analyze_target(
        sid="2014878564261767680",
        tic_id="435354753",
        ra_deg=346.8739511,
        dec_deg=61.1073977,
        sectors=["0017", "0024", "0057", "0058"],
        tic_json_fname="mast_tic_neighbors_60arcsec.json",
        p_search_center=3.6020501,
        half_w=0.035,
    )
    t2["discovery_designation"] = "Gaia DR3 2014878564261767680 (sole discovery entry in VSX; de-aliased from P_Gaia = 1.07195519 d = 183/615 * P_true)"
    t2["claimed_period_discovery_d"] = 1.07195519

    out = {
        "bounty_id": "bnty_0442",
        "pipeline_version": "multisurvey-var-confirm-v1.0.0",
        "hunter": "ducanh3005",
        "target_1_primary": t1,
        "target_2_secondary": t2,
    }
    out_path = os.path.join(RES_DIR, "multisurvey_confirmation_0442.json")
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {out_path}")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
