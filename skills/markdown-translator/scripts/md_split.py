#!/usr/bin/env python3
"""Split a text-only markdown file into parallelizable segments and rejoin them.

Why: the slow part of bulk translation is sequential model generation — a large
chapter translated "segment after segment" in one conversation burns one round
trip per segment. Splitting at heading boundaries turns N sequential segments
into N parallel workers. Split/join are mechanical and verified, so nothing can
be lost; the usual image and structure checks then run unchanged on the joined
file.

Subcommands:
  split <in.md> <segdir> [--target-size BYTES]
      Split <in.md> at heading boundaries into segdir/part_000.md, part_001.md, ...
      A heading is a valid split point only when it is NOT inside a fenced code
      block and NOT inside the YAML frontmatter. Consecutive sections are packed
      so each part is roughly target-size (default 4096 bytes of text). Writes
      segdir/manifest.json with the ordered part names and per-part
      IMG_PLACEHOLDER token counts. Prints a plan; if the file has no usable
      split points it exits 0 with a single part and prints NO-SPLIT so the
      caller translates the file directly.
  join <segdir> <out.md>
      Concatenates part_*.zh.md (the translated counterparts, written by the
      translation workers) in manifest order. Fails if any part is missing or
      empty, or if the total IMG_PLACEHOLDER token count drifted from the
      manifest (a token dropped, renumbered, or added).
"""

import json
import os
import re
import sys

HEADING_RE = re.compile(r"^ {0,3}#{1,6}(?: |$)")
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
TOKEN_RE = re.compile(r"!\[[^\]]*\]\(IMG_PLACEHOLDER_(\d+)\)")
DEFAULT_TARGET = 4096


def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_text(path, text):
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def token_count(text):
    return len(TOKEN_RE.findall(text))


def iter_sections(lines):
    """Return [(start, end), ...] line ranges, splitting only before headings.

    Split points must not fall inside fenced code blocks or the YAML
    frontmatter. Table blocks and lists terminate at a heading in markdown, so
    no extra tracking is needed for them.
    """
    in_fence = None
    sections = []
    start = 0
    i = 0
    n = len(lines)
    if n and lines[0].strip() == "---":
        # consume the whole frontmatter block up front: opener (line 0), body, closer
        i = 1
        while i < n and lines[i].strip() != "---":
            i += 1
        if i < n:
            i += 1  # past the closing marker
    while i < n:
        ln = lines[i].rstrip("\n")
        stripped = ln.strip()
        if in_fence is not None:
            if FENCE_RE.match(ln) and stripped.startswith(in_fence):
                in_fence = None
            i += 1
            continue
        if FENCE_RE.match(ln):
            in_fence = stripped[0]
            i += 1
            continue
        if HEADING_RE.match(ln):
            if i > start:
                sections.append((start, i))
            start = i
        i += 1
    if start < n:
        sections.append((start, n))
    return sections


def pack(sections, lines, target):
    """Greedily merge consecutive sections so each part is ~target bytes."""
    parts = []
    cur_start = cur_end = None
    cur_bytes = 0
    for s, e in sections:
        size = sum(len(l) for l in lines[s:e])
        if cur_start is None:
            cur_start, cur_end, cur_bytes = s, e, size
        elif cur_bytes + size <= target:
            cur_end, cur_bytes = e, cur_bytes + size
        else:
            parts.append((cur_start, cur_end))
            cur_start, cur_end, cur_bytes = s, e, size
    if cur_start is not None:
        parts.append((cur_start, cur_end))
    return parts


def cmd_split(args):
    src, segdir = args[0], args[1]
    target = DEFAULT_TARGET
    if "--target-size" in args:
        target = int(args[args.index("--target-size") + 1])
    text = read_text(src)
    lines = text.splitlines(keepends=True)
    sections = iter_sections(lines)
    os.makedirs(segdir, exist_ok=True)

    if len(sections) <= 1:
        part_text = text
        write_text(os.path.join(segdir, "part_000.md"), part_text)
        manifest = {
            "source": src,
            "parts": ["part_000.md"],
            "token_counts": [token_count(part_text)],
            "total_tokens": token_count(part_text),
        }
        write_text(os.path.join(segdir, "manifest.json"), json.dumps(manifest, indent=1))
        print("NO-SPLIT: no heading boundaries to split on; translate the file directly")
        return

    parts = pack(sections, lines, target)
    manifest_parts = []
    token_counts = []
    for idx, (s, e) in enumerate(parts):
        name = "part_{:03d}.md".format(idx)
        part_text = "".join(lines[s:e])
        write_text(os.path.join(segdir, name), part_text)
        manifest_parts.append(name)
        token_counts.append(token_count(part_text))
    manifest = {
        "source": src,
        "parts": manifest_parts,
        "token_counts": token_counts,
        "total_tokens": sum(token_counts),
    }
    write_text(os.path.join(segdir, "manifest.json"), json.dumps(manifest, indent=1))

    total = sum(len(l) for l in lines)
    print("split {} ({} bytes text) -> {} segments in {}".format(src, total, len(parts), segdir))
    for idx, (s, e) in enumerate(parts):
        size = sum(len(l) for l in lines[s:e])
        print("  part_{:03d}.md  {:6d} bytes  {} placeholder tokens".format(idx, size, token_counts[idx]))
    print("translate each part in parallel, writing <part>.zh.md next to it, then join")


def cmd_join(args):
    segdir, out = args
    manifest_path = os.path.join(segdir, "manifest.json")
    if not os.path.exists(manifest_path):
        raise SystemExit("ERROR: {} missing — run split first".format(manifest_path))
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    parts = []
    for i, name in enumerate(manifest["parts"]):
        zh = os.path.join(segdir, name.replace(".md", ".zh.md"))
        if not os.path.exists(zh):
            raise SystemExit(
                "ERROR: translated part missing: {} (worker did not finish; translate it and rejoin)".format(zh)
            )
        t = read_text(zh)
        if not t.strip():
            raise SystemExit("ERROR: translated part {} is empty".format(zh))
        have = token_count(t)
        expect = manifest["token_counts"][i]
        if have != expect:
            raise SystemExit(
                "ERROR: {} has {} placeholder tokens, expected {} — a token was dropped, renumbered, or added".format(
                    zh, have, expect
                )
            )
        parts.append(t if t.endswith("\n") else t + "\n")

    joined = "".join(parts)
    write_text(out, joined)
    print("joined {} segments -> {} ({} placeholder tokens)".format(len(parts), out, manifest["total_tokens"]))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    commands = {"split": cmd_split, "join": cmd_join}
    cmd = sys.argv[1]
    if cmd not in commands:
        print("unknown subcommand: {}\n".format(cmd) + __doc__)
        sys.exit(1)
    commands[cmd](sys.argv[2:])


if __name__ == "__main__":
    main()
