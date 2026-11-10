"""Unit tests for extract_chapter.py.

Pure helpers are tested without the PDF. Integration tests exercise a real
NXP PDF and are skipped when the PDF (or PyMuPDF) is unavailable; point
NXP_TEST_PDF at any NXP document to run them against it.

Run:
  python3 -m unittest discover -s .agents/skills/nxp-translate/scripts -p 'test_*.py' -v
"""

from __future__ import annotations

import os
import unittest

import extract_chapter as ec


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
PDF = os.environ.get(
    "NXP_TEST_PDF",
    os.path.join(REPO_ROOT, "reference-docs", "nxp", "s32g3",
                 "reference_manual", "RMS32G3.pdf"),
)


class SlugTests(unittest.TestCase):
    def test_slugify_strips_punctuation_and_keeps_identifiers(self):
        cases = {
            "Memory Map": "memory_map",
            "Periodic Interrupt Timer (PIT)": "periodic_interrupt_timer_pit",
            "Network-on-Chip (NoC)": "network_on_chip_noc",
            "System Resource Controller (SRC_0)": "system_resource_controller_src_0",
            "Clock Monitoring Unit - Frequency Meter (CMU_FM)":
                "clock_monitoring_unit_frequency_meter_cmu_fm",
            "SerDes General Purpose Registers (SERDES_GPR)":
                "serdes_general_purpose_registers_serdes_gpr",
            "Ultra Secured Digital Host Controller (uSDHC)":
                "ultra_secured_digital_host_controller_usdhc",
        }
        for title, expected in cases.items():
            with self.subTest(title=title):
                self.assertEqual(ec.slugify(title), expected)

    def test_chapter_dir_pads_to_chapter_count(self):
        # 2-digit padding up to 99 chapters, 3 digits beyond
        self.assertEqual(ec.chapter_dir(3, "Memory Map", 81), "ch03_memory_map")
        self.assertEqual(ec.chapter_dir(43, "Periodic Interrupt Timer (PIT)", 81),
                         "ch43_periodic_interrupt_timer_pit")
        self.assertEqual(ec.chapter_dir(81, "Aurora Trace Port (ATP) Subsystem", 81),
                         "ch81_aurora_trace_port_atp_subsystem")
        self.assertEqual(ec.chapter_dir(5, "SRAM Controller (SRAMCTL)", 111),
                         "ch005_sram_controller_sramctl")
        self.assertEqual(ec.chapter_dir(57, "Mode Entry Module (MC_ME)", 111),
                         "ch057_mode_entry_module_mc_me")


class HeadingTests(unittest.TestCase):
    def test_drops_chapter_number_and_sets_level(self):
        cases = {
            "45.1": (2, "1.", False),
            "45.1.1": (3, "1.1.", False),
            "31.3.1.1": (4, "3.1.1.", False),
            "44.4.3.2": (4, "4.3.2.", False),
            "24.7.2.3.1.1": (6, "7.2.3.1.1.", False),
            "78.8.2.3.2.3.1.3.1": (6, "8.2.3.2.3.1.3.1.", True),
        }
        for number, expected in cases.items():
            with self.subTest(number=number):
                self.assertEqual(ec.heading_label(number), expected)

    def test_never_returns_a_heading_deeper_than_h6(self):
        for n in range(2, 12):
            number = ".".join(["78"] + ["1"] * n)
            level, _, clamped = ec.heading_label(number)
            self.assertLessEqual(level, 6)
            if n + 1 > 6:
                self.assertTrue(clamped)

    def test_rejects_non_section_number(self):
        with self.assertRaises(ValueError):
            ec.heading_label("44")


class ChromeTests(unittest.TestCase):
    def test_universal_chrome_lines(self):
        for line in ["NXP Semiconductors", "Reference Manual",
                     "General Business Information", "2259 / 5101",
                     "10491 / 10491"]:
            with self.subTest(line=line):
                self.assertTrue(ec.is_chrome_line(line))

    def test_derived_running_header_is_chrome(self):
        is_chrome = ec.make_chrome_filter(
            ["S32G3 Reference Manual, Rev. 5, 2025-09-17"])
        self.assertTrue(is_chrome("S32G3 Reference Manual, Rev. 5, 2025-09-17"))
        self.assertTrue(is_chrome("NXP Semiconductors"))
        self.assertFalse(is_chrome("The PIT module is the source of:"))

    def test_content_lines_are_not_chrome(self):
        for line in ["43.1 Chip-specific PIT information",
                     "Table 279. PIT triggers", "The PIT module is the source of:",
                     "S32K5XXRM"]:
            with self.subTest(line=line):
                self.assertFalse(ec.is_chrome_line(line))

    def test_continuation_markers_survive_band_stripping(self):
        for line in ["Table continued from the previous page...",
                     "Table continues on the next page..."]:
            with self.subTest(line=line):
                self.assertTrue(ec.is_continuation_marker(line))
                self.assertFalse(ec.is_chrome_line(line))


def s32g3_style_toc():
    """81 chapters mixing levels: 1-4 level-1, 5-81 level-2 under group headers."""
    toc = [(1, "S32G3 Reference Manual", 1), (1, "Contents", 2)]
    chapter_pages = {1: 96, 2: 106, 3: 113, 4: 114}
    for n in range(5, 82):
        chapter_pages[n] = 115 + n
    for n in range(1, 5):
        toc.append((1, f"{n} Chapter{n}", chapter_pages[n]))
    toc.append((1, "Chapter 5-23: System Modules", 115))
    for n in range(5, 82):
        toc.append((2, f"{n} Chapter{n}", chapter_pages[n]))
    toc.append((1, "Debug", 100))
    toc.append((1, "A General Changes", 5083))
    toc.append((1, "B Release notes", 5084))
    toc.append((3, "44.4.3.2 Status And Control (SC)", 2259))
    toc.append((7, "24.7.2.3.1.1 PFE_MAC_0 RGMII configuration", 908))
    return toc, chapter_pages


def s32k5_style_toc():
    """111 chapters all at level 3 under level-2 group headers; no dots after
    chapter numbers; appendix + legal information trail the last chapter."""
    toc = [(1, "S32K5xx Reference Manual", 1),
           (2, "Power Management", 99), (2, "Safety", 99)]
    pages = {n: 100 + n * 3 for n in range(1, 112)}
    for n in range(1, 112):
        toc.append((3, f"{n} Chapter{n}", pages[n]))
    toc.append((2, "Appendix A", 440))
    toc.append((2, "Legal information", 450))
    return toc, pages


class OutlineTests(unittest.TestCase):
    def test_parse_chapters_finds_contiguous_levels_mixed(self):
        toc, pages = s32g3_style_toc()
        chapters = ec.parse_chapters(toc)
        self.assertEqual([c["number"] for c in chapters], list(range(1, 82)))
        self.assertEqual(chapters[0]["title"], "Chapter1")
        self.assertEqual(chapters[80]["start"], pages[81])

    def test_parse_chapters_accepts_flat_level_shape(self):
        toc, pages = s32k5_style_toc()
        chapters = ec.parse_chapters(toc)
        self.assertEqual([c["number"] for c in chapters], list(range(1, 112)))

    def test_parse_chapters_rejects_broken_outline(self):
        broken = [(1, "1 One", 96), (2, "3 Three", 113)]
        with self.assertRaises(ValueError):
            ec.parse_chapters(broken)

    def test_chapter_range_uses_next_chapter_start(self):
        toc, pages = s32g3_style_toc()
        chapters = ec.parse_chapters(toc)
        self.assertEqual(ec.chapter_range(chapters, toc, 1, 5101), (96, 105))
        self.assertEqual(ec.chapter_range(chapters, toc, 3, 5101), (113, 113))
        self.assertEqual(ec.chapter_range(chapters, toc, 81, 5101),
                         (pages[81], 5082))

    def test_final_chapter_ends_before_trailing_matter(self):
        toc, pages = s32k5_style_toc()
        chapters = ec.parse_chapters(toc)
        # appendix A begins at 440 -> last chapter (433) ends 439
        self.assertEqual(ec.chapter_range(chapters, toc, 111, 460),
                         (pages[111], 439))

    def test_section_tree_is_prefix_scoped(self):
        toc = [(2, "43 Periodic Interrupt Timer (PIT)", 2235),
               (3, "43.1 Chip-specific PIT information", 2235),
               (4, "43.1.1 PIT module instance details", 2235),
               (3, "44.1 Chip-specific FTM information", 2253),
               (4, "43.4 Functional description", 2246)]
        sections = ec.section_tree(toc, 43, 2235, 2252)
        titles = [s["title"] for s in sections]
        self.assertIn("43 Periodic Interrupt Timer (PIT)", titles)
        self.assertIn("43.1 Chip-specific PIT information", titles)
        self.assertNotIn("44.1 Chip-specific FTM information", titles)


class TableTests(unittest.TestCase):
    def test_stitch_drops_repeated_header(self):
        header = ["Field", "Function"]
        grids = [[header, ["31-28", "Reserved"]],
                 [header, ["27-24", "FLTPS"]],
                 [["15-12", "TOF"]]]
        rows = ec.stitch_table_rows(grids)
        self.assertEqual(rows, [header, ["31-28", "Reserved"],
                                ["27-24", "FLTPS"], ["15-12", "TOF"]])

    def test_stitch_keeps_distinct_first_rows(self):
        rows = ec.stitch_table_rows([[["A", "B"]], [["C", "D"]]])
        self.assertEqual(rows, [["A", "B"], ["C", "D"]])


@unittest.skipUnless(os.path.isfile(PDF), "NXP PDF not available (set NXP_TEST_PDF)")
class IntegrationTests(unittest.TestCase):
    def test_page_range_and_target(self):
        report = ec.build_report(PDF, 3, target_root="docs/nxp/s32g3",
                                 sections_only=True)
        self.assertEqual(report["pages"], [113, 113])
        self.assertEqual(report["target"],
                         "docs/nxp/s32g3/ch03_memory_map/index.md")
        self.assertTrue(any(s["title"].startswith("3.1") for s in report["sections"]))

    def test_chapter_78_has_no_chrome(self):
        report = ec.build_report(PDF, 78, sections_only=True)
        self.assertEqual(report["pages"], [4924, 5014])
        self.assertTrue(any(s["title"].startswith("78 ") for s in report["sections"]))

    def test_chapter_1_has_no_chrome(self):
        report = ec.build_report(PDF, 1)
        text = "\n".join(line for p in report["page_text"] for line in p["lines"])
        self.assertIn("1.1 Audience", text)
        for marker in ("NXP Semiconductors", "General Business Information",
                       "/ 5101", "S32G3 Reference Manual"):
            self.assertNotIn(marker, text)


if __name__ == "__main__":
    unittest.main()
