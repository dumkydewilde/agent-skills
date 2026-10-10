---
name: wizard
description: "Generate an interactive bash wizard that walks a human through steps only they can perform. Use for /wizard, 'write a setup script for this', 'walk me through provisioning X', 'turn this README setup section into a script', or when the job means clicking through a third-party dashboard, minting credentials, wiring CI secrets, or running a one-off migration or cutover. Not for steps the agent can perform itself."
metadata:
  credits:
    skill: wizard
    author: Matt Pocock
    license: MIT
    url: "https://github.com/mattpocock/skills/blob/main/skills/engineering/wizard/SKILL.md"
---

# Wizard

Ported from [mattpocock/skills](https://github.com/mattpocock/skills), MIT, including `template.sh` unchanged. The [upstream notes](https://github.com/dumkydewilde/agent-skills/blob/main/docs/mattpocock/UPSTREAM.md) explain what changed.

A **wizard** is a bash script that walks a human, step by step, through a manual procedure that is tedious to do by hand and tedious to re-explain to an agent every time. It opens each URL, says exactly what to click and copy, captures the values, writes them where they belong, confirms at every stage, and shows how many stages are left. It might configure third-party services, run a one-off migration, or move a project from one state to another.

The UX is already solved by [template.sh](template.sh): stage-by-stage progress, confirmation gates, cross-platform URL opening including WSL, hidden secret entry, idempotent `.env` upserts, `gh secret` and `gh variable` writes, and a closing summary. **Your job is only to scope the procedure and author its stages.** The library above the `STAGES` marker is identical in every wizard. That consistency is the point. Never hand-edit it.

A wizard is ephemeral by default: built for one run, saved to a scratch or `scripts/` path, deleted when the job is done. Commit it only when the user wants a repeatable setup path that should live in the repo.

Writing the script instead of narrating the steps is the **build-the-lever** principle. The artifact is the thing a second person reruns.

## When a wizard is the right shape

Good fits in this stack: minting a MotherDuck service-account token and wiring it into `.env` and GitHub Actions, a Cloudflare or Vercel first deploy, homelab provisioning across Prefect, Portainer, SeaweedFS, and Postgres, and any cookbook or docs page whose setup section currently reads as twelve numbered steps and a screenshot.

Bad fit: anything the agent can just do. A wizard that wraps `uv sync` is a worse `uv sync`.

## Process

### 1. Scope the procedure

Work out every manual step the human must take and every value captured along the way. Read the repo first, do not ask cold:

- For setup: `.env`, `.env.example`, `.env.*`, the README, `docker-compose*`, framework config, `pyproject.toml`, and `.github/workflows/*`. Every `secrets.*` and `vars.*` reference is a value the wizard must produce.
- For a migration or transition: the current state, the target state, and the irreversible actions between them.

Then show the user the ordered list of stages and the values each produces, and confirm. They may add, drop, or reorder.

**Done when:** every stage is named in order, and for each captured value you know where the human gets it, where it is written (`.env`, a GitHub secret, both, or nowhere, since some stages are pure actions), and whether it is secret and so needs hidden entry.

### 2. Map each stage's journey

For each stage, write the precise path a human follows: which URL to open, what to do there, where a value is shown, which variable it fills. For example, "Settings, then Service accounts, then Create token, then copy the value". Where you do not actually know the current UI or the exact command, say so and ask the user or check the docs. Never invent steps that may not exist.

**Done when:** every stage traces to concrete instructions a stranger could follow.

### 3. Author the wizard

Copy `template.sh` to the target path. Replace the example stage with one `stage` per step, in dependency order. Use the library helpers: `stage`, `say` and `step`, `open_url`, `ask` and `ask_secret`, `write_env`, `set_secret` and `set_var`, `pause` and `confirm`. Set `TOTAL_STAGES` to the number of stages you wrote.

Hold the bar the template sets. Open the URL before asking for its value. Use `ask_secret` for anything secret. `write_env` every persisted value. `set_secret` only the values CI actually needs. `confirm` before any irreversible action. Each `stage` clears the screen so only the current step is visible, so keep a stage to one focused task and nothing the human needs scrolls away. Do not touch the library above the marker.

### 4. Verify and hand off

- Run `bash -n <script>`, then `shellcheck` if available.
- `chmod +x <script>`.
- Do not run it end to end yourself. It opens browsers and blocks on human input. Trace it statically instead: every value from step 1 is captured and lands where step 1 said, and every `set_secret` name exactly matches a `secrets.*` reference in CI.
- Tell the user how to run it. If it is a repeatable setup path, commit it and link it from the README so the next person runs the script instead of asking an agent.
