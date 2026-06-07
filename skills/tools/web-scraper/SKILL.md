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
  "monitor a page", or asks how to get data from a specific website.
---

# Web Scraper Skill

Build scrapers that survive site redesigns by finding the most stable and
efficient data source first, then generating a clean Python script for
recurring extraction.

## Two-Phase Workflow

**Every scraping task MUST go through both phases in order.** Skipping
discovery leads to fragile scrapers that break on the first deploy.

### Phase 1 — Discovery

Goal: find the most efficient and stable way to get the data. Prefer
structured endpoints over DOM parsing. Work down the priority list until you
find something that works.

**Read `references/discovery-strategies.md` before starting discovery.**

Discovery priority (highest to lowest):

1. **Public/undocumented REST API** — look in XHR/fetch requests, especially
   on pagination or filter actions (page 2, sort, search). Often missed on
   initial page load.
2. **GraphQL endpoint** — check for `/graphql`, `/gql`, or `__relay` in
   network requests.
3. **Server-rendered JSON blobs** — `__NEXT_DATA__`, `__NUXT__`,
   `window.__INITIAL_STATE__`, `window.__DATA__`, Remix `__remixContext`,
   Gatsby `pageContext`, etc.
4. **React Server Components (RSC)** — Next.js App Router sites use RSC
   instead of `__NEXT_DATA__`. Look for `?_rsc=` requests in the network
   tab. Only parse RSC directly if no cleaner source (JSON-LD, API) exists.
5. **CMS/platform API** — WordPress REST (`/wp-json/wp/v2/`), Shopify
   Storefront API, Drupal JSON:API, Contentful, Strapi, Ghost, etc.
6. **Structured data in HTML** — `<script type="application/ld+json">`,
   microdata, RDFa.
7. **data- attributes** — e.g., `data-product-id`, `data-price`,
   `data-sku`.
8. **Stable CSS selectors** — semantic HTML elements (`<article>`, `<li>`,
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
  ├─ Run Discovery (Phase 1)
  │   ├─ API endpoint found? ──Yes──▶ Use httpx + JSON parsing
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

- Always check `robots.txt` and mention it to the user.
- **Discovered does not mean allowed or usable.** If `robots.txt`
  disallows an endpoint (e.g. `/api/search`), treat it as discovery-only:
  use it to understand the data, but scrape from a compliant source
  instead (SSR HTML, `__NEXT_DATA__`, or a non-disallowed route), even
  when that is less elegant.
- **URL fragments (`#...`) are never sent to the server.** A non-JS
  client receives unfiltered results, a silent-failure trap. Map the
  fragment state to the API's real query/body parameters, or use the SSR
  data route. See `references/discovery-strategies.md`.
- Note if the site has terms of service that restrict scraping.
- Add appropriate delays between requests (1-3s default for polite scraping).
- **Measure rate limits conservatively:** never run destructive
  breaking-point tests against a site you do not own. Crawl a bounded
  number of pages at a fixed delay, back off on `429`, and respect
  `Retry-After`.
- For authenticated endpoints, prompt the user for credentials or tokens
  rather than hardcoding anything.
- If the site uses Cloudflare, Akamai, or similar WAFs, flag this early
  and adjust the strategy accordingly.
