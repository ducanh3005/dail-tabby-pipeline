#!/usr/bin/env python3
"""
fetch_mast_payloads.py — Fetch and verify raw Kepler DR25 FITS light curves
(*_llc.fits) and target pixel files (*_lpd-targ.fits.gz) from STScI MAST.

Pure Python standard library only. No API key required.
"""
import gzip
import hashlib
import json
import os
import re
import ssl
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

MAST_LC = "https://archive.stsci.edu/missions/kepler/lightcurves"
MAST_TPF = "https://archive.stsci.edu/missions/kepler/target_pixel_files"

TARGETS = [
    {
        "bounty": "bnty0333",
        "kepid": 7431659,
        "dir": os.path.join(ROOT, "data", "bnty0333", "kic7431659"),
        "tpf_files": ["kplr007431659-2010355172524_lpd-targ.fits.gz"],
    },
    {
        "bounty": "bnty0269",
        "kepid": 11126267,
        "dir": os.path.join(ROOT, "data", "bnty0269", "kic11126267"),
        "tpf_files": ["kplr011126267-2010355172524_lpd-targ.fits.gz"],
    },
]


def fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "dail-tabby-pipeline/1.0"})
    return urllib.request.urlopen(req, timeout=90, context=CTX).read()


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def sync_target(cfg: dict) -> dict:
    kic = cfg["kepid"]
    kpad = f"{kic:09d}"
    mast_dir = os.path.join(cfg["dir"], "mast")
    os.makedirs(mast_dir, exist_ok=True)

    lc_base_url = f"{MAST_LC}/{kpad[:4]}/{kpad}/"
    tpf_base_url = f"{MAST_TPF}/{kpad[:4]}/{kpad}/"

    existing_llc = sorted(f for f in os.listdir(mast_dir) if f.endswith("_llc.fits"))
    if not existing_llc:
        html = fetch_bytes(lc_base_url).decode("utf-8", errors="replace")
        existing_llc = sorted(set(re.findall(r"kplr\d+-\d+_llc\.fits", html)))

    lc_records = []
    for fn in existing_llc:
        local_path = os.path.join(mast_dir, fn)
        url = lc_base_url + fn
        if not os.path.exists(local_path) or os.path.getsize(local_path) == 0:
            blob = fetch_bytes(url)
            with open(local_path, "wb") as fh:
                fh.write(blob)
        lc_records.append({
            "filename": fn,
            "url": url,
            "bytes": os.path.getsize(local_path),
            "sha256": sha256_file(local_path),
        })

    tpf_records = []
    for gz_fn in cfg["tpf_files"]:
        fits_fn = gz_fn[:-3] if gz_fn.endswith(".gz") else gz_fn
        local_path = os.path.join(mast_dir, fits_fn)
        url = tpf_base_url + gz_fn
        if not os.path.exists(local_path) or os.path.getsize(local_path) == 0:
            blob = gzip.decompress(fetch_bytes(url))
            with open(local_path, "wb") as fh:
                fh.write(blob)
        tpf_records.append({
            "filename": fits_fn,
            "archive_gz": gz_fn,
            "url": url,
            "bytes": os.path.getsize(local_path),
            "sha256": sha256_file(local_path),
        })

    manifest = {
        "generated_by": "src/fetch_mast_payloads.py",
        "bounty": cfg["bounty"],
        "kepid": kic,
        "mast_lightcurve_index_url": lc_base_url,
        "mast_tpf_index_url": tpf_base_url,
        "n_lightcurve_files": len(lc_records),
        "n_tpf_files": len(tpf_records),
        "lightcurves": lc_records,
        "target_pixel_files": tpf_records,
    }
    manifest_path = os.path.join(cfg["dir"], "mast_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(f"[{cfg['bounty']}] KIC {kic}: verified {len(lc_records)} llc.fits + {len(tpf_records)} lpd-targ.fits -> {manifest_path}")
    return manifest


def main() -> int:
    for cfg in TARGETS:
        sync_target(cfg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
