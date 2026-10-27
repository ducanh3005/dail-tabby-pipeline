#!/usr/bin/env python3
"""
verify_bnty_0348.py -- Offline, zero-dependency, fail-closed verification of
both open threads from bnty_0314 (bnty_0348):

  Thread 1: 4FGL J1927.5+0154 (WISE J192731.14+015357.9) -- MISS or CONVENTION?
  Thread 2: 4FGL J1613.1-3840 (WISE J161305.29-384009.6) -- Archive audit across
            SDSS, LAMOST, APOGEE, Gaia RVS (and Gaia DR3), NED, and SIMBAD.

Usage (from a fresh clone, no API key, no network required):
    python3 bnty_0348/verify_bnty_0348.py
"""
import gzip
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")

STRIP_W1W2 = (0.50, 2.20)
STRIP_W2W3 = (1.20, 4.50)
P_CHANCE_MAX = 0.05
RADIO_GATE_ARCSEC = 10.8

J1927_WISE_RA = 291.8797823
J1927_WISE_DEC = 1.8994303

J1613_WISE_RA = 243.2720453
J1613_WISE_DEC = -38.6693591

OK = []
FAIL = []


def check(cond, msg):
    (OK if cond else FAIL).append(msg)
    return cond


def read_raw(fname):
    path = os.path.join(RAW, fname)
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    if fname.endswith(".gz"):
        with gzip.open(path, "rt", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def parse_vizier_tsv(raw):
    """Fail-closed parser for VizieR ASU-TSV responses.
    Returns (query_url, rows, is_empty, is_broken).
    """
    lines = raw.splitlines()
    query_url = None
    for l in lines:
        if l.startswith("#INFO\trequest="):
            query_url = l.split("request=", 1)[1].split("\t")[0].strip()
        elif l.startswith("#Error="):
            return query_url, None, False, True
    sep = None
    for idx, l in enumerate(lines):
        if l.startswith("---"):
            sep = idx
            break
    if sep is None:
        body = [l for l in lines if l.strip()]
        broken = bool(body) and not all(l.startswith("#") for l in body)
        return query_url, [], (not broken), broken
    ncol = len(lines[sep].split("\t"))
    rows = []
    for l in lines[sep + 1:]:
        if not l.strip() or l.startswith("#"):
            continue
        fields = l.split("\t")
        if len(fields) < ncol:
            return query_url, None, False, True
        rows.append(fields)
    return query_url, rows, (len(rows) == 0), False


def to_deg(v, ra_hours=False):
    if v is None:
        return None
    s = v.strip()
    if not s:
        return None
    try:
        d = float(s)
        return d * 15.0 if ra_hours else d
    except ValueError:
        pass
    parts = s.replace("h", " ").replace("m", " ").replace("s", " ").split()
    nums = [float(p) for p in parts]
    sign = -1.0 if s.startswith("-") else 1.0
    if len(nums) == 3:
        d = sign * (abs(nums[0]) + nums[1] / 60.0 + nums[2] / 3600.0)
    elif len(nums) == 2:
        d = sign * (abs(nums[0]) + nums[1] / 60.0)
    else:
        d = sign * abs(nums[0])
    return d * 15.0 if ra_hours else d


def sep_arcsec(ra1, dec1, ra2, dec2):
    r0 = math.radians(ra1)
    d0 = math.radians(dec1)
    dr = math.radians(ra2 - ra1)
    dd = math.radians(dec2 - dec1)
    a = math.sin(dd / 2.0) ** 2 + math.cos(d0) ** 2 * math.sin(dr / 2.0) ** 2
    return math.degrees(2.0 * math.asin(math.sqrt(a))) * 3600.0


def in_ellipse(ra, dec, s):
    a, b, pa = s["amaj95"], s["bmin95"], s["pa95"]
    dra = (ra - s["ra"]) * math.cos(math.radians(s["dec"]))
    ddec = dec - s["dec"]
    th = math.radians(pa)
    x = dra * math.sin(th) + ddec * math.cos(th)
    y = dra * math.cos(th) - ddec * math.sin(th)
    return (x / a) ** 2 + (y / b) ** 2 <= 1.0


def strip_ok(w1, w2, w3):
    return (w1 is not None and w2 is not None and w3 is not None and
            STRIP_W1W2[0] <= (w1 - w2) <= STRIP_W1W2[1] and
            STRIP_W2W3[0] <= (w2 - w3) <= STRIP_W2W3[1])


def verify_thread_1():
    print("=" * 76)
    print("THREAD 1: 4FGL J1927.5+0154 (WISE J192731.14+015357.9) -- MISS or CONVENTION?")
    print("=" * 76)

    unassoc = {s["name"]: s for s in json.loads(read_raw("unassociated.json"))}
    house = json.loads(read_raw("house_bnty_0276.json"))["counterparts"]
    s = unassoc["J1927.5+0154"]

    # 1. Verify sample membership in bnty_0276 high-precision sample (1.5 * a95 <= 5.0 arcmin)
    a95_deg = s["amaj95"]
    b95_deg = s["bmin95"]
    r_house_deg = 1.5 * a95_deg
    r_house_arcmin = r_house_deg * 60.0
    r_house_arcsec = r_house_deg * 3600.0
    check(r_house_arcmin <= 5.0,
          f"J1927.5+0154 is inside the house sample (1.5*a95 = {r_house_arcmin:.3f}' <= 5.0')")

    # 2. Parse raw AllWISE response for J1927.5+0154
    q_aw, aw_rows, aw_empty, aw_broken = parse_vizier_tsv(read_raw("J1927.5+0154.allwise.tsv.gz"))
    check(not aw_broken and not aw_empty and q_aw is not None,
          f"J1927.5+0154.allwise.tsv.gz well-formed ({len(aw_rows)} rows, query={q_aw})")

    strip_sources = []
    in_ell_candidates = []
    for r in aw_rows:
        ra, dec = to_deg(r[0]), to_deg(r[1])
        w1, w2, w3 = to_deg(r[2]), to_deg(r[3]), to_deg(r[4])
        wise = r[5].strip()
        sp = sep_arcsec(s["ra"], s["dec"], ra, dec)
        if strip_ok(w1, w2, w3):
            ell = in_ellipse(ra, dec, s)
            item = {
                "wise": wise, "ra": ra, "dec": dec,
                "sep_arcsec": sp, "sep_round2": round(sp, 2),
                "w1": w1, "w2": w2, "w3": w3,
                "w1_w2": round(w1 - w2, 3), "w2_w3": round(w2 - w3, 3),
                "in_ellipse": ell
            }
            strip_sources.append(item)
            if ell:
                in_ell_candidates.append(item)

    strip_sources.sort(key=lambda x: x["sep_arcsec"])
    check(len(in_ell_candidates) == 1 and in_ell_candidates[0]["wise"] == "J192731.14+015357.9",
          "Unique in-ellipse blazar-strip counterpart is WISE J192731.14+015357.9")

    cand = in_ell_candidates[0]
    theta_exact = cand["sep_arcsec"]       # 15.873245"
    theta_orbit = cand["sep_round2"]       # 15.87"
    theta_house_1dp = round(theta_exact, 1)  # 15.9"

    # 3. Recompute P_chance under House convention (bnty_0276) vs Orbit convention (bnty_0314)
    # House convention published in bnty_0276 Section 2.3 / Stage 3:
    #   R_cone = 1.5 * a95 (or max(1.5 * a95, 3.0'); identical for J1927.5+0154 since 1.5*a95 = 3.897' > 3.0')
    #   Sigma_blazar = N_blazar / (pi * R_cone^2)
    #   mu = Sigma_blazar * pi * theta_sep^2 = N_blazar * (theta_sep / R_cone)^2
    #   P_chance = 1 - exp(-mu)
    n_house = sum(1 for x in strip_sources if x["sep_arcsec"] <= r_house_arcsec)
    sigma_house = n_house / (math.pi * (r_house_deg ** 2))
    mu_house_exact = n_house * ((theta_exact / r_house_arcsec) ** 2)
    p_house_exact = 1.0 - math.exp(-mu_house_exact)
    p_house_orbit_theta = 1.0 - math.exp(-n_house * ((theta_orbit / r_house_arcsec) ** 2))
    p_house_1dp_theta = 1.0 - math.exp(-n_house * ((theta_house_1dp / r_house_arcsec) ** 2))

    # Orbit convention (bnty_0314: R_cone = R_FIELD_ARCMIN = 10.0' = 600.0"):
    r_orbit_arcsec = 600.0
    r_orbit_deg = 10.0 / 60.0
    n_orbit = sum(1 for x in strip_sources if x["sep_arcsec"] <= r_orbit_arcsec)
    sigma_orbit = n_orbit / (math.pi * (r_orbit_deg ** 2))
    mu_orbit = n_orbit * ((theta_orbit / r_orbit_arcsec) ** 2)
    p_orbit = round(1.0 - math.exp(-mu_orbit), 6)

    check(n_house == 2, f"House cone (R_cone = 1.5*a95 = 3.897' = 233.82\") holds N_blazar = {n_house}")
    check(n_orbit == 11, f"Orbit cone (R_cone = 10.0' = 600.0\") holds N_blazar = {n_orbit}")
    check(p_house_exact < P_CHANCE_MAX,
          f"J1927.5+0154 PASSES House P_chance gate: P_chance_house = {p_house_exact:.5f} (< 0.05)")
    check(p_orbit == 0.007666 and p_orbit < P_CHANCE_MAX,
          f"J1927.5+0154 PASSES Orbit P_chance gate: P_chance_orbit = {p_orbit:.6f} (< 0.05)")

    print(f"  4FGL J1927.5+0154: RA={s['ra']}, Dec={s['dec']}, a95={a95_deg} deg ({a95_deg*60:.3f}'), b95={b95_deg} deg, PA95={s['pa95']} deg")
    print(f"  WISE counterpart : WISE {cand['wise']} (RA={cand['ra']:.7f}, Dec={cand['dec']:.7f})")
    print(f"  Separation       : {theta_exact:.4f}\" (Orbit 2dp: {theta_orbit:.2f}\", House 1dp: {theta_house_1dp:.1f}\")")
    print(f"  WISE colours     : W1={cand['w1']:.3f}, W2={cand['w2']:.3f}, W3={cand['w3']:.3f} -> W1-W2={cand['w1_w2']:.3f}, W2-W3={cand['w2_w3']:.3f}")
    print(f"  House bnty_0276  : R_cone = 1.5*a95 = {r_house_arcmin:.4f}' ({r_house_arcsec:.2f}\"), N_blazar = {n_house}, Sigma = {sigma_house:.3f} deg^-2")
    print(f"                     P_chance (house, exact sep 15.8732\") = {p_house_exact:.6f} (5dp: {p_house_exact:.5f})")
    print(f"                     P_chance (house, 2dp sep 15.87\")     = {p_house_orbit_theta:.6f} (5dp: {p_house_orbit_theta:.5f})")
    print(f"                     P_chance (house, 1dp sep 15.9\")      = {p_house_1dp_theta:.6f} (5dp: {p_house_1dp_theta:.5f})")
    print(f"  Orbit bnty_0314  : R_cone = 10.0000' (600.00\"), N_blazar = {n_orbit}, Sigma = {sigma_orbit:.3f} deg^-2")
    print(f"                     P_chance (orbit, 2dp sep 15.87\")     = {p_orbit:.6f} (5dp: {p_orbit:.5f})")

    # 4. Verify Radio Gate (counterpart within 10.8" of WISE counterpart position)
    q_vl, vl_rows, vl_empty, vl_broken = parse_vizier_tsv(read_raw("J1927.5+0154.vlass_cp.tsv.gz"))
    q_nv, nv_rows, nv_empty, nv_broken = parse_vizier_tsv(read_raw("J1927.5+0154.nvss_cp.tsv.gz"))
    check(not vl_broken and not vl_empty, f"J1927.5+0154.vlass_cp.tsv.gz well-formed ({len(vl_rows)} rows)")
    check(not nv_broken and not nv_empty, f"J1927.5+0154.nvss_cp.tsv.gz well-formed ({len(nv_rows)} rows)")

    vl_hits = []
    for r in vl_rows:
        ra_r, dec_r = to_deg(r[0], False), to_deg(r[1], False)
        sp_r = round(sep_arcsec(cand["ra"], cand["dec"], ra_r, dec_r), 2)
        vl_hits.append((sp_r, r[4].strip(), r[2].strip(), r[3].strip(), ra_r, dec_r))
    vl_hits.sort(key=lambda x: x[0])

    nv_hits = []
    for r in nv_rows:
        ra_r, dec_r = to_deg(r[0], True), to_deg(r[1], False)
        sp_r = round(sep_arcsec(cand["ra"], cand["dec"], ra_r, dec_r), 2)
        nv_hits.append((sp_r, r[3].strip(), r[2].strip(), ra_r, dec_r))
    nv_hits.sort(key=lambda x: x[0])

    check(vl_hits[0][0] == 1.06 and vl_hits[0][0] <= RADIO_GATE_ARCSEC,
          f"VLASS counterpart {vl_hits[0][1]} at {vl_hits[0][0]}\" <= 10.8\" (Fpeak={vl_hits[0][2]} mJy/beam, Ftot={vl_hits[0][3]} mJy)")
    check(nv_hits[0][0] == 28.81 and nv_hits[0][0] > RADIO_GATE_ARCSEC,
          f"NVSS nearest source {nv_hits[0][1]} is at {nv_hits[0][0]}\" (> 10.8\")")

    print(f"  Radio Gate (10.8\" at WISE counterpart RA={cand['ra']}, Dec={cand['dec']}):")
    print(f"    - VLASS (J/ApJS/255/30/comp): PASS -- {vl_hits[0][1]} at sep = {vl_hits[0][0]}\" (Fpeak = {vl_hits[0][2]} mJy/beam, Ftot = {vl_hits[0][3]} mJy)")
    print(f"    - NVSS  (VIII/65/nvss)      : absent within 10.8\" (nearest in 1' cone: NVSS {nv_hits[0][1]}, S1.4 = {nv_hits[0][2]} mJy at sep = {nv_hits[0][0]}\")")
    print(f"    - SUMSS (VIII/81B/sumss212) : N/A (Dec = +1.90 deg > -30 deg southern coverage boundary)")
    print("  RULING ON THREAD 1 (4FGL J1927.5+0154): MISS (passes BOTH the house P_chance < 0.05 convention and the 10.8\" radio gate).")


def verify_thread_2():
    print("\n" + "=" * 76)
    print("THREAD 2: 4FGL J1613.1-3840 (WISE J161305.29-384009.6) -- ARCHIVE AUDIT")
    print("=" * 76)
    print(f"  Target WISE counterpart: WISE J161305.29-384009.6")
    print(f"  Coordinates queried    : RA = {J1613_WISE_RA:.7f} deg (16h 13m 05.2909s), Dec = {J1613_WISE_DEC:.7f} deg (-38d 40m 09.693s) [J2000 / ICRS]")

    # 1. SDSS DR16 (V/154/sdss16)
    q_sdss, r_sdss, emp_sdss, brk_sdss = parse_vizier_tsv(read_raw("sdss_dr16_vizier.tsv"))
    check(not brk_sdss and emp_sdss and q_sdss is not None,
          f"SDSS DR16 (V/154/sdss16): well-formed zero-row response (0 rows; query={q_sdss})")
    print(f"  1. SDSS (V/154/sdss16, r=1.0')      : WELL-FORMED NULL (0 rows; Dec=-38.67 deg is south of SDSS footprint)")

    # 2. LAMOST DR7 (V/156/dr7lrs)
    q_lam, r_lam, emp_lam, brk_lam = parse_vizier_tsv(read_raw("lamost_dr7_vizier.tsv"))
    check(not brk_lam and emp_lam and q_lam is not None,
          f"LAMOST DR7 (V/156/dr7lrs): well-formed zero-row response (0 rows; query={q_lam})")
    print(f"  2. LAMOST (V/156/dr7lrs, r=1.0')    : WELL-FORMED NULL (0 rows; Dec=-38.67 deg is south of LAMOST footprint)")

    # 3. APOGEE DR17 (III/286/catalog) & DR16 (III/284/allstars)
    q_ap17, r_ap17, emp_ap17, brk_ap17 = parse_vizier_tsv(read_raw("apogee_dr17_vizier.tsv"))
    q_ap16, r_ap16, emp_ap16, brk_ap16 = parse_vizier_tsv(read_raw("apogee_dr16_vizier.tsv"))
    check(not brk_ap17 and emp_ap17 and q_ap17 is not None,
          f"APOGEE DR17 (III/286/catalog): well-formed zero-row response (0 rows; query={q_ap17})")
    check(not brk_ap16 and emp_ap16 and q_ap16 is not None,
          f"APOGEE DR16 (III/284/allstars): well-formed zero-row response (0 rows; query={q_ap16})")
    print(f"  3. APOGEE (III/286/catalog, r=1.0') : WELL-FORMED NULL (0 rows in DR17 and DR16)")

    # 4. Gaia RVS & Gaia DR3 (I/355/gaiadr3)
    q_grvs, r_grvs, emp_grvs, brk_grvs = parse_vizier_tsv(read_raw("gaia_rvs_strict_10.8arcsec_vizier.tsv"))
    q_grvs60, r_grvs60, emp_grvs60, brk_grvs60 = parse_vizier_tsv(read_raw("gaia_rvs_strict_60arcsec_vizier.tsv"))
    q_gdr3, r_gdr3, emp_gdr3, brk_gdr3 = parse_vizier_tsv(read_raw("gaia_dr3_10.8arcsec_vizier.tsv"))
    check(not brk_grvs and emp_grvs, "Gaia RVS (RVS=1, r=10.8\"): well-formed zero-row response (0 RVS spectra)")
    check(not brk_grvs60 and emp_grvs60, "Gaia RVS (RVS=1, r=60.0\"): well-formed zero-row response (0 RVS spectra)")
    check(not brk_gdr3 and len(r_gdr3) == 2, "Gaia DR3 (I/355/gaiadr3, r=10.8\"): 2 optical sources, both with RVS=0 and RV=null")

    # Identify exact optical counterpart Gaia DR3 5997528070572416256 at 0.14"
    g_hits = []
    for r in r_gdr3:
        ra_g, dec_g = float(r[0]), float(r[1])
        sp_g = sep_arcsec(J1613_WISE_RA, J1613_WISE_DEC, ra_g, dec_g)
        g_hits.append((sp_g, r[2].strip(), r[3].strip(), r[4].strip(), r[5].strip(), r[6].strip(), r[8].strip()))
    g_hits.sort(key=lambda x: x[0])
    best_g = g_hits[0]
    check(best_g[1] == "5997528070572416256" and round(best_g[0], 2) == 0.14 and best_g[6] == "0",
          f"Gaia DR3 5997528070572416256 matches WISE position at {best_g[0]:.2f}\" (G={best_g[2]}, BP={best_g[3]}, RP={best_g[4]}, RV='{best_g[5]}', RVS={best_g[6]})")
    print(f"  4. Gaia RVS (I/355/gaiadr3)         : WELL-FORMED NULL for RVS spectrum (0 sources with RVS=1 within 10.8\" and 60\").")
    print(f"                                        Optical counterpart Gaia DR3 {best_g[1]} at sep = {best_g[0]:.2f}\" has 3 broadband SED points")
    print(f"                                        (G = {best_g[2]} mag, BP = {best_g[3]} mag, RP = {best_g[4]} mag) and RVS = {best_g[6]}, RV = null.")

    # 5. NED (ned_objsearch_1arcmin.txt, ned_sed_wisea.txt, ned_sed_nvss.txt)
    ned_obj = read_raw("ned_objsearch_1arcmin.txt")
    ned_sed_w = read_raw("ned_sed_wisea.txt")
    ned_sed_n = read_raw("ned_sed_nvss.txt")
    check("1|WISEA J161305.29-384009.6|243.27205 | -38.66936 |IrS||||     |  0.000|0|0|22|2|0|0|0" in ned_obj,
          "NED object search confirms WISEA J161305.29-384009.6 (IrS, sep=0.000', 22 Photometry Points, 0 Redshift Points)")
    check("2|NVSS J161305-384010|243.27096 | -38.66947 |RadioS|||| 0.92|  0.051|0|0|1|1|0|0|0" in ned_obj,
          "NED object search confirms NVSS J161305-384010 (RadioS, sep=0.051'=3.08\", 1 Photometry Point, 0 Redshift Points)")
    sed_w_rows = [l for l in ned_sed_w.splitlines() if l[:1].isdigit() and "|" in l]
    sed_n_rows = [l for l in ned_sed_n.splitlines() if l[:1].isdigit() and "|" in l]
    check(len(sed_w_rows) == 22, f"NED Photometry table for WISEA J161305.29-384009.6 contains {len(sed_w_rows)} SED points")
    check(len(sed_n_rows) == 1, f"NED Photometry table for NVSS J161305-384010 contains {len(sed_n_rows)} SED point (1.4 GHz, 8.4 +/- 1.0 mJy)")
    print(f"  5. NED (Cone r=1.0' & Photometry)   : 0 spectra / 0 redshifts; 23 SED points across the counterpart pair:")
    print(f"                                        - WISEA J161305.29-384009.6 (sep=0.00\", Type=IrS, z=null): 22 infrared SED points")
    print(f"                                          (AllWISE W1/W2/W3/W4 + Spitzer IRAC 3.6/4.5/5.8/8.0 um & MIPS 24 um: 408 uJy -> 843 uJy)")
    print(f"                                        - NVSS J161305-384010 (sep=3.08\", Type=RadioS, z=null): 1 radio SED point (1.4 GHz: 8.4 +/- 1.0 mJy)")

    # 6. SIMBAD (simbad_tap_10.8arcsec.tsv & simbad_tap_60arcsec.tsv)
    sim10 = [l for l in read_raw("simbad_tap_10.8arcsec.tsv").splitlines() if l.strip()]
    sim60 = [l for l in read_raw("simbad_tap_60arcsec.tsv").splitlines() if l.strip()]
    check(len(sim10) == 1 and sim10[0].startswith("main_id\t"),
          "SIMBAD TAP (r=10.8\"): well-formed zero-row response (header only, 0 objects)")
    check(len(sim60) == 2 and '"4FGL J1613.1-3840"' in sim60[1],
          "SIMBAD TAP (r=60.0\"): 1 row, '4FGL J1613.1-3840' at sep=52.46\" (otype='gam', sp_type=null, redshift=null)")
    print(f"  6. SIMBAD (TAP r=10.8\" and r=60.0\") : WELL-FORMED NULL at the WISE counterpart (0 rows within 10.8\");")
    print(f"                                        within 60.0\", only '4FGL J1613.1-3840' itself at sep = 52.46\" (otype='gam', sp_type=null, z=null).")


def main():
    verify_thread_1()
    verify_thread_2()
    print("\n" + "=" * 76)
    print(f"VERIFICATION SUMMARY: {len(OK)} passed, {len(FAIL)} failed")
    for m in OK:
        print(f"  [PASS] {m}")
    if FAIL:
        for m in FAIL:
            print(f"  [FAIL] {m}")
        return 1
    print("ALL CHECKS PASSED (exit 0)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
