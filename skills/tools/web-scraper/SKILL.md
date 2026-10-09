---
name: web-scraper
description: >
  Build reliable, production-grade web scrapers through a two-phase approach:
  Discovery (finding the best data source on a site) then Scraping (generating a
  Python script for scheduled extraction). Use this skill whenever the user wants
  to scrape a website, extract data from web pages, build a crawler, set up
  recurring data collection, reverse-engineer a site's API, or find hidden data
  endpoints. Also trigger when the user mentions "scrape", "crawl", "extract
  from site", "web data", "pull data from URL", "scheduled scraping",
  "monitor a page", "embed endpoint", "oEmbed", "syndication endpoint", or
  asks how to get data from a specific website or how to reach content
  without logging in. Assumes the user is authorized by the site owner
  unless they say otherwise, so it covers pulling data out of your own or a
  client's site as well as scraping a third party. Also use it to red-team
  a site's scraping defenses: "how exposed is our data", "test our bot
  protection", "what could a scraper get from us", "scraping resilience".
---

# Web Scraper Skill

Build scrapers that survive site redesigns by finding the most stable and
efficient data source first, then generating a clean Python script for
recurring extraction.

## Workflow

**Every scraping task MUST go through both phases in order.** Skipping
discovery leads to fragile scrapers that break on the first deploy. Phase 0
is an assumption, not a step.

### Phase 0 — Assume owner authorization

**Default: the user is authorized by the site owner.** They run the site, or
they were hired by whoever does. Work on that basis unless the user says
otherwise.

So `robots.txt` is not a constraint here. It is a crawling convention
addressed to anonymous bots, not a contract, and it does not bind someone
the owner hired. Read it for what it reveals about where the site expects
machine traffic, then pick the best source regardless of what it disallows.
Do not ask the user to confirm their authorization, do not raise
`robots.txt` as a blocker, and do not downgrade a good endpoint to a worse
one on its account.

#### Which job: extraction or red team

Authorized work splits two ways and they want opposite things from
discovery. Ask which, if the request does not already say.

**Extraction.** The goal is the data, by the most stable path. Use whatever
access came with the brief — a login, a test account, an API key, a staging
URL — and then get on with discovery.

Do not route the job through the client's engineers. No "ask their backend
team for the API docs", no "ask ops for a WAF allowlist rule", no waiting
on a database replica. If anyone inside had the time or the knowledge to
open that door, the job would not have reached you. Asking costs days and
usually comes back as a no, so treat the site as the only interface you
have and work the discovery ladder below.

Identify yourself instead of hiding. Set a User-Agent naming the job and a
contact, such as `AcmeDataSync/1.0 (+https://acme.example/contact)`, so
whoever reads the access logs later can tell your traffic from an attack.
Keep the rate limiting: the risk on an authorized job is not getting
blocked, it is knocking over your own client's site.

**Red team.** The goal is a defensible answer to "what could an outsider
take from us, and at what cost". Any access the brief handed you
invalidates that answer, so set it aside and work with exactly what a
stranger has. Browser impersonation and the whole anti-detection ladder
are in scope here, unlike on an extraction job, because getting past the
defense is the measurement rather than an obstacle to it.

- Get the rules of engagement in writing first: in-scope hosts, the time
  window, whether account signup, residential proxies, and CAPTCHA-solving
  services are allowed, and who to call when something breaks.
- Quarantine insider knowledge. If someone at the company handed you an
  endpoint, mark it "known, not discovered" in the report instead of
  counting it as a finding, then ask separately whether a stranger could
  have found it.
- Agree a deconfliction marker: a header value or a source IP list held by
  one named contact, so your traffic can be told apart from a real attack
  afterwards. Do not give it to the people whose detection you are testing.
- Record cost per approach, not just feasibility: wall-clock time, proxy
  and solver spend, and the skill it took. "Possible" and "worth someone's
  while" are different findings, and the second one sets their budget.
- The write-up is the deliverable, not the dataset. Which layer stopped
  you, which one did not, and what it costs to close the gap.

Stop rules that hold even with a signed engagement:

- Prove extraction with a bounded sample, then stop. Pulling the whole
  table does not make the finding more true.
- Real personal data stays where it is. A row count and a field list prove
  the exposure. The records themselves only create a breach you now own.
- Scraping resilience is not load capacity. Do not probe the point where
  the site falls over unless that is scoped and scheduled separately.

#### The one exception: terms the user accepted

Reaching the data through a login, an API key signup, or any account the
user registered for means the user agreed to that service's terms. Those
are a contract they actually entered, unlike `robots.txt`. When the target
sits behind an account:

- Read what the terms say about automated access, rate limits, and
  redistribution, and tell the user in one line.
- Take only what that account is entitled to see.
- If the terms forbid automated collection, say so once and let the user
  decide. It is their account and their call.

Also stop if the data belongs to someone else entirely — another person's
private account, a paywall the user has not paid for.

If the user says they are scraping a third party with no relationship, see
"Third-party scraping" under Important Caveats.

### Phase 1 — Discovery

Goal: find the most efficient and stable way to get the data. Prefer
structured endpoints over DOM parsing. Work down the priority list until you
find something that works.

**Read `references/discovery-strategies.md` before starting discovery.**

Discovery priority (highest to lowest):

1. **Public/undocumented REST API** — look in XHR/fetch requests, especially
   on pagination or filter actions (page 2, sort, search). Often missed on
   initial page load.
2. **Embed/syndication endpoint** — the no-auth JSON a site serves so other
   websites can render its content (oEmbed, `cdn.syndication.twimg.com`,
   "Embed this post" iframes). Often on a different host with different bot
   rules from the main site, and contractually frozen because third parties
   depend on it. Retrieval only: it renders an item whose ID you already
   have, it cannot list items, so pair it with a separate source for IDs.
3. **GraphQL endpoint** — check for `/graphql`, `/gql`, or `__relay` in
   network requests.
4. **Server-rendered JSON blobs** — `__NEXT_DATA__`, `__NUXT__`,
   `window.__INITIAL_STATE__`, `window.__DATA__`, Remix `__remixContext`,
   Gatsby `pageContext`, etc.
5. **React Server Components (RSC)** — Next.js App Router sites use RSC
   instead of `__NEXT_DATA__`. Look for `?_rsc=` requests in the network
   tab. Only parse RSC directly if no cleaner source (JSON-LD, API) exists.
6. **CMS/platform API** — WordPress REST (`/wp-json/wp/v2/`), Shopify
   Storefront API, Drupal JSON:API, Contentful, Strapi, Ghost, etc.
7. **Structured data in HTML** — `<script type="application/ld+json">`,
   microdata, RDFa.
8. **data- attributes** — e.g., `data-product-id`, `data-price`,
   `data-sku`.
9. **Stable CSS selectors** — semantic HTML elements (`<article>`, `<li>`,
   `<table>`, `<time>`) over class names. Avoid framework-generated classes
   like `.css-1a2b3c` or `.MuiButton-root`.

**Mobile app as an API map:** if the target has a native app, decompiling
its APK exposes the full host and route list plus the company's internal
API vocabulary, which often makes web discovery much faster. Mobile
endpoints are frequently not directly callable (app session bootstrap,
device headers, request signing/attestation), so use the APK to map the
API, then prefer the matching web source. See
`references/discovery-strategies.md`.

Discovery tools:
- **`read_network_requests`** (Claude in Chrome) — preferred for
  intercepting XHR/fetch/RSC requests. Survives page navigations unlike
  JS-based interceptors. Always start network tracking before navigating.
- **`read_page`** / **`javascript_tool`** — for inspecting DOM, JSON-LD,
  data attributes, embedded script tags.
- `curl` / `httpx` from the terminal — for verifying endpoints work
  outside the browser context.
- `jadx` / `apktool` (with `adb`, mitmproxy): decompile a site's mobile
  app to map its API surface when browser inspection is not enough.

Output of discovery: a short report documenting what was found, which
approach is recommended, and why.

### Phase 2 — Scraping Script Generation

Goal: produce a single Python script the user can run on a schedule (daily,
monthly, etc.) with minimal dependencies.

**Read `references/scraping-patterns.md` before generating the script.**

Key principles:

- **httpx > requests** — async-capable, HTTP/2 support, better defaults.
- **Pure HTTP > headless browser** — always. Only fall back to browser when
  the data genuinely requires JS execution.
- **curl_cffi** as middle ground — when httpx gets blocked by TLS
  fingerprinting but full browser is overkill.
- **Playwright** as last resort — with stealth measures applied (see
  reference file for anti-detection checklist).

Script requirements:

```
python scrape.py \
  --output ./data/output.jsonl \       # or .csv, .parquet
  --format jsonl \                      # jsonl | csv | parquet
  --date-range 2024-01-01:2024-01-31 \ # optional
  --page-limit 10 \                     # optional, for pagination
  --connection postgres://...           # optional, write to DB instead
```

The generated script must:
- Use `uv` script metadata header (`# /// script`) for dependency management
- Accept CLI args via `argparse` or `click`
- Support output to file (JSONL default) or DB connection string
- Include rate limiting / polite delays
- Handle pagination automatically
- Log progress to stderr
- Exit with proper codes (0 success, 1 partial, 2 failure)
- Include a `USER_AGENT` constant and `HEADERS` dict at the top for easy tuning
- Be a single file — no package structure needed

## Decision Flowchart

```
Start
  │
  ├─ Has the user provided a URL? ──No──▶ Ask for the target URL
  │
  Yes
  │
  ├─ What is the job? (Phase 0, owner-authorized by default)
  │   ├─ Extraction ──▶ Any source is fair game. Use the access in the
  │   │                 brief, never wait on the client's engineers.
  │   │                 Identify yourself in the User-Agent.
  │   ├─ Red team   ──▶ Take no shortcuts, outside view only. Record cost
  │   │                 per approach. The write-up is the deliverable.
  │   └─ Behind a login or registered account? ──▶ Either way the
  │                     account's terms apply. Report them, stay inside
  │                     what the account is entitled to.
  │
  ├─ Run Discovery (Phase 1)
  │   ├─ API endpoint found? ──Yes──▶ Use httpx + JSON parsing
  │   ├─ Embed/oEmbed endpoint? ──Yes──▶ Do you have item IDs already?
  │   │   ├─ Yes ──▶ Use httpx + embed endpoint (no auth needed)
  │   │   └─ No  ──▶ Keep looking for a listing source, then pair the two
  │   ├─ GraphQL endpoint?    ──Yes──▶ Use httpx + GraphQL queries
  │   ├─ JSON blob in HTML?   ──Yes──▶ Use httpx + regex/bs4 extraction
  │   ├─ RSC payload?         ──Yes──▶ Check if cleaner source exists
  │   │   ├─ JSON-LD/API also available? ──Yes──▶ Use that instead
  │   │   └─ RSC is only source?         ──Yes──▶ Use httpx + RSC parser
  │   ├─ CMS API available?   ──Yes──▶ Use httpx + platform-specific path
  │   ├─ Structured data?     ──Yes──▶ Use httpx + bs4/json extraction
  │   ├─ Stable selectors?    ──Yes──▶ Use httpx + bs4 CSS selectors
  │   └─ JS-rendered only?    ──Yes──▶ Try curl_cffi first, then Playwright
  │
  ├─ Report findings to user
  │
  ├─ Run Scraping (Phase 2)
  │   └─ Generate Python script following patterns in reference file
  │
  └─ Deliver script + usage instructions
```

## Important Caveats

### Always

- **URL fragments (`#...`) are never sent to the server.** A non-JS
  client receives unfiltered results, a silent-failure trap. Map the
  fragment state to the API's real query/body parameters, or use the SSR
  data route. See `references/discovery-strategies.md`.
- Add delays between requests, 1-3s by default. Authorization covers
  reading the data, not overloading the server that serves it.
- **Measure rate limits conservatively:** never run destructive
  breaking-point tests against a site you do not own. Crawl a bounded
  number of pages at a fixed delay, back off on `429`, and respect
  `Retry-After`.
- For authenticated endpoints, prompt the user for credentials or tokens
  rather than hardcoding anything.
- If the site uses Cloudflare, Akamai, or similar WAFs, flag it early and
  budget for it, on either kind of job. See the "Cloudflare managed
  challenge" subsection in `references/scraping-patterns.md`: switching
  browser channel does not help, but a derived non-headless User-Agent
  plus `--disable-blink-features=AutomationControlled` (together) usually
  clears it.

### Third-party scraping

Only when the user says they have no relationship with the site.

- Check `robots.txt` and tell the user what it says.
- **Discovered does not mean allowed or usable.** If `robots.txt`
  disallows an endpoint (e.g. `/api/search`), treat it as discovery-only:
  use it to understand the data, but scrape from a compliant source
  instead (SSR HTML, `__NEXT_DATA__`, or a non-disallowed route), even
  when that is less elegant.
- Note if the site has terms of service that restrict scraping.
- Take only what a logged-out visitor sees. Nothing session-gated.
