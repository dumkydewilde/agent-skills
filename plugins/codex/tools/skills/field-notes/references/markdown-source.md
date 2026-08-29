# Notes as markdown

Sheets can be written as markdown files and built into the pages, instead of
edited as HTML. `scripts/build.py` reads a folder of notes and writes the deck,
the index and the shelf, taking the style from the two templates in `assets/`
and filling in only the content.

**The markdown is the source of record; the HTML is a build artifact.** Edit the
notes and build again — every id, link and count is re-derived, which is the
whole reason to work this way: the counts on a masthead and the anchors under a
card are exactly the errors a person makes by hand.

Use it when there is more than one note, when the text will be revised, or when
someone who does not want to read HTML has to edit it. Hand-build from the
template when a sheet needs markup this format has no field for — and then keep
that deck hand-built, because **a build overwrites the deck it generates.**

## Running it

```bash
uv run scripts/build.py notes/ -o site/        # a shelf of notebooks
uv run scripts/build.py notes/beemster/        # one notebook  → site/
uv run scripts/build.py notes/molengang.md     # one sheet     → site/
python3 -m http.server --directory site 8000   # then open it over http://
```

Stdlib only, no dependencies, Python 3.11+. The shape is inferred from what you
point it at — a file is a sheet, a folder of notes is a notebook, a folder of
folders is a shelf — and `--shape` overrides it.

## The folder

```
notes/
  _shelf.md                    ← optional: the shelf's title and meta line
  beemster/
    _notebook.md               ← optional: this notebook's title, meta, cover line
    01-molengang.md            ← the leading number orders the deck …
    02-land-drained.md         ← … and is stripped from the id
    stamps/molengang.jpg       ← anything not .md is copied beside the pages
  elsewhere/
    01-wittgenstein.md
    photos/…  stamps/…
```

Files starting with `_` are metadata, never sheets. A leading `01-` sets the
reading order and is dropped from the anchor, so re-ordering the deck never
rewrites an index card's `href`. Asset folders are copied as they are, so a
`mark: stamps/molengang.jpg` in the front matter resolves in the built page
exactly as it did in the source folder.

## Front matter

A small subset of YAML: `key: value`, and `- item` lists. No nesting.

| Key | Is | Default |
|---|---|---|
| `title` | the subject | the filename, title-cased |
| `year` | shown in the heading, the caption and on the card | — |
| `number` | `No. 11`, the caption's second line | — |
| `keywords` | three lowercase words, `/`-separated | — |
| `variant` | `A`, `B` or `C`, overriding the inference below | inferred |
| `mark` | a raster mark: the sheet's stamp, and the card's | — |
| `glyph` | a Font Awesome name for a card with no raster, `fa-fan` | — |
| `ink` | `c1`…`c5`, the glyph's colour | carbon |
| `photo` | variant A's photograph | — |
| `grid` | `true` rules the plate as graph paper | false |
| `figures` | a list of `icon \| label \| ink`, making a plate of `Fig.`s | — |
| `id` | the anchor | the filename, without its number prefix |

Notebook and shelf files take `title`, `meta` (the masthead's line) and, for a
notebook, `line` (what its cover says on the shelf). All three default to the
folder name and the counts, and the counts are correct because they are counted.

**The variant is inferred** unless you set it: a `photo` makes it **A**,
`figures` or a Mermaid block make it **C**, and anything else is **B**. Set
`variant: B` explicitly for a written entry that also carries a small diagram.

## The body

Paragraphs, separated by blank lines. Wrap the source however you like — the
lines are joined and the sheet re-wraps them to its own column.

| Written | Is |
|---|---|
| `==text==` | a highlighter sweep, `==text=={.c3}` in viridian |
| `[text]{.ul .c1}` | a drawn underline, in crimson |
| `[text]{.ring .c4}` | a ring round it, in ultramarine |
| `:fa-fan:` | an inline icon, `:fa-industry.c1:` to tint it |
| `**text**`, `*text*` | bold, italic |
| ` ```mermaid ` | the plate: the block is the mark |

Everything else passes through as written, so inline HTML works the way it does
in any markdown. **Block-level HTML does not** — the record is one paragraph
element, and a `<div>` inside it ends the paragraph early.

Which region the body lands in follows the variant: **B** sets it as the entry
filling the left region, **C** as the narrow column under the caption, and **A**
has no room for one — its record is the caption.

## What it does not do

Deliberately small, because a sheet is a heading, a record and a mark:

- **no headings, lists, tables, block quotes or images in the body.** A sheet
  that wants a bullet list wants a figure plate; one that wants a second
  heading wants to be two sheets;
- **no partial builds.** The output folder is written whole. Do not edit the
  generated HTML: your next build silently discards it;
- **no front-matter validation beyond the obvious.** A misspelt key is ignored
  rather than reported, so check the sheet you get.

`assets/examples/notes/` is a working shelf in this format — two notebooks, five
notes, all three variants, every inline mark, a figure plate, a Mermaid plate
and a raster mark. Build it and compare it against the markdown:

```bash
uv run scripts/build.py assets/examples/notes -o /tmp/notebook && \
  python3 -m http.server --directory /tmp/notebook 8000
```
