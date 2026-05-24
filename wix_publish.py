#!/usr/bin/env python3
"""Publish the latest Daily News Roundup to Wix Blog.

Reads the newest `archive/Daily Summary YYYY-MM-DD.xml`, deletes any prior
posts in the "Daily News Roundup" category, then creates and publishes a
single new post containing all of today's items.

On first run, auto-creates the category and uploads the Cobalt Shields
logo to Wix Media. IDs are cached in `wix_state.json` so subsequent runs
are fast.

Required env vars:
    WIX_API_KEY
    WIX_SITE_ID
    WIX_MEMBER_ID
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).parent
ARCHIVE_DIR = REPO_ROOT / "archive"
STATE_FILE = REPO_ROOT / "wix_state.json"

API_BASE = "https://www.wixapis.com"
CATEGORY_LABEL = "Daily News Roundup"
COVER_URL = (
    "https://raw.githubusercontent.com/stevefabiani/dailynewsfeed/main/"
    "Color%20logo%20with%20background.svg"
)
COVER_DISPLAY_NAME = "Cobalt Shields logo"


# ---------- HTTP helpers ---------------------------------------------------

def _headers() -> dict[str, str]:
    return {
        "Authorization": os.environ["WIX_API_KEY"],
        "wix-site-id": os.environ["WIX_SITE_ID"],
        "Content-Type": "application/json",
    }


def call(method: str, path: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        f"{API_BASE}{path}", data=data, headers=_headers(), method=method
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read()
        msg = raw.decode("utf-8", "replace") if raw else ""
        raise SystemExit(f"HTTP {e.code} on {method} {path}: {msg[:500]}")


# ---------- state ----------------------------------------------------------

def load_state() -> dict[str, Any]:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state: dict[str, Any]) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n")


# ---------- archive parsing ------------------------------------------------

def latest_archive() -> Path:
    files = sorted(ARCHIVE_DIR.glob("Daily Summary *.xml"))
    if not files:
        raise SystemExit(f"No archive files found in {ARCHIVE_DIR}")
    return files[-1]


def parse_archive(path: Path) -> tuple[str, str, list[dict[str, str]]]:
    root = ET.parse(path).getroot()
    ch = root.find("channel")
    title = (ch.findtext("title") or "").strip()
    description = (ch.findtext("description") or "").strip()
    items: list[dict[str, str]] = []
    for it in ch.findall("item"):
        items.append({
            "title": (it.findtext("title") or "").strip(),
            "link": (it.findtext("link") or "").strip(),
            "description": (it.findtext("description") or "").strip(),
            "category": (it.findtext("category") or "").strip(),
        })
    return title, description, items


# ---------- Wix: category --------------------------------------------------

def ensure_category(state: dict[str, Any]) -> str:
    if cid := state.get("categoryId"):
        return cid
    # Look it up by label first
    q = call("POST", "/blog/v3/categories/query", {
        "query": {"filter": {"label": CATEGORY_LABEL}}
    })
    for cat in q.get("categories", []):
        if cat.get("label") == CATEGORY_LABEL:
            state["categoryId"] = cat["id"]
            return cat["id"]
    # Create it
    created = call("POST", "/blog/v3/categories", {
        "category": {"label": CATEGORY_LABEL, "slug": "daily-news-roundup"}
    })
    cid = created["category"]["id"]
    state["categoryId"] = cid
    return cid


# ---------- Wix: cover image (best-effort) ---------------------------------

def ensure_cover(state: dict[str, Any]) -> str | None:
    if mid := state.get("coverMediaId"):
        return mid
    body = {
        "url": COVER_URL,
        "displayName": COVER_DISPLAY_NAME,
        "mediaType": "IMAGE",
        "mimeType": "image/svg+xml",
        "private": False,
    }
    try:
        result = call("POST", "/site-media/v1/files/import", body)
    except SystemExit as e:
        print(f"  WARN: cover import failed, posting without cover. {e}", file=sys.stderr)
        return None
    file_id = result.get("file", {}).get("id")
    if not file_id:
        print(f"  WARN: unexpected media import response: {result}", file=sys.stderr)
        return None
    state["coverMediaId"] = file_id
    return file_id


# ---------- Wix: delete old posts in category ------------------------------

def delete_old_posts(category_id: str) -> int:
    q = call("POST", "/blog/v3/posts/query", {
        "query": {"filter": {"categoryIds": {"$hasSome": [category_id]}}, "paging": {"limit": 100}}
    })
    posts = q.get("posts", [])
    for p in posts:
        call("DELETE", f"/blog/v3/posts/{p['id']}")
    # Also clean any drafts left behind
    qd = call("POST", "/blog/v3/draft-posts/query", {
        "query": {"filter": {"categoryIds": {"$hasSome": [category_id]}}, "paging": {"limit": 100}}
    })
    for d in qd.get("draftPosts", []):
        call("DELETE", f"/blog/v3/draft-posts/{d['id']}")
    return len(posts)


# ---------- Ricos rich-content builders ------------------------------------

_node_counter = [0]


def _nid(prefix: str) -> str:
    _node_counter[0] += 1
    return f"{prefix}{_node_counter[0]}"


def text_node(text: str, *, link: str | None = None, bold: bool = False) -> dict:
    decorations: list[dict] = []
    if bold:
        decorations.append({"type": "BOLD", "fontWeightValue": 700})
    if link:
        decorations.append({
            "type": "LINK",
            "linkData": {"link": {"url": link, "target": "BLANK"}},
        })
    return {
        "type": "TEXT",
        "id": _nid("t"),
        "nodes": [],
        "textData": {"text": text, "decorations": decorations},
    }


def paragraph(*nodes: dict) -> dict:
    return {"type": "PARAGRAPH", "id": _nid("p"), "nodes": list(nodes)}


def heading(text: str, *, link: str | None = None, level: int = 3) -> dict:
    return {
        "type": "HEADING",
        "id": _nid("h"),
        "nodes": [text_node(text, link=link, bold=True)],
        "headingData": {"level": level},
    }


def divider() -> dict:
    return {
        "type": "DIVIDER",
        "id": _nid("d"),
        "nodes": [],
        "dividerData": {"lineStyle": "SINGLE", "width": "MEDIUM", "alignment": "CENTER"},
    }


def build_rich_content(intro: str, items: list[dict[str, str]]) -> dict:
    nodes: list[dict] = [paragraph(text_node(intro))]
    for i, it in enumerate(items):
        nodes.append(heading(it["title"], link=it["link"] or None, level=3))
        # Description may contain a trailing "| Source: X" — strip embedded
        # raw URLs (companion links) to keep paragraph clean.
        desc = it["description"].replace("\n", " ").strip()
        nodes.append(paragraph(text_node(desc)))
        if i < len(items) - 1:
            nodes.append(divider())
    return {"nodes": nodes}


# ---------- post composition -----------------------------------------------

def today_date_from_archive(archive_path: Path) -> str:
    # Filename: "Daily Summary YYYY-MM-DD.xml"
    stem = archive_path.stem  # "Daily Summary YYYY-MM-DD"
    return stem.rsplit(" ", 1)[-1]


def build_post_body(
    *,
    member_id: str,
    category_id: str,
    cover_media_id: str | None,
    title: str,
    excerpt: str,
    rich_content: dict,
) -> dict:
    draft: dict[str, Any] = {
        "title": title,
        "memberId": member_id,
        "excerpt": excerpt[:498],
        "richContent": rich_content,
        "categoryIds": [category_id],
        "commentingEnabled": False,
    }
    if cover_media_id:
        draft["media"] = {
            "wixMedia": {"image": {"id": cover_media_id}},
            "displayed": True,
            "custom": False,
        }
    return {"draftPost": draft, "fieldsets": ["URL", "RICH_CONTENT"]}


# ---------- main -----------------------------------------------------------

def main() -> None:
    for k in ("WIX_API_KEY", "WIX_SITE_ID", "WIX_MEMBER_ID"):
        if not os.environ.get(k):
            raise SystemExit(f"{k} is not set")

    member_id = os.environ["WIX_MEMBER_ID"]
    state = load_state()

    archive_path = latest_archive()
    date_str = today_date_from_archive(archive_path)
    print(f"Loading {archive_path.name}")
    _, channel_desc, items = parse_archive(archive_path)
    if not items:
        raise SystemExit("Archive has no items; aborting publish.")
    print(f"  {len(items)} items")

    print(f"Ensuring category '{CATEGORY_LABEL}' exists")
    category_id = ensure_category(state)
    print(f"  categoryId={category_id}")

    print("Ensuring cover image is uploaded to Wix Media")
    cover_media_id = ensure_cover(state)
    print(f"  coverMediaId={cover_media_id or '(none)'}")

    print("Deleting prior posts in category")
    deleted = delete_old_posts(category_id)
    print(f"  removed {deleted} previously-published post(s)")

    title = f"Cobalt Shields — What We're Reading Today ({date_str})"
    intro = (
        f"Today's curated IT reading list for healthcare, higher ed, government, "
        f"K-12, and nonprofit leaders. {channel_desc}"
    )
    rich = build_rich_content(intro, items)

    excerpt_bits = []
    for it in items[:3]:
        excerpt_bits.append(it["title"])
    excerpt = " · ".join(excerpt_bits)

    body = build_post_body(
        member_id=member_id,
        category_id=category_id,
        cover_media_id=cover_media_id,
        title=title,
        excerpt=excerpt,
        rich_content=rich,
    )

    print("Creating draft post")
    draft_resp = call("POST", "/blog/v3/draft-posts", body)
    draft_id = draft_resp["draftPost"]["id"]
    print(f"  draftId={draft_id}")

    print("Publishing draft")
    pub_resp = call("POST", f"/blog/v3/draft-posts/{draft_id}/publish")
    post = pub_resp.get("post") or pub_resp.get("draftPost") or {}
    post_id = post.get("id", "")
    post_url = post.get("url", {}).get("base", "") + post.get("url", {}).get("path", "")
    print(f"  postId={post_id}")
    print(f"  url={post_url or '(unknown)'}")

    state["lastPostId"] = post_id
    state["lastPublishedDate"] = date_str
    save_state(state)
    print(f"State saved to {STATE_FILE.name}")
    print("Done.")


if __name__ == "__main__":
    main()
