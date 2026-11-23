"""Pure Python 3.12 static site generator for MarginKit."""

from __future__ import annotations

import html
import json
import shutil
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
CONFIG_DIR = ROOT / "config"
TOOLS_DIR = ROOT / "tools"
SRC_DIR = ROOT / "src"
DIST_DIR = ROOT / "dist"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def url_for(base_path: str, sub_path: str) -> str:
    bp = base_path.rstrip("/")
    clean = "/" + sub_path.lstrip("/")
    if not bp:
        return clean
    return f"{bp}{clean}"


def canonical_for(base_url: str, sub_path: str) -> str:
    bu = base_url.rstrip("/")
    clean = "/" + sub_path.lstrip("/")
    return f"{bu}{clean}"


def render_head(
    *,
    site: dict[str, Any],
    monetization: dict[str, Any],
    title: str,
    description: str,
    canonical_url: str,
    json_ld_blocks: list[dict[str, Any]] | None = None,
) -> str:
    bp = site.get("base_path", "")
    adsense_client = (monetization.get("adsense_client") or "").strip()
    adsense_tag = ""
    if adsense_client:
        adsense_tag = (
            f'\n  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
            f'?client={esc(adsense_client)}" crossorigin="anonymous"></script>'
        )

    ld_tags = ""
    if json_ld_blocks:
        parts = []
        for block in json_ld_blocks:
            dumped = json.dumps(block, ensure_ascii=False).replace("</", "<\\/")
            parts.append(f'  <script type="application/ld+json">{dumped}</script>')
        ld_tags = "\n" + "\n".join(parts)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{esc(canonical_url)}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canonical_url)}">
  <meta property="og:site_name" content="{esc(site['site_name'])}">
  <link rel="stylesheet" href="{esc(url_for(bp, 'assets/style.css'))}">{adsense_tag}{ld_tags}
</head>"""


def render_header(site: dict[str, Any]) -> str:
    bp = site.get("base_path", "")
    return f"""<header class="site-header">
  <div class="container header-inner">
    <a class="brand" href="{esc(url_for(bp, '/'))}">
      <span class="brand-mark">M</span>
      <span>{esc(site['site_name'])}</span>
    </a>
    <nav class="site-nav" aria-label="Primary">
      <a href="{esc(url_for(bp, '/#tools'))}">Calculators</a>
      <a href="{esc(url_for(bp, 'about/'))}">About</a>
      <a href="{esc(url_for(bp, 'privacy/'))}">Privacy</a>
      <a href="{esc(url_for(bp, 'contact/'))}">Contact</a>
    </nav>
  </div>
</header>"""


def render_footer(site: dict[str, Any]) -> str:
    bp = site.get("base_path", "")
    year = site.get("copyright_year", 2026)
    return f"""<footer class="site-footer">
  <div class="container footer-inner">
    <div>&copy; {esc(year)} {esc(site['site_name'])}. Calculations are provided for informational planning purposes.</div>
    <div class="footer-links">
      <a href="{esc(url_for(bp, 'about/'))}">About</a>
      <a href="{esc(url_for(bp, 'privacy/'))}">Privacy Policy</a>
      <a href="{esc(url_for(bp, 'terms/'))}">Terms</a>
      <a href="{esc(url_for(bp, 'contact/'))}">Contact</a>
      <a href="{esc(url_for(bp, 'sitemap.xml'))}">Sitemap</a>
    </div>
  </div>
</footer>"""


def render_field(field: dict[str, Any]) -> str:
    fid = esc(field["id"])
    label = esc(field["label"])
    ftype = field.get("type", "number")
    hint_html = f'<span class="field-hint">{esc(field["hint"])}</span>' if field.get("hint") else ""

    if ftype == "select":
        opts = []
        for opt in field.get("options", []):
            selected = " selected" if opt.get("selected") else ""
            opts.append(f'<option value="{esc(opt["value"])}"{selected}>{esc(opt["label"])}</option>')
        control = f'<select id="{fid}" name="{fid}">{"".join(opts)}</select>'
        return f'<div class="field"><label for="{fid}">{label}</label>{control}{hint_html}</div>'

    if ftype == "checkbox":
        checked = " checked" if field.get("default") else ""
        return (
            f'<div class="field field-check">'
            f'<input type="checkbox" id="{fid}" name="{fid}"{checked}>'
            f'<label for="{fid}">{label}</label>'
            f"</div>"
        )

    attrs = [
        f'type="number"',
        f'id="{fid}"',
        f'name="{fid}"',
        f'value="{esc(field.get("default", 0))}"',
    ]
    if "min" in field:
        attrs.append(f'min="{esc(field["min"])}"')
    if "max" in field:
        attrs.append(f'max="{esc(field["max"])}"')
    if "step" in field:
        attrs.append(f'step="{esc(field["step"])}"')
    return f'<div class="field"><label for="{fid}">{label}</label><input {" ".join(attrs)}>{hint_html}</div>'


def render_ad_slot(monetization: dict[str, Any], slot_key: str) -> str:
    client = (monetization.get("adsense_client") or "").strip()
    slot_id = (monetization.get("adsense_slots", {}).get(slot_key) or "").strip()
    if not client or not slot_id:
        return ""
    return (
        f'<div class="ad-slot" aria-label="Advertisement">'
        f'<ins class="adsbygoogle" style="display:block" data-ad-client="{esc(client)}" '
        f'data-ad-slot="{esc(slot_id)}" data-ad-format="auto" data-full-width-responsive="true"></ins>'
        f"<script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>"
        f"</div>"
    )


def render_affiliate(monetization: dict[str, Any], category: str) -> str:
    aff = monetization.get("affiliates", {}).get(category)
    if not aff:
        return ""
    return f"""<aside class="affiliate-card" aria-label="Recommended resource">
  <div>
    <span class="tag">{esc(aff.get('badge', 'Recommended'))}</span>
    <h3>{esc(aff['title'])}</h3>
    <p>{esc(aff['description'])}</p>
    <p class="affiliate-disclosure">{esc(aff.get('disclosure', 'Partner link'))}</p>
  </div>
  <a class="btn btn-primary" href="{esc(aff['url'])}" target="_blank" rel="sponsored noopener noreferrer">{esc(aff['cta_text'])} &rarr;</a>
</aside>"""


def render_tool_page(
    tool: dict[str, Any],
    all_tools: dict[str, dict[str, Any]],
    site: dict[str, Any],
    monetization: dict[str, Any],
) -> str:
    bp = site.get("base_path", "")
    bu = site["base_url"]
    slug = tool["slug"]
    page_sub = f"tools/{slug}/"
    canonical_url = canonical_for(bu, page_sub)

    web_app_ld = {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": tool["title"],
        "url": canonical_url,
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "All",
        "description": tool["meta_description"],
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
    }
    faqs = tool.get("faqs", [])
    ld_blocks: list[dict[str, Any]] = [web_app_ld]
    if faqs:
        ld_blocks.append(
            {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": f["q"],
                        "acceptedAnswer": {"@type": "Answer", "text": f["a"]},
                    }
                    for f in faqs
                ],
            }
        )

    fields_html = "\n".join(render_field(f) for f in tool.get("inputs", []))
    outputs_html = []
    for out in tool.get("outputs", []):
        oid = esc(out["id"])
        cls = "kpi-card highlight" if out.get("highlight") else "kpi-card"
        outputs_html.append(
            f'<div class="{cls}" data-output-card="{oid}">'
            f'<div class="kpi-label" data-output-label="{oid}">{esc(out["label"])}</div>'
            f'<div class="kpi-value" id="out-{oid}">{esc(out.get("default", "$0.00"))}</div>'
            f"</div>"
        )

    chart_html = '<div class="chart-box" id="mk-chart" hidden></div>' if tool.get("chart") else ""

    faqs_html = "\n".join(
        f'<details class="faq-item"><summary>{esc(f["q"])}</summary><p>{esc(f["a"])}</p></details>'
        for f in faqs
    )

    related_cards = []
    for r_slug in tool.get("related", []):
        rt = all_tools.get(r_slug)
        if not rt:
            continue
        related_cards.append(
            f'<a class="related-link" href="{esc(url_for(bp, f"tools/{r_slug}/"))}">'
            f'{esc(rt["short_title"])}<span>{esc(rt["category_label"])}</span></a>'
        )

    related_section = ""
    if related_cards:
        related_section = f"""<section class="content-section">
  <h2>Related Calculators</h2>
  <div class="related-grid">{"".join(related_cards)}</div>
</section>"""

    head = render_head(
        site=site,
        monetization=monetization,
        title=f"{tool['title']} | {site['site_name']}",
        description=tool["meta_description"],
        canonical_url=canonical_url,
        json_ld_blocks=ld_blocks,
    )

    return f"""{head}
<body>
{render_header(site)}
<main>
  <div class="container">
    <nav class="breadcrumb" aria-label="Breadcrumb">
      <a href="{esc(url_for(bp, '/'))}">Home</a>
      <span>/</span>
      <span>{esc(tool['category_label'])}</span>
      <span>/</span>
      <span>{esc(tool['short_title'])}</span>
    </nav>

    <div class="tool-header">
      <span class="tag">{esc(tool['category_label'])}</span>
      <h1>{esc(tool['title'])}</h1>
      <p>{esc(tool['lead'])}</p>
    </div>

    {render_ad_slot(monetization, 'tool_top')}

    <div class="calc-grid">
      <section class="panel" aria-label="Inputs">
        <div class="panel-title">
          <span>Parameters</span>
          <button type="button" class="btn btn-ghost" id="mk-reset-btn">Reset</button>
        </div>
        <form id="mk-calc-form" class="form-stack" onsubmit="return false;">
          {fields_html}
        </form>
      </section>

      <section class="panel" aria-label="Results" aria-live="polite">
        <div class="panel-title">
          <span>Live Results</span>
          <button type="button" class="btn btn-primary" id="mk-copy-btn">Copy Summary</button>
        </div>
        <div class="kpi-grid">
          {"".join(outputs_html)}
        </div>
        <table class="breakdown-table" aria-label="Fee and margin breakdown">
          <thead><tr><th>Line Item</th><th>Value</th></tr></thead>
          <tbody id="mk-breakdown-body"></tbody>
        </table>
        {chart_html}
      </section>
    </div>

    {render_affiliate(monetization, tool.get('affiliate_key', tool['category']))}
    {render_ad_slot(monetization, 'tool_bottom')}

    <section class="content-section">
      <h2>Formula &amp; Methodology</h2>
      <div class="formula-box">{tool['formula_html']}</div>
    </section>

    <section class="content-section">
      <h2>Frequently Asked Questions</h2>
      <div class="faq-list">{faqs_html}</div>
    </section>

    {related_section}
  </div>
</main>
{render_footer(site)}
<script defer src="{esc(url_for(bp, 'assets/app.js'))}"></script>
<script defer src="{esc(url_for(bp, f'js/tools/{slug}.js'))}"></script>
</body>
</html>
"""


def render_home_page(
    tools: list[dict[str, Any]],
    site: dict[str, Any],
    monetization: dict[str, Any],
) -> str:
    bp = site.get("base_path", "")
    bu = site["base_url"]
    canonical_url = canonical_for(bu, "/")

    categories: dict[str, str] = {}
    for t in tools:
        categories[t["category"]] = t["category_label"]

    pills = ['<button type="button" class="pill active" data-filter="all">All Tools</button>']
    for cat_key, cat_label in categories.items():
        pills.append(f'<button type="button" class="pill" data-filter="{esc(cat_key)}">{esc(cat_label)}</button>')

    cards = []
    for t in tools:
        badge = f'<span class="badge-hot">{esc(t["badge"])}</span>' if t.get("badge") else ""
        search_blob = f"{t['title']} {t['short_title']} {t['category_label']} {t['meta_description']}"
        tool_href = url_for(bp, f"tools/{t['slug']}/")
        cards.append(
            f'<a class="tool-card" href="{esc(tool_href)}" '
            f'data-category="{esc(t["category"])}" data-search="{esc(search_blob)}">'
            f'<div class="tool-card-top"><span class="tag">{esc(t["category_label"])}</span>{badge}</div>'
            f'<h2>{esc(t["short_title"])}</h2>'
            f'<p>{esc(t["meta_description"])}</p>'
            f'<span class="tool-card-cta">Open calculator &rarr;</span>'
            f"</a>"
        )

    ld_site = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": site["site_name"],
        "url": canonical_url,
        "description": site["description"],
    }

    head = render_head(
        site=site,
        monetization=monetization,
        title=f"{site['site_name']} — {site['tagline']}",
        description=site["description"],
        canonical_url=canonical_url,
        json_ld_blocks=[ld_site],
    )

    return f"""{head}
<body>
{render_header(site)}
<main>
  <div class="container">
    <section class="hero">
      <span class="hero-kicker">100% Free &bull; Instant Client-Side Math</span>
      <h1>B2B Fee, Profit Margin &amp; SaaS Calculators</h1>
      <p>{esc(site['description'])}</p>
      <div class="directory-controls" id="tools">
        <div class="search-box">
          <label for="mk-search" class="sr-only" hidden>Search calculators</label>
          <input id="mk-search" type="search" placeholder="Search calculators (e.g. Stripe, VAT, Shopify, FX)..." autocomplete="off">
        </div>
        <div class="filter-pills" role="group" aria-label="Filter by category">
          {"".join(pills)}
        </div>
      </div>
    </section>

    <section aria-label="Calculator directory">
      <div class="tools-grid" id="mk-tools-grid">
        {"".join(cards)}
      </div>
      <div class="empty-state" id="mk-empty" style="display:none;">
        No calculators matched your search. Try clearing the filter.
      </div>
    </section>
  </div>
</main>
{render_footer(site)}
<script defer src="{esc(url_for(bp, 'assets/app.js'))}"></script>
</body>
</html>
"""


def render_prose_page(
    *,
    site: dict[str, Any],
    monetization: dict[str, Any],
    sub_path: str,
    title: str,
    description: str,
    body_html: str,
) -> str:
    bp = site.get("base_path", "")
    canonical_url = canonical_for(site["base_url"], sub_path)
    head = render_head(
        site=site,
        monetization=monetization,
        title=f"{title} | {site['site_name']}",
        description=description,
        canonical_url=canonical_url,
    )
    return f"""{head}
<body>
{render_header(site)}
<main>
  <div class="container">
    <article class="prose">
      {body_html}
    </article>
  </div>
</main>
{render_footer(site)}
<script defer src="{esc(url_for(bp, 'assets/app.js'))}"></script>
</body>
</html>
"""


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def build() -> dict[str, int]:
    site = load_json(CONFIG_DIR / "site.json")
    monetization = load_json(CONFIG_DIR / "monetization.json")

    tool_files = sorted(TOOLS_DIR.glob("*.json"))
    tools = [load_json(p) for p in tool_files]
    tools_by_slug = {t["slug"]: t for t in tools}

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    # Copy static assets
    shutil.copytree(SRC_DIR / "assets", DIST_DIR / "assets")
    shutil.copytree(SRC_DIR / "js", DIST_DIR / "js")

    # Home page
    write_text(DIST_DIR / "index.html", render_home_page(tools, site, monetization))

    # Tool pages
    sitemap_urls = [canonical_for(site["base_url"], "/")]
    for tool in tools:
        slug = tool["slug"]
        out_html = render_tool_page(tool, tools_by_slug, site, monetization)
        write_text(DIST_DIR / "tools" / slug / "index.html", out_html)
        sitemap_urls.append(canonical_for(site["base_url"], f"tools/{slug}/"))

    # Trust pages (AdSense compliance)
    email = esc(site.get("contact_email", "contact@marginkit.example"))
    site_name = esc(site["site_name"])
    bp = site.get("base_path", "")

    trust_pages = [
        (
            "about/",
            "About Us",
            f"Learn about {site['site_name']} and our transparent client-side financial calculators.",
            f"""<h1>About {site_name}</h1>
<p>{site_name} builds fast, transparent, zero-signup financial and operational calculators for e-commerce operators, SaaS teams, agencies, and independent contractors.</p>
<h2>How Our Calculators Work</h2>
<p>Every calculation executes directly in your browser using documented fee schedules and standard accounting formulas. We never upload your revenue, cost, or invoice figures to a server.</p>
<h2>Editorial &amp; Affiliate Transparency</h2>
<p>{site_name} is free to use. Some calculator pages include clearly labeled partner links or display advertising that helps fund ongoing maintenance and new calculator releases.</p>""",
        ),
        (
            "privacy/",
            "Privacy Policy",
            f"Privacy policy for {site['site_name']}: client-side processing, cookies, and analytics.",
            f"""<h1>Privacy Policy</h1>
<p>Last updated: {esc(site.get('copyright_year', 2026))}</p>
<h2>1. Calculator Inputs</h2>
<p>All numeric inputs entered into {site_name} calculators run locally in your web browser. We do not collect, transmit, or store your financial inputs on our servers.</p>
<h2>2. Advertising &amp; Third-Party Cookies</h2>
<p>If display advertising (such as Google AdSense) is enabled on this site, third-party vendors may use cookies to serve ads based on prior visits. You can opt out of personalized advertising through Google Ad Settings.</p>
<h2>3. Partner Links</h2>
<p>Clicking outbound partner links may set referral tracking cookies on the destination merchant's domain according to that merchant's privacy policy.</p>
<h2>4. Contact</h2>
<p>Questions about this policy can be sent to <a href="mailto:{email}">{email}</a>.</p>""",
        ),
        (
            "terms/",
            "Terms of Use",
            f"Terms of use and financial disclaimer for {site['site_name']}.",
            f"""<h1>Terms of Use</h1>
<h2>Informational Estimates Only</h2>
<p>The calculators on {site_name} provide estimates based on published rates and user-supplied inputs. Payment processors, tax authorities, marketplaces, and banks update fee schedules periodically. Always verify final figures on official invoices, tax filings, or processor statements.</p>
<h2>No Professional Advice</h2>
<p>Nothing on this site constitutes tax, legal, accounting, or investment advice.</p>""",
        ),
        (
            "contact/",
            "Contact",
            f"Get in touch with the {site['site_name']} team to report rate updates or request a calculator.",
            f"""<h1>Contact {site_name}</h1>
<p>Notice a fee schedule update, VAT rate change, or have a calculator request? Reach out anytime.</p>
<p>Email: <a href="mailto:{email}">{email}</a></p>
<p><a href="{esc(url_for(bp, '/'))}">&larr; Back to all calculators</a></p>""",
        ),
    ]

    for sub_path, ptitle, pdesc, pbody in trust_pages:
        write_text(
            DIST_DIR / sub_path.strip("/") / "index.html",
            render_prose_page(
                site=site,
                monetization=monetization,
                sub_path=sub_path,
                title=ptitle,
                description=pdesc,
                body_html=pbody,
            ),
        )
        sitemap_urls.append(canonical_for(site["base_url"], sub_path))

    # 404 page
    write_text(
        DIST_DIR / "404.html",
        render_prose_page(
            site=site,
            monetization=monetization,
            sub_path="404.html",
            title="Page Not Found",
            description="The requested calculator page could not be found.",
            body_html=f'<h1>Page Not Found</h1><p>That calculator does not exist or moved.</p><p><a class="btn btn-primary" href="{esc(url_for(bp, "/"))}">Browse All Calculators</a></p>',
        ),
    )

    # sitemap.xml, robots.txt, .nojekyll
    url_nodes = "\n".join(f"  <url><loc>{esc(u)}</loc></url>" for u in sitemap_urls)
    write_text(
        DIST_DIR / "sitemap.xml",
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{url_nodes}\n</urlset>\n',
    )
    write_text(
        DIST_DIR / "robots.txt",
        f"User-agent: *\nAllow: /\nSitemap: {canonical_for(site['base_url'], 'sitemap.xml')}\n",
    )
    write_text(DIST_DIR / ".nojekyll", "")

    return {"tools": len(tools), "urls": len(sitemap_urls)}


if __name__ == "__main__":
    stats = build()
    print(f"Built MarginKit: {stats['tools']} tools, {stats['urls']} sitemap URLs -> {DIST_DIR}")
