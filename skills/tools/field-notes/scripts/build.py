#!/usr/bin/env python3
"""Build field-notes pages from a directory of markdown notes.

    uv run build.py notes/                 # → site/
    uv run build.py notes/architecture/    # one notebook
    uv run build.py notes/taj-mahal.md     # one sheet

The markdown is the source of record and the HTML is a build artifact: edit the
notes, run this again, and every link, id and count is re-derived. Nothing here
invents style — the two files in `assets/` carry all of it, and this script only
fills in their slides and cards.

Stdlib only, so it runs anywhere Python 3.11 does. The markdown subset it reads
is documented in `references/markdown-source.md`; it is small on purpose,
because a sheet is a heading, a record and a mark, not a document.
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"


# ─────────────────────────────────────────────────────────────────────────────
# Front matter
#
# A deliberate subset of YAML: `key: value` and `- item` lists, no nesting, no
# anchors, no flow style. Adding a YAML library would make the skill depend on
# an install step, and a note that needs more structure than this is a note
# that should be two notes.
# ─────────────────────────────────────────────────────────────────────────────

def parse_front_matter(text: str) -> tuple[dict[str, object], str]:
    if not text.startswith("---"):
        return {}, text
    _, _, rest = text.partition("\n")
    raw, sep, body = rest.partition("\n---")
    if not sep:
        raise ValueError("front matter opened with --- but never closed")

    meta: dict[str, object] = {}
    key = None
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.lstrip().startswith("- ") and key:
            meta.setdefault(key, [])
            if not isinstance(meta[key], list):        # a value, then a list
                meta[key] = []
            meta[key].append(line.lstrip()[2:].strip())
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        meta[key] = value.strip()
    return meta, body.lstrip("\n").removeprefix("-\n")


# ─────────────────────────────────────────────────────────────────────────────
# Inline marks
#
# The three annotations the sheet can draw, plus the inline icon. Written the
# way they read in a notebook rather than as HTML:
#
#   ==text==            a highlighter sweep      → <mark class="hl">
#   ==text=={.c3}       … in viridian
#   [text]{.ul .c1}     a drawn underline
#   [text]{.ring .c4}   a ring round it
#   :fa-fan:            an inline icon, :fa-industry.c1: to tint it
#
# The body is otherwise passed through as written, so raw HTML works the way it
# does in any markdown: this is a page you are authoring, not untrusted input.
# ─────────────────────────────────────────────────────────────────────────────

SPAN = re.compile(r"\[([^\]]+)\]\{([^}]+)\}")
HIGHLIGHT = re.compile(r"==(.+?)==(?:\{\.(c[1-5])\})?", re.S)
ICON = re.compile(r":(fa-[a-z0-9-]+)(?:\.(c[1-5]))?:")
STRONG = re.compile(r"\*\*(.+?)\*\*", re.S)
EM = re.compile(r"(?<![*\w])\*([^*\n]+)\*(?!\*)")

MARK_TAGS = {"hl": "mark", "ul": "span", "ring": "span"}


def _span(match: re.Match[str]) -> str:
    text, classes = match.group(1), match.group(2).replace(".", " ").split()
    kind = next((c for c in classes if c in MARK_TAGS), None)
    if kind is None:                                   # not ours; leave it be
        return match.group(0)
    ink = next((c for c in classes if re.fullmatch(r"c[1-5]", c)), None)
    tag = MARK_TAGS[kind]
    attr = f' data-ink="{ink}"' if ink else ""
    return f'<{tag} class="{kind}"{attr}>{text}</{tag}>'


def inline(text: str) -> str:
    text = SPAN.sub(_span, text)
    text = HIGHLIGHT.sub(
        lambda m: f'<mark class="hl"{f" data-ink={m.group(2)!r}" if m.group(2) else ""}>'
                  f"{m.group(1)}</mark>".replace("'", '"'), text)
    text = ICON.sub(
        lambda m: f'<i class="ic fa-solid {m.group(1)}"'
                  f'{f" data-ink=\"{m.group(2)}\"" if m.group(2) else ""}'
                  ' aria-hidden="true"></i>', text)
    text = STRONG.sub(r"<strong>\1</strong>", text)
    text = EM.sub(r"<em>\1</em>", text)
    return text


FENCE = re.compile(r"^```mermaid\n(.*?)^```\s*$", re.M | re.S)


def unwrap(body: str) -> str:
    """Join the lines inside a paragraph; keep the blank lines between them.

    The sheet sets the record in `white-space:pre-wrap`, so every newline in
    the source is a line break on the paper. Markdown hard-wrapped at 80
    columns would print as 80-column ragged lines inside a column that is not
    80 columns wide. Wrap the source however you like; the sheet re-wraps it.
    """
    paragraphs = re.split(r"\n\s*\n", body.strip())
    return "\n\n".join(" ".join(line.strip() for line in p.splitlines() if line.strip())
                       for p in paragraphs if p.strip())


# ─────────────────────────────────────────────────────────────────────────────
# A note
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Note:
    id: str
    title: str
    year: str = ""
    number: str = ""
    keywords: str = ""
    variant: str = ""
    mark: str = ""
    glyph: str = ""
    ink: str = ""
    photo: str = ""
    grid: bool = False
    figures: list[str] = field(default_factory=list)
    body: str = ""
    mermaid: str = ""

    @property
    def heading(self) -> str:
        title = html.escape(self.title).upper()
        return f"{title}  ·  {self.year}" if self.year else title

    @property
    def card_line(self) -> str:
        title = html.escape(self.title)
        return f"{title} &middot; {self.year}" if self.year else title


def read_note(path: Path) -> Note:
    meta, body = parse_front_matter(path.read_text())
    plates = FENCE.findall(body)
    body = unwrap(FENCE.sub("", body))

    # `03-taj-mahal.md` orders the deck without putting the number in the
    # anchor, which is the thing every index card points at.
    stem = re.sub(r"^\d+[-_]", "", path.stem)
    figures = meta.get("figures") or []
    variant = str(meta.get("variant", "")).upper()
    if not variant:
        variant = "A" if meta.get("photo") else "C" if (plates or figures) else "B"

    return Note(
        id=str(meta.get("id") or stem),
        title=str(meta.get("title") or stem.replace("-", " ").title()),
        year=str(meta.get("year", "")),
        number=str(meta.get("number", "")),
        keywords=str(meta.get("keywords", "")),
        variant=variant,
        mark=str(meta.get("mark", "")),
        glyph=str(meta.get("glyph", "")),
        ink=str(meta.get("ink", "")),
        photo=str(meta.get("photo", "")),
        grid=str(meta.get("grid", "")).lower() in {"true", "yes", "1"},
        figures=[f for f in figures if isinstance(f, str)],
        body=body,
        mermaid=plates[0].strip() if plates else "",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Slides
#
# One template per variant, matching the demonstration sheets in
# assets/field-notes.html class for class. If you change a class here, change
# it there: the stylesheet is the one in the template and nothing is generated.
# ─────────────────────────────────────────────────────────────────────────────

ONERROR_MARK = ('onerror="this.replaceWith(Object.assign(document.createElement(\'div\'),\n'
                "                    {className:'mark-missing',textContent:'stamp'}))\"")
ONERROR_PHOTO = ('onerror="this.outerHTML=\'&lt;div class=&quot;photo-missing&quot;'
                 "&gt;photograph&lt;/div&gt;'\"")


def indent(block: str, spaces: int) -> str:
    pad = " " * spaces
    return "\n".join(pad + line if line.strip() else line for line in block.splitlines())


def caption(note: Note, with_name: bool, with_year: bool = True) -> str:
    """The caption block: subject, number, keywords, year, one per line.

    Variant B leaves the name and the year out, because its heading is already
    `SUBJECT · YEAR` at the top of the entry and a caption repeating it reads
    as a second title rather than a note in the margin.
    """
    lines = []
    if with_name:
        lines.append(f'<span class="name">{html.escape(note.title).upper()}</span>')
    lines += [line for line in (note.number, html.escape(note.keywords)) if line]
    if with_year and note.year:
        lines.append(note.year)
    return "\n".join(lines)


def plate(note: Note, size: str = "") -> str:
    """The mark: a Mermaid drawing, a plate of figures, or a raster stamp."""
    klass = f"plate {size}".strip()
    grid = ' data-plate="grid"' if note.grid else ""
    if note.figures:
        figs = "\n".join(
            f'    <figure class="fig"{f" data-ink=\"{ink}\"" if ink else ""}>\n'
            f'      <span class="frame"><i class="glyph hatch fa-solid {icon}"></i></span>\n'
            f'      <figcaption><span class="n">Fig. {n}</span>{html.escape(label)}</figcaption>\n'
            f"    </figure>"
            for n, (icon, label, ink) in enumerate(map(split_figure, note.figures), 1))
        cols = 3 if len(note.figures) > 4 else 2
        body = f'  <div class="figs" style="--cols:{cols}">\n{figs}\n  </div>'
    elif note.mermaid:
        body = f'  <pre class="mermaid">\n{indent(note.mermaid, 4)}\n  </pre>'
    elif note.mark:
        body = f'  <img class="mark" src="{note.mark}" alt="" {ONERROR_MARK}>'
    else:
        body = '  <div class="mark-missing">stamp</div>'
    return f'<div class="{klass}"{grid}>\n{body}\n</div>'


def split_figure(entry: str) -> tuple[str, str, str]:
    """`fa-fan | Wind stage | c5` — icon, label, and the ink to draw it in."""
    parts = [p.strip() for p in entry.split("|")]
    parts += [""] * (3 - len(parts))
    return parts[0], parts[1], parts[2]


def render_slide(note: Note) -> str:
    body = inline(note.body)
    if note.variant == "A":
        inner = (f'  <img class="photo" src="{note.photo}" alt="" {ONERROR_PHOTO}>\n\n'
                 f'  <div class="stack">\n{indent(plate(note), 4)}\n'
                 f'    <p class="caption jitter">{caption(note, True)}</p>\n  </div>')
    elif note.variant == "C":
        inner = (f'{indent(plate(note, "plate--large"), 2)}\n\n'
                 f'  <div class="col col--bottom">\n'
                 f'    <p class="caption jitter">{caption(note, True)}</p>\n'
                 + (f'    <hr class="rule">\n    <p class="body jitter">{body}</p>\n' if body else "")
                 + "  </div>")
    else:
        inner = (f'  <div class="col col--entry">\n'
                 f'    <p class="heading jitter">{note.heading}</p>\n'
                 f'    <p class="body jitter">{body}</p>\n  </div>\n\n'
                 f'  <div class="stack">\n{indent(plate(note, "plate--small"), 4)}\n'
                 f'    <p class="caption jitter">{caption(note, False, with_year=False)}</p>\n'
                 "  </div>")
    return (f'<section class="slide" id="{note.id}">\n'
            f'<div class="sheet" data-variant="{note.variant}">\n\n'
            f"{inner}\n\n</div>\n</section>\n")


# ─────────────────────────────────────────────────────────────────────────────
# Cards and covers
# ─────────────────────────────────────────────────────────────────────────────

def render_card(note: Note) -> str:
    ink = f' data-ink="{note.ink}"' if note.ink else ""
    if note.mark:
        mark = (f'\n        <img class="mark" src="{note.mark}" alt="" {ONERROR_MARK}>\n      ')
    elif note.glyph:
        mark = f'<i class="glyph hatch fa-solid {note.glyph}"></i>'
    else:
        mark = '<span class="mark-missing">stamp</span>'
    return (f'    <a class="card" href="deck.html#{note.id}"{ink}>\n'
            f'      <span class="frame">{mark}</span>\n'
            f'      <h2 class="card-title jitter">{note.card_line}</h2>\n    </a>\n')


def render_cover(name: str, title: str, line: str) -> str:
    return (f'    <a class="book" href="{name}/index.html">\n      <div class="cover">\n'
            f'        <i class="staple"></i><i class="staple"></i>\n'
            f'        <h2 class="cover-title jitter">{html.escape(title)}</h2>\n'
            f'        <p class="cover-line jitter">{line}</p>\n      </div>\n    </a>\n')


# ─────────────────────────────────────────────────────────────────────────────
# The templates, used as shells
#
# Everything but the content is taken from the two files in assets/ at build
# time, so a fix to the paper, the filters or the fitters reaches every page
# that has ever been generated the next time it is built.
# ─────────────────────────────────────────────────────────────────────────────

def deck_shell() -> tuple[str, str]:
    text = (ASSETS / "field-notes.html").read_text()
    head, rest = text.split('<main class="deck">', 1)
    return head, "</main>" + rest.split("</main>", 1)[1]


def index_shell() -> tuple[str, str]:
    text = (ASSETS / "notebook.html").read_text()
    head = text.split("</defs></svg>", 1)[0] + "</defs></svg>\n"
    return head, '<script type="module">' + text.split('<script type="module">', 1)[1]


def titled(head: str, title: str) -> str:
    return re.sub(r"<title>.*?</title>", f"<title>{title} &mdash; Field Notes</title>",
                  head, count=1, flags=re.S)


def build_deck(notes: list[Note], title: str, home: str | None) -> str:
    head, tail = deck_shell()
    head = titled(head, title)
    if home:
        head = re.sub(r'<a class="home" href="[^"]*">.*?</a>',
                      f'<a class="home" href="index.html">&larr;&nbsp; {html.escape(home)}</a>',
                      head, count=1, flags=re.S)
    else:
        # No index to return to: a link back to a page you are not delivering
        # is worse than no link.
        head = re.sub(r'<a class="home" href="[^"]*">.*?</a>\n', "", head, count=1, flags=re.S)
    return head + '<main class="deck">\n\n' + "\n".join(render_slide(n) for n in notes) + "\n" + tail


def build_page(title: str, meta: str, cols: int, cards: str, home: str | None,
               shelf: bool = False) -> str:
    head, tail = index_shell()
    back = f'<a class="home" href="{home}">&larr; Notebooks</a>\n    ' if home else ""
    klass = "cards cards--shelf" if shelf else "cards"
    return (titled(head, title) + "\n"
            '<div class="desk">\n\n  <header class="masthead">\n    ' + back +
            f'<h1 class="title jitter">{html.escape(title)}</h1>\n'
            f'    <p class="meta jitter">{meta}</p>\n  </header>\n\n'
            f'  <main class="{klass}" style="--cols:{cols}">\n\n{cards}\n  </main>\n</div>\n\n\n'
            + tail)


# ─────────────────────────────────────────────────────────────────────────────
# Builds
# ─────────────────────────────────────────────────────────────────────────────

def notes_in(folder: Path) -> list[Path]:
    return sorted(p for p in folder.glob("*.md") if not p.name.startswith("_"))


def folder_meta(folder: Path, stem: str) -> dict[str, object]:
    source = folder / f"_{stem}.md"
    return parse_front_matter(source.read_text())[0] if source.is_file() else {}


def copy_assets(src: Path, dst: Path) -> None:
    """Marks, photographs and anything else lying beside the notes."""
    for item in src.iterdir():
        if item.name.startswith("_") or item.suffix == ".md":
            continue
        target = dst / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)


def build_notebook(folder: Path, out: Path, home: str | None) -> tuple[str, int]:
    notes = [read_note(p) for p in notes_in(folder)]
    if not notes:
        raise SystemExit(f"no notes in {folder}")
    meta = folder_meta(folder, "notebook")
    title = str(meta.get("title") or folder.name.replace("-", " ").title())

    out.mkdir(parents=True, exist_ok=True)
    (out / "deck.html").write_text(build_deck(notes, title, title))
    (out / "index.html").write_text(build_page(
        title,
        str(meta.get("meta") or f"{len(notes)} sheet{'s' * (len(notes) != 1)}"),
        4, "\n".join(render_card(n) for n in notes), home))
    copy_assets(folder, out)
    return title, len(notes)


def build_shelf(folder: Path, out: Path) -> None:
    books = sorted(p for p in folder.iterdir() if p.is_dir() and notes_in(p))
    if not books:
        raise SystemExit(f"no notebooks in {folder}")
    covers, total = [], 0
    for book in books:
        title, count = build_notebook(book, out / book.name, "../notebooks.html")
        line = str(folder_meta(book, "notebook").get("line")
                   or f"{count} sheet{'s' * (count != 1)}")
        covers.append(render_cover(book.name, title, line))
        total += count

    meta = folder_meta(folder, "shelf")
    out.mkdir(parents=True, exist_ok=True)
    (out / "notebooks.html").write_text(build_page(
        str(meta.get("title") or "Notebooks"),
        str(meta.get("meta") or f"{len(books)} notebooks &middot; {total} sheets"),
        5, "\n".join(covers), None, shelf=True))


def build_sheet(source: Path, out: Path) -> None:
    note = read_note(source)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{note.id}.html").write_text(build_deck([note], note.title, None))
    copy_assets(source.parent, out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("source", type=Path, help="a .md note, a notebook folder, or a folder of them")
    ap.add_argument("-o", "--out", type=Path, default=Path("site"))
    ap.add_argument("--shape", choices=["auto", "sheet", "notebook", "shelf"], default="auto")
    args = ap.parse_args(argv)

    src: Path = args.source
    shape = args.shape
    if shape == "auto":
        if src.is_file():
            shape = "sheet"
        elif notes_in(src):
            shape = "notebook"
        else:
            shape = "shelf"

    if shape == "sheet":
        source = src if src.is_file() else notes_in(src)[0]
        build_sheet(source, args.out)
    elif shape == "notebook":
        build_notebook(src, args.out, None)
    else:
        build_shelf(src, args.out)

    print(f"built {shape} → {args.out}")
    print(f"serve it:  python3 -m http.server --directory {args.out} 8000")
    return 0


if __name__ == "__main__":
    sys.exit(main())
