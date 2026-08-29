"""Ensure the Codex/ChatGPT release bundle contains real, current skills."""

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).parents[1]
CANONICAL_SKILLS = ROOT / "skills" / "tools"
PACKAGED_SKILLS = ROOT / "plugins" / "codex" / "tools" / "skills"
MANIFEST = ROOT / "plugins" / "codex" / "tools" / ".codex-plugin" / "plugin.json"
IGNORED_PARTS = {"__pycache__", ".DS_Store"}


def package_files(root: Path) -> dict[Path, bytes]:
    return {
        path.relative_to(root): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and not IGNORED_PARTS.intersection(path.relative_to(root).parts)
    }


class CodexPluginPackageTest(unittest.TestCase):
    def test_manifest_points_to_the_packaged_skills_directory(self) -> None:
        manifest = json.loads(MANIFEST.read_text())

        self.assertEqual(manifest["skills"], "./skills/")
        self.assertLessEqual(len(manifest["interface"]["displayName"]), 30)
        self.assertLessEqual(len(manifest["interface"]["shortDescription"]), 30)

    def test_packaged_skills_are_real_and_match_the_canonical_source(self) -> None:
        self.assertTrue(PACKAGED_SKILLS.is_dir())
        self.assertFalse(PACKAGED_SKILLS.is_symlink())

        packaged_skill_dirs = sorted(path.name for path in PACKAGED_SKILLS.iterdir() if path.is_dir())
        canonical_skill_dirs = sorted(path.name for path in CANONICAL_SKILLS.iterdir() if path.is_dir())
        self.assertEqual(packaged_skill_dirs, canonical_skill_dirs)

        for skill_dir in PACKAGED_SKILLS.iterdir():
            if skill_dir.is_dir():
                self.assertFalse(skill_dir.is_symlink())
                self.assertTrue((skill_dir / "SKILL.md").is_file())

        self.assertEqual(package_files(PACKAGED_SKILLS), package_files(CANONICAL_SKILLS))
