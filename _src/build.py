"""Build the PetPet Theme documentation site.

Source fragments in _src/pages/*.html contain page content only: an optional
<p class="eyebrow">, an <h1>, a <p class="lede">, then plain HTML. This script
wraps them in _src/layout.html, adds heading anchors, builds the "on this page"
list from the h2/h3 order, and writes flat .html files to the repo root so that
GitHub Pages can serve them directly with no build step at deploy time.

Run:  python _src/build.py
"""

from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_src"
PAGES_DIR = SRC / "pages"

VERSION = "1.0.2"
SITE = "PetPet Theme Documentation"

# Change these three if the site moves. They are the only place the public
# address appears; every page and the theme's theme_info block read from here.
BASE_URL = "https://github-oneyue.github.io/petpet-theme-docs"
REPO_URL = "https://github.com/github-oneyue/petpet-theme-docs"
EMAIL = "oneyue24@gmail.com"

# slug, nav label, nav group, page title, meta description
PAGES = [
    ("index", "Overview", "Start here", "Overview",
     "What PetPet Theme is, what it needs, and where to go next."),
    ("install", "Installation", "Start here", "Installation",
     "Upload, publish and configure PetPet Theme on a Shopify store in four steps."),
    ("settings", "Theme settings", "Reference", "Theme settings",
     "Every global setting in the theme editor: brand, runway, product copy, colours, typography, layout."),
    ("sections", "Sections", "Reference", "Section reference",
     "All 31 sections with the settings each one exposes."),
    ("products", "Product & cart", "Reference", "Product page and cart",
     "Product template blocks, variant handling, structured data and the cart drawer."),
    ("accounts", "Customer accounts", "Reference", "Customer accounts",
     "The seven account templates, address forms and the difference between account types."),
    ("typography", "Typography & fonts", "Reference", "Typography and fonts",
     "Bundled typefaces, Shopify font pickers, the type scale and licensing."),
    ("faq", "FAQ & troubleshooting", "Help", "FAQ and troubleshooting",
     "Common questions about demo content, filters, images and storefront behaviour."),
    ("support", "Support", "Help", "Support",
     "How to get help, what to include in a request and what is covered."),
    ("changelog", "Changelog", "Help", "Changelog",
     "Release history for PetPet Theme."),
]

NAV_GROUPS = ["Start here", "Reference", "Help"]


def slugify(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text).lower()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "section"


def strip_tags(text: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", text)).strip()


def add_anchors(content: str) -> tuple[str, list[tuple[int, str, str]]]:
    """Give every h2/h3 an id and return (content, [(level, id, text)])."""
    seen: dict[str, int] = {}
    headings: list[tuple[int, str, str]] = []

    def repl(match: re.Match[str]) -> str:
        level, attrs, inner = int(match.group(1)), match.group(2) or "", match.group(3)
        existing = re.search(r'id="([^"]+)"', attrs)
        anchor = existing.group(1) if existing else slugify(inner)
        if not existing:
            count = seen.get(anchor, 0)
            seen[anchor] = count + 1
            if count:
                anchor = f"{anchor}-{count + 1}"
        headings.append((level, anchor, strip_tags(inner)))
        if existing:
            return match.group(0)
        return f'<h{level} id="{anchor}"{attrs}>{inner}</h{level}>'

    content = re.sub(r"<h([23])([^>]*)>(.*?)</h\1>", repl, content, flags=re.S)
    return content, headings


def build_toc(headings: list[tuple[int, str, str]]) -> str:
    label = '    <p class="toc__label">On this page</p>'
    if not headings:
        return f"{label}\n    <ul></ul>"

    # Group h3s under the h2 that precedes them; a page with h3s but no h2
    # still renders, as a flat list of anchors.
    groups: list[tuple[str | None, str | None, list[tuple[str, str]]]] = []
    for level, anchor, text in headings:
        if level == 2:
            groups.append((anchor, text, []))
        elif groups:
            groups[-1][2].append((anchor, text))
        else:
            groups.append((None, None, [(anchor, text)]))

    out = [label, "    <ul>"]
    for anchor, text, children in groups:
        if anchor is None:
            for child_anchor, child_text in children:
                out.append(f'      <li><a href="#{child_anchor}">{html.escape(child_text)}</a></li>')
            continue
        out.append(f'      <li><a href="#{anchor}">{html.escape(text)}</a>')
        if children:
            out.append("        <ul>")
            for child_anchor, child_text in children:
                out.append(f'          <li><a href="#{child_anchor}">{html.escape(child_text)}</a></li>')
            out.append("        </ul>")
        out.append("      </li>")
    out.append("    </ul>")
    return "\n".join(out)


def build_nav(current: str) -> str:
    blocks = []
    for group in NAV_GROUPS:
        items = [p for p in PAGES if p[2] == group]
        if not items:
            continue
        lines = [f'      <p class="sidebar__label">{group}</p>', "      <ul>"]
        for slug, label, _group, _title, _desc in items:
            current_attr = ' aria-current="page"' if slug == current else ""
            lines.append(f'        <li><a href="{slug}.html"{current_attr}>{label}</a></li>')
        lines.append("      </ul>")
        blocks.append('    <div class="sidebar__group">\n' + "\n".join(lines) + "\n    </div>")
    return "\n".join(blocks)


def build_pager(current: str) -> str:
    slugs = [p[0] for p in PAGES]
    if current not in slugs:
        return ""
    i = slugs.index(current)
    parts = []
    if i > 0:
        prev_slug, prev_label = PAGES[i - 1][0], PAGES[i - 1][1]
        parts.append(
            f'    <div class="pager"><a class="pager__prev" href="{prev_slug}.html">'
            f'<span>Previous</span>{prev_label}</a>'
        )
    else:
        parts.append('    <div class="pager"><span></span>')
    if i < len(PAGES) - 1:
        nxt_slug, nxt_label = PAGES[i + 1][0], PAGES[i + 1][1]
        parts.append(
            f'<a class="pager__next" href="{nxt_slug}.html"><span>Next</span>{nxt_label}</a>'
        )
    parts.append("</div>")
    return "".join(parts)


def render(slug: str, title: str, desc: str, content: str, layout: str) -> str:
    content = (
        content.replace("{{REPO}}", REPO_URL)
        .replace("{{EMAIL}}", EMAIL)
        .replace("{{BASE}}", BASE_URL)
        .replace("{{VERSION}}", VERSION)
    )
    content, headings = add_anchors(content)
    page_title = title if slug == "index" else f"{title} — PetPet Theme"
    canonical = f"{BASE_URL}/" if slug == "index" else f"{BASE_URL}/{slug}.html"
    out = layout
    out = out.replace("{{TITLE}}", html.escape(f"{page_title} · {SITE}" if slug == "index" else page_title))
    out = out.replace("{{DESC}}", html.escape(desc))
    out = out.replace("{{CANONICAL}}", canonical)
    out = out.replace("{{REPO}}", REPO_URL)
    out = out.replace("{{VERSION}}", VERSION)
    out = out.replace("{{NAV}}", build_nav(slug))
    out = out.replace("{{CONTENT}}", content.rstrip())
    out = out.replace("{{PAGER}}", build_pager(slug))
    out = out.replace("{{TOC}}", build_toc(headings))
    return out


def main() -> None:
    layout = (SRC / "layout.html").read_text(encoding="utf-8")
    written = []

    for slug, _label, _group, title, desc in PAGES:
        fragment = (PAGES_DIR / f"{slug}.html").read_text(encoding="utf-8")
        html_out = render(slug, title, desc, fragment, layout)
        (ROOT / f"{slug}.html").write_text(html_out, encoding="utf-8")
        written.append(slug)

    notfound = (PAGES_DIR / "404.html").read_text(encoding="utf-8")
    notfound = (
        notfound.replace("{{REPO}}", REPO_URL)
        .replace("{{EMAIL}}", EMAIL)
        .replace("{{BASE}}", BASE_URL)
        .replace("{{VERSION}}", VERSION)
    )
    out = layout.replace("{{TITLE}}", f"Page not found · {SITE}")
    out = out.replace("{{DESC}}", "That page does not exist in the PetPet Theme documentation.")
    out = out.replace("{{CANONICAL}}", f"{BASE_URL}/404.html")
    out = out.replace("{{REPO}}", REPO_URL)
    out = out.replace("{{VERSION}}", VERSION)
    out = out.replace("{{NAV}}", build_nav(""))
    out = out.replace("{{CONTENT}}", notfound.rstrip())
    out = out.replace("{{PAGER}}", "")
    out = out.replace("{{TOC}}", '    <p class="toc__label">On this page</p>\n    <ul></ul>')
    (ROOT / "404.html").write_text(out, encoding="utf-8")
    written.append("404")

    print(f"built {len(written)} pages: {', '.join(written)}")


if __name__ == "__main__":
    main()
