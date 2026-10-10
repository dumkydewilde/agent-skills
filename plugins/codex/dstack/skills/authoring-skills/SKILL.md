---
name: authoring-skills
description: "Write or edit a SKILL.md that actually changes agent behavior, and package it so both Claude Code and Codex load it. Use for /authoring-skills, 'write a skill for this', 'turn this into a skill', editing an existing SKILL.md, or fixing a skill that exists but never triggers."
---

# Authoring skills

Agent-facing prose has a higher bar than human prose. An unhelpful sentence in a README is noise. An unhelpful sentence in a SKILL.md is an instruction an agent will follow.

Upstream dstack deferred this to Cursor's built-in `/create-skill`, which does not exist here. This skill fills that hole.

## When a skill earns its place

Write one when the technique was not obvious to you, you would reach for it again across projects, and it applies more broadly than a single repo.

Do not write one for a one-off solution, a standard practice already documented elsewhere, or a project convention that belongs in `CLAUDE.md` or `AGENTS.md`. If the rule is mechanically enforceable with a lint, a type, or a script, encode it there instead and skip the prose entirely (the **encode-lessons-in-structure** principle).

## Baseline first

**If you did not watch an agent fail without the skill, you do not know what the skill needs to teach.**

1. Write the pressure scenario. A concrete task where you expect the wrong behavior.
2. Run it against a subagent with no skill present. Record the exact wrong move and the exact rationalization it used to get there.
3. Write the skill against those specific failures, not against your idea of what someone might get wrong.
4. Re-run the scenario with the skill present. If behavior did not change, the skill does not work yet, however well written it reads.
5. Look for the next rationalization and close it.

This is the **prove-it-works** principle applied to prose. For a structural change to an existing skill, the Eval playbook (`dstack-mode/playbooks/eval.md`) runs the blinded version of the same loop.

## The theory underneath

[`references/writing-for-agents.md`](references/writing-for-agents.md) covers context pointers, context load versus cognitive load, the information hierarchy, progressive disclosure, completion criteria, leading words, negation, and the no-op test. Read it when a skill does not trigger, when one has grown past a page, or when deciding what to inline and what to push behind a pointer.

## Frontmatter is the trigger

The `description` is the only thing a router sees before deciding whether to load the skill. A skill that never fires is almost always a description problem, not a body problem.

```yaml
---
name: kebab-case-name
description: "What it does, then when to use it. Include the literal phrases a user would type."
---
```

Rules that matter:

- `name` is kebab-case and matches the directory name.
- `description` names the trigger conditions, not just the topic. "Search past conversations" is weak. "Use when the user asks 'did we discuss', 'what did we talk about', or references a previous session" fires.
- Include the slash-command form and the natural phrasings side by side.
- Keep Cursor-only keys out. `disable-model-invocation`, `mode`, `icon`, `color`, and `reminder` do nothing in Claude Code or Codex, and their absence means a skill upstream marked non-invocable becomes invocable here.
- Codex reads the same `name` and `description`. Nothing else in the frontmatter is portable.

## Writing the body

Tell it to do the thing. Skip the reason unless the rule is confusing without one.

- When in doubt, delete. Prose earns its keep by changing a decision.
- Point at structural sources (types, READMEs, config, real file paths). Hardcoded details go stale.
- Delegate to other skills by name and path. Do not restate their rules.
- Match tone to scope. A one-rule skill does not need five headings.
- Every referenced file must exist. Every cross-skill link must resolve.
- Bundled scripts cannot rely on `${CLAUDE_PLUGIN_ROOT}`; it only expands in slash commands and hooks. Reference a script through the skill's announced base directory instead.

## Packaging in this repo

Canonical source lives once under `skills/<group>/<skill-name>/`. The Claude plugin symlinks to it. The Codex plugin carries a real copy, because the Codex importer ignores symlinks directly under `skills/`.

1. Add `skills/<group>/<skill-name>/SKILL.md` plus any references, scripts, or assets.
2. Run `scripts/sync-plugin-skills.sh`.
3. Run `python3 -m unittest discover -s tests`. The parity test fails if the Codex copy drifted.
4. Commit both the canonical skill and the generated Codex copy.

## Validate before you ship

- Frontmatter parses, and `name` matches the directory.
- Every referenced path exists.
- The description contains the phrases you expect to trigger on.
- The pressure scenario passes with the skill and failed without it.
- No long dashes and no mid-sentence colons, per the **unslop** skill.

**Reply:** what the skill does, the baseline failure it was written against, the key design decisions, and the validation results.
