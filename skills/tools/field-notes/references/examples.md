# Examples

Finished work that hit the target register, in `assets/examples/`. **Look at the
images before writing a prompt or a sheet** — ink economy, print texture and how
much to leave out are faster to match by eye than from the block text, and the
two failures the prompt blocks warn about (a mark that swells into an
illustration, a print that has been cleaned up) are obvious on sight.

---

## A whole sheet — `amsterdam-centraal-*`

The complete variant **B** output of the Wikipedia flow, in four files:

| File | What it is |
|---|---|
| `amsterdam-centraal-field-notes.html` | the sheet: standalone, self-contained, no build step |
| `amsterdam-centraal-rubber-stamp.png` | the mark, transparent, referenced by the HTML beside it |
| `amsterdam-centraal-source.jpg` | the Commons photo the mark was carved from |
| `amsterdam-centraal-sheet-rendered.jpg` | how the above renders, for a quick look |

Serve the directory over `http://` to see the live one; the drawn underlines
need the script to run.

Read it for:

- **The geometry.** 58/42 columns on one sheet of paper with no rule between
  them. Six short paragraphs starting in the upper third, stopping well above
  the bottom edge. The stamp sits at 32% of its column's height, low, with the
  whole upper half of that column left bare.
- **The record.** Dated, checkable facts in article order — opening, architect,
  what it replaced, 8,687 piles, 45-metre trusses, 15 tracks, 2018 ridership.
  No first-person narration and no atmosphere.
- **Seven crimson underlines,** each on a number or a proper noun, drawn as a
  wobbly printed line by `drawMarks()` rather than by `text-decoration`.
- **Two inks in the mark, brick red and carbon black,** matching the building.
  The roofline, three gables and two turrets survive; the windows are texture
  rather than a counted grid.
- **The credit block,** 8px uppercase and quieter than the caption, linking the
  Commons file page and the article.

Compare `amsterdam-centraal-source.jpg` with the stamp to see what an
image-to-image pass should drop: the sky, the tram wires, the crowd, the
photographic shading, and every window as a distinct opening.

---

## A whole notebook — `notes/` and `notebook/`

One example in two forms: the markdown it is written in, and the pages built
from it. They are the same shelf, so read them side by side.

```
notes/                        ← the source: five .md files and their marks
notebook/                     ← its build, committed so it can just be opened
  notebooks.html                the shelf: two memo books
  beemster/index.html           three notes on the desk
  beemster/deck.html            those three sheets, one per screen
  elsewhere/index.html
  elsewhere/deck.html
```

**Serve `assets/` over `http://` and open `examples/notebook/notebooks.html`** —
the decks import Mermaid as an ES module, which fails on `file://`. Click all
the way down and back: a cover opens an index, a note opens the deck at its own
slide, and `.home` walks back up.

Rebuild it after changing a template, or the committed pages go stale (a test
holds them to it):

```bash
uv run scripts/build.py assets/examples/notes -o assets/examples/notebook
```

Read the pages for:

- **The three surfaces being one desk.** `--desk` never changes across the
  chain, and an object keeps its stock and its shadow at every scale: the card
  you tap on the index is the sheet that fills the screen.
- **Two kinds of card mark.** `molengang` uses a raster mark; the other Beemster
  cards carry hatched glyphs, because those sheets are a chart and a figure
  plate with no raster to show. Every raster card keeps the `onerror` handler
  that swaps in the dashed `stamp` placeholder.
- **A real variant A.** `elsewhere/deck.html#amsterdam-centraal` pairs the
  Commons photograph with the stamp carved from it.
- **The link contract, in working form.** Its links are checked by
  `tests/test_notebooks.py`, so this is the one place in the skill where a
  broken link is a bug rather than a placeholder.

Read the markdown for the format itself, which
`references/markdown-source.md` documents. Between them the five notes exercise
all of it: all three variants, the inferred variant and the override, a Mermaid
plate and a ruled one, a plate of `Fig.` icons, a raster mark, a glyph card, an
ordering prefix that does not reach the anchor, and every inline mark —
`==sweep==`, `[underline]{.ul .c1}`, `[ring]{.ring .c4}`, `:fa-icon:`.
`_shelf.md` and `_notebook.md` show the only metadata there is: a title, a
masthead line and a cover line, all optional because the counts are counted.

---

## A mechanism, annotated — `mark-beemster-mills.jpg`

A *molengang*: three drainage mills in series lifting water out of the Beemster
polder, stage by stage, over the ring dyke. Cropped to the mark; the caption and
the sheet around it are not shown.

Read it for:

- **Three inks, each doing one job.** Carbon black carries the mills and scoop
  wheels, slate blue the water, taupe brown the earth. No ink is decorative and
  none is shared between elements.
- **Repetition as explanation.** The same mill stamped three times at rising
  heights is the whole argument of the diagram. The mechanism reads left to
  right without a caption.
- **Flat fills with visible carving.** Water is a flat blue band, earth a solid
  taupe mass; both are broken by dry patches and ragged horizontal grain. No
  shading, no gradient, no outline around the fills.
- **Four labels, no more.** `mill`, `scoop wheel`, `storage basin`, `ring dyke`
  in small lowercase typewriter type, each on a hairline leader with a thin
  arrowhead, all set in the bare paper above the drawing rather than inside it.
- **What was dropped.** No sails drawn as a full lattice, no gearing interior,
  no farmland, no sky, no figures. The scoop wheel keeps its spokes only because
  that is the detail that identifies it.

This is the `Mechanism or system` row of the MARK table at plate scale, and the
model for variant **C**'s left region.

---

## A landscape in bands — `mark-oostvaardersplassen-reed-geese.jpg`

Reed bed, water, and geese over the Oostvaardersplassen. Also cropped to the
mark.

Read it for:

- **Horizontal banding.** Bare paper (sky), a black dyke line, an olive reed
  bed, a slate-grey water band. Four stacked zones stand in for a landscape that
  has no landform to draw.
- **Texture instead of detail.** The reeds are hundreds of short repeated
  strokes, the water a few broken streaks. Neither is drawn as an object; both
  are drawn as a way of covering paper.
- **Silhouettes at two scales.** Six geese in flight, none more detailed than a
  body and two wing angles, plus three bare trees that exist only to set the
  scale of the reed bed.
- **Muted spot inks.** Olive green, slate grey, carbon black. The saturated
  colour a photograph of this place would carry is deliberately absent.
- **Bare paper doing work.** Roughly the top third is unprinted, which is what
  makes the geese read as flying rather than as marks in a pattern.

This is the `Natural landscape` row of the MARK table, at the small scale
variants **A** and **B** use.

---

## What not to copy

- **The crop.** The two mark files are trimmed to the mark. On a sheet, a small
  mark occupies 25–38% of its region's height and sits low, with whitespace
  above — as it does on the Amsterdam sheet.
- **The label count as a floor.** Four labels is the ceiling for a C plate, and
  A and B marks carry none at all — only the caption beneath them.
- **The palette as a preset.** Each drew its inks from its own subject. Slate
  blue and taupe are what a polder looks like, not a house style.
