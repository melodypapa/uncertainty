# Source resolution — the Arm document corpus

The source of a run is **one Arm document** (TRM, Architecture Reference
Manual, SDEN errata notice) in a mirror of paired **ima-parsed Markdown +
original PDF** — same doc ID and revision, `.md` for text, `.pdf` for figures.
The corpus location is a run parameter; this skill hardcodes no path, file
name or document. A real corpus layout is documented in its ledger; the
cortex example (below) shows the shape.

## Corpus shape

A source directory per core/family, each holding one or more document pairs
(`<doc>.md` + `<doc>.pdf`; some documents are PDF-only). The pairing ledger is
the corpus's own sync-todo **Sources table** — it records doc IDs, revisions,
media size and which pairs are complete; check it before relying on a file.
There is no `README.md` in the corpus. Never edit the sources or the ledger's
source table except to record a genuine corpus change.

Filenames do not always match between `.md` and `.pdf` (a TRM PDF may drop the
revision tag; an errata PDF may carry a long legacy name) — the Sources table
is the pairing record, not the filenames.

Documents can be filed under a family directory they do not strictly belong to
(an Armv8-M ARM inside a `cortex-r52/` folder documents the M-profile
architecture, not the Armv8-R Cortex-R52+); the mapping ledger, not the
directory, says which article series a document pairs with.

## Selecting the source

1. **Topic → document**: TRM chapters describe one core's implementation
   (registers, interfaces, cache, MPU, address map). The architecture
   reference manual describes architectural behaviour (exception model, memory
   model, PMSA/MPU, instruction set). A page may legitimately come from
   either — `references/mapping.md` records the observed source per existing
   article.
2. **Text**: the `.md` parse. Its shape:
   - front matter is the cover, proprietary notice, release history and
     contents;
   - some documents are organised into Parts that contain Chapters: the
     document's own "Using this manual" / contents states the hierarchy and
     the PDF carries a divider page per Part. Detect this before mapping —
     when it is present, chapter articles are filed in
     `part-<designator>/<topic>/` subfolders (SKILL.md Steps 2 and 7). A
     source without Parts keeps flat chapters;
   - chapters are flattened (`# Chapter 8`, `## 8.1.2 …`), some parser
     artefacts split a heading into two `##` lines;
   - figures appear as `![...](2/<hash>/tmp_zip_img/<uuid>.png)` — the path
     does not resolve inside the corpus, it is a parse artefact;
   - merged table cells arrive as HTML `<table>` markup (sometimes inside the
     image alt text): read it as the cell grid, then rebuild the table as text
     (GFM by default; HTML only when the structure qualifies) — the parse's
     `<table>` is a source, not something to paste.
3. **Figures**: crop from the sibling `.pdf` (PyMuPDF), expanding the clip by a
   margin (~4% of the larger dimension per side, min 6pt — never flush with
   the content; see `article-format.md`). Do not screenshot or re-create a
   diagram by hand. Tables are never cropped — when the parse flattened one,
   read the cell grid from the PDF to rebuild it as text (see
   `article-format.md`).

## Verify the pairing

- Figure/table numbers **inside the source text** are the fastest proof: a
  caption `Table 8-1` sits in chapter 8 of the same document. A file name is
  not proof of the same thing.
- Legacy article images can carry numbers from an older revision that no
  longer match the current PDF. Confirm by the figure/table caption text in
  the `.md`, not by a file name.
- When the parse lost the number, match the section heading against the
  chapter's section list before translating.
- If two documents carry the same section (TRM and ARM both describe the
  PSR), prefer the TRM for implementation details and the ARM for
  architectural rules, and state the choice in the queue note or PR text.

## Constraints

- Do not translate from the PDF text layer when a `.md` exists.
- The PDF is also the source for revision-sensitive content; record the
  revision (`r1p0`, `r1p2`, `B.y`, `E.e`) in the PR text when it matters.
- The source corpus is read-only; never commit a new source file or PDF to it
  as part of a translation PR.
