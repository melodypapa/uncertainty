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

Note: check `page.get_image_info()` first — if the page embeds raster images,
extract those instead (the S32G3 RM carries vector figures; the S32K5 RM also
proves vector: 0 embedded images on its figure pages).

Usage:
  recrop_figure.py <pdf> <figure-num> <page> <out.png> [--zoom Z]

Exit codes: 0 ok, 1 figure not found / no drawings, 2 usage.
"""

import argparse
import sys

import pymupdf

GAP_NOT_USED = None  # kept out of the algorithm by design; see docstring
CONTENT_TOP, CONTENT_BOTTOM = 62.0, 740.0
MARGIN_MIN = 6.0
BODY_MIN_CHARS = 40
BODY_MIN_WIDTH = 380.0
MIN_DRAWINGS = 5
PROXIMITY_PT = 25.0
LABEL_MAX_SIZE = 10.0  # pt; section headings are larger


def figure_clip(page, fig_num):
    caps = page.search_for(f"Figure {fig_num}.")
    if not caps:
        return None, "caption not found"
    cap_y = caps[0].y0
    all_draw = [d["rect"] for d in page.get_drawings()
                if d["rect"].y0 > CONTENT_TOP and d["rect"].y1 < CONTENT_BOTTOM
                and d["rect"].width > 0.5 and d["rect"].height > 0.5]
    longs = sorted([pymupdf.Rect(b[:4]) for b in page.get_text("blocks")
                    if b[4].strip() and len(" ".join(b[4].split())) > BODY_MIN_CHARS
                    and (b[2] - b[0]) > BODY_MIN_WIDTH
                    and b[3] < cap_y and b[1] > CONTENT_TOP],
                   key=lambda r: r.y1)
    sentinels = sorted([r.y1 for r in longs] + [CONTENT_TOP], reverse=True)
    for top in sentinels:
        ds = [r for r in all_draw if r.y0 >= top - 2 and r.y1 <= cap_y - 2]
        if len(ds) < MIN_DRAWINGS:
            continue
        u = pymupdf.Rect()
        for r in ds:
            u |= r
        # grow with label-like text to a fixpoint: a label can sit fully
        # outside the drawing union (the "Interrupt vectors" label sits 1.4pt
        # above its box). Label-like = not body width AND label-sized font
        # (section headings are larger and are never absorbed); growth accepts
        # blocks intersecting the bbox, vertically overlapping it, or within
        # PROXIMITY_PT of it, and cascades as the bbox grows
        labels = []
        for blk in page.get_text("dict")["blocks"]:
            if blk.get("type") != 0:
                continue
            r = pymupdf.Rect(blk["bbox"])
            sizes = [s["size"] for ln in blk.get("lines", []) for s in ln.get("spans", [])]
            txt = " ".join(sp["text"] for ln in blk.get("lines", []) for sp in ln.get("spans", []))
            if not txt.strip() or not sizes:
                continue
            if (r.width < BODY_MIN_WIDTH and max(sizes) <= LABEL_MAX_SIZE
                    and CONTENT_TOP < r.y0 and r.y1 < cap_y - 2):
                labels.append((r, txt))
        changed = True
        while changed:
            changed = False
            near = pymupdf.Rect(u.x0 - PROXIMITY_PT, u.y0 - PROXIMITY_PT,
                                u.x1 + PROXIMITY_PT, u.y1 + PROXIMITY_PT)
            for r, txt in labels:
                if r.intersects(near):
                    before = (u.x0, u.y0, u.x1, u.y1)
                    u |= r
                    if (u.x0, u.y0, u.x1, u.y1) != before:
                        changed = True
        band_top = top
        m = max(MARGIN_MIN, 0.04 * max(u.width, u.height))
        clip = pymupdf.Rect(max(40.0, u.x0 - m),
                            max(CONTENT_TOP, u.y0 - 6, band_top + 2),
                            min(page.rect.x1 - 40, u.x1 + m),
                            min(cap_y - 2, u.y1 + m))
        return clip, f"band top {top:.0f}; bbox {u}"
    return None, "no drawing cluster found above the caption"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", help="path to the NXP-published source PDF")
    ap.add_argument("figure", type=int, help="global figure number (Figure N.)")
    ap.add_argument("page", type=int, help="1-based PDF page holding the figure")
    ap.add_argument("out", help="output PNG path")
    ap.add_argument("--zoom", type=float, default=3.0, help="render zoom (default 3.0)")
    args = ap.parse_args(argv)

    doc = pymupdf.open(args.pdf)
    page = doc[args.page - 1]
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
