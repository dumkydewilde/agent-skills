### Docs change

**You own the claim. Every sentence about the product is a testable assertion.**

Documentation, a reference page, a tutorial, a how-to, a README, release notes, or a blog post whose deliverable is prose that has to be correct against a real product. Distinct from Investigation, which explains to one reader and stops. This ships.

The failure mode here is not bad writing. It is confident prose describing behavior nobody ran.

1. Name the audience and the Diátaxis mode before writing. Tutorial, how-to, reference, or explanation. One mode per page. A page that drifts between modes is the most common structural defect, and it is invisible until you name the intended mode first.
2. Ground the claims. Route through the **how** skill when the page explains a subsystem you have not traced. Route through the **why** skill when the page has to say why something works the way it does, since code shape does not carry intent.
3. Throughput checkpoint stays one line for a single page: `throughput checkpoint: n/a, one page`. A docs set spanning many pages gets the four-item version, with pages as independent workstreams and any shared reference page as the blocking first step.
4. **Run every code sample.** This is the step that separates docs from fiction (the **prove-it-works** principle). Every command, query, snippet, and config block gets executed against the real thing, and you paste the real output rather than the output you expected. A sample you cannot run is a risk to name in the reply, not a sample to ship.
5. Check the claims that are not samples. Version numbers, default values, flag names, limits, pricing, and endpoint paths all go stale silently. Verify each against the source of truth, not against another doc page. Prefer linking a structural source over restating a value that will drift.
6. Write it under the **technical-writing** skill in full, then apply **unslop**. Sentence-case headings, active voice, one idea per sentence, no long dashes, no mid-sentence colons.
7. Check the surrounding set. A new page that duplicates an existing one is worse than no page. Find what already covers this, and either extend it or say plainly why a separate page earns its place (the **subtract-before-you-add** principle). Update the nav, the index, and any page that should now link here.
8. Read it once as the reader, start to finish, without skipping the parts you just wrote. Broken step ordering and undefined terms only surface on a straight read.
9. Run **Opening a PR**.

Screenshots and recorded output go stale faster than prose. Prefer a runnable command over a screenshot. When a screenshot is genuinely the clearest thing, note in the PR what would invalidate it.

**Reply:** what changed and who it is for, the Diátaxis mode, which samples you actually ran and their real output, any claim you could not verify and why, and what else in the docs set now points here.
