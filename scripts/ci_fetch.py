#!/usr/bin/env python3
"""Côte d'Ivoire: laws published by the Assemblée nationale (https://www.assnat.ci, rubrique
"LOIS") plus the Constitution and the Code électoral offered on the same site.
Usage: python3 ci_fetch.py [--no-download]"""
import html
import json
import os
import re
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ci_text as T  # noqa

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(os.path.dirname(REPO), "_raw", "ci")
BASE = "https://www.assnat.ci/"
RETRIEVED = os.environ.get("LC_RETRIEVED", "2026-10-13")
os.environ.setdefault("LC_TESSDATA", os.path.join(os.path.dirname(REPO), "_raw", "ci", "tessdata"))
SIDEBAR = {"CONSTITUTION.pdf", "Code-Electoral.pdf", "liste_des_depute_anci.pdf",
           "reglement-assembleenationaledecotedivoire.pdf"}
DL = "--no-download" not in sys.argv


def page(url, dest):
    if DL:
        T.fetch(url, dest, delay=2)
    return open(dest, encoding="utf-8", errors="replace").read() if os.path.exists(dest) else ""


def listing():
    arts = []
    start = 0
    while True:
        s = page(BASE + "?-lois-82-" + ("&debut_articles=%d" % start if start else ""), os.path.join(RAW, "list", "%d.html" % start))
        found = 0
        for m in re.finditer(r'<a[^>]*href="\./\?([^"#&]+)"[^>]*>\s*([^<]*?LOI[^<]*?)\s*</a>', s, re.I):
            slug, title = m.group(1), html.unescape(re.sub(r"\s+", " ", m.group(2))).strip()
            if slug.startswith("-"):
                continue
            if slug not in [a[0] for a in arts]:
                arts.append((slug, title))
                found += 1
        nxt = [int(x) for x in re.findall(r"debut_articles=(\d+)", s)]
        if not nxt or start >= max(nxt):
            break
        start += 12
    return arts


MONTHS = {"janvier": 1, "fevrier": 2, "février": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6, "juillet": 7,
          "aout": 8, "août": 8, "septembre": 9, "octobre": 10, "novembre": 11, "decembre": 12, "décembre": 12}


def find_head(lines):
    for i, x in enumerate(lines[:80]):
        m = re.match(r"^(LOI|Loi)\s+(ORGANIQUE\s+|organique\s+|CONSTITUTIONNELLE\s+)?N\s*[°o]\s*(\d{4}\s*[-–]\s*\d+)\s*(du|DU)?\s*(\d{1,2})?(?:er)?\s*([A-Za-zéûÉÛ]+)?\s*(\d{4})?", x)
        if m:
            d = None
            if m.group(5) and m.group(6) and m.group(7) and m.group(6).lower() in MONTHS:
                d = "%s-%02d-%02d" % (m.group(7), MONTHS[m.group(6).lower()], int(m.group(5)))
            return i, re.sub(r"\s", "", m.group(3)).replace("–", "-"), d, bool(m.group(2))
    return None, None, None, False


def convert(pdf, url, page_url, title_hint, kind=None):
    pages, ocr = T.doc_or_pdf_text(pdf, "fra", tmpdir=RAW)
    lines = T.clean_pages(pages)
    i, num, date, organic = find_head(lines)
    if num is None and title_hint:
        _, num, date, organic = find_head([re.sub(r"(?i)^loi\s+n\s*[°o]\s*", "LOI N° ", title_hint)])
        if num is None:
            m = re.search(r"n\s*[°o]\s*(\d{4})\s*[-–]\s*(\d+)", title_hint, re.I)
            if m:
                num = "%s-%s" % (m.group(1), m.group(2))
    if kind and kind.startswith("constitution"):
        cy = kind.split(":")[1]
        title = "Constitution de la République de Côte d'Ivoire (%s)" % cy
        rel = "constitution/constitution-%s.md" % cy
        typ = "constitution"
        body_lines = lines
        date = {"2016": "2016-11-08", "2000": "2000-08-01", "1960": "1960-11-03"}[cy]
        num = {"2016": "2016-886", "2000": "2000-513", "1960": None}[cy]
    else:
        if i is not None:
            k = i + 1
            while k < min(len(lines), i + 8) and lines[k] and not re.search(r"délibéré|adopté|promulgue|^TITRE|^CHAPITRE|^Article|^ARTICLE", lines[k]):
                k += 1
            title = re.sub(r"\s+", " ", " ".join(x for x in lines[i:k] if x)).strip()
            body_lines = lines[k:]
            pre = [x for x in lines[:i] if x]
            if pre:
                body_lines = lines[:i] + [""] + body_lines  # keep everything before the heading too
        else:
            title, body_lines = title_hint, lines
        if kind == "code-electoral":
            typ, cat = "code", "codes"
        else:
            typ, cat = ("organic_law", "lois-organiques") if organic else ("act", "lois")
        year = (date or num or "undated")[:4]
        rel = "%s/%s/%s.md" % (cat, year if re.match(r"\d{4}$", year) else "undated",
                               ("loi-" + num) if num else T.slug(title_hint, 80))
    body = T.structure(body_lines, "fr")
    if sum(len(x) for x in body) < 200:
        print("SHORT", url, flush=True)
        return None
    meta = {"title": title if len(title) < 500 else title_hint, "identifier": ("Loi n° " + num) if num else None,
            "type": typ, "jurisdiction": "ci", "language": "fr", "date": date, "status": ("in_force" if kind == "constitution:2016" else ("repealed" if kind and kind.startswith("constitution") else "unknown")),
            "source": url, "record": page_url, "retrieved": RETRIEVED,
            "note": ("Text as published by the Conseil constitutionnel" + (" (original 2016 text; the constitutional revision of 2020, loi n° 2020-348 du 19 mars 2020, is not incorporated)" if kind == "constitution:2016" else " (historical constitution)")
                     if kind and kind.startswith("constitution") else "Text as published by the Assemblée nationale (as enacted)") + ("; OCR" if ocr else "")}
    return rel, meta, title, body


def main():
    arts = listing()
    print("articles", len(arts), flush=True)
    CC = "https://www.conseil-constitutionnel.ci/"
    jobs = [("constitution_2016.pdf", CC + "sites/default/files/constitution_2016.pdf", CC + "lois-et-decrets/la-constitution",
             "Constitution", "constitution:2016"),
            ("loi_n_2000-513_du_1er_aout_2000.pdf", CC + "sites/default/files/loi_n_2000-513_du_1er_aout_2000.pdf",
             CC + "lois-et-decrets/la-constitution", "Constitution", "constitution:2000"),
            ("constitution_du_3_novembre_1960.pdf", CC + "sites/default/files/constitution_du_3_novembre_1960.pdf",
             CC + "lois-et-decrets/la-constitution", "Constitution", "constitution:1960")]
    for slug, title in arts:
        s = page(BASE + "?" + slug, os.path.join(RAW, "art", T.slug(slug, 120) + ".html"))
        pdfs = []
        for m in re.finditer(r'href="([^"]+\.pdf)"', s, re.I):
            u = urllib.parse.urljoin(BASE, html.unescape(m.group(1)))
            if u.rsplit("/", 1)[1] in SIDEBAR:
                continue
            u = u.replace("http://www.assnat.ci/assembleenationale/", BASE)
            if u not in pdfs:
                pdfs.append(u)
        if not pdfs:
            print("NOPDF", slug, flush=True)
        for u in pdfs:
            jobs.append((u.rsplit("/", 1)[1], u, BASE + "?" + slug, title, None))
    used = {}
    n = 0
    for fn, url, page_url, title, kind in jobs:
        dest = os.path.join(RAW, "pdf", T.slug(urllib.parse.unquote(fn)[:-4], 120) + ".pdf")
        if DL:
            T.fetch(url, dest, delay=2, check_pdf=True, timeout=300)
        if not os.path.exists(dest) or not T.pdf_ok(dest):
            print("MISSING/BAD", url, flush=True)
            continue
        if "--download-only" in sys.argv:
            continue
        r = convert(dest, url, page_url, title, kind)
        if not r:
            continue
        rel, meta, t, body = r
        if rel in used:
            if used[rel] == url:
                continue
            rel = rel[:-3] + "-" + T.slug(fn[:-4], 40) + ".md"
        used[rel] = url
        T.write_md(os.path.join(REPO, rel), meta, t, body)
        n += 1
        print("OK", rel, flush=True)
    print("written", n)


if __name__ == "__main__":
    main()
