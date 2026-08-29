"""Regression checks for the deck and for the notebook index pages."""

from pathlib import Path
import re
import unittest


SKILL_ROOT = Path(__file__).parents[1]
DECK = SKILL_ROOT / "assets" / "field-notes.html"
INDEX = SKILL_ROOT / "assets" / "notebook.html"
REFERENCE = SKILL_ROOT / "references" / "notebooks.md"


class DeckTest(unittest.TestCase):
    def setUp(self) -> None:
        self.deck = DECK.read_text()

    def test_sheets_are_slides_in_a_snapping_deck(self) -> None:
        self.assertIn('<main class="deck">', self.deck)
        self.assertIn("scroll-snap-type:x mandatory", self.deck)
        self.assertIn("scroll-snap-align:center", self.deck)
        # Every sheet is a slide, and every slide is anchorable from an index.
        self.assertEqual(self.deck.count('<div class="sheet"'),
                         self.deck.count('<section class="slide" id="'))

    def test_the_sheet_is_a_page_lying_on_a_desk(self) -> None:
        """The margin and the shadow are what make it a page, not a background."""
        slide = self.deck.split(".slide{", 1)[1].split("}", 1)[0]
        self.assertIn("background:var(--desk)", slide)
        self.assertIn("padding:4vmin", slide)
        # A padded slide has to be a size container, or the sheet cannot be
        # measured against the padded box and its corners go under the margin.
        self.assertIn("container-type:size", slide)

        sheet = self.deck.split("\n.sheet{", 1)[1].split("}", 1)[0]
        self.assertIn("background-color:var(--paper)", sheet)
        self.assertIn("radial-gradient", sheet)
        self.assertIn("box-shadow", sheet)
        # cq units, not vw/vh: the viewport ignores the margin.
        self.assertIn("width:min(100cqw, 133.334cqh)", sheet)

    def test_a_sheet_is_measured_as_a_fraction_of_itself(self) -> None:
        """Absolute px on a full-screen sheet is a speck on a large display."""
        self.assertIn("--px: calc(100cqw / 1040)", self.deck)
        for size in ("13", "12.5", "12", "11", "10", "9"):
            self.assertIn(f"font-size:calc({size}*var(--px))", self.deck)
        # The JS fitters have to agree with the stylesheet.
        self.assertIn('const unit = el => (el.closest(".sheet")?.clientWidth || 1040) / 1040',
                      self.deck)
        self.assertIn("2.2 * unit(plate)", self.deck)

    def test_the_deck_is_navigable_without_a_touchscreen(self) -> None:
        self.assertIn("ArrowRight", self.deck)
        self.assertIn("ArrowLeft", self.deck)
        # Swiping a deck must not fill the back button with every sheet passed.
        self.assertIn("history.replaceState", self.deck)
        self.assertNotIn("history.pushState", self.deck)

    def test_printing_takes_the_deck_apart_again(self) -> None:
        printed = self.deck.split("@media print{", 1)[1]
        self.assertIn("page-break-after:always", printed)
        self.assertIn(".home{display:none;}", printed)
        # On paper the page IS the sheet: no desk, no margin, no shadow.
        self.assertIn("padding:0;background:none", printed)
        self.assertIn("box-shadow:none", printed)

    def test_a_printed_deck_is_one_sheet_per_page(self) -> None:
        """Both halves of this were one-page-for-the-whole-deck bugs.

        A size container is size-contained, so `height:auto` on a slide
        resolves to zero and every sheet stacks at the same origin; and a
        viewport unit in paged layout has no viewport to resolve against, which
        collapses them the same way. Physical units, and no containment.
        """
        printed = self.deck.split("@media print{", 1)[1]
        self.assertIn("@page{size:A4 landscape;margin:0;}", printed)
        self.assertIn("container-type:normal", printed)
        self.assertIn("width:270mm;height:202.5mm", printed)
        slide_rule = printed.split(".slide{", 1)[1].split("}", 1)[0]
        for viewport_unit in ("vh", "vmin", "cqh", "cqw"):
            self.assertNotIn(viewport_unit, slide_rule)


class NotebookIndexTest(unittest.TestCase):
    def setUp(self) -> None:
        self.index = INDEX.read_text()

    def test_both_index_shapes_ship_from_the_one_file(self) -> None:
        self.assertIn('class="cards" style="--cols:4"', self.index)  # sheets
        # A memo book is portrait and half a sheet's width, so more fit across.
        self.assertIn('class="cards cards--shelf" style="--cols:5"', self.index)
        self.assertIn("grid-template-columns:repeat(var(--cols,4),minmax(0,1fr))",
                      self.index)

    def test_four_across_is_held_down_to_phone_width(self) -> None:
        """Twelve marks on a tablet is the job; two columns at 1024 is an app."""
        self.assertIn("@media (max-width:820px){.cards{grid-template-columns:repeat(2",
                      self.index)
        self.assertNotIn("max-width:1180px", self.index)

    def test_the_index_is_objects_on_the_desk_and_not_a_page(self) -> None:
        """A page carrying twelve notes is a document; the notes lie loose."""
        self.assertNotIn(".page{", self.index)
        # The desk is a width to lay things out on: no stock, no shadow.
        desk = self.index.split("\n.desk{", 1)[1].split("}", 1)[0]
        for printed in ("background", "box-shadow", "border"):
            self.assertNotIn(printed, desk)
        # The gutter is the body's, and the surface is the same as a slide's.
        self.assertIn("margin:0;padding:0 4vmin", self.index)
        self.assertIn("background:var(--desk)", self.index)

    def test_a_note_card_is_the_sheet_shrunk_to_a_hands_width(self) -> None:
        """Same page, same stock, same three shadow cues as a slide's sheet."""
        card = self.index.split("\n.card{", 1)[1].split("}", 1)[0]
        self.assertIn("aspect-ratio:4/3", card)
        self.assertIn("background-color:var(--paper)", card)
        self.assertIn("radial-gradient", card)
        self.assertIn("box-shadow", card)
        # Sized against itself, as a sheet is: --px at a 340px reference width.
        self.assertIn("--px: calc(100cqw / 340)", card)
        self.assertIn("font-size:calc(13*var(--px))", self.index)

    def test_a_notebook_is_a_memo_book_and_not_a_big_note(self) -> None:
        """3.5 x 5.5, kraft, staples in the spine, a page block behind it."""
        book = self.index.split("\n.book{", 1)[1].split("}", 1)[0]
        self.assertIn("aspect-ratio:3.5/5.5", book)
        cover = self.index.split("\n.cover{", 1)[1].split("}", 1)[0]
        self.assertIn("background-color:var(--kraft)", cover)
        # Square at the spine, rounded at the fore-edge.
        self.assertIn("border-radius:calc(2*var(--px)) calc(14*var(--px))", cover)
        self.assertIn(".cover::before{", self.index)   # the page block
        self.assertIn('<i class="staple"></i><i class="staple"></i>', self.index)
        # A cover is type: the notes are inside it, not printed on the front.
        shelf = self.index.split('class="cards cards--shelf"', 1)[1] \
                          .split("</main>", 1)[0]
        self.assertNotIn("glyph", shelf)
        self.assertNotIn('class="mark"', shelf)

    def test_cards_link_a_notebook_to_its_deck_and_a_shelf_to_its_notebooks(self) -> None:
        self.assertIn('href="deck.html#taj-mahal"', self.index)
        self.assertIn('href="architecture/index.html"', self.index)
        # And an index links back up to the shelf, as a deck does to an index.
        self.assertIn('class="home" href="../notebooks.html"', self.index)

    def test_a_portrait_mark_cannot_stretch_its_own_frame(self) -> None:
        """In flow, the frame's aspect-ratio loses to the image's own height."""
        self.assertIn(".card .mark, .card .mark-missing{\n  position:absolute;",
                      self.index)
        self.assertIn("object-fit:contain", self.index)

    def test_the_paper_is_the_frame_and_not_a_ui_card(self) -> None:
        """Nothing is drawn round the mark: a sheet's regions meet on an edge."""
        frame = self.index.split(".card .frame{", 1)[1].split("}", 1)[0]
        for chrome in ("border", "border-radius", "box-shadow", "background"):
            self.assertNotIn(chrome, frame)
        card = self.index.split("\n.card{", 1)[1].split("}", 1)[0]
        self.assertNotIn("border-radius", card)

    def test_hover_picks_the_paper_up_rather_than_lifting_a_card(self) -> None:
        hover = self.index.split(".card:hover,.card:focus-visible{", 1)[1] \
                          .split("}", 1)[0]
        self.assertIn("transform:rotate(0deg)", hover)
        for ui in ("scale(", "translateY", "background"):
            self.assertNotIn(ui, hover)

    def test_the_notebooks_own_title_is_no_bigger_than_a_cards(self) -> None:
        """An index is the notes; a headline for the notebook pushes them down."""
        masthead = self.index.split(".title{", 1)[1].split("}", 1)[0]
        card_title = self.index.split(".card-title{", 1)[1].split("}", 1)[0]
        # 13px at the masthead's widest, and 13 reference px on a card, which
        # is what --px resolves to at the 340px card the grid is drawn for.
        self.assertIn("font-size:clamp(13px,1.15vw,18px)", masthead)
        self.assertIn("font-size:calc(13*var(--px))", card_title)

    def test_a_card_is_a_mark_and_one_line(self) -> None:
        """Number, keywords and record stay on the sheet: they cost a row here."""
        self.assertIn("Taj Mahal &middot; 1653", self.index)
        self.assertNotIn("card-meta", self.index)
        # Twelve cards ship, because twelve on screen is the thing to demonstrate.
        self.assertEqual(self.index.count('<a class="card" href="deck.html#'), 12)


class WorkedNotebookExampleTest(unittest.TestCase):
    """`assets/examples/notebook/` is the three pages, wired up and runnable.

    The templates ship with demonstration content whose links deliberately
    point at files that do not exist. This example is the one place the whole
    chain resolves, so it is also the only place a broken link is a bug.

    It is the build of `assets/examples/notes/`; `test_build.py` holds it to
    that, so it cannot drift away from the templates it was built from.
    """

    EXAMPLE = SKILL_ROOT / "assets" / "examples" / "notebook"

    def test_the_example_carries_all_three_pages(self) -> None:
        for page in ("notebooks.html",
                     "beemster/index.html", "beemster/deck.html",
                     "elsewhere/index.html", "elsewhere/deck.html"):
            self.assertTrue((self.EXAMPLE / page).is_file(), page)

    def test_every_link_in_it_resolves(self) -> None:
        """shelf → index → deck#slide, and every mark it asks for."""
        pattern = re.compile(r'(?:href|src)="([^"#][^"]*)"')
        checked = 0
        for page in self.EXAMPLE.rglob("*.html"):
            text = page.read_text()
            for target in pattern.findall(text):
                if target.startswith(("http", "data:")):
                    continue
                path, _, anchor = target.partition("#")
                resolved = (page.parent / path).resolve()
                self.assertTrue(resolved.is_file(),
                                f"{page.name} → {target} does not exist")
                if anchor:
                    self.assertIn(f'id="{anchor}"', resolved.read_text(),
                                  f"{page.name} → {target} has no such slide")
                checked += 1
        self.assertGreater(checked, 8)

    def test_the_way_back_up_is_wired_at_every_level(self) -> None:
        deck = (self.EXAMPLE / "beemster" / "deck.html").read_text()
        index = (self.EXAMPLE / "beemster" / "index.html").read_text()
        shelf = (self.EXAMPLE / "notebooks.html").read_text()

        self.assertIn('<a class="home" href="index.html">', deck)
        self.assertIn('<a class="home" href="../notebooks.html">', index)
        # The shelf is the top of the chain: there is nowhere above it, and a
        # link to a page that does not exist is worse than no link.
        self.assertNotIn('class="home"', shelf)

    def test_it_demonstrates_both_kinds_of_card_mark(self) -> None:
        cards = "".join((self.EXAMPLE / n / "index.html").read_text()
                        for n in ("beemster", "elsewhere"))
        # A raster mark, where the sheet has one …
        self.assertIn('class="mark" src="stamps/molengang.jpg"', cards)
        # … a hatched glyph, where the sheet carries a diagram instead …
        self.assertIn('class="glyph hatch', cards)
        # … and the fallback every raster card carries for a mark not yet made.
        self.assertIn("mark-missing", cards)


class NotebookRoutingTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skill = (SKILL_ROOT / "SKILL.md").read_text()

    def test_the_skill_routes_a_collection_to_the_reference(self) -> None:
        self.assertIn("references/notebooks.md", self.skill)
        self.assertIn("assets/notebook.html", self.skill)
        for trigger in ("notebook", "deck", "index"):
            self.assertIn(trigger, self.skill)

    def test_the_skill_sizes_the_delivery_before_the_content(self) -> None:
        """One note, one notebook and a shelf name different files."""
        shape = self.skill.split("## Decide the shape before the content", 1)[1] \
                          .split("\n## ", 1)[0]
        for page in ("<subject>.html", "index.html", "deck.html",
                     "notebooks.html", "stamps/"):
            self.assertIn(page, shape)
        # The decision has to come before the variant and the prompt slots.
        self.assertLess(self.skill.index("## Decide the shape"),
                        self.skill.index("## Pick the variant"))

    def test_a_standalone_sheet_still_gets_an_anchor(self) -> None:
        """It is what makes a second note a card instead of a rebuild."""
        self.assertIn("Give every slide an id even on a standalone sheet",
                      self.skill)
        self.assertIn("Set the id even here", REFERENCE.read_text())

    def test_the_reference_carries_a_build_order_for_each_size(self) -> None:
        reference = REFERENCE.read_text()

        for heading in ("### A single sheet", "### A notebook",
                        "### Several notebooks"):
            self.assertIn(heading, reference)
        # And a gate to walk before delivering any of them.
        gate = reference.split("## Check before delivering", 1)[1]
        for check in ("every slide has an id", "every card resolves",
                      "no demonstration content survives", "the counts are true"):
            self.assertIn(check, gate)

    def test_the_reference_carries_the_linking_contract(self) -> None:
        reference = REFERENCE.read_text()

        self.assertIn("deck.html#", reference)
        self.assertIn("index.html", reference)
        self.assertIn("--px", reference)
        # The order the three pages are moved through, in the reference.
        self.assertIn("the shelf → a notebook's index → a sheet in its deck",
                      reference)
        # The list of what an index does not get to have is the point of it.
        self.assertIn("no search, filters, tags or sort controls", reference)
        self.assertIn("no page under the grid", reference)


if __name__ == "__main__":
    unittest.main()
