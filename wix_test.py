#!/usr/bin/env python3
"""Smoke-test Wix Blog API credentials.

Verifies that WIX_API_KEY, WIX_SITE_ID, and WIX_MEMBER_ID are set and that
each one works against the Wix REST API. Read-only — does not create any
posts. Exits non-zero on any failure so it can gate the publish workflow.

Usage (locally):
    export WIX_API_KEY=...
    export WIX_SITE_ID=...
    export WIX_MEMBER_ID=...
    python3 wix_test.py
"""

import json
import os
import sys
import urllib.error
import urllib.request

API_BASE = "https://www.wixapis.com"


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def call(method: str, path: str, headers: dict, body: dict | None = None) -> tuple[int, dict]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{API_BASE}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def main() -> None:
    api_key = os.environ.get("WIX_API_KEY", "")
    site_id = os.environ.get("WIX_SITE_ID", "")
    member_id = os.environ.get("WIX_MEMBER_ID", "")

    if not api_key:
        fail("WIX_API_KEY is not set")
    if not site_id:
        fail("WIX_SITE_ID is not set")
    if not member_id:
        fail("WIX_MEMBER_ID is not set")

    print(f"WIX_API_KEY:   set ({len(api_key)} chars)")
    print(f"WIX_SITE_ID:   set ({len(site_id)} chars)")
    print(f"WIX_MEMBER_ID: set ({len(member_id)} chars)")
    print()

    headers = {
        "Authorization": api_key,
        "wix-site-id": site_id,
        "Content-Type": "application/json",
    }

    print("Test 1: Blog API reachable + auth + site-id valid")
    code, body = call("GET", "/blog/v3/categories", headers)
    if code != 200:
        fail(f"GET /blog/v3/categories returned HTTP {code}: {json.dumps(body)[:300]}")
    cats = body.get("categories", [])
    print(f"  OK — found {len(cats)} blog categories")

    print("Test 2: Member ID is a real member on this site")
    code, body = call("GET", f"/members/v1/members/{member_id}?fieldSet=FULL", headers)
    if code != 200:
        fail(f"GET /members/v1/members/{{id}} returned HTTP {code}: {json.dumps(body)[:300]}")
    member = body.get("member", {})
    email = member.get("loginEmail") or member.get("contact", {}).get("emails", [{}])[0].get("email", "<unknown>")
    print(f"  OK — member resolves to {email}")

    print("Test 3: Listing draft posts (write-scope sanity check)")
    code, body = call("GET", "/blog/v3/draft-posts?paging.limit=1", headers)
    if code != 200:
        fail(f"GET /blog/v3/draft-posts returned HTTP {code}: {json.dumps(body)[:300]}")
    drafts = body.get("draftPosts", [])
    print(f"  OK — drafts endpoint reachable ({len(drafts)} returned, limit=1)")

    print()
    print("All checks passed. Credentials are good to go.")


if __name__ == "__main__":
    main()
