# agent-skills

Agent skills for Claude Code and Codex, shipped as three plugins. All work in
either harness from the same canonical source.

## `tools`

General-purpose utilities.

| Skill | What it does |
|-------|--------------|
| `conversation-history` | Search past Claude Code, Claude Desktop, Codex, and ChatGPT conversations from local logs and exports |
| `web-scraper` | Build resilient scrapers via a discovery-then-script workflow |
| `field-notes` | Build field notes: one sheet, a notebook of them, or a shelf of notebooks. Markdown sources, HTML templates for a swipeable deck on aged paper, the indexes that open it, and image prompts for printed posters |
| `wizard` | Generate an interactive bash wizard that walks a human through steps only they can perform: a third-party dashboard, minting credentials, wiring CI secrets. Ported from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT) |

![Twelve food sheets on a notebook index, each a drawn mark on pale paper
captioned in typewriter type](skills/tools/field-notes/assets/examples/food-notebook-index-rendered.jpg)

*What `field-notes` builds, at the middle size: one notebook of twelve sheets,
generated from markdown. The whole shelf is live on
[dumky.net](https://www.dumky.net/field-notes/).*

## `dstack`

A working style for non-trivial engineering and writing work. Forked from
[pstack](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan (MIT).
[`docs/dstack/UPSTREAM.md`](docs/dstack/UPSTREAM.md) covers what changed in the
port and why; `docs/dstack/LICENSE` carries the upstream MIT notice.

Start with `/dstack-mode` at the top of a task. It matches the task to a
playbook, copies that playbook's steps into a todo list, and routes to the other
skills as the steps need them. The rest are situational.

| Skill | Use it when |
|-------|-------------|
| `dstack-mode` | Default entry point for any non-trivial task |
| `principles` | The twenty-two rules the mode works from, one file each |
| `how` | You want a walkthrough of how a subsystem works |
| `why` | You want to know why something was built this way |
| `teach` | You want to actually understand a change, not just have it summarized |
| `recall` | You are resuming work and want your recent context rebuilt |
| `architect` | Code is about to cross a function boundary and the shape is not settled |
| `arena` | You want N parallel attempts, then the best parts of each |
| `swarm` | You want N parallel workers across slices, then one report |
| `interrogate` | You have a diff and want several reviewers to try to break it |
| `blast-radius` | A small-looking change might break something outside the diff |
| `figure-it-out` | No bundled playbook fits, so design a rigorous one |
| `tdd` | A bug has a cheap local test path, so write the failing test first |
| `create-verification-skill` | The project has no scripted way to prove app behavior |
| `show-me-your-work` | You want a reviewable decision trail for unattended work |
| `reflect` | A long task landed and the lesson should become a skill edit, or the environment it ran in needs an audit |
| `authoring-skills` | You are writing or fixing a SKILL.md |
| `no-comments` | Strip comments before review |
| `unslop` | You are cleaning up writing, removes AI tells |
| `dehistorize` | An artifact narrates its own edit history, strip the leaks |
| `bro` | Restate the last message in plain human language |
| `technical-writing` | Docs, RFCs, readmes, PR descriptions, commit messages |
| `typescript-best-practices` | You are reading or editing TypeScript |
| `setup-dstack` | Change which model runs which dstack role |

Four reference files inside `dstack` are ported from
[mattpocock/skills](https://github.com/mattpocock/skills) (MIT): the ADR format
under `architect`, the glossary format under `technical-writing`, the
environment-audit lens under `reflect`, and the writing-for-agents theory under
`authoring-skills`. See
[`docs/mattpocock/UPSTREAM.md`](docs/mattpocock/UPSTREAM.md).

Claude Code also gets two subagents from this plugin, `dstack-agent` and
`comment-sicko`. The Codex plugin format has no `agents` key, so those are
Claude Code only.

The review panels (`interrogate`, `arena`, `architect`, the `how` critics) want
a second vendor at the table. `/setup-dstack` writes `~/.claude/dstack-models.md`
to say which model runs which role. Without that file each skill falls back to
its inline default, which is Claude-only.

## `studio`

The skills that need a person in the room. dstack's **never-block-on-the-human**
principle and `dstack-mode`'s probe-instead-of-asking rule both push the other
way, and both are about facts. These are about decisions, which only you hold.
Ported from [mattpocock/skills](https://github.com/mattpocock/skills) by Matt
Pocock (MIT). [`docs/mattpocock/UPSTREAM.md`](docs/mattpocock/UPSTREAM.md) covers
what changed in the port; `docs/mattpocock/LICENSE` carries the upstream notice.

| Skill | Use it when |
|-------|-------------|
| `grilling` | A plan or decision needs stress-testing and you are the one who has to answer |
| `to-questionnaire` | A decision is blocked on knowledge someone else holds, several timezones away |
| `writing-fragments` | You have a half-formed idea and want mining for raw material, no structure yet |
| `writing-shape` | You have a pile of material and want it shaped into an article, paragraph by paragraph |
| `wayfinder` | The work is too big to plan in one session, so chart the route as decision tickets on Linear |

`writing-fragments` and `writing-shape` are the explore and exploit halves of one
loop. `unslop` and `technical-writing` are the polish pass that follows them, not
a substitute for them.

## Install in Claude Code

```bash
/plugin marketplace add dumkydewilde/agent-skills
/plugin install tools@agent-skills
/plugin install dstack@agent-skills
/plugin install studio@agent-skills
```

Or wire it into `~/.claude/settings.json` so it stays available and updates
itself:

```json
{
  "extraKnownMarketplaces": {
    "agent-skills": {
      "source": { "source": "github", "repo": "dumkydewilde/agent-skills" }
    }
  }
}
```

## Install in Codex

```bash
codex plugin marketplace add dumkydewilde/agent-skills
codex plugin add tools@agent-skills
codex plugin add dstack@agent-skills
codex plugin add studio@agent-skills
codex plugin list --marketplace agent-skills
```

For local development before pushing, add a clone as a local marketplace from
the repo root:

```bash
codex plugin marketplace add .
codex plugin add dstack@agent-skills
```

## Layout

```
agent-skills/
├─ .claude-plugin/marketplace.json       # Claude marketplace manifest
├─ .agents/plugins/marketplace.json      # Codex marketplace manifest
├─ skills/                               # canonical, agent-agnostic source of truth
│  ├─ tools/{conversation-history,field-notes,web-scraper,wizard}/
│  ├─ dstack/
│  │  ├─ dstack-mode/                    # router, playbooks, references, scripts
│  │  ├─ principles/references/          # twenty-two principle files
│  │  └─ <twenty-two more skills>/
│  └─ studio/{grilling,to-questionnaire,writing-fragments,writing-shape,wayfinder}/
└─ plugins/
   ├─ claude/{tools,dstack,studio}/   (.claude-plugin/plugin.json + skills -> ../../../skills/<name>)
   └─ codex/{tools,dstack,studio}/    (.codex-plugin/plugin.json + real, release-ready skill copy)
```

The canonical skill files live under `skills/<plugin>/<skill-name>/`. The Claude
plugin symlinks to that source. The Codex/ChatGPT plugin carries a real copy,
because their importer ignores symbolic links immediately inside `skills/`.

## Changing a skill

Edit the canonical copy under `skills/`, never the one under
`plugins/codex/`. Then refresh the release copies and check them:

```bash
scripts/sync-plugin-skills.sh
python3 -m unittest discover -s tests -v
```

The tests check three things. The Codex copy matches the canonical source byte
for byte, the Claude symlink points where it should, and every skill has valid
frontmatter with resolvable links and no leftover Cursor-only keys. CI runs the
same two test modules on every push and pull request.

Adding a whole plugin also means adding its name to the `PLUGINS` array in
`scripts/sync-plugin-skills.sh` and to `PLUGINS` in
`tests/test_codex_plugin_package.py`, plus an entry in both marketplace
manifests.

## Notes

- Skills cannot rely on `${CLAUDE_PLUGIN_ROOT}`; that only expands in slash
  commands and hooks. A skill that ships a script references it through the
  skill's announced **base directory** instead, see
  `skills/tools/conversation-history/SKILL.md`.
- `conversation-history` reads local files only: `~/.claude/projects`,
  `~/.codex/sessions`, and ChatGPT export drops. Nothing leaves the machine.

## License

MIT, see [`LICENSE`](LICENSE). Two upstreams ride along under the same license.
The `dstack` plugin is derived from pstack by Lauren Tan, notice at
`docs/dstack/LICENSE`. The `studio` plugin, the `wizard` skill, and four `dstack`
reference files are derived from [mattpocock/skills](https://github.com/mattpocock/skills)
by Matt Pocock, notice at `docs/mattpocock/LICENSE`.
