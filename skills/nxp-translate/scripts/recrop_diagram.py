#!/usr/bin/env python3
"""Crop an unnumbered register `Diagram` bit-field bar from an NXP PDF.

A register bar is not a numbered figure — it has a `Diagram` label above it and
a `Fields` label below it, no `Figure N.` caption. Cropping it the naive way
(union of the page's drawings, or "down to the page bottom") ships the page
footer under the bar, or cuts the bar when a page carries two of them.

This tool anchors on the register's numbered section heading and clips the
first `Diagram` block below it, then:

  * bottom = just above the following `Fields` label when it is on the same
    page;
  * otherwise (the Fields table starts on the next page) bottom = just below
    the last `Reset` row of the bar, never below the page content area — so a
    two-half bar keeps its lower `Reset` row and the page footer is excluded.

A page can carry more than one register bar; anchoring on the heading is what
picks the right one.

Usage:
  recrop_diagram.py <pdf> <out.png> --pages A B --heading REGEX [--zoom 3]
  recrop_diagram.py <pdf> <out.png> --pages A B --heading REGEX --list
  recrop_diagram.py <pdf> <out.png> --pages A B --manual X0 Y0 X1 Y1

  --pages   1-based inclusive page range of the chapter (from the chapter map)
  --heading substring/regex of the register's numbered heading, e.g. "Control \\(CTRL\\)"

Exit codes: 0 ok, 1 heading/bar not found, 2 usage.
"""

import argparse
import re
import sys

import pymupdf

CONTENT_TOP = 62.0
CONTENT_BOTTOM = 740.0   # typical NXP content band bottom; footer sits below
MARGIN_MIN = 6.0


def blocks(pg):
    return [(x0, y0, x1, y1, t.strip())
            for x0, y0, x1, y1, t, *_ in pg.get_text("blocks")]


def find_bar(doc, start, end, heading):
    sec = re.compile(r"^\d+\.\d+(?:\.\d+)*\s")
    hx = re.compile(heading)
    for p in range(start, end + 1):
        pg = doc[p - 1]
        blks = blocks(pg)
        hy = None
        for x0, y0, x1, y1, t in blks:
            if sec.match(t) and hx.search(t):
                hy = y0; break
        if hy is None:
            continue
        diagrams = [b for b in blks if re.match(r"^Diagram\b", b[4]) and b[1] > hy]
        if not diagrams:
            continue
        d = diagrams[0][1]
        fields = [b for b in blks if re.match(r"^Fields\b", b[4]) and b[1] > d]
        if fields:
            bottom = fields[0][1] - 15
            how = "Fields label"
        else:
            resets = [b[3] for b in blks if b[4].startswith("Reset") and b[1] > d]
            cap = min(pg.rect.height - 45, CONTENT_BOTTOM if pg.rect.height > 780 else pg.rect.height - 45)
            bottom = min(cap, (max(resets) + 8) if resets else cap)
            how = "last Reset row"
        x0 = max(40.0, 40.0)
        x1 = pg.rect.x1 - 37
        clip = pymupdf.Rect(x0, d + 18, x1, bottom)
        return pg, clip, (p, round(hy, 1), round(d, 1), how)
    return None, None, None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("out")
    ap.add_argument("--pages", nargs=2, type=int, metavar=("A", "B"), required=True)
    ap.add_argument("--heading", required=True,
                    help="regex/substring of the register's numbered heading")
    ap.add_argument("--zoom", type=float, default=3.0)
    ap.add_argument("--list", action="store_true", help="print the clip, do not render")
    ap.add_argument("--manual", nargs=4, type=float, metavar=("X0", "Y0", "X1", "Y1"))
    args = ap.parse_args(argv)

    doc = pymupdf.open(args.pdf)

    if args.manual:
        pg = doc[args.pages[0] - 1]
        x0, y0, x1, y1 = args.manual
        clip = pymupdf.Rect(x0, y0, x1, y1)
        info = (args.pages[0], "-", "-", "manual")
    else:
        pg, clip, info = find_bar(doc, args.pages[0], args.pages[1], args.heading)
        if pg is None:
            print(f"FAIL: no numbered heading matching {args.heading!r} with a "
                  f"'Diagram' block in pages {args.pages[0]}-{args.pages[1]}",
                  file=sys.stderr)
            return 1

    print(f"page {info[0]} heading_y={info[1]} diagram_y={info[2]} bottom={info[3]} "
          f"clip=({clip.x0:.0f},{clip.y0:.0f},{clip.x1:.0f},{clip.y1:.0f})")
    if args.list:
        return 0
    pix = pg.get_pixmap(matrix=pymupdf.Matrix(args.zoom, args.zoom), clip=clip, alpha=False)
    pix.save(args.out)
    print(f"-> {args.out}  {pix.width}x{pix.height}px")
    return 0


if __name__ == "__main__":
    sys.exit(main())
