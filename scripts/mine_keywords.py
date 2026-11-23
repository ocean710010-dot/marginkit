"""Zero-dependency B2B calculator keyword miner for MarginKit."""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT / "tools"
BACKLOG_PATH = ROOT / "backlog.json"

SEEDS = [
    "shopify fee calculator",
    "square fee calculator",
    "etsy fee and profit calculator",
    "ebay fee calculator",
    "saas cac payback calculator",
    "saas rule of 40 calculator",
    "uk vat calculator",
    "gst calculator australia",
    "sales tax reverse calculator",
    "contractor day rate calculator",
    "agency retainer pricing calculator",
    "gross margin vs markup calculator",
    "dropshipping break even roas calculator",
    "payoneer fee calculator",
    "paddle fee calculator",
]

FALLBACK_CANDIDATES = [
    "etsy fee and profit calculator",
    "ebay final value fee calculator",
    "square processing fee calculator",
    "saas cac payback period calculator",
    "gross margin vs markup calculator",
    "payoneer withdrawal fee calculator",
    "saas rule of 40 calculator",
    "paddle vs stripe fee calculator",
    "uk vat reverse calculator",
    "agency retainer margin calculator",
]

INTENT_WEIGHTS: dict[str, int] = {
    "fee": 25,
    "profit": 25,
    "margin": 25,
    "vat": 22,
    "tax": 20,
    "commission": 20,
    "roas": 24,
    "acos": 24,
    "break even": 24,
    "breakeven": 24,
    "pricing": 20,
    "rate": 18,
    "invoice": 18,
    "ltv": 22,
    "churn": 22,
    "cac": 22,
    "arr": 20,
    "mrr": 20,
    "fx": 20,
    "transfer": 18,
    "payout": 18,
    "markup": 18,
    "payback": 20,
    "calculator": 10,
}


def to_slug(keyword: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", keyword.strip().lower()).strip("-")
    return slug


def score_keyword(keyword: str) -> int:
    text = keyword.lower()
    score = 0
    for term, weight in INTENT_WEIGHTS.items():
        if term in text:
            score += weight
    if len(keyword.split()) >= 3:
        score += 10
    return score


def fetch_autocomplete(query: str, timeout: float = 4.0) -> list[str]:
    encoded = urllib.parse.quote(query)
    url = f"https://suggestqueries.google.com/complete/search?client=firefox&hl=en&q={encoded}"
    req = urllib.request.Request(url, headers={"User-Agent": "MarginKit-Miner/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode("utf-8", "ignore"))
    if isinstance(payload, list) and len(payload) > 1 and isinstance(payload[1], list):
        return [str(x).strip() for x in payload[1] if isinstance(x, str)]
    return []


def existing_tool_slugs(tools_dir: Path = TOOLS_DIR) -> set[str]:
    if not tools_dir.exists():
        return set()
    return {p.stem for p in tools_dir.glob("*.json")}


def merge_backlog(
    existing: list[dict[str, Any]],
    candidates: list[str],
    live_slugs: set[str],
) -> tuple[list[dict[str, Any]], int]:
    seen = set(live_slugs)
    for item in existing:
        if item.get("slug"):
            seen.add(item["slug"])

    now_iso = datetime.now(timezone.utc).isoformat()
    added = 0
    merged = list(existing)

    for kw in candidates:
        slug = to_slug(kw)
        if len(slug) < 8 or slug in seen:
            continue
        score = score_keyword(kw)
        if score < 25:
            continue
        seen.add(slug)
        merged.append(
            {
                "keyword": kw.strip(),
                "slug": slug,
                "score": score,
                "status": "pending",
                "created_at": now_iso,
            }
        )
        added += 1

    merged.sort(key=lambda x: (x.get("status") != "pending", -int(x.get("score", 0)), x.get("slug", "")))
    return merged, added


def run_miner(
    backlog_path: Path = BACKLOG_PATH,
    tools_dir: Path = TOOLS_DIR,
    fetch_online: bool = True,
) -> dict[str, int]:
    existing: list[dict[str, Any]] = []
    if backlog_path.exists():
        with backlog_path.open("r", encoding="utf-8") as fh:
            existing = json.load(fh)

    candidates: list[str] = []
    if fetch_online:
        for seed in SEEDS:
            try:
                suggestions = fetch_autocomplete(seed)
                candidates.extend(suggestions)
            except Exception:
                # Network blocks or transient timeouts should never break the pipeline.
                continue

    if len(candidates) < 5:
        candidates.extend(FALLBACK_CANDIDATES)

    live_slugs = existing_tool_slugs(tools_dir)
    merged, added = merge_backlog(existing, candidates, live_slugs)
    backlog_path.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    pending = sum(1 for item in merged if item.get("status") == "pending")
    return {"added": added, "pending": pending, "total": len(merged)}


if __name__ == "__main__":
    summary = run_miner()
    print(f"Keyword mining complete: +{summary['added']} new, {summary['pending']} pending, {summary['total']} total.")
