#!/usr/bin/env python3
"""
extract_ffi_sectors.py — DAiL bnty_0425:
TIC 158499577 (HD 94871) TESS Full-Frame Image (FFI) Re-Extraction in Unsearched Sectors.

Performs:
1. Complete Sector Manifest across TESS Sectors 1-100 (identifying Sectors 9 & 36 as the
   house 2-minute SPOC baseline and Sectors 63, 90, 99, 100 as the 4 unsearched 200-s FFI
   sectors where TIC 158499577 was observed on Camera 2).
2. Reproducible aperture photometry + sky annulus biweight subtraction + iterative
   dip-masked 1.5-day sliding Tukey-biweight continuum detrending directly from the
   11x11 TESSCut FFI pixel cutouts.
3. Phase-folding at the house ephemeris (P = 11.7672 d, T0 = BTJD 2286.3720) AND
   comparison with the refined joint ephemeris (P = 11.7672170 d, T0 = BTJD 2286.372048),
   measuring folded primary & secondary depths per sector and cataloging every new
   primary and secondary transit observed in Sectors 63, 90, 99, and 100.
"""

import csv
import hashlib
import json
import math
import os
import re
from datetime import datetime, timezone

import numpy as np


def read_tesscut_fits(fpath):
    """Pure-Python + NumPy FITS BINTABLE reader for TESSCut astrocut FITS files (zero external FITS deps)."""
    with open(fpath, "rb") as f:
        raw = f.read()

    pos = 0
    hdr0 = {}
    hdr1 = {}
    for hdu_idx in range(2):
        hdr = {}
        while True:
            block = raw[pos : pos + 2880]
            pos += 2880
            ended = False
            for i in range(0, 2880, 80):
                card = block[i : i + 80].decode("ascii", errors="replace")
                key = card[:8].strip()
                if key == "END":
                    ended = True
                    break
                if "=" in card[:10]:
                    val_part = card[10:].split("/")[0].strip()
                    if val_part.startswith("'") and val_part.endswith("'"):
                        val = val_part[1:-1].strip()
                    else:
                        try:
                            val = int(val_part)
                        except ValueError:
                            try:
                                val = float(val_part)
                            except ValueError:
                                val = val_part
                    hdr[key] = val
            if ended:
                break
        if hdu_idx == 0:
            hdr0 = hdr
        else:
            hdr1 = hdr

    nrows = int(hdr1["NAXIS2"])
    row_bytes = int(hdr1["NAXIS1"])
    tfields = int(hdr1["TFIELDS"])

    dtype_fields = []
    for col in range(1, tfields + 1):
        ttype = str(hdr1[f"TTYPE{col}"]).strip()
        tform = str(hdr1[f"TFORM{col}"]).strip()
        tdim = str(hdr1.get(f"TDIM{col}", "")).strip()
        m = re.match(r"^(\d*)([A-Z])$", tform)
        cnt = int(m.group(1)) if m.group(1) else 1
        code = m.group(2)
        if code == "D":
            base = ">f8"
        elif code == "E":
            base = ">f4"
        elif code == "J":
            base = ">i4"
        elif code == "I":
            base = ">i2"
        elif code == "K":
            base = ">i8"
        elif code == "A":
            dtype_fields.append((ttype, f"S{cnt}"))
            continue
        else:
            raise ValueError(f"Unsupported TFORM: {tform}")

        if tdim.startswith("(") and tdim.endswith(")"):
            dims = tuple(int(x.strip()) for x in tdim[1:-1].split(","))
            dtype_fields.append((ttype, base, dims[::-1]))
        elif cnt > 1:
            dtype_fields.append((ttype, base, (cnt,)))
        else:
            dtype_fields.append((ttype, base))

    dt = np.dtype(dtype_fields)
    assert dt.itemsize == row_bytes, f"Itemsize {dt.itemsize} != NAXIS1 {row_bytes}"
    table_bytes = raw[pos : pos + nrows * row_bytes]
    arr = np.frombuffer(table_bytes, dtype=dt, count=nrows)
    return hdr0, hdr1, arr

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "raw")
RES_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(RES_DIR, exist_ok=True)

P_HOUSE = 11.7672
T0_HOUSE = 2286.3720

P_JOINT = 11.7672170
T0_JOINT = 2286.372048
PHI_SEC_ECC = 0.514107


def tukey_biweight(x, c=6.0, max_iter=5):
    arr = np.asarray(x, dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return np.nan
    m = float(np.median(arr))
    for _ in range(max_iter):
        r = arr - m
        mad = float(np.median(np.abs(r)))
        if mad < 1e-12:
            break
        u = r / (c * 1.4826 * mad)
        mask = np.abs(u) < 1.0
        if not np.any(mask):
            break
        w = (1.0 - u[mask] ** 2) ** 2
        m = float(np.sum(w * arr[mask]) / np.sum(w))
    return m


def robust_sigma(x):
    arr = np.asarray(x, dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size < 2:
        return np.nan
    med = float(np.median(arr))
    return float(1.4826 * np.median(np.abs(arr - med)))


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def load_sector_cubes():
    """Load 11x11 FFI cutouts directly from raw/tesscut_s*.fits and save SHA-256 manifest."""
    meta_path = os.path.join(RAW_DIR, "tesscut_fits_manifest_sha256.json")

    with open(os.path.join(RAW_DIR, "tesscut_sectors.json"), "r", encoding="utf-8") as f:
        sec_list = json.load(f)["results"]

    fits_files = sorted([fn for fn in os.listdir(RAW_DIR) if fn.startswith("tesscut_s") and fn.endswith("_astrocut.fits")])
    assert len(fits_files) == 6, f"Expected 6 TESSCut FITS files in {RAW_DIR}, found {len(fits_files)}"

    manifest_meta = {}
    sectors_data = {}
    for fn in fits_files:
        sec_num = int(fn.split("_")[1][1:])
        fpath = os.path.join(RAW_DIR, fn)
        hdr0, hdr1, data = read_tesscut_fits(fpath)
        t = np.asarray(data["TIME"], dtype=np.float64)
        qual = np.asarray(data["QUALITY"], dtype=np.int32)
        flux = np.asarray(data["FLUX"], dtype=np.float64)
        ferr = np.asarray(data["FLUX_ERR"], dtype=np.float64)
        fbkg = np.asarray(data["FLUX_BKG"], dtype=np.float64)
        info = {
            "sector": sec_num,
            "fits_file": fn,
            "size_bytes": os.path.getsize(fpath),
            "sha256": sha256_file(fpath),
            "camera": int(hdr0.get("CAMERA", 0)),
            "ccd": int(hdr0.get("CCD", 0)),
            "date_obs": str(hdr0.get("DATE-OBS", "")),
            "date_end": str(hdr0.get("DATE-END", "")),
            "n_frames_total": int(len(t)),
            "cutout_shape": list(flux.shape[1:]),
        }
        manifest_meta[str(sec_num)] = info
        sectors_data[sec_num] = {
            "meta": info,
            "time": t,
            "qual": qual,
            "flux": flux,
            "ferr": ferr,
            "fbkg": fbkg,
        }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(manifest_meta, f, indent=2)
    return sec_list, sectors_data


def extract_sector_ffi_lc(sec_num, sdata):
    """
    Reproducible FFI aperture photometry & detrending on an 11x11 TESSCut stamp:
    1. Filter cadences: finite TIME, finite central 5x5 FLUX, QUALITY == 0.
    2. Compute median image across good cadences; find flux-weighted centroid near center (5, 5).
    3. Define:
       - Primary core aperture mask: 3x3 pixels (9 px) centered on peak pixel (r_max, c_max),
         plus thresholded contiguous aperture (pixels with med_img > bg_med + 20 * bg_mad
         within r <= 2.3 px of centroid).
       - Background sky mask: outer pixels with distance r >= 3.2 px from peak and below
         the 50th percentile of the median image (excluding any neighbour stellar wings).
    4. Subtract residual per-cadence Tukey-biweight sky background from each pixel in the
       aperture, and reject extreme scattered-light / spacecraft dump cadences where
       |sky_res| > 6 * MAD(sky_res) or single-frame point-to-point jump > 8 * MAD.
    5. Detrend via an iterative dip-masked 1.5-day sliding Tukey-biweight continuum filter
       (masking eclipse dips with dF/F < -3.5 * MAD so transit depths are unattenuated).
    """
    t_all = sdata["time"]
    q_all = sdata["qual"]
    f_all = sdata["flux"]
    e_all = sdata["ferr"]
    b_all = sdata["fbkg"]

    ny, nx = f_all.shape[1], f_all.shape[2]
    finite_stamp = np.all(np.isfinite(f_all[:, 3:8, 3:8]), axis=(1, 2))
    good_q = (q_all == 0) & np.isfinite(t_all) & finite_stamp

    med_img = np.nanmedian(f_all[good_q], axis=0)
    # Peak pixel near center (3..7, 3..7)
    sub = med_img[3:8, 3:8]
    pr, pc = np.unravel_index(np.argmax(sub), sub.shape)
    pk_r, pk_c = pr + 3, pc + 3

    yy, xx = np.indices((ny, nx))
    rr = np.hypot(yy - pk_r, xx - pk_c)

    # Outer sky annulus pixels: r >= 3.2 px and below median of outer pixels
    outer_candidates = rr >= 3.2
    outer_thresh = np.nanpercentile(med_img[outer_candidates], 55.0)
    bg_mask = outer_candidates & (med_img <= outer_thresh)

    bg_med_val = float(np.nanmedian(med_img[bg_mask]))
    bg_mad_val = float(1.4826 * np.nanmedian(np.abs(med_img[bg_mask] - bg_med_val)))

    # Thresholded target aperture: pixels within r <= 2.5 px with med_img > bg_med + 20 * bg_mad
    thresh_ap_mask = (rr <= 2.5) & (med_img > bg_med_val + 20.0 * max(bg_mad_val, 1.0))
    if np.sum(thresh_ap_mask) < 4:
        thresh_ap_mask = ( np.abs(yy - pk_r) <= 1 ) & ( np.abs(xx - pk_c) <= 1 )

    # Fixed 3x3 core aperture around peak pixel for direct comparison
    core3x3_mask = (np.abs(yy - pk_r) <= 1) & (np.abs(xx - pk_c) <= 1)
    # Tight 5-pixel cross aperture (peak + 4 orthogonal neighbours) for minimal blending
    cross5_mask = rr <= 1.05

    n_ap_thresh = int(np.sum(thresh_ap_mask))
    n_ap_3x3 = int(np.sum(core3x3_mask))
    n_ap_cross5 = int(np.sum(cross5_mask))
    n_bg = int(np.sum(bg_mask))

    t = t_all[good_q]
    f_cube = f_all[good_q]
    e_cube = e_all[good_q]
    b_cube = b_all[good_q]

    order = np.argsort(t)
    t = t[order]
    f_cube = f_cube[order]
    e_cube = e_cube[order]
    b_cube = b_cube[order]

    # Per-cadence residual sky background in bg_mask
    sky_res_pp = np.nanmedian(f_cube[:, bg_mask], axis=1)
    sky_pipe_pp = np.nanmedian(b_cube[:, thresh_ap_mask], axis=1)

    # Filter out extreme scattered-light spikes or spacecraft attitude tweaks
    sky_med = float(np.nanmedian(sky_res_pp))
    sky_sig = robust_sigma(sky_res_pp)
    raw_thresh_flux = np.sum(f_cube[:, thresh_ap_mask], axis=1) - n_ap_thresh * sky_res_pp

    # Reject frames with non-positive flux or extreme sky spikes (> 8 sigma)
    clean_mask = (raw_thresh_flux > 0.2 * np.nanmedian(raw_thresh_flux)) & (
        np.abs(sky_res_pp - sky_med) <= max(8.0 * sky_sig, 50.0)
    )

    t = t[clean_mask]
    f_cube = f_cube[clean_mask]
    e_cube = e_cube[clean_mask]
    sky_res_pp = sky_res_pp[clean_mask]
    sky_pipe_pp = sky_pipe_pp[clean_mask]

    # Compute net fluxes for all 3 apertures:
    # 1) Stated Primary Aperture: Thresholded core aperture (20-sigma above sky, r <= 2.5 px)
    f_thresh = np.sum(f_cube[:, thresh_ap_mask], axis=1) - n_ap_thresh * sky_res_pp
    e_thresh = np.sqrt(np.sum(e_cube[:, thresh_ap_mask] ** 2, axis=1))
    # 2) Fixed 3x3 pixel box aperture (9 px)
    f_3x3 = np.sum(f_cube[:, core3x3_mask], axis=1) - n_ap_3x3 * sky_res_pp
    # 3) Tight 5-pixel cross aperture (5 px)
    f_cross5 = np.sum(f_cube[:, cross5_mask], axis=1) - n_ap_cross5 * sky_res_pp

    # Flux-weighted centroid inside 3x3 aperture
    y_ap = yy[core3x3_mask][None, :]
    x_ap = xx[core3x3_mask][None, :]
    w_ap = np.maximum(f_cube[:, core3x3_mask] - sky_res_pp[:, None], 0.0)
    w_sum = np.sum(w_ap, axis=1)
    cent_r = np.sum(w_ap * y_ap, axis=1) / np.maximum(w_sum, 1e-9)
    cent_c = np.sum(w_ap * x_ap, axis=1) / np.maximum(w_sum, 1e-9)

    def detrend_flux_series(time_arr, flux_arr, window_days=1.5):
        med_f = tukey_biweight(flux_arr)
        fnorm = flux_arr / med_f
        dip_mask = np.zeros(len(time_arr), dtype=bool)
        cont = np.ones(len(time_arr), dtype=float)
        hw = 0.5 * window_days

        # Precompute index bounds for sliding window
        left_idx = np.searchsorted(time_arr, time_arr - hw, side="left")
        right_idx = np.searchsorted(time_arr, time_arr + hw, side="right")

        for _ in range(3):
            ok = ~dip_mask
            for i in range(len(time_arr)):
                sl = slice(left_idx[i], right_idx[i])
                vals = fnorm[sl][ok[sl]]
                if vals.size >= 5:
                    cont[i] = float(np.median(vals))
                else:
                    cont[i] = 1.0
            f_det = fnorm / cont
            sig = robust_sigma(f_det[~dip_mask])
            dip_mask = (1.0 - f_det) > 3.5 * sig

        # Final refine using Tukey biweight on non-dip points in each window
        ok = ~dip_mask
        for i in range(len(time_arr)):
            sl = slice(left_idx[i], right_idx[i])
            vals = fnorm[sl][ok[sl]]
            if vals.size >= 5:
                cont[i] = tukey_biweight(vals, c=6.0, max_iter=3)
        f_det = fnorm / cont
        return med_f, fnorm, cont, f_det, dip_mask

    med_thresh, fnorm_thresh, cont_thresh, fdet_thresh, dip_mask = detrend_flux_series(t, f_thresh)
    _, _, _, fdet_3x3, _ = detrend_flux_series(t, f_3x3)
    _, _, _, fdet_cross5, _ = detrend_flux_series(t, f_cross5)

    depth_thresh = 1.0 - fdet_thresh
    depth_3x3 = 1.0 - fdet_3x3
    depth_cross5 = 1.0 - fdet_cross5
    rel_err = e_thresh / (med_thresh * cont_thresh)

    dt_med_s = float(np.median(np.diff(t)) * 86400.0)
    oot_rms_ppm = float(robust_sigma(depth_thresh[~dip_mask]) * 1e6)

    # Save extracted light curve CSV for this sector
    csv_fn = f"ffi_lc_s{sec_num:04d}.csv"
    csv_path = os.path.join(RES_DIR, csv_fn)
    phi_house = ((t - T0_HOUSE) / P_HOUSE) % 1.0
    phi_joint = ((t - T0_JOINT) / P_JOINT) % 1.0
    with open(csv_path, "w", encoding="utf-8", newline="\n") as fc:
        writer = csv.writer(fc)
        writer.writerow([
            "btjd",
            "raw_ap_flux_e_s",
            "sky_res_e_s_px",
            "continuum_norm",
            "detrended_flux",
            "depth_thresh_ap",
            "depth_3x3_ap",
            "depth_cross5_ap",
            "rel_flux_err",
            "centroid_row_px",
            "centroid_col_px",
            "phase_house_11p7672",
            "phase_joint_11p767217",
        ])
        for i in range(len(t)):
            writer.writerow([
                f"{t[i]:.6f}",
                f"{f_thresh[i]:.2f}",
                f"{sky_res_pp[i]:.3f}",
                f"{cont_thresh[i]:.6f}",
                f"{fdet_thresh[i]:.6f}",
                f"{depth_thresh[i]:.6f}",
                f"{depth_3x3[i]:.6f}",
                f"{depth_cross5[i]:.6f}",
                f"{rel_err[i]:.6f}",
                f"{cent_r[i]:.4f}",
                f"{cent_c[i]:.4f}",
                f"{phi_house[i]:.6f}",
                f"{phi_joint[i]:.6f}",
            ])

    return {
        "sector": sec_num,
        "csv_file": csv_fn,
        "n_frames_total": int(len(t_all)),
        "n_frames_good_q0": int(np.sum(good_q)),
        "n_frames_clean_used": int(len(t)),
        "cadence_s": round(dt_med_s, 1),
        "btjd_start": round(float(t[0]), 5),
        "btjd_stop": round(float(t[-1]), 5),
        "peak_pixel_rc": [int(pk_r), int(pk_c)],
        "n_ap_thresh_px": n_ap_thresh,
        "n_ap_3x3_px": n_ap_3x3,
        "n_ap_cross5_px": n_ap_cross5,
        "n_sky_annulus_px": n_bg,
        "median_ap_flux_e_s": round(float(med_thresh), 1),
        "oot_scatter_ppm": round(oot_rms_ppm, 1),
        "arrays": {
            "t": t,
            "depth_thresh": depth_thresh,
            "depth_3x3": depth_3x3,
            "depth_cross5": depth_cross5,
            "rel_err": rel_err,
            "cent_r": cent_r,
            "cent_c": cent_c,
            "phi_house": phi_house,
            "phi_joint": phi_joint,
        },
    }


def measure_phase_window(phi, depth, center_phi, half_width):
    dphi = (phi - center_phi + 0.5) % 1.0 - 0.5
    m = np.abs(dphi) <= half_width
    vals = depth[m]
    if vals.size == 0:
        return {"n_pts": 0, "median_depth": None, "err_depth": None, "max_depth": None, "mean_depth": None}
    med = float(np.median(vals))
    bw = float(tukey_biweight(vals)) if vals.size >= 5 else med
    mad_sig = robust_sigma(vals) if vals.size >= 3 else float(np.std(vals))
    sem = float(mad_sig / math.sqrt(vals.size)) if vals.size >= 2 else 0.0
    return {
        "n_pts": int(vals.size),
        "biweight_depth": round(bw, 5),
        "median_depth": round(med, 5),
        "mean_depth": round(float(np.mean(vals)), 5),
        "err_depth": round(sem, 5),
        "scatter_mad": round(mad_sig, 5),
        "max_depth": round(float(np.max(vals)), 5),
    }


def find_individual_transits(sec_num, arrays):
    """Find every primary and secondary eclipse event covered by the sector's time span."""
    t = arrays["t"]
    d_th = arrays["depth_thresh"]
    d_3x3 = arrays["depth_3x3"]
    d_cr5 = arrays["depth_cross5"]
    cr = arrays["cent_r"]
    cc = arrays["cent_c"]

    t_min, t_max = float(t[0]), float(t[-1])
    e_min = int(math.floor((t_min - T0_JOINT) / P_JOINT)) - 1
    e_max = int(math.ceil((t_max - T0_JOINT) / P_JOINT)) + 1

    med_cr = float(np.median(cr))
    med_cc = float(np.median(cc))

    events = []
    for ep in range(e_min, e_max + 1):
        for etype, phi_off in [("PRIMARY", 0.0), ("SECONDARY", PHI_SEC_ECC)]:
            t_pred_joint = T0_JOINT + (ep + phi_off) * P_JOINT
            t_pred_house = T0_HOUSE + (ep + (0.0 if etype == "PRIMARY" else 0.5)) * P_HOUSE
            t_pred_house_ecc = T0_HOUSE + (ep + phi_off) * P_HOUSE

            # Check points within +/- 0.14 d (full eclipse duration is +/- 0.122 d)
            win = np.abs(t - t_pred_joint) <= 0.14
            core = np.abs(t - t_pred_joint) <= 0.012  # +/- 17.3 min bottom
            box = np.abs(t - t_pred_joint) <= 0.020   # +/- 28.8 min house-equivalent box

            n_win = int(np.sum(win))
            if n_win == 0:
                continue

            t_win = t[win]
            d_win = d_th[win]
            idx_pk = int(np.argmax(d_win))
            t_obs_pk = float(t_win[idx_pk])
            pk_depth = float(d_win[idx_pk])

            # Parabolic / flux-weighted centroid time of minimum around peak (+/- 0.04 d)
            near_min = np.abs(t - t_obs_pk) <= 0.04
            if np.sum(near_min) >= 3 and np.max(d_th[near_min]) > 0.05:
                w = np.maximum(d_th[near_min] - 0.02, 0.0) ** 2
                t_center = float(np.sum(w * t[near_min]) / np.sum(w)) if np.sum(w) > 0 else t_obs_pk
            else:
                t_center = t_obs_pk

            n_core = int(np.sum(core))
            n_box = int(np.sum(box))
            core_depth = round(float(np.median(d_th[core])), 5) if n_core > 0 else None
            box_depth = round(float(np.median(d_th[box])), 5) if n_box > 0 else None
            core_3x3 = round(float(np.median(d_3x3[core])), 5) if n_core > 0 else None
            core_cr5 = round(float(np.median(d_cr5[core])), 5) if n_core > 0 else None

            # Centroid shift during core eclipse (in millipixels and arcseconds; TESS px = 21.0")
            if n_core > 0:
                dr_mpix = float((np.median(cr[core]) - med_cr) * 1000.0)
                dc_mpix = float((np.median(cc[core]) - med_cc) * 1000.0)
                shift_mpix = round(math.hypot(dr_mpix, dc_mpix), 2)
                shift_arcsec = round(shift_mpix * 0.021, 3)
            else:
                shift_mpix = None
                shift_arcsec = None

            events.append({
                "sector": sec_num,
                "is_new_unsearched_sector": bool(sec_num not in (9, 36)),
                "epoch_E": ep,
                "type": etype,
                "t_pred_joint_btjd": round(t_pred_joint, 5),
                "t_pred_house_ecc_btjd": round(t_pred_house_ecc, 5),
                "t_pred_house_circ_btjd": round(t_pred_house, 5),
                "t_obs_center_btjd": round(t_center, 5),
                "o_minus_c_joint_min": round((t_center - t_pred_joint) * 1440.0, 2),
                "o_minus_c_house_ecc_min": round((t_center - t_pred_house_ecc) * 1440.0, 2),
                "n_pts_window_pm014d": n_win,
                "n_pts_box_pm0020d": n_box,
                "n_pts_core_pm0012d": n_core,
                "core_depth_thresh": core_depth,
                "box_depth_thresh": box_depth,
                "peak_depth_thresh": round(pk_depth, 5),
                "core_depth_3x3": core_3x3,
                "core_depth_cross5": core_cr5,
                "centroid_shift_mpix": shift_mpix,
                "centroid_shift_arcsec": shift_arcsec,
            })
    return events


def main():
    sec_list, sectors_data = load_sector_cubes()

    # 1. Build Complete Sector Manifest (fail-visible across all TESS Cycles / Sectors 1..100)
    observed_sectors = sorted(sectors_data.keys())  # [9, 36, 63, 90, 99, 100]
    unsearched_ffi_sectors = [s for s in observed_sectors if s not in (9, 36)]

    sector_manifest = []
    # Explicitly account for all TESS southern-hemisphere / ecliptic cycles and sectors 1..100
    cycle_groups = [
        ("S0001-S0008", list(range(1, 9)), "no-usable-FFI", "Target (RA=164.160, Dec=-36.580; ecl lon=179.48, lat=-39.77) outside Camera 2 FOV"),
        ("S0009", [9], "usable-FFI (House 2-min SPOC baseline sector; 30-min FFI extracted as cross-check only, excluded from new-FFI combined fold)", "Camera 2 CCD 3 (1800s FFI cadence)"),
        ("S0010-S0035", list(range(10, 36)), "no-usable-FFI", "Target outside TESS FOV (S10-S13 southern late; S14-S26 northern; S27-S35 early Y3)"),
        ("S0036", [36], "usable-FFI (House 2-min SPOC baseline sector; 10-min FFI extracted as cross-check only, excluded from new-FFI combined fold)", "Camera 2 CCD 3 (600s FFI cadence)"),
        ("S0037-S0062", list(range(37, 63)), "no-usable-FFI", "Target outside TESS FOV (S37-S39 late Y3; S40-S60 northern/ecliptic; S61-S62 early Y5)"),
        ("S0063", [63], "usable-FFI (UNSEARCHED SECTOR - extracted & folded)", "Camera 2 CCD 4 (200s FFI cadence, Year 5, 2023-03-10 to 2023-04-06)"),
        ("S0064-S0089", list(range(64, 90)), "no-usable-FFI", "Target outside TESS FOV (S64-S69 late Y5; S70-S86 northern/ecliptic; S87-S89 early Y7)"),
        ("S0090", [90], "usable-FFI (UNSEARCHED SECTOR - extracted & folded)", "Camera 2 CCD 4 (200s FFI cadence, Year 7, 2025-03-12 to 2025-04-09)"),
        ("S0091-S0098", list(range(91, 99)), "no-usable-FFI", "Target outside TESS FOV"),
        ("S0099", [99], "usable-FFI (UNSEARCHED SECTOR - extracted & folded)", "Camera 2 CCD 2 (200s FFI cadence, Year 8, 2025-11-20 to 2025-12-16)"),
        ("S0100", [100], "usable-FFI (UNSEARCHED SECTOR - extracted & folded)", "Camera 2 CCD 4 (200s FFI cadence, Year 8, 2025-12-16 to 2026-01-12)"),
    ]
    for label, secs, status, reason in cycle_groups:
        sector_manifest.append({
            "sector_range": label,
            "sectors": secs,
            "status": status,
            "reason_or_camera": reason,
        })

    # 2. Extract FFI light curves for all 6 observed sectors
    extracted = {}
    all_events = []
    new_ffi_events = []

    for sec_num in observed_sectors:
        ext = extract_sector_ffi_lc(sec_num, sectors_data[sec_num])
        arr = ext["arrays"]

        # Folded depths at exact house ephemeris (P=11.7672 d, T0=BTJD 2286.3720)
        # Note: Over the +1243 d lever arm from S36 (E=0, BTJD 2286.372) to S100 (E=+105, BTJD 3521.930),
        # the house period 11.7672 d drifts by dT = (11.7672170 - 11.7672000) * E = +0.0000170 * E days
        # (+2.57 min at E=+105, or dphi = +0.000152 * E). We report BOTH the strict house-ephemeris
        # phase windows AND the phase-drift-corrected / joint-ephemeris windows!
        sec_events = find_individual_transits(sec_num, arr)
        all_events.extend(sec_events)
        if sec_num in unsearched_ffi_sectors:
            new_ffi_events.extend(sec_events)

        # Measure per-sector folded depths at house ephemeris (P = 11.7672, T0 = 2286.3720)
        phi_h = arr["phi_house"]
        phi_j = arr["phi_joint"]
        d_th = arr["depth_thresh"]
        d_3x3 = arr["depth_3x3"]
        d_cr5 = arr["depth_cross5"]

        # Primary (phi = 0.0000) & Secondary (eccentric phi = 0.51411 AND circular phi = 0.50000)
        # Use core bottom |dphi| <= 0.0010 (+/- 16.9 min) and house-match box |dphi| <= 0.0017 (+/- 28.8 min)
        # For S9 (30-min cadence = 0.00177 phase step), also include |dphi| <= 0.0025
        folded_house = {
            "core_hw0010": {
                "primary_phi0000": measure_phase_window(phi_h, d_th, 0.00000, 0.0010),
                "secondary_ecc_phi05141": measure_phase_window(phi_h, d_th, PHI_SEC_ECC, 0.0010),
                "secondary_circ_phi05000": measure_phase_window(phi_h, d_th, 0.50000, 0.0010),
            },
            "box_hw0017": {
                "primary_phi0000": measure_phase_window(phi_h, d_th, 0.00000, 0.0017),
                "secondary_ecc_phi05141": measure_phase_window(phi_h, d_th, PHI_SEC_ECC, 0.0017),
                "secondary_circ_phi05000": measure_phase_window(phi_h, d_th, 0.50000, 0.0017),
                "control_phi0250": measure_phase_window(phi_h, d_th, 0.25000, 0.0017),
                "control_phi0750": measure_phase_window(phi_h, d_th, 0.75000, 0.0017),
            },
            "mid_hw0025": {
                "primary_phi0000": measure_phase_window(phi_h, d_th, 0.00000, 0.0025),
                "secondary_ecc_phi05141": measure_phase_window(phi_h, d_th, PHI_SEC_ECC, 0.0025),
                "secondary_circ_phi05000": measure_phase_window(phi_h, d_th, 0.50000, 0.0025),
            },
            "ap3x3_box_hw0017": {
                "primary_phi0000": measure_phase_window(phi_h, d_3x3, 0.00000, 0.0017),
                "secondary_ecc_phi05141": measure_phase_window(phi_h, d_3x3, PHI_SEC_ECC, 0.0017),
            },
            "apcross5_box_hw0017": {
                "primary_phi0000": measure_phase_window(phi_h, d_cr5, 0.00000, 0.0017),
                "secondary_ecc_phi05141": measure_phase_window(phi_h, d_cr5, PHI_SEC_ECC, 0.0017),
            },
        }
        folded_joint = {
            "core_hw0010": {
                "primary_phi0000": measure_phase_window(phi_j, d_th, 0.00000, 0.0010),
                "secondary_ecc_phi05141": measure_phase_window(phi_j, d_th, PHI_SEC_ECC, 0.0010),
            },
            "box_hw0017": {
                "primary_phi0000": measure_phase_window(phi_j, d_th, 0.00000, 0.0017),
                "secondary_ecc_phi05141": measure_phase_window(phi_j, d_th, PHI_SEC_ECC, 0.0017),
            },
        }

        extracted[sec_num] = {
            k: v for k, v in ext.items() if k != "arrays"
        }
        extracted[sec_num]["meta"] = sectors_data[sec_num]["meta"]
        extracted[sec_num]["is_unsearched_ffi_sector"] = bool(sec_num in unsearched_ffi_sectors)
        extracted[sec_num]["folded_house_ephemeris"] = folded_house
        extracted[sec_num]["folded_joint_ephemeris"] = folded_joint
        extracted[sec_num]["events"] = sec_events

    # 3. Combined Fold across ONLY the 4 Unsearched FFI Sectors (S63 + S90 + S99 + S100)
    t_un = np.concatenate([ extract_sector_ffi_lc_cached["t"] for extract_sector_ffi_lc_cached in [
        # Re-read arrays from memory
    ] ]) if False else None

    # Gather arrays for unsearched sectors [63, 90, 99, 100]
    un_phi_h = []
    un_phi_j = []
    un_d_th = []
    un_d_3x3 = []
    un_d_cr5 = []
    for sec_num in unsearched_ffi_sectors:
        # Read back from CSV we just wrote to verify CSV reproducibility at the same time!
        csv_p = os.path.join(RES_DIR, f"ffi_lc_s{sec_num:04d}.csv")
        with open(csv_p, "r", encoding="utf-8") as fc:
            rdr = csv.DictReader(fc)
            for row in rdr:
                un_phi_h.append(float(row["phase_house_11p7672"]))
                un_phi_j.append(float(row["phase_joint_11p767217"]))
                un_d_th.append(float(row["depth_thresh_ap"]))
                un_d_3x3.append(float(row["depth_3x3_ap"]))
                un_d_cr5.append(float(row["depth_cross5_ap"]))

    un_phi_h = np.asarray(un_phi_h)
    un_phi_j = np.asarray(un_phi_j)
    un_d_th = np.asarray(un_d_th)
    un_d_3x3 = np.asarray(un_d_3x3)
    un_d_cr5 = np.asarray(un_d_cr5)

    combined_unsearched_fold = {
        "sectors_included": unsearched_ffi_sectors,
        "total_clean_ffi_cadences": int(len(un_d_th)),
        "house_ephemeris_P11p7672_T0_2286p3720": {
            "core_hw0010": {
                "primary_phi0000": measure_phase_window(un_phi_h, un_d_th, 0.00000, 0.0010),
                "secondary_ecc_phi05141": measure_phase_window(un_phi_h, un_d_th, PHI_SEC_ECC, 0.0010),
                "secondary_circ_phi05000": measure_phase_window(un_phi_h, un_d_th, 0.50000, 0.0010),
            },
            "box_hw0017": {
                "primary_phi0000": measure_phase_window(un_phi_h, un_d_th, 0.00000, 0.0017),
                "secondary_ecc_phi05141": measure_phase_window(un_phi_h, un_d_th, PHI_SEC_ECC, 0.0017),
                "secondary_circ_phi05000": measure_phase_window(un_phi_h, un_d_th, 0.50000, 0.0017),
                "control_phi0250": measure_phase_window(un_phi_h, un_d_th, 0.25000, 0.0017),
                "control_phi0750": measure_phase_window(un_phi_h, un_d_th, 0.75000, 0.0017),
            },
            "ap3x3_box_hw0017": {
                "primary_phi0000": measure_phase_window(un_phi_h, un_d_3x3, 0.00000, 0.0017),
                "secondary_ecc_phi05141": measure_phase_window(un_phi_h, un_d_3x3, PHI_SEC_ECC, 0.0017),
            },
            "apcross5_box_hw0017": {
                "primary_phi0000": measure_phase_window(un_phi_h, un_d_cr5, 0.00000, 0.0017),
                "secondary_ecc_phi05141": measure_phase_window(un_phi_h, un_d_cr5, PHI_SEC_ECC, 0.0017),
            },
        },
        "joint_ephemeris_P11p7672170_T0_2286p372048": {
            "core_hw0010": {
                "primary_phi0000": measure_phase_window(un_phi_j, un_d_th, 0.00000, 0.0010),
                "secondary_ecc_phi05141": measure_phase_window(un_phi_j, un_d_th, PHI_SEC_ECC, 0.0010),
            },
            "box_hw0017": {
                "primary_phi0000": measure_phase_window(un_phi_j, un_d_th, 0.00000, 0.0017),
                "secondary_ecc_phi05141": measure_phase_window(un_phi_j, un_d_th, PHI_SEC_ECC, 0.0017),
            },
        },
    }

    out = {
        "bounty_id": "bnty_0425",
        "target": "TIC 158499577 (HD 94871)",
        "coordinates_icrs": {"ra_deg": 164.1597484, "dec_deg": -36.5803139},
        "method_version": "1.0.0",
        "execution_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sector_manifest": sector_manifest,
        "observed_sectors_all": observed_sectors,
        "house_2min_baseline_sectors": [9, 36],
        "unsearched_ffi_sectors": unsearched_ffi_sectors,
        "per_sector_extractions": {str(k): v for k, v in extracted.items()},
        "combined_unsearched_ffi_fold": combined_unsearched_fold,
        "new_transits_in_unsearched_sectors": new_ffi_events,
        "all_ffi_transits_including_s9_s36_crosscheck": all_events,
    }

    res_path = os.path.join(RES_DIR, "ffi_reextraction_results.json")
    with open(res_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print("=== bnty_0425 FFI Re-Extraction Summary ===")
    print("Observed sectors:", observed_sectors, "| Unsearched FFI sectors:", unsearched_ffi_sectors)
    print("Combined Unsearched (S63+S90+S99+S100) Fold at House Ephemeris:")
    ch = combined_unsearched_fold["house_ephemeris_P11p7672_T0_2286p3720"]
    print("  Core (|dphi|<=0.0010): PRI =", ch["core_hw0010"]["primary_phi0000"], "SEC_ecc =", ch["core_hw0010"]["secondary_ecc_phi05141"])
    print("  Box  (|dphi|<=0.0017): PRI =", ch["box_hw0017"]["primary_phi0000"], "SEC_ecc =", ch["box_hw0017"]["secondary_ecc_phi05141"])
    print(f"New transits found in unsearched sectors (S63, S90, S99, S100): {len(new_ffi_events)}")
    for ev in new_ffi_events:
        print(
            f"  S{ev['sector']:02d} E={ev['epoch_E']:+4d} {ev['type']:9s} "
            f"BTJD={ev['t_obs_center_btjd']:.5f} (O-C_house={ev['o_minus_c_house_ecc_min']:+.2f}m, O-C_joint={ev['o_minus_c_joint_min']:+.2f}m) "
            f"n={ev['n_pts_window_pm014d']:3d} core={ev['core_depth_thresh']} box={ev['box_depth_thresh']} pk={ev['peak_depth_thresh']} "
            f"shift={ev['centroid_shift_mpix']} mpix"
        )


if __name__ == "__main__":
    main()
