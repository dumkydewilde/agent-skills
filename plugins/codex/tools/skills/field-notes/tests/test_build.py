"""The markdown build: what a note file turns into, and what it must not lose."""

from pathlib import Path
import importlib.util
import re
import sys
import tempfile
import unittest


SKILL_ROOT = Path(__file__).parents[1]
EXAMPLE_NOTES = SKILL_ROOT / "assets" / "examples" / "notes"

spec = importlib.util.spec_from_file_location("fnbuild", SKILL_ROOT / "scripts" / "build.py")
build = importlib.util.module_from_spec(spec)
# Registered before it is executed: a dataclass resolves its annotations
# through sys.modules, and a module that is not there yet has none.
sys.modules["fnbuild"] = build
spec.loader.exec_module(build)


class FrontMatterTest(unittest.TestCase):
    def test_it_reads_pairs_and_lists(self) -> None:
        meta, body = build.parse_front_matter(
            "---\ntitle: Molengang\nfigures:\n  - fa-fan | Wind | c5\n"
            "  - fa-water | Basin\n---\n\nThe body.\n")
        self.assertEqual(meta["title"], "Molengang")
        self.assertEqual(meta["figures"], ["fa-fan | Wind | c5", "fa-water | Basin"])
        self.assertEqual(body.strip(), "The body.")

    def test_a_note_without_front_matter_is_still_a_note(self) -> None:
        meta, body = build.parse_front_matter("Just a record.\n")
        self.assertEqual(meta, {})
        self.assertEqual(body.strip(), "Just a record.")

    def test_an_unclosed_block_is_an_error_not_a_silent_body(self) -> None:
        with self.assertRaises(ValueError):
            build.parse_front_matter("---\ntitle: Oops\n\nbody\n")


class InlineMarkTest(unittest.TestCase):
    def test_the_three_annotations_and_the_inline_icon(self) -> None:
        self.assertEqual(build.inline("a ==sweep== b"),
                         'a <mark class="hl">sweep</mark> b')
        self.assertEqual(build.inline("==tinted=={.c3}"),
                         '<mark class="hl" data-ink="c3">tinted</mark>')
        self.assertEqual(build.inline("[fact]{.ul .c1}"),
                         '<span class="ul" data-ink="c1">fact</span>')
        self.assertEqual(build.inline("[name]{.ring .c4}"),
                         '<span class="ring" data-ink="c4">name</span>')
        self.assertIn('<i class="ic fa-solid fa-fan" aria-hidden="true"></i>',
                      build.inline("wind :fa-fan: drove it"))
        self.assertIn('data-ink="c1"', build.inline(":fa-industry.c1:"))

    def test_a_bracketed_span_that_is_not_ours_is_left_alone(self) -> None:
        """Markdown in the wild has [text]{…}; only the mark classes are taken."""
        self.assertEqual(build.inline("[text]{.footnote}"), "[text]{.footnote}")

    def test_the_source_wrap_is_not_the_sheet_wrap(self) -> None:
        """`.body` is pre-wrap: a hard-wrapped source would print as ragged."""
        self.assertEqual(build.unwrap("one\ntwo\n\nthree\nfour"),
                         "one two\n\nthree four")


class NoteTest(unittest.TestCase):
    def note(self, text: str, name: str = "01-molengang.md") -> "build.Note":
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / name
            path.write_text(text)
            return build.read_note(path)

    def test_the_order_prefix_never_reaches_the_anchor(self) -> None:
        """Re-ordering a deck must not rewrite every index card's href."""
        self.assertEqual(self.note("---\ntitle: Molengang\n---\n").id, "molengang")

    def test_the_variant_is_inferred_from_what_the_note_carries(self) -> None:
        self.assertEqual(self.note("---\nphoto: p.jpg\n---\n").variant, "A")
        self.assertEqual(self.note("---\ntitle: X\n---\n\nA record.\n").variant, "B")
        self.assertEqual(
            self.note("---\ntitle: X\n---\n\n```mermaid\nflowchart TB\n  A-->B\n```\n").variant,
            "C")
        # An entry that also carries a small plate has to say so.
        self.assertEqual(
            self.note("---\nvariant: B\n---\n\n```mermaid\nflowchart TB\n  A-->B\n```\n").variant,
            "B")

    def test_the_mermaid_block_becomes_the_plate_and_leaves_the_body(self) -> None:
        note = self.note("---\ntitle: X\n---\n\n```mermaid\nflowchart TB\n  A-->B\n```\n\nAfter.\n")
        self.assertIn("flowchart TB", note.mermaid)
        self.assertEqual(note.body, "After.")
        self.assertNotIn("```", note.body)


class BuildTest(unittest.TestCase):
    """Build the worked markdown example and check what came out."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls._tmp.name)
        build.main([str(EXAMPLE_NOTES), "-o", str(cls.out)])

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def test_a_folder_of_folders_builds_a_shelf(self) -> None:
        for page in ("notebooks.html", "beemster/index.html", "beemster/deck.html",
                     "elsewhere/index.html", "elsewhere/deck.html"):
            self.assertTrue((self.out / page).is_file(), page)

    def test_the_marks_travel_with_the_notes(self) -> None:
        self.assertTrue((self.out / "beemster" / "stamps" / "molengang.jpg").is_file())
        self.assertTrue((self.out / "elsewhere" / "photos" / "amsterdam-centraal.jpg").is_file())

    def test_every_link_it_writes_resolves(self) -> None:
        pattern = re.compile(r'(?:href|src)="([^"#][^"]*)"')
        for page in self.out.rglob("*.html"):
            for target in pattern.findall(page.read_text()):
                if target.startswith(("http", "data:")):
                    continue
                path, _, anchor = target.partition("#")
                resolved = (page.parent / path).resolve()
                self.assertTrue(resolved.is_file(), f"{page.name} → {target}")
                if anchor:
                    self.assertIn(f'id="{anchor}"', resolved.read_text())

    def test_the_counts_are_counted_rather_than_typed(self) -> None:
        shelf = (self.out / "notebooks.html").read_text()
        self.assertEqual(shelf.count('<a class="book"'), 2)
        self.assertEqual((self.out / "beemster" / "index.html").read_text()
                         .count('<a class="card"'), 3)
        self.assertEqual((self.out / "beemster" / "deck.html").read_text()
                         .count('<section class="slide" id='), 3)

    def test_it_generates_the_templates_classes_and_no_others(self) -> None:
        """The stylesheet is the template's; a class it does not carry is dead."""
        template = (SKILL_ROOT / "assets" / "field-notes.html").read_text()
        deck = (self.out / "beemster" / "deck.html").read_text()
        slides = deck.split('<main class="deck">', 1)[1]
        for klass in set(re.findall(r'class="([a-z0-9 _-]+)"', slides)):
            for name in klass.split():
                if name.startswith("fa-"):
                    continue          # Font Awesome's, from its own stylesheet
                self.assertIn(f".{name}", template, f"{name} is not in the stylesheet")

    def test_a_single_note_builds_a_sheet_with_no_way_back(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            build.main([str(EXAMPLE_NOTES / "beemster" / "01-molengang.md"), "-o", tmp])
            sheet = (Path(tmp) / "molengang.html").read_text()
            self.assertIn('<section class="slide" id="molengang">', sheet)
            self.assertEqual(sheet.count('<section class="slide" id='), 1)
            # There is no index to return to, so there is no link to one.
            self.assertNotIn('class="home"', sheet)

    def test_a_folder_of_notes_builds_one_notebook(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            build.main([str(EXAMPLE_NOTES / "beemster"), "-o", tmp])
            index = (Path(tmp) / "index.html").read_text()
            self.assertIn('<a class="card" href="deck.html#molengang"', index)
            # Standalone: no shelf above it to link back to.
            self.assertNotIn("notebooks.html", index)
            self.assertIn('<a class="home" href="index.html">',
                          (Path(tmp) / "deck.html").read_text())


class ShippedExampleIsCurrentTest(unittest.TestCase):
    def test_the_built_example_matches_a_fresh_build(self) -> None:
        """`assets/examples/notebook/` is the build of `assets/examples/notes/`.

        It is committed so it can be opened without running anything, which
        means it goes stale the moment a template changes. Rebuild it:

            uv run scripts/build.py assets/examples/notes -o assets/examples/notebook
        """
        shipped = SKILL_ROOT / "assets" / "examples" / "notebook"
        with tempfile.TemporaryDirectory() as tmp:
            build.main([str(EXAMPLE_NOTES), "-o", tmp])
            fresh = Path(tmp)
            self.assertEqual(
                sorted(p.relative_to(fresh).as_posix() for p in fresh.rglob("*")),
                sorted(p.relative_to(shipped).as_posix() for p in shipped.rglob("*")))
            for page in fresh.rglob("*.html"):
                self.assertEqual(page.read_text(),
                                 (shipped / page.relative_to(fresh)).read_text(),
                                 f"{page.name} is stale — rebuild the example")


class TemplateHintTest(unittest.TestCase):
    def test_the_deck_says_so_when_it_is_opened_from_the_filesystem(self) -> None:
        """Without it, a deck on file:// looks like one that was built wrong."""
        deck = (SKILL_ROOT / "assets" / "field-notes.html").read_text()
        hint = deck.split('if (location.protocol === "file:")', 1)[1]
        self.assertIn("SERVE THIS OVER HTTP", hint)
        # A module would fail for the very reason it is warning about.
        self.assertIn("<script>\nif (location.protocol", deck)


if __name__ == "__main__":
    unittest.main()
