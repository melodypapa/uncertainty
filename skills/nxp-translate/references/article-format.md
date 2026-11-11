# NXP article format

Document-agnostic conventions for NXP chapter articles (`<target>/chNN_<slug>/index.md`).
Derived from the translated NXP pages and the `arm-translate` conventions.
There is **no `STANDARD.md` for NXP corpora**: this file plus the neighbouring
article (read for syntax) are the law. Paths below are placeholders — a run's
real target root comes from its run parameters.

## Reading the neighbouring article (syntax only)

Read one neighbouring `<target>/chMM_<slug>/index.md` before writing so the new
page matches its front matter, numbering and figure filenames. Use it **for
syntax only**. Legacy or partial pages may carry defects; do **not** copy
them:

- empty section bodies (`## 3. RTC 寄存器说明` with nothing under it);
- `![Table_1](Table_1.png)` — a table cropped as an image;
- whole register-description chapters dropped;
- untranslated English paragraphs left in the body.

A faithful chapter translation has none of these.

## Front matter

Only `title`. Chinese title, English term in half-width parentheses preceded
by a space — **no Markdown markup in the title** (`**` renders literally:
Material does not parse the front-matter title, so `**PIT**` shows as literal
asterisks in the page h1, the browser tab and the sidebar nav):

```yaml
---
title: "周期性中断定时器 (PIT)"
---
```

Chapters whose title has no acronym use Chinese only
(`"存储器映射（Memory Map）"` is also acceptable when the English term is a
proper term). This differs from body text, where the Chinese gloss keeps
full-width parentheses and **bolds** the term (`本地存储器控制器（**LMEM**）`) —
bold belongs to the body only; the title is rendered un-parsed. The title
check in `check_tables.py` is position-agnostic: a trailing descriptor after
the term (`"S32K5xx 参考手册 (Reference Manual) 章节翻译"`) is fine. Never
add `spec:`, `release:` or tags — that convention belongs to
`docs/autosar/`. Never add a table of contents, document history, proprietary
notice or footer banner to the body.

## Body structure and numbering

- One or two intro sentences mirroring the chapter's opening, then the
  translated sections in **source order**. Do not invent overview or summary
  sections; keep the source's own overview section on the chapter page.
- **Never write `# ` in the body** — the front-matter `title` is the only h1.
- A section that immediately branches into subsections needs no intro text;
  "empty section" means nothing under it at all. `check_tables.py` gates the
  heading-level rule (level = numeric depth + 1) mechanically — a `### 1.7.1.`
  for a 3-component number is a defect, not a style choice.
- **Numbering restarts at 1 for every article.** Drop the chapter number, keep
  the remaining components, and set heading level = (number of remaining
  numeric components) + 1:

  | Source | Article |
  | --- | --- |
  | `45.1 Chip-specific RTC information` | `## 1. 芯片特定的 RTC 信息` |
  | `45.1.1 RTC clocking` | `### 1.1. RTC 时钟` |
  | `31.3.1.1 End-of-line programming` | `#### 3.1.1. End-of-line 编程` |
  | `44.4.3.2 Status And Control (SC)` | `#### 4.3.2. 状态与控制（SC）` |

  `scripts/extract_chapter.py`'s `heading_label()` computes this. Keep the
  relative structure; numbering is contiguous — a jump (`## 3.` with no `## 2.`,
  `### 7.10` with no `### 7.9`) is a defect, not a style choice.
- **Clamp at `######`.** NXP outlines reach level 10 (register and debug
  chapters carry dozens of deep entries, e.g. `78.8.2.3.2.3.1.3.1 Lock`). For a source level whose
  article level would exceed 6, do **not** write `#######`. Render the full
  number and title as a bold paragraph instead:

  ```markdown
  **8.2.3.2.3.1.3.1. 锁定（Lock）**
  ```

  It still carries the number, still translates, and still counts in the gap
  analysis. Deep levels are common in register and debug chapters.
- Update any internal `#anchor` links when renumbering.

## Wording and markup

- Faithful translation of NXP's wording, not a summary. Keep technical
  identifiers, register names, field names, instruction/register syntax and hex
  values untranslated: `PIT_0`, `MCR[MDIS]`, `CR[TEN]`, `4400_C000h`,
  `0000_0000h`, `位 [5:3]`, `0h`.
- Bold the English term on first mention with a Chinese gloss in parentheses:
  `自由运行计数器（**free-running counter**）`; acronyms and register names stay
  bold (`**PIT**`, `**SC**`). Later mentions may drop the parentheses.
- Numbers and encodings as printed. Repair the PDF text layer's underscore
  splits (`PIT 0 _` → `PIT_0`) before writing; normalize non-breaking spaces
  (U+00A0) to plain spaces; keep the underscore separators in hex and binary
  enumerations (`0000_0000h`, `0000_0000_0000_0000_0000b`) — a space-separated
  form is a text-layer artifact, not the printed value.
- A stray `*` outside `**` pairs (`**xxx***`, a dropped opener) renders as a
  literal asterisk — `check_tables.py` gates bold balance. A literal `*` is
  allowed only inside code spans or table cells that document a `*` marker
  (ECC coverage matrices).
- The source itself can carry typos (`AMBA_ AHB` printed in the S32K5 RM).
  Verify against a rendered page region before "repairing", repair to the
  evident intent, and record the source typo in the PR text.
- Lists mirror the source's bullets and numbering. Source `NOTE` → `**注意：**`,
  `CAUTION` → `**警告：**`, followed by the translated body.
- No `**说明**:` + `C` blocks — that is the AUTOSAR API convention.
- Bold markers stay balanced on every line — a stray `**` after a bolded term
  (`复位概述（**Reset Overview**）**`) renders as literal asterisks and is a
  defect.

## Cross-references

- A reference to another chapter of the same manual ("see X", 「参见 X」) becomes
  a Markdown link to the target article, using the article path pre-assigned in
  `references/chapter-map.md`, linked relative between sibling directories:
  `[复位概述（**Reset Overview**）](../ch060_reset_overview/index.md)`.
- A link to a chapter **not yet translated is still written** (a forward link):
  the slug is pre-assigned and stable, so the link goes live when that chapter
  lands. List the forward links in the PR body.
- References inside the same article stay plain text — no self links
  (`[芯片特定的 X 信息](index.md)` is a defect).
- A reference to a whole group of chapters (「参见时钟（**Clocking**）章节」,
  「参见 Reset 或 MC_ME 章节」) stays plain text — groups have no landing page
  to target. Link only when a single chapter article is the target.
- Link text never carries the internal `chNNN` prefix (`[ch012 SIUL2]` →
  `[SIUL2（**System Integration Unit Lite2**）]`).
- Register-name mentions in prose and register subsections ("see PMC
  Configuration (CONFIG)", reset-value tables) stay plain text — with one
  applied exception: **the memory-map table's register-name cells link to the
  register's own subsection** (`| **0h** | [控制密钥寄存器（**CTL_KEY**）](#52-控制密钥寄存器ctl_key) | …`),
  restoring the source PDF's own memory-map hyperlinks. The anchor is the
  target heading's Material slug (number dots stripped, `（）**` dropped, CJK
  kept, lowercased, `[-\s]+` → `-` — `### 5.2. 控制密钥寄存器（**CTL_KEY**）`
  anchors as `52-控制密钥寄存器ctl_key`). Range headings (`MBPTR0_-_MBPTR2`)
  cover their enumerated rows; a register with no in-chapter subsection stays
  plain and is reported. Run `scripts/link_registers.py --list` / `--apply`
  (idempotent) — never hand-write these anchors.
- References to documents outside the chapter corpus (attached IOMUX or
  memory-map sheets, other vendor manuals, Arm documentation) stay plain text:
  there is nothing to link to.

## Tables

- **Every table is text.** GFM is the default: a header row and `| --- |`
  separator, translated cell by cell. Tables are **never** cropped as images —
  a legacy `Table_1.png` in a directory you are editing is a defect, not a
  precedent.
- **The header row is mandatory, never dropped.** A GFM table exists only when
  the first pipe line is a header and the second is the `| --- |` separator;
  rows without them render as one soft-joined run-on paragraph, not a table.
  Every source table carries a header (`Fields` tables: `Field | Function`;
  memory maps: `Offset | Register | Width (In bits) | Access | Reset value`) —
  translate it (`位 | 字段 | 功能`, `偏移 | 寄存器 | 宽度（位） | 访问 | 复位值`),
  matching the column shape the rows actually use. The S32K5 RM corpus shipped
  11 chapters with header-less tables (ch057 alone lost 52 field-table
  headers); `scripts/check_tables.py` gates this in Phase A.
- A table numbered in the source (`Table 279.`) carries its number in the
  paragraph that introduces it, not in a caption line and not in a filename.
- Tables split across pages (`Table continued...` / `Table continues...`) are
  **one** table: stitch the data rows, drop the repeated header, and keep the
  whole grid together.
- In GFM tables, merged cells are expanded, not mirrored: repeat the spanning
  value in each row of the block so every row reads on its own. Multi-tier
  headers flatten into one header row naming each column.
- **HTML exception (narrow, exhaustive).** A raw `<table>` is allowed only when
  GFM cannot carry the structure: cells with block content (lists, code blocks,
  multiple paragraphs), a multi-tier header whose flattened form is ambiguous,
  or merged cells whose spanning semantics carry meaning. A plain wide grid
  stays GFM. HTML tables use `<table>/<thead>/<tbody>`, `<th scope="col">`, real
  `rowspan`/`colspan`, and **raw HTML inline markup** (`<strong>`, `<code>`,
  `<a href>`) — Markdown is not parsed inside HTML cells, so `**bold**` and
  `[text](url)` would render literally.

## Figures

- Every content figure of the chapter embeds where the source has it:
  `![Figure_256](Figure_256.png)`. No caption text; the alt text is the source
  figure number. Keep the source's **global** number — do not renumber per
  chapter.
- The PNG sits in the article directory next to `index.md`; no shared `images/`
  tree. Crop from the PDF with PyMuPDF at ≥ 2× zoom (see
  `references/source-resolution.md`). Never screenshot or redraw by hand.
- Bit-field bars, block diagrams and timing diagrams stay images. A register's
  unnumbered bit-field `Diagram` is also a figure; name it
  `Diagram_<slug>.png` where `<slug>` is the register name lower_snake_cased
  (`Diagram_sc.png`, `Diagram_tctrl0_tctrl6.png`). Add a numeric suffix on a
  name collision (`Diagram_sc_2.png`). Never name a figure `Table_<n>.png`.
- Anything with rows and columns is a table, not a figure.

## Register subsections

Keep the source skeleton in source order:

1. Register name and offset (`**SC** 偏移：**0h**`).
2. The `Function` prose.
3. The `Diagram` bit-field bar as a cropped figure.
4. The `Fields` table (`Field | Function`, with bit ranges).

The memory-map table (`Offset | Register | Width | Access | Reset value`) heads
the register-description section. Access values (`RW`, `RO`), bit ranges, reset
values and offsets match the source exactly — a dropped row is a defect.

**Fields tables match the source row for row** — bit range and field name,
including every `Reserved` row: never merge reserved rows (`31-5`/`4`/`3-1`
stay three rows), never drop one, never rename a field to the Diagram's label
when the Fields table differs. When the RM self-contradicts (Fields vs
Function prose vs Diagram), follow Fields + Diagram — the Function prose is
the likeliest copy-paste error — and record the conflict in the PR text.

## Landing pages and navigation

Applies only when the target root belongs to an MkDocs site; follow that
site's existing conventions for placement. The generic pattern:

- One chapter = one article directory: `<target>/chNN_<slug>/index.md`
  (`ch03_memory_map`, `ch43_periodic_interrupt_timer_pit`). Never split a
  chapter across files.
- Nav config: the corpus's group gets `- "<中文标题>": <site-path>/chNN_<slug>/index.md`
  at the chapter's **source position** (nav is ordered by chapter number, not
  arrival time). Every page must be registered or `--strict` fails.
- `<target>/index.md` is the section landing, registered as the unlabeled
  first entry of the group (`navigation.indexes`). Front-matter title, one
  intro sentence, `## 文章` link list grouped by the document's source group
  headers, then `## 相关内容`.
- Any parent landing page that lists corpora gets a link list for the new
  corpus.

## Quality rules

- No untranslated English paragraph in the body; proper nouns and quoted
  standard wording are the only exceptions.
- No placeholder text, no `TODO`, no empty section bodies.
- Row sets, bit ranges, register offsets and reset values match the source.
- No `![Table…]` image, no `# ` in the body, every `![](...)` target exists in
  the article directory.
- The WeChat QR footer, where present, uses `<section id="wechat">` + `<h4>`,
  never a markdown heading.
