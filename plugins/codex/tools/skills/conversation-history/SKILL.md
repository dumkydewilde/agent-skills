---
name: conversation-history
description: "Searches past Claude, Codex, OpenCode, and ChatGPT conversations from local logs/exports, and offers a consent-based browser extension for missing web history. Use for 'did we discuss', 'find conversation about', 'search history', 'search Claude web chats', 'export my conversations', or references to a previous assistant session."
---

# Conversation History Search

Search local assistant conversation history across Claude Code, Claude Desktop exports, Codex sessions, OpenCode, and ChatGPT exports.

## Tool Location

This skill bundles `conversation_history.py` in its own directory. When the skill
loads, the harness prints its absolute path as the skill's **base directory**.
Set that as `SKILL_DIR` once, then call the script from there:

```bash
# Replace the path with this skill's base directory (shown when the skill loaded):
SKILL_DIR="/path/to/this/skill"
```

All commands below use `"$SKILL_DIR/conversation_history.py"`. The script only
needs `python3` (standard library) and reads data from your home directory, so
it works on any machine where the plugin is installed.

## Available Commands

### Search for a topic
```bash
python3 "$SKILL_DIR/conversation_history.py" search "QUERY"
```
Optional: filter by source, project, or session ID with `--project NAME` (for example, `--project codex`, `--project claude-code`, `--project motherduck`, `--project chatgpt`).

### List recent sessions
```bash
python3 "$SKILL_DIR/conversation_history.py" list --limit 20
```

### Show a specific conversation
```bash
python3 "$SKILL_DIR/conversation_history.py" show SESSION_ID --human-only
```
`SESSION_ID` can be a partial match, and `show` also matches project/title text.

### Generate source index
```bash
python3 "$SKILL_DIR/conversation_history.py" index
```

## Data Sources

- **Claude Code / Conductor**: `~/.claude/projects/*/*.jsonl`
- **Claude web/Desktop exports**: `~/.agents/conversations/claude-desktop/`, legacy
  `~/conductor/claude-desktop-export/`, or `CONVERSATION_HISTORY_CLAUDE_EXPORT` (a JSON file or directory).
  Single-chat JSON and bulk arrays are supported; visible text on the selected message branch is searched.
  The `claude-desktop` source label includes web chats for compatibility.
- **Codex**: `~/.codex/sessions/**/*.jsonl`
- **OpenCode v2**: `~/.local/share/opencode/opencode.db` (or
  `$XDG_DATA_HOME/opencode/opencode.db`). OpenCode stores session metadata in
  `session_v2` and messages in `session_message`; the script reads user/assistant
  text blocks and opens SQLite read-only. Set `OPENCODE_DB` to use a custom
  database path (relative paths resolve under the data directory).
  `opencode debug paths db` prints the active database path.
- **ChatGPT exports**: `conversations.json` from common export locations or `CONVERSATION_HISTORY_CHATGPT_EXPORT`

The ChatGPT macOS app also stores local `conversations-v3-*/*.data` files under `~/Library/Application Support/com.openai.chat/`, but those files are binary/encrypted on this machine and are not directly searchable. Export ChatGPT data to `conversations.json` for searchable ChatGPT history.

## How to Use Results

1. Run `search` to find relevant past conversations.
2. Use `show` with the session ID if the user needs more detail.
3. Summarize findings concisely instead of dumping raw messages.
4. Try multiple search terms for specific topics.
5. If local results are missing/incomplete or the user asks for web history, offer once: **"Would you
   like me to extend this search to your Claude web/Desktop conversations using a browser? You can
   sign in yourself; I’ll search only the agreed scope. Should matching exports stay temporary or be
   saved locally?"** Do not open or inspect a browser before consent. If they agree, follow
   [the browser extension workflow](references/browser-search.md). If they decline, local search still works.

## Usage metrics are a separate concern

This search tool exposes text/session metadata, not calculated token/cost totals. Ordinary Claude chat
JSON may contain no usage counters; text-length/tokenizer estimates are not actual billed usage.
Cowork remote session responses may instead contain `external_metadata.usage` with tokens, cache
counters, and service-reported cost. A usage-analysis skill, such as `common-review-claude-spend` if
separately installed, can import those snapshots. It should own aggregation/pricing rather than
duplicating it here. Keep snapshot cost separate from API-equivalent estimates and do not invent
daily/monthly attribution, cache TTL, miss causes, or historic model mix from a session snapshot.

## Tips

- Search is case-insensitive.
- Results show `[YOU]` for human messages and `[AI]` for assistant messages.
- Use `--project codex`, `--project claude`, or `--project chatgpt` to narrow results by source.
- Use `--project opencode` to search only OpenCode sessions.
