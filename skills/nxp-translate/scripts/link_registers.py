#!/usr/bin/env python3
r"""Link register mentions in an NXP article's memory-map tables to their sections.

The source PDF's memory-map table hyperlinks every register to its own
register-description section; the PDF→markdown translation loses that link.
This restores it intra-article: in a GFM table whose header carries the
memory-map shape (偏移 … 寄存器 … 复位值), the register-name cell
`…（**REG**）` becomes `[…（**REG**）](#anchor)` when a register subsection
heading `…（**REG**）` exists in the same article. Range headings
(`MBPTR0_-_MBPTR2`) cover their enumerated rows (MBPTR0, MBPTR1, MBPTR2).
Everything else — prose mentions, reset-value tables, registers with no
in-chapter subsection — stays plain and is reported by --list.

Anchors replicate MkDocs Material's unicode slug (`pymdownx.slugs`, lower
case, NFKC, `[^\w\s-]` stripped, `[-\s]+` → `-`): a heading
`### 5.2. 控制密钥寄存器（**CTL_KEY**）` anchors as `52-控制密钥寄存器ctl_key`.
Verified against the built site.

Usage:
  link_registers.py --list <article>
  link_registers.py --apply <article>

Exit codes: 0 ok (0 candidates is a valid result), 1 usage error.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

SEP_RE = re.compile(r"^\|[\s:|-]+\|$")
ROW_RE = re.compile(r"^\|.*\|$")
MEMMAP_RE = re.compile(r"偏移.*寄存器.*复位值|Offset.*Register.*Reset")
NAME_RE = re.compile(
    r"（(?:\*\*)?([A-Za-z0-9_]+?)(?:_-_([A-Za-z0-9_]+?))?(?:\*\*)?）")  # bold or plain
HEADING_RE = re.compile(r"^(#{2,6}) (.*)$")


def slugify(heading_text: str) -> str:
    """MkDocs Material heading anchor (pymdownx unicode slug, '-' separator)."""
    value = unicodedata.normalize("NFKC", heading_text)
    value = re.sub(r"\*\*", "", value)
    value = re.sub(r"[^\w\s-]", "", value, flags=re.UNICODE)
    value = re.sub(r"[-\s]+", "-", value).strip("-")
    return value.lower()


def expand_range(first: str, last: str) -> list[str]:
    """`MBPTR0_-_MBPTR2` -> [MBPTR0, MBPTR1, MBPTR2] (numeric-suffix range)."""
    m1, m2 = re.match(r"^(.*?)(\d+)$", first), re.match(r"^(.*?)(\d+)$", last)
    if not (m1 and m2) or m1.group(1) != m2.group(1):
        return [first]
    prefix, a, b = m1.group(1), int(m1.group(2)), int(m2.group(2))
    width = len(m1.group(2))
    if b < a or b - a > 512:
        return [first]
    return [f"{prefix}{i:0{width}d}" if width > 1 else f"{prefix}{i}"
            for i in range(a, b + 1)]


def parse(article: Path):
    """Return (lines, register_anchors, map_tables).

    register_anchors: name -> anchor of the register's own subsection.
    map_tables: list of (start_idx, end_idx) spans of GFM memory-map tables.
    """
    lines = article.read_text(encoding="utf-8").splitlines()
    anchors: dict[str, str] = {}
    tables: list[tuple[int, int]] = []
    in_table, table_start = False, 0
    for i, line in enumerate(lines):
        if m := HEADING_RE.match(line):
            for first, last in NAME_RE.findall(m.group(2)):
                anchor = slugify(m.group(2))
                if last:
                    anchors.setdefault(f"{first}_-_{last}", anchor)
                for name in ([first] if not last else expand_range(first, last)):
                    anchors.setdefault(name, anchor)
        if ROW_RE.match(line):
            if not in_table:
                in_table, table_start = True, i
        else:
            if in_table:
                tables.append((table_start, i - 1))
                in_table = False
    if in_table:
        tables.append((table_start, len(lines) - 1))
    # a run may fuse several tables (a missing blank line); a memory map
    # starts at any row matching the header shape whose next row is a separator
    map_tables = []
    for s, e in tables:
        if e <= s + 1:
            continue
        if MEMMAP_RE.search(lines[s]):
            map_tables.append((s, e))
            continue
        start = None
        for i in range(s + 1, e + 1):
            if MEMMAP_RE.search(lines[i]) and i < e and SEP_RE.match(lines[i + 1]):
                if start is not None:
                    map_tables.append((start, i - 1))
                start = i
        if start is not None:
            map_tables.append((start, e))
    return lines, anchors, map_tables


def candidates(lines, anchors, map_tables):
    """(line_idx, cell_new_text) pairs; a cell links at most once.

    A range cell (`A_-_B`) prefers the range heading's anchor; a single-name
    cell falls back to a range heading that enumerates it.
    """
    out = []
    for s, e in map_tables:
        for i in range(s + 2, e + 1):  # skip header + separator
            line = lines[i]
            if "](" in line:  # already linked — idempotency guard
                continue
            new = line
            for m in NAME_RE.finditer(line):
                matched = m.group(0)
                first, last = m.group(1), m.group(2)
                target = None
                if last:
                    if f"{first}_-_{last}" in anchors:
                        target = anchors[f"{first}_-_{last}"]
                    else:
                        target = next((anchors[n]
                                       for n in expand_range(first, last)
                                       if n in anchors), None)
                elif first in anchors:
                    target = anchors[first]
                if target:
                    new = new.replace(matched, f"[{matched}](#{target})")
                    break
            if new != line:
                out.append((i, new))
    return out


def main(argv):
    if len(argv) != 3 or argv[1] not in ("--list", "--apply"):
        print(__doc__)
        return 1
    mode, path = argv[1], Path(argv[2])
    if path.is_dir():
        path = path / "index.md"
    lines, anchors, map_tables = parse(path)
    cands = candidates(lines, anchors, map_tables)
    if mode == "--list":
        print(f"{path}: {len(map_tables)} memory-map table(s), "
              f"{len(anchors)} register subsection(s), {len(cands)} candidate link(s)")
        for i, new in cands:
            print(f"  L{i+1}: {new[:110]}")
        linked = sum(1 for s, e in map_tables for i in range(s + 2, e + 1)
                     if "](" in lines[i])
        print(f"  already linked: {linked}")
        return 0
    for i, new in sorted(cands, reverse=True):
        lines[i] = new
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{path}: applied {len(cands)} link(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
