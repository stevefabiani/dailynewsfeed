# Cobalt Shields — What We're Reading Today

Daily IT/cybersecurity reading list for healthcare, higher ed, government, K-12, and nonprofit leaders. Curated each weekday, published as both an RSS feed and a Wix blog post.

- **Live RSS feed:** https://raw.githubusercontent.com/stevefabiani/dailynewsfeed/main/feed.xml
- **Wix blog post:** auto-published in the *Daily News Roundup* category on cobaltshields.com

---

## How it works

Two workflows, one repo:

```
┌─────────────────────┐      ┌──────────────────────┐
│ 1. CURATION         │ ──▶  │ 2. PUBLISH TO WIX    │
│ (Claude Code)       │      │ (GitHub Actions)     │
│                     │      │                      │
│ Builds feed.xml +   │      │ Reads latest archive │
│ archive files,      │      │ XML, deletes prior   │
│ commits to main     │      │ post, publishes new  │
└─────────────────────┘      └──────────────────────┘
         │                              │
         ▼                              ▼
     feed.xml             https://cobaltshields.com/blog
   (RSS readers)            (Daily News Roundup)
```

### 1. Curation (currently human-triggered)

Start a Claude Code session pointed at this repo. The full curation routine lives in `CLAUDE.md` and is auto-loaded by Claude Code, so a short prompt is enough:

> "Build today's brief."

Claude reads `CLAUDE.md`, fetches paywall-free items from the approved sources within the window (after 2:30AM yesterday), summarizes each in ≤4 sentences, prepends them to `feed.xml`, writes the dated archive files, and pushes to `main`.

### 2. Publish (fully automated)

The push to `archive/**` triggers `.github/workflows/wix-publish.yml`. The workflow:

1. Checks out the repo
2. Runs `wix_publish.py` which:
   - Reads the newest `archive/Daily Summary *.xml`
   - Ensures the *Daily News Roundup* category exists in Wix (auto-creates)
   - Imports `assets/cover.png` to Wix Media (cached after first run)
   - Deletes any prior posts in that category
   - Builds Ricos rich content: H3 brand-blue headline + summary paragraph + divider, per item
   - Creates a draft, publishes it
3. Commits the updated `wix_state.json` (caches category ID, cover media ID, last post ID)

You can also trigger it manually: **Actions → Publish to Wix → Run workflow → main → Run**.

---

## Repository layout

```
.
├── README.md                       ← this file
├── feed.xml                        ← live RSS feed (rolling 7 days)
├── pipeline.py                     ← helper to regenerate feed.xml from stories.json
├── stories.json                    ← optional curated story list for offline mode
├── wix_publish.py                  ← posts latest archive to Wix Blog
├── wix_test.py                     ← smoke-tests the Wix API credentials
├── wix_state.json                  ← cached Wix IDs (category, cover, last post)
├── Color logo with background.svg  ← brand SVG (used in RSS <image>)
├── assets/
│   └── cover.png                   ← raster cover used on every Wix post
├── archive/
│   ├── Daily Summary 2026-05-24.xml
│   ├── Daily Summary 2026-05-24.md
│   └── …
└── .github/
    ├── dependabot.yml              ← monthly action-version checks
    └── workflows/
        ├── wix-test.yml            ← manual credential smoke test
        ├── wix-publish.yml         ← daily publisher
        └── dependabot-auto-merge.yml  ← auto-merges minor/patch dep PRs
```

---

## One-time setup (already done — kept here for re-create / disaster recovery)

### Wix side

1. Install the Wix Blog app on the site.
2. Dashboard → Settings → Headless Settings → **API Keys** → create key `dailynewsfeed-publisher` with scopes:
   - `Wix Blog / Manage Blog`
   - `Wix Blog / Read Blog`
   - `Wix Members / Read Members`
3. Note your **Site ID** (in the dashboard URL) and **Member ID** (returned by `GET /members/v1/members`).
4. Dashboard → Settings → **Allow auto-merge** (enables the Dependabot auto-merge workflow to function).

### GitHub side

1. Repo → Settings → Secrets and variables → Actions → add:
   - `WIX_API_KEY`
   - `WIX_SITE_ID`
   - `WIX_MEMBER_ID`
2. Settings → Actions → General → Workflow permissions → ☑ **Allow GitHub Actions to create and approve pull requests**
3. Settings → General → Pull Requests → ☑ **Allow auto-merge**

### Verifying credentials

Run **Actions → Wix credentials smoke test → Run workflow**. Expected output:

```
WIX_API_KEY:   set (N chars)
WIX_SITE_ID:   set (36 chars)
WIX_MEMBER_ID: set (36 chars)
Test 1: Blog API reachable + auth + site-id valid — OK
Test 2: Member ID is a real member on this site — OK
Test 3: Listing draft posts (write-scope sanity check) — OK
All checks passed. Credentials are good to go.
```

---

## Daily operation

**To run the day's curation + publish:**

1. Open a Claude Code session against this repo.
2. Ask for today's summary (see the prompt above).
3. Claude pushes; the **Publish to Wix** workflow auto-runs.
4. Refresh your Wix blog — new post should appear within ~30 seconds of the workflow's `postId=` log line.

**To re-publish without re-curating** (e.g., after a script change):

- Actions → Publish to Wix → Run workflow → main → Run.

---

## Tweaking the look

| What | Where |
| --- | --- |
| Per-item headline color | `HEADING_COLOR = "#01328e"` in `wix_publish.py` |
| Cover image | replace `assets/cover.png` and delete `coverMediaId` from `wix_state.json` (next run re-imports) |
| Post title format | `title = f"Cobalt Shields — What We're Reading Today ({date_str})"` in `wix_publish.py` |
| Excerpt content | `excerpt_bits = …` in `wix_publish.py` (currently first three item titles, joined by `·`) |
| Category name | `CATEGORY_LABEL = "Daily News Roundup"` in `wix_publish.py` |
| Source list, sectors, topic filters | the standing curation prompt (in `CLAUDE.md` or your saved Claude Code instructions) |

---

## Maintenance

### Action version updates

Dependabot scans the workflow files monthly (first Monday) and opens one PR per month with available bumps.

- **Patch/minor bumps** auto-merge via `dependabot-auto-merge.yml` — zero clicks.
- **Major bumps** are held for your manual review. Skim the changelog, click Merge.

### Node deprecation env var

`FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: "true"` is set in each workflow as an interim opt-in until `actions/checkout` and `actions/setup-python` ship majors that bundle Node 24 natively. When Dependabot bumps those to their next majors, delete the env var lines (they become no-ops). When Node 26 eventually becomes the next deprecation, GitHub will provide a new env var name to repeat the pattern.

---

## Troubleshooting

**Workflow fails with `HTTP 401` or `HTTP 403`.**
The API key was revoked, expired, or is missing a scope. Regenerate it in Wix → Headless Settings, update the `WIX_API_KEY` repo secret, re-run.

**Workflow runs but `removed 0 previously-published post(s)` even though there's an old post.**
That old post isn't in the `Daily News Roundup` category. Either move it into the category manually, or delete it via the Wix dashboard once. After that, every run replaces cleanly.

**Cover image doesn't appear.**
Wix Media rejects SVG for blog covers. `assets/cover.png` must be a raster (PNG/JPEG). After replacing the file, delete `coverMediaId` from `wix_state.json` and re-run so the import re-attempts.

**Headlines look washed out.**
Wix's blog theme styles `<h3>` faintly. The script forces them to `HEADING_COLOR` (currently `#01328e`). Adjust that constant in `wix_publish.py` if needed.

**Post title (the very top one) renders in a color you don't want.**
That's controlled by Wix's blog theme, not by this script. Edit it in Wix Editor → Design → Blog Post Page → Title styling.

**Push to `main` doesn't trigger the publish.**
The push trigger only fires for changes under `archive/**`. Changes to `feed.xml` alone won't trigger it. To force a publish without an archive change, trigger the workflow manually.

**Stop hook complains about uncommitted/untracked files.**
The repo's stop hook checks for clean working tree. Commit or stash before ending a session. `__pycache__/` is `.gitignore`d already.

---

## Manual lookups (for re-discovery later)

Get the Member ID for a different author:

```bash
curl -s -X POST "https://www.wixapis.com/members/v1/members/query" \
  -H "Authorization: $WIX_API_KEY" \
  -H "wix-site-id: $WIX_SITE_ID" \
  -H "Content-Type: application/json" \
  -d '{"query":{"filter":{"loginEmail":"someone@example.com"},"fieldSet":"FULL"}}' \
  | python3 -m json.tool
```

List Wix Blog categories:

```bash
curl -s "https://www.wixapis.com/blog/v3/categories" \
  -H "Authorization: $WIX_API_KEY" \
  -H "wix-site-id: $WIX_SITE_ID" \
  | python3 -m json.tool
```

Delete a stuck post by ID (e.g., the auto-replace failed and you want to force a clean slate):

```bash
curl -s -X DELETE "https://www.wixapis.com/blog/v3/posts/POST_ID_HERE" \
  -H "Authorization: $WIX_API_KEY" \
  -H "wix-site-id: $WIX_SITE_ID"
```

---

## Roadmap / known gaps

- **Curation is still human-triggered.** Fully automating it requires either a scheduled Claude Code on the web session, a serverless cron calling the Anthropic API, or GitHub Actions running the `claude` CLI headlessly with the curation prompt. Pick a path when ready.
- **No tests.** `wix_test.py` is a credential smoke test, not unit tests for the Ricos builder. If `wix_publish.py` grows, consider extracting `build_rich_content` and adding fixtures.
- **No rate-limit handling.** Wix's published limits are generous for one post/day; if cadence increases significantly, add exponential backoff around the `call()` helper.
