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
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import formatdate, parsedate_to_datetime
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
MAX_AGE_DAYS = 7

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


def format_description(story: dict) -> str:
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
    return " | ".join(desc_parts)


def _parse_pubdate(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def story_to_item(story: dict) -> dict:
    """Normalize a fetched/curated story into a uniform feed item."""
    url = story.get("url") or HN_ITEM_URL.format(id=story.get("id", ""))
    pub = story.get("pubDate")
    if not pub and story.get("time"):
        dt = datetime.fromtimestamp(story["time"], tz=timezone.utc)
        pub = formatdate(dt.timestamp(), usegmt=True)
    return {
        "title": story.get("title", "(no title)"),
        "link": url,
        "guid": story.get("guid") or url,
        "description": format_description(story),
        "pubDate": pub or "",
        "category": story.get("category", ""),
    }


def existing_items(path: Path) -> list[dict]:
    """Load items already present in an RSS file, preserving descriptions verbatim."""
    if not path.exists():
        return []
    try:
        channel = ET.parse(path).getroot().find("channel")
    except ET.ParseError:
        return []
    if channel is None:
        return []
    items: list[dict] = []
    for el in channel.findall("item"):
        link = (el.findtext("link") or "").strip()
        items.append({
            "title": (el.findtext("title") or "").strip(),
            "link": link,
            "guid": (el.findtext("guid") or link).strip(),
            "description": (el.findtext("description") or "").strip(),
            "pubDate": (el.findtext("pubDate") or "").strip(),
            "category": (el.findtext("category") or "").strip(),
        })
    return items


def merge_items(new_items: list[dict], old_items: list[dict], count: int) -> list[dict]:
    """Prepend new items ahead of existing ones, drop duplicates and anything
    older than MAX_AGE_DAYS, order newest-first, and cap the total at ``count``."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)
    oldest = datetime.min.replace(tzinfo=timezone.utc)
    merged: list[dict] = []
    seen: set[str] = set()
    for item in [*new_items, *old_items]:
        key = item.get("guid") or item.get("link")
        if not key or key in seen:
            continue
        seen.add(key)
        dt = _parse_pubdate(item.get("pubDate"))
        if dt is not None and dt < cutoff:
            continue  # outside the 7-day window
        item["_dt"] = dt
        merged.append(item)
    merged.sort(key=lambda i: i["_dt"] or oldest, reverse=True)
    for item in merged:
        item.pop("_dt", None)
    if count and count > 0:
        merged = merged[:count]
    return merged


def build_feed(items: list[dict]) -> str:
    rss = Element("rss", version="2.0")
    rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")

    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = "Cobalt Shields - What We're Reading Today"
    SubElement(channel, "link").text = "https://github.com/stevefabiani/dailynewsfeed"
    SubElement(channel, "description").text = (
        "Cobalt Shields — Trusted | Reliable. Daily IT, cybersecurity, and "
        "infrastructure reading list curated for healthcare, higher ed, "
        "government, K-12, and nonprofit leaders."
    )
    SubElement(channel, "language").text = "en-us"
    now = formatdate(usegmt=True)
    SubElement(channel, "lastBuildDate").text = now
    SubElement(channel, "pubDate").text = now
    SubElement(channel, "generator").text = "dailynewsfeed/pipeline.py"

    image = SubElement(channel, "image")
    SubElement(image, "url").text = (
        "https://raw.githubusercontent.com/stevefabiani/dailynewsfeed/main/"
        "Color%20logo%20with%20background.svg"
    )
    SubElement(image, "title").text = "Cobalt Shields - What We're Reading Today"
    SubElement(image, "link").text = "https://github.com/stevefabiani/dailynewsfeed"
    SubElement(image, "width").text = "144"
    SubElement(image, "height").text = "46"
    SubElement(image, "description").text = "Cobalt Shields — Trusted | Reliable"

    atom_link = SubElement(channel, "atom:link")
    atom_link.set(
        "href",
        "https://raw.githubusercontent.com/stevefabiani/dailynewsfeed/main/feed.xml",
    )
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")

    for item in items:
        item_el = SubElement(channel, "item")
        SubElement(item_el, "title").text = item.get("title", "(no title)")

        url = item.get("link", "")
        SubElement(item_el, "link").text = url
        SubElement(item_el, "guid", isPermaLink="true").text = item.get("guid") or url

        SubElement(item_el, "description").text = item.get("description", "")

        if item.get("pubDate"):
            SubElement(item_el, "pubDate").text = item["pubDate"]

        if item.get("category"):
            SubElement(item_el, "category").text = item["category"]

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

    out = Path(args.output)
    new_items = [story_to_item(s) for s in stories]
    old_items = existing_items(out)
    items = merge_items(new_items, old_items, args.count)
    print(
        f"Merging {len(new_items)} new + {len(old_items)} existing "
        f"-> {len(items)} items (dropped items older than {MAX_AGE_DAYS} days)."
    )

    if not items:
        print("No items within the window; aborting.", file=sys.stderr)
        sys.exit(1)

    xml_content = build_feed(items)
    out.write_text(xml_content, encoding="utf-8")
    print(f"Written {out} ({out.stat().st_size:,} bytes, {len(items)} items)")


if __name__ == "__main__":
    main()
