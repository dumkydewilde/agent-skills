# The codex panelist

Every Claude panel in dstack is one vendor. Three Claude reviewers agreeing is
closer to one opinion held three times than to three independent confirmations,
because they share training, tokenizer, and failure modes. Upstream got its
adversarial signal from four vendors disagreeing. This file is how you get some
of that back.

Codex runs headless, so one reviewer per panel is a real second vendor. It is a
Bash call, not an Agent call. It never takes a `model` value from
`~/.claude/dstack-models.md`, because those values are Claude model names.

## The invocation

```bash
codex exec --model gpt-5.6-terra --sandbox read-only \
  -o /tmp/codex-panelist.md "<the filled panelist prompt>" \
  < /dev/null > /dev/null 2>&1
cat /tmp/codex-panelist.md
```

Give it the same filled prompt the Claude panelists get. It reads the repo
itself, so pass file paths rather than pasting file contents.

## Four things that will bite you

- **`< /dev/null` is required.** Without it `codex exec` blocks waiting on
  stdin and the call hangs until the timeout kills it.
- **`-o <file>` is the only clean way to get the answer.** Plain stdout carries
  roughly 130KB of session preamble, hook chatter, and unrelated auth and
  telemetry errors around a few hundred bytes of review.
- **`--sandbox read-only` keeps a reviewer from editing the tree.** Every panel
  role here is read-only by contract. Use `workspace-write` only when the
  panelist has to run something to reach its verdict.
- **Run it from inside the git repo.** Outside a trusted directory it aborts
  unless you pass `--skip-git-repo-check`.

## Model slug

`gpt-5.6-terra` needs codex-cli 0.153 or newer. Older CLIs reject it with
"requires a newer version of Codex"; fall back to `gpt-5.5`, which is slower to
reason but works. Check with `codex --version` if a run fails at the model
line rather than assuming the panelist is unavailable.

## Folding the findings in

Label its output `Reviewer (codex)` wherever the skill lists reviewers, so the
verdict shows which claims survived a second vendor.

Weight agreement accordingly. A finding raised by codex and a Claude reviewer
is the strongest signal a panel produces. A finding raised by two Claude
reviewers and not codex is weaker than its count suggests. Say which kind you
have when the verdict turns on it.

Budget for one extra round trip. A codex reviewer on a real diff takes
noticeably longer than a Claude subagent, so run it in parallel with the Claude
panelists rather than after them. The one exception is **arena**, where the
judge must not start until every candidate has finished writing. If it starts
earlier it reads half-written files and reports them as dropouts.

Skip it, and say you skipped it, when the review is small enough that the round
trip costs more than the diversity buys.
