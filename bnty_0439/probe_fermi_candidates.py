import json
import urllib.request
import urllib.parse
import os

TARGETS = [
    {"name": "4FGL J0251.1-1830", "short": "J0251.1-1830", "ra": 42.7835, "dec": -18.5093, "glat": -61.19, "amaj95": 0.0343, "bmin95": 0.0342, "pa95": -41.5},
]

HEASARC_CATS = [
    "fermilpsc", "swift2sxps", "rass2rxs", "xmmssc", "csc",
    "nvss", "sumss", "first", "vlssr", "milliquas", "wibrals", "romabzcat", "atnfpulsar"
]

RAW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")
os.makedirs(RAW_DIR, exist_ok=True)

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "ducanh3005-fermi-vetter/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")

def query_mast_tic(ra, dec, radius_deg=0.05):
    req_obj = {
        "service": "Mast.Catalogs.Filtered.Tic.Position",
        "format": "json",
        "params": {
            "columns": "ID,ra,dec,GAIA,TWOMASS,ALLWISE,UCAC4,Tmag,e_Tmag,Vmag,e_Vmag,Bmag,e_Bmag,Gmag,e_Gmag,BPmag,RPmag,Jmag,Hmag,Kmag,w1mag,e_w1mag,w2mag,e_w2mag,w3mag,e_w3mag,w4mag,e_w4mag,plx,e_plx,pmRA,e_pmRA,pmDEC,e_pmDEC,objType",
            "filters": [],
            "ra": ra,
            "dec": dec,
            "radius": radius_deg
        }
    }
    url = "https://mast.stsci.edu/api/v0/invoke?request=" + urllib.parse.quote(json.dumps(req_obj))
    return fetch(url, timeout=20)

for t in TARGETS:
    s = t["short"]
    ra, dec = t["ra"], t["dec"]
    print(f"=== Probing {t['name']} ({ra}, {dec}) ===")
    mast_txt = query_mast_tic(ra, dec, radius_deg=0.05)
    with open(os.path.join(RAW_DIR, f"{s}_mast_tic_3arcmin.json"), "w", encoding="utf-8") as f:
        f.write(mast_txt)
    print(f"  MAST TIC (<=3'): {len(json.loads(mast_txt).get('data', []))} rows")

    ned_url = f"https://ned.ipac.caltech.edu/cgi-bin/objsearch?search_type=Near+Position+Search&in_csys=Equatorial&in_equinox=J2000.0&lon={ra}d&lat={dec}d&radius=3.0&of=ascii_bar"
    ned_txt = fetch(ned_url, timeout=20)
    with open(os.path.join(RAW_DIR, f"{s}_ned_3arcmin.txt"), "w", encoding="utf-8") as f:
        f.write(ned_txt)
    ned_lines = [ln for ln in ned_txt.splitlines() if ln and ln[0].isdigit() and "|" in ln]
    print(f"  NED (<=3'): {len(ned_lines)} rows")

    for cat in HEASARC_CATS:
        h_url = f"https://heasarc.gsfc.nasa.gov/db-perl/W3Browse/w3query.pl?tablehead=name%3D{cat}&Action=Query&Entry={ra},{dec}&Radius=5&Radius_unit=arcmin&displaymode=BatchDisplay&Fields=All"
        h_txt = fetch(h_url, timeout=15)
        with open(os.path.join(RAW_DIR, f"{s}_heasarc_{cat}.txt"), "w", encoding="utf-8") as f:
            f.write(h_txt)
        data_lines = [ln for ln in h_txt.splitlines() if ln.startswith("|") and not ln.startswith("|name") and not ln.startswith("|srcid") and not ln.startswith("|---")]
        if data_lines:
            print(f"  HEASARC {cat} (<=5'): {len(data_lines)} rows -> {data_lines[0][:100]}")
