#!/usr/bin/env python3
"""Check a multi-phase plan against the skeleton in playbooks/multi-phase-plan.md.

Usage: uv run --no-project check_plan.py <plan.md>

Exits 1 when the plan has problems, 0 when it is clean.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

RULE = (
    "Tests alone are not sufficient verification. "
    "A PR is verified only when its unit and live boxes are both checked."
)
SUB_BLOCKS = [
    "Depends on.",
    "Files.",
    "Build.",
    "You see.",
    "Verify, unit.",
    "Verify, live.",
    "Review gate.",
    "Merge.",
]
BOXED_BLOCKS = ["Files.", "Build.", "You see.", "Verify, unit.", "Verify, live.", "Merge."]
RULE_BLOCKS = ["Verify, unit.", "Verify, live."]
PROGRAM_H3 = ["Arm the program", "Order the work", "PR mechanics", "Verdict and merge"]
HOW_TO_READ_MARKERS = [
    "One box is one unit of work",
    "names the evidence",
    "Check a box only when its evidence exists",
    RULE,
]

BOX = re.compile(r"^\s*- \[[ x]\] (.*)$")
SUB_BLOCK_HEAD = re.compile(r"^\*\*([^*]+)\*\*(.*)$")
LANE = re.compile(r"^Lane (\d+)\. ")
INLINE_CODE = re.compile(r"`[^`]*`")
IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
LINK_TARGET = re.compile(r"\]\([^)]*\)")


@dataclass
class Line:
    n: int
    text: str
    code: bool


@dataclass
class Section:
    title: str
    n: int
    body: list[Line] = field(default_factory=list)


def strip_markup(text: str) -> str:
    """Drop code spans, image tags, and link targets so prose rules only see prose."""
    return LINK_TARGET.sub("]", IMAGE.sub("", INLINE_CODE.sub("`", text)))


def read_lines(raw: list[str]) -> list[Line]:
    start = 0
    if raw and raw[0] == "---":
        try:
            start = raw.index("---", 1) + 1
        except ValueError:
            start = 0

    lines: list[Line] = []
    in_fence = False
    for offset, text in enumerate(raw[start:]):
        if text.startswith("```"):
            in_fence = not in_fence
        lines.append(Line(n=start + offset + 1, text=text, code=in_fence))
    return lines


def split_sections(lines: list[Line]) -> list[Section]:
    sections: list[Section] = []
    for line in lines:
        if not line.code and line.text.startswith("## "):
            sections.append(Section(title=line.text[3:].strip(), n=line.n))
        elif sections:
            sections[-1].body.append(line)
    return sections


def boxes(lines: list[Line]) -> list[tuple[int, str]]:
    found = []
    for line in lines:
        if line.code:
            continue
        match = BOX.match(line.text)
        if match:
            found.append((line.n, match.group(1)))
    return found


class Checker:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.problems: list[str] = []
        self.report: list[str] = []

    def fail(self, line: int, message: str) -> None:
        self.problems.append(f"{self.path}:{line}: {message}")

    def check_prose(self, lines: list[Line]) -> None:
        for line in lines:
            if line.code:
                continue
            prose = strip_markup(line.text)
            if re.search(r"[–—]", prose):
                self.fail(line.n, "long dash")
            if re.search(r"[‘’“”]", prose):
                self.fail(line.n, "curly quote")
            if re.search(r": \S", prose):
                self.fail(line.n, "mid-sentence colon")

    def check_intro(self, lines: list[Line], sections: list[Section]) -> Section | None:
        h1 = next((i for i, l in enumerate(lines) if not l.code and l.text.startswith("# ")), None)
        if h1 is None:
            self.fail(1, "no H1 title")

        how_to_read = next((s for s in sections if s.title == "How to read this"), None)
        if how_to_read is None:
            self.fail(1, 'no "## How to read this" section')
            return None

        if h1 is not None:
            intro = [l for l in lines[h1 + 1 :] if l.n < how_to_read.n and l.text.strip()]
            if len(intro) >= 10:
                self.fail(lines[h1].n, f"intro is {len(intro)} lines, under ten required")

        body = "\n".join(l.text for l in how_to_read.body)
        for marker in HOW_TO_READ_MARKERS:
            if marker not in body:
                self.fail(how_to_read.n, f'How to read this lacks "{marker}"')
        return how_to_read

    def check_program(self, sections: list[Section]) -> Section | None:
        program = next((s for s in sections if s.title == "Program checklist"), None)
        if program is None:
            self.fail(1, 'no "## Program checklist" section')
            return None

        headings = [l.text[4:].strip() for l in program.body if not l.code and l.text.startswith("### ")]
        cursor = 0
        for name in PROGRAM_H3:
            at = next((i for i, t in enumerate(headings) if i >= cursor and t.startswith(name)), None)
            if at is None:
                self.fail(program.n, f'Program checklist lacks "### {name}" in order')
            else:
                cursor = at + 1
        return program

    def check_pr_section(self, pr: Section) -> None:
        heads: list[tuple[str, int, str, list[Line]]] = []
        for line in pr.body:
            if line.code:
                continue
            match = SUB_BLOCK_HEAD.match(line.text)
            if match and match.group(1) in SUB_BLOCKS:
                heads.append((match.group(1), line.n, match.group(2).strip(), []))
            elif heads:
                heads[-1][3].append(line)

        names = [h[0] for h in heads]
        if names != SUB_BLOCKS:
            self.fail(
                pr.n,
                f"{pr.title}: sub-blocks are [{', '.join(names)}], expected [{', '.join(SUB_BLOCKS)}]",
            )

        by_name = {h[0]: h for h in heads}

        depends = by_name.get("Depends on.")
        if depends and not depends[2]:
            self.fail(depends[1], f"{pr.title}: Depends on names nothing")

        for name in BOXED_BLOCKS:
            block = by_name.get(name)
            if block and not boxes(block[3]):
                self.fail(block[1], f"{pr.title}: {name} has no box")

        for name in RULE_BLOCKS:
            block = by_name.get(name)
            if block and not block[2].startswith(RULE):
                self.fail(block[1], f"{pr.title}: {name} does not open with the rule")

        live = by_name.get("Verify, live.")
        if live:
            lanes = [(n, t, LANE.match(t)) for n, t in boxes(live[3])]
            if not lanes:
                self.fail(live[1], f"{pr.title}: Verify, live has no lane")
            numbers = sorted(int(m.group(1)) for _, _, m in lanes if m)
            if numbers and numbers != list(range(1, len(numbers) + 1)):
                self.fail(live[1], f"{pr.title}: lanes are {numbers}, expected 1 to {len(numbers)}")
            for n, text, match in lanes:
                if not match:
                    self.fail(n, f"{pr.title}: live box is not a lane")
                elif not re.search(r"Save `[^`]+`", text):
                    self.fail(n, f"{pr.title}: lane {match.group(1)} names no artifact")
                elif "Pass when" not in text:
                    self.fail(n, f"{pr.title}: lane {match.group(1)} has no pass predicate")

        gate = by_name.get("Review gate.")
        if gate:
            gate_boxes = boxes(gate[3])
            if gate[2].startswith("None."):
                if gate_boxes:
                    self.fail(gate[1], f"{pr.title}: Review gate says None but has boxes")
            elif not gate_boxes:
                self.fail(gate[1], f"{pr.title}: Review gate has no box")

        counts = {h[0]: len(boxes(h[3])) for h in heads}
        cells = [
            f"{name.rstrip('.').replace(', ', '-').replace(' ', '-').lower()}={counts.get(name, 0)}"
            for name in SUB_BLOCKS
            if name != "Depends on."
        ]
        self.report.append(f"{pr.title}  boxes={len(boxes(pr.body))}  {' '.join(cells)}")

    def run(self) -> int:
        lines = read_lines(self.path.read_text().split("\n"))
        sections = split_sections(lines)

        self.check_prose(lines)
        self.check_intro(lines, sections)
        program = self.check_program(sections)

        close = next((s for s in sections if s.title == "Close the program"), None)
        if close is None:
            self.fail(1, 'no "## Close the program" section')

        pr_sections: list[Section] = []
        if program is not None and close is not None:
            pr_sections = sections[sections.index(program) + 1 : sections.index(close)]
            if not pr_sections:
                self.fail(1, "no PR sections between Program checklist and Close the program")

        for pr in pr_sections:
            self.check_pr_section(pr)

        if close is not None:
            tail = sections[sections.index(close) + 1 :]
            for section in tail:
                if not section.title.startswith("Appendix"):
                    self.fail(section.n, f'"## {section.title}" after Close the program is not an appendix')
            if not any("Prototype evidence" in s.title for s in tail):
                self.fail(close.n, 'no "## Appendix ... Prototype evidence" section')

        for line in self.report:
            print(line)
        print(f"{len(pr_sections)} PR sections, {len(self.problems)} problems")
        for problem in self.problems:
            print(problem, file=sys.stderr)
        return 1 if self.problems else 0


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: check_plan.py <plan.md>", file=sys.stderr)
        return 2
    path = Path(argv[1])
    if not path.is_file():
        print(f"no such file: {path}", file=sys.stderr)
        return 2
    return Checker(path).run()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
