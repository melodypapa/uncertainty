#!/usr/bin/env python3
"""Dump one chapter of an NXP-published PDF for translation.

Works with any chaptered NXP document (reference manual, safety manual, ...)
that carries a PDF outline: chapter boundaries and the section tree come from
`get_toc()`, page text is stripped of the repeated running header and footer
(both by page bands and by lines auto-derived from the document itself), tables
are emitted as row grids, and figure/table captions are indexed by page.
Nothing about the document is hardcoded — pass any PDF path and chapter number.

Read-only: opens the PDF for reading only, never writes anything.

Usage:
  extract_chapter.py <pdf> <chapter> [--target-root DIR] [--out FILE]
                     [--sections-only] [--json]

Exit codes: 0 ok, 2 bad input / missing source / outline not parseable,
3 missing PyMuPDF.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import sys
from collections import Counter

try:
    import pymupdf
except ImportError:  # pragma: no cover - environment dependent
    print("error: PyMuPDF is not installed (pip install pymupdf)", file=sys.stderr)
    sys.exit(3)

# '<N> Title' — whitespace right after the number excludes section entries
# ('57.1 Chip-specific …' does not match). Chapters may sit at any outline
# level and may mix levels across one document.
CHAPTER_RE = re.compile(r"^(\d+)\s+(.+)$")
SECTION_RE = re.compile(r"^(\d+(?:\.\d+)+)\s")
CAPTION_RE = re.compile(r"^(Figure|Table)\s+(\d+)\.\s*(.*)$", re.IGNORECASE)
CONTINUATION_RE = re.compile(r"^Table\s+(?:continued|continues)\b", re.IGNORECASE)
PAGE_NUMBER_RE = re.compile(r"^\d+\s*/\s*\d+$")

# NXP layout universals. The document-specific running header (title, revision)
# is auto-derived per document — see derive_running_headers().
BASE_CHROME_RES = [
    re.compile(r"^NXP Semiconductors$"),
    re.compile(r"^Reference Manual$"),
    re.compile(r"^General Business Information$"),
    PAGE_NUMBER_RE,
]

TOP_BAND = 62.0     # blocks above this y0 are the running header
BOTTOM_BAND = 740.0  # blocks below this y0 are the page footer


def slugify(title: str) -> str:
    """lower_snake_case of a chapter title, keeping identifier underscores."""
    s = re.sub(r"[^A-Za-z0-9]+", "_", title.lower()).strip("_")
    return re.sub(r"_+", "_", s)


def chapter_dir(number: int, title: str, total: int) -> str:
    """Target article directory, zero-padded so lexical order == chapter order.

    Pad width follows the chapter count: 2 digits up to 99 chapters (ch03),
    3 digits beyond (ch057 of 111).
    """
    width = max(2, len(str(total)))
    return f"ch{number:0{width}d}_{slugify(title)}"


def heading_label(section_number: str):
    """Map a source section number to the article's heading.

    Drop the chapter number, keep the rest; heading level = number of remaining
    numeric components + 1, clamped at h6. Deeper levels become a bold paragraph
    carrying the full number instead of an invalid ####### heading.

    Returns (level, label, clamped).
    """
    parts = section_number.split(".")
    if len(parts) < 2:
        raise ValueError(f"not a section number: {section_number!r}")
    remaining = parts[1:]
    label = ".".join(remaining) + "."
    level = min(len(remaining) + 1, 6)
    return level, label, len(remaining) + 1 > 6


def derive_running_headers(doc, sample: int = 40) -> list[str]:
    """Lines repeated on (nearly) every sampled page: the running header/footer
    text this document prints in addition to the NXP universals (title,
    revision, confidential markings)."""
    sample = min(sample, doc.page_count)
    counts: Counter[str] = Counter()
    for pno in range(sample):
        for block in doc[pno].get_text("blocks"):
            y0 = block[1]
            if y0 < TOP_BAND or y0 > BOTTOM_BAND:
                for raw in block[4].splitlines():
                    line = raw.strip()
                    if line and not CONTINUATION_RE.match(line):
                        counts[line] += 1
    threshold = sample / 2
    return [line for line, n in counts.items() if n >= threshold]


def make_chrome_filter(running_headers: list[str]):
    res = list(BASE_CHROME_RES)
    for line in running_headers:
        res.append(re.compile("^" + re.escape(line) + "$"))

    def is_chrome_line(line: str) -> bool:
        return any(rx.match(line) for rx in res)

    return is_chrome_line


def is_chrome_line(line: str) -> bool:
    """Base-list variant (no derived headers); kept for direct reuse/tests."""
    return any(rx.match(line) for rx in BASE_CHROME_RES)


def is_continuation_marker(line: str) -> bool:
    return bool(CONTINUATION_RE.match(line))


def parse_chapters(toc):
    """Numbered chapters from the PDF outline, document-shape agnostic.

    A chapter is any outline entry titled '<N> <Title>'. Entries may sit at any
    outline level or mix levels across one document. Validation: the detected
    numbers must form the contiguous sequence 1..N — otherwise the outline
    shape is not understood and the error names what was found.
    """
    chapters = []
    for level, title, page in toc:
        if m := CHAPTER_RE.match(title):
            chapters.append({"number": int(m.group(1)), "title": m.group(2).strip(),
                             "start": page})
    numbers = [c["number"] for c in chapters]
    if not numbers or numbers != list(range(1, numbers[-1] + 1)):
        raise ValueError(
            "outline does not yield contiguous numbered chapters; got "
            f"{numbers[:8]}…{numbers[-8:] if len(numbers) > 8 else numbers[-8:]} "
            "— this document's outline shape needs manual inspection "
            "(doc.get_toc()) before extracting"
        )
    return chapters


def chapter_range(chapters, toc, number: int, page_count: int):
    """Inclusive PDF page range for a chapter.

    A non-final chapter ends where the next chapter starts. The final chapter
    ends before the first trailing-matter entry (appendices, release notes,
    legal information) — the first outline entry after the chapter's start
    whose title is not one of the chapter's own sections.
    """
    ch = next(c for c in chapters if c["number"] == number)
    if number < chapters[-1]["number"]:
        end = next(c["start"] for c in chapters if c["number"] == number + 1) - 1
    else:
        prefix = re.compile(rf"^{number}[\s.]")
        end = page_count
        for level, title, page in toc:
            if page > ch["start"] and not prefix.match(title):
                end = page - 1
                break
        end = max(end, ch["start"])
    return ch["start"], end


def section_tree(toc, number: int, start: int, end: int):
    """All outline entries belonging to one chapter, in source order."""
    prefix = re.compile(rf"^{number}[.\s]")
    out = []
    for level, title, page in toc:
        if not (start <= page <= end):
            continue
        if prefix.match(title):
            out.append({"level": level, "title": title, "page": page})
    return out


def clean_page(page, is_chrome=None):
    """Text lines with the repeated header/footer removed.

    Header/footer blocks live outside the TOP_BAND/BOTTOM_BAND content area.
    Continuation markers ("Table continued...", "Table continues...") sit near
    those bands but carry table state, so they are always preserved.
    """
    if is_chrome is None:
        is_chrome = is_chrome_line
    lines = []
    for block in page.get_text("blocks"):
        x0, y0, x1, y1, text = block[:5]
        in_band = y0 < TOP_BAND or y0 > BOTTOM_BAND
        for raw in text.splitlines():
            line = raw.strip()
            if not line:
                continue
            if is_continuation_marker(line):
                lines.append(line)
                continue
            if in_band or is_chrome(line):
                continue
            lines.append(line)
    return lines


def stitch_table_rows(grids):
    """Concatenate per-page table grids, dropping repeated header rows."""
    rows = []
    for grid in grids:
        if not grid:
            continue
        if rows and grid[0] == rows[0]:
            grid = grid[1:]
        rows.extend(grid)
    return rows


def page_tables(page):
    """Row grids detected on a page (stdout noise from PyMuPDF suppressed)."""
    grids = []
    with contextlib.redirect_stdout(io.StringIO()):
        found = page.find_tables()
    for table in found.tables:
        grid = [[re.sub(r"\s+", " ", cell or "").strip()
                 for cell in row] for row in table.extract()]
        if grid:
            grids.append(grid)
    return grids


def check_source(path: str):
    if not os.path.isfile(path):
        print(f"error: source PDF not found: {path}", file=sys.stderr)
        sys.exit(2)
    with open(path, "rb") as fh:
        head = fh.read(200)
    if b"git-lfs.github.com/spec/v1" in head:
        print("error: source is an unresolved Git LFS pointer; run 'git lfs pull'", file=sys.stderr)
        sys.exit(2)


def build_report(pdf_path, number, target_root=".", sections_only=False):
    doc = pymupdf.open(pdf_path)
    toc = doc.get_toc()
    chapters = parse_chapters(toc)
    if not any(c["number"] == number for c in chapters):
        print(f"error: chapter {number} is out of range 1-{chapters[-1]['number']}",
              file=sys.stderr)
        sys.exit(2)
    start, end = chapter_range(chapters, toc, number, doc.page_count)
    ch = next(c for c in chapters if c["number"] == number)
    total = chapters[-1]["number"]
    document = (doc.metadata.get("title") or "").strip() or os.path.basename(pdf_path)
    report = {
        "source": pdf_path,
        "document": document,
        "chapter": number,
        "title": ch["title"],
        "pages": [start, end],
        "target": f"{target_root}/{chapter_dir(number, ch['title'], total)}/index.md",
        "sections": section_tree(toc, number, start, end),
        "captions": [],
        "tables": [],
        "page_text": [],
    }
    if sections_only:
        doc.close()
        return report

    is_chrome = make_chrome_filter(derive_running_headers(doc))
    for pno in range(start, end + 1):
        page = doc[pno - 1]
        lines = clean_page(page, is_chrome)
        report["page_text"].append({"page": pno, "lines": lines})
        for line in lines:
            if m := CAPTION_RE.match(line):
                report["captions"].append({"page": pno, "kind": m.group(1).title(),
                                           "number": int(m.group(2)), "text": line})
            elif is_continuation_marker(line):
                report["captions"].append({"page": pno, "kind": "Continuation",
                                           "number": None, "text": line})
        for grid in page_tables(page):
            report["tables"].append({"page": pno, "rows": grid})
    doc.close()
    return report


def render_text(report):
    out = [
        f"# Chapter {report['chapter']} — {report['title']}",
        "",
        f"Source: {report['source']} ({report['document']})",
        f"PDF pages: {report['pages'][0]}-{report['pages'][1]}",
        f"Target: {report['target']}",
        "",
        f"## Outline sections ({len(report['sections'])})",
    ]
    for s in report["sections"]:
        out.append(f"  L{s['level']:<2} p{s['page']:<5} {s['title']}")
    if not report["page_text"]:
        return "\n".join(out) + "\n"

    out += ["", f"## Captions ({len(report['captions'])})"]
    for c in report["captions"]:
        out.append(f"  p{c['page']:<5} {c['text']}")

    out += ["", "## Page text"]
    for p in report["page_text"]:
        out += ["", f"### PDF page {p['page']}"] + p["lines"]

    out += ["", f"## Table grids ({len(report['tables'])})"]
    for i, t in enumerate(report["tables"], 1):
        out += ["", f"### Table grid {i} (PDF page {t['page']})"]
        for row in t["rows"]:
            out.append("| " + " | ".join(row) + " |")
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", help="path to the NXP-published source PDF")
    ap.add_argument("chapter", type=int, help="chapter number to dump")
    ap.add_argument("--target-root", default=".",
                    help="article root the chapter maps to (default: current directory)")
    ap.add_argument("--out", help="write the dump to this file instead of stdout")
    ap.add_argument("--sections-only", action="store_true",
                    help="emit only the outline section tree (fast, no page text)")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = ap.parse_args(argv)

    check_source(args.pdf)
    report = build_report(args.pdf, args.chapter, args.target_root,
                          args.sections_only)
    if args.json:
        payload = json.dumps(report, ensure_ascii=False, indent=2)
    else:
        payload = render_text(report)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(payload)
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
