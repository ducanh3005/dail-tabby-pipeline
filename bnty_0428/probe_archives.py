#!/usr/bin/env python3
"""
probe_archives.py — Query public archives for ATLAS, KELT-South, HATSouth, Evryscope
and supplementary wide-field catalogs around TIC 158499577 (RA=164.1597484, Dec=-36.5803139).
"""

import json
import os
import urllib.parse
import urllib.request

RAW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")
os.makedirs(RAW_DIR, exist_ok=True)

RA = 164.1597484
DEC = -36.5803139


def fetch_url(url, fn, timeout=30):
    path = os.path.join(RAW_DIR, fn)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; Python-urllib)"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode("utf-8", errors="replace")
            status = r.status
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)
        return {"ok": True, "status": status, "len": len(body), "file": fn, "preview": body[:300]}
    except Exception as e:
        err_obj = {"ok": False, "error": str(e), "url": url}
        with open(path + ".err.json", "w", encoding="utf-8") as f:
            json.dump(err_obj, f, indent=2)
        return err_obj


def tap_nea(query, fn):
    url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=" + urllib.parse.quote(query) + "&format=json"
    return fetch_url(url, fn, timeout=40)


def vizier_tsv(source, radius_arcsec, fn, extra=""):
    url = (
        f"https://vizier.cds.unistra.fr/viz-bin/asu-tsv?-source={urllib.parse.quote(source)}"
        f"&-c={RA:.6f}{DEC:+.6f}&-c.rs={radius_arcsec}&-out.max=50{extra}"
    )
    return fetch_url(url, fn, timeout=30)


def main():
    log = {}

    # 1. KELT-South on NASA Exoplanet Archive (kelttimeseries)
    log["kelt_cone_1deg"] = tap_nea(
        f"select * from kelttimeseries where ra between {RA-1.0} and {RA+1.0} and dec between {DEC-1.0} and {DEC+1.0}",
        "nea_kelt_box1deg.json",
    )
    log["kelt_cone_2p5deg"] = tap_nea(
        f"select * from kelttimeseries where ra between {RA-2.5} and {RA+2.5} and dec between {DEC-2.5} and {DEC+2.5}",
        "nea_kelt_box2p5deg.json",
    )
    log["kelt_S23_southern_edge"] = tap_nea(
        "select top 10 kelt_sourceid,kelt_field,kelt_orientation,proc_type,ra,dec,kelt_mag,bjdstart,bjdstop,npts "
        "from kelttimeseries where kelt_field='S23' and ra between 163.5 and 164.8 order by dec asc",
        "nea_kelt_S23_southern_edge.json",
    )
    log["kelt_S24_western_edge"] = tap_nea(
        "select top 10 kelt_sourceid,kelt_field,kelt_orientation,proc_type,ra,dec,kelt_mag,bjdstart,bjdstop,npts "
        "from kelttimeseries where kelt_field='S24' and dec between -37.0 and -36.0 order by ra asc",
        "nea_kelt_S24_western_edge.json",
    )

    # 2. ATLAS: VizieR Refcat2 (J/ApJ/867/105), ATLAS Variable Stars (J/AJ/156/241), and forcedphot portal status
    log["atlas_refcat2_vizier"] = vizier_tsv("J/ApJ/867/105/refcat2", 30, "vizier_atlas_refcat2.tsv", "&-out.all=1")
    log["atlas_var_vizier"] = vizier_tsv("J/AJ/156/241", 120, "vizier_atlas_var.tsv", "&-out.all=1")
    log["atlas_forcedphot_web"] = fetch_url("https://fallingstar-data.com/forcedphot/", "atlas_forcedphot_index.html", timeout=20)

    # 3. HATSouth: VizieR HATSouth catalogs + hatsouth.org public pages
    log["hatsouth_vizier_meta"] = fetch_url(
        "https://vizier.cds.unistra.fr/viz-bin/asu-tsv?-words=HATSouth&-meta=1",
        "vizier_hatsouth_catalogs.tsv",
        timeout=25,
    )
    log["hatsouth_org_planets"] = fetch_url("https://hatsouth.org/planets/", "hatsouth_org_planets.html", timeout=20)
    log["hatsouth_org_lcs"] = fetch_url("https://hatsouth.org/ planets/lightcurves.html".replace(" ", ""), "hatsouth_org_lcs.html", timeout=20)

    # 4. Evryscope: VizieR Evryscope catalogs
    log["evryscope_vizier_meta"] = fetch_url(
        "https://vizier.cds.unistra.fr/viz-bin/asu-tsv?-words=Evryscope&-meta=1",
        "vizier_evryscope_catalogs.tsv",
        timeout=25,
    )
    log["evryscope_south_crests"] = vizier_tsv("J/ApJ/889/117", 300, "vizier_evryscope_J_ApJ_889_117.tsv")
    log["evryscope_mdwarfs"] = vizier_tsv("J/ApJ/890/115", 300, "vizier_evryscope_J_ApJ_890_115.tsv")

    # 5. MAST Caom Cone for any HLSP at target (ATLAS, KELT, Evryscope, QLP, TESS-SPOC, GSFC-ELEANOR-LITE)
    mast_payload = json.dumps({
        "service": "Mast.Caom.Cone",
        "params": {"ra": RA, "dec": DEC, "radius": 0.05},
        "format": "json",
        "pagesize": 200,
        "page": 1,
    }).encode("utf-8")
    req_m = urllib.request.Request(
        "https://mast.stsci.edu/api/v0/invoke",
        data=urllib.parse.urlencode({"request": mast_payload.decode("utf-8")}).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Mozilla/5.0"},
        method="POST",
    )
    with urllib.request.urlopen(req_m, timeout=40) as rm:
        mast_body = rm.read().decode("utf-8")
    with open(os.path.join(RAW_DIR, "mast_caom_cone_all.json"), "w", encoding="utf-8") as f:
        f.write(mast_body)
    mast_json = json.loads(mast_body)
    rows = mast_json.get("data", [])
    by_coll = {}
    for r in rows:
        c = r.get("obs_collection")
        by_coll[c] = by_coll.get(c, 0) + 1
    log["mast_caom_collections"] = by_coll

    # 6. Check ASAS-3 (II/264) & Hipparcos (I/239) on VizieR as supplementary wide-field check
    log["vizier_asas3"] = vizier_tsv("II/264", 60, "vizier_asas3.tsv", "&-out.all=1")
    log["vizier_hipparcos"] = vizier_tsv("I/239", 60, "vizier_hipparcos.tsv", "&-out.all=1")

    with open(os.path.join(RAW_DIR, "probe_summary.json"), "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)
    print(json.dumps(log, indent=2))


if __name__ == "__main__":
    main()
