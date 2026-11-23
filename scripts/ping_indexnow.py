"""Submit site URLs to IndexNow (Bing, Yandex, Naver, Seznam)."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_CONFIG = ROOT / "config" / "site.json"
DIST_SITEMAP = ROOT / "dist" / "sitemap.xml"


def parse_sitemap_urls(xml_text: str) -> list[str]:
    root = ET.fromstring(xml_text)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = root.findall(".//sm:loc", ns)
    if not locs:
        locs = root.findall(".//loc")
    return [el.text.strip() for el in locs if el.text and el.text.strip().startswith("http")]


def submit_urls(host: str, key: str, key_location: str, urls: list[str]) -> tuple[int, str]:
    payload = json.dumps(
        {
            "host": host,
            "key": key,
            "keyLocation": key_location,
            "urlList": urls,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow",
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, resp.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "ignore")
        return exc.code, body


def main() -> int:
    parser = argparse.ArgumentParser(description="Submit MarginKit URLs to IndexNow.")
    parser.add_argument("--from-sitemap", action="store_true", help="Read URLs from dist/sitemap.xml")
    parser.add_argument("--live-sitemap", action="store_true", help="Fetch URLs from live base_url/sitemap.xml")
    parser.add_argument("urls", nargs="*", help="Explicit URLs to submit")
    args = parser.parse_args()

    site = json.loads(SITE_CONFIG.read_text(encoding="utf-8")) if SITE_CONFIG.exists() else {}
    base_url = (site.get("base_url") or "").rstrip("/")
    host = os.environ.get("SITE_HOST", "").strip() or urllib.parse.urlparse(base_url).netloc
    key = os.environ.get("INDEXNOW_KEY", "").strip() or (site.get("indexnow_key") or "").strip()

    urls = [u for u in args.urls if u.startswith("http")]
    if args.live_sitemap:
        live_sm = f"{base_url}/sitemap.xml"
        req = urllib.request.Request(live_sm, headers={"User-Agent": "MarginKit-IndexNow/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            urls = parse_sitemap_urls(resp.read().decode("utf-8"))
    elif args.from_sitemap:
        urls = parse_sitemap_urls(DIST_SITEMAP.read_text(encoding="utf-8"))

    if not host or not key or not urls:
        print("Skipped IndexNow: missing host, indexnow_key, or URLs.")
        return 1

    key_location = f"{base_url}/{key}.txt" if base_url else f"https://{host}/{key}.txt"
    status, body = submit_urls(host, key, key_location, urls)
    print(f"IndexNow POST {len(urls)} URL(s) -> HTTP {status} | keyLocation={key_location}")
    if body:
        print(f"Response: {body[:400]}")
    return 0 if status in (200, 202) else 1


if __name__ == "__main__":
    sys.exit(main())
