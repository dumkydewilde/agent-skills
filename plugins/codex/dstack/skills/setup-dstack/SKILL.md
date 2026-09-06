---
name: setup-dstack
description: "Configure which model dstack uses per role. Writes ~/.claude/dstack-models.md, an override layer the dstack skills read before spawning subagents. Use for /setup-dstack, 'configure dstack models', or changing which model runs a dstack role."
---

# Setup dstack

Write `~/.claude/dstack-models.md`, a per-role model table the dstack skills read before spawning a subagent. Every skill falls back to its inline default when a line is absent, so this is an override layer, not a requirement. Nothing breaks if the file does not exist.

Upstream wrote a Cursor `.mdc` rule with `alwaysApply: true`. Claude Code has no equivalent, so this is a plain markdown file the skills read on demand.

## Precedence

1. `.claude/dstack-models.md` in the repo, when present. Project settings win.
2. `~/.claude/dstack-models.md`.
3. The inline default in each skill.

## Values

A value is a Claude Code model name, `opus`, `sonnet`, `haiku`, or `fable`. The alias `inherit` means the role runs on the parent chat model, so the caller omits `model` on the Agent call.

Panel roles take a comma-separated list. **One subagent runs per entry, so the list length sets the fan-out.** A three-entry list spawns three reviewers.

The Agent tool has no reasoning-effort parameter, so a role is a model choice only. Differentiate panelists by the lens in their prompt, not by effort.

## Steps

### 1. Load current state

Read `~/.claude/dstack-models.md` if it exists and treat its values as the current choices. Otherwise start from the defaults in step 4.

### 2. Confirm

Show every role with its current model. Ask whether to accept as-is or change specific roles, offering `opus`, `sonnet`, `haiku`, `fable`, and `inherit`. Prefer a structured question over free text. For panel roles, confirm the list length too, since it sets how many subagents spawn.

### 3. Validate

Every value must be one of `opus`, `sonnet`, `haiku`, `fable`, or `inherit`. Reject anything else and ask again. A table pointing at a name the Agent tool rejects breaks every delegation that reads it.

### 4. Write the file

Overwrite the whole file so re-runs stay idempotent. Shape:

```markdown
# dstack model configuration

One line per role. Delete a line to fall back to the skill default.
Values: opus | sonnet | haiku | fable | inherit.
A panel role takes a list, and one subagent runs per entry.

feature, refactoring: sonnet
bug-fix: opus
perf-issue: opus
judgment and prose: fable
hardest tasks: opus
how explorer: sonnet
how explainer: fable
how critics: fable, opus, sonnet
why investigators: sonnet
why synthesizer: fable
reflect tooling: opus
reflect judgment, divergent, synthesizer: fable
arena runners: fable, opus, sonnet
arena cross-judge pool: fable, opus
swarm workers: sonnet
architect runners: fable, opus, sonnet
interrogate reviewers: fable, opus, sonnet

## Cross-vendor panelist (codex)

Each panel role listed here adds one non-Agent reviewer run through Bash.
This is not a `model` value and never goes on an Agent call.

codex panelist: interrogate reviewers, arena cross-judge pool, architect runners, how critics
```

Keep the codex section unless the user opts out. It is the only part of this
file that buys real reviewer diversity; the rest picks between models that
share a vendor.

### 5. Check that codex actually runs

Do not write the codex line on faith. Run one throwaway call and read the
output:

```bash
codex exec --model gpt-5.6-terra --sandbox read-only \
  -o /tmp/codex-check.md "Reply with exactly: CODEX_OK" \
  < /dev/null > /dev/null 2>&1
cat /tmp/codex-check.md
```

`CODEX_OK` means the panelist works. A model-slug error means the CLI is older
than 0.153; either upgrade it or write `gpt-5.5` into the file instead. Anything
else (no `codex` on PATH, an auth failure) means drop the codex section and tell
the user the panels are single-vendor until they fix it.

See [`../dstack-mode/references/codex-panelist.md`](../dstack-mode/references/codex-panelist.md)
for what each flag is doing.

### 6. Confirm

Tell the user the file was written and that skills pick it up on their next run.

Say plainly which panels now carry a codex reviewer, and that agreement between
two Claude panelists is weaker evidence than agreement between a Claude
panelist and codex. If step 5 failed and you dropped the codex section, say that
instead, and say what would fix it.

### 7. Offer a verification skill (optional)

Check whether the project has a way to drive the real app for proof (a `verify-*` skill, or an existing harness). If not, offer once: "want a project-local verification skill, so agents can drive the app the way a user does and prove changes work? I can generate one with **create-verification-skill**." On yes, invoke it. On no, move on without pushing.
