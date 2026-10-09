---
name: dehistorize
description: "Strip leaked edit history from an existing artifact: v2 names, 'now supports' docs, '(was X)' UI copy, comments that describe the change instead of the code. Use for /dehistorize, 'remove the history leakage', 'this doc reads like a changelog', 'scrub the edit history from this', or when interrogate or unslop flags history leakage and the fix is more than one line."
---

# Dehistorize

Remediation pass for the **Keep History Out of the Artifact** principle ([`../principles/references/keep-history-out-of-the-artifact.md`](../principles/references/keep-history-out-of-the-artifact.md)). The principle stops you from writing leaks; this skill removes them from an artifact that already shipped with them. Read the principle leaf first. It defines what counts as a leak and gives the test: would a from-scratch implementer with the current requirements write this line?

Finding leaks is the easy half. The failure mode of an unguided cleanup is overdeletion. A baseline run on a seeded fixture caught every leak, then deleted the changelog ("that's git's job") and the migration guide ("pure migration history"). Both exist to carry the delta. Most of this skill is about what to keep.

## Process

1. Seed scan. Case-insensitive grep over the artifact for the common markers: `previously`, `changed from`, `no longer`, `now `, `(was`, `legacy`, `deprecated`, `updated`, `improved`, `new`, `old`, `_v2` and `V2`/`V3` suffixes. The list is a starting point full of false positives ("now" in "know", a genuinely new feature announcement). Judgment decides, the grep only points.
2. Judgment pass. Read the artifact end to end once. Leaks the grep cannot see: docs whose structure mirrors the order changes landed in rather than how a new reader needs them, tests named for the change that introduced them, config keys and schema columns that encode revision order.
3. Classify every hit as one of three things before touching it: a leak, a delta surface, or a feature. Only leaks get rewritten.
4. Rewrite leaks as if the current version is the only version that ever existed. Renames update every call site in the same pass.
5. Verify and report.

## What to keep

**Delta surfaces.** Changelogs, release notes, migration and upgrade guides, audit logs, ADRs, versioned API docs. Their content IS the before/after; deleting one removes information its readers rely on, which is data loss, not cleanup. "Git already has the history" is not a reason. The surface exists for readers who do not read git. Inside a delta surface, leave the deltas alone.

**Features that compare data over time.** "Score: 50 (was 35)" is a leak when "was 35" refers to what the previous version of the code computed, and a feature when it refers to what this lead scored last week. The test: does the comparison run over the artifact's own revisions, or over the data at runtime? If removing the line would change behavior a user may depend on, do not decide silently. Flag it, name both readings, and let the requirement owner call it. The baseline run got this case right but resolved it on its own; the flag is the part that does not happen without this rule.

**Rationale with no other home.** A comment like "weighted sum, linear scaling undercounted demo requests" leaks the change but also holds the only record of why. Do not delete the knowledge with the leak. Rewrite the artifact copy to present tense ("demo requests dominate the score by design") and move the before/after story to where deltas belong: the cleanup's commit message, the changelog if the project keeps one, an ADR if it is an architecture call.

## Renames

Rename `scoreV2`, `newCalculateScore`, or `legacy_weights` to what a from-scratch implementer would pick, usually the unsuffixed name. Update every call site, import, doc example, and test in the same change; a half-done rename is worse than the leak. If the name is part of a published API with consumers outside the repo, do not break them for cosmetics: add the clean name, alias the old one, and flag the break for the owner to schedule.

## Verify and report

- Run the project's tests, or its verification skill if it has one.
- Re-run the seed scan. Every remaining hit is either inside a delta surface or gets one line of justification in your reply.
- Reply with three lists: leaks removed, delta surfaces and features kept, judgment calls that need an owner's decision. The before/after of the cleanup itself goes in the commit message, not the artifact.
