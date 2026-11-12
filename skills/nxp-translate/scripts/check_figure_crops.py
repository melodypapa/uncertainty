#!/usr/bin/env python3
"""Inspect cropped figure/diagram images for crop defects.

Every crop must contain *only the figure*: no page header/footer, no body text,
no caption, and no large blank band. A crop whose rectangle ran to the page
bottom silently ships the running footer (copyright + revision) under the
diagram — invisible unless you open the PNG, and a whole corpus can carry it
(the S32K5 RM had 54 such diagrams).

Two classes of finding:

  HARD (exit 1)      BLANK       (almost) no ink at all
                     LEAD_WS     leading blank margin > 22% of the height
                     TRAIL_WS    trailing blank margin > 22% of the height
  ADVISORY (review)  REVIEW_EDGE a thin content band at the very top/bottom
                                 edge, separated from the figure by a blank
                                 gap — *may* be the page header/footer. A
                                 bit-field bar's own `Bits`/`Reset` rows have
                                 the same geometry, so this is a pointer to
                                 open and confirm, not an automatic verdict.
                                 `--strict` turns it into a failure.

The whitespace checks are reliable; the edge check is deliberately advisory
because no OCR-free row profile can separate a bar's own rows from page chrome.

Usage:
  check_figure_crops.py <path>... [--strict] [--json]

  <path> may be an article directory, a corpus root, or individual image files.
Exit codes: 0 clean / advisory-only, 1 hard defects (or advisory under
--strict), 2 usage.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image
    import numpy as np
except ImportError:  # pragma: no cover
    print("error: Pillow + numpy are required (pip install pillow numpy)", file=sys.stderr)
    sys.exit(2)

IMG_EXT = (".png", ".jpg", ".jpeg")
SCAN_W = 400        # downscale width for the row-ink profile
INK_THR = 0.014     # a row is "content" when this fraction of pixels is dark
EDGE_NEAR = 0.06    # content within this fraction of an edge "touches" it
BAND_MAX = 0.15     # a chrome-like edge band is at most this fraction of h
GAP_MIN = 0.06      # ... and is separated by a gap of at least this fraction
WS_MAX = 0.22       # leading/trailing blank above this fraction is untrimmed
BLANK_INK = 0.002

HARD = ("BLANK", "LEAD_WS", "TRAIL_WS")
ADVISORY = ("REVIEW_EDGE(bottom)", "REVIEW_EDGE(top)")


def _profile(path):
    im = Image.open(path).convert("L")
    w, h = im.size
    if w == 0 or h == 0:
        return None
    im2 = im.resize((SCAN_W, max(1, int(SCAN_W * h / w))))
    ink = (np.asarray(im2, dtype=np.uint8) < 200).mean(axis=1)
    return w, h, ink


def _blank_runs(ink, thr=INK_THR):
    runs, s = [], None
    for i, v in enumerate(ink):
        if v < thr and s is None:
            s = i
        elif v >= thr and s is not None:
            runs.append((s, i)); s = None
    if s is not None:
        runs.append((s, len(ink)))
    return runs


def analyse(path):
    p = _profile(path)
    if p is None:
        return {"file": str(path), "flags": ["UNREADABLE"], "size": [0, 0]}
    w, h, ink = p
    H = len(ink)
    px = h / H
    flags, metrics = [], {}

    if float(ink.mean()) < BLANK_INK:
        return {"file": str(path), "flags": ["BLANK"], "size": [w, h], "metrics": metrics}
    idx = np.where(ink >= INK_THR)[0]
    if not len(idx):
        return {"file": str(path), "flags": ["BLANK"], "size": [w, h], "metrics": metrics}
    first, last = int(idx[0]), int(idx[-1])
    blank = _blank_runs(ink)

    # bottom edge band (possible page footer)
    if last >= H - 1 - max(2, int(EDGE_NEAR * H)):
        cands = [(a, b) for a, b in blank
                 if a > 0.40 * H and b <= last + 1
                 and (last - b) * px <= BAND_MAX * h
                 and (b - a) * px >= GAP_MIN * h]
        if cands:
            a, b = max(cands, key=lambda r: r[1] - r[0])
            flags.append("REVIEW_EDGE(bottom)")
            metrics["bottom_band_px"] = round((last - b) * px)
            metrics["bottom_gap_px"] = round((b - a) * px)

    # top edge band (possible running header)
    if first <= max(2, int(EDGE_NEAR * H)):
        cands = [(a, b) for a, b in blank
                 if b < 0.60 * H and a >= first - 1
                 and (a - first) * px <= BAND_MAX * h
                 and (b - a) * px >= GAP_MIN * h]
        if cands:
            a, b = max(cands, key=lambda r: r[1] - r[0])
            flags.append("REVIEW_EDGE(top)")
            metrics["top_band_px"] = round((a - first) * px)
            metrics["top_gap_px"] = round((b - a) * px)

    if not flags:
        lead, trail = first * px, (H - 1 - last) * px
        metrics["lead_blank_px"], metrics["trail_blank_px"] = round(lead), round(trail)
        if lead > WS_MAX * h:
            flags.append("LEAD_WS")
        if trail > WS_MAX * h:
            flags.append("TRAIL_WS")

    return {"file": str(path), "flags": flags, "size": [w, h], "metrics": metrics}


def collect(paths):
    files = []
    for p in paths:
        p = Path(p)
        if p.is_dir():
            files += [q for q in sorted(p.rglob("*")) if q.suffix.lower() in IMG_EXT]
        elif p.suffix.lower() in IMG_EXT:
            files.append(p)
    return files


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", help="article dirs / corpus root / image files")
    ap.add_argument("--strict", action="store_true",
                    help="fail on advisory REVIEW_EDGE findings too")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args(argv)

    files = collect(args.paths)
    if not files:
        print("no images found", file=sys.stderr)
        return 2

    results = [analyse(f) for f in files]
    hard = [r for r in results if any(f in HARD for f in r["flags"])]
    review = [r for r in results if any(f in ADVISORY for f in r["flags"])]

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for r in results:
            if not r["flags"]:
                continue
            mt = " ".join(f"{k}={v}" for k, v in r.get("metrics", {}).items())
            kind = "HARD" if any(f in HARD for f in r["flags"]) else "review"
            print(f"  [{kind}] {'/'.join(r['flags']):26s} {r['size'][0]}x{r['size'][1]}  "
                  f"{r['file']}  {mt}")
        print(f"\nchecked {len(results)} image(s): {len(hard)} hard defect(s), "
              f"{len(review)} edge-review candidate(s)")

    if hard:
        return 1
    if args.strict and review:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
