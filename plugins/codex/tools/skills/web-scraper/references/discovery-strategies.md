# Discovery Strategies Reference

Systematic approaches to find the best data source on a target site.
Work through these in order — stop as soon as you find a viable approach.

## Table of Contents

1. [Network Request Interception](#1-network-request-interception)
2. [Embed and Syndication Endpoints](#2-embed-and-syndication-endpoints)
3. [Mobile App API Discovery (APK Decompilation)](#3-mobile-app-api-discovery-apk-decompilation)
4. [Server-Rendered JSON Blobs](#4-server-rendered-json-blobs)
5. [CMS and Platform APIs](#5-cms-and-platform-apis)
6. [GraphQL Endpoints](#6-graphql-endpoints)
7. [Structured Data in HTML](#7-structured-data-in-html)
8. [Data Attributes](#8-data-attributes)
9. [Stable CSS Selectors](#9-stable-css-selectors)
10. [Discovery Report Template](#10-discovery-report-template)

---

## 1. Network Request Interception

The single most valuable discovery technique. Most modern sites load data
via XHR/fetch — finding these endpoints gives you a clean JSON API.

### What to look for

- Requests to `/api/`, `/v1/`, `/v2/`, `/_next/data/`, `/graphql`
- JSON responses with the data you need
- Pagination parameters: `?page=2`, `?offset=20`, `?cursor=abc`
- Auth headers: `Authorization: Bearer ...`, API keys in query params

### Critical: check page 2 and interactions

Many SPAs load the first page from server-rendered HTML but fetch
subsequent pages via API. **Always try these actions:**

- Click "next page" or "load more"
- Change sort order or apply a filter
- Scroll down (infinite scroll triggers)
- Open a detail view / modal
- Use the site's search

Each of these actions may reveal API endpoints not visible on initial load.

### Using Claude in Chrome for discovery

**Always use the `read_network_requests` tool** rather than injecting JS-based
network interceptors (e.g., patching `fetch` or `XMLHttpRequest`). JS
interceptors are lost on page navigation, which is exactly when the most
interesting requests happen (pagination, filter changes, search). The
`read_network_requests` tool survives navigations and captures everything.

Workflow:

```
1. Call read_network_requests once to start tracking (even before navigating)
2. Navigate to the target URL
3. Wait for the page to load (2-3 seconds)
4. Read network requests filtered by useful patterns:
   - urlPattern="/api/"    → REST endpoints
   - urlPattern="graphql"  → GraphQL
   - urlPattern="_rsc"     → React Server Components
   - urlPattern="_next"    → Next.js data routes
5. Interact with the page (paginate, filter, search, sort)
6. Read network requests again — new endpoints often appear only on
   interaction, not on initial load
7. Inspect promising requests:
   - URL pattern and query parameters
   - Response format (JSON, RSC payload, HTML)
   - Pagination mechanism (page number, cursor, offset)
```

**Why not JS interceptors?** When you navigate to page 2 or apply a filter,
the browser often does a full navigation (not a client-side transition).
This destroys any `fetch`/`XHR` monkey-patches you injected. The
`read_network_requests` tool is browser-level and persists across
navigations within the same domain.

### Using curl to verify an endpoint

Once you find a candidate endpoint, verify with curl:

```bash
curl -s 'https://example.com/api/products?page=1&limit=20' \
  -H 'Accept: application/json' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)' \
  | python3 -m json.tool | head -50
```

Check:
- Does it return JSON without browser context?
- Does it require cookies or auth tokens?
- Does pagination work by incrementing a parameter?
- What's the rate limit? (check `X-RateLimit-*` headers)
- **Test the page size limit** — many APIs accept much larger `limit` or
  `per_page` values than the frontend uses (e.g., 500 or 1000 instead of
  20). Fewer requests means less rate limiting risk. Try increasing the
  limit parameter in steps: 50 → 100 → 250 → 500. Stop when the API
  errors or caps the response.

### Gotcha: URL fragments are never sent to the server

State encoded in the URL fragment (everything after `#`, e.g.
`#filter=brand:acme&page=2`) is invisible to the server and to any non-JS
HTTP client. The browser's JS reads `window.location.hash`, parses it, and
turns it into query/body parameters on the real API call. `curl`/`httpx`
will fetch the page and get the *unfiltered* result: a silent-failure trap
where you scrape the wrong data while believing the filter applied.

To handle it: toggle one filter in the browser, diff the resulting API
request, and map the fragment values to the API's real parameters. Then
call the endpoint (or the SSR data route) with those parameters directly.
Never try to "send" the fragment.

---

## 2. Embed and Syndication Endpoints

The unauthenticated API a site exposes so that *other people's websites* can
render its content. When a tweet is pasted into a blog post, the resulting
`<blockquote>` plus widget script has to fetch that tweet's text, author,
and timestamp from somewhere. That somewhere is
`cdn.syndication.twimg.com/tweet-result`, and it returns clean JSON to
anyone who asks.

Generalize the move: **find the path the site built for third-party
consumption, and use it instead of the path it built for its own users.**

### Why it is reliably softer than the main site

Not an oversight, a structural consequence of what an embed has to do:

- **It cannot require auth.** The point is that a logged-out stranger on
  someone else's blog sees the content. A session check would break the
  product.
- **It cannot require the site's own JS runtime.** It is called from a
  foreign origin, so it needs permissive CORS and a stable contract.
- **It usually lives on a different host** (`cdn.syndication.twimg.com`,
  not `x.com`). Different host often means different WAF config, different
  bot rules, and a different rate-limit budget from the main app. A UA or
  Cloudflare blockade on the main domain can be entirely irrelevant here.
- **The contract is frozen.** Third parties depend on the response shape,
  so it changes far more slowly than internal APIs and survives redesigns:
  the team rebuilding the feed does not get to break every embed on the
  internet.
- **The payload is already denormalized.** Embeds need one round trip, so
  you tend to get the whole object rather than a fragment to stitch
  together from three calls.

That combination (no auth, stable, one request) ranks an embed endpoint
above almost everything else in this file when it fits the job.

### How to find one

1. **Look for the embed or share affordance in the product UI.** Post menu
   → "Embed this post" hands you an iframe URL or a script tag. That URL is
   the endpoint, or one hop from it.
2. **Load that snippet on a scratch HTML page and watch the network tab.**
   The widget script fires the real data request. Use
   `read_network_requests` and note the host, params, and any token.
3. **Check the oEmbed standard first**, it costs one request:
   ```bash
   # Sites advertise oEmbed in the page head
   curl -s "$URL" | grep -i 'json+oembed'
   # → <link rel="alternate" type="application/json+oembed" href="...">
   ```
4. **Replay it with curl, logged out, cookies cleared.** This step is not
   optional: plenty of "open" endpoints only worked because the browser
   carried a session.
5. **Poke the params.** In `?id=<id>&token=a`, a token that accepts a
   single junk character is not a token, it is a cache-buster or a
   vestigial anti-CSRF field. Drop params one at a time to find the true
   minimum.

### Known endpoints

| Site | Endpoint |
|------|----------|
| X / Twitter | `cdn.syndication.twimg.com/tweet-result?id=<id>&token=a` |
| YouTube | `youtube.com/oembed?url=<url>&format=json` |
| Vimeo | `vimeo.com/api/oembed.json?url=<url>` |
| Bluesky | `embed.bsky.app/oembed?url=<url>` |
| SoundCloud | `soundcloud.com/oembed?format=json&url=<url>` |
| Spotify | `open.spotify.com/oembed?url=<url>` |
| Flickr | `flickr.com/services/oembed/?format=json&url=<url>` |
| TikTok | `tiktok.com/oembed?url=<url>` |
| WordPress | `/wp-json/oembed/1.0/embed?url=<url>` |
| Reddit | `.json` suffix on any permalink (requires a real UA) |

```python
import httpx

# One request, no auth, no headers, full object back
r = httpx.get(
    "https://cdn.syndication.twimg.com/tweet-result",
    params={"id": tweet_id, "token": "a"},
)
tweet = r.json()
tweet["text"], tweet["user"]["screen_name"], tweet["created_at"]
```

### Hard limits: retrieval, not discovery

Two constraints decide whether this pattern helps at all:

- **Keyed by an ID you must already have.** Embed endpoints answer "render
  *this* item", never "list items". They solve retrieval, not discovery. If
  the hard part of the job is finding which items exist, and the listing
  surface is session-gated, an open embed endpoint does not help no matter
  how open it is. Pair it with a separate discovery source (sitemap, RSS,
  search, a public index page) that yields IDs.
- **Public visibility only.** You get exactly what a logged-out stranger
  would get. Nothing session-gated leaks through.

Beyond that: undocumented means unversioned, so it can vanish without a
deprecation notice (Instagram's oEmbed went from open to app-token-required
this way). `robots.txt` and ToS still apply the same as any other route.
And the rate-limit budget is often thinner than it looks, because the host
is a CDN sized for cached embed traffic rather than for someone iterating a
list, so pace accordingly.

---

## 3. Mobile App API Discovery (APK Decompilation)

When the browser network tab and the JS bundles do not reveal the full
API, the site's mobile app usually does. A native Android app ships a
near-complete map of the backend: hosts, route names, request shapes, and
the domain vocabulary the company uses internally.

**Use the APK to MAP the API, not necessarily to call it.** This is the
key judgment. Decompiled mobile endpoints are frequently not callable from
a plain HTTP client (see the caveat below). The high-value outcome is
usually a faster, better-informed *web* investigation, not a working
mobile-API scraper.

### Tools and steps

1. **Get the APK.** Download from a mirror (APKPure, APKMirror) or pull
   from a device you control: `adb shell pm path <pkg>` then `adb pull`.
   Split APKs (`.xapk`/`.apks`) need merging first (APKEditor, `apkeep`).
2. **Decode resources:** `apktool d app.apk`. Check
   `res/values/strings.xml` and `res/xml/network_security_config.xml` for
   base URLs, environment hosts, and pinned domains.
3. **Decompile to Java:** `jadx -d out app.apk` (or `jadx-gui`), then grep
   the output.
4. **Extract the API surface** by searching decompiled sources and raw
   strings for:
   - Hosts: `https://`, including non-production hosts (staging,
     integration, internal cloud subdomains) that hint at the API layout.
   - Routes: `/api`, `/v1`, `/v2`, and Retrofit annotations (`@GET`,
     `@POST`, `@Query`, `@Path`). Retrofit interfaces hand you exact route
     names, path params, and query params as a de facto API spec.
   - Auth/headers: `Authorization`, `X-Api-Key`, `X-Client-*`,
     `X-App-Version`, OAuth client IDs, any baked-in keys.

```bash
# Decompile and dump candidate hosts + endpoints
jadx -d out app.apk
grep -rhoE 'https?://[a-zA-Z0-9./_-]+' out/sources | sort -u > hosts.txt
grep -rhoE '"/(api|v[0-9]|[a-z]+/v[0-9])[a-zA-Z0-9./{}_-]+"' out/sources \
  | sort -u > routes.txt
```

### Map mobile routes to web routes

Mobile and web frontends usually talk to the same conceptual services with
parallel naming, so a decompiled mobile route often has a recognizable web
counterpart, for example mobile `GET /mobile/v3/products/search` maps to
web `GET /api/products/search`. The APK also reveals the company's internal
names for each product area (the path segment that groups a feature's
endpoints), and those same names tend to appear in the web JS. Once you
know that vocabulary the web bundles become much faster to read: you know
what to grep for and what each endpoint does. Use the APK to learn the
route names, then find the matching web endpoint that already works with an
anonymous browser session.

### Caveat: mobile endpoints are often not directly scrapeable

A decompiled endpoint is rarely usable from a plain anonymous HTTP client.
Expect one or more of:

- **App session bootstrap:** the app obtains an anonymous session/token on
  launch before any data call works, so a cold request from a fresh client
  often returns 401/403/404.
- **Device/app headers:** mandatory `X-App-Version`, `X-Device-Id`,
  `User-Agent`, and locale headers, copied verbatim from the app.
- **Request signing or attestation:** HMAC-signed requests, per-request
  nonces, or Google Play Integrity / SafetyNet. True device attestation
  cannot be forged from Python.
- **TLS fingerprinting:** stock clients get flagged, so you need
  `curl_cffi` impersonation.

Reproducing the full app bootstrap is brittle and intrusive. For polite,
scheduled scraping, the public web source (SSR HTML, `__NEXT_DATA__`, or a
non-disallowed web API) is usually simpler, more stable, and safer. Treat
the mobile API as a map and a last-resort source, not the default.

To confirm what a mobile endpoint really needs, capture live app traffic
with mitmproxy or Burp (modern apps pin certs: use a rooted emulator plus
Frida SSL-unpinning, or `objection patchapk`). Replicate one captured
request exactly, get a `200`, then strip headers one at a time to find the
minimal required set.

---

## 4. Server-Rendered JSON Blobs

Many frameworks embed the full page data as JSON in the initial HTML.
This is often the easiest approach — one HTTP request, all data included.

### Framework-specific patterns

| Framework | Where to look | Extraction |
|-----------|--------------|------------|
| **Next.js** | `<script id="__NEXT_DATA__" type="application/json">` | `json.loads(script.string)["props"]["pageProps"]` |
| **Nuxt.js** | `<script>window.__NUXT__=` or `<script id="__NUXT_DATA__">` | Parse the JS assignment or JSON |
| **Remix** | `<script>window.__remixContext =` | Parse the JS object |
| **Gatsby** | `<script>/*! gatsby-page-data */` or inline `pageContext` | Extract from script content |
| **SvelteKit** | `<script type="application/json" data-sveltekit-fetched>` | `json.loads(script.string)` |
| **Angular Universal** | `<script id="serverApp-state" type="application/json">` | `json.loads(script.string)` |
| **Vue SSR** | `<script>window.__INITIAL_STATE__=` | Parse the JS assignment |
| **Astro** | `<script type="application/json" data-astro-*>` | `json.loads(script.string)` |

### React Server Components (RSC) payloads

Next.js App Router sites (13.4+) do NOT use `__NEXT_DATA__`. Instead they
stream React Server Components as a custom line-based format. You'll
recognise RSC by:

- Network requests with `?_rsc=` query parameter
- `Content-Type: text/x-component` in response headers
- Response body with lines like `0:["$","div",null,{"children":...}]`

RSC payloads contain the full page data but in a nested, non-trivial format.
During **discovery**, check if the same data is available more cleanly
(JSON-LD, `<script>` tags, or an API). Only parse RSC directly when no
better source exists.

#### When to use RSC parsing

RSC is the right choice when:
- No JSON-LD or structured data in the HTML
- No API endpoints found via network inspection
- The site is a Next.js App Router app (RSC requests visible in network)
- The RSC payload contains data not available elsewhere (e.g., aggregated
  counts, metadata, filters)

#### RSC format overview

Each line in an RSC response is: `ID:TYPE_OR_JSON`

```
0:["$","$L1",null,{"children":["$","div",null,...]}]
1:["$","$L2",null,{"data":{"products":[...]}}]
2:"$Sreact.suspense"
3:["$","ul",null,{"children":[["$","li",...]]}]
```

- Lines starting with a number + colon contain data or component trees
- JSON arrays/objects are embedded within each line
- Data you want is typically nested inside arrays with `"children"` or
  `"data"` keys

#### Extraction pattern

```python
import json
import re

import httpx


def fetch_rsc(url: str, client: httpx.Client) -> str:
    """Fetch the RSC payload for a URL."""
    resp = client.get(
        url,
        params={"_rsc": "1"},  # trigger RSC response
        headers={
            "RSC": "1",  # required header for RSC
            "Next-Router-State-Tree": "",
            **HEADERS,
        },
    )
    resp.raise_for_status()
    return resp.text


def parse_rsc_payload(rsc_text: str) -> list[dict]:
    """Extract JSON objects from RSC line protocol.
    
    RSC lines look like:
        0:["$","div",null,{...}]
        1:{"key":"value"}
        2:"plain string"
    
    We extract all parseable JSON from each line and collect
    any dicts/lists that look like data (not React component trees).
    """
    results = []

    for line in rsc_text.splitlines():
        # Strip the line ID prefix: "0:", "1a:", "2f:" etc.
        match = re.match(r'^[0-9a-f]+:', line)
        if not match:
            continue
        payload = line[match.end():]

        try:
            parsed = json.loads(payload)
        except (json.JSONDecodeError, TypeError):
            continue

        # Collect interesting data — skip plain strings and React markers
        if isinstance(parsed, dict):
            results.append(parsed)
        elif isinstance(parsed, list):
            # Walk the RSC array to find nested data objects
            _extract_data_from_rsc_tree(parsed, results)

    return results


def _extract_data_from_rsc_tree(node, results: list):
    """Recursively walk an RSC tree and extract data-like dicts.
    
    RSC arrays follow the pattern: ["$", "tag", key, props_dict]
    Data objects are typically inside props dicts under keys like
    "data", "items", "results", "children", "pageProps".
    """
    if isinstance(node, dict):
        # If it has data-like keys, collect it
        data_keys = {"data", "items", "results", "products", "listings",
                     "pageProps", "initialData", "props"}
        if data_keys & set(node.keys()):
            results.append(node)
        # Also recurse into all dict values
        for v in node.values():
            if isinstance(v, (dict, list)):
                _extract_data_from_rsc_tree(v, results)
    elif isinstance(node, list):
        for item in node:
            if isinstance(item, (dict, list)):
                _extract_data_from_rsc_tree(item, results)
```

#### Tips for RSC discovery

- **Compare RSC payload vs HTML source**: sometimes the HTML already
  contains the data as JSON-LD or `<script>` tags (server-rendered for
  SEO), making RSC parsing unnecessary.
- **Multiple RSC requests**: App Router may split data across several RSC
  fetches (shell, page data, suspended chunks). Check all `_rsc` requests.
- **The `RSC: 1` header** is required — without it, the server returns
  full HTML instead of the RSC payload.
- **Pagination via RSC**: when paginating client-side, the browser fetches
  only the RSC diff (not full HTML). This can be much smaller and faster
  to parse than the full page.

### Framework detection cheat sheet

```python
import json, re
from bs4 import BeautifulSoup

html = httpx.get(url).text
soup = BeautifulSoup(html, "html.parser")

# Next.js
tag = soup.find("script", id="__NEXT_DATA__")
if tag:
    data = json.loads(tag.string)
    page_data = data["props"]["pageProps"]

# Nuxt
tag = soup.find("script", string=re.compile(r"window\.__NUXT__"))
if tag:
    # Extract JSON from: window.__NUXT__={...}
    match = re.search(r'window\.__NUXT__\s*=\s*(.+?);\s*$', tag.string, re.DOTALL)
    if match:
        data = json.loads(match.group(1))

# Generic initial state
for tag in soup.find_all("script"):
    if tag.string and "window.__INITIAL_STATE__" in tag.string:
        match = re.search(r'window\.__INITIAL_STATE__\s*=\s*(.+?);\s*$',
                          tag.string, re.DOTALL)
        if match:
            data = json.loads(match.group(1))
```

---

## 5. CMS and Platform APIs

If the site runs on a known platform, there's almost certainly a REST API.

### WordPress

```bash
# Check if it's WordPress
curl -s https://example.com/wp-json/ | python3 -m json.tool

# List posts (public by default)
curl -s 'https://example.com/wp-json/wp/v2/posts?per_page=20&page=1'

# Other endpoints
/wp-json/wp/v2/pages
/wp-json/wp/v2/categories
/wp-json/wp/v2/tags
/wp-json/wp/v2/users        # sometimes restricted
/wp-json/wp/v2/media
/wp-json/wp/v2/comments
```

Detection: look for `<link rel="https://api.w.org/"` in HTML head, or
`/wp-content/` / `/wp-includes/` in page source.

### Shopify

```bash
# Product listing (JSON)
curl -s 'https://store.example.com/products.json?limit=250&page=1'

# Collection products
curl -s 'https://store.example.com/collections/all/products.json'

# Single product
curl -s 'https://store.example.com/products/product-handle.json'

# Storefront API (GraphQL, may need token)
curl -s 'https://store.example.com/api/2024-01/graphql.json' \
  -H 'Content-Type: application/json' \
  -H 'X-Shopify-Storefront-Access-Token: TOKEN' \
  -d '{"query": "{ products(first: 10) { edges { node { title } } } }"}'
```

Detection: `Shopify.theme`, `cdn.shopify.com`, `myshopify.com`.

### Drupal (JSON:API)

```bash
curl -s 'https://example.com/jsonapi/node/article?page[limit]=20'
```

Detection: `<meta name="Generator" content="Drupal"`, `/sites/default/files/`.

### Ghost

```bash
curl -s 'https://example.com/ghost/api/content/posts/?key=API_KEY&limit=20'
```

Detection: `<meta name="generator" content="Ghost"`.

### Webflow

```bash
# Webflow sites expose collection data via their API
# Look for data-w-id attributes and /api/v1/ endpoints
```

Detection: `webflow.js`, `data-wf-site`, `data-wf-page`.

### Squarespace

```bash
# Append ?format=json to most URLs
curl -s 'https://example.com/blog?format=json'
```

Detection: `squarespace.com`, `static.squarespace.com`.

### Wix

```bash
# Wix sites use a data API internally
# Look for /_api/ endpoints in XHR requests
# Common: /_api/communities-blog-node-api/
```

Detection: `wix.com`, `parastorage.com`, `static.wixstatic.com`.

---

## 6. GraphQL Endpoints

### Detection

Common GraphQL endpoint URLs:
- `/graphql`
- `/gql`
- `/api/graphql`
- `/v1/graphql`
- `/__graphql`

Check for:
- Requests with `Content-Type: application/json` and a `query` field in body
- The string `__typename` in responses
- Relay-style `edges` / `node` / `pageInfo` patterns

### Introspection query

```bash
curl -s 'https://example.com/graphql' \
  -H 'Content-Type: application/json' \
  -d '{"query": "{ __schema { queryType { name } types { name fields { name type { name } } } } }"}'
```

Many production endpoints disable introspection, but it's worth trying.
If it works, you get the full schema — which makes building queries trivial.

### Query building without introspection

If introspection is disabled, observe the queries the frontend makes
(via network tab), then adapt them. The frontend's queries are typically
well-tested and paginated.

---

## 7. Structured Data in HTML

Many sites embed structured data for SEO. This is clean, reliable, and
rarely changes.

### JSON-LD

```python
import json
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, "html.parser")
for tag in soup.find_all("script", type="application/ld+json"):
    data = json.loads(tag.string)
    # Common types: Product, Article, Event, Recipe, Organization
    print(data.get("@type"), data)
```

### Microdata / RDFa

Less convenient to parse but still structured. Use `extruct` library:

```python
import extruct

data = extruct.extract(html, syntaxes=["json-ld", "microdata", "rdfa", "opengraph"])
```

---

## 8. Data Attributes

Modern frameworks often attach data to DOM elements via `data-` attributes.
These are typically more stable than class names.

### What to look for

```python
# Find elements with data attributes
for elem in soup.find_all(attrs={"data-product-id": True}):
    print(elem["data-product-id"], elem.get("data-price"))

# Common patterns
# data-id, data-item-id, data-product-id
# data-price, data-currency
# data-category, data-type
# data-url, data-href, data-src
# data-testid (React Testing Library — surprisingly stable)
# data-cy (Cypress test IDs — also stable)
```

---

## 9. Stable CSS Selectors

Last resort for DOM-based scraping. Prefer semantic HTML elements
over class names.

### Good selectors (stable across redesigns)

```css
article                  /* semantic HTML5 */
article h2 a            /* link inside article heading */
table tbody tr td        /* table data */
li                       /* list items */
time[datetime]           /* dates with machine-readable value */
[itemprop="name"]        /* microdata attributes */
nav a                    /* navigation links */
main section             /* main content sections */
figure img               /* images with semantic wrapper */
```

### Bad selectors (will break)

```css
.css-1a2b3c             /* CSS-in-JS generated */
.MuiButton-root         /* Material UI internals */
.sc-bdVTJa              /* styled-components hash */
.tw-flex.tw-gap-4       /* Tailwind utility soup */
._3xk2z                 /* minified class names */
div > div > div > span  /* fragile nesting */
```

### Resilience tips

- Anchor on `<table>`, `<article>`, `<section>` when possible
- Use attribute selectors: `[role="listitem"]`, `[aria-label="Price"]`
- Combine tag + attribute: `li[data-testid]`
- Avoid nth-child selectors — position changes break them
- Test selector matches a consistent count across multiple pages

---

## 10. Discovery Report Template

After running discovery, produce a brief report for the user:

```markdown
## Discovery Report: [site name]

**Target URL:** https://example.com/products
**Date:** 2024-01-15

### Findings

| # | Method | Endpoint/Selector | Auth needed? | Paginated? | Max page size | Notes |
|---|--------|-------------------|-------------|-----------|--------------|-------|
| 1 | REST API | /api/v1/products?page={n} | No | Yes (page param) | 250 (tested) | Returns JSON, default 20 items/page |
| 2 | __NEXT_DATA__ | Embedded in HTML | No | No (single page) | N/A | Full product list on first load |
| 3 | CSS selectors | article.product-card | No | No | N/A | 20 items per page load |

### Recommendation

**Use approach #1 (REST API)** because:
- Clean JSON response, no HTML parsing needed
- Built-in pagination
- No authentication required
- Likely the most stable (API contracts change less than HTML)

### Caveats
- robots.txt allows /api/ paths
- No visible rate limit headers (recommend 1-2 req/s)
- TOS does not explicitly prohibit scraping
```
