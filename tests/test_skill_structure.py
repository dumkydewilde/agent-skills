"""Every canonical skill has valid frontmatter and resolvable relative links."""

from __future__ import annotations

import re
from pathlib import Path
import unittest


ROOT = Path(__file__).parents[1]
SKILL_GROUPS = ("tools", "dstack", "studio")

FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)
NAME = re.compile(r"^name:\s*(.+)$", re.M)
DESCRIPTION = re.compile(r"^description:\s*(.+)$", re.M)
LINK = re.compile(r"\]\(([^)\s]+)\)")
URI_SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*:", re.I)
FENCE = re.compile(r"^\s*```")


def is_relative_file_link(link: str) -> bool:
    """A path we can check on disk, not a URL and not a template placeholder."""
    if URI_SCHEME.match(link):
        return False
    path = link.split("#", 1)[0]
    return bool(path) and ("/" in path or "." in path)

# Cursor-only keys. Neither Claude Code nor Codex honours them, so a skill that
# still carries one was ported without being read.
CURSOR_ONLY_KEYS = ("disable-model-invocation", "mode", "icon", "color", "reminder")


def skill_dirs(group: str) -> list[Path]:
    return sorted(p for p in (ROOT / "skills" / group).iterdir() if p.is_dir())


def outside_fences(text: str) -> list[str]:
    """Lines outside fenced code blocks, so template placeholders are not linted."""
    lines, in_fence = [], False
    for line in text.split("\n"):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append(line)
    return lines


class SkillFrontmatterTest(unittest.TestCase):
    def test_every_skill_has_a_name_matching_its_directory(self) -> None:
        for group in SKILL_GROUPS:
            for skill in skill_dirs(group):
                with self.subTest(skill=f"{group}/{skill.name}"):
                    md = skill / "SKILL.md"
                    self.assertTrue(md.is_file(), f"{skill} has no SKILL.md")

                    match = FRONTMATTER.match(md.read_text())
                    self.assertIsNotNone(match, f"{md} has no frontmatter")
                    frontmatter = match.group(1)

                    name = NAME.search(frontmatter)
                    self.assertIsNotNone(name, f"{md} has no name")
                    self.assertEqual(name.group(1).strip().strip('"'), skill.name)

                    description = DESCRIPTION.search(frontmatter)
                    self.assertIsNotNone(description, f"{md} has no description")
                    self.assertTrue(description.group(1).strip(), f"{md} has an empty description")

    def test_no_skill_carries_cursor_only_frontmatter(self) -> None:
        for group in SKILL_GROUPS:
            for skill in skill_dirs(group):
                with self.subTest(skill=f"{group}/{skill.name}"):
                    match = FRONTMATTER.match((skill / "SKILL.md").read_text())
                    frontmatter = match.group(1) if match else ""
                    for key in CURSOR_ONLY_KEYS:
                        self.assertIsNone(
                            re.search(rf"^{key}:", frontmatter, re.M),
                            f"{skill.name} carries the Cursor-only key '{key}'",
                        )


class SkillLinkTest(unittest.TestCase):
    def test_dstack_mode_explains_installed_path_resolution(self) -> None:
        paths = (
            ROOT / "skills" / "dstack" / "dstack-mode" / "SKILL.md",
            ROOT / "plugins" / "codex" / "dstack" / "skills" / "dstack-mode" / "SKILL.md",
        )

        for path in paths:
            with self.subTest(path=path.relative_to(ROOT)):
                text = path.read_text()

                self.assertIn(
                    "Resolve `playbooks/` and `references/` paths relative to this file.",
                    text,
                )
                self.assertNotIn("See `docs/dstack/UPSTREAM.md`", text)

    def test_relative_links_resolve(self) -> None:
        for group in SKILL_GROUPS:
            for md in sorted((ROOT / "skills" / group).rglob("*.md")):
                for line in outside_fences(md.read_text()):
                    for link in LINK.findall(line):
                        if not is_relative_file_link(link):
                            continue
                        target = md.parent / link.split("#", 1)[0]
                        with self.subTest(file=str(md.relative_to(ROOT)), link=link):
                            self.assertTrue(target.exists(), f"{md}: broken link to {link}")


if __name__ == "__main__":
    unittest.main()
