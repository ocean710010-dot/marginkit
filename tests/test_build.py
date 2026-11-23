"""End-to-end build, SEO schema, pathing, and keyword-miner unit tests for MarginKit."""

from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import build as builder  # noqa: E402
import mine_keywords  # noqa: E402


EXPECTED_TOOLS = [
    "amazon-fba-profit-calculator",
    "eu-vat-calculator",
    "freelance-hourly-rate-calculator",
    "paypal-fee-calculator",
    "saas-mrr-churn-calculator",
    "shopify-profit-margin-calculator",
    "stripe-fee-calculator",
    "wise-vs-bank-fx-calculator",
]


class TestSiteBuild(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.stats = builder.build()
        cls.site = builder.load_json(ROOT / "config" / "site.json")
        cls.dist = ROOT / "dist"

    def test_expected_files_exist(self) -> None:
        self.assertGreaterEqual(self.stats["tools"], 8)
        for rel in [
            "index.html",
            "404.html",
            "sitemap.xml",
            "robots.txt",
            ".nojekyll",
            "assets/style.css",
            "assets/app.js",
            "about/index.html",
            "privacy/index.html",
            "terms/index.html",
            "contact/index.html",
        ]:
            self.assertTrue((self.dist / rel).exists(), f"Missing built file: {rel}")

    def test_all_tool_pages_and_jsonld(self) -> None:
        bp = self.site.get("base_path", "").rstrip("/")
        bu = self.site["base_url"].rstrip("/")
        ld_re = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)

        for slug in EXPECTED_TOOLS:
            html_path = self.dist / "tools" / slug / "index.html"
            js_path = self.dist / "js" / "tools" / f"{slug}.js"
            self.assertTrue(html_path.exists(), f"Missing tool HTML: {slug}")
            self.assertTrue(js_path.exists(), f"Missing tool JS: {slug}")
            self.assertGreater(js_path.stat().st_size, 100)

            content = html_path.read_text(encoding="utf-8")
            canonical = f'<link rel="canonical" href="{bu}/tools/{slug}/">'
            self.assertIn(canonical, content)

            if bp:
                self.assertIn(f'href="{bp}/assets/style.css"', content)
                self.assertIn(f'src="{bp}/assets/app.js"', content)
                self.assertIn(f'src="{bp}/js/tools/{slug}.js"', content)
                self.assertNotIn('href="/assets/', content)
                self.assertNotIn('src="/assets/', content)
                self.assertNotIn('src="/js/', content)

            blocks = ld_re.findall(content)
            self.assertGreaterEqual(len(blocks), 1, f"Missing JSON-LD on {slug}")
            for raw_json in blocks:
                parsed = json.loads(raw_json)
                self.assertIn("@context", parsed)
                self.assertIn("@type", parsed)

    def test_sitemap_lists_all_tools(self) -> None:
        sitemap = (self.dist / "sitemap.xml").read_text(encoding="utf-8")
        bu = self.site["base_url"].rstrip("/")
        for slug in EXPECTED_TOOLS:
            self.assertIn(f"{bu}/tools/{slug}/", sitemap)

    def test_indexnow_key_file_generated(self) -> None:
        key = (self.site.get("indexnow_key") or "").strip()
        self.assertTrue(key, "Expected non-empty indexnow_key in config/site.json")
        key_file = self.dist / f"{key}.txt"
        self.assertTrue(key_file.exists(), f"Missing IndexNow key file: {key_file}")
        self.assertEqual(key_file.read_text(encoding="utf-8"), key)


class TestKeywordMiner(unittest.TestCase):
    def test_slug_and_scoring(self) -> None:
        self.assertEqual(mine_keywords.to_slug("  Etsy Fee & Profit Calculator! "), "etsy-fee-profit-calculator")
        self.assertGreater(
            mine_keywords.score_keyword("shopify profit margin calculator"),
            mine_keywords.score_keyword("random calculator"),
        )

    def test_merge_backlog_deduplicates(self) -> None:
        existing = [
            {"keyword": "ebay fee calculator", "slug": "ebay-fee-calculator", "score": 45, "status": "pending"}
        ]
        merged, added = mine_keywords.merge_backlog(
            existing,
            [
                "ebay fee calculator",
                "stripe fee calculator",
                "square processing fee calculator",
                "hi",
            ],
            live_slugs={"stripe-fee-calculator"},
        )
        self.assertEqual(added, 1)
        slugs = [x["slug"] for x in merged]
        self.assertIn("square-processing-fee-calculator", slugs)
        self.assertNotIn("stripe-fee-calculator", slugs)


if __name__ == "__main__":
    unittest.main()
