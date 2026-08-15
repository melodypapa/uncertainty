#!/usr/bin/env python3
"""Structural completeness comparison for translated markdown (stripped files with IMG_PLACEHOLDER tokens).

Checks that a translation contains every piece of CONTENT from the source:
headings (by number and order), images (by token), tables (by caption number and row count),
figures (caption number), list items, and rough paragraph count.

Additional checks that catch real-world translation defects:
  * blank-line separation - a heading directly after a table row (no blank line)
    is swallowed INTO the table by renderers like MkDocs/Python-Markdown
  * continuation-marker drift - docling "Table continued from the previous page..."
    markers must keep their exact positions relative to sections AND their exact
    markdown form: a marker that is a `##` heading in the source must stay a
    heading, and a bare paragraph marker must stay a paragraph. Converting a
    plain-text marker into a heading (or vice versa) changes the rendered HTML
    (<h2>/<p> counts no longer match the source) even though every table row is
    still present.
  * callout-marker translation - docling callout headings like `## NOTE` must keep
    the English marker word; translating it to Chinese (注) breaks site styles and
    doc pipelines that key on it
  * untranslated English prose left inside table cells

Usage: compare_structure.py <source.stripped.md> <translated.stripped.md> <label>
Exit code: 0 = no problems, 1 = problems found.
"""

import difflib
import re
import sys
from collections import Counter


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
    """Caption numbers from NON-table lines only. A "Table NNN. ..." string that
    sits inside a table cell (docling merges page-split tables and caption text
    becomes cell content) is not a caption and must not be required."""
    caps = set()
    for ln in text.splitlines():
        if ln.lstrip().startswith("|"):
            continue
        caps.update(m.group(1) for m in re.finditer(pat, ln))
    return sorted(caps)


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


def heading_lines(text):
    """(heading index, line number) for every heading line in order."""
    out = []
    for i, ln in enumerate(text.splitlines()):
        if ln.startswith("#"):
            out.append((len(out), i))
    return out


def blank_before_heading(text):
    """For each heading line (in order), whether the line above it is blank
    (or the heading is the first line of the file)."""
    lines = text.splitlines()
    out = []
    for i, ln in enumerate(lines):
        if ln.startswith("#"):
            out.append(i == 0 or not lines[i - 1].strip())
    return out


def is_continuation_marker(text):
    """Docling 'table continues/continued on the next/previous page' page-break
    marker, English or Chinese. Distinguishes them from table captions
    ('Table 131. ...' / '表 131. ...'), which never match."""
    t = text.lstrip("#").strip()
    tl = t.lower()
    if "continued from the previous page" in tl or "continues on the next page" in tl:
        return True
    # Chinese variants seen in the field. '表（续' covers 表（续）...、表（续上页）。
    # 表（续）自上一页...、表（续）来自上一页...、表（续）在下页...、表（续）在下一页...
    # 表（续）至下一页...、表（续）见下一页... Translators are inconsistent about
    # which variant maps to 'continues' vs 'continued', so all of them collapse to
    # one structural key (see structural_key).
    return t.startswith("表（续")


def structural_key(h):
    """Normalize a heading to a structural token so translated headings compare
    equal to their source counterparts: numbered sections by number, docling
    continuation markers, table captions, register-substructure headings."""
    m = re.match(r"#+\s*(\d+(?:\.\d+)*)", h)
    if m:
        return "SEC:" + m.group(1)
    t = h.lstrip("#").strip()
    tl = t.lower()
    if is_continuation_marker(t):
        # All marker variants (EN continued/continues, CN 表（续）...) collapse to
        # one key: Chinese translations don't consistently preserve the
        # continued-vs-continues distinction, so enforcing it would create false
        # positives. Count/order/position relative to sections is what matters.
        return "CONT"
    if re.match(r"Table \d+\.", t) or re.match(r"表 \d+", t):
        return "CAP"
    if t in ("Offset", "Function", "Diagram", "Fields", "Register reset values") or t in (
        "偏移量", "偏移", "功能", "图示", "图", "字段", "寄存器复位值"
    ):
        return "BODY"
    if t == "NOTE":
        return "NOTE"
    return "OTHER"


def nearest_section(heads, idx):
    """The last numbered section heading at or before index idx (or first one)."""
    for h in reversed(heads[: idx + 1]):
        if re.match(r"#+\s*\d+(\.\d+)*", h):
            return h
    for h in heads:
        if re.match(r"#+\s*\d+(\.\d+)*", h):
            return h
    return "(start of document)"


def structural_drift(skeys, dkeys, sh, dh):
    """Find inserted/deleted structural markers (section numbers, continuation
    markers, captions, register-substructure headings) between source and
    translation. Returns (counts, examples)."""
    sm = difflib.SequenceMatcher(a=skeys, b=dkeys, autojunk=False)
    inserted, deleted = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        a = [k for k in skeys[i1:i2] if k != "OTHER"]
        b = [k for k in dkeys[j1:j2] if k != "OTHER"]
        if tag == "insert" and b:
            ctx = nearest_section(dh, j1)
            inserted.append((b, ctx))
        elif tag == "delete" and a:
            ctx = nearest_section(sh, i1)
            deleted.append((a, ctx))
        elif tag == "replace" and a != b:
            # a mix of insert+delete at the same spot
            if b:
                inserted.append((b, nearest_section(dh, j1)))
            if a:
                deleted.append((a, nearest_section(sh, i1)))
    return inserted, deleted


def continuation_forms(text):
    """Count docling continuation-marker lines by markdown form, as
    (headings, plain_text). The source mixes `## Table continued from the
    previous page...` headings with bare 'Table continues on the next page...'
    paragraphs; a translation that flips a marker between forms changes the
    rendered <h2>/<p> structure even when count/position are preserved."""
    heads = plain = 0
    for ln in text.splitlines():
        if not is_continuation_marker(ln):
            continue
        if ln.lstrip().startswith("#"):
            heads += 1
        else:
            plain += 1
    return heads, plain


CALLOUT_MARKERS = ("NOTE", "WARNING", "CAUTION", "IMPORTANT", "INFO", "TIP")
TRANSLATED_CALLOUTS = ("注", "注意", "警告", "小心", "重要", "提示", "信息")


def translated_callout_headings(sh, dh):
    """Flag translation headings that translated a docling callout marker heading
    (## NOTE / ## WARNING / ...) into Chinese. The skill keeps the marker word
    untranslated - site styles and doc pipelines key on it. A translation heading
    is flagged only when it is a bare Chinese callout word AND the source has an
    English callout heading in the same numbered section, so genuine Chinese
    headings elsewhere are not false positives."""
    def section(hs, i):
        for h in reversed(hs[: i + 1]):
            m = re.match(r"#+\s*(\d+(?:\.\d+)*)", h)
            if m:
                return m.group(1)
        return None

    flags = []
    for i, h in enumerate(dh):
        t = h.lstrip("#").strip()
        if t not in TRANSLATED_CALLOUTS:
            continue
        sec = section(dh, i)
        if sec is None:
            continue
        src_in_sec = [s for j, s in enumerate(sh) if section(sh, j) == sec]
        src_markers = [
            s.lstrip("#").strip()
            for s in src_in_sec
            if s.lstrip("#").strip().upper() in CALLOUT_MARKERS
        ]
        if src_markers:
            flags.append((t, sec, src_markers))
    return flags


def untranslated_prose_cells(text):
    """Table cells in the translation that are still English prose (not
    identifiers/symbols): at least 2 words, one lowercase, no digits/underscore/
    equals, and no Chinese. These should have been translated per the skill
    ('Table cells containing prose'). OCR-spaced field names like 'D d ACP' or
    'MRCFG c' (a standalone lowercase letter between tokens) are identifiers
    and are not flagged."""
    flags = []
    for ln in text.splitlines():
        if not ln.lstrip().startswith("|"):
            continue
        for cell in ln.strip().strip("|").split("|"):
            cell = cell.strip()
            if re.search(r"[\u4e00-\u9fff]", cell):
                continue
            if len(cell) < 6:
                continue
            if "_" in cell or "=" in cell or "{" in cell or "}" in cell:
                continue
            if re.search(r"\d", cell):
                continue
            # OCR-spaced identifier: a standalone lowercase letter between tokens
            # (D d ACP, MRCFG c, PID m [TSM] (b), DERRLOC d [MRCINST])
            if re.search(r"(^| )[a-z]( |$)", cell):
                continue
            words = re.findall(r"[A-Za-z][A-Za-z\-']*", cell)
            if len(words) < 2:
                continue
            if not any(w[0].islower() for w in words):
                continue
            flags.append(cell)
    return flags


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
            problems.append("heading #{} numbering differs: source {!r} vs translation {!r} (see continuation/structure drift below for the cause)".format(i + 1, a, b))
            break

    # Blank-line separation: a heading glued to the preceding table row.
    lines_dst = dst.splitlines()
    dhl = dict(heading_lines(dst))  # heading index -> line number
    sb, db = blank_before_heading(src), blank_before_heading(dst)
    lost = [i for i in range(min(len(sb), len(db))) if sb[i] and not db[i]]
    glued = [
        i
        for i in lost
        if i in dhl and dhl[i] > 0 and lines_dst[dhl[i] - 1].lstrip().startswith("|")
    ]
    if lost:
        n, g = len(lost), len(glued)
        shown = lost[:8]
        detail = "; ".join("heading #{} ({})".format(i + 1, dh[i][:45]) for i in shown)
        if g:
            problems.append(
                "blank line before heading lost at {} heading(s) - {} of them directly after a table row and will render INSIDE the table (MkDocs/Python-Markdown): {}{}".format(
                    n, g, detail, " ..." if n > len(shown) else ""
                )
            )
        else:
            problems.append(
                "blank line before heading lost at {} heading(s): {}{}".format(
                    n, detail, " ..." if n > len(shown) else ""
                )
            )

    # Docling continuation markers must keep their positions.
    skeys = [structural_key(h) for h in sh]
    dkeys = [structural_key(h) for h in dh]
    ins, dele = structural_drift(skeys, dkeys, sh, dh)
    if ins or dele:
        total_ins = sum(len(ks) for ks, _ in ins)
        total_del = sum(len(ks) for ks, _ in dele)
        parts = []
        for ks, ctx in ins[:3]:
            parts.append("inserted {} (near '{}')".format(", ".join(ks), ctx[:50]))
        for ks, ctx in dele[:3]:
            parts.append("deleted {} (near '{}')".format(", ".join(ks), ctx[:50]))
        problems.append(
            "continuation/structure drift: {} marker(s) inserted, {} deleted - docling 'Table continued' markers must keep their exact positions - {}".format(
                total_ins, total_del, "; ".join(parts)
            )
        )

    si, di = images(src), images(dst)
    if si != di:
        missing = sorted(set(si) - set(di), key=int)
        extra = sorted(set(di) - set(si), key=int)
        problems.append("image tokens differ: missing {} extra {}".format(missing, extra))

    for pat, kind in [
        (r"Table (\d+)\.", "table captions"),
        (r"表 (\d+)\.", "table captions"),
        (r"Figure (\d+)", "figure captions"),
        (r"图 (\d+)", "figure captions"),
    ]:
        s_caps = table_captions(src, pat)
        if not s_caps:
            continue
        if pat.startswith("Table"):
            d_pat = r"表 (\d+)\."
        elif pat.startswith("Figure"):
            d_pat = r"图 (\d+)"
        elif pat.startswith("表"):
            d_pat = r"Table (\d+)\."
        else:
            d_pat = r"Figure (\d+)"
        missing = sorted(set(s_caps) - set(table_captions(dst, d_pat)), key=int)
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

    # Docling continuation markers must also keep their markdown form
    # (## heading vs bare paragraph line): a flip changes the rendered
    # <h2>/<p> structure of the generated HTML.
    sf = continuation_forms(src)
    df = continuation_forms(dst)
    if sf != df:
        problems.append(
            "continuation-marker form drift: source has {} heading + {} plain-text marker(s), translation has {} heading + {} plain - a 'Table continues/continued...' / '表（续）...' marker was converted between ## heading and paragraph form, which changes the rendered <h2>/<p> structure".format(
                sf[0], sf[1], df[0], df[1]
            )
        )

    # Callout marker headings (## NOTE etc.) must keep the English marker word.
    callouts = translated_callout_headings(sh, dh)
    if callouts:
        detail = "; ".join(
            "'{}' (section {}) - source has {}".format(t, sec, ",".join(m))
            for t, sec, m in callouts[:6]
        )
        problems.append(
            "{} callout marker heading(s) translated to Chinese (keep the English marker word NOTE/WARNING/CAUTION/IMPORTANT): {}{}".format(
                len(callouts), detail, " ..." if len(callouts) > 6 else ""
            )
        )

    # Untranslated English prose left in table cells.
    flags = untranslated_prose_cells(dst)
    if flags:
        counts = Counter(flags)
        top = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:15]
        detail = "; ".join("{!r} x{}".format(c, n) for c, n in top)
        problems.append(
            "{} table cell(s) still English prose (translate them; identifiers/hex are fine): {}".format(
                len(flags), detail + (" ..." if len(counts) > len(top) else "")
            )
        )

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
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
