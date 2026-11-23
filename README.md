# MarginKit

Free, zero-dependency B2B financial, fee, VAT, SaaS, and FX calculators built with pure Python 3.12 static generation and client-side JavaScript.

Live URL: `https://ocean710010-dot.github.io/marginkit/`

## Project Structure

- `config/site.json` — Site branding, `base_url`, `base_path`, and contact email
- `config/monetization.json` — Google AdSense publisher ID & slot IDs + category affiliate CTA cards
- `tools/*.json` — Declarative calculator pages (inputs, outputs, formula docs, FAQs, related links)
- `src/js/tools/*.js` — Pure client-side calculation logic for each tool
- `build.py` — Static generator outputting `dist/` (HTML, JSON-LD, trust pages, `sitemap.xml`, `robots.txt`)
- `scripts/mine_keywords.py` — Long-tail B2B tool keyword miner populating `backlog.json`
- `tests/test_build.py` — Automated build, JSON-LD, base-path, and miner checks

## Local Build & Test

```powershell
py -3.12 build.py
py -3.12 -m unittest discover -s tests -v
py -3.12 scripts/mine_keywords.py
```

## Monetization Setup (AdSense + Affiliates)

1. Update `contact_email` in `config/site.json` before applying for Google AdSense.
2. Fill in `adsense_client` (e.g. `"ca-pub-XXXXXXXXXXXXXXXX"`) and `adsense_slots` in `config/monetization.json`.
3. Replace the default URLs under `affiliates` in `config/monetization.json` with your Shopify / Wise / Payoneer / PartnerStack tracking links.
4. Commit and push to `main` — GitHub Actions rebuilds and deploys automatically.

## Moving to a Custom Domain (Recommended for AdSense)

1. Change `base_url` in `config/site.json` to `"https://yourdomain.com"` and set `base_path` to `""`.
2. Add your domain in **GitHub Repository Settings → Pages → Custom domain** (or deploy `dist/` directly on Cloudflare Pages via `python build.py`).
3. Submit `https://yourdomain.com/sitemap.xml` in Google Search Console and Bing Webmaster Tools.

## Adding a New Calculator

1. Create `tools/<slug>.json` following the schema of `tools/stripe-fee-calculator.json`.
2. Create `src/js/tools/<slug>.js` using `window.MK.bindCalculator(...)`.
3. Run `py -3.12 build.py` and `py -3.12 -m unittest discover -s tests -v`, then commit & push.
