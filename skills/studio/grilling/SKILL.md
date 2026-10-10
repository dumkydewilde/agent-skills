---
name: grilling
description: "Interview the user in rounds until a plan, decision, or idea is fully settled. Use for /grilling, 'grill me', 'grill me on this', 'stress-test my thinking', 'interview me about this', 'poke holes in my plan', or any call where the user holds the answer and no experiment can settle it."
metadata:
  credits:
    skill: grilling
    author: Matt Pocock
    license: MIT
    url: "https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md"
---

# Grilling

Ported from [mattpocock/skills](https://github.com/mattpocock/skills), MIT. The [upstream notes](https://github.com/dumkydewilde/agent-skills/blob/main/docs/mattpocock/UPSTREAM.md) explain what changed.

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

## This is the one place dstack asks

The **never-block-on-the-human** principle says proceed on reversible work instead of asking. `dstack-mode` sharpens it: if a probe could answer the question, probe. Both are about **facts**. Grilling is about **decisions**, and the two never trade places.

- A fact is anything the environment can settle: behavior, timing, layout, output, performance, what a file contains. Never ask. Dispatch a subagent or run the probe.
- A decision is a preference, a product call, an editorial judgment, a scope boundary. Only the user holds it. Ask, and wait.

Misrouting a fact into a question is the failure mode this section exists to stop. Before every question, ask yourself whether you could have looked it up. If yes, go look it up.

## Rounds

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask now without guessing at answers you have not heard yet. Ask the whole frontier in one round. Number each question and give your recommended answer. Then wait for the user's answers before the next round.

Format a round like this:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Word each question so "yes" accepts your recommended answer. That makes agreement cheap and disagreement specific.

Each round of answers reshapes the tree. Settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a later round, not this one.

## Facts are your job

When a frontier question needs a fact from the environment, dispatch a subagent to find it. Do not block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the subagent to report. Ask the rest of the frontier now.

Use `subagent_type: "Explore"` for read-only lookups and `run_in_background: true`, per **guard-the-context-window**.

## Done

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms you have reached a shared understanding.

A recommended answer is a judgment, not a validation. Where you think the user is wrong, say so in the recommendation rather than offering a neutral menu.
