# Provenance

The `studio` plugin, the `wizard` skill in `tools`, and four reference files inside `dstack` come from **[mattpocock/skills](https://github.com/mattpocock/skills)** by Matt Pocock, MIT licensed.

- Upstream: <https://github.com/mattpocock/skills>
- Ported from commit `49dd158d1076134a641b33efb035946536778336` (2026-10-09)
- License: MIT, see [`LICENSE`](LICENSE) alongside this file

This is a port, not a mirror. There is no upstream sync pipeline, on purpose. Every file here was rewritten against this repo's skill set, its tracker, and its stack, so merging upstream would conflict on files that were deliberately changed. Pull upstream ideas by hand when they look worth it.

Upstream ships 38 skills. Six were ported whole, three were folded into existing dstack skills as reference files, and the rest were left behind.

## What came across

### As the `studio` plugin

A new plugin, because these five share one property dstack does not have: a human has to be in the room. dstack's **never-block-on-the-human** principle and `dstack-mode`'s "probe instead of asking" rule both push the opposite way, and both are about facts. These are about decisions. Keeping them in their own plugin keeps that boundary visible, and keeps one upstream per provenance doc.

| Skill | Upstream | What changed |
|---|---|---|
| `grilling` | `skills/productivity/grilling` | Added the "this is the one place dstack asks" section, drawing the fact-versus-decision line against **never-block-on-the-human** explicitly. Fact-finding subagents now name `subagent_type: "Explore"` and `run_in_background: true` per **guard-the-context-window**. Added the closing line that a recommended answer is a judgment, not a menu. |
| `to-questionnaire` | `skills/productivity/to-questionnaire` | Added an `unslop` pass as step 4, and a note that the common case is a colleague several timezones out, so order for a single pass. |
| `writing-fragments` | `skills/in-progress/writing-fragments` | Points at the ported `grilling` for the interview mechanic. Added the "do not unslop the pile" section, because `unslop` and `technical-writing` are exploit-phase tools and running them here destroys raw material. |
| `writing-shape` | `skills/in-progress/writing-shape` | Added a Diátaxis mode choice as step 2 and an unslop-and-verify step 8 that runs every code sample against the real product, per **prove-it-works** and the `docs-change` playbook. |
| `wayfinder` | `skills/engineering/wayfinder` | The big one. Upstream abstracts over a configurable tracker and tells you to run `/setup-matt-pocock-skills` if none is set. Here the tracker is Linear, named directly, reached through the Linear MCP or the `linear-cli` skill, with a local-markdown fallback. The four ticket types were rewired onto skills that exist here: research to `why` or a background `Explore` agent, prototype to `dstack-mode`'s `playbooks/prototype.md`, grilling to the ported `grilling` plus the ADR and glossary references, task to the ported `wizard`. Added a "when this is the wrong tool" section pointing at `multi-phase-plan`, because wayfinder is the heaviest thing in this repo and ceremony scales with the task. |

`writing-beats` (`skills/in-progress/writing-beats`) was deliberately left behind. It is a second exploit mode alongside `writing-shape`, aimed at narrative essays. Carrying both would mean choosing between them every time.

Upstream marks `grilling`'s user-invoked twin `grill-me`, plus `to-questionnaire`, both writing skills, and `wayfinder` with `disable-model-invocation`. That key does nothing in Claude Code or Codex, so it was dropped and the descriptions were rewritten to carry real trigger phrases instead. The `grill-me` alias was dropped with it: it exists upstream only to force user invocation, and `/grilling` already does that here.

### Into `tools`

**`wizard`** (`skills/engineering/wizard`). `template.sh` came across byte for byte: it is the whole point of the skill, 223 lines of stage progress, confirmation gates, WSL-aware URL opening, hidden secret entry, idempotent `.env` upserts, and `gh secret` writes. The SKILL.md gained a "when a wizard is the right shape" section naming the fits in this stack (MotherDuck service-account tokens, Cloudflare and Vercel deploys, the homelab, cookbook setup sections) and the anti-fit (anything the agent can just run), plus a line tying it to **build-the-lever**.

It landed in `tools` rather than `studio` because it is a generator with a bundled library, not a conversation.

### Folded into `dstack`

Three upstream skills had content worth keeping and triggers that would have fought with skills already here. Each became a reference file under the skill that owns the trigger.

| Upstream | Landed as | Why folded instead of ported |
|---|---|---|
| `skills/engineering/domain-modeling` (ADR half) | `architect/references/adr-format.md` | The three-part test (hard to reverse, surprising without context, a real trade-off) is the whole value and nothing in dstack wrote an ADR. `architect` Phase C is where the trade-off already exists in writing. |
| `skills/engineering/domain-modeling` (glossary half) | `technical-writing/references/glossary-format.md` | Hooks onto review checklist item 6, "does each thing have exactly one name across the docs". The upstream multi-context `GLOSSARY-MAP.md` layout, with one glossary per bounded context under `src/`, was dropped: it assumes a DDD service layout that neither a docs repo nor a dbt project has. The single-glossary case and the whole active-maintenance half were kept. |
| `skills/engineering/retro` | `reflect/references/environment-audit.md` | Same input as `reflect` (the session transcript), different output. `reflect` produces skill edits; `retro` produces repo and tooling changes. Shipped as a fourth parallel reviewer whose findings file under Backlog rather than taking a Routing. |
| `skills/productivity/writing-for-agents` | `authoring-skills/references/writing-for-agents.md` | Trigger overlapped `authoring-skills` head on; content did not overlap at all. `authoring-skills` says what to do, this says why: context pointers, the two loads, the information hierarchy, completion criteria, leading words, negation, the no-op test. The pointer to upstream's `SKILL-MECHANICS.md`, which was not ported, now points at `authoring-skills` itself. |

## What was left behind

- **Already covered here, usually tighter.** `ask-matt` (`dstack-mode` routes), `code-review` (the built-in plus `interrogate`), `tdd`, `prototype` (a dstack playbook), `research` (12 lines, less than `why` does), `diagnosing-bugs` (the bug-fix playbook), `pr` (the opening-a-pr playbook), `handoff` and `claude-handoff` (Conductor plus `recall` plus `conversation-history`), `grill-with-docs`, `improve-codebase-architecture`.
- **Name collisions.** `teach` exists here and means something else: dstack's explains a body of work, upstream's runs a multi-session tutoring workspace. `wait-what` is `bro`.
- **Wrong stack.** `codebase-design` and `setup-ts-deep-modules` are Ousterhout deep modules via dependency-cruiser, TypeScript only. `migrate-to-shoehorn`, `scaffold-exercises`, `setup-pre-commit` are TypeScript and Husky. `git-guardrails-claude-code` duplicates an existing permission setup.
- **A coupled system.** `to-spec`, `to-tickets`, `triage`, `implement`, `implement-spec`, and `setup-matt-pocock-skills` share a tracker-config contract. Taking one means taking all six, and they would collide with dstack's playbooks. `wayfinder` was the exception worth paying for, and its tracker dependency was rewritten rather than imported.
- **Beta siblings.** `chief-of-staff`, `loop-me`, `writing-beats`.

## Attribution

Every ported skill carries a `metadata.credits` block in its frontmatter, naming the skill, Matt Pocock, the MIT license, and the upstream file URL. That block is upstream's own convention: their `pr` skill uses the same shape to credit Dex Horthy. Each ported body opens with a one-line provenance note linking back here, matching what `dstack-mode` does for pstack. Every folded-in reference file opens the same way.

Note that upstream's `pr` skill is itself credited to Dex Horthy at Humanlayer. It was not ported, so that second attribution does not ride along.

## The known weak spot

Three of the five `studio` skills, and parts of `wayfinder`, are `in-progress` upstream: explicitly subject to change or deletion without warning. That is an argument for porting rather than depending on them, and it means upstream fixes will not arrive on their own. Re-read the upstream files by hand when something here stops working.
