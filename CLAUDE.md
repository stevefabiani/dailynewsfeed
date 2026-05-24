# Daily curation routine

Pull the current feed.xml from the repo. Build today's "Cobalt Shields — What We're Reading Today" brief following these rules.

## WINDOW

- Include only paywall-free articles published or updated after 2:30AM yesterday.

## RELIABLE SOURCES (paywall-free)

BBC, DW, France 24, NHK World, ABC Australia, CBC, Swissinfo, NPR, PBS NewsHour, Reuters, AP, AFP, The Conversation, ProPublica, CSMonitor, Al Jazeera English, The Guardian.

## SECTOR RELEVANCE

Healthcare, higher ed, government, K-12, nonprofit.

## TOPICS

- Major infosec breaches and vulnerabilities
- End-user tech trends
- Academic tech trends
- ERP trends
- Tech leadership and org dev
- Tech governance
- Tech-related audit / risk / legal compliance — especially new and emerging law
- Major M&A involving products used in the target sectors

## PER-ITEM RULES

- Summarize in ≤4 sentences.
- Combine substantially similar articles from different outlets into one item; cite the lead source and link any companion stories inline in the description.
- Use paywall-free, direct article URLs (no aggregator redirects).
- End each description with ` | Source: <Outlet>`.
- Order by date and time last updated, with most recent first.

## FEED UPDATE (feed.xml at repo root)

- Prepend new items as RSS 2.0 `<item>` elements (newest first).
- Drop items older than 7 days.
- Drop items that have been updated with newer versions of the same article.
- Update `<lastBuildDate>` and `<pubDate>` on `<channel>` to now (GMT).
- Preserve the existing `<title>` "Cobalt Shields - What We're Reading Today", the `<image>` element, and the `<atom:link>` self-reference.

## ARCHIVE (two files per day)

- `archive/Daily Summary YYYY-MM-DD.xml` — same RSS 2.0 structure, channel title `Cobalt Shields - What We're Reading Today — Summary for YYYY-MM-DD`, containing only today's new items.
- `archive/Daily Summary YYYY-MM-DD.md` — human-readable markdown version of the same items: H1 "Cobalt Shields - What We're Reading Today — YYYY-MM-DD", then per-item: H2 title, metadata line (category · date · source · link), then the summary paragraph.

## COMMIT & PUSH

- Branch: `main`
- Commit message: `Daily IT news summary YYYY-MM-DD`
- Push to origin.

## WHAT HAPPENS NEXT (no action needed)

The push touches `archive/**`, which triggers `.github/workflows/wix-publish.yml`. It deletes any existing post in the "Daily News Roundup" category and publishes a new Wix blog post with today's items, branded with the Cobalt Shields cover from `assets/cover.png`.
