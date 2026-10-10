---
name: to-questionnaire
description: "Turn a decision you cannot answer alone into a Markdown questionnaire for the one person who can. Use for /to-questionnaire, 'turn this into a questionnaire', 'write questions for <person>', 'I need to ask the team about this', 'draft an async brief for them to fill in', or when a blocked decision is waiting on knowledge someone else holds."
metadata:
  credits:
    skill: to-questionnaire
    author: Matt Pocock
    license: MIT
    url: "https://github.com/mattpocock/skills/blob/main/skills/productivity/to-questionnaire/SKILL.md"
---

# To questionnaire

Ported from [mattpocock/skills](https://github.com/mattpocock/skills), MIT. The [upstream notes](https://github.com/dumkydewilde/agent-skills/blob/main/docs/mattpocock/UPSTREAM.md) explain what changed.

Turn something the user cannot answer alone into a **questionnaire**: a Markdown document they hand to one person to fill in async, or fill out together over a meeting. The recipient holds knowledge the user lacks. The questionnaire pulls it out of them.

**Grill the send, not the subject.** Interview the user only about the send, which they can always answer: who it goes to, and what they need back. The questions in the document then target the **gap** between what the recipient knows and what the user needs.

## Steps

1. **Who is it going to?** Ask, in one exchange, the recipient's role, expertise, and relationship to the user. This fixes the questionnaire's tone and how much context it must carry. Done when you know who the recipient is and what they know that the user does not.

2. **What do you need back?** Ask, in one exchange, the specific decisions or facts the user cannot resolve alone and needs from this person. Done when you have a concrete list of what the user must walk away able to do or decide.

3. **Write the questionnaire.** Draft questions aimed at the gap from steps 1 and 2, following the document structure below. Write it to `to-questionnaire-<slug>.md` in the current directory, slug from the topic, and report the path. Done when the file exists and every item the user named in step 2 is covered by a question.

4. **Unslop it.** Run the **unslop** skill over the draft before handing it over. A questionnaire a colleague reads is a prose surface like any other.

## Timezone note

The common case here is a colleague several hours out of sync. Assume one pass, not a conversation. Order questions most-important-first so a half-finished reply still lands the thing that was blocking.

## Document structure

Frame the document as a **discovery questionnaire**: the user lacks context, the recipient holds it. Order questions most-important-first, since async means you may only get one pass, and group them under `##` headings by theme once there are more than a handful.

<questionnaire-template>

# <Questionnaire title>

**Purpose:** why this questionnaire exists and the decision riding on it.

**From:** <the user>, **To:** <the recipient>, **How your answers will be used:** <where they go>

## Context

One paragraph orienting a recipient who was not in the user's head. Enough to answer well, not a page.

## How to answer

Deadline and rough effort. Partial answers and "I don't know" are useful: flag anything you are unsure of rather than skipping it.

## <Theme heading>

One `##` section per theme. Under each, its questions, most-important-first. Every question is one idea, never compound, with an answer stub directly beneath, and a one-line _why this matters_ only where the question could be misread or invite a throwaway answer.

<question-example>
### What load is the system expected to handle at launch?

_Why this matters: it decides whether we provision for burst traffic now or defer it._

>
</question-example>

## Anything else?

A closing catch-all: anything we did not ask that we should know?

</questionnaire-template>
