# PetPet Theme — documentation

Static documentation and support site for **PetPet Theme**, a Shopify Online Store 2.0
theme. Written in plain HTML and CSS: no framework, no build step at deploy time, so
GitHub Pages can serve it straight from the repository root.

Live site: <https://github-oneyue.github.io/petpet-theme-docs/>

| Page | Purpose |
| --- | --- |
| `index.html` | What the theme does, what it needs, and where to go next |
| `install.html` | Upload, publish, menus, pages, country selector, go-live checklist |
| `settings.html` | The seven global setting groups, with defaults |
| `sections.html` | All 31 sections and the fields each one exposes |
| `products.html` | Product blocks, variants, structured data, cart drawer |
| `accounts.html` | The seven customer account templates |
| `typography.html` | Font pickers, bundled typefaces, the type scale |
| `faq.html` | Demo content, filters, saved items, account behaviour |
| `support.html` | Contact channels, what to include, support scope |
| `changelog.html` | Release history |
| `404.html` | Custom not-found page |

## Publishing

1. Create an empty **public** repository named `petpet-theme-docs`.
2. Push this repository to it (`main` branch).
3. On GitHub: **Settings → Pages → Build and deployment → Source: Deploy from a branch**,
   branch `main`, folder `/ (root)`. Save.
4. Wait for the first build, then open <https://github-oneyue.github.io/petpet-theme-docs/>.

The `.nojekyll` file is intentional: it stops GitHub from running Jekyll over the site, so
files are served exactly as committed.

## Editing

Pages are assembled from fragments so the sidebar, table of contents and pager stay
consistent without being copied nine times.

```
_src/
  layout.html        shell: head, top bar, sidebar slot, TOC slot, footer
  pages/*.html       page content only (eyebrow, h1, lede, body)
  build.py           assembles the above into the .html files at the repo root
assets/
  docs.css           one stylesheet
  docs.js            sidebar toggle, TOC highlighting, copy buttons
  fonts.css          @font-face for the four bundled typefaces
  fonts/*.woff2      Latin subsets only, copied from the theme
  PF-FONT-LICENSES.txt
```

After editing anything under `_src/`, rebuild:

```bash
python _src/build.py
```

The script adds `id` attributes to `h2`/`h3`, builds the "on this page" list from them,
marks the current page in the sidebar, and wires the previous/next links. It does not
touch `assets/`.

### Changing the address

`_src/build.py` holds three constants at the top — `BASE_URL`, `REPO_URL`, `EMAIL`. Every
absolute URL and the support mailbox come from those. If the site moves to a custom
domain, change `BASE_URL` and rerun the build.

`sections.html` and `settings.html` are generated from the theme itself by a separate
script that reads `config/settings_schema.json` and each section's `{% schema %}` block,
so their tables cannot drift from the code. Rerun that generator after changing a schema.

## Typography licensing

The four bundled typefaces — DM Sans, Instrument Serif, DM Mono, Noto Sans SC — are
licensed under the **SIL Open Font License 1.1**, which permits commercial use,
modification and self-hosting. The licence texts must travel with the font files:
`assets/PF-FONT-LICENSES.txt`. Do not delete it.

## Content licence

Documentation text © 2026 Soho Digital. The theme itself is licensed to the buyer under
the terms of the Theme Store purchase; this repository covers the documentation only.
