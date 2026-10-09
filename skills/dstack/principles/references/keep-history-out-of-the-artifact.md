# Keep History Out of the Artifact

*Apply when modifying anything with an audience beyond this conversation: UI copy, names, docs, comments, reports, tests. The artifact describes only its current state; the before/after story goes in the commit, PR, or reply, never in the artifact.*

A change has two audiences. The requester cares about the delta: what moved, from what, to what. The artifact's audience was never part of the conversation; to them the previous version does not exist. When the delta leaks into the artifact, process knowledge the product was supposed to hide becomes product behavior. A lead-scoring app that shows "new score: 50 (was 35)" after a scoring tweak is exposing its own development history to users who only ever needed "score: 50".

What leakage looks like:

- UI copy that narrates the edit: "new score: 50 (was 35)", "updated dashboard", "improved algorithm"
- Names that encode revision order: `scoreV2`, `newCalculateScore`, `legacy_weights`
- Comments that describe the change instead of the code: "changed from linear scaling", "now uses weighted sum"
- Docs written as deltas: "the score is now calculated as..." reads as a changelog entry; "now" means nothing to a first-time reader
- Tests named for the change: `test_new_scoring` is meaningless once the change is a month old

The test: would a competent implementer, handed only the current requirements and no knowledge of the previous version, write this line? If not, it is leaked history. Rewrite as if the current version is the only version that ever existed.

The delta still gets reported, in full, where deltas belong: the commit message, the PR description, the reply to the user, the changelog if the project keeps one. The exception runs the other way too. A surface whose job is the delta (a changelog, release notes, a migration guide, an audit log) keeps its before/after; deleting one is data loss, not cleanup.

For an artifact that already shipped with leaked history, the **dehistorize** skill ([`../../dehistorize/SKILL.md`](../../dehistorize/SKILL.md)) runs the remediation pass: find, classify, rewrite, verify.

**Redesign from First Principles** is the design-level sibling: don't bolt the new requirement onto the old shape. This principle is the content level: even a well-integrated design can leak history through copy, names, comments, and docs.
