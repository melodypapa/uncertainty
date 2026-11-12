# Source resolution — the NXP PDF

The source of a run is **one NXP-published PDF** (reference manual, safety
manual, datasheet — anything chaptered that NXP distributes). Its path comes
from the requester or the corpus ledger; this skill hardcodes no location, file
name or document identity. The source is **read-only**.

**NXP documents have no parsed Markdown mirror.** The PDF is the sole source
for both text and figures. Never look for a `.md` beside it, and never create
one from the PDF text layer as a source — the dump produced by
`scripts/extract_chapter.py` is a per-run working file, not a source.

## Before relying on the file

```bash
file <pdf>        # must say "PDF document", not "ASCII text"
git lfs pull      # only if the file is an unresolved LFS pointer
```

`.gitattributes` often tracks PDFs through Git LFS, so a fresh clone may hold a
~130-byte pointer instead of the real file. `extract_chapter.py` exits 2 when
the file is missing or is a pointer.

**Interpreter.** PyMuPDF (`import pymupdf`) is required. It is usually present
in the system `python3` but is **not** part of an MkDocs venv's
`requirements.txt`. Run the helper with system `python3` or install PyMuPDF
into the venv; never add `pymupdf` to a site's `requirements.txt` — site builds
never read the source corpus.

## The outline is the structural source

`doc.get_toc()` is the authority for chapter boundaries and the section tree;
page text is the authority for wording. The outline's shape varies per document
(chapters at different levels, dots after chapter numbers or not, different
group-header conventions) — `parse_chapters()` in the helper handles all of
these and fails loudly when the detected chapter numbers are not contiguous.
Never re-derive chapter boundaries from a page-text search.

- Section headings are chapter-scoped (`44.1`, `44.1.1`, `44.4.3.2`); outlines
  can reach level 10 — `references/article-format.md` clamps deep levels to h6.
- Chapter page range = outline start → (next chapter's start − 1); the helper's
  `chapter_range()` ends the final chapter before trailing matter
  (appendices / release notes / legal information).

Use the helper instead of re-deriving any of this:

```bash
python3 <path-to>/nxp-translate/scripts/extract_chapter.py <pdf> <N> --out /tmp/chN.txt
python3 <path-to>/nxp-translate/scripts/extract_chapter.py <pdf> <N> --sections-only
python3 <path-to>/nxp-translate/scripts/extract_chapter.py <pdf> <N> --target-root <target> --json
```

The dump carries the section tree, cleaned page text with page markers,
detected table grids and the caption index. It never writes anything.

## Reading page text

NXP pages repeat a running header and a footer. The helper strips blocks
outside the content area (`y0 < 62`, `y0 > 740`) plus NXP-universal chrome
lines (`NXP Semiconductors`, `Reference Manual`,
`General Business Information`, `NNNN / NNNNN` page numbers) **and the
document's own running header/footer lines, which it derives automatically**
from the most repeated band lines across a sample of pages — so nothing about
the document's title or revision is hardcoded. The running chapter title in
the header varies per chapter, so it is matched by position, not by string.
**Preserve** `Table continued from the previous page...` and
`Table continues on the next page...` — they sit near those bands but carry
table state.

The PDF text layer splits identifiers at underscores: `PIT_0` arrives as
`PIT 0 _`, `0000_0000h` as `0000 0000h _`. Repair these back to their source
form before translating; never paste the split form into an article. A dropped
or misplaced `_` in a register name, bit range or hex value is a fidelity
defect.

Tables sometimes appear in the raw text as a vertical list of cell values (one
cell per line). Do not read that as prose — use `page.find_tables()` (the
helper already emits the row grids) and, when the detector misses a table,
read the cell grid from the PDF layout and rebuild it as text.

## Tables

- Numbered **globally** (`Table 279.`, `Table 280.`), not per chapter. The
  number is only an identifier in the introducing paragraph; it does not appear
  in the article title or as a caption line.
- `page.find_tables()` works on NXP layouts. Merge continuation pages: drop the
  repeated header row, append the data rows, keep the whole table in one place.
  A table split across pages is one table.
- **Every table becomes text** — GFM by default, raw HTML only for the narrow
  exception in `references/article-format.md`. Never crop a table as a PNG.

## Figures

- Numbered **globally** (`Figure 256.`, `Figure 260.`). The caption sits
  **below** the drawing.
- Figures are **vector drawings**, not embedded images: `page.get_images()` is
  empty on figure pages while `page.get_drawings()` returns many objects.
  Extract embedded XObjects and you get nothing. Crop by rendering a clip
  rect — **the clip must contain only the figure**. The naive "union of all
  drawings on the page" is wrong: NOTE/CAUTION pills and their divider rules
  are vector drawings too, so their rects merge the figure's bbox with the
  body text above it and the crop ships that text (observed on ch059 WKPU:
  a NOTE block, a section heading and two paragraphs above the diagram).
  Use `scripts/recrop_figure.py`, which implements the accurate recipe:

  1. caption_y = position of the `Figure N.` caption;
  2. body text above the caption = text blocks with >40 chars AND >380pt
     width (figure labels can be long but never span the text column);
  3. the figure band starts below the LAST such body block, walking upward
     until the band contains >= 5 drawings (a NOTE sitting between the figure
     and its caption steps past it);
  4. bbox = union of the drawings inside the band, grown with every text
     block that intersects it or vertically overlaps it without body width —
     figure labels can sit just outside the drawing union (a bus label left
     of the diagram);
  5. margins: ~4% of the larger dimension (min 6pt) left/right/bottom; the
     top margin is capped at 6pt and clamped below the body-text boundary so
     NOTE borders cannot re-enter;
  6. render at >= 2x zoom, then VERIFY the PNG: no body text, no heading, no
     NOTE and no caption may appear in it.

```bash
python3 <path-to>/nxp-translate/scripts/recrop_figure.py <pdf> 260 <page> Figure_260.png
```

**Unnumbered register `Diagram` bars.** These have no `Figure N.` caption: a
`Diagram` label sits above the bit-field bar and a `Fields` label below it.
Crop with `scripts/recrop_diagram.py`:

```bash
python3 <path-to>/nxp-translate/scripts/recrop_diagram.py <pdf> Diagram_ctrl.png \
    --pages <A> <B> --heading 'Control \(CTRL\)'
```

The recipe: find the register's numbered section heading in the chapter's page
range, take the first `Diagram` block **below that heading** (a page can carry
two register bars — the heading disambiguates), and clip from `heading+18pt` to
the following `Fields` label `-15pt`. When the `Fields` table starts on the next
page, the bottom is the bar's **last `Reset` row `+8pt`**, capped above the page
content band (≈740pt). **Never clip to the page bottom:** the running footer
(copyright + revision) sits there and would be baked into the PNG, and a bar
crop that starts too low loses its top `Bits` row — both are silent defects.

After cropping, run `scripts/check_figure_crops.py <article-dir>`: it fails on
blank/untrimmed images and lists `REVIEW_EDGE` candidates to open by hand (a
bar's own `Bits`/`Reset` rows look like chrome to a row profile, so the final
confirmation is visual, not automatic).

**Manual fallback.** Some pages defeat the automatic recipe: tables fused
directly onto waveforms, text-heavy lead-ins (terminology table + bullets +
heading), prose directly above the diagram, two-figure pages. Observed on the
S32K5 corpus (ch070 F340/F341, ch071 F342, ch038 F157, ch040 F160, ch055
F260, ch069 F311/F320/F324). For those, set the boundaries by hand:

```bash
# step 1: render the whole content band above the caption for boundary reading
python3 <path-to>/nxp-translate/scripts/recrop_figure.py <pdf> <N> <page> band.png --band
# step 2: render the hand-set clip (PDF coordinates read off the band)
python3 <path-to>/nxp-translate/scripts/recrop_figure.py <pdf> <N> <page> Figure_N.png --manual X0 Y0 X1 Y1
```

Read the top boundary off the band (below the last table row / heading /
prose), keep the full content width when labels sit beside the diagram
("Peripheral bus" sits left of the WKPU diagram), and VERIFY the result:
complete labels, nothing above the boundary. Two crops typically need a
second boundary raise (the first top clip cuts the waveform's top row or a
lane header). Record the manual coordinates in the PR text.

Bit-field bars inside register descriptions carry an unnumbered `Diagram`
label rather than a `Figure N.` caption; they are still figures and use
`Diagram_<slug>.png` (see `references/article-format.md`).

Block diagrams, bit-field bars and timing diagrams stay images. Anything with
rows and columns is a table.

## Register descriptions

NXP register descriptions have a fixed shape. Keep it:

1. A memory-map table: `Offset | Register | Width (In bits) | Access | Reset value`.
2. One subsection per register: `Offset`, prose under `Function`, the
   `Diagram` bit-field bar, then a `Fields` table (`Field | Function`, with bit
   ranges like `31-28`).
3. Access information comes from the memory map; bit ranges, reset values and
   offsets stay exactly as printed (`0h`, `98h`, `0000_0000h`, `位 [5:3]`).

Register subsections can be very long (hundreds of pages). They are part of
the chapter and translate; they are not droppable chrome.

## Notes and cautions

`NOTE` renders as `**注意：**` + translated body, `CAUTION` as `**警告：**`.
Both carry content and translate.

## Recording the document identity

Read the document's own identity — title, document ID, revision, date — from
its cover page and running headers (the helper's dump header carries what it
could derive). Record it in the PR text and in the header of the corpus's
`chapter-map.md`. NXP articles carry **no** `spec:` / `release:` front matter
(that convention belongs to `docs/autosar/`). When a new revision of the same
document lands, re-run the chapter inventory before translating against it.

## Constraints

- The source is read-only. Never edit a PDF, never add a `.md` parse beside it,
  never commit a PDF as site content.
- One run consumes one chapter. Do not read a thousand-page document end to
  end to translate one chapter.
- When a document's outline defeats `parse_chapters()` (no contiguous numbered
  chapters), stop and inspect `doc.get_toc()` manually; do not improvise
  chapter boundaries from page text.
