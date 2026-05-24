#!/usr/bin/env python3
"""Daily IT news pipeline.

Live mode (default): fetches top tech stories from Hacker News API.
Offline mode (--from-json FILE): reads pre-fetched stories from a JSON file.

Usage:
    python3 pipeline.py                          # live fetch from HN
    python3 pipeline.py --from-json stories.json # offline / curated mode
    python3 pipeline.py --output my-feed.xml     # custom output path
    python3 pipeline.py --count 20               # limit items in feed
"""

import argparse
import json
import sys
import urllib.request
from datetime import datetime, timezone
from email.utils import formatdate
from pathlib import Path
from xml.dom.minidom import parseString
from xml.etree.ElementTree import Element, SubElement, tostring

HN_API = "https://hacker-news.firebaseio.com/v0"
TOP_STORIES_URL = f"{HN_API}/topstories.json"
ITEM_URL = f"{HN_API}/item/{{id}}.json"
HN_ITEM_URL = "https://news.ycombinator.com/item?id={id}"

DEFAULT_OUTPUT = Path(__file__).parent / "feed.xml"
DEFAULT_COUNT = 30
MAX_EXAMINE = 200

IT_KEYWORDS = {
    "security", "linux", "python", "cloud", "devops", "kubernetes", "docker",
    "api", "database", "sql", "aws", "azure", "gcp", "networking", "firewall",
    "vulnerability", "exploit", "patch", "ransomware", "breach", "zero-day",
    "open source", "github", "rust", "golang", "typescript", "javascript",
    "ai", "ml", "llm", "cybersecurity", "infosec", "sysadmin", "infrastructure",
    "microservices", "serverless", "ci/cd", "monitoring", "observability",
    "encryption", "ssl", "tls", "dns", "ssh", "vpn", "soc", "siem", "cve",
    "malware", "botnet", "ddos", "supply chain", "threat", "incident",
}


def fetch_json(url: str) -> object:
    with urllib.request.urlopen(url, timeout=10) as resp:
        return json.loads(resp.read())


def is_it_relevant(story: dict) -> bool:
    title = (story.get("title") or "").lower()
    return any(kw in title for kw in IT_KEYWORDS)


def fetch_live(count: int) -> list[dict]:
    print("Fetching top story IDs from Hacker News…")
    ids = fetch_json(TOP_STORIES_URL)
    stories: list[dict] = []
    examined = 0
    for sid in ids:
        if len(stories) >= count:
            break
        if examined >= MAX_EXAMINE:
            break
        examined += 1
        try:
            item = fetch_json(ITEM_URL.format(id=sid))
        except Exception as exc:
            print(f"  skip {sid}: {exc}", file=sys.stderr)
            continue
        if not item or item.get("type") != "story" or not item.get("title"):
            continue
        if is_it_relevant(item):
            stories.append(item)
            print(f"  [{len(stories):2d}] {item['title'][:80]}")
    print(f"Collected {len(stories)} IT-relevant stories (examined {examined}).")
    return stories


def load_json_stories(path: Path, count: int) -> list[dict]:
    print(f"Loading stories from {path}…")
    raw = json.loads(path.read_text(encoding="utf-8"))
    stories = raw[:count]
    print(f"Loaded {len(stories)} stories.")
    return stories


def build_feed(stories: list[dict]) -> str:
    rss = Element("rss", version="2.0")
    rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")

    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = "Daily IT News"
    SubElement(channel, "link").text = "https://github.com/stevefabiani/dailynewsfeed"
    SubElement(channel, "description").text = (
        "Top IT, cybersecurity, and infrastructure stories — updated daily"
    )
    SubElement(channel, "language").text = "en-us"
    SubElement(channel, "lastBuildDate").text = formatdate(usegmt=True)
    SubElement(channel, "generator").text = "dailynewsfeed/pipeline.py"

    atom_link = SubElement(channel, "atom:link")
    atom_link.set(
        "href",
        "https://raw.githubusercontent.com/stevefabiani/dailynewsfeed/main/feed.xml",
    )
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")

    for story in stories:
        item_el = SubElement(channel, "item")
        SubElement(item_el, "title").text = story.get("title", "(no title)")

        url = story.get("url") or HN_ITEM_URL.format(id=story.get("id", ""))
        SubElement(item_el, "link").text = url
        SubElement(item_el, "guid", isPermaLink="true").text = url

        desc_parts: list[str] = []
        if story.get("description"):
            desc_parts.append(story["description"])
        if story.get("source"):
            desc_parts.append(f"Source: {story['source']}")
        if story.get("score"):
            desc_parts.append(f"Score: {story['score']}")
        if story.get("descendants") is not None:
            desc_parts.append(f"Comments: {story['descendants']}")
        if story.get("by"):
            desc_parts.append(f"By: {story['by']}")
        SubElement(item_el, "description").text = " | ".join(desc_parts)

        if story.get("pubDate"):
            SubElement(item_el, "pubDate").text = story["pubDate"]
        elif story.get("time"):
            pub = datetime.fromtimestamp(story["time"], tz=timezone.utc)
            SubElement(item_el, "pubDate").text = formatdate(pub.timestamp(), usegmt=True)

        if story.get("category"):
            SubElement(item_el, "category").text = story["category"]

    raw = tostring(rss, encoding="unicode", xml_declaration=False)
    pretty = parseString(f'<?xml version="1.0" encoding="UTF-8"?>{raw}').toprettyxml(
        indent="  ", encoding=None
    )
    lines = [ln for ln in pretty.splitlines() if ln.strip()]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Daily IT news pipeline")
    parser.add_argument("--from-json", metavar="FILE", help="Load stories from JSON instead of fetching live")
    parser.add_argument("--output", metavar="FILE", default=str(DEFAULT_OUTPUT), help="Output RSS file path")
    parser.add_argument("--count", type=int, default=DEFAULT_COUNT, help="Max number of feed items")
    args = parser.parse_args()

    if args.from_json:
        stories = load_json_stories(Path(args.from_json), args.count)
    else:
        stories = fetch_live(args.count)

    if not stories:
        print("No stories found; aborting.", file=sys.stderr)
        sys.exit(1)

    xml_content = build_feed(stories)
    out = Path(args.output)
    out.write_text(xml_content, encoding="utf-8")
    print(f"Written {out} ({out.stat().st_size:,} bytes, {len(stories)} items)")


if __name__ == "__main__":
    main()
