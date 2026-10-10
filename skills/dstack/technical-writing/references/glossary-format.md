# Glossary format

Adapted from the `domain-modeling` skill in [mattpocock/skills](https://github.com/mattpocock/skills/blob/main/skills/engineering/domain-modeling/GLOSSARY-FORMAT.md) by Matt Pocock, MIT. The multi-context `GLOSSARY-MAP.md` layout was dropped; see the [upstream notes](https://github.com/dumkydewilde/agent-skills/blob/main/docs/mattpocock/UPSTREAM.md).

Checklist item 6 asks whether each thing has exactly one name across the docs. A `GLOSSARY.md` is how that stays true once more than one person writes.

One file at the repo root. Create it lazily, when the first term is actually contested.

## Structure

```md
# {Project name}

{One or two sentences on what this project is and why it exists.}

## Language

**Duckling**:
A unit of compute that executes queries for one user session.
_Avoid_: instance, node, worker

**Share**:
A read-only, point-in-time copy of a database published to other accounts.
_Avoid_: snapshot, export, replica
```

## Rules

- **Be opinionated.** When several words exist for one concept, pick the best and list the rest under `_Avoid_`. A glossary that records both names has recorded the problem, not the decision.
- **Keep definitions tight.** One or two sentences. Define what it is, not what it does.
- **Only terms specific to this project.** General concepts (timeouts, retries, caching) do not belong even if the project uses them heavily. Before adding a term, ask whether it is unique to this context or just programming. Only the former belongs.
- **No implementation detail.** The glossary is not a spec, a scratchpad, or a home for design decisions. Those go in an ADR, per the `architect` skill's ADR reference.
- **Group under subheadings** when natural clusters emerge. A flat list is fine when the terms cohere.

## Maintaining it during a session

This is the active half, and it is where the value is. Merely reading the glossary for vocabulary is a one-line habit any skill can do.

- **Challenge against the glossary.** When someone uses a term that conflicts with what is written, call it out immediately. "The glossary defines a share as read-only, but you are describing writes. Which is it?"
- **Sharpen fuzzy language.** When a term is vague or overloaded, propose a precise canonical one. "You said account. Do you mean the organization or the user? Those are different things."
- **Stress-test with scenarios.** When relationships are being discussed, invent concrete edge cases that force precision about where one concept ends and the next begins.
- **Cross-reference with code.** When someone states how something works, check whether the code agrees. Surface contradictions rather than writing down the claim.
- **Write it down inline.** When a term is resolved, update the file right there. Do not batch. A term agreed and not recorded will be re-litigated.
