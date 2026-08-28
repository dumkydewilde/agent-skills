# Prompt blocks

Concatenate: `CANVAS` → `LAYOUT-*` → `MARK` → `INK-AND-PRINT` → `TYPE` → `AVOID`.
Copy the block text verbatim into the prompt; fill every `{{slot}}`.

---

## CANVAS (shared)

> Create a single "Field Notes" poster. Output one image only, no collage, no
> grid, no multi-panel variations.
>
> 4:3 landscape composition, divided into a left and a right region. There is no
> visible dividing line, rule, border, or frame between the regions: they meet on
> a plain edge.
>
> Wherever bare paper shows, it is a warm off-white aged sheet with subtle
> fibers, natural grain, light handling marks, and a matte, unglazed surface.
> Large areas of that paper are left unprinted. The whitespace is an essential
> part of the layout, not empty space to be filled.

---

## LAYOUT-A — photo left, stamp right

> The left region takes about 58% of the frame and holds the supplied
> photograph, faithfully preserved. Maintain the subject's identity, terrain,
> architecture, plants, people, spatial relationships, natural lighting and
> shadows, authentic textures, and the original color atmosphere. Apply only
> restrained, art-publication-level color grading and extremely subtle
> fine-grained film noise. Natural cropping is allowed to fit the layout. Do not
> stretch, distort, shift, replace, retouch, or redraw the subject.
>
> The right region takes about 42% of the frame and is aged paper. A single
> stamped mark sits in the lower-middle of this region, occupying only about
> 30–38% of the region's height, with generous whitespace above and around it.
> The caption sits directly below the mark.
>
> Derive the mark from the photograph itself: extract the most
> location-distinctive outlines, structures, terrain contours, plant forms,
> roads, shorelines, or spatial relationships. Do not transcribe the photo
> element by element.

---

## LAYOUT-B — written entry left, small mark right

> The whole sheet is aged paper. There is no photograph.
>
> The left region takes about 58% of the frame and holds a written field-note
> entry in typewriter type: a heading, then short observation lines set flush
> left with a ragged right edge, generous leading, and no justification. Wide
> outer margins. The text block starts in the upper third and does not reach the
> bottom edge; the lower portion of the column stays unprinted.
>
> The right region takes about 42% of the frame and carries one small stamped
> mark low in the region, occupying only about 25–32% of the region's height,
> with the identification caption directly beneath it. The mark and its caption
> sit as a pair on the bottom margin: the caption's last line rests just above
> the sheet's bottom edge and the mark sits in the lower half. Everything above
> them in this region is bare paper.

---

## LAYOUT-C — large plate left, narrow text column right

> The whole sheet is aged paper. There is no photograph.
>
> The left region takes about 66% of the frame and holds one large stamped
> plate: the principal drawing or diagram of the subject, printed at scale but
> still reading as a hand-carved stamp rather than a finished illustration. It is
> inset from the sheet edges with clear paper margin on all sides, and it is
> seated low: its base rests on the bottom margin and it grows upward, so the
> weight of the drawing falls in the lower half and the paper above it stays
> open. Sparse hand-set annotation is allowed inside the plate: at most four
> short typewriter labels with thin hairline leader lines to the parts they name.
>
> The right region takes about 34% of the frame and holds a single narrow column
> of typewriter text: the identification caption, then a short descriptive
> passage of a few lines. The column is bottom-aligned — its last line rests just
> above the sheet's bottom margin, level with the base of the plate, and the
> paper above the column is bare. It is set flush left, ragged right, and never
> fills the region's height.

---

## MARK (shared)

> Compress the subject into a multi-color hand-carved rubber stamp image, at the
> scale given above. Retain only the minimal information needed to recognize the
> subject and its spatial relationships instantly. Remove crowds, vehicles, dense
> window grids, repeated buildings, fragmented vegetation, decorative flourishes,
> and irrelevant background. However large it is printed, the mark keeps a
> stamp's economy: it must not become a finished illustration, a full landscape
> painting, or a brand logo.

Append the matching row's instruction:

| Subject | Retain |
|---|---|
| Iconic architecture | the distinctive outer contour, roofline, dome, arcade, or tower; one structural rhythm, not every opening |
| Mountain settlement | buildings compressed into a few terraced color blocks aligned along the terrain |
| Coastal scene | mountain contour, layered settlement, shoreline, and sparse intermittent water ripples |
| City panorama | the main skyline, one iconic building, and one or two layers of distant hills |
| Natural landscape | primary landform, tree silhouettes, shoreline, or road orientation |
| Foreground occlusion | if narratively important, keep it as a foreground stamp outline over the subject |
| Object or specimen | the silhouette, one internal structure line, and the single detail that identifies it |
| Mechanism or system | the principal bodies and their connections as blocks and lines, and nothing that is merely housing or trim |
| Route or map | the line of travel, two or three anchor landmarks, one water or terrain edge |

---

## INK-AND-PRINT (shared)

> Use 2–4 spot inks drawn from the subject's own palette. Prioritize desaturated
> colors: carbon black, deep green, brick red, ochre yellow, slate blue, taupe
> brown. Do not force a fixed palette; preserve the subject's most distinctive
> color character, and let only a small area carry saturated color for emphasis.
>
> Print each ink as a separately hand-stamped layer: authentic carving texture,
> visible hand-engraved marks, uneven line widths, notched contours, fractured
> edges, dry ink shortages, paper show-through, granular ink, uneven pressure,
> partial ghosting, and about 1–2 mm of subtle misregistration between layers.
> Allow natural misalignment. Edges must never be digitally smoothed. The result
> should read as a real carved stamp pressed onto aged paper, not a photo filter,
> a clean vector, or line art.

---

## TYPE (shared)

> Set all text in a small, restrained typewriter face with slight mechanical
> imperfection: uneven ink weight letter to letter, minutely irregular baselines.
> The typography should read as a traveler's or observer's own record, not an
> advertising headline. Spell every word exactly as given. Add no slogans,
> brands, dates, or decorative copy beyond the text specified below.

Then the variant's text, given as literal lines the model must set. Introduce
each with "Set exactly these lines <where>:" so the model places it, and give
the lines as a code block.

**A** — beneath the mark, one block:

```
{{SUBJECT_NAME}}
No. {{number}}
{{keyword}} / {{keyword}} / {{keyword}}
{{year}}
```

**B** — two blocks. First the left-hand entry:

```
{{SUBJECT_NAME}}  ·  {{year}}

{{body — 4 to 8 short observation lines, written out in full}}
```

then the caption beneath the right-hand mark:

```
No. {{number}}
{{keyword}} / {{keyword}} / {{keyword}}
```

**C** — one block, the right-hand column:

```
{{SUBJECT_NAME}}
No. {{number}}
{{keyword}} / {{keyword}} / {{keyword}}
{{year}}

{{body — 3 to 6 short descriptive lines, written out in full}}
```

Plate labels for C, if used: `{{label}}`, `{{label}}`, `{{label}}`, `{{label}}`.

---

## AVOID (shared)

> Avoid: an obvious central dividing line; circular seals; Chinese red seal
> stamps; postage perforations; wax seals; sticker collage; tourist souvenir
> templates; smooth vector logos; generic city icons; replicating every piece of
> architecture; dense detailing; childlike craft; cartoon style; 3D rendering;
> plastic texture; glossy digital gradients; oversaturation; excess text;
> decorative clutter.

For A, add:

> Do not redraw, restyle, or alter the photograph in the left region.

---

## Worked example — variant A

Photo: San Marco campanile across the lagoon. Assembled prompt ends with:

> …Use 2–4 spot inks drawn from the subject's own palette… [INK-AND-PRINT] …
> Set all text in a small, restrained typewriter face… [TYPE] Set exactly these
> lines beneath the mark:
>
> ```
> VENICE
> No. 01
> brick / bell / lagoon
> 2026
> ```
>
> Avoid: an obvious central dividing line… [AVOID] Do not redraw, restyle, or
> alter the photograph in the left region.

The mark that results: campanile silhouette in brick red and carbon black, the
waterfront palaces reduced to two ochre and slate bands, one slate-blue smear of
lagoon under them. Three inks, no windows counted, no crowds, no boats.
