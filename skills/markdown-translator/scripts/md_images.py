#!/usr/bin/env python3
"""Helpers for translating docling-style markdown that contains inline base64 images.

Subcommands:
  status <file.md>                    Print inline-image count and byte breakdown.
  extract <in.md> <out.md> <map.json> Replace each inline image with a placeholder token.
  restore <in.md> <map.json> <out.md>  Re-insert original images at their placeholders.
  verify <src.md> <dst.md>            Prove the translated file still contains every source image byte-for-byte.
  plan <src_dir> <dst_dir>            List which target translations are MISSING or STALE.
"""

import json
import os
import re
import sys

DATA_URI_RE = re.compile(r"!\[([^\]]*)\]\((data:[^)\s]*;base64,[A-Za-z0-9+/=%]*)\)")
TOKEN_RE = re.compile(r"!\[([^\]]*)\]\(IMG_PLACEHOLDER_(\d+)\)")


def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_text(path, text):
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def cmd_status(args):
    (path,) = args
    text = read_text(path)
    matches = list(DATA_URI_RE.finditer(text))
    img_bytes = sum(len(m.group(0)) for m in matches)
    print("file={}".format(path))
    print("inline_images={}".format(len(matches)))
    print("inline_image_bytes={}".format(img_bytes))
    print("text_bytes={}".format(len(text) - img_bytes))


def cmd_extract(args):
    src, dst, map_path = args
    text = read_text(src)
    originals = []

    def repl(m):
        originals.append(m.group(0))
        return "![{}]({})".format(m.group(1), "IMG_PLACEHOLDER_{}".format(len(originals) - 1))

    stripped = DATA_URI_RE.sub(repl, text)
    write_text(dst, stripped)
    with open(map_path, "w", encoding="utf-8") as f:
        json.dump({"source": src, "image_count": len(originals), "images": originals}, f, ensure_ascii=False)
    print("extracted {} images from {}".format(len(originals), src))
    print("text-only copy: {}".format(dst))
    print("map: {}".format(map_path))


def cmd_restore(args):
    src, map_path, dst = args
    text = read_text(src)
    with open(map_path, "r", encoding="utf-8") as f:
        mapping = json.load(f)
    images = mapping["images"]
    used = [False] * len(images)

    def repl(m):
        idx = int(m.group(2))
        if idx >= len(images):
            raise SystemExit("ERROR: token IMG_PLACEHOLDER_{} has no image in the map {}".format(idx, map_path))
        used[idx] = True
        return images[idx]

    result, count = TOKEN_RE.subn(repl, text)
    missing = [i for i, u in enumerate(used) if not u]
    if missing:
        raise SystemExit(
            "ERROR: placeholders {} were lost or mangled during translation; refusing to write broken output".format(missing)
        )
    write_text(dst, result)
    print("restored {} images ({} tokens replaced) -> {}".format(len(images), count, dst))


def cmd_verify(args):
    src, dst = args
    src_imgs = DATA_URI_RE.findall(read_text(src))
    dst_imgs = DATA_URI_RE.findall(read_text(dst))
    ok = True
    if src_imgs != dst_imgs:
        ok = False
        print("FAIL: images differ between source and translated file")
        print("  source has {} images, translated file has {}".format(len(src_imgs), len(dst_imgs)))
        for i, (a, b) in enumerate(zip(src_imgs, dst_imgs)):
            if a != b:
                print("  image {}: DIFFERS (alt or base64 payload changed)".format(i))
        if len(src_imgs) != len(dst_imgs):
            print("  image count mismatch - images lost, duplicated, or added")
    leftover = TOKEN_RE.findall(read_text(dst))
    if leftover:
        ok = False
        print("FAIL: untranslated placeholders remain in the translated file: {}".format(sorted(set(t[1] for t in leftover))))
    if ok:
        print("PASS: all {} inline images byte-identical, no placeholders left".format(len(src_imgs)))
    else:
        sys.exit(1)


def cmd_plan(args):
    src_dir, dst_dir = args
    missing, stale, ok = [], [], []
    for root, _, files in os.walk(src_dir):
        for name in sorted(files):
            if not name.lower().endswith((".md", ".markdown")):
                continue
            s = os.path.join(root, name)
            rel = os.path.relpath(s, src_dir)
            d = os.path.join(dst_dir, rel)
            if not os.path.exists(d):
                missing.append(rel)
            elif os.path.getmtime(s) > os.path.getmtime(d):
                stale.append(rel)
            else:
                ok.append(rel)
    for rel in missing:
        print("MISSING {}".format(rel))
    for rel in stale:
        print("STALE  {}".format(rel))
    print("summary: {} missing, {} stale, {} up-to-date".format(len(missing), len(stale), len(ok)))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    commands = {"status": cmd_status, "extract": cmd_extract, "restore": cmd_restore, "verify": cmd_verify, "plan": cmd_plan}
    cmd = sys.argv[1]
    if cmd not in commands:
        print("unknown subcommand: {}\n".format(cmd) + __doc__)
        sys.exit(1)
    commands[cmd](sys.argv[2:])


if __name__ == "__main__":
    main()
