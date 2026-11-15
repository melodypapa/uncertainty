> Worked example of a per-corpus article↔source mapping, kept because the
> cortex corpus still consumes it. The rules live in [../mapping.md](../mapping.md).

# Source → article mapping

Evidence column = the figure/table numbers inside the translated page, which
carry the source chapter number. Rows marked *(verify)* were inferred without a
numbered figure; confirm against the source heading before translating.

## Cortex-R52+ TRM (`docs/cortex/r52plus-trm/`)

Source: `cortex-r52/cortex_r52_trm_100026_0100_00_en.md` (TRM r1p0), plus
`cortex-r52/arm_cortex_r52plus_processor_trm_102199_0001_03_en.pdf` (TRM r0p3 —
the authoritative revision, chapter numbers two above r1p0). Articles are filed
under `cortex/r52plus-trm/`. The Cortex-R52+ is Armv8-R AArch32; its
architecture rules come from the TRM, not from the Armv8-M ARM.

| Article | Source chapter | Evidence |
| --- | --- | --- |
| `r52plus-trm/programmers_model/` | TRM ch2 Programmers Model | chapter heading; legacy images named `Table3-*` |
| `r52plus-trm/system_control/` | TRM ch3 System Control | chapter heading; legacy images named `Figure4-*`, `Table4-48` |
| `r52plus-trm/memory_system/` | TRM ch7 Memory System | chapter heading; legacy images named `Figure8_*` |
| `r52plus-trm/memory_protection_unit/` | TRM ch8 Memory Protection Unit | chapter heading; source tables are `Table 8-1`…`Table 8-7`, legacy images named `Table9-*` |

**The legacy pages were translated from an older revision whose chapter numbers
are current + 1.** The evidence is consistent: Programmers Model is chapter 2
(images `Table3-*`), System Control chapter 3 (`Figure4-*`, `Table4-48`),
Memory System chapter 7 (`Figure8_*`), MPU chapter 8 (`Table9-*`, content
`Table 8-1 EL1-controlled MPU background region - …`). Chapter 9 in this
revision is the Generic Interrupt Controller. Confirm a chapter by its heading
and table text, never by a legacy file name, and do not rename existing files.

Not yet translated from the R52 TRM (coverage backlog, in chapter order):
clocking and resets (ch4), power management (ch5), initialization (ch6),
generic interrupt controller (ch9), generic timer (ch10), debug (ch11),
performance monitor unit (ch12), cross trigger (ch13), ETM (ch14), Advanced
SIMD and floating-point (ch15).

## Cortex-M7 (`docs/cortex/m7-trm/` and `docs/cortex/armv7-m/`)

Sources: `cortex-m7/DDI0489F_cortex_m7_trm_r1p2.md` (TRM r1p2) and
`cortex-m7/DDI0403E_e_armv7m_arm.md` (Armv7-M ARM E.e);
`cortex-m7/cortex_m7_at610_at611_sden_1068427_v11_0_en.md`
is the errata notice. Articles are filed per source document: `cortex/m7-trm/`
for the TRM chapters, `cortex/armv7-m/` for the ARM chapters. The ARM is
Part-structured, so its chapter articles sit one level deeper in
`cortex/armv7-m/part-<designator>/` (see the rule in `../mapping.md` and
SKILL.md Step 2); the TRM has no Parts and stays flat. A merged article
(implementation chapter + architecture chapter) stays whole under its
implementation document.

| Article | Source | Evidence |
| --- | --- | --- |
| `armv7-m/part-a/arm_architecture_memory_mode/index.md` | Armv7-M ARM appendix A3 (Part A) | `FigureA3-1`…`FigureA3-5` |
| `m7-trm/programmers_model/` | M7 TRM programmers model + Armv7-M ARM exceptions chapter (merged 2026-11-06) | `Table2-3`…`Table2-6A`, `Figure2-1`, `Figure2-2`, `Table2-14-1` *(verify)* |
| `m7-trm/nested_vectored_interrupt_controller/` | M7 TRM NVIC chapter | no figures *(verify)* |
| `m7-trm/instruction_set/` | Armv7-M ARM instruction-set chapters + TRM summary | no figures *(verify)* |
| `m7-trm/mpu/` | M7 TRM MPU chapter + Armv7-M ARM appendix B3 (merged 2026-11-06) | `TableB3-1`…`TableB3-11` |
| `armv7-m/part-b/system_address_map/index.md` | Armv7-M ARM system address map (B3.1–B3.4, Part B) | `TableB3-3` *(verify)* |

Not yet translated (coverage backlog): M7 TRM clocking/reset, power control,
debug/trace chapters, and the SDEN errata notice.

## Armv8-M ARM (`docs/cortex/armv8-m/`)

Source: `cortex-r52/DDI0553B_y_armv8m_arm.md` + `.pdf` (Armv8-M ARM B.y). This
is a **separate M-profile series** — the Cortex-R52+ is Armv8-R AArch32, so
DDI0553B is not the R52+ architecture manual. The group was DEFERRED with an
empty queue until 2026-11-10, when the series opened.

DDI0553B is organised into Parts containing Chapters ("Using this manual",
printed 41–42), so every chapter article lives in its Part subfolder
`armv8-m/part-<designator>/<topic>/index.md`, with a Part index page at
`part-<designator>/index.md`. The Part designators come from the source, not
from this example.

| Article | Source chapter | Evidence |
| --- | --- | --- |
| `armv8-m/part-a/introduction/index.md` | Part A A1 Introduction | chapter heading; `FigureA1-1` (synthetic — the source diagram has no caption/number) |
| `armv8-m/part-b/memory_model/index.md` | Part B B7 Memory Model | chapter heading; `FigureB7-1`…`FigureB7-4` |
| `armv8-m/part-c/instruction_encoding_32bit/index.md` | Part C C2.3 Instruction Specification | `FigureC2-25`…`FigureC2-98` *(verify)* |
| `armv8-m/part-g/glossary/index.md` | Part G Glossary (no numbered Chapter) | source glossary row set |

Parts D / E / F (registers, pseudocode, packet protocols) are reference
material, deliberately deferred, and have no translated article and therefore
no Part index page. Chapter C2.4 is split into alphabetical bands under
`armv8-m/part-c/instruction_list/` on user request. See
`docs/cortex/sync-todo/ARMv8-M.md` for the current queue.

## Naming new articles

- Directory = lower_snake_case topic name (`memory_protection_unit`, `system_control`),
  not the chapter number. When the source has Parts, the topic directory sits
  inside `part-<designator>/` (`part-b/memory_model/index.md`), with the Part
  index page at `part-<designator>/index.md`; a source without Parts keeps the
  flat `memory_protection_unit/index.md`.
- One source chapter per article; split a chapter only when the user asks, and
  then state the split in the PR.
- A topic present in both the TRM and the ARM manual (e.g. exceptions) takes
  the architectural source for behaviour and cites TRM differences inline.
