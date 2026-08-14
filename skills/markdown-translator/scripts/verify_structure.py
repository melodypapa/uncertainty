#!/usr/bin/env python3
"""Structural completeness comparison for translated markdown (stripped files with IMG_PLACEHOLDER tokens).

Checks that a translation contains every piece of CONTENT from the source:
headings (by number and order), images (by token), tables (by caption number and row count),
figures (caption number), list items, and rough paragraph count.

Usage: compare_structure.py <source.stripped.md> <translated.stripped.md> <label>
"""

import re
import sys


def headings(text):
    return [ln.rstrip() for ln in text.splitlines() if ln.startswith("#")]


def heading_numbers(hs):
    out = []
    for h in hs:
        m = re.match(r"#+\s*(\d+(?:\.\d+)*)", h)
        out.append(m.group(1) if m else None)
    return out


def images(text):
    return re.findall(r"IMG_PLACEHOLDER_(\d+)", text)


def table_captions(text, pat):
    return sorted(set(re.findall(pat, text)))


def table_row_counts(text):
    """Row counts for each contiguous table block, in document order."""
    counts, cur = [], 0
    for ln in text.splitlines():
        if ln.lstrip().startswith("|"):
            cur += 1
        elif cur:
            counts.append(cur)
            cur = 0
    if cur:
        counts.append(cur)
    return counts


def list_items(text):
    return [ln for ln in text.splitlines() if re.match(r"\s*[-*]\s", ln)]


def nonempty(text):
    return [ln for ln in text.splitlines() if ln.strip()]


def main():
    src_path, dst_path, label = sys.argv[1], sys.argv[2], sys.argv[3]
    src = open(src_path, encoding="utf-8").read()
    dst = open(dst_path, encoding="utf-8").read()

    problems = []

    sh, dh = headings(src), headings(dst)
    if len(sh) != len(dh):
        problems.append("heading COUNT differs: source {} vs {} ({} heading(s) missing or extra)".format(len(sh), len(dh), label))
    sn, dn = heading_numbers(sh), heading_numbers(dh)
    for i, (a, b) in enumerate(zip(sn, dn)):
        if a != b:
            problems.append("heading #{} numbering differs: source {!r} vs {} {!r} (heading may be missing/misplaced)".format(i + 1, a, label, b))
            break

    si, di = images(src), images(dst)
    if si != di:
        missing = sorted(set(si) - set(di), key=int)
        extra = sorted(set(di) - set(si), key=int)
        problems.append("image tokens differ: missing {} extra {}".format(missing, extra))

    for pat, kind, fmt in [
        (r"Table (\d+)\.", "table captions", "表 {}"),
        (r"表 (\d+)\.", "table captions", "Table {}"),
        (r"Figure (\d+)", "figure captions", "图 {}"),
        (r"图 (\d+)", "figure captions", "Figure {}"),
    ]:
        s_caps = table_captions(src, pat)
        if s_caps:
            d_caps = table_captions(dst, pat if pat.startswith(r"Table") or pat.startswith(r"Figure") else (r"表 (\d+)" if pat.startswith(r"表") else r"图 (\d+)"))
            if pat.startswith("Table"):
                d_caps = table_captions(dst, r"表 (\d+)\.")
            elif pat.startswith("Figure"):
                d_caps = table_captions(dst, r"图 (\d+)")
            missing = sorted(set(s_caps) - set(d_caps), key=int)
            if missing:
                problems.append("{} missing: {}".format(kind, ", ".join(missing)))

    srows, drows = table_row_counts(src), table_row_counts(dst)
    if len(srows) != len(drows):
        problems.append("table BLOCK count differs: source {} vs {} (a table may be missing)".format(len(srows), len(drows)))
    else:
        for i, (a, b) in enumerate(zip(srows, drows)):
            if a != b:
                problems.append("table block #{} (starting ~row {}) has {} source rows vs {} translated rows".format(i + 1, sum(srows[:i]) + 1, a, b))

    sl, dl = len(list_items(src)), len(list_items(dst))
    if abs(sl - dl) > max(2, sl // 10):
        problems.append("list item count differs notably: source {} vs {} {}".format(sl, dl, label))

    se, de = len(nonempty(src)), len(nonempty(dst))
    print("== {} ==".format(label))
    print("headings: src {} / trans {}   images: src {} / trans {}   table blocks: src {} / trans {}   table rows: src {} / trans {}   list items: src {} / trans {}   non-empty lines: src {} / trans {}".format(
        len(sh), len(dh), len(si), len(di), len(srows), len(drows), sum(srows), sum(drows), sl, dl, se, de))
    if problems:
        print("CONTENT PROBLEMS ({}):".format(len(problems)))
        for p in problems:
            print("  - " + p)
    else:
        print("CONTENT COMPLETE: no structural omissions detected")
    print()


if __name__ == "__main__":
    main()
