# Review-comment triage

Use this reference when a review bot, an agentic security review, or `/code-review` leaves comments on a PR. The goal is not to ignore them by default. The goal is to stop treating every comment as a required code change.

Automated reviewers catch real bugs and also file non-issues and nitpicks. Assess each on its merits and dismiss noise with a concrete reason instead of churning code.

## Decision rubric

Classify each thread before acting:

- `fix`. The comment identifies a plausible correctness, security, privacy, data loss, auth, billing, migration, idempotency, race, or shipped-behavior issue. Fix it in the lowest owning PR, then reply with the commit SHA and resolve the thread.
- `dismiss`. The comment matches a documented low-risk noisy pattern, and the current code proves the concern needs no change. Reply with a short reason and resolve the thread.
- `ask`. The comment is novel, high-severity, security or privacy or data related, or ambiguous. Ask instead of guessing.

When in doubt, ask. Skipping a noisy code-quality comment is cheap. Skipping a real data or security bug is not.

## Ask by default

Never auto-dismiss these, even when a previous PR dismissed something similar:

- Security, privacy, auth, billing, data retention, and permission-boundary findings.
- High-severity findings.
- Migration, schema, idempotency, concurrency, and cross-system behavior findings.
- Comments where the suggested fix is small and clearly reduces risk without changing product intent.

## Recurring skip candidates

### Intentional UI or design-system visual changes

- Confidence: candidate
- Skip when: the PR description, screenshots, or nearby code makes the visual change explicit, and the comment only restates that a shared visual default changed.
- Do not skip when: the comment points to accessibility, focus visibility, keyboard navigation, color contrast, or a component API contract the PR did not intentionally change.

### Usage the reviewer cannot see

- Confidence: candidate
- Skip when: an export, component, or helper is flagged as unused, and a later PR in the stack or a caller outside the diff demonstrably uses it.
- Do not skip when: the PR is standalone, the symbol is public API, or the claimed use cannot be verified.

### Temporary duplication during a parallel implementation

- Confidence: candidate
- Skip when: the PR intentionally duplicates a small amount of code to keep a new path parallel to an old path being deleted or proven out.
- Do not skip when: the duplicated code touches security, billing, data access, or API behavior.

### An existing invariant already covers the warning

- Confidence: candidate
- Skip when: the concern is already guaranteed by a shared component, framework contract, type invariant, or single source of truth visible in the diff or nearby code.
- Do not skip when: the invariant is assumed but not enforced, depends on timing, or crosses async or state boundaries where values can diverge.

### The finding is already fixed later in the same PR

- Confidence: candidate
- Skip when: the review claims a missing check, and the current PR tip clearly includes that exact gate with tests, typically added in a hardening commit after the review ran.
- Do not skip when: the cited helper is a no-op for the case under discussion, or the check runs after the side effect it guards.

### A cheaply verifiable claim, so verify before classifying

- Confidence: recurring
- Skip when: never skip the verification itself, it costs one command. When the comment claims a test or assertion no longer matches the code, run that test on the PR tip before classifying. A red run confirms the claim. A green run is a concrete disproof for the dismissal reply.
- Note: repeat-pass "probably noise" heuristics misfire here. Prose-pinning tests drift precisely because earlier fix rounds edit the prose.

### Manual reimplementations of native browser behavior

- Confidence: candidate
- Skip when: practically never. When a diff replaces native browser behavior with a manual equivalent (native sticky becomes JS-positioned clones, native scroll targeting becomes forwarded wheel and touch events, paint-order occlusion becomes masks or clip-path), logic-bug findings against that code have been consistently legitimate. Default to fix.
- Example signal: "masks do not affect hit-testing", "overlay blocks wheel scroll", "ignores deltaMode".

### Widening a deliberately narrow error condition

- Confidence: candidate
- Skip when: the finding asks to broaden a narrow error condition (a specific errno, error code, or status class) into a catch-all, and that narrowness encodes a real distinction. The canonical shape is a dependency fallback gated on `ENOENT`. "The binary is not installed" is a different situation from "the command ran and failed", and retrying on any non-zero exit would hide the true error behind the fallback's error.
- Do not skip when: the narrow condition misses a case in the same category (another "binary unusable" errno such as `EACCES`), the unhandled path loses data, or the retry is idempotent and the original error is still surfaced.

## Learned pattern format

Add future patterns in this shape:

```markdown
### <short pattern name>

- Confidence: candidate | recurring | strong
- Skip when: <conditions that must be true>
- Do not skip when: <risk boundaries>
- Example signal: <phrases or code context that identify the pattern>
- Source: <PR or comment URL, or a short historical note>
```

Use `candidate` for one or two examples. Use `recurring` after multiple real dismissals. Use `strong` only when the pattern is narrow, repeatedly verified, and low risk.
