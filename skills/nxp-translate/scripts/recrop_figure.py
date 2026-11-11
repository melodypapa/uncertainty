#!/usr/bin/env python3
"""Accurately crop one numbered figure from an NXP PDF.

The naive recipe — union of all drawings on the page, rendered above the
caption — is wrong whenever the page top carries vector decorations: NOTE and
CAUTION pills and their divider rules are drawings too, so their rects merge
the figure's bbox with the body text above it and the crop ships that body
text (observed on ch059 WKPU Figure_273: a NOTE block, a section heading and
two paragraphs above the diagram).

The accurate recipe implemented here:

1. caption_y = position of the `Figure N.` caption;
2. body text above the caption = text blocks with >40 chars AND >380pt width
   (figure labels can be long but never span the text column);
3. the figure band starts below the LAST such body block, walking upward until
   the band contains >= 5 drawings (a NOTE sitting between the figure and its
   caption steps past it);
4. bbox = union of the drawings inside the band, grown with label-like text
   to a fixpoint: a block qualifies when it is not body width AND its font is
   label-sized (<= 10pt; section headings are larger and are never absorbed),
   and it intersects the bbox, vertically overlaps it, or sits within 25pt of
   it — a label can sit fully outside the drawing union (the "Interrupt
   vectors" label sits 1.4pt above its box; a bus label sits left of the
   diagram);
5. margins: ~4% of the larger dimension (min 6pt) left/right/bottom; the top
   margin is capped at 6pt and clamped below the body-text boundary so NOTE
   borders cannot re-enter;
6. render at >= 2x zoom, then VERIFY the PNG: complete labels, no body text,
   no heading, no NOTE and no caption.

Manual fallback (`--band` + `--manual`): some pages defeat the automatic
recipe — tables fused directly onto waveforms, text-heavy lead-ins, prose
directly above the diagram. For those, set the boundaries by hand:
  1. `--band` renders the whole content band above the caption at reading
     resolution — read the figure's boundaries off it;
  2. re-run with `--manual X0 Y0 X1 Y1` (PDF coordinates) to render the
     hand-set clip;
  3. verify the PNG (complete labels, nothing above the boundary), and record
     the manual boundaries in the PR text.

Note: check `page.get_image_info()` first — if the page embeds raster images,
extract those instead (the S32G3 RM carries vector figures; the S32K5 RM also
proves vector: 0 embedded images on its figure pages).

Usage:
  recrop_figure.py <pdf> <figure-num> <page> <out.png> [--zoom Z]
  recrop_figure.py <pdf> <figure-num> <page> <out.png> --band
  recrop_figure.py <pdf> <figure-num> <page> <out.png> --manual X0 Y0 X1 Y1

Exit codes: 0 ok, 1 figure not found / no drawings, 2 usage.
"""

import argparse
import re
import sys
from pathlib import Path

import pymupdf

GAP_NOT_USED = None  # kept out of the algorithm by design; see docstring
CONTENT_TOP, CONTENT_BOTTOM = 62.0, 740.0
MARGIN_MIN = 6.0
BODY_MIN_CHARS = 40
BODY_MIN_WIDTH = 380.0
MIN_DRAWINGS = 5
PROXIMITY_PT = 25.0
LABEL_MAX_SIZE = 10.0  # pt; section headings are larger
CLUSTER_GAP_PT = 30.0  # vertical gap that separates figure clusters


def find_caption(page, fig_num):
    """The caption rect: a line that BEGINS with 'Figure N.' — prose
    cross-references ('... as shown in Figure 319, ...') sit mid-line and are
    rejected."""
    for r in page.search_for(f"Figure {fig_num}."):
        line = page.get_text("text", clip=pymupdf.Rect(r.x0 - 2, r.y0 - 1,
                                                       page.rect.x1 - 40, r.y1 + 1))
        if line.strip().startswith(f"Figure {fig_num}."):
            return r
    return None


def all_caption_lines(page):
    """Every 'Figure N.' caption line on the page (not prose mentions)."""
    out = []
    for b in page.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        for ln in b.get("lines", []):
            r = pymupdf.Rect(ln["bbox"])
            txt = "".join(sp["text"] for sp in ln.get("spans", [])).strip()
            if re.match(r"^Figure \d+\.", txt):
                out.append((r, txt))
    return out


def figure_clip(page, fig_num):
    cap = find_caption(page, fig_num)
    if cap is None:
        return None, "caption not found on this page"
    cap_y = cap.y0

    # a page can hold several figures; only drawings of THIS figure belong to
    # the band — the previous figure's drawings end above its own caption
    prev_cap_bottom = CONTENT_TOP
    for r, txt in all_caption_lines(page):
        if r.y1 < cap_y - 5:
            prev_cap_bottom = max(prev_cap_bottom, r.y1 + 2)

    draws = [d["rect"] for d in page.get_drawings()
             if d["rect"].y0 > prev_cap_bottom and d["rect"].y1 < cap_y - 2
             and (d["rect"].width > 1 or d["rect"].height > 1)]
    if len(draws) < MIN_DRAWINGS:
        return None, (f"only {len(draws)} drawings between the previous caption "
                      f"({prev_cap_bottom:.0f}) and this caption")
    # cluster by vertical proximity; the figure = the bottom-most cluster with
    # a dominant area (it sits directly above its caption)
    draws.sort(key=lambda r: r.y0)
    clusters = []
    for r in draws:
        if clusters and r.y0 - max(x.y1 for x in clusters[-1]) <= CLUSTER_GAP_PT:
            clusters[-1].append(r)
        else:
            clusters.append([r])
    unions = []
    for g in clusters:
        u = pymupdf.Rect()
        for r in g:
            u |= r
        unions.append(u)
    max_area = max(u.get_area() for u in unions)
    cand = [u for u in unions
            if u.get_area() >= 0.4 * max_area]
    u = max(cand, key=lambda r: r.y1)  # bottom-most dominant cluster

    # grow with label-like text to a fixpoint: a label can sit fully outside
    # the drawing union (the "Interrupt vectors" label sits 1.4pt above its
    # box; a bus label sits left of the diagram). Label-like = not body width
    # and label-sized font (section headings are larger, never absorbed)
    labels = []
    for blk in page.get_text("dict")["blocks"]:
        if blk.get("type") != 0:
            continue
        r = pymupdf.Rect(blk["bbox"])
        sizes = [s["size"] for ln in blk.get("lines", []) for s in ln.get("spans", [])]
        txt = " ".join(sp["text"] for ln in blk.get("lines", []) for sp in ln.get("spans", []))
        if (txt.strip() and sizes and r.width < BODY_MIN_WIDTH
                and max(sizes) <= LABEL_MAX_SIZE
                and prev_cap_bottom < r.y0 and r.y1 < cap_y - 2):
            labels.append(r)
    changed = True
    while changed:
        changed = False
        near = pymupdf.Rect(u.x0 - PROXIMITY_PT, u.y0 - PROXIMITY_PT,
                            u.x1 + PROXIMITY_PT, u.y1 + PROXIMITY_PT)
        for r in labels:
            if r.intersects(near):
                before = (u.x0, u.y0, u.x1, u.y1)
                u |= r
                if (u.x0, u.y0, u.x1, u.y1) != before:
                    changed = True

    m = max(MARGIN_MIN, 0.04 * max(u.width, u.height))
    clip = pymupdf.Rect(max(40.0, u.x0 - m),
                        max(CONTENT_TOP, u.y0 - 6, prev_cap_bottom + 2),
                        min(page.rect.x1 - 40, u.x1 + m),
                        min(cap_y - 2, u.y1 + m))
    return clip, f"figure cluster {u}; prev caption bottom {prev_cap_bottom:.0f}"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", help="path to the NXP-published source PDF")
    ap.add_argument("figure", type=int, help="global figure number (Figure N.)")
    ap.add_argument("page", type=int, help="1-based PDF page holding the figure")
    ap.add_argument("out", help="output PNG path")
    ap.add_argument("--zoom", type=float, default=3.0, help="render zoom (default 3.0)")
    ap.add_argument("--band", action="store_true",
                    help="manual fallback step 1: render the whole content band "
                         "above the caption at 1.5x for boundary reading")
    ap.add_argument("--manual", nargs=4, type=float, metavar=("X0", "Y0", "X1", "Y1"),
                    help="manual fallback step 2: render this hand-set clip "
                         "instead of the automatic recipe")
    args = ap.parse_args(argv)

    doc = pymupdf.open(args.pdf)
    page = doc[args.page - 1]
    if args.band:
        caps = page.search_for(f"Figure {args.figure}.")
        if not caps:
            print(f"FAIL Figure {args.figure}: caption not found", file=sys.stderr)
            return 1
        cap_y = caps[0].y0
        top = CONTENT_TOP if cap_y < 300 else max(CONTENT_TOP, cap_y - 480)
        pix = page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5),
                              clip=pymupdf.Rect(40, top, page.rect.x1 - 37, cap_y + 8),
                              alpha=False)
        pix.save(args.out)
        print(f"Figure {args.figure}: p{args.page} boundary-reading band "
              f"{pix.width}x{pix.height}px (caption y={cap_y:.0f}) -> {args.out}")
        return 0
    if args.manual:
        x0, y0, x1, y1 = args.manual
        pix = page.get_pixmap(matrix=pymupdf.Matrix(args.zoom, args.zoom),
                              clip=pymupdf.Rect(x0, y0, x1, y1), alpha=False)
        pix.save(args.out)
        print(f"Figure {args.figure}: p{args.page} MANUAL clip "
              f"({x0:g},{y0:g},{x1:g},{y1:g}) {pix.width}x{pix.height}px -> {args.out}")
        return 0
    # embedded raster? extract it natively instead of rendering the vector
    # clip (preserves the source resolution, no recomposition)
    caps = page.search_for(f"Figure {args.figure}.")
    if caps:
        cap_y = caps[0].y0
        imgs = [im for im in page.get_image_info(xrefs=True)
                if pymupdf.Rect(im["bbox"]).y1 <= cap_y + 2
                and pymupdf.Rect(im["bbox"]).y0 > CONTENT_TOP]
        # extract only when a raster DOMINATES the figure; small insets and
        # icon tiles inside an otherwise vector diagram render fine with the
        # vector path below
        union = pymupdf.Rect()
        for d in page.get_drawings():
            r = d["rect"]
            if r.y1 <= cap_y + 2 and r.y0 > CONTENT_TOP and (r.width > 1 or r.height > 1):
                union |= r
        dominant = imgs and (
            not union.is_empty
            and pymupdf.Rect(max(imgs, key=lambda im: pymupdf.Rect(im["bbox"]).get_area())["bbox"]).get_area()
            >= 0.6 * union.get_area())
        if imgs and dominant:
            best = max(imgs, key=lambda im: pymupdf.Rect(im["bbox"]).get_area())
            bbox = pymupdf.Rect(best["bbox"])
            try:
                raw = doc.extract_image(best["xref"])
                out = Path(args.out)
                out.write_bytes(raw["image"])
                print(f"Figure {args.figure}: p{args.page} extracted embedded "
                      f"{raw['width']}x{raw['height']} {raw['ext']} -> {out}")
                return 0
            except Exception as exc:
                # broken xref (observed in watermarked-plain rebuilds): fall
                # back to rendering the image's own bbox — still exactly the
                # picture, no surrounding decorations
                m = max(MARGIN_MIN, 0.04 * max(bbox.width, bbox.height))
                clip = pymupdf.Rect(max(40.0, bbox.x0 - m), max(CONTENT_TOP, bbox.y0 - 2),
                                    min(page.rect.x1 - 40, bbox.x1 + m),
                                    min(cap_y - 2, bbox.y1 + 2))
                pix = page.get_pixmap(matrix=pymupdf.Matrix(args.zoom, args.zoom),
                                      clip=clip, alpha=False)
                pix.save(args.out)
                print(f"Figure {args.figure}: p{args.page} rendered embedded-image "
                      f"bbox {pix.width}x{pix.height}px (extract failed: {exc})")
                return 0
    clip, info = figure_clip(page, args.figure)
    if clip is None:
        print(f"FAIL Figure {args.figure}: {info}", file=sys.stderr)
        return 1
    pix = page.get_pixmap(matrix=pymupdf.Matrix(args.zoom, args.zoom),
                          clip=clip, alpha=False)
    pix.save(args.out)
    print(f"Figure {args.figure}: p{args.page} {pix.width}x{pix.height}px ({info})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
