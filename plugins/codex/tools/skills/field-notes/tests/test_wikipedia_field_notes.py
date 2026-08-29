"""Regression checks for the Wikipedia field-notes route."""

from pathlib import Path
import unittest


SKILL_ROOT = Path(__file__).parents[1]


class WikipediaFieldNotesTest(unittest.TestCase):
    def test_skill_routes_wikipedia_pages_to_a_standalone_sheet(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text()

        self.assertIn("Wikipedia", skill)
        self.assertIn("references/wikipedia-field-notes.md", skill)
        self.assertIn("standalone", skill)
        self.assertIn("rubber-stamp sketch", skill)

    def test_reference_requires_factual_notes_and_source_attribution(self) -> None:
        reference = (SKILL_ROOT / "references" / "wikipedia-field-notes.md").read_text()

        self.assertIn("page/summary", reference)
        self.assertIn("imageinfo", reference)
        self.assertIn("underlines only", reference)
        self.assertIn("CC BY-SA", reference)

    def test_route_requires_crimson_template_underlines(self) -> None:
        skill = (SKILL_ROOT / "SKILL.md").read_text()
        reference = (SKILL_ROOT / "references" / "wikipedia-field-notes.md").read_text()

        self.assertIn('data-ink="c1"', skill)
        self.assertIn('<span class="ul" data-ink="c1">', reference)
        self.assertIn("crimson", reference)

    def test_route_requires_the_template_drawn_underline_renderer(self) -> None:
        reference = (SKILL_ROOT / "references" / "wikipedia-field-notes.md").read_text()

        self.assertIn("`.marks .mk--ul`", reference)
        self.assertIn("not a `.ul::after`", reference)


if __name__ == "__main__":
    unittest.main()
