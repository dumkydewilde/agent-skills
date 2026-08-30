# Notebooks

A **sheet** is one field note. A **deck** is the sheets, one per screen, that
you swipe through. A **notebook** is a deck plus the index that opens it. A
**shelf** is the index of notebooks. Three pages, two templates, and one order
to move through them:

**the shelf → a notebook's index → a sheet in its deck.**

| Page | Built from | Is | You are looking at |
|---|---|---|---|
| the shelf | `assets/notebook.html` | one memo book per notebook, opening its index | a desk with the notebooks on it |
| the notebook index | `assets/notebook.html` | one small sheet per note, opening the deck at it | that notebook's notes, spread out on the desk |
| the deck | `assets/field-notes.html` | every sheet in the notebook, one per slide | one note, picked up |

The two indexes are the same component with different content, which is why
they are one file. It ships with both built; **delete the one you are not
delivering.** A page carries a single index.

## Three sizes of delivery

One note is not a small notebook, and a notebook is not a small shelf: each is
the one before it plus a page. Pick the size from what was asked, before writing
anything, because it names the files.

At two notes and up, consider writing them as markdown and building the pages
with `scripts/build.py` — same output, but the ids, hrefs and counts below are
derived instead of typed. `references/markdown-source.md` has the format; what
follows is the structure it produces, and what to do by hand without it.

| Asked for | Deliver | Pages | Built from |
|---|---|---|---|
| one note, one poster, one page field-noted | a **sheet** | `<subject>.html` | the deck template, one slide |
| a notebook, a deck, slides, an overview of notes | a **notebook** | `index.html` + `deck.html` | both templates |
| several subjects or collections, a shelf | a **shelf** | `notebooks.html` + one directory per notebook | both templates, the index one twice |

### A single sheet

Copy `assets/field-notes.html` to `<subject>.html`. Delete the demonstration
slides you are not using, delete the `.home` link — there is no index to return
to — and keep the surviving sheet inside its `<section class="slide" id="…">`.
A deck of one is what a standalone sheet is: it costs nothing, keeps the desk
and the margin, and is the difference between a second note being a card and
being a rebuild. **Set the id even here.**

### A notebook

1. Build the deck first, as `deck.html`: one slide per sheet, in reading order,
   each with a kebab-cased subject id. Point `.home` at `index.html`.
2. Then the index, from `assets/notebook.html` as `index.html`: delete the
   shelf, keep the card grid at `--cols:4`, one card per slide in the same
   order, each `href="deck.html#<id>"`.
3. Marks go in `stamps/<subject>.png`, one per sheet that has one. A sheet whose
   mark is a diagram gets a hatched glyph on its card instead.
4. Point the index's `.home` at `../notebooks.html`, or delete it if no shelf is
   coming.

### Several notebooks

Build each notebook complete before starting the next, in its own directory —
half-built notebooks side by side is how ids and hrefs drift apart. Then the
shelf, from `assets/notebook.html` again as `notebooks.html`: delete the card
grid, keep the memo books at `--cols:5`, one cover per notebook,
`href="<notebook>/index.html"`.

Do not vary the two templates between notebooks. Different stock or a different
grid per notebook makes a set of unrelated sites; the whole point of a shelf is
that they are one collection.

## The file layout

```
notebooks.html              ← the shelf
architecture/
  index.html                ← the notebook index
  deck.html                 ← the deck
  stamps/taj-mahal.png      ← one mark per sheet that has one
water/
  index.html
  deck.html
  stamps/…
```

The links between them are the whole structure, so get them right in this
order: a shelf card points at `<notebook>/index.html`; an index card points at
`deck.html#<slide-id>`; a deck's `.home` link points back at `index.html`, and
an index's `.home` link back at `../notebooks.html`. Delete a `.home` whose
target you are not delivering — a link back to a shelf that does not exist is
worse than no link.

Serve over `http://`. The deck imports Mermaid as an ES module, which fails on
`file://`, and both pages fetch Courier Prime and Font Awesome from the network.

**`assets/examples/notebook/` is that layout, built and live** — a shelf, two
notebooks, five sheets, every link resolving. Open it before building one; it is
faster to click the chain than to reason about it. `references/examples.md` says
what each part of it demonstrates.

## One desk, three views of it

`--desk`, a shade grey of the stock, is the surface under all three pages, and
it never changes. What changes is what is lying on it: notebooks, then that
notebook's notes, then one note filling the screen. Every object on it — a
sheet, a card, a memo book — gets the same three cues, a lit top edge, a tight
contact shadow and one soft cast shadow, so an object is the same object at
every scale.

Nothing is ever printed on the desk itself. A masthead sits on the bare surface
as a label, quiet and small; titles, marks and records are printed on the
objects. **An index is not a page.** A single tall sheet of paper carrying
twelve notes is a document; twelve pieces of paper lying on a desk is a
notebook spread out in front of you, and picking one up is the whole
navigation. If you find yourself putting a paper background behind the grid,
you have turned the notebook back into a printout.

On the deck the same rule reads as a margin: the sheet is the largest 4:3 page
that fits, with a hand's width of desk round it. Keep that margin small. This
is a page held open, not a card floating in a gallery, and every millimetre
added to it is taken off the note.

## The deck

Each sheet is a `<section class="slide" id="…">` inside `<main class="deck">`.
The slide is the screen: it carries the desk and the margin, and the sheet is
the largest 4:3 page that fits inside it — `min(100cqw, 133.334cqh)` against the
slide's padded box, which is why `.slide` is a size container. On a tablet, whose
screen is already 4:3, that is very nearly the whole display.

**Give every slide an id.** It is the deck's anchor — `deck.html#taj-mahal` —
which is what an index card links to, and what the address bar is kept current
with as you move. Use the subject, kebab-cased; do not number them, because
inserting a sheet would then rewrite every link after it.

Swiping is `scroll-snap`, so touch, trackpad and scripted scrolling all land the
same way. The script adds only the keyboard (arrows, space, page keys, home,
end), the jump to `#id` on arrival, and the `replaceState` that keeps the hash
on the sheet you are looking at.

On desktops at least 900px wide, the current sheet is centred with a transparent
sliver of its previous and next neighbours left visible. Click either neighbour
to turn to it. The deck must calculate its snap positions from each slide's
actual centre — not `viewport width × page number` — because the slides are
narrower at this breakpoint. Keep one full opaque page on tablet and phone;
the preview is a wide-desk affordance, not a way to shrink the note.

Delete `.home` when the deck is standalone — a link back to an index that does
not exist is worse than no link.

### Everything on a sheet is a fraction of the sheet

A sheet is as large as the screen allows, so absolute type sizes no longer
work: 12.5px
that reads well on a 1040px sheet is a speck on a 2560px one. `.sheet` defines
`--px` as one pixel at the 1040px reference width, every size is written as
`calc(12.5 * var(--px))`, and `fitEntries` and `fitPlates` do the same
conversion in JS through `unit()`. The design numbers are unchanged; they are
just no longer absolute. **If you add a size to a sheet, write it in `--px`** —
one absolute px among them is invisible at the reference width and wrong
everywhere else.

## The notebook index: notes on the desk

**An index is the notes, not the notebook.** Two things follow from that, and
they are the two things most likely to be undone by someone tidying up:

- **The masthead is set at a card's size**, not as a headline, and it sits on
  the bare desk rather than on anything. The name of the notebook is the least
  surprising thing on its own index; giving it forty points of type spends the
  top of the screen telling the reader what they already know, and pushes the
  notes below the fold.
- **A dozen notes are on screen at once.** Four across puts eight on a laptop
  and twelve on a tablet, which is the whole job: take in the notebook at a
  glance. Anything that costs a row — a bigger title, a second caption line,
  more padding — has to earn it.

**A card is the sheet, shrunk to a hand's width**: the same 4:3, the same
stock, the same three shadow cues as a slide in the deck, with the mark on it
and one line printed under it — the subject and its year, the way a sheet's own
heading reads. Nothing is drawn round it, because the paper's own edge is the
frame, and nothing sits behind it, because it is not a card. It is a piece of
paper you can pick up.

```html
<a class="card" href="deck.html#taj-mahal">
  <span class="frame">
    <img class="mark" src="stamps/taj-mahal.png" alt="" onerror="…">
  </span>
  <h2 class="card-title jitter">Taj Mahal &middot; 1653</h2>
</a>
```

The number, the keywords and the record stay on the sheet, one tap away. Adding
them here is the change that turns an index back into a list.

Everything printed on a card is written in `--px`, the same rule the sheet
uses, against a 340px reference width instead of 1040. `.card` is the container
the `cq` units resolve against, so **a size used in `.card`'s own rule cannot
use them** — put it on a descendant, or write it as a percentage of the card.

A note is laid down by hand, not printed in a grid: a fraction of a degree of
rotation each way, two stocks and three handling-mark positions across the
grid. Keep the tilt under a degree. Past that it is a scatter, and a scatter is
a mood board. On hover the paper straightens and its shadow deepens — the one
gesture allowed, because it is what picking a page up looks like.

The note index moves from four columns on a full desktop to three at 1100px and
two at 820px. Do not jump directly from four to two: it wastes the compact
desktop width and makes the desk feel like a phone app. One column remains the
phone-only fallback at 520px.

The card mark is the sheet's own stamp where the sheet has one. Where the sheet
carries a Mermaid diagram instead, there is no raster to show: use a hatched
Font Awesome glyph, `data-ink` on the card to colour it. Set it small on the
card — a glyph blown up to fill the paper reads as an app icon, and sat small
with stock around it reads as a specimen. Do not screenshot a plate to make a
card mark; a shrunken diagram is illegible at card size and reads as a broken
image.

## The shelf: memo books on the desk

A notebook is not a big note, so it is not drawn as one. It is a 3½ × 5½ memo
book, the object the whole style is named after: kraft cover, black type,
square at the spine and rounded at the fore-edge, two saddle staples set into
the crease, and a sliver of the page block showing past the cover.

```html
<a class="book" href="architecture/index.html">
  <div class="cover">
    <i class="staple"></i><i class="staple"></i>
    <h2 class="cover-title jitter">Architecture</h2>
    <p class="cover-line jitter">Twelve sheets<br>1645&ndash;1973</p>
  </div>
</a>
```

That object is the whole difference between the two indexes: you can see you
are picking up a book here and a loose sheet there before you read a word. So:

- **A cover carries no mark.** A memo book's cover is type — the notes are
  inside it, and putting one of them on the front makes it a sheet with a
  title. The name, and one small line for what is in it.
- **`--kraft`, `--kraft-shade` and `--staple` are the shelf's alone.** Nothing
  on a sheet is kraft, and nothing on the shelf is rag paper except the page
  block.
- **Five across, not four.** A memo book is portrait and half the width of a
  sheet, so more of them fit before they stop looking like books; three on a
  tablet and two on a phone, where a sheet index has dropped to one.
- Cover type is written in `--px` against a 240px reference width.

## What an index does not have

The index is the part of a notebook that most wants to grow fluff, and every
one of these has a paper reason to stay off it:

- **no search, filters, tags or sort controls** — a notebook you cannot take in
  at a glance is too big, and the fix is another notebook;
- **no descriptions or excerpts** — the subject and its year are the index; the
  sheet is one tap away and says the rest;
- **no page under the grid** — an index is objects on a desk, not a document;
- **no UI chrome on an object: no fill behind the paper, no radius on a sheet,
  no border drawn round it, no lift-and-scale on hover.** The only shadow is
  the one the object casts on the desk, and the only hover is the paper
  straightening under a hand. A UI card on rag paper breaks the whole style;
- **no rules or dividers between the columns** — the regions of a sheet meet on
  a paper edge, and so do the objects on a desk;
- **no numbers, keywords, dates, counts or badges beyond the card's one line.**

What an index has instead of all that is the notes themselves, twelve at a
time, lying on the desk.

## Check before delivering

Both templates ship with demonstration content whose links point at files that
do not exist, so a delivery that has not been walked through is a delivery with
dead links in it. Serve it over `http://` and click the whole chain, then check:

- **every slide has an id**, kebab-cased from its subject, and no two the same;
- **every card resolves** — an index card to a slide id that exists in that
  deck, a shelf cover to an `index.html` that exists;
- **every `.home` points at a page you are delivering**, or has been deleted;
- **no demonstration content survives** — no Taj Mahal card, no Beemster sheet
  you did not mean to keep, no `stamps/*.png` for a mark that was never made;
- **one index per page.** Both were built in the file you copied;
- **the counts are true.** A masthead saying twelve sheets over nine cards, or a
  cover saying fourteen over a deck of six, is the one error a reader checks.

The same walk is worth scripting for anything bigger than a couple of
notebooks: `tests/test_notebooks.py` does exactly this over
`assets/examples/notebook/`, and its link checker is short enough to copy.
Building from markdown skips most of this list, because ids, hrefs and counts
are then derived rather than typed — see `references/markdown-source.md`.

Two more, about what leaves your machine:

- **Three things come from the network** — Courier Prime, Font Awesome and, on
  a deck, Mermaid. Offline, the type falls back to Courier New, the glyph marks
  vanish and the plates stay as unrendered code. That is fine for a page shared
  today and not fine for an archive: to make one that keeps, vendor the three
  next to the pages and point the tags at the local copies.
- **Keep a mark under a few hundred kilobytes.** A dozen full-resolution stamps
  is a notebook that takes ten seconds to open on a phone, and a stamp is drawn
  at about 400px on the sheet and 300px on a card. Resize before delivering:
  `sips -Z 900 stamp.png --out stamps/subject.png`.
