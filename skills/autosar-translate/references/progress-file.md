# Progress file — <target>/TODO.md

The TODO file is the running work queue of the AUTOSAR translation program.
It lives in the repo at `<target>/TODO.md`, is excluded from the site
build (`exclude_docs` in `mkdocs.yml`), and is maintained by this skill.

## Maintenance rules

1. After **every** sync that touches an article, update that article's row in
   the same PR: new status, refreshed note, and bump the `Last updated` date
   at the top.
2. When creating a brand-new article, move its row into the appropriate
   group/section list with the appropriate status (an ❌/missing document's
   first translation lands its row under the group's section list).
3. Never reorder or reformat sections casually — the file is diffed across
   PRs; keep one bullet per spec, stable ordering (alphabetical by spec name
   within a section).
4. If the file has drifted badly (many syncs skipped it), regenerate the
   affected sections from a fresh gap analysis instead of patching blindly.

## Format (regrouped 2026-11-11)

Since 2026-11-11 the ledger is split into two top-level groups —
`## Unfinished（未完成）` then `## Finished（已完成）` — each keeping the
per-section subsections. A row moves between groups only when its status
changes to/from an open state (🔶/⚠️/⛔/❌ are open; ✅/📖/📄 are done).

```markdown
# AUTOSAR Article Translation Progress

> Maintained by the autosar-translate skill per [STANDARD.md](STANDARD.md); update the touched entry and the `Last updated` date after every sync.
> Status: ✅ Type A-compliant · 🔶 Translated pending alignment · ⚠️ Partial · ⛔ Stub · ❌ Missing · 📖 Guide/topic (exempt from the skeleton)
> Baseline: R23-11 · Last updated: YYYY-MM-DD

## Overview
(one summary table: counts per status, coverage %)

## Unfinished（未完成）
### Backlog            (program-level `- [ ]` work items only)
### <section>          (only the 🔶/⚠️/⛔ rows of that section)
### foundation（未完成） (only the ❌ rows)
### Missing queues      (queue-derived counts, reconciled against sync-todo/index.md)

## Finished（已完成）
### Backlog records     (ticked records, kept verbatim as the audit trail)
### <section>            (one section per site dir: communication, io, …)
- ✅ [article title](relative link) — SWS_spec
- 📖 [guide article](relative link) — EXP_spec (exempt from the skeleton)
### Archive notes       (one-line records of purged stale blocks)
```

## Work todo lists (per-run)

The execution queue is the **persistent batch-queue files** in
`<target>/sync-todo/` — since the 2026-11-11 regroup: `Group-unfinished.md`
(open rows with 6-step sub-checklists, grouped by source batch) +
`Group-finished.md` (condensed done-row archive); `index.md` holds the resume
rules — one row consumed per run,
never conversation-only (`todo.md` alongside the outputs for a workspace run).
Format, row template, resume and tick rules: `references/todo-format.md`.
Program-level fixes outside single-article runs (wording sweeps, hygiene)
live in the `### Backlog` subsection under `## Unfinished（未完成）` as
`- [ ]` items; ticked records move to the `### Backlog records` subsection
under `## Finished（已完成）`.

Rules for queue rows:

- One verifiable action per step; findings and decisions on `- Note:` bullets
  under the row, appended when they happen.
- A row's inputs: STANDARD.md rule checklist, the article's current row in
  this file, and the fresh gap analysis — plus mid-run user decisions.
- Ticked items in `## Backlog` get removed (or archived) once the
  corresponding status row has been updated — a work item is done only when
  its status row says so.
- The two files are linked: a status row flips (Step 8) only after the queue
  row's 6 steps are `[x]` and the Step 8 user confirmation was given; the
  flipped queue row (with commit hash + PR link) is the evidence behind the
  status row.

## Status definitions

| Status | Meaning |
| --- | --- |
| ✅ Type A-compliant | Seven chapters present, canonical wording, no forbidden chapters |
| 🔶 Translated pending alignment | Complete seven chapters but with legacy wording, extra site-specific chapters, or forbidden-chapter residue |
| ⚠️ Partial | Skeleton incomplete — missing ≥1 chapter (often just 「API规范」) |
| ⛔ Stub | ≤ ~19 lines, effectively empty |
| ❌ Missing | No article for the spec |
| 📖 Guide/topic | EXP guides, TPS templates, bespoke topic articles — exempt from the Type A skeleton (STANDARD.md §7) |

## Status transitions

- ⛔/⚠️ → ✅: after a sync completes the missing chapters AND aligns wording.
- 🔶 → ✅: after a wording/forbidden-chapter alignment pass.
- ❌ → ⚠️/✅: after a first translation (⚠️ if delivered partial by agreement).
- Never mark ✅ without running the strict build and comparing chapter headings
  against STANDARD.md §1/§2.
