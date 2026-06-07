---
name: conversation-history
description: Search past Claude, Codex, and ChatGPT conversations. Use when user asks "did we discuss", "what did we talk about", "find conversation about", "search history", "past conversations", or references something from a previous assistant session.
---

# Conversation History Search

Search local assistant conversation history across Claude Code, Claude Desktop exports, Codex sessions, and ChatGPT exports.

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
- **Claude Desktop exports**: `~/conductor/claude-desktop-export/*/conversation.json`
- **Codex**: `~/.codex/sessions/**/*.jsonl`
- **ChatGPT exports**: `conversations.json` from common export locations or `CONVERSATION_HISTORY_CHATGPT_EXPORT`

The ChatGPT macOS app also stores local `conversations-v3-*/*.data` files under `~/Library/Application Support/com.openai.chat/`, but those files are binary/encrypted on this machine and are not directly searchable. Export ChatGPT data to `conversations.json` for searchable ChatGPT history.

## How to Use Results

1. Run `search` to find relevant past conversations.
2. Use `show` with the session ID if the user needs more detail.
3. Summarize findings concisely instead of dumping raw messages.
4. Try multiple search terms for specific topics.

## Tips

- Search is case-insensitive.
- Results show `[YOU]` for human messages and `[AI]` for assistant messages.
- Use `--project codex`, `--project claude`, or `--project chatgpt` to narrow results by source.
