# Scraping Patterns Reference

Python script templates and patterns for the scraping phase.
All scripts use `uv` inline metadata for dependency management.

## Table of Contents

1. [Script Template](#1-script-template)
2. [HTTP Client Ladder](#2-http-client-ladder)
3. [Output Handlers](#3-output-handlers)
4. [Pagination Patterns](#4-pagination-patterns)
5. [Playwright Stealth](#5-playwright-stealth)
6. [Error Handling and Retry](#6-error-handling-and-retry)
7. [Rate Limiting](#7-rate-limiting)
8. [Common Extraction Patterns](#8-common-extraction-patterns)

---

## 1. Script Template

Every generated script should follow this structure. Use `uv` script
metadata so the user can run it with `uv run scrape.py` without
managing a virtual environment.

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "httpx",
#     "selectolax",
# ]
# ///
"""
Scraper: [Site Name] — [what it extracts]
Discovery: [method used, e.g., REST API at /api/v1/products]

Usage:
    uv run scrape.py --output data/products.jsonl
    uv run scrape.py --output data/products.csv --format csv
    uv run scrape.py --connection "postgresql://user:pass@host/db?table=products"
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

# ── Configuration ──────────────────────────────────────────────
BASE_URL = "https://example.com"
API_URL = f"{BASE_URL}/api/v1/products"
# Default: identify the scraper and give the site's ops team a contact.
# Swap in the browser UA below only when the job is a third-party site that
# blocks unknown agents.
USER_AGENT = "AcmeDataSync/1.0 (+https://acme.example/contact)"
# USER_AGENT = (
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
#     "AppleWebKit/537.36 (KHTML, like Gecko) "
#     "Chrome/131.0.0.0 Safari/537.36"
# )
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}
REQUEST_DELAY = 1.5  # seconds between requests
PAGE_SIZE = 20  # Try increasing during discovery — many APIs accept 100-500+

# ── Logging ────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", "-o", type=Path, help="Output file path")
    p.add_argument(
        "--format", "-f",
        choices=["jsonl", "csv", "parquet"],
        default="jsonl",
        help="Output format (default: jsonl)",
    )
    p.add_argument("--connection", "-c", help="DB connection string")
    p.add_argument("--page-limit", type=int, default=0, help="Max pages (0=all)")
    p.add_argument("--date-range", help="Date range: YYYY-MM-DD:YYYY-MM-DD")
    return p.parse_args()


def fetch_page(client: httpx.Client, page: int) -> list[dict]:
    """Fetch a single page of results. Adapt to your endpoint."""
    resp = client.get(API_URL, params={"page": page, "limit": PAGE_SIZE})
    resp.raise_for_status()
    data = resp.json()
    return data.get("items", data.get("results", data.get("data", [])))


def transform(raw: dict) -> dict:
    """Normalize a single raw record. Customize per site."""
    return {
        "id": raw.get("id"),
        "title": raw.get("title", "").strip(),
        "url": raw.get("url"),
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        # add more fields as needed
    }


def scrape(args: argparse.Namespace) -> list[dict]:
    records = []
    page = 1
    with httpx.Client(headers=HEADERS, timeout=30, follow_redirects=True) as client:
        while True:
            log.info("Fetching page %d", page)
            items = fetch_page(client, page)
            if not items:
                log.info("No more items, stopping at page %d", page)
                break
            for item in items:
                records.append(transform(item))
            log.info("Got %d items (total: %d)", len(items), len(records))
            if args.page_limit and page >= args.page_limit:
                log.info("Reached page limit %d", args.page_limit)
                break
            page += 1
            time.sleep(REQUEST_DELAY)
    return records


def write_output(records: list[dict], args: argparse.Namespace) -> None:
    if args.connection:
        write_to_db(records, args.connection)
        return

    output = args.output or Path(f"output.{args.format}")
    output.parent.mkdir(parents=True, exist_ok=True)

    if args.format == "jsonl":
        with open(output, "w") as f:
            for r in records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    elif args.format == "csv":
        import csv
        if not records:
            return
        with open(output, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=records[0].keys())
            w.writeheader()
            w.writerows(records)
    elif args.format == "parquet":
        import pyarrow as pa
        import pyarrow.parquet as pq
        table = pa.Table.from_pylist(records)
        pq.write_table(table, output)

    log.info("Wrote %d records to %s", len(records), output)


def write_to_db(records: list[dict], connection: str) -> None:
    """Write records to a database. Supports PostgreSQL connection strings."""
    import duckdb
    db = duckdb.connect()
    db.execute("INSTALL postgres; LOAD postgres;")
    # Use DuckDB to write to postgres via its postgres extension,
    # or adapt to use psycopg/sqlalchemy as preferred
    import pyarrow as pa
    table = pa.Table.from_pylist(records)
    db.register("records", table)
    # Adapt table name from connection string query params
    from urllib.parse import urlparse, parse_qs
    parsed = urlparse(connection)
    table_name = parse_qs(parsed.query).get("table", ["scraped_data"])[0]
    clean_conn = connection.split("?")[0]
    db.execute(f"ATTACH '{clean_conn}' AS pg (TYPE postgres)")
    db.execute(f"CREATE TABLE IF NOT EXISTS pg.{table_name} AS SELECT * FROM records WHERE false")
    db.execute(f"INSERT INTO pg.{table_name} SELECT * FROM records")
    log.info("Wrote %d records to %s.%s", len(records), clean_conn, table_name)


def main() -> int:
    args = parse_args()
    try:
        records = scrape(args)
        if not records:
            log.warning("No records scraped")
            return 1
        write_output(records, args)
        return 0
    except httpx.HTTPStatusError as e:
        log.error("HTTP error: %s", e)
        return 2
    except Exception as e:
        log.error("Fatal error: %s", e, exc_info=True)
        return 2


if __name__ == "__main__":
    sys.exit(main())
```

---

## 2. HTTP Client Ladder

Try these in order. Move to the next only if the previous one gets blocked.

### Level 1: httpx (default)

```python
# /// script
# dependencies = ["httpx"]
# ///
import httpx

with httpx.Client(
    headers=HEADERS,
    timeout=30,
    follow_redirects=True,
    http2=True,  # enable HTTP/2
) as client:
    resp = client.get(url)
```

### Level 2: curl_cffi (TLS fingerprint bypass)

When sites block based on TLS fingerprint (JA3/JA4). curl_cffi
impersonates real browser TLS fingerprints.

```python
# /// script
# dependencies = ["curl_cffi"]
# ///
from curl_cffi import requests as curl_requests

resp = curl_requests.get(
    url,
    headers=HEADERS,
    impersonate="chrome131",  # match a real browser
    timeout=30,
)
```

Available impersonation targets (use recent ones):
- `"chrome131"`, `"chrome124"`, `"chrome120"`
- `"safari18_0"`, `"safari17_5"`
- `"edge131"`

### Level 3: Playwright (full browser, last resort)

See [Playwright Stealth](#5-playwright-stealth) section below.

---

## 3. Output Handlers

### JSONL (default, recommended)

Append-friendly, one JSON object per line. Best for streaming and
incremental scraping.

```python
with open(output, "w") as f:
    for record in records:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
```

### CSV

```python
import csv

with open(output, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=records[0].keys())
    writer.writeheader()
    writer.writerows(records)
```

### Parquet

Best for analytical workloads and DuckDB/MotherDuck ingestion.

```python
# /// script
# dependencies = ["pyarrow"]
# ///
import pyarrow as pa
import pyarrow.parquet as pq

table = pa.Table.from_pylist(records)
pq.write_table(table, output, compression="snappy")
```

### PostgreSQL via DuckDB

```python
# /// script
# dependencies = ["duckdb", "pyarrow"]
# ///
import duckdb

db = duckdb.connect()
db.install_extension("postgres")
db.load_extension("postgres")
table = pa.Table.from_pylist(records)
db.register("records", table)
db.execute(f"ATTACH '{conn_string}' AS pg (TYPE postgres)")
db.execute(f"INSERT INTO pg.{table_name} SELECT * FROM records")
```

---

## 4. Pagination Patterns

### Probe the maximum page size first

Before paginating, test whether the API accepts larger page sizes than
the frontend defaults. Many APIs let you request 250–500 items per page
even if the UI only shows 20. This dramatically reduces the number of
requests and lowers the chance of hitting rate limits.

```python
# During discovery, probe the max page size:
for size in [50, 100, 250, 500]:
    resp = client.get(url, params={"limit": size, "page": 1})
    if resp.status_code == 200 and len(resp.json().get("items", [])) > 0:
        log.info("Page size %d works (%d items)", size, len(resp.json()["items"]))
    else:
        log.info("Page size %d rejected or capped", size)
        break
```

### Page-number based

```python
page = 1
while True:
    data = client.get(url, params={"page": page, "per_page": 20}).json()
    items = data["items"]
    if not items:
        break
    yield from items
    page += 1
    time.sleep(REQUEST_DELAY)
```

### Cursor-based

```python
cursor = None
while True:
    params = {"limit": 20}
    if cursor:
        params["cursor"] = cursor
    data = client.get(url, params=params).json()
    yield from data["items"]
    cursor = data.get("next_cursor")
    if not cursor:
        break
    time.sleep(REQUEST_DELAY)
```

### Offset-based

```python
offset = 0
limit = 20
while True:
    data = client.get(url, params={"offset": offset, "limit": limit}).json()
    items = data["results"]
    if not items:
        break
    yield from items
    offset += limit
    time.sleep(REQUEST_DELAY)
```

### Next-URL based

```python
next_url = initial_url
while next_url:
    data = client.get(next_url).json()
    yield from data["results"]
    next_url = data.get("next")  # full URL to next page
    time.sleep(REQUEST_DELAY)
```

### Infinite scroll / load-more (JS required)

If all HTTP approaches fail for pagination, use Playwright:

```python
async def scroll_and_collect(page):
    previous_height = 0
    while True:
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)
        current_height = await page.evaluate("document.body.scrollHeight")
        if current_height == previous_height:
            break
        previous_height = current_height
```

---

## 5. Playwright Stealth

Only use when httpx and curl_cffi both fail. Apply ALL of these
anti-detection measures.

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "playwright",
# ]
# ///
"""Run `playwright install chromium` before first use."""

from playwright.sync_api import sync_playwright

def create_stealth_browser():
    pw = sync_playwright().start()
    browser = pw.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
            "--disable-infobars",
            "--no-first-run",
            "--no-default-browser-check",
        ],
    )
    context = browser.new_context(
        user_agent=USER_AGENT,
        viewport={"width": 1920, "height": 1080},
        locale="en-US",
        timezone_id="America/New_York",
        # Realistic screen params
        screen={"width": 1920, "height": 1080},
        color_scheme="light",
    )

    # Remove automation indicators
    context.add_init_script("""
        // Remove webdriver flag
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

        // Fix plugins array (headless has empty plugins)
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });

        // Fix languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });

        // Fix permissions query
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) =>
            parameters.name === 'notifications'
                ? Promise.resolve({ state: Notification.permission })
                : originalQuery(parameters);

        // Fix chrome object
        window.chrome = { runtime: {} };

        // Fix connection info
        Object.defineProperty(navigator, 'connection', {
            get: () => ({ effectiveType: '4g', rtt: 50, downlink: 10, saveData: false }),
        });

        // Hide headless renderer
        Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
        Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
    """)

    page = context.new_page()
    return pw, browser, page
```

### Anti-detection checklist

When using Playwright, verify ALL of these:

- [ ] `navigator.webdriver` returns `undefined` (not `true`)
- [ ] `navigator.plugins` has entries (not empty)
- [ ] `navigator.languages` is set (not empty)
- [ ] `window.chrome` object exists
- [ ] User-Agent matches a real, recent browser (derive it by stripping the
      `HeadlessChrome` marker from the browser's own UA, don't hardcode one that
      may mismatch the platform/TLS fingerprint)
- [ ] Viewport is a realistic resolution (1920x1080, not 800x600)
- [ ] `--disable-blink-features=AutomationControlled` is set
- [ ] Real-looking mouse movements and delays between actions
- [ ] Timezone and locale are set consistently
- [ ] `hardwareConcurrency` and `deviceMemory` return reasonable values

### Cloudflare "managed challenge" (headless 403 "Just a moment...")

**Ask for an allowlist rule before trying any of this.** On an
owner-authorized job, a WAF skip rule on your source IP or a shared secret
header takes the site's ops team a minute, needs no browser at all, and does
not break when Cloudflare updates its detection. Everything below is for
when nobody can grant that.

Cloudflare's managed/JS challenge blocks the default headless fingerprint
outright: HTTP `403` with page title `Just a moment...` and body markers like
`challenge-platform`, `cf_chl`, or a `cf-mitigated` response header. Field-tested
lessons:

- **Switching the browser *channel* does not help.** Headless Chromium, headless
  Chrome, and headless Edge (`channel="msedge"`) are all blocked the same way.
  The signal Cloudflare keys on is *headless*, not the brand — so "try it with
  Edge" is a dead end while the browser stays headless.
- **Two cheap fixes, effective only *together*.** A real (non-`HeadlessChrome`)
  User-Agent AND `--disable-blink-features=AutomationControlled`. In a controlled
  test, each one *alone* still returned 403; only the combination passed, stably.
  Test the combination, never either half in isolation.
- **Derive the UA, don't hardcode it.** Read the browser's own UA and strip the
  headless marker so the Chrome version and platform stay consistent with the
  real TLS/JA3 fingerprint. A hardcoded UA naming the wrong platform is itself a
  detectable mismatch.

```python
def stealth_user_agent(browser) -> str:
    """Real UA with the headless marker removed (version/platform-consistent)."""
    ctx = browser.new_context()
    try:
        ua = ctx.new_page().evaluate("navigator.userAgent")
    finally:
        ctx.close()
    return ua.replace("HeadlessChrome", "Chrome")
```

**Diagnose with a controlled matrix — and rule out IP reputation.** Before
concluding a tweak "fixed" it, run the same request under each of: plain headless
/ UA-only / flag-only / both / headed. A prior *successful* solve (e.g. one headed
run) can warm your IP's Cloudflare reputation so later headless requests pass for
reasons unrelated to your change; re-run plain-headless to confirm it still fails.

```python
CF_MARKERS = ("just a moment", "challenge-platform", "cf_chl",
              "enable javascript and cookies", "cf-mitigated")

def is_challenged(title: str, body: str) -> bool:
    hay = (title + " " + body).lower()
    return any(m in hay for m in CF_MARKERS)
```

**Escalation ladder** if UA + flag is not enough:

1. Headed browser under a virtual display (`xvfb-run ...`) on servers — a real,
   non-headless browser solves the JS challenge itself.
2. A residential IP / proxy (datacenter ranges carry low reputation).
3. A dedicated challenge-solver service (last resort).

**Authenticated personal sessions.** A stored `cf_clearance` cookie is bound to
the IP + UA + TLS that solved the challenge, so it usually will NOT transfer from
the machine where you captured the session to the host that runs the scraper. A
real browser re-solves the challenge fresh each run and so does not depend on that
cookie carrying over. Keep the site's *auth/subscriber* cookies (which unlock
paywalled content) conceptually separate from Cloudflare clearance — the former
transfer fine; the latter generally don't.

### Playwright with human-like behavior

```python
import random

async def human_like_delay():
    """Random delay between 0.5-2.5 seconds."""
    await asyncio.sleep(random.uniform(0.5, 2.5))

async def human_like_scroll(page):
    """Scroll with varying speed like a human."""
    for _ in range(random.randint(2, 5)):
        await page.mouse.wheel(0, random.randint(200, 600))
        await asyncio.sleep(random.uniform(0.3, 1.0))
```

---

## 6. Error Handling and Retry

```python
from time import sleep

MAX_RETRIES = 3
RETRY_BACKOFF = [2, 5, 15]  # seconds


def fetch_with_retry(client: httpx.Client, url: str, **kwargs) -> httpx.Response:
    for attempt in range(MAX_RETRIES):
        try:
            resp = client.get(url, **kwargs)
            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", RETRY_BACKOFF[attempt]))
                log.warning("Rate limited, sleeping %ds", retry_after)
                sleep(retry_after)
                continue
            resp.raise_for_status()
            return resp
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500 and attempt < MAX_RETRIES - 1:
                log.warning("Server error %d, retry in %ds",
                            e.response.status_code, RETRY_BACKOFF[attempt])
                sleep(RETRY_BACKOFF[attempt])
                continue
            raise
        except (httpx.ConnectError, httpx.ReadTimeout) as e:
            if attempt < MAX_RETRIES - 1:
                log.warning("Connection error: %s, retry in %ds",
                            e, RETRY_BACKOFF[attempt])
                sleep(RETRY_BACKOFF[attempt])
                continue
            raise
    raise RuntimeError(f"Failed after {MAX_RETRIES} retries: {url}")
```

---

## 7. Rate Limiting

### Simple sleep-based (default)

```python
REQUEST_DELAY = 1.5  # seconds
time.sleep(REQUEST_DELAY)
```

### Adaptive rate limiting

```python
class RateLimiter:
    def __init__(self, requests_per_second: float = 1.0):
        self.min_interval = 1.0 / requests_per_second
        self.last_request = 0.0

    def wait(self):
        elapsed = time.time() - self.last_request
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request = time.time()

limiter = RateLimiter(requests_per_second=0.5)  # 1 req every 2 seconds
```

### Respect Retry-After headers

```python
if resp.status_code == 429:
    wait = int(resp.headers.get("Retry-After", 60))
    log.warning("Rate limited. Waiting %d seconds.", wait)
    time.sleep(wait)
```

### Measure limits conservatively

Never run destructive "find the breaking point" tests against a site you
do not own. Even on an owner-authorized job, run load tests against staging
and ask what the production budget is rather than discovering it. Measure
politely instead: crawl a bounded number of pages at a fixed delay and
record status codes plus any rate-limit headers. If you only ever see
`200`s with no `429`, `Retry-After`, or `X-RateLimit-*` at 1-2s spacing,
that is enough to set a safe scheduled cadence. Many sites
expose only CDN cache metadata (Cloudflare, CloudFront, Fastly, and
similar) rather than explicit rate-limit headers, so the absence of
`X-RateLimit-*` is not a green light to go fast. Keep the crawl bounded by
page count and avoid parallel requests.

---

## 8. Common Extraction Patterns

### JSON API response

```python
data = resp.json()
items = data["items"]  # or data["results"], data["data"], etc.
```

### BeautifulSoup HTML parsing

```python
# /// script
# dependencies = ["httpx", "beautifulsoup4"]
# ///
from bs4 import BeautifulSoup

soup = BeautifulSoup(resp.text, "html.parser")
for article in soup.select("article"):
    title = article.select_one("h2 a")
    yield {
        "title": title.get_text(strip=True) if title else None,
        "url": title["href"] if title else None,
    }
```

### selectolax (faster alternative to BS4)

```python
# /// script
# dependencies = ["httpx", "selectolax"]
# ///
from selectolax.parser import HTMLParser

tree = HTMLParser(resp.text)
for node in tree.css("article"):
    title_node = node.css_first("h2 a")
    yield {
        "title": title_node.text(strip=True) if title_node else None,
        "url": title_node.attrs.get("href") if title_node else None,
    }
```

### JSON-LD extraction

```python
import json
from bs4 import BeautifulSoup

soup = BeautifulSoup(resp.text, "html.parser")
for script in soup.find_all("script", type="application/ld+json"):
    try:
        data = json.loads(script.string)
        if isinstance(data, list):
            yield from data
        else:
            yield data
    except json.JSONDecodeError:
        continue
```

### __NEXT_DATA__ extraction

```python
import json, re

match = re.search(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
    resp.text,
    re.DOTALL,
)
if match:
    data = json.loads(match.group(1))
    page_props = data["props"]["pageProps"]
```

### React Server Components (RSC) extraction

For Next.js App Router sites (13.4+) that don't have `__NEXT_DATA__`.
The RSC payload is fetched by adding the `RSC: 1` header.

```python
# /// script
# dependencies = ["httpx"]
# ///
import json
import re

import httpx


def fetch_rsc_payload(client: httpx.Client, url: str) -> str:
    """Fetch RSC payload instead of full HTML."""
    resp = client.get(
        url,
        headers={
            **HEADERS,
            "RSC": "1",
            "Next-Router-State-Tree": "",
        },
    )
    resp.raise_for_status()
    return resp.text


def extract_data_from_rsc(rsc_text: str) -> list[dict]:
    """Parse the RSC line protocol and extract data objects.
    
    Each RSC line is: LINE_ID:JSON_PAYLOAD
    We parse each line's JSON and recursively look for data-like dicts.
    """
    data_objects = []
    for line in rsc_text.splitlines():
        m = re.match(r'^[0-9a-f]+:', line)
        if not m:
            continue
        try:
            parsed = json.loads(line[m.end():])
        except (json.JSONDecodeError, TypeError):
            continue
        _walk_rsc(parsed, data_objects)
    return data_objects


def _walk_rsc(node, out: list):
    """Recursively collect dicts that look like data (not React nodes)."""
    if isinstance(node, dict):
        # Heuristic: dicts with data-like keys are interesting
        useful_keys = {"data", "items", "results", "products", "listings",
                       "props", "pageProps", "initialData", "records"}
        if useful_keys & set(node.keys()):
            out.append(node)
        for v in node.values():
            if isinstance(v, (dict, list)):
                _walk_rsc(v, out)
    elif isinstance(node, list):
        for item in node:
            if isinstance(item, (dict, list)):
                _walk_rsc(item, out)
```

**When to use RSC vs HTML:** If the site also embeds JSON-LD or other
structured data in the HTML, prefer that — it's simpler and more stable.
RSC parsing is the fallback when the data only exists in the RSC stream.

### Table extraction

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(resp.text, "html.parser")
table = soup.select_one("table")
headers = [th.get_text(strip=True) for th in table.select("thead th")]
for row in table.select("tbody tr"):
    cells = [td.get_text(strip=True) for td in row.select("td")]
    yield dict(zip(headers, cells))
```
