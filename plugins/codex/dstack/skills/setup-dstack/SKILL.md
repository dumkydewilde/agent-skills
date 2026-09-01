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
```

### 5. Confirm and note the single-vendor limit

Tell the user the file was written and that skills pick it up on their next run.

Say plainly that every panel is Claude models, so cross-model agreement is weaker evidence here than it was upstream, where panels spanned four vendors. Point at the `codex exec` note in **interrogate** and **arena** as the path to a genuinely independent reviewer.

### 6. Offer a verification skill (optional)

Check whether the project has a way to drive the real app for proof (a `verify-*` skill, or an existing harness). If not, offer once: "want a project-local verification skill, so agents can drive the app the way a user does and prove changes work? I can generate one with **create-verification-skill**." On yes, invoke it. On no, move on without pushing.
