### Multi-phase or multi-PR plan

**You own the plan, not the code. The plan is a checklist an owner runs box by box and a reviewer audits from the evidence.** For work that spans phases or stacked PRs. The plan is the deliverable. Do not implement.

1. When the change is one or two files with an obvious approach, skip the plan. Say so and stop.
2. Settle open questions by prototype before you write. For a question about layout, timing, behavior, or whether an API works, run `playbooks/prototype.md`. Keep the branch, the SHA, and the artifacts for Appendix A. Ask the user only about a product or preference call no run can settle. Give options (the **never-block-on-the-human** principle).
3. Explore in subagents with `subagent_type: "dstack-agent"` and an explicit model per the Subagents section (the **guard-the-context-window** principle). Each returns file pointers, conventions, test commands, and entry points. No inlined dumps.
4. Copy the skeleton below into the plan file and fill every placeholder. Write it under the repo's own convention. This repo uses `docs/plans/<YYYY-MM-DD>-<slug>.md`. Keep every heading and sub-block in the order shown. One section per PR. One PR is one change with its own evidence (the **sequence-verifiable-units** principle).
5. Write under `/technical-writing` in full, then `/unslop`. The body is one Diátaxis mode, how-to. Appendices hold explanation and reference. Each heading states the task or the finding. No long dashes. No mid-sentence colons.
6. Run `uv run --no-project skills/dstack/dstack-mode/scripts/check_plan.py <plan.md>` and fix every line it prints (the **encode-lessons-in-structure** principle). It enforces the skeleton's shape, the verification rule in every verification block, and the punctuation rules.
7. Hand back. Post the plan path and the script's output, then stop. Execution starts on the user's explicit go.

**Verification.** Tests alone are not sufficient verification. A PR is verified only when its unit and live boxes are both checked (the **prove-it-works** principle). That sentence is the verification rule. Every verification block opens with it. The live block is mandatory and names how the real surface gets driven, with the artifact each lane saves and its pass predicate. A perf block is optional. Add it when the PR claims a speed or size change, and then it names the metric, the probe, the baseline measured first, and the number that fails.

**Driving the real surface.** Pick the harness by surface. Browser and web UIs use the Playwright or Chrome DevTools MCP. CLIs and TUIs use a scripted invocation with captured stdout. Data work reads the actual table or file the change writes. A repo with no scripted way to prove behavior gets one from the **create-verification-skill** skill. A surface with no harness is a risk in Appendix C, and its live block still names how each lane drives it by hand.

````markdown
# <Program> plan

<Under ten lines. What changes, for whom, the rule the program enforces, and the PR ids in order.>

## How to read this

One box is one unit of work. Every box names the evidence that checks it. A nested box is a sub-step of the box above it. Check a box only when its evidence exists, a file, a log line, an artifact, a test run, or a SHA. The body is a how-to. The appendices explain and record.

Tests alone are not sufficient verification. A PR is verified only when its unit and live boxes are both checked.

## Program checklist

### Arm the program

- [ ] State the plan to the user, then stop. Start execution only on an explicit go.
- [ ] Read these from trunk at program start, and again whenever the run resumes.
  - [ ] `git show origin/main:skills/dstack/dstack-mode/playbooks/opening-a-pr.md`
  - [ ] `git show origin/main:skills/dstack/<each other skill the program uses>/SKILL.md`
- [ ] Name the wake mechanism for unattended stretches, per `playbooks/autonomous-run.md`. Never leave the cadence to memory.
- [ ] Keep a decision trail per the **show-me-your-work** skill when the user reviews this after stepping away.

### Order the work

- [ ] Follow this dependency graph. Start dependent work only after its parent merges, or base it on the parent branch when stacking.
  - [ ] <PR id> and <PR id> are independent and first. Both branch from `main`.
  - [ ] <PR id> after <PR id>.
- [ ] Hold the file boundaries. <PR id or class> touches only `<glob>`.
- [ ] Hold the review gate. <PR ids> change behavior a person sees. They wait for the user's review before merge.

### PR mechanics, for every PR

- [ ] Open the PR ready, never draft, with `gh pr create`.
- [ ] Run the repo's lint, typecheck, and tests once before the PR-facing push.
- [ ] Run `/simplify` before each commit and `/no-comments` before review.
- [ ] Triage every review comment on its merits per `../references/review-triage.md`.
- [ ] Rebase onto current trunk before the merge-ready report.

### Verdict and merge, for every PR

- [ ] At the merge-ready head SHA, verify per the PR's **Verify, unit** and **Verify, live** blocks. Add an audit pass that reads the diff and the receipts and distrusts the PR body.
- [ ] Clean only when every check passes. Findings go back to the owner. A new head gets a fresh verdict.
- [ ] <The merge rule. Who clicks it and after which gate.>

## <Task as a verb phrase> (<PR id>)

**Depends on.** <PR id, or None.>

**Files.**

- [ ] Edit `<path>`.
- [ ] Create `<path>`.
- [ ] Delete `<path>`.

**Build.**

- [ ] <One change. Name the symbol and the file.>

**You see.**

- [ ] <One observable result, with the exact log line or screen state.>

**Verify, unit.** Tests alone are not sufficient verification. A PR is verified only when its unit and live boxes are both checked.

- [ ] <Test file and the case it gains.> Run `<command>`.

**Verify, live.** Tests alone are not sufficient verification. A PR is verified only when its unit and live boxes are both checked. Drive the real surface through <harness>.

- [ ] Lane 1. <Scenario.> Save `<artifact>`. Pass when <predicate>.
- [ ] Lane 2. <Scenario.> Save `<artifact>`. Pass when <predicate>.

**Review gate.** <The user reviews before merge, or `None. <PR id> is not review-gated.`>

- [ ] Post the artifacts from the live lanes. Stop at merge-ready and wait.

**Merge.**

- [ ] Clean verdict at the exact head SHA.
- [ ] Review-comment triage done.
- [ ] Rebased onto current trunk after the verdict.
- [ ] <Who merges.>

## Close the program

- [ ] Every box above is checked with its evidence.
- [ ] Reply with the report, naming what shipped and what stayed open.

## Appendix A. Prototype evidence

<Each open question a prototype answered, with the branch, the SHA, and the artifact links. Each question that stays unproven.>

## Appendix B. Alternatives rejected

<Each approach weighed and why it lost.>

## Appendix C. Risks

<Each risk with the PR it lands in and what the owner watches.>

## Appendix D. Links and reading list

<Docs to read before editing. Which PRs get the **how** skill and which get **interrogate**. The trail per the **show-me-your-work** skill.>
````

**Reply:** the plan path, the PR ids with their dependencies and the review-gated set, what the prototypes proved and what stays unproven, and the check script's output.
