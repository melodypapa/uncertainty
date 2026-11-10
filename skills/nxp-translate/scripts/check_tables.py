#!/usr/bin/env python3
"""Check table structure and bold balance in translated NXP articles.

Two mechanical gates, both born from defects that shipped in the corpus:

1. Table header/separator. A GFM table only renders as a table when its header
   row is followed by a `| --- |` separator. A block of pipe rows without them
   is not a table: GFM treats the lines as one soft-wrapped paragraph and joins
   them into a single run-on line (`... reserved. | | 0 | PCE | ...`). The
   S32K5 RM corpus shipped 11 chapters this way (ch057 alone lost the header on
   52 field tables). Every maximal run of consecutive lines starting with `|`
   (outside fenced code blocks) must have at least two lines and its second
   line must be a separator row.
2. Bold balance. A stray `*` outside `**` pairs (`**xxx***`, a dropped opener)
   renders as a literal asterisk. Checked on non-table lines only — table
   cells may carry a documented literal `*` (ECC coverage matrices) — after
   stripping the bullet marker, with fenced code blocks skipped.
3. Heading level. A numbered heading's `#` count must equal its numeric depth
   + 1 (`45.1.1` → `### 1.1.`). ch057 and ch074 shipped 96 under-leveled
   headings (`### 1.7.1.`, `#### 4.1.1.1.`) this way.
4. Front-matter title. No Markdown markup (`**` renders literally in the h1,
   tab and nav), and a parenthesised English term takes half-width parentheses
   with a space before the opener — `"中文 (Term)"`, position-agnostic. The
   S32K5 corpus shipped `"中文（**Term**）"` (full-width, bolded).

Usage:
  check_tables.py <path> [<path> ...]

Each path is an article `index.md`, any `.md` file, or a directory (scanned
recursively for `.md`).

Exit codes: 0 clean, 1 defects found, 2 bad usage.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PIPE = "|"
SEP_RE_TEXT = r"^\|[ :\-|]*\|$"


def _is_separator(line: str) -> bool:
    body = line.strip()
    if not (body.startswith("|") and body.endswith("|")):
        return False
    if not all(c in "| :-" for c in body):
        return False
    return "-" in body


def check_file(path: Path) -> list[str]:
    defects: list[str] = []
    full = path.read_text(encoding="utf-8")
    lines = full.splitlines()
    in_fence = False
    run: list[tuple[int, str]] = []

    def flush() -> None:
        if not run:
            return
        first_line, first_text = run[0]
        if len(run) < 2:
            defects.append(
                f"{path}:{first_line}: stray pipe line outside any table: "
                f"{first_text[:60]!r}"
            )
        elif not _is_separator(run[1][1]):
            defects.append(
                f"{path}:{first_line}: table block of {len(run)} pipe lines with "
                f"no header+separator (renders as one run-on paragraph); "
                f"second line: {run[1][1][:60]!r}"
            )
        run.clear()

    for lineno, text in enumerate(lines, 1):
        stripped = text.lstrip()
        if stripped.startswith("```"):
            flush()
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if text.lstrip().startswith(PIPE):
            run.append((lineno, text))
            continue
        flush()
        # bold balance on non-table lines: strip the bullet marker, remove the
        # `**` pairs; any leftover `*` is stray markup (`**xxx***` renders as
        # bold-xxx plus a literal `*`). Table rows are skipped: their cells may
        # carry a documented literal `*` (ECC coverage matrices).
        body = re.sub(r"^\s*(?:\*|-|\+)\s+", "", text)
        body = re.sub(r"`[^`]*`", "", body)  # literal `*` inside code spans is fine
        body = body.replace(r"\*", "")      # escaped literal asterisk is fine
        body = re.sub(r"\*\*[^*]+\*\*", "", body)   # bold spans
        body = re.sub(r"\*[^*\s][^*]*\*", "", body) # italic spans
        if "*" in body:
            defects.append(
                f"{path}:{lineno}: stray `*` outside bold pairs (renders as a "
                f"literal asterisk): {text.strip()[:60]!r}"
            )
        # heading level = numeric depth + 1 (`45.1.1` → `### 1.1.`); ch057 and
        # ch074 shipped 96 under-leveled headings this way
        m = re.match(r"^(#{2,6}) ((\d+\.)+) ", text)
        if m:
            depth = len(m.group(2).rstrip(".").split("."))
            if len(m.group(1)) != depth + 1:
                defects.append(
                    f"{path}:{lineno}: heading level {len(m.group(1))} does not "
                    f"match numeric depth {depth} (expected {'#' * (depth + 1)}): "
                    f"{text.strip()[:60]!r}"
                )
    flush()

    # front-matter title format (§ Front matter): no Markdown markup at all —
    # Material renders the title un-parsed, so `**` shows as literal asterisks
    # in the h1, the browser tab and the nav. English term takes half-width
    # parentheses with a space before the opener.
    m = re.search(r'^title: "(.*)"\s*$', full, re.M)
    if m:
        title = m.group(1)
        if "**" in title:
            defects.append(
                f"{path}:1: front-matter title carries Markdown bold (`**`) — "
                f"it renders as literal asterisks in the h1/tab/nav; "
                f"got: {title!r}"
            )
        elif re.search(r"\S\(", title) and re.search(r"\S\(\S+\)", title):
            # parenthesised term present but glued to the Chinese part
            if re.search(r"[\u4e00-\u9fff]\(", title):
                defects.append(
                    f"{path}:1: front-matter title missing the space before "
                    f"the term's opening parenthesis: {title!r}"
                )
    return defects


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    targets: list[Path] = []
    for arg in argv[1:]:
        p = Path(arg)
        if p.is_dir():
            targets.extend(sorted(p.rglob("*.md")))
        elif p.is_file():
            targets.append(p)
        else:
            print(f"check_tables: no such path: {arg}", file=sys.stderr)
            return 2
    defects: list[str] = []
    for t in targets:
        defects.extend(check_file(t))
    for d in defects:
        print(d)
    print(f"check_tables: {len(defects)} defect(s) across {len(targets)} file(s)")
    return 1 if defects else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
