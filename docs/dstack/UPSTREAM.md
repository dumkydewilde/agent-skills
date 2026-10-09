# Provenance

dstack is a fork of **pstack** by Lauren Tan, MIT licensed.

- Upstream: <https://github.com/cursor/plugins/tree/main/pstack>
- Forked from: `cursor/plugins` commit `b9ddc83c32972210b8a94d389130713e8eed346e` (2026-08-31), pstack version 0.14.5
- License: MIT, see `LICENSE` alongside this file

This is a fork, not a mirror. There is no upstream sync pipeline, on purpose. The port rewrites the model routing, the PR flow, and the playbook set, so merging upstream would conflict on files that were deliberately changed. Pull upstream ideas by hand when they look worth it.

## What changed

### Dropped

Fifteen skills and eleven playbooks, because they assume Cursor, Graphite, Bugbot, cloud VMs, or the closed `cursor-team-kit` plugin.

- Skills: `setup-pstack` (replaced by `setup-dstack`), `automate-me`, `make-bot-ui`, `maintain-verification-skill`, and the `benny` automation pack.
- Playbooks: hillclimb, runtime-forensics, trace-forensics, visual-parity, babysit, shipping, orchestrate, autopilot-full, autopilot-stack, pause-safely, worktree-cleanup.

### Collapsed

The 21 `principle-*` skills became one `principles` skill with one file each under `references/`. Upstream shipped them as 21 top-level skills, which costs 21 entries in the session's skill list for one paragraph each. The index and the read-the-leaf-in-full rule are preserved.

### Added

- `authoring-skills`. Upstream deferred SKILL.md authoring to Cursor's built-in `/create-skill`, which does not exist here. This also covers the gap left by dropping superpowers' `writing-skills`.
- `docs-change` playbook. No upstream equivalent. The deliverable is prose that has to be correct against a running product, so every sample gets executed.
- `dstack-mode/scripts/check_plan.py`. A Python port of upstream's `check-plan.mjs`, rewritten against the leaner plan skeleton. Upstream's ran on Bun.
- `dstack-mode/references/review-triage.md`. Upstream's `bugbot-triage.md`, generalized off Bugbot and Graphite.
- `keep-history-out-of-the-artifact`, a twenty-second principle. No upstream equivalent. Added after artifacts kept shipping with their own edit history inside them: `v2` names, "now supports" docs, "(was X)" UI copy, comments describing the change instead of the code. `interrogate` and `unslop` check for it.
- `dehistorize`. The remediation pass for that principle, for an artifact that already shipped with the leaks; the principle stops you writing them, the skill removes them. Most of it is about what not to delete. An unguided baseline run on a seeded fixture found every leak and then also deleted the changelog and the migration guide, both of which exist to carry the delta.
- Intent freeze in `interrogate`, with a **Challenge the intent** section, plus the `ask:` todo and the **Deviations from the ask** reply line in `dstack-mode`. Added after a session let a unanimous plan review swap the dataset and turn a one-minute demo into a seventeen-hour backfill without asking. Upstream trusts cross-vendor agreement as signal; here, agreement on a leading question is treated as a prompt defect. A finding that would change the goal is carried to the human as an open decision while the work continues on the ask as stated, so autonomy is kept by staying on the goal rather than by stopping.

### Translated

| Upstream | Here |
|---|---|
| `.cursor-plugin/plugin.json` | `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` |
| `mode`, `icon`, `color`, `reminder`, `disable-model-invocation` frontmatter | removed, no equivalent in either harness |
| `~/.cursor/rules/pstack-models.mdc` with `alwaysApply: true` | `~/.claude/dstack-models.md`, read on demand by the skills |
| Model slugs across four vendors | `opus`, `sonnet`, `haiku`, `fable`, `inherit` |
| `readonly: true` on subagents | a prompt constraint, plus `subagent_type: Explore` where a search agent fits |
| `environment: "cloud"`, `cloud_base_branch` | local subagents with `isolation: "worktree"` |
| `subagent_type: generalPurpose` | `subagent_type: general-purpose` |
| `AskQuestion` | ask in plain text, or the Conductor MCP question tool |
| Cursor `/create-skill` | the `authoring-skills` skill |
| Cursor `/loop` | the `/loop` skill |
| `/deslop` from `cursor-team-kit` | the built-in `/simplify` skill |
| `control-ui` / `control-cli` from `cursor-team-kit` | Playwright or Chrome DevTools MCP, scripted CLI runs, or `create-verification-skill` |
| Graphite `gt` stacks | `gh` and stacked branches |
| Bugbot | `references/review-triage.md`, generalized to any review bot |
| Cursor transcript paths | the `conversation-history` skill from the `tools` plugin, which also covers Codex and ChatGPT |
| `poteto-agent`, `Comment Sicko` | `dstack-agent`, `comment-sicko`, in `plugins/claude/dstack/agents/` |

### The known weak spot

Upstream's `how` critics, `arena` runners, `architect` runners, and `interrogate` reviewers each fanned out across four vendors, and treated cross-vendor agreement as the signal. Every panel here is Claude models, so that signal is weaker and correlated blind spots are the real risk.

Two mitigations are in place. Each panelist gets a distinct lens rather than an identical brief, and the skills say to weight agreement lower than upstream did.

The real fix is a panelist that is not a Claude model. Codex is installed and runs headless, so `codex exec --model gpt-5.6-terra` folded in as an extra reviewer is the planned next step. `interrogate` and `arena` both carry the note where it plugs in.

### Not ported to Codex

The Codex plugin manifest format has no `agents` key, so `dstack-agent` and `comment-sicko` are Claude Code only. In Codex, `dstack-mode` still works; references to `subagent_type: "dstack-agent"` degrade to an ordinary subagent that should be told to read `dstack-mode/SKILL.md` first.
