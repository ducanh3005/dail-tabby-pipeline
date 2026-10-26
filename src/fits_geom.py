#!/usr/bin/env python3
"""
bnty0269_fits_geom.py -- correct, self-contained FITS reader for the bnty_0269
target-pixel file, plus the empirical stamp-orientation test.

WHY THIS FILE EXISTS
--------------------
Three separate defects were found in the previously committed tooling for
bnty_0269 (KIC 9101271), and each of them changes a number that was
published:

1. The APERTURE image extension was read as int16. Its BITPIX is 32, so
   every aperture value read before was a mis-parse of half of an int32.
   src/fits_lc.py does not read image extensions at all -- it skips their
   data and then tries to parse them as binary tables -- so the aperture
   mask was never actually read from the file; it was guessed.

2. The stamp orientation was assumed. The 30 raw counts per cadence have a
   TDIM card, TDIM4 = '(6,5)', and the APERTURE image extension has
   NAXIS1 = 6, NAXIS2 = 5. Whether the 30 values run 6-wide or 5-wide
   decides the whole centroid geometry, and the two choices give
   centroids that differ by more than the gate tolerance. This file
   settles it empirically instead of by assumption.

3. Centroid shifts were published in pixels under a "_mpix" label in one
   place and in millipixels in another. Millipixels are pixels x 1000.

WHAT THIS FILE DOES
-------------------
* Walks the FITS file HDU by HDU, handling multi-block headers, and
  derives every data size from the header (BITPIX, NAXIS1, NAXIS2,
  TFORMn) rather than from a guessed byte offset.
* Reads the APERTURE image as int32 and prints it as a 6x5 grid.
* Reads the TARGETTABLES vector columns RAW_CNTS and FLUX.
* Runs the orientation test: for a bright cadence, builds the 30-pixel
  flux image under both candidate layouts and asks which one puts the
  flux peak on a pixel the APERTURE mask marks as target (value == 1),
  which one gives a smoother blob, and which one's centroid tracks
  POS_CORR1 / POS_CORR2.

Stdlib only. No numpy, no astropy.
"""
import json
import math
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TPF = os.path.join(
    ROOT, "data", "bnty0269", "kic9101271", "tpf", "009101271",
    "kplr009101271-2011271113734_lpd-targ.fits")

BLOCK = 2880
CARD = 80


# ---------------------------------------------------------------- FITS core

def _card_value(raw):
    """The value field of a FITS card, as a string."""
    if len(raw) < 10:
        return ""
    if raw[8:10] != "= ":
        # COMMENT / HISTORY / blank / CONTINUE
        return ""
    v = raw[10:].split("/")[0].strip()
    # strip a trailing unquoted string
    if v.startswith("'"):
        end = v.rfind("'")
        if end > 0:
            v = v[1:end].strip()
        return v
    return v.strip()


def read_header_blocks(fh):
    """Read one header, which may span several 2880-byte blocks.

    Returns (cards, end_offset). `cards` is a list of (key, value) pairs
    in file order, with the raw card text kept for the ones that matter.
    """
    cards = []
    while True:
        block = fh.read(BLOCK)
        if len(block) < BLOCK:
            break
        done = False
        for i in range(0, BLOCK, CARD):
            raw = block[i:i + CARD].decode("ascii", "replace")
            key = raw[:8].strip()
            if key == "END":
                done = True
                break
            if key in ("COMMENT", "HISTORY", "") or raw[8:10] != "= ":
                continue
            cards.append((key, _card_value(raw)))
        if done:
            break
    return cards, fh.tell()


def hget(cards, key, default=None):
    for k, v in cards:
        if k == key:
            return v
    return default


def hget_int(cards, key, default=None):
    v = hget(cards, key)
    if v is None:
        return default
    try:
        return int(v)
    except ValueError:
        return default


def tdim_of(cards, colname):
    """The TDIM shape of a vector column, from the TDIMn card whose
    matching TYPEn card names this column. Returns (n0, n1) or None."""
    for key, val in cards:
        if key.startswith("TDIM") and key[4:].isdigit():
            idx = int(key[4:])
            ttype = hget(cards, "TTYPE%d" % idx)
            if ttype and ttype.strip() == colname:
                s = val.strip().strip("()").replace(" ", "")
                try:
                    parts = [int(x) for x in s.split(",") if x != ""]
                except ValueError:
                    return None
                if len(parts) >= 2:
                    return parts[0], parts[1]
    return None


def tform_width(tform):
    """Bytes per element and element count for a TFORM string."""
    t = tform.strip()
    i = 0
    while i < len(t) and t[i].isdigit():
        i += 1
    repeat = int(t[:i]) if i else 1
    code = t[i:].strip().upper()
    if code == "A":
        return 1, repeat
    if code in ("L", "B", "A"):
        return 1, repeat
    if code == "I":
        return 2, repeat
    if code in ("J", "E"):
        return 4, repeat
    if code in ("D", "K"):
        return 8, repeat
    if code in ("C", "M"):
        return 8, repeat
    return 1, repeat


def read_image(fh, cards, offset):
    """Read an image HDU's data, using BITPIX/NAXISn for the size."""
    bitpix = hget_int(cards, "BITPIX", 8)
    naxis = hget_int(cards, "NAXIS", 0)
    shape = [hget_int(cards, "NAXIS%d" % (i + 1), 0) for i in range(naxis)]
    nelem = 1
    for s in shape:
        nelem *= s
    nbytes = nelem * abs(bitpix) // 8
    fh.seek(offset)
    raw = fh.read(nbytes)
    if bitpix == 32:
        vals = list(struct.unpack(">%di" % nelem, raw))
    elif bitpix == 16:
        vals = list(struct.unpack(">%dh" % nelem, raw))
    elif bitpix == 8:
        vals = list(struct.unpack(">%db" % nelem, raw))
    elif bitpix == -32:
        vals = list(struct.unpack(">%ff" % nelem, raw))
    elif bitpix == 64:
        vals = list(struct.unpack(">%dd" % nelem, raw))
    elif bitpix == -64:
        vals = list(struct.unpack(">d" * nelem, raw))
    else:
        vals = []
    bzero = hget_int(cards, "BZERO", 0)
    bscale = hget_int(cards, "BSCALE", 1) or 1
    if bzero:
        vals = [v * bscale + bzero for v in vals]
    return vals, shape


def read_table(fh, cards, offset):
    """Read a binary table HDU. Returns (rows, cols) where cols is a list
    of (name, values, tform)."""
    rows = hget_int(cards, "NAXIS2", 0)
    rowlen = hget_int(cards, "NAXIS1", 0)
    tfields = hget_int(cards, "TFIELDS", 0)
    fields = []
    for i in range(1, tfields + 1):
        tform = hget(cards, "TFORM%d" % i, "")
        name = hget(cards, "TTYPE%d" % i, "")
        width, count = tform_width(tform)
        fields.append({"name": name, "tform": tform, "width": width,
                       "count": count, "off": None})
    off = 0
    for f in fields:
        f["off"] = off
        off += f["width"] * f["count"]
    if off != rowlen:
        sys.stderr.write("WARNING: field widths sum to %d, NAXIS1=%d\n"
                         % (off, rowlen))
    fh.seek(offset)
    raw = fh.read(rowlen * rows)
    cols = []
    for f in fields:
        code = f["tform"].strip().lstrip("0123456789").upper()
        vals = []
        for r in range(rows):
            base = r * rowlen + f["off"]
            chunk = raw[base:base + f["width"] * f["count"]]
            if code == "J":
                v = list(struct.unpack(">%di" % f["count"], chunk))
            elif code == "I":
                v = list(struct.unpack(">%dh" % f["count"], chunk))
            elif code == "E":
                v = list(struct.unpack(">%df" % f["count"], chunk))
            elif code == "D":
                v = list(struct.unpack(">%dd" % f["count"], chunk))
            else:
                v = None
            if v is not None and f["count"] == 1:
                # a scalar column: store the bare value, not a 1-element list
                v = v[0]
            vals.append(v)
        cols.append((f["name"], vals, f["tform"]))
    return rows, cols


def walk_hdus(path):
    """Yield (name, cards, data_offset) for every HDU in the file."""
    with open(path, "rb") as fh:
        cards, off = read_header_blocks(fh)
        naxis = hget_int(cards, "NAXIS", 0)
        yield ("PRIMARY", cards, off)
        if naxis:
            shape = [hget_int(cards, "NAXIS%d" % (i + 1), 0)
                     for i in range(naxis)]
            nelem = 1
            for s in shape:
                nelem *= s
            bitpix = hget_int(cards, "BITPIX", 8)
            nbytes = nelem * abs(bitpix) // 8
            off += ((nbytes + BLOCK - 1) // BLOCK) * BLOCK
        while True:
            fh.seek(off)
            cards, doff = read_header_blocks(fh)
            if not cards:
                break
            name = hget(cards, "XTENSION", "EXT")
            extname = hget(cards, "EXTNAME", name)
            yield (extname, cards, doff)
            naxis = hget_int(cards, "NAXIS", 0)
            if naxis == 0:
                break
            if hget(cards, "XTENSION", "") == "BINTABLE" or \
               hget_int(cards, "TFIELDS", 0) > 0:
                rowlen = hget_int(cards, "NAXIS1", 0)
                nrows = hget_int(cards, "NAXIS2", 0)
                nbytes = rowlen * nrows
            else:
                shape = [hget_int(cards, "NAXIS%d" % (i + 1), 0)
                         for i in range(naxis)]
                nelem = 1
                for s in shape:
                    nelem *= s
                bitpix = hget_int(cards, "BITPIX", 8)
                nbytes = nelem * abs(bitpix) // 8
            off = doff + ((nbytes + BLOCK - 1) // BLOCK) * BLOCK


# ------------------------------------------------------------- orientation

def flux_centroid(vals, ncol, nrow, weights=None):
    """Flux-weighted centroid of a nrow x ncol image given in row-major
    order (index = row * ncol + col). Returns (cx, cy, total)."""
    tot = 0.0
    sx = 0.0
    sy = 0.0
    for idx, v in enumerate(vals):
        if v is None:
            continue
        w = float(v)
        if weights is not None:
            w *= weights[idx]
        if w <= 0:
            continue
        r = idx // ncol
        c = idx % ncol
        tot += w
        sx += w * c
        sy += w * r
    if tot <= 0:
        return (float("nan"), float("nan"), 0.0)
    return (sx / tot, sy / tot, tot)


def blob_smoothness(vals, ncol, nrow, mask):
    """Mean absolute difference between the 4-neighbour flux differences,
    over pixels the aperture mask marks as target. A correctly oriented
    stamp gives a smooth blob; a transposed one smears the PSF."""
    num = 0.0
    cnt = 0
    for r in range(nrow):
        for c in range(ncol):
            i = r * ncol + c
            if not mask[i]:
                continue
            for dr, dc in ((0, 1), (1, 0)):
                rr = r + dr
                cc = c + dc
                if rr >= nrow or cc >= ncol:
                    continue
                j = rr * ncol + cc
                if not mask[j]:
                    continue
                num += abs(vals[i] - vals[j])
                cnt += 1
    if cnt == 0:
        return float("nan")
    return num / cnt


def main():
    out = {"tpf": os.path.relpath(TPF, ROOT)}

    # ---- 1. HDU walk ----------------------------------------------------
    hdus = []
    for name, cards, doff in walk_hdus(TPF):
        naxis = hget_int(cards, "NAXIS", 0)
        info = {
            "extname": name,
            "naxis": naxis,
            "bitpix": hget_int(cards, "BITPIX"),
            "shape": [hget_int(cards, "NAXIS%d" % (i + 1), 0)
                      for i in range(naxis)],
            "nrows": hget_int(cards, "NAXIS2"),
            "rowlen": hget_int(cards, "NAXIS1"),
            "tfields": hget_int(cards, "TFIELDS"),
        }
        hdus.append(info)
    out["hdus"] = hdus

    # ---- 2. APERTURE image (int32) --------------------------------------
    aperture = None
    for name, cards, doff in walk_hdus(TPF):
        if name.upper() != "APERTURE":
            continue
        vals, shape = read_image(open(TPF, "rb"), cards, doff)
        n1 = shape[0]
        n2 = shape[1]
        aperture = {"shape": [n1, n2], "values": vals}
        break

    if aperture is None:
        # fall back: any extension with NAXIS=2 and a small size
        for name, cards, doff in walk_hdus(TPF):
            if hget_int(cards, "NAXIS", 0) == 2:
                vals, shape = read_image(open(TPF, "rb"), cards, doff)
                aperture = {"shape": list(shape), "values": vals,
                            "extname_used": name}
                break

    if aperture is None:
        print("ERROR: no image extension found")
        return 1

    n1, n2 = aperture["shape"]
    out["aperture"] = {
        "shape": [n1, n2],
        "distinct_values": sorted(set(aperture["values"])),
        "grid_row_major": [aperture["values"][r * n1:(r + 1) * n1]
                           for r in range(n2)],
    }

    # ---- 3. TARGETTABLES -------------------------------------------------
    tt = None
    for name, cards, doff in walk_hdus(TPF):
        if name.upper() != "TARGETTABLES":
            continue
        fh = open(TPF, "rb")
        rows, cols = read_table(fh, cards, doff)
        fh.close()
        d = {c[0]: c for c in cols}
        tt = {"rows": rows, "d": d, "cards": cards}
        break

    if tt is None:
        print("ERROR: no TARGETTABLES")
        return 1

    d = tt["d"]
    out["targettables"] = {
        "columns": sorted(d.keys()),
        "nrows": tt["rows"],
        "tdim_raw_cnts": tdim_of(tt["cards"], "RAW_CNTS"),
        "tdim_flux": tdim_of(tt["cards"], "FLUX"),
    }

    raw = d["RAW_CNTS"][1]
    flux = d["FLUX"][1] if "FLUX" in d else None
    pc1 = d["POS_CORR1"][1] if "POS_CORR1" in d else None
    pc2 = d["POS_CORR2"][1] if "POS_CORR2" in d else None
    qual = d["QUALITY"][1] if "QUALITY" in d else None
    times = d["TIME"][1] if "TIME" in d else None
    cadno = d["CADENCENO"][1] if "CADENCENO" in d else None

    # ---- 4. pick a bright, good cadence ---------------------------------
    best = None
    bestf = -1e30
    for i in range(min(len(raw), len(flux) if flux else len(raw))):
        if qual is not None and qual[i] != 0:
            continue
        f = flux[i] if flux else None
        if f is None:
            continue
        s = sum(v for v in f if v is not None and v > 0)
        if s > bestf:
            bestf = s
            best = i
    out["probe_cadence_index"] = best
    out["probe_cadence_no"] = cadno[best] if cadno else None
    out["probe_time"] = times[best] if times else None

    ap = aperture["values"]
    # The aperture grid is 6 wide (NAXIS1) by 5 tall (NAXIS2), stored
    # row-major: index = row * NAXIS1 + col.
    ap_ncol = n1
    ap_nrow = n2
    target_mask = [1 if ap[i] == 1 else 0 for i in range(len(ap))]

    out["aperture"]["target_pixel_count_value1"] = sum(target_mask)
    out["aperture"]["value1_indices_rowmajor"] = [
        i for i in range(len(ap)) if ap[i] == 1]
    out["aperture"]["distinct_value_counts"] = {
        str(v): sum(1 for x in ap if x == v) for v in sorted(set(ap))}

    # ---- 5. orientation test --------------------------------------------
    # The aperture mask and the raw counts are two views of the SAME 30
    # physical pixels, so they share one index ordering. The question the
    # test asks is how to arrange that index sequence in 2-D.
    #
    #   Layout A: 6 wide x 5 tall  (row = idx // 6, col = idx % 6)
    #   Layout B: 5 wide x 6 tall  (row = idx // 5, col = idx % 5)
    #
    # Two independent facts argue for A: the APERTURE image extension has
    # NAXIS1 = 6, NAXIS2 = 5 and image data is stored with NAXIS1
    # fastest, and TDIM4 = '(6,5)' names 6 as the fastest-varying axis.
    # The tests below check that empirically rather than assuming it.
    results = {}
    if flux is not None and best is not None:
        fvals = flux[best]
        # Layout-independent alignment check: does the flux peak land on a
        # pixel the aperture mask calls target (value == 1)?
        peak = max(range(len(fvals)),
                   key=lambda i: (fvals[i] if fvals[i] is not None else -1e30))
        results["alignment"] = {
            "peak_index": peak,
            "peak_value": fvals[peak],
            "aperture_value_at_peak": ap[peak],
            "peak_on_aperture_value1": bool(target_mask[peak]),
            "n_aperture_value1": sum(target_mask),
            "note": "layout-independent: it tests that the aperture "
                    "sequence and the flux sequence share one index order",
        }
        for label, ncol, nrow in (("A_6wide_5tall", ap_ncol, ap_nrow),
                                  ("B_5wide_6tall", ap_nrow, ap_ncol)):
            if ncol * nrow != len(fvals):
                results[label] = {"error": "shape mismatch %dx%d vs %d"
                                   % (ncol, nrow, len(fvals))}
                continue
            # the same per-pixel attributes, arranged in this layout
            mask = target_mask
            pr = peak // ncol
            pc = peak % ncol
            cx, cy, tot = flux_centroid(fvals, ncol, nrow)
            results[label] = {
                "ncol": ncol, "nrow": nrow,
                "peak_row": pr, "peak_col": pc,
                "peak_value": fvals[peak],
                "centroid_x": cx, "centroid_y": cy,
                "blob_smoothness": blob_smoothness(fvals, ncol, nrow, mask),
                "n_mask_target": sum(mask),
            }
        # positional-correction correlation for each layout
        if pc1 is not None and pc2 is not None:
            for label, ncol, nrow in (("A_6wide_5tall", ap_ncol, ap_nrow),
                                      ("B_5wide_6tall", ap_nrow, ap_ncol)):
                xs, ys, p1, p2 = [], [], [], []
                step = max(1, len(raw) // 900)
                for i in range(0, len(raw), step):
                    if qual is not None and qual[i] != 0:
                        continue
                    f = flux[i] if flux else None
                    if f is None or len(f) != ncol * nrow:
                        continue
                    if pc1[i] is None or pc2[i] is None:
                        continue
                    cx, cy, tot = flux_centroid(f, ncol, nrow)
                    if tot <= 0:
                        continue
                    xs.append(cx); ys.append(cy)
                    p1.append(pc1[i]); p2.append(pc2[i])

                def corr(a, b):
                    n = len(a)
                    if n < 10:
                        return None
                    ma = sum(a) / n
                    mb = sum(b) / n
                    sa = math.sqrt(sum((v - ma) ** 2 for v in a))
                    sb = math.sqrt(sum((v - mb) ** 2 for v in b))
                    if sa == 0 or sb == 0:
                        return None
                    return sum((a[i] - ma) * (b[i] - mb) for i in range(n)) / (sa * sb)

                results[label]["corr_cx_poscorr1"] = corr(xs, p1)
                results[label]["corr_cy_poscorr2"] = corr(ys, p2)
                results[label]["corr_cx_poscorr2"] = corr(xs, p2)
                results[label]["corr_cy_poscorr1"] = corr(ys, p1)
                results[label]["n_cadences_corr"] = len(xs)

    out["orientation_test"] = results

    dst = os.path.join(ROOT, "data", "bnty0269", "kic9101271",
                       "stamp_geometry.json")
    with open(dst, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")

    print(json.dumps({k: out[k] for k in
                      ("hdus", "aperture", "targettables",
                       "probe_cadence_index", "orientation_test")},
                     indent=1, sort_keys=True))
    print("\nwrote %s" % dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
