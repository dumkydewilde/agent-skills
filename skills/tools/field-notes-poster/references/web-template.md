# The web template

`assets/field-notes.html` — one self-contained file. Copy it, delete the sheets
you don't need, replace the content.

It ships four sheets: variant C with a block diagram, variant B with a written
entry and a small diagram, a variant C with a ruled grid field, and variant A
with photo and stamp placeholders. The entry sheet also demonstrates the
long-text fit and all three annotation marks.

Serve over `http://`; ES module imports fail on `file://`. It fetches Mermaid 11
and Courier Prime from the network.

---

## The style

One style, no variants to choose between. Warm off-white paper, carbon lettering
and outlines, blocks filled flat in one of five spot colours. Defined once at
`:root`:

| Variable | Is |
|---|---|
| `--paper` | `#efe9dd`, warm off-white stock |
| `--paper-shade` | `#e4dccc`, for placeholders |
| `--ink` | `#2b2b2b`, lettering and outlines |
| `--line` | `#5a6068`, connectors between blocks |
| `--c1`…`--c5` | crimson, goldenrod, viridian, ultramarine, brown |

Fill a block by class in the Mermaid source: `P["POLDER FLOOR"]:::c5`. The
`classDef`s are injected from the palette at render time, so changing a hue
restyles every diagram without editing any of them, and each block's lettering is
picked for contrast against its own fill — carbon on the goldenrod, cream on the
rest.

**Keep the fills opaque.** Gouache is an opaque medium: it covers the paper
rather than staining it. Run these hues at partial strength and they go chalky
and pastel, which is the single thing that stops a block reading as a painted
plate. Putting `mix-blend-mode: multiply` on a plate is the same mistake by
another route — it tints every block with the stock underneath and pulls the
saturation back out. Texture is the `#gouache` filter's job, not transparency's.

Keep to five colours. Past that a sheet stops reading as a record and starts
reading as a chart legend.

## Annotation

Marks added to a sheet after it was typed. Wrap a run of text:

| Markup | Is |
|---|---|
| `<mark class="hl">…</mark>` | marker sweep, uneven pressure across the stroke |
| `<span class="ul">…</span>` | drawn underline that wobbles off the baseline |
| `<span class="ring">…</span>` | an ellipse round a term |

Add `data-ink="c1"`…`"c5"` for colour; goldenrod is the default marker.

Annotations **are** translucent, for the same reason the plate fills are not: a
highlighter is a translucent medium laid over finished print, so it darkens the
type it crosses instead of covering it. Hence `multiply`, and hence sitting above
the glyphs rather than behind them.

Each mark is randomised per instance — rotation, how far it overshoots each end,
and one of three noise filters. The variation is the point: a page of identical
ragged edges reads as a repeated graphic, not as a hand. The roll is remembered
per element, so a resize redraws the same marks in the same hand rather than
reshuffling them.

## Figures

Icons, for a small pictorial diagram or to clarify a term mid-sentence. Font
Awesome Free supplies the shapes, loaded from the CDN alongside the fonts.

A plate of figures:

```html
<div class="figs" style="--cols:3">
  <figure class="fig" data-ink="c4">
    <span class="frame"><i class="glyph hatch fa-solid fa-water"></i></span>
    <figcaption><span class="n">Fig. 2</span>Storage basin</figcaption>
  </figure>
</div>
```

Inline: `Wind <i class="ic fa-solid fa-fan" aria-hidden="true"></i> drove every
stage`. Both take `data-ink="c1"`…`"c5"`.

**Font Awesome's shapes are not period, and cannot be made period.** They are
geometric, uniform-weight and rounded — interface chrome next to typewriter type
on rag paper. What makes a figure read as late-19th-century is the treatment, in
this order of effect:

1. **Hatching** (`class="hatch"`). A solid silhouette is the single strongest
   modern tell. `background-clip:text` fills the glyph with ruled diagonals
   instead, which is how an engraving carries tone. Free's outline (`fa-regular`)
   set is far too small to rely on — most pictorial icons ship solid only — so
   hatching, not outlining, is what does this job.

   Hatching has to be paired with a **contour**, and its density has to be high
   enough to carry: the first version ruled 0.7px of ink in a 2.2px period, only
   ~32% coverage, which averaged out to a pale figure over cream and left the
   silhouette to be eaten by its own ruling. It is now 1.1px in 2.1px (~52%)
   plus a 0.55px `-webkit-text-stroke` keyline — cut the edge first, fill it
   afterwards, the way an engraver works. If a figure ever looks weak, those two
   numbers are the dial, not the filter.
2. **Presentation.** A hairline frame, a `Fig.` number and a small-caps label
   turn an icon into a specimen on a plate. This does more work than any filter.
3. **A wobbled edge** (`#engraved`), so the line is drawn rather than plotted.
   Kept gentle: icon strokes are thin, and the displacement that suits a painted
   block would break them apart.

The hatch angle varies down the plate by `nth-child`. At one angle throughout,
six figures read as a single texture rather than as six drawn things.

Two limits worth knowing before you plan a figure plate:

- **Light hues die at text size.** Goldenrod inline on cream is invisible.
  Inline icons default to `--ink`; if you tint one, use `c1`, `c4` or `c5`.
- **Goldenrod needs a carbon keyline even as a figure.** It is the one hue light
  enough to float off the paper at full ruling density, so `data-ink="c2"`
  overrides `-webkit-text-stroke-color` to `--ink`. That is the only per-hue
  exception in the file, and it is what a chromolithograph does with a pale ink.
- **Verified in Chromium only.** `-webkit-text-stroke` is also supported in
  Firefox and Safari, but its interaction with `background-clip:text` has not
  been checked there; if a figure loses its edge in another engine, that pair is
  the first thing to look at.
- **The shapes stay approximate.** `fa-fan` is a fan, not a windmill. If a
  figure has to be genuinely period-accurate, draw it as a stamp with the image
  prompt or source a public-domain engraving; icons are for clarification, not
  for depiction.

## The grid field

When a plate carries a plotted series instead of blocks, add `data-plate="grid"`
to it: the plate is ruled as graph paper, inset with bare paper and a thin
border, and a plotted line is weighted to 5px. Same palette, same paper — only
the field changes.

Charts use `xychart-beta`. **`xychart` gives one colour per series, not per
bar**, so a plate whose categories each need their own colour has to be a
flowchart of filled blocks rather than a bar chart. Bars plus a line on the same
axes works well and is what the demo sheet does.

## Long entries

The sheet is a fixed 4:3, so a long entry would run off the bottom and
`overflow:hidden` would eat the last lines mid-sentence. `fitEntries()` gives up
leading first (2.05 down to 1.65 — generous leading is a luxury only short notes
can afford), then reduces type size in 0.25px steps to an 8.5px floor.

Roughly 260 words fits variant B's column at full 12.5px type on leading alone.
Past the floor it logs a warning instead of clipping, because at that point the
text needs cutting or the sheet needs to be variant C, whose column is wider.

Fitting a long entry costs the whitespace the style is built on. It stays
legible, but a column packed to 85% of its height reads as a page of prose, not
as a field note. If an entry needs that much room, trimming it is usually the
honest move.

---

## Do not "simplify" these

Each of these looks like overcomplicated code, and each is the fix for a real
failure that will come back if it is reverted.

**`look: "classic"`, not `"handDrawn"`.** rough.js renders a fill as *hachure*,
so a filled block under `handDrawn` comes out as diagonal hatching in the fill
colour instead of a block. The hand-made quality comes from `#gouache` instead.

**Plain hex colours, never `rgba()`.** Mermaid's `classDef` grammar rejects the
parenthesis, and `plotColorPalette` is a comma-separated list, so one `rgba()`
value splits into three entries.

**Plate sizing in JS (`fitPlates`), not CSS.** Mermaid's svg carries a viewBox
but no height attribute, so every percentage resolves circularly:
`width:100%` + `height:auto` collapses to a ~17px intrinsic height with the width
back-derived from the viewBox ratio, and `width:100%` + `height:100%` in an auto
grid row scales the drawing past its region. `fitPlates` measures the padded box
and sets explicit px, capped at 2.2× so a plate keeps paper around it.

**Charts drawn at their field's proportions** (`xyChart: {width, height}`).
xychart's natural aspect is landscape; letterboxing one into a portrait region
strands it in a band with empty field above and below.

**The viewBox grown by a few px after render.** xychart lays its outermost axis
label flush with the viewBox edge, so the last one is cut in half — "1900" prints
as "190". Growing the chart instead just moves the clip inward.

**`rect.background` forced transparent.** xychart paints an opaque background
rect that covers the paper, and the grid on a ruled plate. `themeVariables` alone
does not clear it.

**Annotation marks as overlay elements, one per line fragment.** An absolutely
positioned pseudo-element cannot follow an inline that wraps — it collapses onto
the first fragment, so any annotation crossing a line break lands in the wrong
place at the wrong size.

**Those rects merged by line first.** The jitter pass wraps every word in an
inline-block, and `getClientRects()` returns one rect per inline-block, so an
unmerged run draws a sweep with a gap at every space.

**`await document.fonts.ready` before measuring.** Courier Prime arrives over the
network; laying marks out against fallback metrics puts every sweep in the wrong
place.

**The `col.clientHeight < 120` guard in `fitEntries`.** A collapsed or
not-yet-laid-out column reports a near-zero height; fitting against that drives
the type straight to the 8.5px floor and leaves it there.

**`margin:0` on `.fig`.** `<figure>` carries a UA default of `margin: 1em 40px`.
Forty pixels a side eats half a grid column, collapsing every specimen frame to
a thumbnail no matter what the grid is told to do.

**`place-items:center stretch` on a figure plate.** `.plate` sets
`place-items:center`, and `justify-items:center` makes the grid item
shrink-to-fit, so the figure grid's `width:100%` resolves against its own
content. Same trap as the plate svg sizing, one level up — worth recognising by
name, because it has now caused three separate collapse bugs in this file.

**Word-level `nowrap` spans in the jitter pass.** Per-character inline-blocks are
all line-break opportunities, so without the word wrapper text breaks mid-stem
("in sta / ges").
