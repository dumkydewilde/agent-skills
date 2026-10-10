---
name: wayfinder
description: "Chart a chunk of work too big for one agent session as a map of decision tickets on Linear, then resolve them one at a time until the way to the destination is clear. Use for /wayfinder, 'this is too big to plan in one go', 'chart a map for this', 'work the next wayfinder ticket', a docs information-architecture overhaul, a cookbook restructure, or any loose idea whose route is still fogged in."
metadata:
  credits:
    skill: wayfinder
    author: Matt Pocock
    license: MIT
    url: "https://github.com/mattpocock/skills/blob/main/skills/engineering/wayfinder/SKILL.md"
---

# Wayfinder

Ported from [mattpocock/skills](https://github.com/mattpocock/skills), MIT. The [upstream notes](https://github.com/dumkydewilde/agent-skills/blob/main/docs/mattpocock/UPSTREAM.md) explain what changed, including the swap from a configurable tracker to Linear.

A loose idea has arrived, too big for one agent session, and wrapped in fog: the way from here to the **destination** is not visible yet. Wayfinding is about finding that way, not charging at the destination. This skill charts the way as a **shared map** on Linear, then works its **decision tickets**, questions whose resolution is a decision rather than slices of a build to execute, one at a time until the route is clear.

The destination varies per effort, and naming it is the first act of charting: it shapes every ticket. It might be a spec to hand off and iterate on, a decision to lock before planning starts, or a change made in place like a schema migration. The map is domain-agnostic: engineering work, a docs restructure, a talk, whatever fits the shape.

## When this is the wrong tool

Wayfinder is the heaviest thing in this repo. Ceremony scales with the task, and that rule outranks this skill. Use `dstack-mode`'s `multi-phase-plan` playbook when the work spans phases but still fits in one head. Reach for wayfinder only when charting the route is itself the work.

## Plan, do not do

Wayfinder is **planning** by default: each ticket resolves a decision, and the map is done when the way is clear, with nothing left to decide before someone goes and does the thing. The pull to just do the work is usually the signal you have reached the edge of the map and it is time to hand off. An effort can override this in its **Notes**, carrying execution into the map itself, but absent that, produce decisions, not deliverables.

## Refer by name

Every map and ticket is a Linear issue, so it has a **name**: its title. In everything the human reads, narration and the map's Decisions-so-far alike, refer to it by that name, never by a bare id or slug. A wall of `DOC-42, DOC-43, DOC-44` is illegible. Names read at a glance. The id and URL do not vanish; a name wraps its link, but they ride inside the name, never stand in for it.

## The tracker

Linear is the tracker. Reach it through the Linear MCP when it is connected, otherwise the **linear-cli** skill. If neither is available, fall back to a local markdown tracker: one file per ticket under `docs/wayfinder/<map-slug>/`, with blocking edges written as text in each file, and say in the reply that you fell back.

Linear specifics this skill relies on:

- **The map** is an issue labelled `wayfinder:map`.
- **Tickets** are sub-issues of the map, each labelled with exactly one `wayfinder:<type>`.
- **Blocking** uses Linear's native blocked-by relation, not a body convention. This matters because it renders the frontier visually in Linear's own UI, so the human sees what is takeable without opening the map.
- **The frontier** is a filter: open sub-issues of the map, unassigned, with no open blockers.

Create the `wayfinder:*` labels on first use if they do not exist.

## The map

The map is a single Linear issue, the canonical artifact. It is an **index**, not a store. It lists the decisions made and points at the tickets that hold their detail. A decision lives in exactly one place, its ticket, so the map never restates it, only gists it and links.

### The map body

The whole map at low resolution, loaded once per session. Open tickets are not listed: they are open sub-issues, found by query.

```markdown
## Destination

<what reaching the end of this map looks like: the spec, decision, or change this effort is finding its way to. One or two lines; every session orients to it before choosing a ticket.>

## Notes

<domain; skills every session should consult; standing preferences for this effort>

## Decisions so far

<!-- the index: one line per closed ticket, enough to judge relevance, then follow the link for the detail the ticket holds -->

- [<closed ticket title>](link): <one-line gist of the answer>

## Not yet specified

<!-- see "Fog of war": in-scope fog you cannot ticket yet; graduates as the frontier advances -->

## Out of scope

<!-- see "Out of scope": work ruled beyond the destination; closed, never graduates -->
```

### Tickets

Each ticket is a sub-issue of the map. Its body is the question, sized to one agent session:

```markdown
## Question

<the decision or investigation this ticket resolves>
```

A session **claims** a ticket by assigning it to the person driving the map, first, before any work, so concurrent sessions skip it. That assignee is the claim: an open, unassigned ticket is unclaimed. Conductor makes parallel sessions cheap, so expect other sessions to be editing Linear while you work.

A ticket is **unblocked** when every ticket blocking it is closed. The **frontier** is the open, unblocked, unclaimed sub-issues: the edge of the known.

The answer is not part of the body. It is recorded on resolution. Assets created while resolving a ticket are linked from the issue, not pasted in.

## Ticket types

Every ticket is either **HITL**, worked with a human who speaks for themselves, or **AFK**, driven by the agent alone. A HITL ticket only resolves through that live exchange. The agent never stands in for the human's side of it. A grilling agent that answers its own questions has broken this.

- **Research** (AFK), label `wayfinder:research`. Reading documentation, third-party APIs, or internal knowledge bases to surface a fact a decision waits on. Resolve with the **why** skill for decisions already made inside this org, or a background `Explore` subagent against primary sources for anything external. Capture findings as a cited markdown file and link it from the ticket. Use when the fact lives outside the working directory.
- **Prototype** (HITL), label `wayfinder:prototype`. Raise the fidelity of the discussion by making a cheap, rough, concrete artifact to react to: an outline, a stub, a chart, a Dive, a throwaway script. Run `dstack-mode`'s `playbooks/prototype.md`. Link the prototype as an asset. Use when "how should it look" or "how should it behave" is the key question. This is also the escape hatch when a supposed decision turns out to be a fact: probe it instead of asking.
- **Grilling** (HITL), label `wayfinder:grilling`. Conversation. The default case. Run the **grilling** skill. Where the exchange settles terminology, write it into the project glossary as you go, per the **technical-writing** skill's glossary reference. Where it settles something hard to reverse, offer an ADR per the **architect** skill's ADR reference.
- **Task** (HITL or AFK), label `wayfinder:task`. Manual work that must happen before a decision can be made: nothing to decide, prototype, or research, but the discussion is blocked until it is done. Signing up for a service so its API can be judged, provisioning access, moving data so its shape can be seen. This is the one type that does rather than decides, and it earns its place by unblocking a decision, not by delivering the destination. The agent drives it alone where it can; otherwise it hands the human a precise checklist, and the **wizard** skill in the `tools` plugin turns that checklist into a script worth running twice. Resolved when the work is done. The answer records what was done and any resulting facts, such as credential locations, new URLs, or row counts, that later tickets depend on.

`wayfinder:` labels are the only labels a map and its tickets carry. These are decisions, not implementation work, so no triage or ready-for-agent label belongs on them.

## Fog of war

The map is deliberately incomplete. Do not chart what you cannot yet see. Beyond the live tickets lies the **fog of war**: the dim view of decisions and investigations you can tell are coming but cannot yet pin down, because they hang on questions still open. Resolving a ticket clears the fog ahead of it, graduating whatever is now specifiable into fresh tickets, one at a time, until the way to the destination is clear and no tickets remain.

The map's **Not yet specified** section is where that dim view is written down: the suspected question, the area to revisit later. It is the undiscovered frontier toward the destination. Everything here is in scope, just not sharp enough to ticket. Write as loosely or as fully as the view allows. It doubles as a signpost for collaborators reading where the effort is headed.

**Fog or ticket?** The test is whether you can state the question precisely now, not whether you can answer it now.

- **Ticket** when the question is already sharp, even if it is blocked and you cannot act on it yet.
- **Not yet specified** when you cannot yet phrase it that sharply. Do not pre-slice the fog into ticket-sized pieces: it is coarser than a ticket, and one patch may graduate into several tickets, or none, once the frontier reaches it.

**Not yet specified** excludes what is already decided, what is already a live ticket, and what is out of scope.

## Out of scope

Fog only ever gathers toward the destination. The destination fixes the scope, so work beyond it is **out of scope**: it is not fog, and it does not belong in **Not yet specified**. It gets its own **Out of scope** section on the map: work you have consciously ruled out of this effort. Scope, not sharpness, lands it here.

Out-of-scope work never graduates, so it returns only if the destination is redrawn, and then as a fresh effort, not a resumption.

Ruling something out of scope is a scoping act, not a step on the route. When a ticket that already exists turns out to sit past the destination, mis-scoped in while charting or exposed by a resolution, **close it**, since a closed ticket is unambiguously off the frontier, and leave one line in the **Out of scope** section: the gist plus why it is out, linking the closed ticket. It stays out of **Decisions so far**, which records the route actually walked. A scope boundary is not a step on it.

## Invocation

Two modes. Either way, **never resolve more than one ticket per session**, with the exception of research tickets.

### Chart the map

The user invokes with a loose idea.

1. **Name the destination.** Run the **grilling** skill to pin down what this map is finding its way to: the spec, decision, or change. The destination fixes the scope, so it is settled first.
2. **Map the frontier.** Grill again, breadth-first this time: fan out across the whole space rather than deep on any one thread, surfacing the open decisions and the first steps takeable now. **If this surfaces no fog**, meaning the way to the destination is already clear and the whole journey fits one session, you do not need a map. Stop, say so, and point at `multi-phase-plan` instead.
3. **Create the map** labelled `wayfinder:map`, with Destination and Notes filled in, Decisions-so-far empty, and the fog sketched into **Not yet specified**.
4. **Create the tickets you can specify now** as sub-issues, then wire blocking edges in a second pass, because issues need ids before they can reference each other. Write cross-references in that pass too, with real ids. Wiring sorts them into the frontier and the blocked. Everything you cannot yet specify stays in the fog.
5. **Fire the research subagents.** For each `wayfinder:research` ticket you just created, spin up a background subagent to resolve it in parallel, capturing its findings on a throwaway `research/<name>` branch with a link from the ticket. Push the branch but open no pull request: it is never merged.
6. Stop. Charting is one session's work. It hand-resolves nothing.

### Work through the map

The user invokes with a map URL or id. A ticket is optional: without one, you pick the next decision, not the user.

1. Load the **map**: the low-res view, not every ticket body.
2. Choose the ticket. If the user named one, use it. Otherwise take the first frontier ticket in order. **Claim it**: assign it to yourself before any work.
3. Resolve it as the type its `wayfinder:<type>` label names. Read the label, not just the body. The body never states the type. **Zoom as needed**: fetch the full body of any related or closed ticket on demand, and run whichever skills the `## Notes` block names. If in doubt, run the **grilling** skill.
4. Record the resolution: post the answer as a resolution comment, close the issue, and append a one-line gist plus link to the map's Decisions-so-far.
5. Add newly-surfaced tickets, create then wire. Graduate any fog the answer has made specifiable, clearing each graduated patch from **Not yet specified** so it lives only as its new ticket. If the answer reveals that a ticket sits beyond the destination, rule it out of scope rather than resolving it on the route. If the decision invalidates other parts of the map, update or delete those tickets.
