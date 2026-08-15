---
name: markdown-translator
description: "Bulk-translate markdown docs from a source-language folder (default en/) into a target-language folder (default chn/, Simplified Chinese), mirroring structure. Safe for docling/PDF markdown with inline base64 images, preserved byte-for-byte via extract→translate→restore. Use whenever the user asks to translate markdown or .md files, convert an en folder to Chinese or another language, localize docs, translate a PDF-derived or docling markdown manual, or make a Chinese version of docs."
author: melodypapa
license: MIT
repository: https://github.com/melodypapa/uncertainty
keywords: [markdown, translation, localization, docling, simplified-chinese]
version: "1.0.0"
---

# Markdown Translator

Translate every markdown file under a source-language folder into a target language, writing results to a parallel folder with the same internal structure. The default and most common case is English (`en/`) → Simplified Chinese (`chn/`), but the folder names and target language are parameters, so the same workflow handles any pair (e.g., `en/` → `ja/` in Japanese).

The translation is done by you and the subagents you dispatch: files and segments are translated in parallel (see *Performance: parallel translation*), then verified mechanically. No external translation services are used.

## Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `path` | current working directory | Root folder containing the source folder |
| `source_dir` | `en` | Subfolder of `path` holding the original markdown files |
| `target_dir` | `chn` | Subfolder of `path` where translations are written |
| `target_language` | Simplified Chinese (zh-Hans) | Language to translate into |

Defaults exist so a vague prompt still works. Explicit user wording always wins: if the user says "translate `site/content/en` to Japanese in `jp`", then `path=site/content`, `target_dir=jp`, `target_language=Japanese`, and `source_dir` stays `en`. If the user names a source folder other than `en`, honor that too.

## Workflow

1. **Resolve the parameters** from the prompt. If the user gave only a path, apply the defaults for everything else. Don't ask the user to confirm parameters that are already unambiguous — just state the resolved configuration in one line before starting.

2. **Discover the files.** Recursively list all `*.md` (and `*.markdown`) files under `<path>/<source_dir>/`. Sort them for a stable order. If there are none, say so and stop — never invent or search outside the given folder.

3. **Check for existing translations.** The target counterpart of `<source_dir>/a/b.md` is `<target_dir>/a/b.md`. If any counterparts already exist, ask the user how to proceed *before* translating anything:
   - **Skip existing** — translate only the files that have no translation yet
   - **Update stale only** — compare modification times; re-translate files whose source is newer than its translation
   - **Re-translate all**

   For large trees, don't compare by hand — run the bundled `scan` subcommand once (`python <skill-dir>/scripts/md_images.py scan <path>/<source_dir> <path>/<target_dir>`). It prints JSON: every file's `status` (missing/stale/ok), its `text_bytes` (size with inline images excluded), and a `todo_text_bytes` total — exactly the input needed to plan the parallel work (see *Performance*).

   If no interactive user is available (background or headless run), default to **skip existing** and list the skipped files in the final summary instead of silently overwriting someone's work.

4. **Translate — in parallel, never segment after segment.** One conversation translating a large chapter section by section is the slowest possible path: every segment is a separate sequential round trip. Work through the batch in parallel instead (see *Performance: parallel translation*): small files whole, large files split into segments, each handled by its own subagent. Per file: check inline images with `python <skill-dir>/scripts/md_images.py status <file>` (or `grep -c 'data:image' <file>`); zero inline images — read it, translate it completely, write it to the mirrored path (creating parent directories as needed); any inline images — use the extract → translate → restore pipeline in *Embedded images* below. When a file references local image or asset files, copy them into the mirrored location in the target folder. Never leave sections untranslated, never insert TODO placeholders, and never truncate long files — a partial translation looks done but isn't. An interrupted run loses at most one segment, not the batch.

5. **Report.** When finished, print a short summary: number of files translated, parallel workers used and segments split (see *Performance*), inline images restored and local asset files copied, files skipped (and why), and any files that contained no translatable prose (pure code/config files — just copy or note them). Include the output folder path.

For large batches (more than ~10 files), give brief progress updates as parallel workers complete rather than going silent.

## What to preserve verbatim

Getting this wrong breaks builds and links, which is far worse than an awkward sentence:

- **Fenced code blocks** (``` or ~~~) — content byte-for-byte unchanged, including comments inside them
- **Inline code** `` `like this` ``
- **YAML frontmatter** — the whole block between `---` markers stays exactly as-is (site generators and tooling often parse it)
- **URLs, link targets, image paths** — translate link text and alt text, never the target
- **HTML tags** — keep the tags; translate the visible text between them
- **Identifiers of any kind** — file paths, commands, class/function/variable names, config keys, XML/ARXML element and attribute names
- **Markdown structure** — heading levels, list markers, table pipes, blockquotes, bold/italic markers, emoji

## Embedded images (docling-style markdown)

Docling and similar PDF→markdown converters embed images INLINE as base64 data URIs: `![Image](data:image/png;base64,AAAA…)`. In real manuals these dominate the file — a 1 MB chapter is often 97% image bytes. Two hard constraints follow:

- Such files must never be read or written raw: file-reading tools truncate at modest size limits, and no model can re-emit megabytes of base64 without corrupting it. A single wrong character silently breaks the image.
- Only lightweight placeholder tokens should ever pass through translation. The bundled script `scripts/md_images.py` keeps the base64 out of the model entirely.

### The extract → translate → restore pipeline

1. **Extract** — `python <skill-dir>/scripts/md_images.py extract <src.md> <work>/src stripped.md <work>/src.map.json`
   Writes a text-only copy where every inline image becomes `![Image](IMG_PLACEHOLDER_0)`, plus a JSON map holding the original image markdown.
2. **Translate** the text-only copy into `<work>/translated.md` following the rules in this skill. If the copy is large (>~8 KB of text), translate it as parallel segments instead — see *Performance: parallel translation*. The tokens are load-bearing: never translate, renumber, reorder, reformat, or delete `IMG_PLACEHOLDER_N`, and never alter the `![...]()` wrapper around it. Each token stays on the same line/position as in the stripped file.
3. **Restore** — `python <skill-dir>/scripts/md_images.py restore <work>/translated.md <work>/src.map.json <dst.md>`
   Re-inserts each original image byte-for-byte. The script exits with an error naming any placeholder the translation lost, so corruption surfaces immediately instead of shipping broken images.
4. **Verify** — run both checks on every file that used the pipeline:
   - `python <skill-dir>/scripts/md_images.py verify <src.md> <dst.md>` — proves every inline image survived byte-for-byte and no placeholder tokens remain.
   - `python <skill-dir>/scripts/verify_structure.py <src-stripped.md> <translated.md> "<file label>"` — proves nothing was dropped: every heading (by number and order), every table block and row, every figure/table caption, every list item. A translation that silently drops rows of a register table or entries of a glossary looks fine to a reader but is wrong; this makes it impossible to ship.

   If either check fails, the output must not be delivered.

Keep work files in a scratch folder (e.g. `<target_dir>/.work/` or `/tmp`) and delete them after a successful verify; they never belong in the source tree.

### Other image and docling rules

- **Local image files** (relative refs that resolve inside the source folder): copy the file, bytes unchanged, to the same relative location under the target folder — translating `en/ch1/manual.md` that references `en/ch1/images/pic_0.jpg` means writing `chn/ch1/manual.md` and copying the image to `chn/ch1/images/pic_0.jpg`. Never rename, re-path, or re-encode. A referenced image missing from the source tree: keep the reference as-is and note it in the final summary.
- **External URLs and absolute paths** are left alone — no copying, no rewriting.
- **Captions**: docling places figure captions as a text line directly below the image, often italic (`*Figure 3: Parser workflow*`) — translate them as normal prose.
- **Alt text**: docling's generic `Image` alt carries no meaning; it comes back byte-for-byte with the reinserted image anyway. Never invent descriptive alt text that isn't in the source.
- **Callout marker headings**: docling maps PDF callout boxes to marker headings like `## NOTE`, `## CAUTION`, `## WARNING`, `## IMPORTANT`. Keep the marker word untranslated — doc pipelines and site styles often key on it — and translate the paragraph below it.

The most dangerous failure mode of bulk translation is silent omission: a dropped table row, a skipped glossary entry, a missing section. Readers rarely notice, so verification must be mechanical, not visual. That is why the pipeline ends in two independent checks (image bytes + structure). A related trap specific to docling output: converters split long tables across page breaks into separate blocks with `Table continues...` / `Table continued...` markers between them. Keep the source's block boundaries exactly — do not merge continued tables into one or re-split them at different points, or the translated document will no longer line up with the source's pagination structure.

## Performance: parallel translation

Sequential translation — one conversation reading a file and generating its translation "segment after segment" — is the bottleneck of bulk work. Every segment is a separate model round trip; a 40 KB chapter can cost dozens, and a batch costs dozens more. Files are independent of each other, and the sections of one file are independent once the terminology is fixed, so translate in parallel with subagents.

### Plan the work with `scan` (once, before translating)

    python <skill-dir>/scripts/md_images.py scan <path>/<source_dir> <path>/<target_dir>

Prints JSON: per-file `status` (missing/stale/ok) and `text_bytes` (inline images excluded — the size that actually drives translation cost), plus a `todo_text_bytes` summary. Use it to decide:

- **Big files** (`text_bytes > ~8000`, roughly 150+ lines of prose) → split into segments (below).
- **Everything else** → translate whole, one subagent per file or small group.
- **Worker count** → 3–6 subagents total; group small files so each worker gets a fair share. A few small files don't pay for the overhead — translate directly.

### Fix terminology before any worker starts

The only thing that couples translations is terminology, and it must be decided once, up front, so workers never wait on each other:

1. If the target folder already has translations, skim one and extract its term pairs (e.g. `component → 组件`).
2. Otherwise skim the most representative source file — an index or glossary file if present, else the first file in sorted order — and pick terms for the recurring nouns (parser, interface, configuration, pipeline, ...).
3. Hand the SAME glossary and language conventions to every worker. Consistency then holds by construction instead of by checking each other's output.

### Parallelize a batch across files

Dispatch one subagent per file (or per small group). Each worker gets: the source path, the mirrored destination path, the target language, the glossary, and the translation rules in this skill (preserve code/frontmatter/URLs verbatim; translate headings/prose/tables/link text; run extract → restore → verify for its own files if they contain inline images). Workers write their own files and run their own verification; the main agent re-translates nothing.

### Parallelize one large file across segments

For a big file (or a big stripped copy):

1. **Extract** inline images if any (pipeline above) → text-only copy + map.
2. **Split** the text-only copy at heading boundaries:

       python <skill-dir>/scripts/md_split.py split <stripped.md> <segdir> --target-size 4096

   Segments never split inside fenced code blocks or frontmatter, and the IMG_PLACEHOLDER_N tokens keep their global numbering, so no renumbering is ever needed. A `NO-SPLIT` result means the file has no usable heading boundaries — translate it directly.
3. **Dispatch** one subagent per part. Each worker reads its part file and writes `<part>.zh.md` next to it, then stops. The worker prompt must repeat the preservation rules: keep code blocks, frontmatter, URLs, HTML tags, and every `IMG_PLACEHOLDER_N` token byte-for-byte; keep heading levels and table structure; apply the glossary and language conventions. Workers never restore images or verify structure — that happens once, after join.
4. **Join**:

       python <skill-dir>/scripts/md_split.py join <segdir> <translated.md>

   Fails loudly if any part is missing (a worker that didn't finish) or if a placeholder token count drifted. Fix the failed part, then rejoin.
5. **Restore + verify** exactly as in the single-file pipeline (restore, then image verify + structure verify). The checks don't change: the joined file IS the full translation.

Keep segments in the scratch folder (`<target_dir>/.work/segments/`) and delete them after a successful verify.

**Never** hand-split a file, **never** let workers translate each other's segments or re-read the whole manual, and **never** skip the final verification after joining — split/join bugs surface exactly there.

## What to translate

- Headings, paragraphs, list items, blockquotes
- Table cells containing prose (keep the table structure and alignment)
- Link text and image alt text
- HTML comment text outside code blocks, and visible text inside inline HTML

## Terminology

- Keep in English: product and standard names (AUTOSAR, ARXML), acronyms the reader is expected to know (ECU, BSW, API, CLI), tool and command names (`arxml-format`), and anything that is also an identifier in the surrounding code.
- Translate common technical nouns when a standard term exists in the target language (e.g., Simplified Chinese: component → 组件, interface → 接口, configuration → 配置, parser → 解析器). When no standard term exists, keep the English word — an untranslated term reads fine, a mistranslated one misleads.
- If the target folder (or the project) already contains translations, skim one first and match its terminology and tone. Consistency with existing docs beats individual preference.
- Pick terminology in the first file and stick with it across the whole batch. In a parallel run, decide the glossary BEFORE any worker starts — see *Fix terminology before any worker starts* under *Performance*; workers start simultaneously, so there is no "first file" to learn from.

## Simplified Chinese conventions

Apply these when `target_language` is Simplified Chinese; adapt analogously for other languages:

- Simplified characters only; full-width punctuation for Chinese sentences （，。：；！？、）, including full-width parentheses（）when the content is Chinese
- Keep half-width punctuation inside code, URLs, and identifiers
- A thin space between Chinese characters and adjacent Latin words or numbers is standard technical style: `使用 ARXML 解析器解析 3 个文件`
- Translate meaning, not words. Output should read like it was originally written in Chinese — natural, fluent technical prose
- Keep the source's tone: a tutorial stays friendly and imperative, a spec stays formal
- No translator's notes, no 译者注, no explanations of translation choices in the output files

## Example

**Input — `en/getting-started.md`:**

```markdown
---
title: Getting Started
---

## Installation

Install the parser package with pip, then configure the release:

    AUTOSAR.setARRelease('R23-11')

See the [Python documentation](https://docs.python.org/3/) for details.

![Image](images/fig1.png)

*Figure 1: Parser workflow*
```

**Output — `chn/getting-started.md`:**

```markdown
---
title: Getting Started
---

## 安装

使用 pip 安装解析器包，然后配置版本：

    AUTOSAR.setARRelease('R23-11')

详情请参阅 [Python 文档](https://docs.python.org/3/)。

![Image](images/fig1.png)

*图 1：解析器工作流程*
```

Note how the frontmatter, code, URL, and image path are untouched, while headings, prose, the caption, and link text are translated — and `images/fig1.png` gets copied to `chn/images/fig1.png`.
