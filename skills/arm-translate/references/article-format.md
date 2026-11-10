# Cortex article format

Derived from the translated Arm article corpus. Match the neighbouring
article in the same tree; this file records the rules that hold across them.

## Front matter

Only `title`, quoting the Chinese title with the English term in full-width
parentheses when the source chapter title is a proper term:

```yaml
---
title: "内存保护单元（Memory Protection Unit）"
---
```

Short implementation chapters may use Chinese only (`"Cortex-M7 程序状态寄存器"`).
Never add `spec:`, `release:` or tags — that convention belongs to `docs/autosar/`.
The gloss order stays Chinese-first even though `docs/autosar/` titles are
English-first: an AUTOSAR module name is a product identifier, an Arm chapter
title is a descriptive phrase. Do not "realign" the order.

## Body structure

- One or two intro sentences mirroring the source chapter's opening
  ("本章介绍 **MPU**。"), then the translated sections.
- Chapter numbering **restarts at 1** for every article: `## 1. 关于 MPU`,
  `## 2. MPU 区域`, `### 2.1. …`, `#### 4.2.1. …`. The number reflects the
  source's relative structure, not the source's absolute chapter number.
- Never write `# ` in the body — the front-matter title is the only h1.
- Numbering is contiguous: every `## N.` and `### N.M.` has its predecessor. A
  jump (`## 3.` with no `## 2.`, or a `### 7.10` with no `### 7.9`) is a defect,
  not a style choice — fix it even when the page is otherwise complete.
- Preserve the source's section order and nesting; do not invent overview or
  summary sections. A source overview section is not invented content: keep it
  on the chapter page (TRM 2.1, 2.2, 2.5) even when a sibling page carries the
  deeper topic.
- No table of contents, no document history, no proprietary notice, no footer
  banner.

## Wording and markup（术语与表述）

These rules mirror the autosar-translate terminology/expression regime
(`docs/autosar/STANDARD.md` §4–§5) where the corpora overlap; Arm-specific
conventions are marked as such.

- Faithful translation of Arm's wording; technical identifiers stay in English.
- **Term entries use the bold-head + blockquote-definition form** — the same
  form as the autosar glossary/definition chapters, never a GFM table and
  never a bullet list:

  ```markdown
  **Address Area**
  > 逻辑地址空间中的连续内存区域，通常将多个物理存储器扇区组合成一个逻辑地址区域。
  ```

  The English term is the entry head and stays verbatim (a glossary term is a
  key, not prose); the head carries no Chinese, and the entry is a **head line
  immediately followed by the blockquote** — never a bold paragraph with a
  plain paragraph under it. The definition is the translated source sentence;
  when the source sentence names or glosses the term, the definition opens with
  the Chinese rendering and the English term in an unbolded parenthetical
  (`> 架构可见（Architecturally visible）：…` — no `**…**`, because the head
  already bolds it). One blank line between entries; the entry order is the
  source's order, and the row set matches the source exactly — no entry added,
  merged, split or dropped. This replaces both the source's two-column
  *Term | Definition* table, a source prose definition list, and the source's
  `## Term` + paragraph layout.
- **First mention in body prose**: the Chinese gloss first, then the bolded
  English term in full-width parentheses — `直写缓存（**Write-Through caching**）`;
  later mentions drop the parentheses. A sentence that only names a term (no
  gloss, no definition) is not a term entry — keep it inline prose.
- **Bold marks terminology and identifiers only**: the English term inside a
  first-mention gloss, a term entry's head, and register/field mentions
  (`**PRBAR**`, `**SCTLR.M**`). Numbers, units and ordinary prose are not
  bolded — legacy pages over-bold (`**256** 字节`); never copy that into new
  work.
- **One term, one rendering per document series**: a recurring architecture
  term keeps the same Chinese rendering in every article of the series — grep
  the sibling articles and reuse the established rendering before inventing
  one. A term defined in one article is not re-defined word-for-word in
  another; the second article refers to it.
- **Every heading translates, at every level** (`##`–`######`): the title
  carries Chinese. The only exemptions are identifier-titled headings —
  register names (`MPU_RBAR`), instruction mnemonics, exception names — which
  stay verbatim, like the code identifiers above. Prose-looking English titles
  (Overview, Registers, Introduction) are **not** exempt. Enforced by
  `check_heading_lang.py <article>` (Step 8 Phase A).
- Numbers and encodings as in the source: `位 [5:3]`, `0x…`, `0b…`.
- Angle-bracket placeholders in prose (`MPU_RBAR<n>`, `<Rt>` outside a listing)
  render via HTML entities `&lt;…&gt;` — a bare `<n>` is dropped by the browser
  as an unknown tag. Never inside code fences, where the listing stays
  verbatim. In a heading the entity changes the Material slug — sweep inbound
  anchors in the same commit.
- Notes: `**注意：**` followed by the translated note body.
- Cross-references: the source's "see section Bx.y" and "See also" render as
  inline references or `参见：` bullets, renumbered to the article's own
  section numbers and linked to the local anchor; a reference into a chapter
  that lives on a sibling page links there instead.
- Instruction and pseudo-code snippets go in fenced blocks, verbatim, tagged
  `ARM`; C snippets use `C`. Comments inside a listing translate; mnemonics and
  operands do not. (Legacy pages also use lowercase `arm`.)
- Register subsections keep the source skeleton: register name, purpose,
  `**使用限制**`, access table, then field table.

## Tables

- Every table is text, and GFM is the default: a Markdown table with a header
  row and `| --- |` separator, translated cell by cell. Tables are never
  cropped as images — merged cells included.
- **HTML exception (narrow).** A raw HTML `<table>` is allowed only when GFM
  cannot carry the structure without loss or unreadability: cells containing
  block content (lists, code blocks, multiple paragraphs), a multi-tier header
  whose flattened form is ambiguous, or merged cells whose spanning semantics
  carry meaning that repeating values would obscure. A plain row/column grid,
  however wide, stays GFM. These three cases are exhaustive; see the decision
  log below.
- HTML tables must use `<table>` with `<thead>`/`<tbody>`, `<th>` headers with
  `scope="col"` or `scope="row"`, and real `rowspan`/`colspan` for spans.
  Inline markup inside cells must be written as raw HTML (`<strong>`, `<code>`,
  `<a href="…">`) — Markdown is **not** parsed inside HTML table cells even
  with `md_in_html`, so `**bold**` and `[text](url)` would render literally.
  Never paste the source parse's `<table>` markup verbatim; write clean HTML.
- In GFM tables, merged cells are expanded, not mirrored: repeat the spanning
  value in each row of the block so every row reads on its own, e.g. three
  regions sharing one attribute each repeat `RW` instead of one `RW` cell
  spanning three rows.
- In GFM tables, multi-tier headers flatten into one header row that names each
  column (`| 位 | 名称 | 类型 | 复位值 | 描述 |`); the source's two-tier
  `位 / 名称` header becomes two columns.
- Access tables keep the source's three columns:
  `| EL0 | EL1 | EL2 |` with `-` / `RW` values.
- Bit-field bars (`Figure7-1`), block diagrams and timing diagrams are figures,
  not tables — they stay as cropped images.
- No visible `Table x-y:` caption line; the paragraph that introduces the table
  carries it. Legacy `Table<chapter>-<n>.png` images in older directories are
  converted to text tables (GFM by default, HTML when the structure qualifies)
  as those articles are touched.
- Table footnotes carry over: markers as `<sup>N</sup>`, the footnote text as
  `> N …` blockquotes after the table (the autosar convention).

## Figures

- Every content figure of the translated chapter embeds where the source has it:
  `![Figure8-2](Figure8-2.png)` — no caption text, alt text is the source
  figure number.
- The PNG sits in the same directory as `index.md`; no shared `images/` tree.
- Naming: `Figure<chapter>-<sequence>.png`, using the source document's own
  numbering (`Figure8-2`, `FigureB3-1` for an appendix). Legacy directories mix
  `Figure4_77.png`, `FigureA3-1.png` and now-unused `Table9-1.png` — never
  rename existing files. When the source has no figure number (a caption-less
  parse diagram), use a synthetic `Figure<chapter>-<n>.png` and record it in
  the queue note.
- Crop from the sibling PDF with PyMuPDF at a resolution that keeps bitmap text
  legible (scale ≥ 2× page zoom).
- **Leave a margin when cropping (user decision 2026-11-07)** — never crop a
  figure flush to its content: expand the clip rect on all four sides by ~4% of
  the larger of (width, height), minimum 6pt, clamped to the page rect. The
  padding keeps cropped diagrams from rendering edge-to-edge (顶天立地) in the
  page. Equivalent post-processing: pad the PNG with a uniform white border of
  ~2% of its pixel width when the clip cannot be expanded (figure touching the
  page edge):

  ```python
  import fitz  # pymupdf
  page = doc[page_no]
  r = figure_bbox + (-m, -m, m, m)   # m = max(6, 0.04 * max(w, h))
  pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=r & page.rect)
  ```

  The same margin rule applies to any other figure-extraction flow (PPTX
  region crops, image truncation) — a saved figure carries visible whitespace
  around its content. **Converter-extracted PNGs are not exempt**: corpus
  artifacts (`image_*.png`) are typically flush — at review, measure the border
  whitespace of every embedded figure and replace any figure with less than
  ~1% margin by padding it in place (white border, ~2% of pixel width, min
  12px); never leave a flush figure in the article (user decision 2026-11-07).

## Landing pages and navigation

- `<target>/<document>/<topic>/index.md` — one directory per topic, under
  the source document folder (`m7-trm/`, `armv7-m/`, `r52plus-trm/`,
  `armv8-m/`).
- One source chapter maps to exactly one article. Do not split a chapter across
  directories (two articles for ch2's PSR and exception model, a separate MPU
  page for ch6); merge the parts into one page, renumber the appended sections,
  and keep old URLs alive through `redirect_maps`.
- The document glossary goes in `<target>/<document>/glossary/index.md` with
  the `title: "术语表（Glossary）"`, registered last in the document group
  (appendix position). It holds the **translated source glossary** in the
  §Wording term-entry form (`**Term**` + `>` definition), alphabetically
  sectioned (`## A` … `## Z`) when the source glossary is alphabetical. It is
  not a link stub: a term the source document defines appears here as an entry,
  and every translation run extends the page in the same commit. One term is
  defined once — a second document contributing the same term appends a 来源
  line instead of a second definition; the doc ID and revision are stated once
  in the page intro. The single link to the Arm Glossary stays, as the pointer
  to terms the document itself does not define. A document whose source has no
  glossary chapter (the Cortex-M7 TRM DDI0489F) keeps the link-only page —
  never invent entries.
- `mkdocs.yml`, group `ARM Cortex` → one nav group per source document, using
  short labels (doc IDs live on the landing pages, not in the nav):
  `Cortex-M7 TRM`, `Armv7-M 架构参考手册`, `Cortex-R52+ TRM` and
  `Armv8-M 架构参考手册`. Add
  `- "<中文标题>": cortex/<document>/<topic>/index.md` under the matching
  document group.
- `<target>/<document>/index.md`: numbered link in source chapter order
  (`1. [程序员模型（Programmers Model）](programmers_model/index.md)`).
- `<target>/index.md`: numbered link to the **document landing page**
  (`1. [Cortex-R52+ TRM（102199 r0p3）](r52plus-trm/index.md)`), never to the
  individual chapter. A new document series also gets its own `## N.` section
  here.
- A `concept/` subtree holds externally sourced explainers; they are not
  produced by this skill.

## Quality rules

- No untranslated English paragraph in the body; proper nouns and quoted
  standard wording are the only exceptions.
- No placeholder text, no `TODO`, no empty section bodies.
- Row sets, bit ranges and register addresses match the source exactly — a
  dropped row is a defect, not a style choice.

## Decision log

- 2026-11-05, issue #283 — Raw HTML `<table>` permitted as a narrow exception
  for structurally complex tables; GFM remains the default and the three
  qualification cases in §Tables are exhaustive. Lifted by user decision after
  verifying that Material styles a plain `<table>` identically to a GFM table
  (`.md-typeset table:not([class])`) but that `md_in_html` does not parse
  Markdown inside HTML cells. Supersedes the earlier unrestricted "every table
  is a GFM table" wording.
- 2026-11-10, issue #361 — Opened the fourth document series `armv8-m/` for
  the Armv8-M ARM (DDI0553B B.y), a separate M-profile series: the Cortex-R52+
  is Armv8-R AArch32, and DDI0553B is not its architecture manual. With it,
  corrected the corpus path from `private-docs/ARM/{M7,R52}/` to
  `reference-docs/arm/{cortex-m7,cortex-r52}/` (no README on disk — the
  sync-todo Sources table is the pairing ledger), generalised the
  folder/nav-group enumerations to four short-label groups, and fixed the
  verification script paths (`.agents/skills/skills/...`). Synthetic figure
  numbers are allowed when the source diagram has no caption.
- 2026-11-10 — §Wording and markup aligned with the autosar-translate
  terminology/expression regime (STANDARD.md §1 ch.2, §4–§5): **term entries
  render as `**English Term**` + `>` blockquote definition** — the user's
  stated format, replacing both the source's *Term | Definition* table and any
  bullet-list definition; the glossary page carries those real entries instead
  of being a link stub, extended by every run, one term defined once. Also
  codified: heading-language rule at every level with the identifier-title
  exemption, the angle-bracket `&lt;…&gt;` rule, bold discipline (terms and
  identifiers only), one-term-one-rendering per document series, and the
  cross-reference and table-footnote rules. Front-matter titles stay
  Chinese-first — unlike autosar's English-first module titles, because an
  Arm chapter title is a descriptive phrase, not a product identifier.
