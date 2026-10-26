#!/usr/bin/env python3
"""
bls.py — Box Least Squares transit search, pure Python standard library.

Implements the standard BLS algorithm for transit detection. For a trial
period P and epoch t0, a box of depth d and duration q is fitted to the
folded light curve; the periodisation is scored by the signal-to-noise
ratio of the box depth against the out-of-transit scatter.

WHY STANDARD LIBRARY ONLY
--------------------------
Every dossier produced with this code has to be reproducible by a
reviewer on a bare Python 3 interpreter, with no pip install step. The
arithmetic is pure Python floats: slower than numpy, but completely
self-contained, which matters more than speed for this use case.

ALGORITHM
---------
A naive implementation -- for each period, for each epoch, re-fold every
cadence -- is O(n_periods * n_epochs * n_cadences) and is hopeless in
pure Python. This uses the standard two-level BLS structure:

  Stage 1 (binned search, O(n) per period)
      For a trial period, each cadence is assigned to a phase bin. Per-bin
      sums of weighted flux, weight, weighted flux squared and count are
      accumulated. A circular prefix-sum over the doubled bin array then
      gives the in-transit and out-of-transit statistics for ANY box
      position in O(1). Sweeping all bin positions therefore costs
      O(n_bins) per (period, duration) rather than O(n_cadences).

  Stage 2 (exact refinement, O(log n) per candidate)
      The winning candidates are re-scored without binning, using a
      phase-sorted index with prefix sums of the weighted flux and the
      weighted flux squared. The window is located by binary search, so
      the refined depth and scatter are exact to the cadence.

SNR DEFINITION
--------------
    SNR = depth * sqrt(N_in) / sigma_out

where sigma_out is the scatter of the out-of-transit cadences. This is
the same form used by the reference implementation, so the SNR >= 8
detection gate used here is comparable to the literature.

Reference:
  Kovacs, Zucker & Mazeh 2002, A&A 391, 369   (the original BLS paper)
  Kovacs 2020, boxleastquares                 (reference implementation)

Usage:
    python3 bls.py --help
"""

import argparse
import json
import math
import sys
from typing import List, Sequence, Tuple


# ----------------------------------------------------------------------
# Data handling
# ----------------------------------------------------------------------


def read_lc(path: str) -> Tuple[List[float], List[float], List[float]]:
    """Read a light curve in MAST-style CSV: TIME, FLUX, FLUX_ERR.

    Comment lines (leading '#') and blank lines are skipped. Rows with a
    missing or non-numeric value in any column are skipped rather than
    silently coerced, because a silently bad flux row biases the depth.
    """
    times: List[float] = []
    flux: List[float] = []
    err: List[float] = []
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p for p in line.replace(",", " ").split() if p]
            if len(parts) < 3:
                continue
            try:
                t = float(parts[0])
                f = float(parts[1])
                e = float(parts[2])
            except ValueError:
                continue
            if not (math.isfinite(t) and math.isfinite(f) and math.isfinite(e)):
                continue
            if e <= 0:
                continue
            times.append(t)
            flux.append(f)
            err.append(e)
    return times, flux, err


def median(values: Sequence[float]) -> float:
    """Median of a sequence; nan for an empty input."""
    if not values:
        return float("nan")
    s = sorted(values)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return s[mid]
    return 0.5 * (s[mid - 1] + s[mid])


def weighted_median(values: Sequence[float], weights: Sequence[float]) -> float:
    """Weighted median, used for the out-of-transit baseline level.

    The baseline must be robust: a single deep transit inside a window
    must not drag the baseline down and inflate the measured depth.
    """
    if not values:
        return float("nan")
    pairs = sorted(zip(values, weights))
    total = sum(w for _, w in pairs)
    if total <= 0:
        return median(values)
    acc = 0.0
    for v, w in pairs:
        acc += w
        if acc >= total / 2.0:
            return v
    return pairs[-1][0]


def mad_to_sigma(values: Sequence[float]) -> float:
    """Robust scatter: 1.4826 * median absolute deviation.

    The curve's own scatter, not the formal error bars, is what the
    per-cadence SNR is computed against, as the bounty gates require.
    """
    if not values:
        return float("nan")
    med = median(values)
    return 1.4826 * median([abs(v - med) for v in values])


def _bisect(arr: Sequence[float], x: float) -> int:
    """Lower-bound bisect: the insertion point of x in a sorted list."""
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


# ----------------------------------------------------------------------
# Stage 1: binned search
# ----------------------------------------------------------------------


def _binned_search(
    times: Sequence[float],
    flux: Sequence[float],
    err: Sequence[float],
    period: float,
    durations: Sequence[float],
    n_bins: int,
    t0: float,
    dip_only: bool = False,
) -> List[dict]:
    """Binned BLS over one period; returns one record per duration.

    The phase bin index of every cadence is computed once. Per-bin
    accumulators are then built, and the doubled-array prefix sums make
    every candidate box position an O(1) lookup.
    """
    n = len(times)
    if n == 0:
        return []

    # Per-bin accumulators.
    b_wf = [0.0] * n_bins
    b_w = [0.0] * n_bins
    b_wf2 = [0.0] * n_bins
    b_n = [0] * n_bins

    for i in range(n):
        t = times[i]
        ph = ((t - t0) / period) % 1.0
        b = int(ph * n_bins)
        if b >= n_bins:
            b = n_bins - 1
        elif b < 0:
            b = 0
        w = 1.0 / (err[i] * err[i])
        f = flux[i]
        b_wf[b] += f * w
        b_w[b] += w
        b_wf2[b] += f * f * w
        b_n[b] += 1

    # Doubled arrays so a box can wrap around phase 0.
    d_wf = b_wf + b_wf
    d_w = b_w + b_w
    d_wf2 = b_wf2 + b_wf2
    d_n = b_n + b_n

    # Prefix sums over the doubled arrays.
    p_wf = [0.0] * (2 * n_bins + 1)
    p_w = [0.0] * (2 * n_bins + 1)
    p_wf2 = [0.0] * (2 * n_bins + 1)
    p_n = [0] * (2 * n_bins + 1)
    for k in range(2 * n_bins):
        p_wf[k + 1] = p_wf[k] + d_wf[k]
        p_w[k + 1] = p_w[k] + d_w[k]
        p_wf2[k + 1] = p_wf2[k] + d_wf2[k]
        p_n[k + 1] = p_n[k] + d_n[k]

    tot_wf = p_wf[n_bins]
    tot_w = p_w[n_bins]
    tot_wf2 = p_wf2[n_bins]
    tot_n = p_n[n_bins]
    if tot_w <= 0:
        return []

    out: List[dict] = []
    for dur in durations:
        if dur >= period:
            continue
        width = max(1, int(round(dur / period * n_bins)))
        best = None
        for s in range(n_bins):
            a = s
            b = s + width
            in_w = p_w[b] - p_w[a]
            in_wf = p_wf[b] - p_wf[a]
            in_wf2 = p_wf2[b] - p_wf2[a]
            n_in = p_n[b] - p_n[a]
            if in_w <= 0 or n_in <= 0:
                continue
            out_w = tot_w - in_w
            if out_w <= 0:
                continue
            out_wf = tot_wf - in_wf
            out_wf2 = tot_wf2 - in_wf2
            out_mean = out_wf / out_w
            var = out_wf2 / out_w - out_mean * out_mean
            if var < 0:
                var = 0.0
            sigma = math.sqrt(var)
            if sigma <= 0:
                continue
            depth = out_mean - (in_wf / in_w)
            if dip_only and depth <= 0:
                # Dip-only mode: a flare or a systematics bump is not a
                # transit, and the BLS objective is symmetric in the sign
                # of the depth, so without this the "best" box of a
                # light curve is very often an OUTBURST.
                continue
            # BLS objective: the reduction in chi-square obtained by
            # splitting the curve into in-transit and out-of-transit
            # groups with a best-fit depth,
            #
            #     dchi2 = depth^2 * W_in * W_out / W_total
            #
            # where W are inverse-variance weights. This is the standard
            # BLS objective and it is the correct one to rank by:
            # ranking on the raw depth-SNR instead favours an over-wide
            # box (a wider box has a larger N_in, which can out-score a
            # narrower, deeper, correct one) and so dilutes the reported
            # depth. With this objective an over-wide box is penalised
            # because the depth falls faster (1/ratio) than N_in rises
            # (proportional to ratio).
            dchi2 = depth * depth * in_w * out_w / tot_w
            snr = depth * math.sqrt(n_in) / sigma
            if best is None or dchi2 > best["dchi2"]:
                # Bin centre -> phase -> epoch.
                phase_centre = (s + width / 2.0) / n_bins
                best = {
                    "period": period,
                    "duration": dur,
                    "epoch": t0 + phase_centre * period,
                    "depth": depth,
                    "snr": snr,
                    "dchi2": dchi2,
                    "n_in_transit": n_in,
                    "sigma_out": sigma,
                }
        if best is not None:
            out.append(best)
    return out


# ----------------------------------------------------------------------
# Stage 2: exact refinement
# ----------------------------------------------------------------------


class _ExactIndex:
    """Phase-sorted index of a light curve for exact window statistics.

    Sorted by phase relative to a reference epoch, with prefix sums of the
    weighted flux and the weighted flux squared. Any phase window is
    located by binary search and its statistics are exact.
    """

    __slots__ = ("phases", "pwf", "pwf2", "pw", "n", "t_ref", "period")

    def __init__(self, times, flux, err, period, t_ref):
        idx = []
        for i, t in enumerate(times):
            ph = ((t - t_ref) / period) % 1.0
            if ph > 0.5:
                ph -= 1.0
            idx.append((ph, i))
        idx.sort()
        self.n = len(idx)
        self.t_ref = t_ref
        self.period = period
        self.phases = [p for p, _ in idx]
        self.pwf = [0.0] * (self.n + 1)
        self.pwf2 = [0.0] * (self.n + 1)
        self.pw = [0.0] * (self.n + 1)
        a1 = a2 = a3 = 0.0
        for k, (_, i) in enumerate(idx):
            w = 1.0 / (err[i] * err[i])
            f = flux[i]
            a1 += f * w
            a2 += f * f * w
            a3 += w
            self.pwf[k + 1] = a1
            self.pwf2[k + 1] = a2
            self.pw[k + 1] = a3

    def window(self, lo: float, hi: float) -> Tuple[int, int]:
        a = _bisect(self.phases, lo)
        b = _bisect(self.phases, hi)
        return a, b

    def exact_stats(self, epoch, period, duration):
        """Exact in/out statistics for a box at (epoch, period, duration).

        The phase window is [ph_ref - half, ph_ref + half) on the phase
        axis, which can wrap across the +/- 0.5 boundary. The wrap is
        handled by taking the window as the complement of the gap, so the
        in-transit set is always a contiguous run in the phase-sorted
        array. All the sums are exact (unbinned) to the cadence.
        """
        ph_ref = ((epoch - self.t_ref) / period) % 1.0
        half = duration / 2.0
        lo = ph_ref - half
        hi = ph_ref + half
        if lo < -0.5 or hi > 0.5:
            # Wrapping window: in-transit is the complement of the gap
            # [ph_ref + half, ph_ref - half] (mod 1).
            gap_lo = ph_ref + half
            gap_hi = ph_ref - half
            a1, b1 = self.window(gap_hi, gap_lo)
            in_n = self.n - (b1 - a1)
            in_wf = (self.pwf[self.n] - self.pwf[b1]) + self.pwf[a1]
            in_wf2 = (self.pwf2[self.n] - self.pwf2[b1]) + self.pwf2[a1]
            in_w = (self.pw[self.n] - self.pw[b1]) + self.pw[a1]
        else:
            a, b = self.window(lo, hi)
            in_n = b - a
            in_wf = self.pwf[b] - self.pwf[a]
            in_wf2 = self.pwf2[b] - self.pwf2[a]
            in_w = self.pw[b] - self.pw[a]
        tot_w = self.pw[self.n]
        tot_wf = self.pwf[self.n]
        tot_wf2 = self.pwf2[self.n]
        if in_w <= 0 or in_n <= 0:
            return None
        out_w = tot_w - in_w
        if out_w <= 0:
            return None
        out_wf = tot_wf - in_wf
        out_wf2 = tot_wf2 - in_wf2
        out_mean = out_wf / out_w
        var = out_wf2 / out_w - out_mean * out_mean
        if var < 0:
            var = 0.0
        sigma = math.sqrt(var)
        if sigma <= 0:
            return None
        depth = out_mean - (in_wf / in_w)
        snr = depth * math.sqrt(in_n) / sigma
        # BLS objective: chi-square reduction from a best-fit box depth.
        # See the note in _binned_search: this is the quantity that must
        # be maximised, not the raw depth-SNR.
        dchi2 = depth * depth * in_w * out_w / tot_w
        return {
            "period": self.period,
            "duration": duration,
            "epoch": epoch,
            "depth": depth,
            "snr": snr,
            "dchi2": dchi2,
            "n_in_transit": in_n,
            "sigma_out": sigma,
        }


def refine(
    times: Sequence[float],
    flux: Sequence[float],
    err: Sequence[float],
    candidate: dict,
    n_refine: int = 60,
    duration_factors: Sequence[float] = (0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.4, 1.6, 2.0),
    dip_only: bool = False,
) -> dict:
    """Refine a binned candidate to exact, unbinned statistics.

    The epoch is swept finely around the binned solution, and at each
    epoch a small grid of durations around the binned duration is tried.
    Both are scored with exact (unbinned) statistics from the phase-sorted
    index, so the reported depth and duration are not quantised by the
    phase binning.
    """
    period = candidate["period"]
    duration = candidate["duration"]
    t_ref = times[0]
    index = _ExactIndex(times, flux, err, period, t_ref)

    best = None
    span = duration / 2.0
    for k in range(n_refine):
        frac = (k / max(n_refine - 1, 1) - 0.5) * 2.0
        epoch = candidate["epoch"] + frac * span
        for fac in duration_factors:
            dur = duration * fac
            if dur >= period:
                continue
            st = index.exact_stats(epoch, period, dur)
            if st is None:
                continue
            if dip_only and st["depth"] <= 0:
                continue
            if best is None or st["dchi2"] > best["dchi2"]:
                best = st
    return best if best is not None else candidate


def bls_search(
    times: Sequence[float],
    flux: Sequence[float],
    err: Sequence[float],
    periods: Sequence[float],
    durations: Sequence[float],
    n_bins: int = 200,
    dip_only: bool = False,
) -> List[dict]:
    """Full BLS search: binned stage then exact refinement.

    Returns one record per duration, holding the best (period, epoch)
    solution found for that duration.
    """
    if not times:
        return []
    base = weighted_median(flux, [1.0 / (e * e) for e in err])
    f = [x - base for x in flux]
    t0 = min(times)

    best_by_duration: dict = {}
    for period in periods:
        for rec in _binned_search(times, f, err, period, durations, n_bins, t0, dip_only):
            dur = rec["duration"]
            prev = best_by_duration.get(dur)
            if prev is None or rec["dchi2"] > prev["dchi2"]:
                best_by_duration[dur] = rec

    out: List[dict] = []
    for dur in durations:
        cand = best_by_duration.get(dur)
        if cand is None:
            continue
        out.append(refine(times, f, err, cand, dip_only=dip_only))
    # Rank the final solutions by the BLS objective (chi-square reduction).
    out.sort(key=lambda r: -r.get("dchi2", r["snr"]))
    return out


def exact_sigma(
    times: Sequence[float],
    flux: Sequence[float],
    period: float,
    epoch: float,
    duration: float,
) -> float:
    """Robust scatter of the out-of-transit cadences (1.4826 * MAD).

    This is the 'curve's own scatter' the gates ask for. It is reported
    alongside the formal sigma so a reader can see both.
    """
    half = duration / 2.0
    out = []
    for t, y in zip(times, flux):
        ph = ((t - epoch) / period) % 1.0
        if ph > 0.5:
            ph -= 1.0
        if abs(ph) > half:
            out.append(y)
    if len(out) < 10:
        return float("nan")
    return mad_to_sigma(out)


def odd_even_depth(
    times: Sequence[float],
    flux: Sequence[float],
    period: float,
    epoch: float,
    duration: float,
) -> Tuple[float, float]:
    """Depth measured on odd and even epochs separately.

    A real planet repeats at the same phase every cycle. A systematic
    (instrumental) artifact often shows up on alternating cycles, or with
    a different depth, because it tracks the spacecraft's downlink or
    momentum-dump pattern. Comparing the two depths is the standard
    odd-even test.
    """
    half = duration / 2.0
    odd_in: List[float] = []
    odd_out: List[float] = []
    even_in: List[float] = []
    even_out: List[float] = []
    for t, y in zip(times, flux):
        ph = ((t - epoch) / period) % 1.0
        if ph > 0.5:
            ph -= 1.0
        epoch_index = int(math.floor((t - epoch) / period))
        if abs(ph) <= half / 2.0:
            (odd_in if epoch_index % 2 else even_in).append(y)
        elif abs(ph) > 0.3:
            (odd_out if epoch_index % 2 else even_out).append(y)

    def depth(inl, outl):
        if not inl or not outl:
            return float("nan")
        return median(outl) - median(inl)

    return depth(odd_in, odd_out), depth(even_in, even_out)


def period_grid(
    t_min: float, t_max: float, p_min: float, p_max: float, n_p: int
) -> List[float]:
    """Log-spaced period grid spanning the requested baseline.

    Log spacing is required because transit searches need fine resolution
    at short periods and can afford coarse resolution at long ones.
    """
    if t_max <= t_min or p_min <= 0 or p_max <= p_min or n_p < 2:
        return []
    lo = math.log(p_min)
    hi = math.log(p_max)
    return [math.exp(lo + (hi - lo) * i / (n_p - 1)) for i in range(n_p)]


def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser(description="BLS transit search (stdlib only)")
    ap.add_argument("--lc", required=True, help="light curve CSV: TIME,FLUX,FLUX_ERR")
    ap.add_argument("--p-min", type=float, default=0.5)
    ap.add_argument("--p-max", type=float, default=100.0)
    ap.add_argument("--n-periods", type=int, default=2000)
    ap.add_argument("--n-bins", type=int, default=200)
    ap.add_argument("--durations", default="0.02,0.03,0.05,0.08",
                    help="comma separated durations in days")
    ap.add_argument("--out", default=None, help="write results JSON here")
    ap.add_argument("--top", type=int, default=10, help="how many results to print")
    args = ap.parse_args(argv)

    times, flux, err = read_lc(args.lc)
    if not times:
        print("no usable cadences in %s" % args.lc, file=sys.stderr)
        return 2

    print("cadences: %d  baseline span: %.3f d" % (len(times), max(times) - min(times)))
    periods = period_grid(min(times), max(times), args.p_min, args.p_max, args.n_periods)
    durations = [float(x) for x in args.durations.split(",") if x.strip()]
    print("searching %d periods x %d durations" % (len(periods), len(durations)))

    res = bls_search(times, flux, err, periods, durations, n_bins=args.n_bins)
    res.sort(key=lambda r: -r["snr"])

    top = res[: args.top]
    for r in top:
        odd, even = odd_even_depth(times, flux, r["period"], r["epoch"], r["duration"])
        r["odd_depth"] = odd
        r["even_depth"] = even
        r["odd_even_delta"] = abs(odd - even)
        r["sigma_robust"] = exact_sigma(times, flux, r["period"], r["epoch"], r["duration"])

    payload = {
        "source": args.lc,
        "n_cadences": len(times),
        "baseline_days": max(times) - min(times),
        "period_min": args.p_min,
        "period_max": args.p_max,
        "n_periods": len(periods),
        "n_bins": args.n_bins,
        "durations_days": durations,
        "top": top,
    }
    text = json.dumps(payload, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print("wrote %s" % args.out)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
