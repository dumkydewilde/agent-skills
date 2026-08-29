# Field-noting a Wikipedia page

Turn a Wikipedia article into one standalone, printable field-notes sheet. Use
the template's **B** geometry: a dense typed record on the left, a modest
rubber-stamp sketch on the lower right, and a small caption plus source credit
below it. Do not add a new example to `assets/field-notes.html`.

`assets/examples/amsterdam-centraal-field-notes.html` is a finished sheet from
this exact flow — read it for the record's density, the underline markup, the
stamp block, and the credit line before writing your own.

## 1. Gather the record

Use the URL's page title with the REST summary endpoint for the subject, lead
image, and canonical page URL:

```sh
curl --fail --silent --show-error --location \
  "https://en.wikipedia.org/api/rest_v1/page/summary/<PAGE_TITLE>"
```

The summary is an orientation aid, not the whole note. Retrieve the article's
wikitext for precise dates, dimensions, counts, and named designers:

```sh
curl --fail --silent --show-error --location --get \
  'https://en.wikipedia.org/w/api.php' \
  --data-urlencode 'action=parse' \
  --data-urlencode 'page=<PAGE_TITLE>' \
  --data-urlencode 'prop=wikitext' \
  --data-urlencode 'format=json'
```

Select concrete, article-supported observations. Preserve dates on statistics
whose measurement year is supplied by the article; never turn an older figure
into an undated claim about the present.

## 2. Credit the source image

Read the lead image filename from the summary, then retrieve its Commons credit
and licence. `imageinfo` is required; the image URL alone is not attribution.

```sh
curl --fail --silent --show-error --location --get \
  'https://commons.wikimedia.org/w/api.php' \
  --data-urlencode 'action=query' \
  --data-urlencode 'titles=File:<LEAD_IMAGE_FILENAME>' \
  --data-urlencode 'prop=imageinfo' \
  --data-urlencode 'iiprop=extmetadata|url' \
  --data-urlencode 'format=json'
```

Keep the artist, licence (for example, CC BY-SA 4.0), and `descriptionurl`.
The finished sheet must link its visible source line to `descriptionurl`.

## 3. Write the observation record

Write roughly 180–260 words in five to seven short paragraphs. It is a concise
summary of the article, not historical fiction:

- state construction, design, material, and scale facts plainly;
- add changes over time, function, and connections when the article supports
  them;
- use paragraph order to make the subject legible: origin, construction,
  defining physical detail, operation, later changes, dated capacity;
- omit first-person narration, expectations, feelings, and invented reactions;
- underline five to seven high-value facts with
  `<span class="ul" data-ink="c1">…</span>`; `c1` is the template's crimson
  annotation ink. A bare `.ul` defaults to goldenrod.
- use **underlines only**—no `<mark class="hl">` or `<span class="ring">`.

## 4. Make a stamp from the source photo

`assets/examples/amsterdam-centraal-source.jpg` and
`amsterdam-centraal-rubber-stamp.png` are this step's input and output, side by
side; `examples.md` lists what the pass dropped.

Use the Commons lead image as an **image-input reference**, not as the final
right-hand image. Ask an image-to-image model for a transparent or removable
flat-background rubber-stamp sketch. Retain the subject's distinctive silhouette
and two or three defining structures, but remove crowd, traffic, incidental
text, dense window grids, and photographic shading.

Use this prompt structure, filled with the subject's actual details:

```text
Transform the supplied source photograph of <SUBJECT> into a small hand-carved
rubber-stamp sketch for a field-notes sheet. Preserve <DISTINCTIVE SILHOUETTE>
and <TWO OR THREE DEFINING STRUCTURES>. Use carbon black and at most one or two
desaturated spot inks from the source. Show carved contour lines, dry ink gaps,
rough cut edges, slight misregistration, and sparse engraved texture. No
photographic shading, no text, no watermark, no dense repeated detail, no
crowds, vehicles, or signs. Leave generous empty margin around the stamp.
```

For a transparent result, follow the active image-generation skill's chroma-key
and local-removal workflow. Do not substitute a monochrome, sepia, or
CSS-filtered source photo: the right-hand mark must be a generated
**rubber-stamp sketch**.

## 5. Build the standalone sheet

Copy `assets/field-notes.html` into the delivery directory, then delete all of
its built-in examples. Keep one `data-variant="B"` sheet, **inside its
`<section class="slide">` and its `<main class="deck">`** — the paper is
painted on the slide, so a sheet lifted out of one is printed on nothing. A
deck of one is the standalone sheet. Delete the `.home` link, which points at
an index this delivery does not have. Retain the
template's annotation CSS plus its `drawMarks()` script: these turn `.ul` runs
into a `.marks .mk--ul` overlay with deliberately wobbly printed lines. Put the factual entry in
`.col--entry`, marking only factual phrases as, for example,
`<span class="ul" data-ink="c1">1889</span>`; do not replace this renderer with
a custom CSS underline, and specifically not a `.ul::after` pseudo-element.
After the page loads, inspect the DOM: every `.ul` must have a corresponding
`.marks .mk--ul` overlay. In the right-hand `.stack`, replace the small Mermaid
plate with the generated stamp:

```html
<div class="plate plate--small">
  <img class="mark" src="<STAMP_FILE>"
       alt="Rubber-stamp sketch of <SUBJECT>">
</div>
<p class="caption jitter"><span class="name"><SUBJECT></span>
No. <NUMBER>
<KEYWORD> / <KEYWORD> / <KEYWORD>
<YEAR></p>
<p class="source">STAMP AFTER A PHOTO BY
  <a href="<COMMONS_FILE_PAGE>"><ARTIST> / <LICENCE></a>
</p>
```

Add a small `.source` rule if the copied template does not already have one;
keep it quieter than the caption. Serve the result over `http://`, inspect the
rendered sheet, and verify that the note fits, exactly one sheet remains, the
stamp is right-aligned and recognizably drawn rather than photographic, and no
highlights or rings remain.
