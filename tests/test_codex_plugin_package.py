"""Ensure every Codex/ChatGPT release bundle contains real, current skills."""

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).parents[1]
PLUGINS = ("tools", "dstack")
IGNORED_PARTS = {"__pycache__", ".DS_Store"}


def canonical_skills(plugin: str) -> Path:
    return ROOT / "skills" / plugin


def packaged_skills(plugin: str) -> Path:
    return ROOT / "plugins" / "codex" / plugin / "skills"


def manifest_path(plugin: str) -> Path:
    return ROOT / "plugins" / "codex" / plugin / ".codex-plugin" / "plugin.json"


def package_files(root: Path) -> dict[Path, bytes]:
    return {
        path.relative_to(root): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and not IGNORED_PARTS.intersection(path.relative_to(root).parts)
    }


class CodexPluginPackageTest(unittest.TestCase):
    def test_manifest_points_to_the_packaged_skills_directory(self) -> None:
        for plugin in PLUGINS:
            with self.subTest(plugin=plugin):
                manifest = json.loads(manifest_path(plugin).read_text())

                self.assertEqual(manifest["name"], plugin)
                self.assertEqual(manifest["skills"], "./skills/")
                self.assertLessEqual(len(manifest["interface"]["displayName"]), 30)
                self.assertLessEqual(len(manifest["interface"]["shortDescription"]), 30)

    def test_packaged_skills_are_real_and_match_the_canonical_source(self) -> None:
        for plugin in PLUGINS:
            with self.subTest(plugin=plugin):
                packaged = packaged_skills(plugin)
                canonical = canonical_skills(plugin)

                self.assertTrue(packaged.is_dir())
                self.assertFalse(packaged.is_symlink())

                packaged_dirs = sorted(p.name for p in packaged.iterdir() if p.is_dir())
                canonical_dirs = sorted(p.name for p in canonical.iterdir() if p.is_dir())
                self.assertEqual(packaged_dirs, canonical_dirs)

                for skill_dir in packaged.iterdir():
                    if skill_dir.is_dir():
                        self.assertFalse(skill_dir.is_symlink())
                        self.assertTrue((skill_dir / "SKILL.md").is_file())

                self.assertEqual(package_files(packaged), package_files(canonical))

    def test_claude_plugin_symlinks_to_the_canonical_source(self) -> None:
        for plugin in PLUGINS:
            with self.subTest(plugin=plugin):
                link = ROOT / "plugins" / "claude" / plugin / "skills"

                self.assertTrue(link.is_symlink())
                self.assertEqual(link.resolve(), canonical_skills(plugin).resolve())
