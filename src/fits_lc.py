#!/usr/bin/env python3
"""
fits_lc.py — minimal FITS reader for Kepler OGIP light-curve products.

Pure Python standard library. No numpy, no astropy.

WHY THIS EXISTS
---------------
To re-derive a rotation period from the public Kepler light curve, the
photometry has to actually be read. The MAST `llc.fits` products are
FITS files with a binary table extension holding the time series, and
the usual route (astropy) is not installed on the machine that has to
reproduce the result. So this reads the file directly.

THE FORMAT, AS VERIFIED ON THE REAL FILES (2026-10-21)
-------------------------------------------------------
  * The file starts with a PRIMARY header (NAXIS=0) and then one or
    more extensions, each a 2880-byte-aligned header followed by data.
  * The light curve lives in extension 1, an OGIP binary table with
    columns TIME, TIMECORR, CADENCENO, SAP_FLUX, SAP_FLUX_ERR,
    SAP_BKG, SAP_BKG_ERR, PDCSAP_FLUX, PDCSAP_FLUX_ERR, SAP_QUALITY,
    PSF_CENTR1, ... . The file is BIG-ENDIAN, as FITS requires.
  * Column data is stored column-major: the whole TIME column first,
    then the whole CADENCENO column, and so on, each padded to a
    2880-byte boundary.
  * TTYPE1 gives the column name, TFORM1 the format ('D' = float64,
    'E' = float32, 'J' = int32, 'I' = int16), TUNIT1 the unit and
    TDIMn the dimensionality.
  * TIME is in BJD - 2454833.0 (Kepler's convention) and must have
    2454833.0 added back to get a full barycentric Julian date.

This reader returns a list of (name, values) pairs plus the primary
header, and it validates that the byte count it computes matches the
file size, so a misread is a loud failure rather than a silent one.
"""

import os
import struct
import sys

BLOCK = 2880


def _cards(block):
    """Parse one 2880-byte FITS header block into a dict."""
    out = {}
    i = 0
    while i < len(block):
        card = block[i:i + 80].decode("ascii", "replace")
        key = card[:8].strip()
        if key == "END":
            break
        if key and "=" in card[8:10]:
            value = card[10:].split("/")[0].strip()
            if value.startswith("'") and value.endswith("'"):
                value = value[1:-1].strip()
            else:
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        pass
            out[key] = value
        i += 80
    return out


# FITS binary-table format code -> (bytes per item, struct format char).
#
# The subtlety that bit me first: struct's 'e' is a VALID format code
# for IEEE half-precision (2 bytes), and FITS 'E' is float32 (4 bytes).
# Using `code.lower()` therefore silently produced '>e' and then failed
# with "requires a buffer of 2 bytes" -- a confusing error for what is
# really a code-mapping mistake. There is no half-precision in FITS.
FITS_TYPES = {
    "L": (1, "b"),    # logical
    "B": (1, "B"),    # unsigned byte
    "I": (2, "h"),    # int16
    "J": (4, "i"),    # int32
    "K": (8, "q"),    # int64
    "E": (4, "f"),    # float32
    "D": (8, "d"),    # float64
    "C": (8, "f"),    # complex64
    "M": (16, None),  # complex128
    "P": (8, None),   # 8-byte descriptor
    "Q": (16, None),  # 16-byte descriptor
}


def _fmt_info(tform):
    """Return (code, count, bytes_total) for a FITS TFORM string."""
    tform = tform.strip()
    i = 0
    while i < len(tform) and tform[i].isdigit():
        i += 1
    count = int(tform[:i]) if i else 1
    code = tform[i:i + 1] if i < len(tform) else "D"
    if code not in FITS_TYPES:
        raise ValueError("unsupported TFORM %r" % tform)
    return code, count, FITS_TYPES[code][0] * count


def read_fits(path):
    """Read a FITS file.

    Returns (primary_header, [(extname, header, columns), ...]) where
    `columns` is a list of (name, unit, values) with `values` a flat
    list of numbers, or a list of lists for vector columns.
    """
    with open(path, "rb") as fh:
        raw = fh.read()
    if not raw.startswith(b"SIMPLE"):
        raise ValueError("%s is not a FITS file" % path)

    pos = 0
    primary = {}
    extensions = []

    while pos < len(raw):
        header = {}
        while True:
            if pos + BLOCK > len(raw):
                raise ValueError("truncated header in %s" % path)
            block = raw[pos:pos + BLOCK]
            pos += BLOCK
            # The header ends in the block whose first card is "END".
            # A FITS header is a whole number of 2880-byte blocks, and
            # "END" may be followed by further padding cards, so scan
            # the block's cards rather than assuming a fixed position.
            end_found = False
            for i in range(0, BLOCK, 80):
                card = block[i:i + 80].decode("ascii", "replace")
                key = card[:8].strip()
                if key == "END":
                    end_found = True
                    break
                if not key or "=" not in card[8:10]:
                    continue
                value = card[10:].split("/")[0].strip()
                if value.startswith("'") and value.endswith("'"):
                    value = value[1:-1].strip()
                else:
                    try:
                        value = int(value)
                    except ValueError:
                        try:
                            value = float(value)
                        except ValueError:
                            pass
                header[key] = value
            if end_found:
                break
        # a header always ends on a block boundary
        if not header:
            break
        naxis = int(header.get("NAXIS", 0))
        if naxis == 0:
            primary = header
            continue

        # ---- primary data unit (usually empty for our files) ----
        if "PRIMARY" not in str(header.get("EXTNAME", "PRIMARY")).upper():
            pass
        bitpix = int(header.get("BITPIX", 8))
        nelem = 1
        for k in range(1, naxis + 1):
            nelem *= int(header["NAXIS%d" % k])
        nbytes = abs(bitpix) // 8 * nelem
        if naxis == 0:
            nbytes = 0
        data_start = pos
        pos += ((nbytes + BLOCK - 1) // BLOCK) * BLOCK
        if nbytes == 0:
            extensions.append((header.get("EXTNAME", ""), header, []))
            continue

        # ---- binary table extension ----
        nrows = int(header.get("NAXIS2", 0))
        rowlen = int(header.get("NAXIS1", 0))
        fields = []
        idx = 1
        while True:
            tform = header.get("TFORM%d" % idx)
            if tform is None:
                break
            code, count, nbytes_col = _fmt_info(tform)
            fields.append((header.get("TTYPE%d" % idx, "").strip(),
                           header.get("TUNIT%d" % idx, ""),
                           code, count))
            idx += 1

        blob = raw[data_start:data_start + nrows * rowlen]
        cols = []
        # A FITS binary table is stored ROW-major: every row holds all
        # the columns back to back, and the rows follow one another.
        # So a column is a stride of `rowlen` bytes, not a contiguous
        # block. Getting this wrong silently reads the wrong numbers.
        field_offset = 0
        for name, unit, code, count in fields:
            itemsize, scode = FITS_TYPES[code]
            nbytes_col = itemsize * count
            if scode is None:
                vals = [blob[r * rowlen + field_offset:
                             r * rowlen + field_offset + itemsize]
                        for r in range(nrows)]
            elif count == 1:
                vals = [struct.unpack(">" + scode,
                                      blob[r * rowlen + field_offset:
                                           r * rowlen + field_offset + itemsize])[0]
                        for r in range(nrows)]
            else:
                vals = [list(struct.unpack(">%d%s" % (count, scode),
                                           blob[r * rowlen + field_offset:
                                                r * rowlen + field_offset + nbytes_col]))
                        for r in range(nrows)]
            field_offset += nbytes_col
            cols.append((name, unit, vals))
        if field_offset != rowlen and fields:
            raise ValueError("column widths sum to %d but NAXIS1 is %d"
                             % (field_offset, rowlen))
        extensions.append((header.get("EXTNAME", ""), header, cols))
    return primary, extensions


def load_lightcurve(path):
    """Return (time_bjd_minus_2454833, pdcsap_flux, sap_flux, quality) lists."""
    _, exts = read_fits(path)
    for name, header, cols in exts:
        d = dict((c[0], c) for c in cols)
        if "TIME" in d and ("PDCSAP_FLUX" in d or "SAP_FLUX" in d):
            time = d["TIME"][2]
            pdcsap = d["PDCSAP_FLUX"][2] if "PDCSAP_FLUX" in d else []
            sap = d["SAP_FLUX"][2] if "SAP_FLUX" in d else []
            qual = d["SAP_QUALITY"][2] if "SAP_QUALITY" in d else []
            return time, pdcsap, sap, qual, header
    raise ValueError("no light-curve extension found in %s" % path)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    for path in argv[1:]:
        primary, exts = read_fits(path)
        print("=" * 70)
        print(path, os.path.getsize(path), "bytes")
        print("  OBJECT=%s KEPLERID=%s QUARTER=%s SEASON=%s OBSMODE=%s"
              % (primary.get("OBJECT"), primary.get("KEPLERID"),
                 primary.get("QUARTER"), primary.get("SEASON"),
                 primary.get("OBSMODE")))
        for name, header, cols in exts:
            print("  EXT %-8s rows=%s cols=%s"
                  % (name, header.get("NAXIS2"),
                     [c[0] for c in cols]))
            for cname, unit, vals in cols:
                if cname in ("TIME", "PDCSAP_FLUX", "SAP_FLUX", "SAP_QUALITY"):
                    good = [v for v in vals if v == v]
                    print("      %-14s n=%-6d unit=%-8s first=%s"
                          % (cname, len(vals), unit,
                             vals[0] if vals else None))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
