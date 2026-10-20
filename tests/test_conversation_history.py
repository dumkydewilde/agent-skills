"""Conversation readers use synthetic local SQLite/JSON fixtures, never a browser or account."""

from __future__ import annotations

from contextlib import redirect_stdout
import importlib
import io
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from argparse import Namespace
from unittest.mock import patch


ROOT = Path(__file__).parents[1]
SKILL_DIR = ROOT / "skills" / "tools" / "conversation-history"
sys.path.insert(0, str(SKILL_DIR))
history = importlib.import_module("conversation_history")


class ClaudeBrowserExportTest(unittest.TestCase):
    def test_single_and_bulk_exports_are_searchable_without_hidden_or_tool_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = {"uuid": "synthetic-chat", "name": "Browser example", "updated_at": "2026-09-01T00:00:00Z",
                    "current_leaf_message_uuid": "selected", "chat_messages": [
                        {"uuid": "user", "sender": "human", "text": "", "parent_message_uuid": "root",
                         "content": [{"type": "text", "text": "Synthetic sunflower query"}]},
                        {"uuid": "alternative", "sender": "assistant", "text": "Discarded alternative",
                         "parent_message_uuid": "user"},
                        {"uuid": "selected", "sender": "assistant", "text": "", "parent_message_uuid": "user",
                         "content": [{"type": "text", "text": "Selected answer"},
                                     {"type": "tool_result", "content": [{"type": "text", "text": "Private memory"}]},
                                     {"type": "thinking", "thinking": "Hidden reasoning"}]},
                    ]}
            (root / "single.json").write_text(json.dumps(data))
            newer = dict(data, updated_at="2026-09-02T00:00:00Z")
            (root / "bulk.json").write_text(json.dumps([newer, dict(data, uuid="synthetic-chat-two")]))
            (root / "broken.json").write_text("{")
            history.load_claude_conversations.cache_clear()
            with patch.object(history, "CLAUDE_DESKTOP_EXPORT_DIRS", ()), patch.dict(
                os.environ, {"CONVERSATION_HISTORY_CLAUDE_EXPORT": str(root)}
            ):
                sessions = list(history.iter_claude_desktop_sessions())
            self.assertEqual(len(sessions), 2)
            for session in sessions:
                self.assertEqual(list(history.read_messages(session)), [
                    ("user", "Synthetic sunflower query"), ("assistant", "Selected answer")])
            self.assertEqual(next(s for s in sessions if s.session_id == "synthetic-chat").path.name, "bulk.json")
            history.load_claude_conversations.cache_clear()


class OpenCodeHistoryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.data_home = Path(self.temp_dir.name)
        self.data_dir = self.data_home / "opencode"
        self.data_dir.mkdir()

    def database_from_fixture(self, fixture: str) -> Path:
        path = self.data_dir / "opencode.db"
        connection = sqlite3.connect(path)
        try:
            connection.executescript((ROOT / "tests" / "fixtures" / fixture).read_text())
            connection.commit()
        finally:
            connection.close()
        return path

    def test_v2_database_sessions_and_searchable_text(self) -> None:
        path = self.database_from_fixture("opencode_v2.sql")
        with patch.dict(os.environ, {"XDG_DATA_HOME": str(self.data_home), "OPENCODE_DB": ""}):
            sessions = list(history.iter_opencode_sessions())
            self.assertEqual(history.opencode_db_path(), path)
            self.assertEqual(len(sessions), 1)
            session = sessions[0]
            self.assertEqual(session.session_id, "ses_synthetic_v2")
            self.assertEqual(session.source, "opencode")
            self.assertEqual(session.project, "sample-app")
            self.assertEqual((session.extra or {}).get("title"), "Synthetic session title")
            self.assertEqual(
                list(history.read_opencode_messages(session)),
                [
                    ("user", "Synthetic sunflower lookup phrase"),
                    ("assistant", "Synthetic assistant answer"),
                ],
            )

    def test_search_cli_finds_opencode_and_title_filter(self) -> None:
        self.database_from_fixture("opencode_v2.sql")
        environment = {"XDG_DATA_HOME": str(self.data_home), "OPENCODE_DB": ""}
        with (
            patch.dict(os.environ, environment),
            patch.object(history, "iter_claude_code_sessions", return_value=iter(())),
            patch.object(history, "iter_claude_desktop_sessions", return_value=iter(())),
            patch.object(history, "iter_codex_sessions", return_value=iter(())),
            patch.object(history, "iter_chatgpt_export_sessions", return_value=iter(())),
        ):
            output = io.StringIO()
            with redirect_stdout(output):
                args = Namespace(
                    query="sunflower", limit=20, project="synthetic session title"
                )
                history.cmd_search(args)

        result = output.getvalue()
        self.assertIn("opencode", result)
        self.assertIn("Synthetic sunflower lookup phrase", result)
        self.assertNotIn("Synthetic hidden reasoning", result)
        self.assertNotIn("Synthetic tool output", result)

    def test_legacy_message_and_part_tables_remain_readable(self) -> None:
        self.database_from_fixture("opencode_legacy.sql")
        with patch.dict(os.environ, {"XDG_DATA_HOME": str(self.data_home), "OPENCODE_DB": ""}):
            sessions = list(history.iter_opencode_sessions())
            self.assertEqual(len(sessions), 1)
            self.assertEqual(sessions[0].session_id, "ses_synthetic_legacy")
            self.assertEqual(
                list(history.read_opencode_messages(sessions[0])),
                [("user", "Synthetic legacy search phrase")],
            )

    def test_database_override_and_connection_are_read_only(self) -> None:
        path = self.database_from_fixture("opencode_v2.sql")
        environment = {"XDG_DATA_HOME": str(self.data_home), "OPENCODE_DB": "opencode.db"}
        with patch.dict(os.environ, environment):
            self.assertEqual(history.opencode_db_path(), path)
            connection = history.open_opencode_db(path)
            self.addCleanup(connection.close)
            with self.assertRaises(sqlite3.OperationalError):
                connection.execute("CREATE TABLE should_not_be_created (id TEXT)")


if __name__ == "__main__":
    unittest.main()
