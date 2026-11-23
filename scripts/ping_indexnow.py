"""Submit newly published URLs to IndexNow (used once a custom domain is attached)."""

from __future__ import annotations

import json
import os
import sys
import urllib.request


def submit_urls(host: str, key: str, urls: list[str]) -> int:
    payload = json.dumps(
        {
            "host": host,
            "key": key,
            "keyLocation": f"https://{host}/{key}.txt",
            "urlList": urls,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow",
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status


if __name__ == "__main__":
    host = os.environ.get("SITE_HOST", "").strip()
    key = os.environ.get("INDEXNOW_KEY", "").strip()
    urls = [u for u in sys.argv[1:] if u.startswith("http")]

    if not host or not key or not urls:
        print("Skipped IndexNow: set SITE_HOST, INDEXNOW_KEY, and pass one or more URLs.")
        sys.exit(0)

    status = submit_urls(host, key, urls)
    print(f"IndexNow submitted {len(urls)} URL(s): HTTP {status}")
