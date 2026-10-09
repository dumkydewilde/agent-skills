#!/usr/bin/env python3
"""
Search local assistant conversation history.

Data sources:
  - Claude Code / Conductor: ~/.claude/projects/*/*.jsonl
  - Claude Desktop exports: ~/conductor/claude-desktop-export/*/conversation.json
  - Codex: ~/.codex/sessions/**/*.jsonl
  - ChatGPT exports: conversations.json from common export locations or
    CONVERSATION_HISTORY_CHATGPT_EXPORT

Usage:
  python3 conversation_history.py search "QUERY" [--project NAME] [--limit N]
  python3 conversation_history.py list [--limit N]
  python3 conversation_history.py show SESSION_ID [--human-only]
  python3 conversation_history.py index
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Iterator

HOME = Path.home()
HOME_DIR_PREFIX = str(HOME).replace("/", "-") + "-"
CLAUDE_PROJECTS = HOME / ".claude" / "projects"
CLAUDE_DESKTOP_EXPORT = HOME / "conductor" / "claude-desktop-export"
CODEX_SESSIONS = HOME / ".codex" / "sessions"
CHATGPT_APP_SUPPORT = HOME / "Library" / "Application Support" / "com.openai.chat"
CHATGPT_EXPORT_CANDIDATES = (
    # The conversation-archive sync consolidates each export here, so prefer it.
    HOME / "data" / "chatgpt-export" / "conversations.json",
    HOME / "Downloads" / "conversations.json",
    HOME / "Downloads" / "chatgpt-export" / "conversations.json",
    HOME / "Downloads" / "ChatGPT-export" / "conversations.json",
    HOME / "conductor" / "chatgpt-export" / "conversations.json",
    HOME / "conductor" / "ChatGPT-export" / "conversations.json",
    HOME / ".agents" / "chatgpt-export" / "conversations.json",
)


@dataclass(frozen=True)
class Session:
    session_id: str
    source: str
    project: str
    path: Path
    timestamp: datetime
    extra: dict[str, Any] | None = None


def parse_timestamp(value: Any, fallback: datetime) -> datetime:
    if isinstance(value, (int, float)):
        # ChatGPT exports use Unix seconds. Some local formats use ms.
        if value > 10_000_000_000:
            value = value / 1000
        try:
            return datetime.fromtimestamp(value)
        except (OSError, OverflowError, ValueError):
            return fallback
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            return fallback
    return fallback


def path_mtime(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_mtime)


def clean_project_name(project_dir: Path) -> str:
    # Claude Code encodes a project's absolute path by swapping "/" for "-".
    name = project_dir.name
    return name.removeprefix(HOME_DIR_PREFIX).replace("-", "/")


def extract_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(part for part in (extract_text(item) for item in value) if part)
    if isinstance(value, dict):
        if isinstance(value.get("text"), str):
            return value["text"]
        if isinstance(value.get("value"), str):
            return value["value"]
        if "parts" in value:
            return extract_text(value["parts"])
        if "content" in value:
            return extract_text(value["content"])
    return ""


def iter_claude_code_sessions() -> Iterator[Session]:
    if not CLAUDE_PROJECTS.exists():
        return
    for project_dir in CLAUDE_PROJECTS.iterdir():
        if not project_dir.is_dir():
            continue
        project = clean_project_name(project_dir)
        for jsonl in project_dir.glob("*.jsonl"):
            session_id = jsonl.stem
            if not re.match(r"^[0-9a-f]{8}-", session_id):
                continue
            yield Session(session_id, "claude-code", project, jsonl, path_mtime(jsonl))


def iter_claude_desktop_sessions() -> Iterator[Session]:
    if not CLAUDE_DESKTOP_EXPORT.exists():
        return
    for entry in CLAUDE_DESKTOP_EXPORT.iterdir():
        conv = entry / "conversation.json"
        if conv.exists():
            yield Session(entry.name, "claude-desktop", "desktop", conv, path_mtime(conv))


def read_codex_meta(path: Path) -> tuple[str, datetime]:
    project = "codex"
    timestamp = path_mtime(path)
    with path.open("r", errors="replace") as f:
        for _ in range(20):
            line = f.readline()
            if not line:
                break
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if item.get("type") != "session_meta":
                continue
            payload = item.get("payload", {})
            cwd = payload.get("cwd")
            if isinstance(cwd, str) and cwd:
                project = cwd.replace(str(HOME) + "/", "")
            timestamp = parse_timestamp(payload.get("timestamp") or item.get("timestamp"), timestamp)
            break
    return project, timestamp


def iter_codex_sessions() -> Iterator[Session]:
    if not CODEX_SESSIONS.exists():
        return
    for jsonl in CODEX_SESSIONS.glob("**/*.jsonl"):
        session_id = jsonl.stem
        project, timestamp = read_codex_meta(jsonl)
        yield Session(session_id, "codex", project, jsonl, timestamp)


def chatgpt_export_paths() -> list[Path]:
    paths: list[Path] = []
    env_path = os.environ.get("CONVERSATION_HISTORY_CHATGPT_EXPORT")
    if env_path:
        candidate = Path(env_path).expanduser()
        if candidate.is_dir():
            candidate = candidate / "conversations.json"
        paths.append(candidate)
    paths.extend(CHATGPT_EXPORT_CANDIDATES)
    return list(dict.fromkeys(paths))


@lru_cache(maxsize=8)
def load_chatgpt_export(export_path: str) -> tuple[dict[str, Any], ...]:
    path = Path(export_path)
    try:
        with path.open("r", errors="replace") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return ()
    if not isinstance(data, list):
        return ()
    return tuple(conv for conv in data if isinstance(conv, dict))


def iter_chatgpt_export_sessions() -> Iterator[Session]:
    for export_path in chatgpt_export_paths():
        if not export_path.exists():
            continue
        for conv in load_chatgpt_export(str(export_path)):
            session_id = str(conv.get("id") or conv.get("conversation_id") or "")
            if not session_id:
                continue
            title = str(conv.get("title") or "untitled").strip() or "untitled"
            fallback = path_mtime(export_path)
            timestamp = parse_timestamp(conv.get("update_time") or conv.get("create_time"), fallback)
            yield Session(
                session_id=session_id,
                source="chatgpt-export",
                project=f"chatgpt/{title}",
                path=export_path,
                timestamp=timestamp,
                extra={"conversation_id": session_id},
            )


def all_sessions() -> list[Session]:
    sessions = (
        list(iter_claude_code_sessions())
        + list(iter_claude_desktop_sessions())
        + list(iter_codex_sessions())
        + list(iter_chatgpt_export_sessions())
    )
    sessions.sort(key=lambda s: s.timestamp, reverse=True)
    return sessions


def read_claude_code_messages(path: Path) -> Iterator[tuple[str, str]]:
    with path.open("r", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            msg_type = item.get("type")
            if msg_type not in ("user", "assistant"):
                continue
            msg = item.get("message", {})
            if isinstance(msg, dict):
                content = extract_text(msg.get("content", ""))
                role = msg.get("role", msg_type)
            else:
                content = str(msg)
                role = msg_type
            if content.strip():
                yield str(role), content


def read_claude_desktop_messages(path: Path) -> Iterator[tuple[str, str]]:
    with path.open("r", errors="replace") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return
    for msg in data.get("chat_messages", []):
        if not isinstance(msg, dict):
            continue
        sender = msg.get("sender", "")
        text = msg.get("text") or extract_text(msg.get("content", []))
        role = "user" if sender == "human" else "assistant"
        if text.strip():
            yield role, text


def read_codex_messages(path: Path) -> Iterator[tuple[str, str]]:
    with path.open("r", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if item.get("type") != "response_item":
                continue
            payload = item.get("payload", {})
            if payload.get("type") != "message":
                continue
            role = payload.get("role")
            if role not in ("user", "assistant"):
                continue
            text = extract_text(payload.get("content", []))
            if text.strip():
                yield role, text


def read_chatgpt_export_messages(session: Session) -> Iterator[tuple[str, str]]:
    target_id = (session.extra or {}).get("conversation_id", session.session_id)
    for conv in load_chatgpt_export(str(session.path)):
        if conv.get("id") != target_id and conv.get("conversation_id") != target_id:
            continue
        mapping = conv.get("mapping", {})
        nodes = list(mapping.values()) if isinstance(mapping, dict) else []
        nodes.sort(key=lambda n: ((n or {}).get("message") or {}).get("create_time") or 0)
        for node in nodes:
            if not isinstance(node, dict):
                continue
            message = node.get("message")
            if not isinstance(message, dict):
                continue
            author = message.get("author", {})
            role = author.get("role") if isinstance(author, dict) else None
            if role not in ("user", "assistant"):
                continue
            content = extract_text(message.get("content", {}))
            if content.strip():
                yield role, content
        return


def read_messages(session: Session) -> Iterator[tuple[str, str]]:
    if session.source == "claude-code":
        return read_claude_code_messages(session.path)
    if session.source == "claude-desktop":
        return read_claude_desktop_messages(session.path)
    if session.source == "codex":
        return read_codex_messages(session.path)
    if session.source == "chatgpt-export":
        return read_chatgpt_export_messages(session)
    return iter(())


def role_label(role: str) -> str:
    return "[YOU]" if role in ("user", "human") else "[AI]"


def snippet(text: str, max_len: int = 200) -> str:
    text = re.sub(
        r"<system[_-]?(?:instruction|reminder)[^>]*>.*?</system[_-]?(?:instruction|reminder)>",
        "",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > max_len:
        return text[:max_len] + "..."
    return text


def matches_filter(session: Session, project_filter: str | None) -> bool:
    if not project_filter:
        return True
    haystack = f"{session.source} {session.project} {session.session_id}".lower()
    return project_filter in haystack


def cmd_search(args: argparse.Namespace) -> None:
    query = args.query.lower()
    limit = args.limit or 20
    project_filter = args.project.lower() if args.project else None

    results = []
    for session in all_sessions():
        if not matches_filter(session, project_filter):
            continue
        try:
            matches = [(role, text) for role, text in read_messages(session) if query in text.lower()]
        except Exception:
            continue
        if matches:
            results.append((session, matches))

    if not results:
        print(f"No results found for '{args.query}'")
        return

    print(f"Found {len(results)} sessions matching '{args.query}'\n")
    for session, matches in results[:limit]:
        short_id = session.session_id[:12]
        print(
            f"--- {short_id} | {session.source} | {session.project} | "
            f"{session.timestamp.strftime('%Y-%m-%d %H:%M')} ({len(matches)} matches) ---"
        )
        for role, text in matches[:3]:
            print(f"  {role_label(role)} {snippet(text, 300)}")
        if len(matches) > 3:
            print(f"  ... and {len(matches) - 3} more matches")
        print()


def cmd_list(args: argparse.Namespace) -> None:
    limit = args.limit or 20
    sessions = all_sessions()
    print(f"Recent sessions ({len(sessions)} total, showing {min(limit, len(sessions))}):\n")
    for session in sessions[:limit]:
        short_id = session.session_id[:40]
        summary = ""
        try:
            for role, text in read_messages(session):
                if role in ("user", "human"):
                    summary = snippet(text, 100)
                    break
        except Exception:
            pass
        print(f"  {session.timestamp.strftime('%Y-%m-%d %H:%M')}  {short_id}")
        print(f"    {session.source} | {session.project}")
        if summary:
            print(f"    {summary}")
        print()


def cmd_show(args: argparse.Namespace) -> None:
    target = args.session_id.lower()
    human_only = args.human_only

    for session in all_sessions():
        if target not in session.session_id.lower() and target not in session.project.lower():
            continue
        print(f"Session: {session.session_id}")
        print(f"Source: {session.source}")
        print(f"Project: {session.project}")
        print(f"Date: {session.timestamp.strftime('%Y-%m-%d %H:%M')}")
        print(f"{'=' * 60}\n")
        try:
            for role, text in read_messages(session):
                if human_only and role not in ("user", "human"):
                    continue
                print(f"{role_label(role)} {snippet(text, 2000)}\n")
        except Exception as e:
            print(f"Error reading session: {e}")
        return

    print(f"No session found matching '{args.session_id}'")


def cmd_index(args: argparse.Namespace) -> None:
    sessions = all_sessions()
    print(f"Total searchable sessions: {len(sessions)}\n")

    by_source: dict[str, list[Session]] = {}
    for session in sessions:
        by_source.setdefault(session.source, []).append(session)

    for source in sorted(by_source):
        items = sorted(by_source[source], key=lambda s: s.timestamp, reverse=True)
        latest = items[0].timestamp.strftime("%Y-%m-%d")
        earliest = items[-1].timestamp.strftime("%Y-%m-%d")
        print(f"  {source}: {len(items)} sessions ({earliest} to {latest})")

    app_cache_count = sum(1 for _ in CHATGPT_APP_SUPPORT.glob("conversations-v3-*/*.data"))
    if app_cache_count:
        print(f"\n  chatgpt-app-cache: {app_cache_count} encrypted/binary local files (not searchable)")
        print("    Export ChatGPT data as conversations.json and set CONVERSATION_HISTORY_CHATGPT_EXPORT if needed.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Search local assistant conversations")
    sub = parser.add_subparsers(dest="command")

    p_search = sub.add_parser("search", help="Search conversations")
    p_search.add_argument("query", help="Search term")
    p_search.add_argument("--project", help="Filter by source, project, or session ID")
    p_search.add_argument("--limit", type=int, default=20, help="Max results")

    p_list = sub.add_parser("list", help="List recent sessions")
    p_list.add_argument("--limit", type=int, default=20, help="Max sessions to show")

    p_show = sub.add_parser("show", help="Show a specific conversation")
    p_show.add_argument("session_id", help="Session ID, title/project text, or partial match")
    p_show.add_argument("--human-only", action="store_true", help="Show only human messages")

    sub.add_parser("index", help="Generate session index")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    {"search": cmd_search, "list": cmd_list, "show": cmd_show, "index": cmd_index}[args.command](args)


if __name__ == "__main__":
    main()
