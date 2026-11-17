# Launch guide: replacing atmosbuild.com

Everything the live site needs is in the `site/` folder. It is plain HTML, CSS and JavaScript, so any static host can serve it. This guide assumes **Cloudflare**.

## 1. Confirm these before going live

These statements are on the site. Each one is a promise or a fact only you can verify. The review panel flagged the first three as the ones buyers will check first.

**Likely to block a bid list if left open**

| # | Where | What the site says | Check |
|---|---|---|---|
| 1 | Hero, FAQ, About | "Licensed & insured"; "carries liability insurance"; COI on request | **Confirmed by you (licensed and insured).** Keep the policy active. **The site says nothing about workers' compensation.** Property managers will ask. If you carry it, tell me and I'll add it; if you don't, expect it to block some bid lists |
| 2 | Property Managers | "Send us your additional-insured and endorsement requirements and we'll confirm them with our broker" | Confirm your broker can issue additional-insured endorsements |
| 3 | Everywhere | The business is "Atmos Design + Build" (footer: "Atmos Design Build, LLC") | Must match the name on your CSLB license record exactly |

**Process commitments (only keep the ones you will do every time)**

| # | Where | What the site promises |
|---|---|---|
| 4 | Form, hero, contact, thank-you | A reply within one business day, from a named project lead **(confirmed by you)** |
| 5 | Property Managers | A five-step occupied-unit protocol: notice schedule agreed with the office and who is on site each day, photo log before work, protection and dust control, keys signed out and units locked, daily cleanup and status update |
| 6 | Property Managers, STR | A day-by-day schedule with every bid, materials ordered before starting, a written heads-up if a date is at risk |
| 7 | Several pages | Itemized written bids, per-unit pricing for repeatable scopes, change orders approved in writing, regular photo updates |
| 8 | Hotel page | A model room first, a weekly count of rooms out of service, pricing per key and per room type |
| 9 | FAQ, Property Managers | Registering in a client's vendor compliance platform (roughly $100 a year per platform) |

**Facts and claims**

| # | Where | What the site says | Check |
|---|---|---|---|
| 10 | Hero, About, Portfolio | 25+ years, 100+ projects, $45M+ "project value represented" | Carried over unchanged from the old site. Three reviewers found "represented" vague. If you can define it (for example "combined value of projects we designed or built"), I'll reword it |
| 11 | Home, Multifamily, Landscape, Portfolio, About | 47 apartment communities designed, 500+ units; 8 communities complete, 5 under construction | Provided by you in November 2026. The portfolio page shows six of these communities |
| 12 | Every project card | An "Atmos role" and "Status" row (for example "Site & landscape design", "Under construction") | Taken from the old site's project pages. Correct any that have changed |
| 13 | Hotel page | "Hotels are a new focus for Atmos", with the model room as the first step | There are no hotel projects in the portfolio, and reviewers said an owner finds that gap in two clicks. Saying it plainly scored better with the hotel reviewer than implying experience. Remove the page if you don't want hotel leads yet |
| 14 | Hotel, Landscape | Pool work is built with a licensed pool contractor; landscape and irrigation installation by licensed landscape contractors or within a multi-trade renovation; stamped drawings from a licensed design professional | A B license covers multi-trade projects. Confirm you have these partners |
| 15 | Exterior page | Repairs from SB 721 balcony inspection reports (not the inspections) | Confirm you want this work |
| 16 | STR, Design, Hotel | Ordering and installing furniture and finishes; coordinating FF&E with a purchasing agent | Carried over from the old site's FAQ, narrowed after review |
| 17 | Testimonial | Eileen Molloy, "Client on three Atmos-designed communities" | SDRE Homebuyers is listed as the client on Woodline, Alder and Bower. One grammar fix was made: "attention to details were" became "attention to detail was". Confirm with her |
| 18 | Project pages | Client, building designer and general contractor credits | Copied from the old site. Confirm each firm is happy to be named |
| 19 | Privacy Policy, Terms | Adapted from your existing pages, dated November 14, 2026 | Have an attorney review. Update the date to your launch date |
| 20 | Handyman mentions | "Our sister handyman company" (no name or link) | When the brand launches, set `handyman_name` and `handyman_url` in `build.py` and rebuild. Every mention becomes a named link |

## 2. Deploy on Cloudflare

The repository is connected to Cloudflare as a Worker that serves the `site/` folder. `wrangler.jsonc` in the repository root tells Cloudflare what to serve, so the dashboard needs no build settings:

- **Build command:** leave empty
- **Deploy command:** `npx wrangler deploy` (the default)
- **Branch:** `claude/affectionate-euler-wf4gjj` (the repository has no `main` branch yet; switch this later if you create one)

Every change pushed to that branch deploys automatically. The Worker's overview page shows its preview address, ending in `.workers.dev`. That preview address sends a `noindex` header (set in `site/_headers`), so search engines index only your real domain.

If a deployment fails with a message about the Worker name, change `"name"` in `wrangler.jsonc` to the name shown in the dashboard.

**Turn on the bid form.** Cloudflare has no built-in form handling, so the form sends through Web3Forms (free for 250 requests a month).

1. Go to https://web3forms.com, enter the address that should receive bid requests (`info@atmosbuild.com`) and create an access key. It arrives by email.
2. Put the key in `form_access_key` at the top of `build.py`, run `python3 build.py`, commit and push. Or send me the key and I'll do it. The key is public by design, so it is safe to share.
3. Submit one test bid on the preview address and confirm the email arrives.

Until the key is set, the form shows a "please call or email us" message instead of sending, and the build prints a warning.

## 3. Point the domain

The old site treats `https://atmosbuild.com` (no `www`, no trailing slash) as the main address. Keep that, so Google's indexed URLs stay valid.

1. Open the Worker, go to **Settings → Domains & Routes → Add → Custom domain** and add `atmosbuild.com`. Add `www.atmosbuild.com` as well.
2. If the domain's DNS is already on Cloudflare, the records are created for you. If it's elsewhere, either move the nameservers to Cloudflare or add the CNAME record the dashboard shows.
3. Redirect `www` to the main address: in the domain's **Rules → Redirect Rules**, create a rule matching hostname `www.atmosbuild.com` that redirects to `https://atmosbuild.com` plus the original path, status 301.
4. HTTPS is issued automatically.
5. Cancel or unpublish the Framer site only after the new one is live on the domain.

**Using Netlify or Cloudflare Pages instead?** Connect the repository, leave the build command empty and set the output directory to `site`. The `_redirects` and `_headers` files and the form work unchanged.

## 4. Redirects from old URLs

`site/_redirects` already sends every retired URL to its closest new page:

| Old URL | New URL |
|---|---|
| `/services/building-design`, `/services/3d-rendering-visualization` | `/design-build` |
| `/services/interior-design-planning` | `/interior-renovation` |
| `/services/site-landscape-design` | `/landscape-hardscape` |
| `/services/consulting-services`, `/services/project-management`, `/services/feasibility-studies` | `/services` |
| `/design-lab` and everything under it | `/design-build` |
| `/portfolio/clairevue-copy` | `/portfolio/zig-zag` |
| `/portfolio/blooming-nook` | `/portfolio` |
| `/blogs` | `/` |
| `/reviews` | `/about` |

These URLs are unchanged: `/`, `/about`, `/services`, `/portfolio`, `/contact-us`, `/privacy-policy`, `/terms`, and the project pages for Laguna, Crestview, Woodline, Terraza, Alder, Bower, Sea Breeze, Slate, Takibi Supesu and Clairevue.

**Check before switching DNS.** On the preview address, run these and confirm the result:

```bash
curl -sI https://YOUR-PREVIEW-ADDRESS/portfolio | head -1
```

```bash
curl -sI https://YOUR-PREVIEW-ADDRESS/portfolio/laguna | head -1
```

```bash
curl -sI https://YOUR-PREVIEW-ADDRESS/services/building-design | head -3
```

The first two should return `200`. The third should return `301` with `location: /design-build`. After launch, open each old URL once and confirm it lands on a real page.

The `www` redirect is not in this file. It is set as a Redirect Rule in the Cloudflare dashboard (section 3).

## 5. Search engine setup

**Before switching DNS**
- In Google Search Console, add a **Domain property** for `atmosbuild.com` and verify it with the DNS TXT record. Export the Performance report (last 16 months) as a baseline.

**On launch day**
- Search Console → **Sitemaps** → submit `https://atmosbuild.com/sitemap.xml`.
- Use **URL Inspection → Request indexing** on the homepage and the eight audience and service pages.
- Bing Webmaster Tools → import the site from Search Console.
- Do not use Google's "Change of Address" tool. That is only for moving to a different domain.

**Google Business Profile**
- Name: exactly the licensed business name.
- Set up as a service-area business (address hidden), with San Diego County cities as service areas.
- Primary category: **General contractor**. Secondary: Remodeler, Construction company, Kitchen remodeler, Bathroom remodeler, Landscape designer. Do not choose "Landscaper" or "Landscape architect".
- Put "CA Lic. #1154511" in the description. Add one service per page on the site, upload project photos, and ask clients for reviews.
- Website link: `https://atmosbuild.com/?utm_source=google&utm_medium=organic&utm_campaign=gbp`

**Keep name, phone and address identical** everywhere: the site, Google, Bing Places, Apple Business Connect, LinkedIn, Instagram, Facebook, Yelp, Houzz, BBB.

**What's already built in**
- A unique title and description on every page, one H1 per page, canonical tags, Open Graph tags and a share image.
- Structured data on every page: the business as a `GeneralContractor` with the CSLB license, breadcrumbs, and a `Service` entry on each service page.
- `sitemap.xml` and `robots.txt`, regenerated on every build.
- Responsive WebP images with lazy loading, one self-hosted font file, no third-party scripts.

## 6. Analytics (optional, 5 minutes)

The site ships with no tracking. To add it, paste your provider's snippet into `src/partials/head.html` just above `</head>` and rebuild.

- **Plausible** or **Cloudflare Web Analytics**: lightweight, no cookie banner needed.
- **Google Analytics 4**: choose this if you plan to run Google Ads.

The site already reports three events to whichever of those is installed: `generate_lead` (bid form sent), `click_to_call` and `email_click`. In GA4, mark `generate_lead` as a key event.

If you add analytics that set cookies, update section 6 of the Privacy Policy.

## 7. Editing the site later

```bash
python3 build.py --serve
```

That rebuilds the site and opens a preview at http://localhost:8000. Requires Python 3 only.

| To change | Edit |
|---|---|
| Phone, email, license, handyman brand | `CONFIG` at the top of `build.py` |
| Page copy | `src/pages/<page>.html` |
| Header, footer, bid form | `src/partials/` |
| Projects | `src/projects.json` |
| Colors, type, layout | `site/assets/site.css` |

**Adding a project photo:**

```bash
python3 tools/optimize_images.py path/to/photo.jpg my-photo-name
```

Then reference `my-photo-name` in `src/projects.json` or a page and rebuild. After adding or changing a project, also run `python3 tools/make_og.py` to create its link-preview image. The build stops with a clear message if a link or image is broken, or a title or description is too long.

## 8. What to add as you win work

The site is honest about what Atmos has done so far. Every reviewer on the panel named the same gap: proof of completed renovation work for these buyers. These additions will raise conversion the most:

1. **A completed unit-turn or interior upgrade case study** with units, days per turn and cost per unit.
2. **A hospitality project**, even one model room, with photos. Until then, a named project lead with occupied-hotel experience is what a hotel owner will ask for.
3. **Two or three references and testimonials** from property managers, with name, title and company.
4. **A per-unit price sheet** for typical turn scopes (paint and flooring, light upgrade, full kitchen and bath).
5. **Your insurance limits** in dollars, workers' compensation status, and vendor platforms where you're approved.
6. **Association memberships** (SCRHA, IREM San Diego) once you've joined, shown in the trust bar.
7. **Finished photography** of the communities now under construction, to replace renderings.
8. **A finished short-term rental project**, with days offline.

See [REVIEW-PANEL.md](REVIEW-PANEL.md) for how the site scored and what the reviewers asked for.
