---
name: writing-fragments
description: "Explore phase for any piece of writing: mine the user for raw fragments and append them to one markdown file, no structure yet. Use for /writing-fragments, 'help me work out what I want to say', 'mine me for material', 'I have a half-formed idea for a post', 'brain-dump this with me', or before drafting a blog post, talk, or docs page whose argument is not settled. Hand the pile to writing-shape when the exploring is done."
metadata:
  credits:
    skill: writing-fragments
    author: Matt Pocock
    license: MIT
    url: "https://github.com/mattpocock/skills/blob/main/skills/in-progress/writing-fragments/SKILL.md"
---

# Writing fragments

Ported from [mattpocock/skills](https://github.com/mattpocock/skills), MIT. The [upstream notes](https://github.com/dumkydewilde/agent-skills/blob/main/docs/mattpocock/UPSTREAM.md) explain what changed.

<what-to-do>

This is pure **explore**: widen the space of what could be written without committing to structure. Committing is **exploit**, the **writing-shape** skill's job. Run a grilling session that produces fragments, interviewing the user relentlessly about whatever they want to write about. Imposing phases, outlines, or article structure is out of scope here.

Run the **grilling** skill for the interview mechanic: rounds, a frontier, numbered questions each carrying your recommended answer. Facts are still yours to look up, never the user's to supply.

As fragments emerge from either side of the conversation, append them to a single markdown file.

If the user did not pass a path, ask once where to save the document, then remember it for the rest of the session.

Capture fragments from the very first thing the user says, including the initial prompt.

On first write, put a single H1 at the top with a working title. It can change later. Nothing else: no metadata, no table of contents, no date.

</what-to-do>

<supporting-info>

## What is a fragment

A fragment is any piece of text that might survive into the final article. It must be readable by the author, meaning the author can tell what it means. It does not need to define its terms or be comprehensible to a cold reader. The bar is "is this a piece of good writing?", not "is this a self-contained argument?"

Fragments are deliberately heterogeneous. Any of these could be one:

- A sharp sentence you would want to deploy somewhere but do not yet know where.
- A claim with a one-line justification.
- A vignette: a thing that happened, a code snippet, a query, a scenario, an analogy.
- A half-thought: "something about how X feels like Y, work this out later."
- A quote, a piece of dialogue, an overheard line.
- A list of related observations that hang together by feel.
- A complaint, a confession, a punchline.
- A **leading word**: a compact metaphor or coinage the whole piece can hang on, one term that names the idea the way _tracer bullets_ or _fog of war_ names a whole pattern.

Of these, the leading word is the most valuable fragment to land. It is the one that pays through the entire exploit phase, shaping the structure, the transitions, and the title. When the conversation circles a recurring idea, push to coin a word for it.

The novelist's diary is the model: years of unstructured noticings that later get mined for raw material. Fragments are noticings.

## Do not unslop the pile

The **unslop** and **technical-writing** skills are exploit-phase tools. They belong in **writing-shape** and after, never here. A fragment that gets polished before it is placed is a fragment that stops being raw material and starts being a commitment. Capture the user's actual phrasing, including the rough bits.

## File format

```markdown
# Working title

A first fragment lives here.

It can be multiple paragraphs. It can include lists, code, quotes: whatever
shape the fragment naturally takes.

---

A second fragment.

---

> A quoted line that the user wants to keep around.

A reaction to it.

---

- A cluster of related observations
- That hang together by feel
- And want to be near each other
```

Fragments are separated by a horizontal rule. No headings inside the body. No tags. No order beyond the order they were added.

## Writing rhythm

Append silently. Do not ask permission for each fragment. Mention what you added in passing ("adding that"), but do not interrupt the conversation with save dialogs.

Before every write, re-read the file from disk. The user may have edited, reordered, or deleted fragments between turns, so preserve their changes. Never overwrite the file. Only append, or, if the user asks, edit a specific fragment in place.

The user can say "cut the last one", "rewrite that one sharper", "merge those two" at any time. Treat those as first-class instructions.

</supporting-info>
