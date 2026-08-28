---
name: field-notes-poster
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
  subject.
---

# Field Notes Poster

A field-notes sheet is 4:3 landscape, split into two regions with no dividing
rule: one carries the record, the other carries a hand-made mark, captioned in
small typewriter type on aged paper. Whitespace is part of the layout, not space
left over.

## Route first: prompt, web, or cited-source web

| When the mark is | Make it | Because |
|---|---|---|
| **pictorial** — a skyline, landform, building, specimen | an image prompt → `references/prompt-templates.md` | only an image model can draw a carved stamp of a real place |
| **a diagram** — a system, mechanism, route, process, chart | the web template → `references/web-template.md` | the Mermaid source *is* the mark, so it is exact rather than described |
| **both** — a photo plus a stamp | prompt for the stamp, then place it in the web template's variant A | |
| **a Wikipedia page** | a standalone source-note sheet → `references/wikipedia-field-notes.md` | facts stay verifiable, while the lead image becomes a generated stamp sketch |

Prefer the web template whenever the text must stay editable, selectable, or
printable. Prefer the prompt when the mark has to look drawn by hand from life.

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
delete its demonstration sheets, and retain only the Wikipedia sheet. The source
image is reference material for an image-to-image rubber-stamp sketch; never
drop a monochrome or CSS-filtered photograph into the right column.

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

## Common mistakes

- **Enlarging the mark.** On A and B it is a stamp, not an illustration. The
  whitespace around it is the design.
- **Replicating the photo in the mark.** Keep only what makes the place
  recognizable at a glance.
- **Letting the model write the caption.** Fill the slots.
- **Adding a dividing line.** The regions meet on a paper edge, not a rule.
- **Cleaning up the print.** Misregistration, dry patches and ragged edges are
  the point.
