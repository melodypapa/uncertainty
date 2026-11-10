---
name: arm-translate
description: >
  Use when translating, completing, verifying or inventorying the Chinese Arm
  reference articles of an Arm document series (Cortex TRM, Armv7-M/Armv8-M
  architecture manuals, SDEN errata notices — any Arm-published document with
  a paired Markdown mirror + PDF); syncing a source chapter into a topic
  article; answering coverage questions about MPU, cache, memory system,
  programmers model, exception model, instruction set or system address map;
  or merging split chapter pages and registering a glossary. Corpus-agnostic:
  the source corpus and the target location are run parameters.
author: melodypapa
license: MIT
repository: https://github.com/melodypapa/uncertainty
version: "1.0.0"
product-version: "1.0.0"
---

# Arm Document → Article Sync

Translate or complete the Chinese articles of an Arm document series from the
Arm document corpus (paired ima-parsed Markdown + original PDF). Follow the
steps in order; the conventions live in `references/`, not in this file.

## Run parameters

Every run is anchored on two parameters, taken from the requester or from the
corpus's own ledger — never from this skill:

| Parameter | Meaning |
| --- | --- |
| **Source corpus** | the paired `.md` + `.pdf` mirror holding the Arm document(s) to translate from |
| **Target root** | the directory the articles are written to (`<target>/<document>/<topic>/index.md`) |

Per-corpus artifacts (article↔source mapping, sync ledger, glossaries) live
**inside the target root**, so multiple document series never collide. This
skill names no repository or folder of any specific corpus; the cortex corpus
serves as the worked example in `references/examples/`.

## Step 0 — Read the law of the land

There is no `STANDARD.md` for the Arm corpus. The law is the existing articles
plus `references/article-format.md`. Read that reference before writing, and
read at least one neighbouring article in the same `<target>/<document>/` tree
so the new page matches its tone and structure.

## Step 1 — Resolve the source document

Read `references/source-resolution.md`. Summary:

1. The source corpus location is a run parameter. Primary source is the
   ima-parsed Markdown paired with the original PDF of the same doc ID and
   revision. Use the `.md` for text, the `.pdf` for figures, and the `.pdf` to
   read the cell grid of a table the parse flattened.
2. Confirm the pairing from the corpus's sync-todo **Sources table** — it
   records the doc ID, revision, media size and which pairs are complete.
   Filenames do not always match between `.md` and `.pdf`.
3. The `.md` files are read-only; never edit them. Never translate from the PDF
   text layer when a `.md` exists — the parse is the structural source.

## Step 2 — Map source → target article

Read `references/mapping.md` for the article ↔ source-chapter mapping rules.
The evidence is the figure/table number in the source (`Figure8-*` ⇒ chapter 8,
`TableB3-*` ⇒ appendix B3); when the numbering does not prove it, match
section headings before writing.

A source chapter becomes one article at
`<target>/<document>/<topic>/index.md`, where `<document>` is the source
document series folder. First level is the source document, second level the
topic; never file two documents in one folder. Propose the directory name to
the user when a topic straddles two chapters or could be split, and propose a
new document folder name (matched to the existing lower_snake_case series)
when opening a source document that has no series yet.

## Step 3 — Gap analysis before any writing
Compare the article's `## ` headings against the source chapter's section list:

- **Missing article** → plan a full translation of that chapter.
- **Partial / stub** → plan in-place completion; insert translations where the
  source has them, in source order, and renumber the sections that follow.
- **Covered elsewhere** → before writing off a section as "another article has
  it", confirm the sibling page actually carries it and record the mapping.
  Overview, modes and monitor sections stay on the chapter page even when the
  sibling page covers the deeper topic.
- **Complete** → report alignment; check for sections the article dropped.

The droppable set is the document chrome only: cover page, proprietary notice,
contents, document history, feedback and index. Everything else that carries
content — including notes, register descriptions and "Related references" —
translates. For a source chapter longer than ~1500 lines, present the plan and
get confirmation before translating.

Gap analysis is text-only: compare Markdown headings, never open figures.
Count the chapter's figures and tables from the source heading/text before
writing and record the count; if the requester's description of the chapter
contradicts the source (wrong length, "no figures", "one table"), say so and
follow the source.

## Step 4 — Create the work todo list

One run consumes one article. Emit an explicit checklist before writing:
chapter sections in source order, figures to crop, tables to rebuild as text
(GFM by default; HTML only for qualified complex structures), register entries,
nav registration if the target belongs to a site, landing-page update,
verification commands. If the user names an article with no target directory,
create the directory first.

## Step 5 — Translate in place

- **The main session translates — never a subagent**, sequentially, regardless
  of chapter length. Read-only subagents may do censuses or verification.
- Faithful translation of Arm's own wording, not a summary. Keep technical
  identifiers, register names, bit-field names and instruction syntax
  untranslated. Terminology and expression follow
  `references/article-format.md` §Wording and markup (aligned with the
  autosar-translate regime): Chinese gloss first with the bolded English term
  in full-width parentheses on first mention, one rendering per term across
  the document series, every heading level translated (identifier-titled
  headings exempt), angle-bracket placeholders as `&lt;…&gt;` outside code
  fences.
- Renumber the source chapter to `## 1.` and mirror its relative structure
  (`### 1.1.`, `#### 1.1.1.`). Numbering restarts at 1 in every article.
- Never write `# ` in the body (front-matter `title` is the only h1).
- Keep code and instruction snippets in fenced blocks tagged `arm`
  (`MCR p15, 0, <Rt>, c6, CRm, op2`), verbatim from the source.
- Source notes render as `**注意：**` paragraphs.
- **术语与定义（term entries）render as a bold English head + `>` blockquote
  definition** — the autosar glossary/definition form, never a GFM table and
  never a bullet list:

  ```markdown
  **Address Area**
  > 逻辑地址空间中的连续内存区域，通常将多个物理存储器扇区组合成一个逻辑地址区域。
  ```

  The English term is the head and stays verbatim (a term is a key, not
  prose); the head carries no Chinese and is immediately followed by the
  blockquote — never a bold paragraph with a plain paragraph under it. The
  definition is the translated source sentence, opening with `中文（English）：`
  in an unbolded parenthetical when the source names the term. Entry order and
  entry set match the source exactly (no entry added, merged, split or
  dropped). A source two-column *Term | Definition* table, a source prose
  definition list and the source's `## Term` + paragraph layout all translate
  into this form. A later mention in body prose is inline: 中文（**English**）
  on first mention, the bare term after.
- Register subsections keep the source's order: name, description,
  `**使用限制**`, access table (`| EL0 | EL1 | EL2 |`), field table.
- Tables: every table translates to text. GFM is the default (header row +
  `| --- |`), including bit-field, access-rights, encoding and register-summary
  tables. Never crop a table as an image, merged cells included. In GFM tables,
  expand a merged cell by repeating the spanning value in each row of the block,
  so every row reads on its own; leave a cell blank only where the blank is
  unambiguous. A table the parse flattened is rebuilt from the PDF layout, still
  as text.
  A narrow HTML exception applies when GFM cannot carry the structure (block
  content in cells, an ambiguous multi-tier header, or meaningful spanning
  cells) — see `references/article-format.md` §Tables for the exhaustive
  criteria and the raw-HTML inline-markup requirement.
- Figures: every content figure in the chapter embeds, cropped and referenced
  without caption text (`![Figure8-2](Figure8-2.png)`); crops carry a margin
  (~4% of the larger dimension per side, min 6pt — never flush, see
  `references/article-format.md`). When the source has no figure number, use a
  synthetic `Figure<chapter>-<n>.png` name and record it in the queue note.

**Precedence.** The conventions in `references/` are the default. When the
requester waives one — keep source numbering, skip figures, summarise tables,
"add nav later", "I'll check the build" — say what the waiver costs and take it
only as an explicit instruction; never silently drop a figure, a table row, a
register, the nav entry or the landing link, and never copy a section from a
neighbouring article to fill a gap.

## Step 6 — Produce the figures

Read `references/article-format.md` for naming. Figures only: crop from the
source PDF with PyMuPDF into the article directory (`Figure<chapter>-<n>.png`),
keeping source numbering so the figure can be traced back — expand the clip by
a margin (~4% of the larger dimension per side, min 6pt, clamped to the page)
so the crop is never flush with its content. Figures that are
bit-field bars, block diagrams or timing diagrams stay images; anything with
rows and columns is a table and goes through Step 5 as text.

Legacy directories may mix `Figure4_77.png` and `FigureA3-1.png` — never rename
existing files, only keep new ones consistent. A legacy `Table<chapter>-<n>.png`
in a directory you are already editing is converted to a text table (GFM by
default, HTML when the structure qualifies) in the same run: delete the PNG and
its reference once the translated table is verified against the source, and only
if nothing else links to it.

## Step 7 — Register the page (only when the target belongs to a site)

Follow **that site's** existing registration conventions for where the Arm
groups live and how they are labelled (short labels; doc IDs live on the
landing pages, not in the nav). The generic pattern:

- Nav config: add the page under the source document's group; insert at the
  page's **source chapter position** — nav groups and landing lists are
  ordered by chapter number (ch1 → ch14 → appendix), not by arrival time.
  Never append a new page at the end of the group; a concept article takes the
  position of the closest chapter it supports.
- `<target>/<document>/index.md`: add the numbered link to the document landing
  page; the corpus root index only links the document landing pages.
- **One source chapter = one article.** When a chapter is currently split
  across two directories, merge them into a single `index.md`: keep the first
  article's directory and title, append the second article's sections with
  their numbers shifted by the first article's last chapter number, move its
  images, delete the retired directory, and add `redirect_maps` entries for
  every retired `…/index.md`. Internal `#anchor` links inside moved sections
  must be renumbered with the new heading number. Fix any reference to the old
  paths in the article tree and in the sync-todo ledger.
- A merged chapter page must still be **chapter-complete**: the source's
  overview, mode/state and monitor sections belong on the chapter page even
  when the chapter also points at sibling pages for other topics. Insert them
  at their source position and renumber every later section, or the page
  silently drops the chapter's own front matter.
- **The glossary page carries real term entries, not a link**:
  `<target>/<document>/glossary/index.md`, `title: "术语表 (Glossary)"`,
  registered last in the document group (appendix position). It translates the
  source document's own glossary chapter in the Step 5 term-entry form
  (`**Term**` + `>` definition), alphabetically sectioned (`## A` … `## Z`)
  when the source is alphabetical, otherwise in source order.
  - **One term is defined once**: a term already defined on the page is never
    re-defined with different wording; a second source document adding the same
    term appends a 来源 line, not a second definition. The release/document
    attribution goes in the page intro or the 来源 line — state the doc ID and
    revision once, not per entry.
  - **Every translation run extends it** in the same commit: the run's new
    architecture terms and abbreviations are added, so the page reflects the
    whole series rather than a single article.
  - Terms the source document does not define stay out of the page; the
    document's own glossary row set is the boundary, and the single link to the
    Arm Glossary stays as the pointer to terms outside it.
  - **A document with no glossary chapter keeps the link-only page** — it
    states that the source has no Glossary chapter and links the Arm Glossary.
    Do not invent entries for such a document; the rule above applies only
    where the source has a glossary to translate.
- Concept articles that cite external sources stay outside this skill.

## Step 8 — Verify (two-phase gate)

Phase A (mechanical, all must pass):

```
python3 <path-to>/autosar-translate/scripts/check_indexes.py --root <site-root>
python3 <path-to>/autosar-translate/scripts/check_heading_lang.py <article> [...]
# when the target belongs to an MkDocs site, that site's strict build, e.g.:
/tmp/mkdocs-venv/bin/python -m mkdocs build --strict --site-dir /tmp/mkdocs-check
```

`check_heading_lang.py --site` sweeps only the AUTOSAR Type A articles of its
target; for an Arm corpus you must pass the article paths explicitly.

Plus: every `![](...)` target exists in the article directory; no `![Table…]`
table image left in the article (each table is either a GFM table with a header
row and `| --- |`, or an HTML `<table>` with `<thead>`/`<th>` headers); HTML
table cells must contain no unprocessed Markdown (`**…**`, `[…](…)`); no `# `
in the body; every heading at every level carries Chinese (identifier-titled
headings exempt — `check_heading_lang.py` above is the tripwire); no
untranslated English paragraph left behind.

Terminology gate (same Phase A pass):

- every glossary/definition entry is a `**English term**` line immediately
  followed by a `>` blockquote definition — no `| 术语 | 定义 |` GFM table and
  no `- **术语**（…）。` bullet list carries a definition;
- `grep -c '^\*\*' <glossary page>` shows the run's new terms were added, and
  `grep -n '^\*\*<Term>\*\*$'` finds each of them;
- no term is defined twice on the glossary page with different wording
  (`grep` the term head, then compare the definitions);
- the same term renders identically across the series: grep the documented
  Chinese rendering in the sibling articles and compare.

Phase B (fidelity): walk the chapter section by section — each source section
has a translation, each register/figure/table is present, row sets and bit
ranges match the source, and deprecated Chinese-only wording is not used where
the source is a proper noun. Also check **numbering continuity**: every numbered
heading has its predecessor (`### 7.10` implies `### 7.9`, `## 3.` implies
`## 2.`); a jump is a defect even when the text reads fine.

Report both phases with concrete evidence; do not claim completion without the
verification output. Run the gate even when the requester says they will verify
it themselves — Phase A is the author's responsibility, not a hand-off.

## Step 9 — Repository workflow (only when the target lives in a repo)

Follow the host repo's own conventions for branching, issue/PR language and
commit messages. Baseline rules: feature branch, English issue and PR text,
`docs:` commit, the Step 8 gate before every commit, and **no co-work
attribution** (never add `Co-Authored-By:` / "Generated with …" footers or any
mention of the agent/session). Skill rule edits live in the skills submodule
and need a separate commit there (plus a submodule-pointer bump in the parent
when the parent tracks it). Merge through a PR when the default branch is
protected.

## Common mistakes

- Renumbering the article to the source chapter number (must restart at 1).
- Cropping a table as `Table<ch>-<n>.png` because the cells are merged, or
  leaving a legacy table image in place while editing the article — tables are
  text (GFM with spans expanded row by row, or HTML for qualified complex
  structures).
- Using an HTML table for a plain grid GFM can carry, or leaving `**bold**` /
  Markdown links inside HTML cells — they render literally.
- Pasted PDF text with broken table cells or hyphen splits left unrepaired.
- Figures skipped "because the parse has no caption" — the figure still embeds.
- Rendering a term entry as a bullet list, a `| 术语 | 定义 |` table, a bold
  paragraph over a plain paragraph, or a `## Term` heading — it is a bold
  English head with the definition in a `>` blockquote.
- Translating the proprietary notice or document history.
- Adding the page without the nav entry (strict build passes, page is orphaned).
- Treating an M-profile architecture manual as another series' architecture
  manual — each core series follows its own TRM plus its own architecture
  manual; they are separate document series.
