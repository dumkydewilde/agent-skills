# Environment audit lens

Adapted from the `retro` skill in [mattpocock/skills](https://github.com/mattpocock/skills/blob/main/skills/engineering/retro/SKILL.md) by Matt Pocock, MIT. Folded in rather than ported as its own skill, because it would have competed with `reflect` for the same trigger. See the [upstream notes](https://github.com/dumkydewilde/agent-skills/blob/main/docs/mattpocock/UPSTREAM.md).

`reflect`'s three reviewers mine the transcript for learnings that become **skill edits**. This fourth lens mines the same transcript for changes to the **environment** the agent ran in. Different output, same input, so it rides along as a fourth parallel reviewer rather than a separate pass.

Findings from this lens route to a repo change or a tracker item, never to a skill edit. They skip the Routing field in step 5 and file under Backlog.

## Prompt for the reviewer

You are auditing the environment a coding agent worked in, using the transcript at `<TRANSCRIPT_PATH>`. You are not reviewing the code and you are not suggesting skill edits. You are looking for changes to the repo and the agent's tooling that would make the next run go better.

Report findings most severe first. For each one, name the evidence in the transcript, the category, and the concrete change.

### Categories

- **Navigation.** How easy was it for the agent to find the right files? Are there hidden dependencies between files? Would a pointer in `AGENTS.md` or `CLAUDE.md` naming the right file have saved the search? Fires when the session spent a long time locating one piece of information.
- **Automated checks.** Is there a check that would have caught a mistake the agent made? Linting, typing, tests, a filesystem linter. Read the repo's own check command first, meaning its task runner entries and its CI workflow, so a check that already exists but sits unwired or silently broken is the finding rather than a reinvention. A repo with no guardrail at all, no pre-commit hook and no CI job running its lint, typecheck, or test command, is itself a finding. An unchecked repo is a standing missed opportunity, not a neutral default.
- **Coding standards.** Classify the violation first. A **mechanical** one, meaning a fixed syntactic pattern, a banned API, an import shape, or a file-location rule, gets a deterministic check, full stop: a custom lint rule, a pre-commit hook, or a CI job, whichever the repo's language and existing guardrail make cheapest. Default to building the check over writing the rule. Reserve prose standards for genuine judgement calls, meaning cross-file consistency or "matches the surrounding style", anything no guardrail could substitute for. Fires when a reviewer failed to catch a mistake.
- **Steering files.** Are there instructions in `CLAUDE.md` or `AGENTS.md` that belong in a coding standard or an automated check instead? Fires when a steering file is large, in the repo or in the user's global scope.
- **Tool economy.** Did the agent make expensive tool calls that could be streamlined? Is any custom tooling, a CLI or an MCP server, particularly token-inefficient? A tool whose every call returns thousands of tokens to answer a yes-or-no question is a finding.
- **No-ops.** Instructions in steering files that do not change the agent's behavior versus its default. The test is model-relative, not reader-relative: settle it by running the document, not by debate. When a line fails the test, delete the whole line rather than trimming words from it. Fires when steering files are large and unwieldy.
- **Information access.** Opportunities to increase the agent's access to information: teeing dev server logs to a file, read-only credentials for a third-party service, a scripted way to drive the app. Fires when a crucial piece of information was not reachable.

### Why standards belong to review, not implementation

All work goes through implementation and review. The implementation agent carries the most **context pressure**: it explores, writes code, and debugs failures. The review agent carries the least, since it receives a diff and needs no exploration.

So coding standards belong to the review agent. A standard pushed into the implementation agent's context competes with the work for attention and loses. Weight findings accordingly.
