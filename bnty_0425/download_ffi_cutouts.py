#!/usr/bin/env python3
"""
download_ffi_cutouts.py — Query MAST TESSCut for all sectors covering TIC 158499577
(RA=164.1597484, Dec=-36.5803139) and download 11x11 FFI TPF cutouts for every unsearched
sector (plus sector manifest metadata).
"""

import io
import json
import os
import urllib.parse
import urllib.request
import zipfile

RAW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")
os.makedirs(RAW_DIR, exist_ok=True)

RA = 164.1597484
DEC = -36.5803139


def main():
    # 1. Query TESSCut sector endpoint
    sec_url = f"https://mast.stsci.edu/tesscut/api/v0.1/sector?ra={RA}&dec={DEC}"
    req = urllib.request.Request(sec_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        sec_body = r.read().decode("utf-8")
    with open(os.path.join(RAW_DIR, "tesscut_sectors.json"), "w", encoding="utf-8") as f:
        f.write(sec_body)
    sec_data = json.loads(sec_body)
    results = sec_data.get("results", [])
    print("TESSCut sectors found:", len(results))
    for s in results:
        print(" ", s)

    # 2. Download 11x11 astrocut FITS for every sector (especially unsearched FFI sectors)
    manifest_files = {}
    for s in results:
        sec_num = int(s["sector"])
        cut_url = (
            f"https://mast.stsci.edu/tesscut/api/v0.1/astrocut"
            f"?ra={RA}&dec={DEC}&y=11&x=11&sector={sec_num}"
        )
        print(f"Downloading TESSCut 11x11 FFI TPF for Sector {sec_num} ...")
        req_c = urllib.request.Request(cut_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req_c, timeout=180) as rc:
            zbytes = rc.read()
        with zipfile.ZipFile(io.BytesIO(zbytes)) as zf:
            names = zf.namelist()
            for nm in names:
                out_name = f"tesscut_s{sec_num:04d}_{os.path.basename(nm)}"
                out_path = os.path.join(RAW_DIR, out_name)
                with open(out_path, "wb") as fo:
                    fo.write(zf.read(nm))
                manifest_files[sec_num] = {
                    "sector": sec_num,
                    "sectorName": s.get("sectorName"),
                    "camera": s.get("camera"),
                    "ccd": s.get("ccd"),
                    "fits_file": out_name,
                    "size_bytes": os.path.getsize(out_path),
                }
                print(f"  Saved {out_name} ({os.path.getsize(out_path)} bytes)")

    with open(os.path.join(RAW_DIR, "tesscut_download_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest_files, f, indent=2)
    print("All TESSCut FFI cutouts downloaded successfully!")


if __name__ == "__main__":
    main()
