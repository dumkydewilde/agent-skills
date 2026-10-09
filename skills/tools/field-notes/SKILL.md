---
name: field-notes
description: >
  Use when the user wants a "field notes" poster, plate, card, or sheet: a
  hand-made mark on aged paper paired with a photo, a written observation, or a
  large drawn diagram, captioned in typewriter type. Triggers on "field notes",
  "field note style", "rubber stamp poster", "travel poster from this photo",
  "stamp sketch", "naturalist plate", "specimen card", "aged paper poster",
  "make a poster from these photos", "field-note a Wikipedia page", and on
  wanting a diagram, chart, or mermaid graph to look hand-drawn, printed,
  painted, or annotated on paper rather than rendered by a computer. Also use
  when the user supplies photos or a Wikipedia URL and asks for one poster per
  subject, and when several sheets have to be collected — a "notebook", a
  "deck" or "slides" of field notes, an "overview" or "index" page of notes or
  notebooks, a "shelf" of several notebooks, or a set to swipe through on a
  tablet. Covers all three sizes: one standalone note, one notebook of notes,
  and a collection of notebooks.
---

# Field Notes Poster

![Twelve food sheets laid out on a notebook index, each a drawn mark on pale
paper captioned in typewriter type](assets/examples/food-notebook-index-rendered.jpg)

*One notebook of twelve sheets, built from markdown by `scripts/build.py`. It is
the food notebook on [dumky.net](https://www.dumky.net/field-notes/), where the
whole shelf is live.*

A field-notes sheet is 4:3 landscape, split into two regions with no dividing
rule: one carries the record, the other carries a hand-made mark, captioned in
small typewriter type on aged paper. Whitespace is part of the layout, not space
left over.

## Decide the shape before the content

How many notes, and are they collected? This decides the filenames, and turning
one shape into another afterwards means rewriting every link.

| Asked for | Deliver | Files |
|---|---|---|
| one note, one poster, one page field-noted | a **sheet** — a deck of one | `<subject>.html` |
| a notebook, a deck, slides, an overview or index of notes | a **notebook** — an index over a deck | `index.html`, `deck.html`, `stamps/` |
| several subjects or collections, a shelf, an index of notebooks | a **shelf** over notebooks | `notebooks.html`, then `<notebook>/index.html` + `deck.html` each |

Each is the one below it plus a page, built from the same two templates:

- **a sheet** — copy `assets/field-notes.html`, keep one slide, delete the
  `.home` link and the other demonstration sheets;
- **a notebook** — the same file as `deck.html`, one slide per sheet; then
  `assets/notebook.html` as `index.html`, keeping the sheet cards and deleting
  the shelf;
- **a shelf** — one directory per notebook as above, plus `assets/notebook.html`
  again as `notebooks.html`, keeping the memo books and deleting the cards.

Scaling up is cheap in one direction only, sheet → notebook → shelf, and only if
the anchors exist. **Give every slide an id even on a standalone sheet**, and a
second note later is a card pointing at it rather than a rebuild.

This sizes a **web** delivery. Image prompts have no files: it is one prompt per
sheet at every size. A notebook whose marks are stamps needs both routes —
prompts first, then the generated images into `stamps/` and the sheets into the
deck.

**Write the notes as markdown when there is more than one, or when the text will
be revised.** `scripts/build.py` turns a folder of `.md` files into the deck,
the index and the shelf, so ids, links and counts are derived rather than typed:

```bash
uv run scripts/build.py notes/ -o site/
```

Front matter carries the subject, year, number, keywords and mark; the body
carries the record, with `==highlights==`, `[underlines]{.ul .c1}`,
`[rings]{.ring .c4}`, `:fa-icons:` and Mermaid blocks. Read
`references/markdown-source.md` for the format. Hand-build from the template
instead when a sheet needs markup the format has no field for, and keep that
deck hand-built: a build overwrites the deck it generates.

`references/notebooks.md` has the build order, the linking contract and the
checks. `assets/examples/notebook/` is a shelf, two notebooks and five sheets
with every link live — open it before building the first one.

## From a source URL

For a browser bookmark that starts a new Field Notes request from the page in
front of you, read `references/bookmarklet.md`. It lets the user choose between
ChatGPT web, Claude Desktop, and Codex Desktop. Use ChatGPT web as the portable
default; Claude Desktop has a documented new-chat deep link, while the Codex
Desktop option is version-dependent and must be described as such.

When a user arrives with a URL, open and read the source before choosing a
variant or writing the note. Treat the page title and URL as a lead, not as
facts: retain a visible source link, distinguish the source's claims from your
observations, and ask for pasted text when an article cannot be accessed. Use
the dedicated Wikipedia route for Wikipedia pages; for other articles, infer
the sheet, notebook, or shelf from the user's request rather than treating one
URL as an instruction to make one fixed kind of deliverable.

## Route first: prompt, web, or cited-source web

| When the mark is | Make it | Because |
|---|---|---|
| **pictorial** — a skyline, landform, building, specimen | an image prompt → `references/prompt-templates.md` | only an image model can draw a carved stamp of a real place |
| **a diagram** — a system, mechanism, route, process, chart | the web template → `references/web-template.md` | the Mermaid source *is* the mark, so it is exact rather than described |
| **both** — a photo plus a stamp | prompt for the stamp, then place it in the web template's variant A | |
| **a Wikipedia page** | a standalone source-note sheet → `references/wikipedia-field-notes.md` | facts stay verifiable, while the lead image becomes a generated stamp sketch |

Prefer the web template whenever the text must stay editable, selectable, or
printable. Prefer the prompt when the mark has to look drawn by hand from life.

More than one sheet is built inside the structure above, never as loose files
collected afterwards. Read **`references/notebooks.md`** before the first sheet,
not after the last one.

## Pick the variant

| Variant | Left region | Right region | Needs |
|---|---|---|---|
| **A — photo-stamp** | the photo, 58%, preserved | mark + caption, 42% | one photo per poster |
| **B — notes-primary** | typewriter entry, ~58% | small mark + caption, ~42% | a subject, source page, or what to record |
| **C — plate-primary** | large plate or diagram, ~66% | narrow text column, ~34% | a subject to draw |

Infer it from what the user brought, and say which you picked:

- photos, no text → **A**
- a report, log, observation, or "write up X" → **B**
- "diagram", "plate", "cutaway", "map", "chart", "big sketch" → **C**
- a Wikipedia page → **B**, with the source-note pattern

Ask only when two variants would produce genuinely different work and the inputs
don't lean either way.

## Writing an image prompt

Read `references/prompt-templates.md` and concatenate its six blocks **in this
order**: `CANVAS`, the variant's `LAYOUT`, `MARK` plus the matching subject row,
`INK-AND-PRINT`, `TYPE` plus the variant's filled text, `AVOID`.

Look at `assets/examples/` first, with `references/examples.md` for what each
one demonstrates: a finished Amsterdam Centraal sheet and two marks. Ink
economy, carving texture and how much to leave out are all faster to calibrate
by eye than from the block text.

Resolve every slot yourself — an unfilled slot is where a model invents slogans
and misspells place names:

- `{{subject_name}}` — place, object, or system, in caps, spelled correctly
- `{{number}}` — `No. 01`, incrementing across a series in one request
- `{{keywords}}` — exactly three short lowercase words, `/`-separated
- `{{year}}` — Gregorian, four digits
- `{{body}}` (B, C) — the actual observation lines, written out
- `{{plate}}` (B, C) — what the mark depicts: the parts, their arrangement, the
  order to read them in
- `{{inks}}` (B, C) — which ink carries which element

Variant A takes `{{plate}}` and `{{inks}}` from the photograph. B and C have no
source to read, so without them a text-to-image model invents a stand-in.

**Delivery.** One prompt per poster, each in its own fenced block, labelled with
its subject. Never one prompt for a grid or collage: five photos is five prompts.
Say which model to run it in — variant A needs an image-input model (Nano Banana,
GPT-Image edit, Midjourney with a reference) because the photo must survive
unredrawn; B and C are text-to-image and work anywhere.

## Field-noting a Wikipedia page

Use the **B** geometry: factual typewritten observations on the left, a small
rubber-stamp sketch on the right. Read `references/wikipedia-field-notes.md`
before fetching, writing, or generating the mark.

This is a **standalone output**, not a new sheet in
`assets/field-notes.html`. Copy the web template to the requested destination,
delete its demonstration sheets, and retain only the Wikipedia sheet — kept in
its slide, since a deck of one is what a standalone sheet is. Several pages at
once is a notebook rather than several files: one slide each in one deck, with
an index over them. The source image is reference material for an
image-to-image rubber-stamp sketch; never drop a monochrome or CSS-filtered
photograph into the right column.

Summarize the actual page in dense, short paragraphs. Record observations rather
than writing a time-traveller's expectations or feelings. Use **crimson**
underlines only for emphasis: write `<span class="ul" data-ink="c1">…</span>`,
not a bare `.ul`, a CSS `text-decoration`, highlighter sweeps, or rings. Keep
the copied template's annotation CSS and `drawMarks()` script; they draw the
wobbly printed line. Keep source-photo credit plus a link to its Commons file
page on the sheet.

## Building a web sheet

Copy `assets/field-notes.html` and edit the content. It carries the paper, inks,
typewriter type and two-region geometry in CSS, renders the mark as a Mermaid
diagram, and supports hand-drawn highlights, underlines and rings over the text.

It also carries **figures**: Font Awesome icons, either as a plate of framed,
`Fig.`-numbered specimens or inline to clarify a term. They are hatched rather
than solid, because a solid glyph reads as interface chrome on rag paper. Use
them for clarification, not depiction — `fa-fan` is a fan, not a windmill, so a
mark that has to be period-accurate is still a stamp from the image prompt.

**Read `references/web-template.md` before editing it.** Several parts look like
overcomplicated code and are load-bearing; the reference says which and why.

Serve it over `http://` — ES module imports fail on `file://` — and note it
fetches Mermaid and Courier Prime from the network.

## Collecting sheets

The template is a **deck**: one `<section class="slide">` per sheet, swiped
between with `scroll-snap`. A sheet is a page lying on a desk — the largest 4:3
page that fits the screen, with a hand's width of surface showing round it and a
shadow under it, because a sheet bled to the window edge is a background image
rather than a page you are turning. Give every slide an id; that anchor is what
an index links to.

On desktop, the deck keeps a transparent sliver of the preceding and following
sheet visible. Those pages are click targets, so the deck reads as one
continuous run of paper; keyboard and swipe navigation retain the same anchors.
Do not copy this narrow-page treatment to phone or tablet layouts.

`assets/notebook.html` builds both indexes and ships with both, so **delete the
one you are not delivering.** The three pages are one move outward and back: a
desk of notebooks → that notebook's notes on the desk → one note, full screen.
The desk under them never changes.

An index is objects on the desk, never a page with a list printed on it. A
note's card is the sheet itself shrunk to a hand's width, same 4:3 stock and
same shadow; a notebook is a 3½ × 5½ kraft memo book, type only, staples in the
spine. The masthead sits on the bare desk, set no larger than a card's title,
and a dozen notes are on screen at once.

Read `references/notebooks.md` before building either: it carries the build
order, the linking contract, the `--px` rule that makes a sheet hold its
proportions at any screen size, and the list of things an index does not get to
have. The templates' own demo links (`stamps/*.png`, `deck.html`,
`architecture/index.html`) point at files that do not exist by design; the
worked example is where they resolve.

## Common mistakes

- **Enlarging the mark.** On A and B it is a stamp, not an illustration. The
  whitespace around it is the design.
- **Replicating the photo in the mark.** Keep only what makes the place
  recognizable at a glance.
- **Letting the model write the caption.** Fill the slots.
- **Adding a dividing line.** The regions meet on a paper edge, not a rule.
- **Cleaning up the print.** Misregistration, dry patches and ragged edges are
  the point.
- **Dressing up an index.** Search, tags, excerpts, fills, radii and hover lifts
  are all fluff on rag paper. A card is a small sheet of paper with a mark and
  one line on it.
- **Printing the index on a page.** One long scrolling sheet carrying twelve
  notes is a document. The notes lie on the desk as separate pieces of paper.
- **Delivering a collection as loose files.** Five sheets in five HTML files
  with nothing opening them is five deliveries, not a notebook. Size the
  delivery first; the index is the cheap part, and only if the ids exist.
