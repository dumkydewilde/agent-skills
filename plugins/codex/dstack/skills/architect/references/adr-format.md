# ADR format

Adapted from the `domain-modeling` skill in [mattpocock/skills](https://github.com/mattpocock/skills/blob/main/skills/engineering/domain-modeling/ADR-FORMAT.md) by Matt Pocock, MIT. The multi-context glossary machinery around it was dropped; see the [upstream notes](https://github.com/dumkydewilde/agent-skills/blob/main/docs/mattpocock/UPSTREAM.md).

An **architecture decision record** captures that a decision was made and why. ADRs live in `docs/adr/` with sequential numbering: `0001-slug.md`, `0002-slug.md`. Create the directory lazily, when the first ADR is needed. Scan for the highest existing number and increment.

## When to offer one

All three must be true. Miss any one and skip the ADR.

1. **Hard to reverse.** The cost of changing your mind later is meaningful. If it is easy to reverse you will just reverse it.
2. **Surprising without context.** A future reader will look at the code and wonder why on earth it was done this way. If it is not surprising, nobody will wonder.
3. **The result of a real trade-off.** There were genuine alternatives and you picked one for specific reasons. With no real alternative there is nothing to record beyond "we did the obvious thing".

This test is deliberately hard to pass. An ADR per decision is a changelog, and a changelog nobody reads.

## Template

```md
# {Short title of the decision}

{One to three sentences: what the context was, what was decided, and why.}
```

That is it. An ADR can be a single paragraph. The value is in recording that a decision was made and why, not in filling out sections.

Optional sections, only when they add genuine value, which most will not need:

- **Status** frontmatter (`proposed`, `accepted`, `deprecated`, `superseded by ADR-NNNN`). Useful when decisions get revisited.
- **Considered options.** Only when the rejected alternatives are worth remembering.
- **Consequences.** Only when non-obvious downstream effects need calling out.

## What qualifies

- **Architectural shape.** "Ingest lands in DuckLake, serving tables are native MotherDuck."
- **Integration patterns between components.** "The pipeline publishes shares, consumers never query the source database."
- **Technology choices that carry lock-in.** Database, orchestrator, auth provider, deployment target. Not every library, just the ones that would take a quarter to swap out.
- **Boundary and scope decisions.** Who owns which data, and what the explicit no-s are. The no-s are as valuable as the yes-s.
- **Deliberate deviations from the obvious path.** "Hand-written SQL instead of the ORM, because X." Anything where a reasonable reader would assume the opposite. These stop the next person from "fixing" something that was deliberate.
- **Constraints not visible in the code.** Compliance rules, a partner API's latency contract, a cost ceiling.
- **Rejected alternatives when the rejection is non-obvious.** Otherwise someone suggests the same thing again in six months.

## Where this fires

`architect` Phase C is the natural moment: the synthesized design package is the trade-off, already written down. Lift the decision out of the rationale and into an ADR when it passes the three-part test. The rationale template holds the full reasoning; the ADR holds the one paragraph a future reader needs.

Writing one is **keep-history-out-of-the-artifact** working as intended. The ADR is where the delta is allowed to live, so the code does not have to carry it.
