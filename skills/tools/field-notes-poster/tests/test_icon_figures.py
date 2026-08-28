"""Regression checks for the icon figures on the field-notes sheet."""

from pathlib import Path
import unittest


SKILL_ROOT = Path(__file__).parents[1]
TEMPLATE = SKILL_ROOT / "assets" / "field-notes.html"
REFERENCE = SKILL_ROOT / "references" / "web-template.md"


class IconFigureTest(unittest.TestCase):
    def setUp(self) -> None:
        self.template = TEMPLATE.read_text()

    def test_font_awesome_is_loaded_and_used_for_figures_and_inline_icons(self) -> None:
        self.assertIn("fontawesome-free", self.template)
        self.assertIn('class="figs"', self.template)
        self.assertIn('class="glyph hatch fa-solid', self.template)
        self.assertIn('class="ic fa-solid', self.template)

    def test_glyphs_are_hatched_rather_than_solid(self) -> None:
        """A solid silhouette is the modern tell; tone comes from ruled fill."""
        self.assertIn("background-clip:text", self.template)
        self.assertIn("repeating-linear-gradient(\n    var(--hatch,48deg)", self.template)
        # The ruling direction has to vary, or the plate reads as one texture.
        for nth in ("3n+1", "3n+2", "3n+3"):
            self.assertIn(f".figs .fig:nth-child({nth})", self.template)

    def test_figures_carry_enough_ink_to_read_on_cream(self) -> None:
        """At ~32% coverage and no contour the figures came out washed out."""
        # ~52% ink: 1.1px ruled in a 2.1px period.
        self.assertIn("var(--mark) 0 1.1px,\n    transparent 1.1px 2.1px", self.template)
        # The keyline. Hatching with no edge lets the ruling eat the silhouette.
        self.assertIn("-webkit-text-stroke:.55px var(--mark)", self.template)
        # Goldenrod is light enough to need a carbon edge instead of its own.
        self.assertIn('[data-ink="c2"].fig .glyph.hatch::before', self.template)
        self.assertIn("-webkit-text-stroke-color:var(--ink)", self.template)

    def test_figure_layout_keeps_the_two_collapse_fixes(self) -> None:
        """Both were real bugs: frames collapsed to thumbnails without them."""
        # <figure>'s UA margin (1em 40px) eats half a grid column.
        self.assertIn(".fig{display:flex;flex-direction:column;gap:.7em;min-width:0;margin:0;}",
                      self.template)
        # .plate's justify-items:center makes the grid shrink-to-fit.
        self.assertIn(".plate--large:has(.figs){place-items:center stretch", self.template)

    def test_reference_documents_the_period_treatment_and_its_limits(self) -> None:
        reference = REFERENCE.read_text()

        self.assertIn("## Figures", reference)
        self.assertIn("cannot be made period", reference)
        self.assertIn("clarification, not", reference)


if __name__ == "__main__":
    unittest.main()
