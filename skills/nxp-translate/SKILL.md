---
name: nxp-translate
description: >
  Use when translating, completing, verifying or inventorying Chinese article
  versions of an NXP-published PDF (reference manual, safety manual,
  datasheet — any chaptered NXP document); when a chapter needs a
  one-chapter-one-file page; when asked about chapter coverage or a module
  chapter (registers, memory maps, field tables); or when the task involves
  NXP register tables, globally numbered figures, or cropping diagrams from
  an NXP manual PDF. Source PDF and target location are run parameters.
author: melodypapa
license: MIT
repository: https://github.com/melodypapa/uncertainty
version: "1.0.0"
product-version: "1.0.0"
---

# NXP PDF → Chapter Article Translation

Translate or complete Chinese chapter articles from an NXP-published PDF.
**One numbered chapter = one markdown file.** Follow the steps in order; the
conventions live in `references/`, not in this file.

The source is a **PDF with no parsed Markdown mirror**. Everything structural
comes from the PDF outline; everything textual comes from the PDF.

## Run parameters

Every run is anchored on two parameters, taken from the requester or from the
corpus's own ledger — never from this skill:

| Parameter | Meaning |
| --- | --- |
| **Source PDF** | the NXP-published document to translate from (any path) |
| **Target root** | the directory the articles are written to |

All derived artifacts (chapter map, progress ledger) live **inside the target
root**, so multiple documents never collide. This skill names no repository,
folder or file of any specific document.

## Step 0 — Read the law of the land

Read `references/article-format.md`, `references/source-resolution.md` and
`references/chapter-map.md` before writing. If the target root already holds
articles, read at least one neighbouring `<target>/chNN_<slug>/index.md`.

Read the neighbouring page **for syntax only**: front matter, numbering,
figure filenames. A legacy or partial page may carry defects — do not copy
them: empty section bodies, tables cropped as images (`![Table_1](Table_1.png)`),
whole register-description sections dropped, untranslated English paragraphs.
A faithful chapter translation has none of these. When a neighbouring page and
`references/article-format.md` disagree, the reference wins.

## Step 1 — Resolve the source document

Read `references/source-resolution.md`. Summary:

1. The source PDF path is a run parameter. Confirm it is materialised (not a
   Git-LFS pointer) with `file` / `git lfs pull` before relying on it.
2. Use system `python3` with PyMuPDF (`pymupdf` is typically not in an MkDocs
   venv's `requirements.txt`).
3. `doc.get_toc()` is the structural source: the section tree and chapter
   boundaries. Page text is the source for wording. Never re-derive chapter
   boundaries from a page-text search. Outline shapes differ per document —
   `parse_chapters()` accepts chapters at any level and fails loudly when the
   numbers are not contiguous.
4. Run `scripts/extract_chapter.py <pdf> <chapter> --out /tmp/chNN.txt` for the
   chapter dump (section tree, chrome-stripped page text, table grids, caption
   index). `--sections-only` for a fast outline-only census;
   `--target-root <target>` to report the article path.
5. Record the document identity (title, doc ID, revision, date) **as printed
   by the document itself** in the PR text and the corpus's chapter-map header.
   NXP articles carry no `spec:` / `release:` front matter.

Never edit a PDF, never add a `.md` parse beside it, never commit a PDF as
site content.

## Step 2 — Map chapter → target article

Read `references/chapter-map.md`. One source chapter becomes exactly one
article: `<target>/chNN_<slug>/index.md`, zero-padded to the chapter count's
width, slug derived by `slugify()`. Use the corpus's recorded chapter map —
derive it from the outline on the first run (see the reference for the rules
and a worked example), never invent a filename from a chapter title on the
fly. One run consumes one chapter. Never split a chapter across files, never
merge two chapters into one file, and never append a new page at the end of
its nav group.

## Step 3 — Gap analysis before any writing

Compare the article's headings against the chapter's outline section tree:

- **Missing article** → plan a full translation of that chapter.
- **Partial / stub** → plan in-place completion; insert translations where the
  source has them, in source order, and renumber the sections that follow.
- **Covered elsewhere** → confirm the sibling page actually carries it before
  writing a section off; record the mapping.
- **Complete** → report alignment; check for sections the article dropped.

Compare **all heading levels** (`##` through `######`) plus the bold-paragraph
labels used for outline levels deeper than h6. The outline can reach level 10 —
register and debug chapters have dozens of deep sections; comparing only `##`
silently drops them. Do not open figures during gap analysis; it is text-only.

Count the chapter's figures and tables from the caption index in the dump and
record the count. If the requester's description contradicts the source (wrong
length, "no figures", "one table"), say so and follow the source.

The droppable set is document chrome only: cover, contents, revision/release
notes, legal notice, appendices. Everything else that carries content —
including notes, register descriptions, memory maps and field tables —
translates. For a chapter whose dump exceeds ~1500 lines, present the plan and
get confirmation before translating.

## Step 4 — Create the work todo list

Emit an explicit checklist before writing: chapter sections in source order,
figures to crop, tables to rebuild as text (GFM by default; HTML only for
qualified complex structures), register entries, nav registration if the
target belongs to a site, landing-page update, verification commands. If the
target directory does not exist, create it first.

A full document cannot land in one session. On the first run create the
persistent ledger described in `references/chapter-map.md` (`<target>/TODO.md`,
`<target>/sync-todo/`), excluded from any site build via `exclude_docs` when
the target is inside an MkDocs `docs/` tree, and record each chapter's status.
**Resume rule:** take the first unfinished row in chapter order; do not
re-derive scope or re-ask decisions already recorded in the row.

## Step 5 — Translate in place

- **The main session translates — never a subagent**, sequentially, regardless
  of chapter length. Read-only subagents may do censuses or verification.
- Faithful translation of NXP's own wording, not a summary. Translate the full
  chapter: chip-specific information, overview, memory map, register
  descriptions, functional description, initialization and application
  information.
- Keep technical identifiers, register names, bit-field names and hex values
  untranslated; bold the English term on first mention, Chinese gloss in
  parentheses. Repair the PDF text layer's underscore splits (`PIT 0 _` →
  `PIT_0`) before writing.
- **Numbering:** drop the chapter number, keep the remaining components, heading
  level = (number of remaining numeric components) + 1. `45.1` → `## 1.`,
  `45.1.1` → `### 1.1.`, `44.4.3.2` → `#### 4.3.2.`. **Clamp at `######`** —
  deeper outline levels become a bold paragraph `**8.2.3.2.3.1.3.1. 锁定**`,
  never `#######`. Numbering is contiguous.
- **Never write `# ` in the body** (front-matter `title` is the only h1).
- Source `NOTE` → `**注意：**`, `CAUTION` → `**警告：**`.
- **Tables: every table becomes text.** GFM by default (header row + `| --- |`),
  including memory maps, field tables and register summaries. Never crop a
  table as an image. Expand merged cells by repeating the spanning value in
  each row of the block. Stitch tables split across pages (`Table continued...`
  / `Table continues...`) into one grid, dropping the repeated header. A table
  the detector flattened is rebuilt from the PDF layout, still as text. The
  narrow HTML exception (block content in cells, ambiguous multi-tier header,
  meaningful spanning cells) is in `references/article-format.md` §Tables.
- Register subsections keep the source order: name + offset, `Function` prose,
  `Diagram` bit-field bar, `Fields` table. Bit ranges, reset values and offsets
  match the source exactly; the `Fields` table matches the source row for row.
- Intra-article register links: the chapter's memory-map table links each
  register-name cell to the register's own subsection, restoring the source
  PDF's own hyperlinks. Run `scripts/link_registers.py --apply <article>`
  once the article is complete (`--list` for the census; idempotent). See
  `references/article-format.md` § Cross-references.
- Figures: every content figure embeds, cropped and referenced without caption
  text (`![Figure_256](Figure_256.png)`).

**Precedence.** The conventions in `references/` are the default. When the
requester waives one — keep source numbering, skip figures, summarise tables,
"add nav later", "I'll check the build" — say what the waiver costs and take it
only as an explicit instruction; never silently drop a figure, a table row, a
register, an empty section, the nav entry or the landing link, and never copy a
section from a neighbouring article to fill a gap.

## Step 6 — Produce the figures

Read `references/article-format.md` for naming. Figures only: crop from the
source PDF into the article directory, keeping the source's **global** figure
number (`Figure_256.png`, `Figure_260.png`) so the figure can be traced back.
Figures are vector drawings — crop with `scripts/recrop_figure.py` (a naive
union of the page's drawings ships body text when the page top carries
NOTE/CAUTION decorations; the script's body-text-band recipe prevents that)
and VERIFY the PNG: no body text, heading, NOTE or caption inside it. When a
page defeats the automatic recipe (tables fused onto waveforms, text-heavy
lead-ins, prose directly above the diagram), use the manual fallback:
`recrop_figure.py --band` to read the boundaries, then `--manual X0 Y0 X1 Y1`
— and verify the result the same way.
Unnumbered register `Diagram` bars are not numbered figures: they carry a
`Diagram` label above and a `Fields` label below, with no caption. Crop them
with `scripts/recrop_diagram.py`, which anchors on the register's numbered
section heading (a page can carry two bars), clips the first `Diagram` block
below it, and ends at the `Fields` label — or, when the Fields table starts on
the next page, at the bar's last `Reset` row. **Never let a clip run to the page
bottom**: the running footer sits there and would be shipped inside the PNG.
Bit-field bars, block diagrams and timing diagrams stay images; anything with
rows and columns is a table.

After the PNGs exist, run the crop gate and act on its output:

```bash
python3 <path-to>/nxp-translate/scripts/check_figure_crops.py <article-dir>
```

It **fails** on `BLANK` / `LEAD_WS` / `TRAIL_WS` (reliable) and lists
`REVIEW_EDGE` candidates — a thin band at the image edge separated from the
figure by a gap. That band may be the page header/footer, but a bit-field bar's
own `Bits`/`Reset` rows have the same geometry, so it is a pointer to **open and
confirm**, not a verdict (`--strict` upgrades it to a failure). Fix direction:
if the figure content is intact and only footer/whitespace is present, **trim**
the PNG at the gap; if content is missing (a cut bar), **re-crop** from the PDF
with `recrop_diagram.py` / `recrop_figure.py`. No OCR-free profile can separate
a bar's own rows from page chrome, which is why the final check is visual.

Unnumbered register `Diagram` bit-field bars use `Diagram_<slug>.png`
(`Diagram_sc.png`), with a numeric suffix on collision. Never name a figure
`Table_<n>.png`. Legacy `Table_1.png` in a directory you are already editing is
converted to a text table in the same run: delete the PNG and its reference
once the translated table is verified against the source, and only if nothing
else links to it.

## Step 7 — Register the page (only when the target belongs to a site)

If the target root is part of an MkDocs site, follow **that site's** existing
registration conventions — where NXP/manual groups live, how section landings
are registered, where a new subgroup goes. The generic pattern:

- `mkdocs.yml` (or equivalent nav config): the corpus's section landing as the
  **unlabeled first entry** of its group (`navigation.indexes`), then the new
  article's `<中文标题>` at the chapter's **source position** (nav is ordered
  by chapter number, not arrival time). Every page must be registered or
  `--strict` fails.
- Section landing page (`<target>/index.md`): front matter, one intro sentence,
  `## 文章` link list grouped by the document's group headers, then
  `## 相关内容`.
- Every page registered; a strict build passing with an unregistered page
  means the page is orphaned.

**Offline / output-dir mode.** When the requester asks for output to a
directory outside any site, for an inventory, or explicitly says "don't modify
the repo", produce only the articles/dumps there and **skip Steps 7–9**. Evals
use this mode. Never claim the site was updated when it was not.

## Step 8 — Verify (two-phase gate)

Phase A (mechanical, all must pass):

```
python3 <path-to>/nxp-translate/scripts/check_tables.py <target>
python3 <path-to>/nxp-translate/scripts/check_figure_crops.py <target>   # trim/re-crop anything it fails
python3 <path-to>/autosar-translate/scripts/check_indexes.py   # when the target lives in the autosar-managed site
python3 <path-to>/autosar-translate/scripts/check_heading_lang.py <article>
# when the target belongs to an MkDocs site, that site's strict build, e.g.:
/tmp/mkdocs-venv/bin/python -m mkdocs build --strict --site-dir /tmp/mkdocs-check
```

Plus: every `![](...)` target exists in the article directory; no `![Table…]`
image left; no `# ` in the body; every `## ` heading is Chinese with the source
number; numbering continuity at every level (`### 7.10` implies `### 7.9`,
`## 3.` implies `## 2.`); no untranslated English paragraph; no empty section
body; and a **file → nav orphan check** for all `<target>/ch*/index.md` pages
when the target belongs to a site (a strict build only checks nav → file, not
the reverse). Also: bold markers balanced on every line (no odd `**` count),
and every 「参见 X」 pointing at another chapter is a Markdown link to the
target article path from the corpus's chapter map (forward links to
untranslated chapters allowed; see `references/article-format.md`
§ Cross-references). `check_heading_lang.py` is AUTOSAR-tuned and blind to
bold-paragraph deep labels, so it is a tripwire, not the whole check.
`check_tables.py` enforces four rules mechanically: (1) every block of pipe
lines carries a header row + `| --- |` separator — without them GFM renders the
rows as one soft-joined run-on paragraph (a corpus once shipped 11 chapters
this way, one alone losing 52); (2) bold balance — a stray `*` outside `**`
pairs renders as a literal asterisk (`**xxx***`); (3) heading level = numeric
depth + 1; (4) no Markdown markup in front-matter titles (`**` renders
literally in the h1, browser tab and nav). Checked, never eyeballed. The
memory-map register links come from `link_registers.py --apply` — verify with
`--list` (a second `--apply` must change 0 lines). `check_figure_crops.py`
fails on blank or untrimmed crops and lists `REVIEW_EDGE` candidates; open every
candidate and confirm it holds only the figure — never the page header/footer.

Phase B (fidelity): walk the chapter section by section — each outline section
has a translation, each register/figure/table is present, row sets, bit ranges,
register offsets and reset values match the source, and deprecated Chinese-only
wording is not used where the source is a proper noun. When comparing Fields
tables programmatically, cut each section's text at the next section's heading
line, never at the TOC's page boundary: a register's Fields table often sits
below the next section's start page, and the `Fields` block on a section's own
start page may belong to the previous register.

Report both phases with concrete evidence; do not claim completion without the
verification output. Run the gate even when the requester says they will verify
it themselves — Phase A is the author's responsibility, not a hand-off.

## Step 9 — Repository workflow (only when the target lives in a repo)

Follow the host repo's own conventions for branching, issue/PR language and
commit messages. Baseline rules: feature branch, English issue and PR text,
`docs:` commit (a PR that creates or changes the skill itself is `feat:`), the
quality gate from Step 8 before every commit, and **no co-work attribution**
(never add `Co-Authored-By:` / "Generated with …" footers or any mention of the
agent/session). PR body: lead with a summary, group changes per area (article /
skill+script / other), end with a verification list including the gate results.
Merge through a PR when the default branch is protected.

## Common mistakes

- Inventing a filename from the chapter title instead of using the corpus's
  chapter map, or omitting the `chNN_` prefix / wrong zero-padding width.
- Keeping the source chapter number (`## 43.1.`) instead of restarting at 1.
- Writing `#######` for an outline level deeper than h6 instead of a bold
  paragraph.
- Cropping a table as `Table_<n>.png`, or leaving a legacy table image in
  place while editing the article — tables are text.
- Emitting table rows without the header row and `| --- |` separator (a GFM
  table does not exist without them — the rows render as one run-on
  paragraph); run `check_tables.py`, do not eyeball it.
- Writing a heading whose `#` count does not match its numeric depth
  (`### 1.7.1.` for a 3-component number) — the gate catches it.
- Merging or dropping `Reserved` rows in a Fields table, or renaming a field
  away from the source Fields table (e.g. to the Diagram's label): the row set
  must match the source row for row. When the document self-contradicts
  (Fields vs Function prose vs Diagram), follow Fields + Diagram and record
  the conflict.
- Putting Markdown markup (`**`) in a front-matter title — it renders as
  literal asterisks.
- Linking a chapter to itself (`[芯片特定的 X 信息](index.md)`) — same-article
  references stay plain text.
- Copying PDF text-layer artifacts: non-breaking spaces (U+00A0), split hex /
  binary values (`0000 0000h` → `0000_0000h`), stray underscores that exist in
  the source itself (`AMBA_ AHB`) — verify against a rendered page region and
  repair.
- Pasting PDF text with split identifiers (`PIT 0 _`, `0000 0000h _`) or broken
  table cells unrepaired.
- Treating a legacy partial page as the standard and leaving empty sections or
  dropping register descriptions.
- Using Arm conventions: `Figure<ch>-<n>.png`, chapter-scoped table numbers,
  chapter-scoped figure numbering, or cropping register `Diagram` bars as
  tables.
- Letting a crop rectangle run to the page bottom: the running header/footer
  (title, `© … NXP B.V.`, revision line) gets baked into the PNG. A crop holds
  the figure only.
- Cropping a register `Diagram` bar to the page bottom, or cutting it at the
  wide gap between its two halves, so the lower `Bits`/`Reset` rows are lost —
  use `recrop_diagram.py`, which ends at `Fields` (or the last `Reset` row).
- Shipping an untrimmed crop with a large blank band (a re-crop artefact);
  `check_figure_crops.py` fails it.
- Translating the cover, contents, release notes or legal notice.
- Adding the page without the nav entry, or adding it at the end of the group
  instead of its chapter position.
- Claiming the site was updated in offline mode.

## Red flags — stop and start over

- "One chapter is small, I'll skip the outline" — the outline is structural.
- "I'll summarise the register tables" — a dropped row is a defect.
- "The legacy pages do it this way" — they are partial and carry defects.
- "Tables are easier as images" — never.
- "I'll check the build later" — Phase A is the author's job.
- "This is different because it's an NXP doc" — it is exactly what this skill
  is for.
- "The outline doesn't parse, I'll eyeball chapter boundaries" — stop and
  inspect `doc.get_toc()`; never improvise boundaries from page text.
