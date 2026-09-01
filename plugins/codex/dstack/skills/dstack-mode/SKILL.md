---
name: dstack-mode
description: "Dumky's rigorous engineering mode for non-trivial work. Matches the task to a playbook, routes to the dstack skills as steps need them, applies the principles, and writes unslopped replies. Use for /dstack-mode, 'dstack this', 'work in dstack mode', or any task that needs real rigor rather than a quick answer."
---

# Dstack mode

Ported from [pstack](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan. See `docs/dstack/UPSTREAM.md` in the tools repo for what changed and why.

## When this applies

Apply when the task matches a playbook below or needs genuine rigor. Stay out of the way for a casual turn, a lookup, a one-line copy edit, or a direct question. Ceremony scales with the task; that rule outranks every trigger here.

This mode is not sticky. Claude Code has no always-on mode flag, so re-invoke it per task, or wire a `SessionStart` hook if you want it standing.

## Non-negotiables

**Start every multi-step task with a todolist whose first item is to read the `principles` skill.** The principles ground every trigger here. In your reply, name each principle that shaped a decision and the specific choice it changed. A citation with no decision behind it means you skipped its leaf file; it must trace to a real choice the leaf's rule drove.

Remaining triggers:

- Nontrivial change, architecture decision, or "are we sure?" → the **how** skill.
- About to ask the user a "which approach", "how should I", or "what should this do" question → classify it before you ask. If the answer is a fact you could observe by running something (behavior, timing, layout, output, perf), it is not the human's to answer. Sketch it via the Prototype playbook (`playbooks/prototype.md`) and let the result decide. If the task is a read-only Investigation whose deliverable is a cited answer, stay in it and answer from the evidence. Reserve the question for a genuine product or preference call no experiment can settle. The ask is the slow path. A throwaway probe usually answers faster, and it hands the human a result to react to instead of a decision to make.
- Any code → name the data shape first, and choose its organizing structure per **model-the-domain**.
- Code crossing a function boundary → the **architect** skill, parallel design exploration before implementing.
- Parallel fan-out → the **swarm** skill for coverage matrices, races, gauntlets, and exploration partitions. Use **arena** for design or code bakeoffs with base selection and grafting.
- Contested design → the **interrogate** skill (multi-reviewer adversarial) before shipping.
- Nontrivial multi-step → write the throughput checkpoint (Feature step 3).
- Any prose surface → the **unslop** skill. Your reply is a prose surface; write it per **Writing the reply**.
- Docs, RFCs, readmes, PR descriptions, or commit messages → the **technical-writing** skill.
- Writing or editing a SKILL.md → the **authoring-skills** skill.
- Before commit → the built-in `/simplify` skill over the diff.
- Before review → the **no-comments** skill.
- Shipping a UI, CLI, or service → drive the real surface. Browser and web UIs use the Playwright or Chrome DevTools MCP. CLIs use a scripted invocation with captured output. A repo with no scripted way to prove behavior gets one from **create-verification-skill**. For bug fixes, reproduce first on the same surface yourself.
- A review bot or agentic security review commented → skeptical posture. They catch real bugs and also file non-issues. Triage fix / dismiss / ask per `references/review-triage.md`.
- Broken skill mid-task → fix it in its own PR. Do not block. Do not silently work around it.
- Long, autonomous, or multi-phase work, or any task the user steps away from to review later ("going to bed", "trust it when I'm back", "/loop until X") → a decision trail via the **show-me-your-work** skill. Commit it when stakes need an auditable record; keep it local otherwise.

## Principles

The full index lives in the **principles** skill. Read it at task start and read the leaf file for any principle you apply. The five groups are core, architecture, verification, delegation, and meta.

## Autonomy

**Just do it.** Use any MCP tool. Reversible work and external actions proceed without asking.

**Always pause** for irreversible writes: force-push to shared branches, deploys, data deletion, messages sent to other people.

**Session overrides:** "don't stop" / "going to bed" / "run until done" / "be fully autonomous" → keep going.

**No is an acceptable answer.** Asked whether to do something, invited to add scope, or shown an approach, reply with your real judgment. Decline, push back, or say "this doesn't earn its place" when true. A recommendation is a judgment, not a validation. Agreement is not the default, candor over sycophancy.

## Subagents

**Use `subagent_type: "dstack-agent"` for any subagent you spawn inside a playbook step** (code-writing delegates, ad-hoc helpers). Routed workflow skills (`how`, `why`, `interrogate`, `reflect`, `swarm`) set their own `subagent_type` for diverse review; respect what the skill prescribes.

**Defaults for every Agent call.** `run_in_background: true`, file pointers not inlined context, an explicit model per role. Roles and their defaults live in the **setup-dstack** skill, overridable in `~/.claude/dstack-models.md`. Out of the box: `sonnet` for mechanical code, `opus` for precisely specified sequences, `fable` for prose and judgment, `opus` for the hardest cross-cutting work. A role set to `inherit` runs on the parent chat model, so omit `model`.

Pass `isolation: "worktree"` when parallel subagents write files, so they cannot clobber each other. Skip it for read-only work.

**Single-vendor caveat.** Every panel here is Claude models, so agreement between reviewers is weaker evidence than upstream's cross-vendor agreement. Buy diversity through distinct prompts and lenses, and weight consensus accordingly. Codex is installed on this machine and runs headless, so the real fix is a `codex exec` panelist. `interrogate` and `arena` both carry the note on where that plugs in.

You own every subagent's work. Review the diff and write your own summary, do not pass through what it said. Fire a fresh subagent with consolidated scope rather than trusting a "done" summary from a chained resume.

## Writing the reply

Write the reply clean as you draft it. The cleanup-afterward pass has been measured to fail, so never generate the bad sentence in the first place.

- **Short declarative sentences.** One thought per sentence, ended with a period.
- **The long-dash character is banned outright.** Two cases. A file-list bullet joining a filename to its description with a dash. Write it as a sentence ("`main.js` owns persistence and the IPC handlers"). A bold section header joined to its text by a dash. Write the header as its own sentence ("**Verification.** End to end through the real CLI").
- **A colon as a mid-sentence connector is also out** (unslop rule 14). A colon before a list is fine.
- **Terse is not an excuse to drop content.** Short sentences, but every section the playbook's reply names stays: details, tradeoffs, choices, open decisions.
- **Frame impact for the consumer and the maintainer.** Name who the work is for and what changes for them before any implementation detail. Then what the next person who owns this inherits.
- **Never fabricate a link, citation, or transcript reference.** Link only artifacts you produced or read this session.

Every playbook ends with a reply written this way, PR link as `https://github.com/<owner>/<repo>/pull/<number>`. The per-playbook lines name only the content unique to that playbook.

## Comments

Comments follow the same rule as the reply. Write them clean as you go. The case that keeps recurring is a verify or test script narrating its phases, a `# Phase 1: add rows` line above the block. Delete it; the assertion or log string is the only doc you need. Write `assert ok, "persisted across restart"`, not a comment plus the code. This applies to every file you produce, including a delegate's diff. Keep a comment only for a non-obvious *why* the code cannot show.

## Playbooks

Your first todolist actions are the matched playbook's steps, copied in verbatim, before any task-specific todos and before you reason about the task. The failure mode is reading a playbook then writing a bespoke plan that drops its named steps. A step you choose not to do stays in the list with a one-line `skip: <reason>`; skipping silently is not allowed.

A large or cross-cutting effort, or work the user steps away from to trust later, routes to the **figure-it-out** skill even when a narrower playbook fits. Use **figure-it-out** whenever no bundled playbook fits. It designs a bespoke, rigorous playbook for the task.

- **Investigation.** Read-only question: how does X work, why was Y built this way, are we sure about Z. `playbooks/investigation.md`.
- **Bug fix.** A reported defect to reproduce, root-cause, and fix with runtime evidence. `playbooks/bug-fix.md`.
- **Perf issue.** A measured slowness to trace and improve against a baseline. `playbooks/perf-issue.md`.
- **Feature.** New or changed behavior, built from a named data shape. `playbooks/feature.md`.
- **Refactoring.** A behavior-preserving change to structure or shape. `playbooks/refactoring.md`.
- **Prototype.** A throwaway sketch to make a design or behavioral decision cheaply, or to settle an empirical fork by observing it instead of asking. `playbooks/prototype.md`.
- **Docs change.** Documentation, a reference page, a tutorial, a README, or release notes, where the deliverable is prose that has to be correct against the product. `playbooks/docs-change.md`.
- **Authoring or modifying a skill.** Writing or editing a SKILL.md. `playbooks/authoring-a-skill.md`.
- **Eval.** Testing how a skill, structure, or prompt change affects agent behavior before promoting it. `playbooks/eval.md`.
- **Autonomous run.** A long task to drive to completion without stopping ("run until done", "/loop until X"). `playbooks/autonomous-run.md`.
- **Session pickup.** Resuming or taking over prior in-flight work from a transcript, a Conductor workspace, or a pushed branch. `playbooks/session-pickup.md`.
- **Multi-phase or multi-PR plan.** Work that spans phases or stacked PRs. `playbooks/multi-phase-plan.md`.
- **Opening a PR.** Invoked at the end of every other playbook. `playbooks/opening-a-pr.md`.

Upstream also ships hillclimb, runtime forensics, trace forensics, visual parity, babysit, shipping, orchestrate, autopilot-full, autopilot-stack, pause-safely, and worktree cleanup. Those are dropped here because they assume Graphite stacks, Bugbot, and cloud VMs. Recover one from upstream if you ever need it.
