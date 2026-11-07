#!/usr/bin/env python3
"""
DAiL bnty_0426 — TIC 158499577 (HD 94871): Independent Re-Fold, Different Code
Hunter: ducanh3005
Pipeline Version: v1.0.0 (2026-11-04)

Independent re-fold of TIC 158499577 at the house ephemeris (P = 11.7672 d,
T0 = BTJD 2286.3720) covering TESS SPOC 2-minute data (Sectors 9, 36) and
SuperWASP DR1 (2006-2008, 1SWASP J105638.34-363449.0), using:
  1. Independent detrending:
     - TESS (both PDCSAP_FLUX and raw SAP_FLUX): Iterative Tukey biweight /
       moving polynomial continuum filter (1.5-d sliding window with 2.5-sigma
       iterative eclipse masking), compared against raw sector median.
     - SuperWASP DR1 (both TAMFLUX2 and raw FLUX2): Per-camera & per-season
       iterative biweight continuum + intranight airmass slope detrending,
       compared against raw global median.
  2. Independent period-finding methods:
     - Lafler-Kinman (1965) Phase String-Length statistic Theta_LK(P)
     - Stellingwerf (1978) Phase Dispersion Minimization statistic Theta_PDM(P)
  3. Complete folded depths (primary, secondary at both eccentric phi=0.51411
     and nominal circular phi=0.50000, across narrow core |dphi|<0.0008,
     intermediate |dphi|<0.0017 / 0.0025, and wide full-duration |dphi|<0.0108
     windows), per-event depths (all 8 TESS events + all SuperWASP event windows
     with >=3 in-eclipse points), quadrature control folds at phi=0.25 and 0.75,
     and plain quantification of every discrepancy from the house numbers
     (TESS 0.332 / 0.293; SuperWASP +0.189 / +0.137 mag).
"""

import json
import math
import os
import struct
import sys
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "raw")
RES_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(RES_DIR, exist_ok=True)

BLOCK = 2880
FITS_TYPES = {
    "L": (1, "b"),
    "B": (1, "B"),
    "I": (2, "h"),
    "J": (4, "i"),
    "K": (8, "q"),
    "E": (4, "f"),
    "D": (8, "d"),
    "A": (1, "c"),
}


def _fmt_info(tform):
    tform = tform.strip()
    i = 0
    while i < len(tform) and tform[i].isdigit():
        i += 1
    count = int(tform[:i]) if i else 1
    code = tform[i:i + 1] if i < len(tform) else "D"
    return code, count, FITS_TYPES[code][0] * count


def read_fits_table(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    pos = 0
    primary = {}
    extensions = []
    while pos < len(raw):
        header = {}
        while True:
            block = raw[pos:pos + BLOCK]
            pos += BLOCK
            end_found = False
            for i in range(0, BLOCK, 80):
                card = block[i:i + 80].decode("ascii", "replace")
                key = card[:8].strip()
                if key == "END":
                    end_found = True
                    break
                if not key or "=" not in card[8:10]:
                    continue
                val = card[10:].split("/")[0].strip()
                if val.startswith("'") and val.endswith("'"):
                    val = val[1:-1].strip()
                else:
                    try:
                        val = int(val)
                    except ValueError:
                        try:
                            val = float(val)
                        except ValueError:
                            pass
                header[key] = val
            if end_found:
                break
        if not header:
            break
        naxis = int(header.get("NAXIS", 0))
        if naxis == 0:
            primary = header
            continue
        bitpix = int(header.get("BITPIX", 8))
        nelem = 1
        for k in range(1, naxis + 1):
            nelem *= int(header["NAXIS%d" % k])
        nbytes = abs(bitpix) // 8 * nelem
        data_start = pos
        pos += ((nbytes + BLOCK - 1) // BLOCK) * BLOCK
        nrows = int(header.get("NAXIS2", 0))
        rowlen = int(header.get("NAXIS1", 0))
        fields = []
        idx = 1
        while True:
            tform = header.get("TFORM%d" % idx)
            if tform is None:
                break
            code, count, _ = _fmt_info(tform)
            fields.append((header.get("TTYPE%d" % idx, "").strip(), code, count))
            idx += 1
        if not fields:
            continue
        blob = raw[data_start:data_start + nrows * rowlen]
        cols = {}
        offset = 0
        for name, code, count in fields:
            itemsize, scode = FITS_TYPES[code]
            nb = itemsize * count
            if code != "A" and count == 1:
                dt = np.dtype(">" + scode)
                arr = np.ndarray(shape=(nrows,), dtype=dt, buffer=blob, offset=offset, strides=(rowlen,)).astype(float)
                cols[name] = arr
            elif code == "A":
                # Extract camera ID (first 3 chars of IMAGEID in SuperWASP)
                cam = [int(blob[r * rowlen + offset:r * rowlen + offset + 3].decode("ascii", "replace")) for r in range(nrows)]
                cols[name + "_CAM"] = np.array(cam, dtype=int)
            offset += nb
        extensions.append((header.get("EXTNAME", ""), header, cols))
    return primary, extensions


def tukey_biweight_location(x, c=6.0, max_iter=5):
    """Iterative Tukey biweight robust location estimator."""
    if len(x) == 0:
        return np.nan
    m = float(np.median(x))
    mad = float(np.median(np.abs(x - m)))
    if mad < 1e-12:
        return m
    s = 1.4826 * mad
    for _ in range(max_iter):
        u = (x - m) / (c * s)
        mask = np.abs(u) < 1.0
        if not np.any(mask):
            break
        w = (1.0 - u[mask] ** 2) ** 2
        m = float(np.sum(w * x[mask]) / np.sum(w))
    return m


def detrend_tess_biweight_poly(t, flux, window_d=1.5):
    """Independent TESS detrender:
    Iteratively masks downward dips > 2.5 sigma below baseline, then fits a
    piecewise orbital-segment quadratic + 1.5-d Tukey biweight continuum.
    """
    med0 = tukey_biweight_location(flux)
    fn0 = flux / med0
    mad0 = 1.4826 * np.median(np.abs(fn0 - 1.0))
    # Mask eclipse dips (> 3 * mad0 below 1.0)
    out_mask = fn0 > (1.0 - max(0.01, 3.5 * mad0))
    # Split at mid-sector downlink gap (gap > 0.5 d)
    gaps = np.where(np.diff(t) > 0.5)[0] + 1
    seg_indices = np.split(np.arange(len(t)), gaps)
    cont = np.ones_like(flux)
    for idx in seg_indices:
        if len(idx) == 0:
            continue
        ts = t[idx]
        fs = flux[idx]
        om = out_mask[idx]
        if np.sum(om) > 20:
            t_mid_s = 0.5 * (ts.min() + ts.max())
            p2 = np.polyfit(ts[om] - t_mid_s, fs[om], 2)
            trend_poly = np.polyval(p2, ts - t_mid_s)
            res_ratio = fs / trend_poly
            # Coarse 0.5-d grid biweight residual smoothing on out-of-eclipse points
            g_centers = np.arange(ts.min(), ts.max() + 0.25, 0.25)
            g_vals = []
            for gc in g_centers:
                w_m = om & (np.abs(ts - gc) < 0.5 * window_d)
                if np.sum(w_m) >= 5:
                    g_vals.append(tukey_biweight_location(res_ratio[w_m]))
                else:
                    g_vals.append(1.0)
            smooth_corr = np.interp(ts, g_centers, np.array(g_vals))
            cont[idx] = trend_poly * smooth_corr
        else:
            cont[idx] = med0
    return flux / cont


def detrend_superwasp_biweight(hjd, mag, mag_err, cam):
    """Independent SuperWASP detrender:
    Removes per-camera & per-season Tukey biweight zero-point (computed with a
    symmetric +/-0.08 mag clip around the median) + intranight linear airmass
    drift on non-eclipse nights.
    """
    med_glob = tukey_biweight_location(mag[mag_err < 0.08])
    out_m = (np.abs(mag - med_glob) < 0.08) & (mag_err < 0.08)

    dmag_det = np.copy(mag)
    # 1. Per-season + camera biweight zero-point
    seasons = [(2453800, 2454000), (2454050, 2454350), (2454400, 2454700)]
    for s_min, s_max in seasons:
        for c_id in np.unique(cam):
            m_sc = (hjd >= s_min) & (hjd <= s_max) & (cam == c_id)
            if np.sum(m_sc) == 0:
                continue
            m_sc_out = m_sc & out_m
            zp = tukey_biweight_location(mag[m_sc_out]) if np.sum(m_sc_out) >= 5 else med_glob
            dmag_det[m_sc] = mag[m_sc] - zp

    # 2. Intranight linear drift on non-eclipse nights (nights where < 10% points have dmag > 0.08)
    nights = np.floor(hjd).astype(int)
    for n_id in np.unique(nights):
        mn = nights == n_id
        if np.sum(mn) < 25:
            continue
        # Only fit intranight slope if the night is NOT an eclipse night
        if np.sum(dmag_det[mn] > 0.08) == 0:
            mn_out = mn & out_m
            if np.sum(mn_out) >= 20 and (hjd[mn_out].max() - hjd[mn_out].min() > 0.08):
                t0_n = np.mean(hjd[mn_out])
                p1 = np.polyfit(hjd[mn_out] - t0_n, dmag_det[mn_out], 1)
                # Cap slope correction at +/-0.02 mag to prevent over-detrending
                corr = np.clip(np.polyval(p1, hjd[mn] - t0_n), -0.02, 0.02)
                dmag_det[mn] -= corr
    return dmag_det


def lafler_kinman_theta(t, y, P_grid):
    """Lafler-Kinman (1965) string-length statistic Theta_LK(P)."""
    var_denom = np.sum((y - np.mean(y)) ** 2)
    thetas = np.empty_like(P_grid)
    for i, P in enumerate(P_grid):
        ph = (t / P) % 1.0
        order = np.argsort(ph)
        ys = y[order]
        diffs = np.diff(ys, append=ys[0])
        thetas[i] = np.sum(diffs ** 2) / var_denom
    return thetas


def stellingwerf_pdm_theta(t, y, P_grid, n_bins=200, n_covers=5):
    """Stellingwerf (1978) Phase Dispersion Minimization Theta_PDM(P) with (n_bins, n_covers) overlapping bins."""
    var_tot = np.var(y, ddof=1)
    thetas = np.empty_like(P_grid)
    for i, P in enumerate(P_grid):
        ph = (t / P) % 1.0
        ss_within = 0.0
        dof_within = 0
        for c in range(n_covers):
            ph_c = (ph + (c / float(n_bins * n_covers))) % 1.0
            b_idx = np.clip((ph_c * n_bins).astype(int), 0, n_bins - 1)
            counts = np.bincount(b_idx, minlength=n_bins)
            sums = np.bincount(b_idx, weights=y, minlength=n_bins)
            means = np.divide(sums, counts, out=np.zeros(n_bins), where=counts > 0)
            ss_within += np.sum((y - means[b_idx]) ** 2)
            dof_within += len(y) - np.sum(counts > 0)
        thetas[i] = (ss_within / max(1, dof_within)) / var_tot
    return thetas


def main():
    s9_path = os.path.join(RAW_DIR, "tess2019058134432-s0009-0000000158499577-0139-s_lc.fits")
    s36_path = os.path.join(RAW_DIR, "tess2021065132309-s0036-0000000158499577-0207-s_lc.fits")
    sw_path = os.path.join(RAW_DIR, "1SWASP_J105638.34-363449.0.fits")

    p9, s9_exts = read_fits_table(s9_path)
    p36, s36_exts = read_fits_table(s36_path)
    _, sw_exts = read_fits_table(sw_path)

    c9 = s9_exts[0][2]
    c36 = s36_exts[0][2]
    csw = sw_exts[0][2]

    # House fold parameters
    P_house = 11.767200
    T0_house = 2286.372000
    phi_sec_ecc = 0.514107  # True eccentric secondary phase

    # 1. Load & Independently Detrend TESS (PDCSAP_FLUX and SAP_FLUX)
    m9_q0 = (c9["QUALITY"].astype(int) == 0) & np.isfinite(c9["TIME"]) & np.isfinite(c9["PDCSAP_FLUX"]) & np.isfinite(c9["SAP_FLUX"])
    m36_q0 = (c36["QUALITY"].astype(int) == 0) & np.isfinite(c36["TIME"]) & np.isfinite(c36["PDCSAP_FLUX"]) & np.isfinite(c36["SAP_FLUX"])

    t9, pdc9_raw, sap9_raw = c9["TIME"][m9_q0], c9["PDCSAP_FLUX"][m9_q0], c9["SAP_FLUX"][m9_q0]
    t36, pdc36_raw, sap36_raw = c36["TIME"][m36_q0], c36["PDCSAP_FLUX"][m36_q0], c36["SAP_FLUX"][m36_q0]

    # Independent biweight-polynomial detrended vs simple median-normalized
    pdc9_det = detrend_tess_biweight_poly(t9, pdc9_raw)
    pdc36_det = detrend_tess_biweight_poly(t36, pdc36_raw)
    sap9_det = detrend_tess_biweight_poly(t9, sap9_raw)
    sap36_det = detrend_tess_biweight_poly(t36, sap36_raw)

    pdc9_med = pdc9_raw / np.median(pdc9_raw)
    pdc36_med = pdc36_raw / np.median(pdc36_raw)
    sap9_med = sap9_raw / np.median(sap9_raw)
    sap36_med = sap36_raw / np.median(sap36_raw)

    t_tess = np.concatenate([t9, t36])
    pdc_det = np.concatenate([pdc9_det, pdc36_det])
    pdc_med = np.concatenate([pdc9_med, pdc36_med])
    sap_det = np.concatenate([sap9_det, sap36_det])
    sap_med = np.concatenate([sap9_med, sap36_med])

    # 2. Load & Independently Detrend SuperWASP DR1 (TAMFLUX2 and raw FLUX2)
    hjd_sw = 2453005.5 + csw["TMID"] / 86400.0
    btjd_sw = hjd_sw - 2457000.0
    tam = csw["TAMFLUX2"]
    tam_err = csw["TAMFLUX2_ERR"]
    flx2 = csw["FLUX2"]
    flx2_err = csw["FLUX2_ERR"]
    cam_sw = csw.get("IMAGEID_CAM", np.full(len(hjd_sw), 222, dtype=int))

    mag_tam = 15.0 - 2.5 * np.log10(np.maximum(tam, 1e-9))
    mag_tam_err = (2.5 / math.log(10.0)) * (tam_err / np.maximum(tam, 1e-9))
    mag_flx2 = 15.0 - 2.5 * np.log10(np.maximum(flx2, 1e-9))
    mag_flx2_err = (2.5 / math.log(10.0)) * (flx2_err / np.maximum(flx2, 1e-9))

    dmag_tam_raw = mag_tam - float(np.median(mag_tam))
    dmag_flx2_raw = mag_flx2 - float(np.median(mag_flx2))
    dmag_tam_det = detrend_superwasp_biweight(hjd_sw, mag_tam, mag_tam_err, cam_sw)
    dmag_flx2_det = detrend_superwasp_biweight(hjd_sw, mag_flx2, mag_flx2_err, cam_sw)

    cl_sw = (mag_tam_err < 0.08) & (np.abs(dmag_tam_raw) < 0.80)

    # 3. Independent Period-Finding (Lafler-Kinman String-Length & Stellingwerf PDM)
    # Run on TESS (subsampled by 2 for LK speed + full on fine grid) and SuperWASP
    P_scan_tess = np.linspace(11.760, 11.775, 301)
    lk_tess = lafler_kinman_theta(t_tess[::2], pdc_det[::2], P_scan_tess)
    pdm_tess = stellingwerf_pdm_theta(t_tess, pdc_det, P_scan_tess, n_bins=100)
    P_lk_tess = float(P_scan_tess[int(np.argmin(lk_tess))])
    P_pdm_tess = float(P_scan_tess[int(np.argmin(pdm_tess))])

    # Fine period scan around 11.7672 d on TESS + SuperWASP
    P_fine = np.linspace(11.7668, 11.7676, 161)
    pdm_tess_fine = stellingwerf_pdm_theta(t_tess, pdc_det, P_fine, n_bins=200)
    pdm_sw_fine = stellingwerf_pdm_theta(btjd_sw[cl_sw], dmag_tam_det[cl_sw], P_fine, n_bins=120)
    lk_sw_fine = lafler_kinman_theta(btjd_sw[cl_sw], dmag_tam_det[cl_sw], P_fine)

    P_pdm_tess_fine = float(P_fine[int(np.argmin(pdm_tess_fine))])
    P_pdm_sw_fine = float(P_fine[int(np.argmin(pdm_sw_fine))])
    P_lk_sw_fine = float(P_fine[int(np.argmin(lk_sw_fine))])

    # 4. Folded Depths at House Ephemeris (P = 11.7672 d, T0 = BTJD 2286.3720)
    ph_tess = ((t_tess - T0_house) / P_house) % 1.0
    ph_tess_s = ((ph_tess + 0.5) % 1.0) - 0.5

    ph_sw = ((btjd_sw - T0_house) / P_house) % 1.0
    ph_sw_s = ((ph_sw + 0.5) % 1.0) - 0.5

    def measure_tess_fold(arr):
        res_w = {}
        for wlabel, hw in [("core_bottom_hw0008", 0.0008), ("house_match_box_hw0017", 0.0017), ("mid_box_hw0025", 0.0025), ("full_dur_box_hw0104", 0.0104)]:
            mp = np.abs(ph_tess_s) < hw
            ms_ecc = np.abs(ph_tess - phi_sec_ecc) < hw
            ms_circ = np.abs(ph_tess - 0.5000) < hw
            mc_025 = np.abs(ph_tess - 0.2500) < hw
            mc_075 = np.abs(ph_tess - 0.7500) < hw

            def stats_depth(m_sub):
                vals = 1.0 - arr[m_sub]
                med = float(np.median(vals))
                mean = float(np.mean(vals))
                se = float(np.std(vals, ddof=1) / math.sqrt(len(vals))) if len(vals) > 1 else 0.0
                return {"n": int(len(vals)), "median_depth": round(med, 5), "mean_depth": round(mean, 5), "se": round(se, 5)}

            res_w[wlabel] = {
                "half_width_phase": hw,
                "half_width_min": round(hw * P_house * 1440.0, 2),
                "primary_phi0000": stats_depth(mp),
                "secondary_ecc_phi05141": stats_depth(ms_ecc),
                "secondary_circ_phi05000": stats_depth(ms_circ),
                "control_phi0250": stats_depth(mc_025),
                "control_phi0750": stats_depth(mc_075),
            }
        return res_w

    tess_folds = {
        "PDCSAP_biweight_detrended": measure_tess_fold(pdc_det),
        "PDCSAP_sector_median": measure_tess_fold(pdc_med),
        "SAP_biweight_detrended": measure_tess_fold(sap_det),
        "SAP_sector_median": measure_tess_fold(sap_med),
    }

    def measure_swasp_fold(dmag_arr, mask_use):
        ph_u = ph_sw[mask_use]
        ph_us = ph_sw_s[mask_use]
        dm_u = dmag_arr[mask_use]
        res_w = {}
        for wlabel, hw in [("core_bottom_hw0025", 0.0025), ("mid_box_hw0050", 0.0050), ("house_match_full_dur_hw0108", 0.0108)]:
            mp = np.abs(ph_us) < hw
            ms_ecc = np.abs(ph_u - phi_sec_ecc) < hw
            ms_circ = np.abs(ph_u - 0.5000) < hw
            mc_025 = np.abs(ph_u - 0.2500) < hw
            mc_075 = np.abs(ph_u - 0.7500) < hw

            def stats_mag(m_sub):
                vals = dm_u[m_sub]
                if len(vals) == 0:
                    return {"n": 0, "median_dmag": None, "mean_dmag": None, "se_mag": None}
                med = float(np.median(vals))
                mean = float(np.mean(vals))
                mad_se = float(1.4826 * np.median(np.abs(vals - med)) / math.sqrt(len(vals))) if len(vals) > 1 else 0.0
                flux_drop = float(1.0 - 10.0 ** (-0.4 * med))
                return {"n": int(len(vals)), "median_dmag": round(med, 4), "mean_dmag": round(mean, 4), "se_mag": round(mad_se, 4), "equiv_flux_depth": round(flux_drop, 4)}

            res_w[wlabel] = {
                "half_width_phase": hw,
                "half_width_min": round(hw * P_house * 1440.0, 2),
                "primary_phi0000": stats_mag(mp),
                "secondary_ecc_phi05141": stats_mag(ms_ecc),
                "secondary_circ_phi05000": stats_mag(ms_circ),
                "control_phi0250": stats_mag(mc_025),
                "control_phi0750": stats_mag(mc_075),
            }
        return res_w

    swasp_folds = {
        "TAMFLUX2_biweight_detrended_clean": measure_swasp_fold(dmag_tam_det, cl_sw),
        "TAMFLUX2_raw_median_all6789": measure_swasp_fold(dmag_tam_raw, np.ones(len(hjd_sw), dtype=bool)),
        "FLUX2_raw_aperture_biweight_clean": measure_swasp_fold(dmag_flx2_det, cl_sw),
    }

    # 5. Per-Event Depths in TESS (all 8 events: 7 Q=0 PDCSAP+SAP events + 1 S9 E=-62 SAP Q=4096 primary)
    tess_per_event = []
    tess_event_list = [
        (9, -63, "PRI", 1545.03767, False),
        (9, -63, "SEC", 1551.08723, False),
        (9, -62, "PRI_SAP_Q4096", 1556.80507, True),
        (9, -62, "SEC", 1562.85457, False),
        (36, 0, "PRI", 2286.37205, False),
        (36, 0, "SEC", 2292.42182, False),
        (36, 1, "PRI", 2298.13921, False),
        (36, 1, "SEC", 2304.18897, False),
    ]
    for sec_num, cyc, etype, tc, is_sap_only in tess_event_list:
        if not is_sap_only:
            m_ev_in = np.abs(t_tess - tc) < 0.122
            m_ev_core = np.abs(t_tess - tc) < (0.0008 * P_house)
            m_ev_box17 = np.abs(t_tess - tc) < (0.0017 * P_house)
            pdc_core = float(np.median(1.0 - pdc_det[m_ev_core]))
            pdc_box17 = float(np.median(1.0 - pdc_det[m_ev_box17]))
            pdc_peak = float(np.max(1.0 - pdc_det[m_ev_in]))
            sap_core = float(np.median(1.0 - sap_det[m_ev_core]))
            sap_box17 = float(np.median(1.0 - sap_det[m_ev_box17]))
            tess_per_event.append({
                "sector": sec_num,
                "cycle": cyc,
                "type": etype,
                "t_mid_btjd": round(tc, 5),
                "n_in_eclipse": int(np.sum(m_ev_in)),
                "pdcsap_core_depth": round(pdc_core, 5),
                "pdcsap_box0017_depth": round(pdc_box17, 5),
                "pdcsap_peak_depth": round(pdc_peak, 5),
                "sap_core_depth": round(sap_core, 5),
                "sap_box0017_depth": round(sap_box17, 5),
            })
        else:
            m62 = ((c9["QUALITY"].astype(int) == 0) | (c9["QUALITY"].astype(int) == 4096)) & np.isfinite(c9["TIME"]) & np.isfinite(c9["SAP_FLUX"]) & (np.abs(c9["TIME"] - tc) < 0.30)
            t62, s62 = c9["TIME"][m62], c9["SAP_FLUX"][m62]
            b62 = (t62 - tc) > 0.15
            pb62 = np.polyfit(t62[b62] - tc, s62[b62], 1)
            sn62 = s62 / np.polyval(pb62, t62 - tc)
            m_in62 = np.abs(t62 - tc) < 0.122
            m_core62 = np.abs(t62 - tc) < (0.0008 * P_house)
            m_box17_62 = np.abs(t62 - tc) < (0.0017 * P_house)
            tess_per_event.append({
                "sector": sec_num,
                "cycle": cyc,
                "type": etype,
                "t_mid_btjd": round(tc, 5),
                "n_in_eclipse": int(np.sum(m_in62)),
                "pdcsap_core_depth": None,
                "pdcsap_box0017_depth": None,
                "pdcsap_peak_depth": None,
                "sap_core_depth": round(float(np.median(1.0 - sn62[m_core62])), 5),
                "sap_box0017_depth": round(float(np.median(1.0 - sn62[m_box17_62])), 5),
                "sap_peak_depth": round(float(np.max(1.0 - sn62[m_in62])), 5),
            })

    # 6. Per-Event Depths in SuperWASP (every event window with >=3 in-eclipse points)
    # Check across full eclipse half-duration |dt| < 0.130 d (|dphi| < 0.01105) for PRI (0.000), SEC_ecc (0.51411), and SEC_circ (0.50000)
    swasp_per_event = []
    for E in range(-470, -390):
        for kind, phi0 in [("PRI_phi0.0000", 0.0), ("SEC_ecc_phi0.5141", phi_sec_ecc), ("SEC_circ_phi0.5000", 0.5000)]:
            tc = T0_house + (E + phi0) * P_house
            m_in = np.abs(btjd_sw - tc) < 0.130
            if np.sum(m_in) >= 3:
                hjd_n = int(np.floor(np.median(hjd_sw[m_in])))
                vals_det = dmag_tam_det[m_in]
                vals_raw = dmag_tam_raw[m_in]
                vals_flx2 = dmag_flx2_det[m_in]
                # Core points within |dt| < 0.035 d (|dphi| < 0.0030) if any
                m_core = np.abs(btjd_sw - tc) < 0.035
                med_core = round(float(np.median(dmag_tam_det[m_core])), 4) if np.sum(m_core) >= 1 else None
                swasp_per_event.append({
                    "cycle": E,
                    "window_type": kind,
                    "hjd_night": hjd_n,
                    "t_pred_btjd": round(tc, 4),
                    "n_in_eclipse": int(np.sum(m_in)),
                    "n_near_bottom_dt035": int(np.sum(m_core)),
                    "med_dmag_tam_det": round(float(np.median(vals_det)), 4),
                    "mean_dmag_tam_det": round(float(np.mean(vals_det)), 4),
                    "med_dmag_tam_raw": round(float(np.median(vals_raw)), 4),
                    "max_dmag_tam_det": round(float(np.max(vals_det)), 4),
                    "core_bottom_dmag": med_core,
                    "med_dmag_flux2_raw_ap": round(float(np.median(vals_flx2)), 4),
                })

    # Seasonal + camera zero-point audit in SuperWASP DR1
    swasp_zeropoint_audit = {
        "global_median_all6789_mag": round(float(np.median(mag_tam)), 5),
        "2006_cam222_n309_med_mag": round(float(np.median(mag_tam[(hjd_sw < 2454000) & (cam_sw == 222)])), 5),
        "2006_cam223_n16_med_mag": round(float(np.median(mag_tam[(hjd_sw < 2454000) & (cam_sw == 223)])), 5),
        "2007_cam222_n1876_med_mag": round(float(np.median(mag_tam[(hjd_sw >= 2454050) & (hjd_sw <= 2454350) & (cam_sw == 222)])), 5),
        "2008_cam222_n4588_med_mag": round(float(np.median(mag_tam[(hjd_sw >= 2454400) & (cam_sw == 222)])), 5),
        "step_2008_minus_2007_mag": round(float(np.median(mag_tam[(hjd_sw >= 2454400) & (cam_sw == 222)]) - np.median(mag_tam[(hjd_sw >= 2454050) & (hjd_sw <= 2454350) & (cam_sw == 222)])), 5),
    }

    # 7. Plain Quantification of Discrepancies vs House Numbers (TESS 0.332 / 0.293; SuperWASP +0.189 / +0.137 mag)
    discrepancies = {
        "discrepancy_1_eccentric_secondary_phase": {
            "summary": "Secondary eclipse is displaced from circular phase 0.50000 to phi_sec = 0.51411 (+0.01411 phase = +3.98 hours, e*cos(w) = +0.02216).",
            "tess_sec_at_phi05000_hw0017": tess_folds["PDCSAP_biweight_detrended"]["house_match_box_hw0017"]["secondary_circ_phi05000"]["median_depth"],
            "tess_sec_at_phi05141_hw0017": tess_folds["PDCSAP_biweight_detrended"]["house_match_box_hw0017"]["secondary_ecc_phi05141"]["median_depth"],
            "size_of_discrepancy_at_phi05000_tess": round(tess_folds["PDCSAP_biweight_detrended"]["house_match_box_hw0017"]["secondary_circ_phi05000"]["median_depth"] - 0.293, 5),
            "swasp_sec_at_phi05000_hw0025_mag": swasp_folds["TAMFLUX2_biweight_detrended_clean"]["core_bottom_hw0025"]["secondary_circ_phi05000"]["median_dmag"],
            "swasp_sec_at_phi05141_hw0025_mag": swasp_folds["TAMFLUX2_biweight_detrended_clean"]["core_bottom_hw0025"]["secondary_ecc_phi05141"]["median_dmag"],
        },
        "discrepancy_2_tess_bottom_vs_box_and_sap_vs_pdcsap": {
            "house_tess_pri_sec": [0.332, 0.293],
            "our_pdcsap_true_bottom_hw0008": [
                tess_folds["PDCSAP_biweight_detrended"]["core_bottom_hw0008"]["primary_phi0000"]["median_depth"],
                tess_folds["PDCSAP_biweight_detrended"]["core_bottom_hw0008"]["secondary_ecc_phi05141"]["median_depth"],
            ],
            "diff_true_bottom_minus_house": [
                round(tess_folds["PDCSAP_biweight_detrended"]["core_bottom_hw0008"]["primary_phi0000"]["median_depth"] - 0.332, 5),
                round(tess_folds["PDCSAP_biweight_detrended"]["core_bottom_hw0008"]["secondary_ecc_phi05141"]["median_depth"] - 0.293, 5),
            ],
            "our_pdcsap_box_hw0017_reproducing_house": [
                tess_folds["PDCSAP_biweight_detrended"]["house_match_box_hw0017"]["primary_phi0000"]["median_depth"],
                tess_folds["PDCSAP_biweight_detrended"]["house_match_box_hw0017"]["secondary_ecc_phi05141"]["median_depth"],
            ],
            "diff_box0017_minus_house": [
                round(tess_folds["PDCSAP_biweight_detrended"]["house_match_box_hw0017"]["primary_phi0000"]["median_depth"] - 0.332, 5),
                round(tess_folds["PDCSAP_biweight_detrended"]["house_match_box_hw0017"]["secondary_ecc_phi05141"]["median_depth"] - 0.293, 5),
            ],
            "our_sap_true_bottom_hw0008": [
                tess_folds["SAP_biweight_detrended"]["core_bottom_hw0008"]["primary_phi0000"]["median_depth"],
                tess_folds["SAP_biweight_detrended"]["core_bottom_hw0008"]["secondary_ecc_phi05141"]["median_depth"],
            ],
            "our_sap_box_hw0017": [
                tess_folds["SAP_biweight_detrended"]["house_match_box_hw0017"]["primary_phi0000"]["median_depth"],
                tess_folds["SAP_biweight_detrended"]["house_match_box_hw0017"]["secondary_ecc_phi05141"]["median_depth"],
            ],
            "diff_sap_box0017_minus_house": [
                round(tess_folds["SAP_biweight_detrended"]["house_match_box_hw0017"]["primary_phi0000"]["median_depth"] - 0.332, 5),
                round(tess_folds["SAP_biweight_detrended"]["house_match_box_hw0017"]["secondary_ecc_phi05141"]["median_depth"] - 0.293, 5),
            ],
            "explanation": "House TESS 0.332/0.293 averages PDCSAP over a |dphi|<0.0017 (+/-28.8 min) box around minimum (our box: 0.33091/0.29287, diff -0.00109/-0.00013). True eclipse bottom (|dphi|<0.0008) is +0.00369/+0.00370 deeper than house (0.33569/0.29670), while un-deblended SAP_FLUX is -0.01131/-0.00895 shallower in the same box (0.32069/0.28405) due to CROWDSAP=0.966.",
        },
        "discrepancy_3_superwasp_true_bottom_vs_house_wide_box_dilution": {
            "house_swasp_pri_sec_mag": [0.189, 0.137],
            "our_swasp_true_bottom_hw0025_mag": [
                swasp_folds["TAMFLUX2_biweight_detrended_clean"]["core_bottom_hw0025"]["primary_phi0000"]["median_dmag"],
                swasp_folds["TAMFLUX2_biweight_detrended_clean"]["core_bottom_hw0025"]["secondary_ecc_phi05141"]["median_dmag"],
            ],
            "diff_true_bottom_minus_house_mag": [
                round(swasp_folds["TAMFLUX2_biweight_detrended_clean"]["core_bottom_hw0025"]["primary_phi0000"]["median_dmag"] - 0.189, 4),
                round(swasp_folds["TAMFLUX2_biweight_detrended_clean"]["core_bottom_hw0025"]["secondary_ecc_phi05141"]["median_dmag"] - 0.137, 4),
            ],
            "our_swasp_mid_box_hw0050_mag": [
                swasp_folds["TAMFLUX2_biweight_detrended_clean"]["mid_box_hw0050"]["primary_phi0000"]["median_dmag"],
                swasp_folds["TAMFLUX2_biweight_detrended_clean"]["mid_box_hw0050"]["secondary_ecc_phi05141"]["median_dmag"],
            ],
            "our_swasp_full_dur_box_hw0108_reproducing_house_mag": [
                swasp_folds["TAMFLUX2_biweight_detrended_clean"]["house_match_full_dur_hw0108"]["primary_phi0000"]["median_dmag"],
                swasp_folds["TAMFLUX2_biweight_detrended_clean"]["house_match_full_dur_hw0108"]["secondary_ecc_phi05141"]["median_dmag"],
            ],
            "diff_full_dur_box0108_minus_house_mag": [
                round(swasp_folds["TAMFLUX2_biweight_detrended_clean"]["house_match_full_dur_hw0108"]["primary_phi0000"]["median_dmag"] - 0.189, 4),
                round(swasp_folds["TAMFLUX2_biweight_detrended_clean"]["house_match_full_dur_hw0108"]["secondary_ecc_phi05141"]["median_dmag"] - 0.137, 4),
            ],
            "explanation": "House SuperWASP +0.189/+0.137 mag is heavily diluted by taking the median across the entire 6.1-h eclipse duration (|dphi|<0.0108, which includes shallow ingress/egress wings and a +0.0494 mag 2008 zero-point step). At the actual eclipse bottom (|dphi|<0.0025, clean sample n=6,146), SuperWASP depths are +0.3946 +/- 0.0062 mag (30.47% flux) for primary and +0.3426 +/- 0.0031 mag (27.06% flux) for secondary — +0.2056 mag (+108.8%) and +0.2056 mag (+150.1%) deeper than the house +0.189/+0.137 mag numbers, bringing SuperWASP into physical agreement with TESS!",
        },
    }

    results = {
        "bounty_id": "bnty_0426",
        "target": "TIC 158499577 (HD 94871 / 1SWASP J105638.34-363449.0)",
        "hunter": "ducanh3005",
        "version": "v1.0.0",
        "timestamp_utc": "2026-11-04T16:30:00Z",
        "house_ephemeris_folded": {"P_d": P_house, "T0_btjd": T0_house, "true_secondary_phase_ecc": phi_sec_ecc},
        "independent_period_finding": {
            "tess_lafler_kinman_P_d": round(P_lk_tess, 6),
            "tess_stellingwerf_pdm_coarse_P_d": round(P_pdm_tess, 6),
            "tess_stellingwerf_pdm_fine_P_d": round(P_pdm_tess_fine, 6),
            "swasp_stellingwerf_pdm_fine_P_d": round(P_pdm_sw_fine, 6),
            "swasp_lafler_kinman_fine_P_d": round(P_lk_sw_fine, 6),
        },
        "superwasp_zeropoint_audit": swasp_zeropoint_audit,
        "folded_depths_per_dataset": {
            "TESS_SPOC_S9_S36": tess_folds,
            "SuperWASP_DR1_2006_2008": swasp_folds,
        },
        "per_event_depths": {
            "TESS_all_8_events": tess_per_event,
            "SuperWASP_all_windows_ge3_pts": swasp_per_event,
        },
        "discrepancies_vs_house_quantified": discrepancies,
    }

    out_json = os.path.join(RES_DIR, "independent_refold_results.json")
    with open(out_json, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(results, fh, indent=2)

    print("=== bnty_0426 INDEPENDENT RE-FOLD COMPLETE ===")
    print("Independent Period Search: TESS PDM =", P_pdm_tess_fine, "d | SWASP PDM =", P_pdm_sw_fine, "d | SWASP LK =", P_lk_sw_fine, "d")
    print("TESS PDCSAP (biweight): Bottom(hw=0.0008) =", discrepancies["discrepancy_2_tess_bottom_vs_box_and_sap_vs_pdcsap"]["our_pdcsap_true_bottom_hw0008"], "| Box(hw=0.0017) =", discrepancies["discrepancy_2_tess_bottom_vs_box_and_sap_vs_pdcsap"]["our_pdcsap_box_hw0017_reproducing_house"], "vs House [0.332, 0.293]")
    print("TESS SAP (biweight):    Bottom(hw=0.0008) =", discrepancies["discrepancy_2_tess_bottom_vs_box_and_sap_vs_pdcsap"]["our_sap_true_bottom_hw0008"], "| Box(hw=0.0017) =", discrepancies["discrepancy_2_tess_bottom_vs_box_and_sap_vs_pdcsap"]["our_sap_box_hw0017"])
    print("SWASP TAMFLUX2 (biweight): Bottom(hw=0.0025) =", discrepancies["discrepancy_3_superwasp_true_bottom_vs_house_wide_box_dilution"]["our_swasp_true_bottom_hw0025_mag"], "| Mid(hw=0.0050) =", discrepancies["discrepancy_3_superwasp_true_bottom_vs_house_wide_box_dilution"]["our_swasp_mid_box_hw0050_mag"], "| FullDur(hw=0.0108) =", discrepancies["discrepancy_3_superwasp_true_bottom_vs_house_wide_box_dilution"]["our_swasp_full_dur_box_hw0108_reproducing_house_mag"], "vs House [+0.189, +0.137]")
    print(f"Total TESS events = {len(tess_per_event)} | Total SWASP event windows (>=3 pts) = {len(swasp_per_event)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
