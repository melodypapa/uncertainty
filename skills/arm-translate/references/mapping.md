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
for the TRM chapters, `cortex/armv7-m/` for the ARM chapters. A merged article
(implementation chapter + architecture chapter) stays whole under its
implementation document.

| Article | Source | Evidence |
| --- | --- | --- |
| `armv7-m/arm_architecture_memory_mode/` | Armv7-M ARM appendix A3 | `FigureA3-1`…`FigureA3-5` |
| `m7-trm/programmers_model/` | M7 TRM programmers model + Armv7-M ARM exceptions chapter (merged 2026-11-06) | `Table2-3`…`Table2-6A`, `Figure2-1`, `Figure2-2`, `Table2-14-1` *(verify)* |
| `m7-trm/nested_vectored_interrupt_controller/` | M7 TRM NVIC chapter | no figures *(verify)* |
| `m7-trm/instruction_set/` | Armv7-M ARM instruction-set chapters + TRM summary | no figures *(verify)* |
| `m7-trm/mpu/` | M7 TRM MPU chapter + Armv7-M ARM appendix B3 (merged 2026-11-06) | `TableB3-1`…`TableB3-11` |
| `armv7-m/system_address_map/` | Armv7-M ARM system address map (B3.1–B3.4) | `TableB3-3` *(verify)* |

Not yet translated (coverage backlog): M7 TRM clocking/reset, power control,
debug/trace chapters, and the SDEN errata notice.

## Armv8-M ARM (`docs/cortex/armv8-m/`)

Source: `cortex-r52/DDI0553B_y_armv8m_arm.md` + `.pdf` (Armv8-M ARM B.y). This
is a **separate M-profile series** — the Cortex-R52+ is Armv8-R AArch32, so
DDI0553B is not the R52+ architecture manual. The group was DEFERRED with an
empty queue until 2026-11-10, when the series opened.

| Article | Source chapter | Evidence |
| --- | --- | --- |
| `armv8-m/introduction/` | Part A A1 Introduction | chapter heading; `FigureA1-1` (synthetic — the source diagram has no caption/number) |

Not yet translated (coverage backlog, in chapter order): Part B chapters B1
Resets, B2 Power Management, B3 Programmers' Model, B4 Floating-point Support,
B5 Vector Extension, B6 Pointer Authentication / BTI Extension, B7 Memory
Model, B8 The System Address Map, B9 Synchronization and Semaphores, B10 The
Armv8-M Protected Memory System Architecture, B11 The System Timer SysTick,
B12 Nested Vectored Interrupt Controller, B13 Debug, B14 Debug and Trace
Components, B15 The Performance Monitors Extension, B16 RAS Extension. Parts
C–G (instruction set, register payload specification, pseudocode, debug packet
protocols, glossary) are reference material, deliberately deferred — see
`docs/cortex/sync-todo/ARMv8-M.md`.

## Naming new articles

- Directory = lower_snake_case topic name (`memory_protection_unit`, `system_control`),
  not the chapter number.
- One source chapter per article; split a chapter only when the user asks, and
  then state the split in the PR.
- A topic present in both the TRM and the ARM manual (e.g. exceptions) takes
  the architectural source for behaviour and cites TRM differences inline.
