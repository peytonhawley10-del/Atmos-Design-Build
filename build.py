#!/usr/bin/env python3
"""Static site builder for atmosbuild.com. Python 3 standard library only.

    python3 build.py           render src/ into site/ and run the checks
    python3 build.py --serve   same, then preview at http://localhost:8000

Edit page copy in src/pages/, shared header/footer/form in src/partials/, projects in
src/projects.json and the site-wide facts in CONFIG below. Deploy the site/ folder.
"""
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC, OUT = ROOT / "src", ROOT / "site"
SITE = "https://atmosbuild.com"

CONFIG = {
    "phone": "(619) 736-7590",
    "tel": "+16197367590",
    "email": "peyton@atmosbuild.com",
    "license": "1154511",
    "cslb": "https://www.cslb.ca.gov/OnlineServices/CheckLicenseII/LicenseDetail.aspx?LicNum=1154511",
    "year": str(date.today().year),
    # Bid form delivery. Get a free access key at https://web3forms.com (enter the address that should receive
    # bid requests; the key arrives by email). The key is public by design. Until it is set, the form shows
    # its "call or email us" fallback instead of sending.
    "form_endpoint": "https://api.web3forms.com/submit",
    "form_access_key": "a2f435dc-363b-4db0-a9e0-44f24e37f802",
    # Sister handyman brand. Leave both empty until it launches; the copy then reads
    # "our sister handyman company" and small jobs route through the bid form.
    "handyman_name": "",
    "handyman_url": "",
}

PHONE_SIZES = "(max-width: 760px) 66vw, 100vw"
IMAGES = json.loads((SRC / "images.json").read_text())
PROJECTS = json.loads((SRC / "projects.json").read_text())
ICONS = json.loads((SRC / "icons.json").read_text())
PARTIALS = {p.stem: p.read_text() for p in (SRC / "partials").glob("*.html")}
CATEGORY = {"multifamily": "Multifamily", "interior": "Interior renovation",
            "outdoor": "Exterior & outdoor living", "residential": "Residential renovation"}


def esc(s):
    return html.escape(s, quote=True)


def img(name, alt="", sizes="100vw", cls="", eager=""):
    m = IMAGES[name]
    if sizes.endswith("100vw"):
        # ponytail: phones with 3x screens get 2x-quality images (about half the bytes). Remove if photos look soft.
        sizes = sizes[:-5] + PHONE_SIZES
    srcset = ", ".join(f"/assets/img/{name}-{w}.webp {w}w" for w in m["widths"])
    src = m["widths"][min(1, len(m["widths"]) - 1)]
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return (f'<img src="/assets/img/{name}-{src}.webp" srcset="{srcset}" sizes="{sizes}" '
            f'width="{m["w"]}" height="{m["h"]}" alt="{esc(alt)}" {load}{c}>')


def icon(name, cls=""):
    return (f'<svg class="icon {cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


def btn(href, label, variant="", ico="chevrons-right"):
    cls = f"btn btn--{variant}" if variant else "btn"
    href = MACROS["bid"]() if href == "bid" else href
    return f'<a class="{cls}" href="{href}"><span class="btn__icon">{icon(ico)}</span><span>{label}</span></a>'


def tag(label, ico="layers"):
    return f'<p class="tag"><span class="tag__icon">{icon(ico)}</span>{label}</p>'


def handyman():
    if CONFIG["handyman_url"]:
        return f'<a href="{CONFIG["handyman_url"]}" rel="noopener">{esc(CONFIG["handyman_name"])}</a>, our sister handyman company'
    return "our sister handyman company"


def project_facts(p):
    scale = ("Units", p["units"]) if p.get("units") else ("Size", p.get("size"))
    facts = [("Atmos role", p["role"]), scale, ("Location", p["location"]), ("Year", p.get("year")), ("Status", p["status"])]
    return [(k, v) for k, v in facts if v]


ON_PROJECTS = [False]  # rendering badges show only on the projects pages


def pos(p):
    return f' style="--pos:{p["cover_pos"]}"' if p.get("cover_pos") else ""


def cards(slugs=""):
    """Project cards in the original site's style: dark info panel + image."""
    chosen = [p for p in PROJECTS if p["slug"] in slugs.split(",")] if slugs else PROJECTS
    if slugs:
        chosen.sort(key=lambda p: slugs.split(",").index(p["slug"]))
    out = []
    for p in chosen:
        facts = "".join(f"<li><span>{k}</span>{esc(v)}</li>" for k, v in project_facts(p))
        out.append(
            f'<a class="pcard" href="/portfolio/{p["slug"]}" data-cat="{p["category"]}">'
            f'<div class="pcard__info"><div><h3>{esc(p["name"])}</h3>'
            f'<p class="pcard__type">{CATEGORY[p["category"]]} <span>&mdash;</span> {esc(p["type"])}</p></div>'
            f'<ul class="pcard__facts">{facts}</ul>'
            f'<span class="pcard__more">View project {icon("arrow-up-right")}</span></div>'
            f'<div class="pcard__img"{pos(p)}>{img(p["cover"], p["cover_alt"], "(min-width: 900px) 60vw, 100vw")}'
            + (f'<span class="badge">{esc(p["badge"])}</span>' if p.get("badge") and ON_PROJECTS[0] else "")
            + "</div></a>")
    return f'<div class="pcards">{"".join(out)}</div>'


def compare(before, after, before_alt, after_alt):
    """Before/after slider. A native range input drives a CSS variable."""
    return (f'<div class="compare" style="--pos:50%">'
            f'{img(after, after_alt, "(min-width: 900px) 50vw, 100vw")}'
            f'<div class="compare__before">{img(before, before_alt, "(min-width: 900px) 50vw, 100vw")}</div>'
            f'<span class="compare__label compare__label--b">Before</span><span class="compare__label compare__label--a">After</span>'
            f'<span class="compare__handle" aria-hidden="true">{icon("chevrons")}</span>'
            f'<input type="range" min="0" max="100" value="50" aria-label="Drag to compare before and after"></div>')


MACROS = {
    "img": img, "icon": icon, "btn": btn, "tag": tag, "cards": cards, "compare": compare,
    "handyman": handyman,
    "include": lambda name: PARTIALS[name],
    **{k: (lambda v=v: v) for k, v in CONFIG.items()},
}
MACRO_RE = re.compile(r"\{\{(\w+)(?::(.*?))?\}\}", re.S)


def expand(text):
    for _ in range(6):  # partials may contain macros
        new = MACRO_RE.sub(lambda m: MACROS[m.group(1)](*(m.group(2).split("|") if m.group(2) else [])), text)
        if new == text:
            return new
        text = new
    raise RuntimeError("macro expansion did not settle")


def business_ld():
    return {
        "@type": "GeneralContractor", "@id": f"{SITE}/#business", "name": "Atmos Design + Build",
        "url": f"{SITE}/", "logo": f"{SITE}/assets/icon-512.png", "image": f"{SITE}/assets/og.jpg",
        "description": "San Diego design-build general contractor renovating multifamily, hotel and short-term rental "
                       "properties: interiors, exteriors and landscape, from design and material selection through turnkey build-out.",
        "telephone": CONFIG["tel"], "email": CONFIG["email"],
        "address": {"@type": "PostalAddress", "addressLocality": "San Diego", "addressRegion": "CA", "addressCountry": "US"},
        "areaServed": {"@type": "AdministrativeArea", "name": "San Diego County, CA"},
        "hasCredential": {"@type": "EducationalOccupationalCredential",
                          "name": f"California Class B General Building Contractor License #{CONFIG['license']}",
                          "credentialCategory": "license", "identifier": CONFIG["license"], "url": CONFIG["cslb"],
                          "recognizedBy": {"@type": "GovernmentOrganization", "name": "Contractors State License Board",
                                           "url": "https://www.cslb.ca.gov/"}},
        "sameAs": ["https://www.instagram.com/atmosdesign_build/", "https://www.linkedin.com/company/atmos-design-build/",
                   "https://www.facebook.com/people/Atmos-Design-Build/61592077359168/"],
    }


def crumbs_ld(trail):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(trail)]}


def render(path, meta, body):
    """path is the clean URL ('/', '/about', '/portfolio/laguna')."""
    url = SITE + path
    has_form = "{{include:form}}" in body
    MACROS["bid"] = lambda: "#bid" if has_form else "/contact-us#bid"
    ON_PROJECTS[0] = path.startswith("/portfolio")
    graph = [business_ld()]
    if path == "/":
        graph.append({"@type": "WebSite", "@id": f"{SITE}/#website", "url": f"{SITE}/", "name": "Atmos Design + Build",
                      "publisher": {"@id": f"{SITE}/#business"}})
    trail = [("Home", "/")]
    if meta.get("parent"):
        name, purl = meta["parent"].split("|")
        trail.append((name, purl))
    if path != "/":
        trail.append((meta.get("crumb", meta["title"].split(" | ")[0]), path))
        graph.append(crumbs_ld(trail))
    if meta.get("service"):
        graph.append({"@type": "Service", "@id": f"{url}#service", "name": meta["service"], "serviceType": meta["service"],
                      "provider": {"@id": f"{SITE}/#business"}, "url": url,
                      "areaServed": {"@type": "AdministrativeArea", "name": "San Diego County, CA"}})
    og = f"assets/og/{path.strip('/').replace('/', '_')}.jpg"  # per-page preview image if one exists
    head = PARTIALS["head"].format(
        title=esc(meta["title"]), description=esc(meta["description"]), url=url,
        og_image=f"{SITE}/{og if (OUT / og).is_file() else 'assets/og.jpg'}",
        robots='<meta name="robots" content="noindex">' if meta.get("noindex") else "",
        preload=meta.get("preload", ""),
        ld=json.dumps({"@context": "https://schema.org", "@graph": graph}, separators=(",", ":")))
    page = (head + f'<body class="{meta.get("class", "")}">' + PARTIALS["header"]
            + f'<main id="main">{body}</main>' + PARTIALS["footer"] + "</body></html>\n")
    return expand(page)


def read_page(file):
    head, body = file.read_text().split("\n---\n", 1)
    meta = dict(line.split(": ", 1) for line in head.splitlines() if line.strip())
    return meta, body


def project_page(p):
    spec = [("Client", p.get("client")), ("Type", p["type"]), ("Units", p.get("units")), ("Size", p.get("size")),
            ("Location", p["location"]), ("Year", p.get("year")), ("Atmos scope", p["services"]), ("Status", p["status"])]
    spec_html = "".join(f"<div><dt>{k}</dt><dd>{esc(v)}</dd></div>" for k, v in spec if v)
    body = [f'<section class="phero"><div class="wrap"><p class="crumbs"><a href="/portfolio">Projects</a> / {esc(p["name"])}</p>'
            f'{{{{tag:{CATEGORY[p["category"]]}|image}}}}<h1>{esc(p["name"])}</h1><p class="lead">{esc(p["summary"])}</p></div>'
            f'<div class="wrap"><div class="phero__img"{pos(p)}>{img(p["cover"], p["cover_alt"], "(min-width: 1400px) 1340px, 100vw", "", "1")}'
            + (f'<span class="badge">{esc(p["badge"])}</span>' if p.get("badge") else "") + "</div></div></section>",
            f'<section class="section"><div class="wrap pgrid"><dl class="spec">{spec_html}</dl><div class="prose">']
    for block in p.get("body", []):
        body.append(f"<h2>{esc(block['h'])}</h2>" + "".join(f"<p>{esc(t)}</p>" for t in block.get("p", []))
                    + ("<ul>" + "".join(f"<li>{esc(t)}</li>" for t in block["ul"]) + "</ul>" if block.get("ul") else ""))
    if p.get("credits"):
        body.append("<h2>Credits</h2><ul>" + "".join(f"<li>{esc(c)}</li>" for c in p["credits"]) + "</ul>")
    body.append("</div></div></section>")
    if p.get("before"):
        b, a = p["before"], p["after"]
        body.append('<section class="section section--sand"><div class="wrap"><div class="shead">{{tag:Before &amp; after|image}}'
                    f'<h2>{esc(p.get("compare_h", "Drag to compare"))}</h2></div>'
                    f'<div class="compare-wrap">{compare(b["img"], a["img"], b["alt"], a["alt"])}</div></div></section>')
    if p.get("gallery"):
        figs = "".join(f'<figure>{img(g["img"], g["alt"], "(min-width: 900px) 50vw, 100vw")}'
                       f'<figcaption>{esc(g["cap"])}</figcaption></figure>' for g in p["gallery"])
        body.append('<section class="section"><div class="wrap"><div class="shead">{{tag:Project gallery|image}}'
                    f'<h2>Inside the project</h2></div><div class="gallery">{figs}</div></div></section>')
    others = [q["slug"] for q in PROJECTS if q["slug"] != p["slug"] and q["category"] == p["category"]][:2]
    others += [q["slug"] for q in PROJECTS if q["slug"] != p["slug"] and q["slug"] not in others][:2 - len(others)]
    body.append('<section class="section section--sand"><div class="wrap"><div class="shead shead--row"><div>{{tag:More projects|layers}}'
                '<h2>Keep exploring</h2></div>{{btn:/portfolio|View all projects|light}}</div>'
                f'{{{{cards:{",".join(others)}}}}}</div></section>' + "{{include:form}}")
    meta = {"title": p["title"], "description": p["description"], "parent": "Projects|/portfolio", "crumb": p["name"]}
    return meta, "".join(body)


def check(pages):
    """Fail the build on broken internal links, missing files or SEO limits."""
    errors, valid = [], set(pages) | {"/"}
    for path, (meta, out) in pages.items():
        if len(meta["title"]) > 60:
            errors.append(f"{path}: title is {len(meta['title'])} chars (max 60)")
        if not 70 <= len(meta["description"]) <= 160:
            errors.append(f"{path}: description is {len(meta['description'])} chars (70-160)")
        if len(re.findall(r"<h1[ >]", out)) != 1:
            errors.append(f"{path}: needs exactly one <h1>")
        if "{{" in out:
            errors.append(f"{path}: unexpanded macro")
        for ref in set(re.findall(r'(?:href|src)="(/[^"#?]*)', out)) | set(re.findall(r"(/assets/[^\s\",)]+)", out)):
            if ref not in valid and not (OUT / ref.lstrip("/")).is_file():
                errors.append(f"{path}: broken reference {ref}")
        for anchor in set(re.findall(r'href="#([\w-]+)"', out)):
            if f'id="{anchor}"' not in out:
                errors.append(f"{path}: missing anchor #{anchor}")
    for line in (OUT / "_redirects").read_text().splitlines():  # every redirect must leave a dead URL for a live one
        parts = line.split()
        if len(parts) >= 2 and parts[0].startswith("/"):
            src, dst = parts[0], parts[1]
            if src in valid:
                errors.append(f"_redirects: {src} is a live page")
            if dst.startswith("/") and dst not in valid:
                errors.append(f"_redirects: target {dst} does not exist")
    titles = [m["title"] for m, _ in pages.values()]
    errors += [f"duplicate title: {t}" for t in set(titles) if titles.count(t) > 1]
    if errors:
        sys.exit("BUILD CHECK FAILED\n  " + "\n  ".join(errors))


def build():
    pages = {}
    for file in sorted((SRC / "pages").glob("*.html")):
        meta, body = read_page(file)
        path = "/" if file.stem == "index" else "/" + file.stem
        pages[path] = (meta, render(path, meta, body))
    for p in PROJECTS:
        meta, body = project_page(p)
        path = "/portfolio/" + p["slug"]
        pages[path] = (meta, render(path, meta, body))
    for path, (meta, out) in pages.items():
        dest = OUT / ("index.html" if path == "/" else path.lstrip("/") + ".html")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(out)
    listed = [p for p, (m, _) in pages.items() if not m.get("noindex") and p != "/404"]
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{SITE}{'/' if p == '/' else p}</loc></url>\n" for p in listed)
        + "</urlset>\n")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    check(pages)
    if not CONFIG["form_access_key"]:
        print("WARNING: form_access_key is empty in build.py, so the bid form will not deliver requests yet")
    print(f"built {len(pages)} pages -> {OUT}")


def serve(port=8000):
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=str(OUT), **k)

        def translate_path(self, path):  # clean URLs: /about -> about.html, like Netlify
            p = super().translate_path(path)
            return p + ".html" if not Path(p).is_file() and Path(p + ".html").exists() else p

        def log_message(self, *a):
            pass

    print(f"preview: http://localhost:{port}")
    ThreadingHTTPServer(("", port), Handler).serve_forever()


if __name__ == "__main__":
    build()
    if "--serve" in sys.argv:
        serve()
