---
name: share-secrets
description: Keep API keys and tokens in one password manager and load them on every machine through its CLI, with 1Password op:// references in a committed .tpl file, or Bitwarden Secrets Manager through bws. Read this when a project or shell needs a secret, when setting up a new machine, or before writing a key into a .env, a shell rc, or a config file.
---

Someone who runs several providers on several machines needs one place that
holds the keys. That place does not have to be AWS Secrets Manager or Vault.
The password manager they already pay for is enough: the 1Password CLI (`op`)
or the Bitwarden Secrets Manager CLI (`bws`). Machines hold references to
secrets, never the secrets themselves, and the CLI fills them in.

Check which CLI is installed and signed in before you pick a flow:
`op vault list >/dev/null`, or `bws project list` with `BWS_ACCESS_TOKEN` set.
Skip `op whoami`: with the 1Password desktop app integration it reports "not
signed in" even when reads work. If neither CLI works, ask the user which
manager they use rather than writing a plaintext `.env`.

## Pick a setup

The trade-off is a human unlock versus a stored token. A password manager
CLI that needs an unlock keeps the secret behind something the user knows,
and cannot run unattended. A machine token runs anywhere, and whoever reads
the token reads everything it is scoped to.

| Setup | Use |
|---|---|
| The user's laptops, interactive shells | `op` with the desktop app integration, which prompts for Touch ID. On Bitwarden, `bws` with one machine account per laptop and its token in the Keychain. |
| Headless: CI, servers, a homelab | `op` with a service account, or `bws`. Never `bw`, which would need the master password on disk. |
| A team sharing one project's keys | A shared 1Password vault or a shared `bws` project, with a token per person or machine. |
| A one-off secret already in the personal vault | `op read` or `bw get` by hand. Not worth a template. |

1Password covers both sides with one CLI and one template: desktop unlock on
a laptop, a service account elsewhere. Bitwarden splits them into two
products. Default to `bws` for anything that becomes an env var, and keep
`bw`, the password manager CLI, for the last row. Keep every token's scope
small, so a leaked one exposes one project.

### Examples

- **An agent logs into a website**, say a Playwright check against a staging
  admin page. The login already lives in the personal vault, so use the
  password manager CLI and hand the value to the script through the
  environment, never the transcript:
  `STAGING_PASSWORD=op://Private/Staging admin/password` in a template run with
  `op run`, or `STAGING_PASSWORD="$(bw get password staging.example.com)"`
  inline. One-time codes come from `op item get "Staging admin" --otp` or
  `bw get totp staging.example.com`.
- **A project needs the same keys on two machines**, say a MotherDuck token
  and an OpenAI key on a laptop and a desktop. That is the secrets-manager
  case: a committed `.env.tpl` against one 1Password item, or one `bws`
  project, so a rotated key reaches both machines on the next run.
- **A scheduled job on a server**, say a nightly Prefect flow on a homelab NAS.
  Nobody is there to unlock anything, so use a 1Password service account or a
  `bws` machine account, scoped to that one project.
- **A teammate clones the repo.** They need access to the shared vault or
  `bws` project and nothing else; the template already says which keys exist
  and the comment at the top says how to run it.
- **Coding agents in every shell need model provider keys.** Use the cached
  rc block below, with only those keys in it.

## 1Password: references in a template

A secret reference is `op://<vault>/<item>/<field>`, for example
`op://Private/OpenAI/credential`. The reference is not secret, so the file that
holds it can be committed. Name it after the file it produces, with `.tpl`
added: `.env.tpl` produces `.env`.

There are two ways to use the template, and they want different syntax.

**`op run` for one command.** The secrets exist only in that process's
environment and never touch disk. References are bare values:

```sh
# .env.tpl
# Run: op run --env-file=.env.tpl -- uv run python main.py
OPENAI_API_KEY=op://Engineering/dev-myapp/OPENAI_API_KEY
MOTHERDUCK_TOKEN=op://Engineering/dev-myapp/MOTHERDUCK_TOKEN
# Not secret, so a literal value
API_BASE_URL=http://localhost:3000
```

Conventions that keep a shared template readable, from MotherDuck's own repos:

- One item per app per environment, `dev-<app>` and `prod-<app>`.
- Field names equal the env var names, so each line reads as its own mapping.
- Non-secret config sits inline as literal values.
- A usage comment at the top says the exact command.
- With more than one 1Password account signed in, pick one with
  `OP_ACCOUNT=<team>.1password.com` or `--account`.
- An item, section, or field name containing a dot breaks the reference,
  because `op` reads the dot as a separator.

**`op inject` for a file a tool insists on reading.** References go in double
braces, and the output is plaintext:

```sh
# config.yml.tpl
api_key: {{ op://Private/OpenAI/credential }}
```

```sh
op inject -i config.yml.tpl -o config.yml
```

Prefer `op run`. Use `op inject` only when the tool reads a file and cannot take
environment variables. Put the generated file in `.gitignore` in the same
change that creates the template. Ignoring `.env` and `.env.*`, then
re-including `!.env.tpl`, covers every generated variant. Wire both into the project's task runner
(a Makefile target, a taskipy task, an npm script) so nobody types the command
from memory.

To find a reference, run `op item get "<item>" --format json` and read the
field's `reference` value. Do not paste the field's value anywhere.

## Bitwarden Secrets Manager

Use `bws`, the Secrets Manager CLI, not `bw`, the password manager CLI. `bws`
has no template file. A project in Secrets Manager groups the secrets, and
each secret's key becomes the env var name, so name keys like
`OPENAI_API_KEY`. A key that is not a valid env var name is skipped by shells
and commented out of `env` output.

`bws` authenticates with a machine account's access token in
`BWS_ACCESS_TOKEN`. Give each machine its own machine account, scoped to the
projects it needs, so one lost laptop is one revoked token.

```sh
bws run --project-id <project-id> -- 'uv run python main.py'
```

Single-quote the command so the shell does not expand it before `bws` does.
The project id is not secret and can go in the repo's task runner.

## Shell-wide keys, cached in the rc file

Keys a user wants in every shell, such as model provider keys for coding
agents, go in one template outside any repo, for example
`~/.config/secrets/env.tpl`:

```sh
export ANTHROPIC_API_KEY="{{ op://Private/Anthropic/credential }}"
export OPENAI_API_KEY="{{ op://Private/OpenAI/credential }}"
```

Calling `op` from `~/.zshrc` on every new shell is slow and prompts for
unlock each time. Cache the resolved file instead and refresh it when it is
older than 12 hours:

```zsh
# ~/.zshrc
secrets_tpl=~/.config/secrets/env.tpl
secrets_cache=~/.cache/secrets.env
if [[ -r $secrets_tpl ]] && (( $+commands[op] )); then
  stale=($secrets_cache(N.mh+12))
  if [[ ! -s $secrets_cache || -n $stale ]]; then
    mkdir -p ${secrets_cache:h}
    (umask 077
     op inject --force -i $secrets_tpl -o $secrets_cache.tmp >/dev/null &&
       mv $secrets_cache.tmp $secrets_cache)
  fi
fi
[[ -r $secrets_cache ]] && source $secrets_cache
unset secrets_tpl secrets_cache stale
```

`umask 077` makes the cache readable by the user only. Writing to `.tmp` first
keeps the old cache when `op` is locked or offline. To force a refresh after
rotating a key, delete `~/.cache/secrets.env` and open a new shell.

The template is the part that travels. Put it in the user's dotfiles repo; a
new machine needs the template, the rc block, and `op signin`.

With Bitwarden, the project is the template. Swap the refresh line for:

```zsh
bws secret list <project-id> --output env --color no >$secrets_cache.tmp &&
  mv $secrets_cache.tmp $secrets_cache
```

and guard on `(( $+commands[bws] ))` instead of the template. The output is
`KEY="value"` lines without `export`, so source it with
`set -a; source $secrets_cache; set +a`. `bws` does not escape values, so a
secret containing `"`, `$` or a backtick breaks or expands when sourced; keep
those out of the shell-wide project. `BWS_ACCESS_TOKEN` itself cannot come
from the cache; read it from the macOS Keychain with
`security find-generic-password -s bws -w` or from a mode 600 file.

The cache is plaintext on disk. That is the trade for fast shells. Keep
anything with production write access out of it, and load those with `op run`
per command.

## CI and servers

There is no desktop app to unlock in CI. Keep the same template and give the
runner a 1Password service account token scoped to one vault, as
`OP_SERVICE_ACCOUNT_TOKEN`; `op run` and `op inject` then work unchanged. With
Bitwarden, give the runner its own machine account's `BWS_ACCESS_TOKEN` and
the same `bws run` command. Otherwise set the values as the CI or hosting
provider's own secrets (Vercel, Cloudflare, GitHub Actions) and keep
production references out of the template altogether.

## Never

- Commit a resolved file, or a template whose values are real secrets rather
  than references.
- Print a secret into the conversation: no `op read`, `cat .env`, or `echo
  $KEY` to check it worked. Check presence instead, for example
  `[[ -n $OPENAI_API_KEY ]] && echo set`.
- Save a secret to Valise. A memory may record which vault and item holds a
  key, never its value.
