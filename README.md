# Atmos Design + Build website

The website for [atmosbuild.com](https://atmosbuild.com): renovation and landscape services for property managers, multifamily owners, hotels and short-term rentals in San Diego.

It is a static site with no framework and no build dependencies beyond Python 3.

## Preview it

```bash
python3 build.py --serve
```

Open http://localhost:8000.

## Deploy it

Publish the `site/` folder. On Cloudflare Pages, connect this repository, leave the build command empty and set the output directory to `site`.

Full steps for domain, forms, redirects and search-engine setup are in [docs/LAUNCH.md](docs/LAUNCH.md).

## What's where

| Path | What it is |
|---|---|
| `site/` | The finished site. Deploy this folder |
| `src/pages/` | Copy for each page |
| `src/partials/` | Header, footer, bid form and `<head>` shared by every page |
| `src/projects.json` | Portfolio projects. Each entry becomes a project page and a card |
| `build.py` | Assembles pages into `site/`, writes the sitemap, and checks for broken links |
| `tools/optimize_images.py` | Converts a photo into responsive WebP files for the site |
| `tools/make_og.py` | Creates the link-preview image for each project page |
| `docs/LAUNCH.md` | Go-live checklist, including what to confirm before launch |
| `docs/REVIEW-PANEL.md` | How the site scored with six reviewers over three rounds |
| `docs/RESEARCH.md` | Market, competitor and SEO research behind the redesign |

Site-wide facts (phone, email, license number, the bid form access key, the sister handyman brand) live in `CONFIG` at the top of `build.py`.

After any change, run `python3 build.py` and commit the result. The build fails with a clear message if a link or image is broken.
