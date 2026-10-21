#!/usr/bin/env python3
"""Convert the Word sources in source/ into the static HTML site.

Usage:  python tools/build.py        (requires pandoc on PATH, stdlib only, tested on Python 3.14)

Generated files (do not edit by hand): index.html, checkliste.html, pruefung.html,
sprechen.html, schreiben.html, lesen.html, hoeren.html, grammatik/*.html, assets/search-index.js
"""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source"

# ---------------------------------------------------------------- page layout
# (file, nav title, description, [source heading ids])
GRAMMAR_PAGES = [
    ("grammatik/grundlagen.html", "Grundlagen & Zeiten",
     "Pronomen, Artikel, Adjektivdeklination, Verben, Konjunktiv II der Vergangenheit",
     ["grundlagen", "ergänzungen-zu-den-grundlagen-b2", "konjunktiv-ii-der-vergangenheit-b2"]),
    ("grammatik/konnektoren.html", "Konnektoren",
     "Verbindungswörter nach Wortstellung, zweiteilige und erweiterte Konnektoren",
     ["konnektoren", "erweiterte-konnektoren-b2"]),
    ("grammatik/praepositionen.html", "Präpositionen",
     "Kasus nach Präposition, Verben/Adjektive/Nomen mit Präposition, da-/wo-Compounds",
     ["kasus-und-präposition", "verben-mit-präpositionen", "adjektive-mit-präpositionen-b2",
      "nomen-mit-präpositionen-b2", "pronominaladverbien-da--wo-compounds"]),
    ("grammatik/infinitiv.html", "Infinitivkonstruktionen",
     "zu + Infinitiv nach Verben, Adjektiven und Nomen; Infinitiv ohne zu; Doppelinfinitiv",
     ["zu-infinitiv-nach-verben", "zu-infinitiv-nach-adjektiven", "zu-infinitiv-nach-nomen",
      "infinitiv-ohne-zu", "doppelinfinitiv-im-perfekt-b2"]),
    ("grammatik/passiv-relativ-stil.html", "Passiv, Relativsätze & Stil",
     "Passiv und Ersatzformen, Partizipialattribute, Relativsätze, Nominalisierung, Wortbildung",
     ["passiversatzformen-passive-alternatives", "partizipialattribute-b2",
      "n-deklination-weak-masculine-nouns", "passive-vorgangs-vs.-zustands", "modalpassiv-b2",
      "nominalisierung-verbal-to-nominal-style", "relativsätze-mit-präpositionen",
      "erweiterte-relativsätze-dessen-deren-was-wo-b2", "funktionsverbgefüge",
      "wortbildung-für-sprachbausteine-teil-2-b2"]),
]
SKILL_PAGES = [
    ("sprechen.html", "Sprechen", "Teil 1–3, Gesprächsmanagement, Präsentation",
     ["teil-1-b1-sich-vorstellen", "teil-2-b1-themabeschreibung-meinung",
      "teil-3-b1-gemeinsam-etwas-planen", "gesprächsmanagement-diskursmarker-b2",
      "teil-2-präsentation-b2"]),
    ("schreiben.html", "Schreiben", "E-Mails, Beschwerdebrief, Zusammenfassung, Forumsbeitrag",
     ["informelle-e-mail-b1", "halbformelle-formelle-e-mail-b1b2", "beschwerdebrief-b2",
      "höfliche-bitten-b2", "teil-2-zusammenfassung-b2", "konjunktiv-i-zwei-fehlende-regeln",
      "teil-3-forumsbeitrag-erörterung-b2"]),
    ("pruefung.html", "Prüfungsschicht", "Prüfungsaufbau, Bewertung, Vorlagen und telc-Fallen (Step3)",
     [f"s3-{i}" for i in range(1, 10)]),
    ("lesen.html", "Lesen", "Textverständnis & Dekodierung", ["textverständnis-dekodierung"]),
    ("hoeren.html", "Hören", "Signalwörter & Strategie", ["signalwörter-strategie"]),
]
CHECKLIST = ("checkliste.html", "Checkliste", "49 Einheiten in 3 Phasen mit Fortschrittsanzeige")
ALL_CONTENT_PAGES = GRAMMAR_PAGES + SKILL_PAGES

PRUEFUNG_NOTICE = (
    '<p class="note"><strong>Quellenhinweis:</strong> Die Angaben auf dieser Seite beruhen auf dem '
    '<em>telc Deutsch B2 Handbuch</em> (8. Aufl. 2019) und der offiziellen telc-Prüfungsseite. '
    'Es handelt sich um eigene Zusammenfassungen zum persönlichen Lernen; die Rechte am Handbuch und an den '
    'telc-Prüfungsmaterialien liegen bei der telc gGmbH bzw. dem Verlag. telc® ist eine eingetragene Marke der '
    'telc gGmbH. Dieses Projekt steht in keiner Verbindung zu telc.</p>')

STEP3_ANCHORS = {}

# Checklist "Referenz" cells that don't match a heading title directly.
REF_OVERRIDES = {
    "dieselbe tabelle": ["konjunktiv-ii-der-vergangenheit-b2"],
    "drei tabellen": ["zu-infinitiv-nach-verben", "zu-infinitiv-nach-adjektiven", "zu-infinitiv-nach-nomen"],
    "grundlagen + ergänzungen": ["grundlagen", "ergänzungen-zu-den-grundlagen-b2"],
    "ergänzungen zu den grundlagen": ["ergänzungen-zu-den-grundlagen-b2"],
    "pronominaladverbien": ["pronominaladverbien-da--wo-compounds"],
    "passiversatzformen": ["passiversatzformen-passive-alternatives"],
    "n-deklination": ["n-deklination-weak-masculine-nouns"],
    "nominalisierung": ["nominalisierung-verbal-to-nominal-style"],
    "passive: vorgangs vs. zustands": ["passive-vorgangs-vs.-zustands"],
}


# ------------------------------------------------------------------- helpers
def slug(text):
    t = text.strip().lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        t = t.replace(a, b)
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", " ", s))


def base(s):
    """Heading/reference title without parentheses or anything after ' —' / ':'."""
    s = re.sub(r"\([^)]*\)", "", norm(s))
    return re.split(r" — |:", s)[0].strip()


def norm(s):
    s = strip_tags(s).lower()
    s = re.sub(r"\s+", " ", s).strip()
    return s


def pandoc(docx):
    r = subprocess.run(["pandoc", str(docx), "-t", "html", "--wrap=none"],
                       capture_output=True, text=True, encoding="utf-8", check=True)
    return r.stdout


def clean_tables(h):
    h = re.sub(r"</?blockquote>", "", h)
    h = re.sub(r"<colgroup>.*?</colgroup>", "", h, flags=re.S)
    h = re.sub(r'<table[^>]*>', "<table>", h)
    h = re.sub(r"<table>", '<div class="table-wrap"><table>', h)
    h = h.replace("</table>", "</table></div>")
    h = re.sub(r"<p>\s*</p>", "", h)
    return h


# ------------------------------------------------------------ parse reference
def parse_reference():
    h = pandoc(SRC / "DB2CS_v3.docx")
    # drop TOC (everything before first h2)
    h = h[h.index("<h2 "):]
    parts = re.split(r"(?=<h[23] id=)", h)
    sections = {}  # old id -> dict(title, body)
    for p in parts:
        m = re.match(r'<h([23]) id="([^"]*)">(.*?)</h\1>(.*)', p, re.S)
        if not m or m.group(1) == "2":
            continue
        sid, title, body = m.group(2), strip_tags(m.group(3)).strip(), m.group(4)
        sections[sid] = {"title": title, "body": clean_tables(body).strip()}
    return sections


STEP3_SUBHEADS = ("Bewertungskriterien", "Vor dem Abgeben", "Beschwerdebrief —", "Anfrage / Bitte",
                  "Teil 1 —", "Teil 2 —", "Den Partner einbeziehen", "Teil 3 —")
# checklist "Step3 → …" text -> sub-heading / section key
STEP3_REFS = {
    "bausteine + 3-von-4-regel": "Beschwerdebrief —", "anfrage-vorlage": "Anfrage / Bitte",
    "checkliste": "Vor dem Abgeben", "teil 1": "Teil 1 —", "teil 2 + konjunktiv i": "Teil 2 —",
    "teil 3": "Teil 3 —", "abschnitt 4": "4.", "lesen-fallen": "6.", "hören": "7.",
    "3-schritte-strategie": "8.",
}


def parse_step3():
    """Split the Step3 doc into numbered sections; return (sections, anchors)."""
    h = clean_tables(pandoc(SRC / "telc_B2_Pruefungsschicht_Step3.docx"))
    lines = h.split("\n")
    head_re = re.compile(r"^<p><strong>(\d)\. ([^<]*)</strong></p>$")
    sections, anchors, cur, intro = {}, {}, None, []
    for ln in lines[1:]:  # first line is the document title
        m = head_re.match(ln)
        if m:
            n = int(m.group(1))
            cur = {"title": f"{n}. {m.group(2)}", "id": slug(m.group(2)), "body": []}
            sections[f"s3-{n}"] = cur
            anchors[f"{n}."] = (f"s3-{n}", cur["id"], cur["title"])
            continue
        if cur is None:
            intro.append(ln)
            continue
        sm = re.match(r"^<p><strong>([^<]*)</strong></p>$", ln)
        if sm and sm.group(1).startswith(STEP3_SUBHEADS):
            sid = slug(sm.group(1))
            anchors[next(k for k in STEP3_SUBHEADS if sm.group(1).startswith(k))] = (None, sid, sm.group(1))
            ln = f'<h3 id="{sid}">{sm.group(1)}</h3>'
            anchors[sm.group(1)[:12]] = None
        cur["body"].append(ln)
    sections["s3-1"]["body"] = intro + sections["s3-1"]["body"]
    for k in sections:
        sections[k]["body"] = "\n".join(sections[k]["body"]).strip()
    # sub-heading anchors live on the section that contains them
    out = {}
    for key, val in anchors.items():
        if val is None:
            continue
        sec, aid, label = val
        if sec is None:
            sec = next(k for k, v in sections.items() if f'id="{aid}"' in v["body"])
        out[key] = ("pruefung.html", aid, label)
    return sections, out


# -------------------------------------------------------------------- layout
def sidebar(root, current, page_sections):
    def a(href, label, cls=""):
        active = ' class="active"' if href == current else ""
        return f'<a href="{root}{href}"{active}>{html.escape(label)}</a>'

    out = ['<nav class="sidebar" id="sidebar" aria-label="Navigation">',
           f'<a class="brand" href="{root}index.html">{FLAG_SVG}telc B2<span>Companion</span></a>',
           '<input type="search" id="search" placeholder="Suchen …" autocomplete="off" aria-label="Suche">',
           '<div id="search-results" class="search-results" hidden></div>',
           '<div class="nav-group">', a("index.html", "Start"), a(CHECKLIST[0], "Checkliste"), "</div>",
           '<div class="nav-label">Grammatik</div><div class="nav-group">']
    out += [a(f, t) for f, t, _, _ in GRAMMAR_PAGES]
    out += ['</div><div class="nav-label">Prüfungsteile</div><div class="nav-group">']
    out += [a(f, t) for f, t, _, _ in SKILL_PAGES]
    out.append("</div>")
    if page_sections:
        out.append('<div class="nav-label">Auf dieser Seite</div><div class="nav-group toc">')
        out += [f'<a href="#{i}">{html.escape(t)}</a>' for i, t in page_sections]
        out.append("</div>")
    out.append("</nav>")
    return "\n".join(out)


# German flag as inline SVG: flag emoji render as plain "DE" letters on Windows, SVG looks the same everywhere.
_FLAG_RECTS = ('<rect width="5" height="1" fill="#000"/><rect y="1" width="5" height="1" fill="#d00"/>'
               '<rect y="2" width="5" height="1" fill="#ffce00"/>')
FLAG_SVG = ('<svg class="flag" viewBox="0 0 5 3" role="img" aria-label="Deutschland">'
            + _FLAG_RECTS + "</svg>")
FAVICON = ("%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 5 3'%3E"
           + _FLAG_RECTS.replace('"', "'").replace("#", "%23").replace("<", "%3C").replace(">", "%3E")
           + "%3C/svg%3E")


REPO = "https://github.com/kalaiguna/deutsch-telc-b2"
FOOTER = ('<footer class="site-footer">© 2026 <a href="https://github.com/kalaiguna">Gunasekaran Chandrasekaran</a> · '
          f'<a href="{REPO}/blob/main/LICENSE">MIT License</a> · <a href="{REPO}">GitHub</a> · '
          'Nicht verbunden mit der telc gGmbH.</footer>')


def page(root, filename, title, body, page_sections=(), lead=""):
    prev_next = ""
    order = [CHECKLIST[0]] + [f for f, *_ in ALL_CONTENT_PAGES]
    if filename in order:
        i = order.index(filename)
        titles = {CHECKLIST[0]: CHECKLIST[1], **{f: t for f, t, *_ in ALL_CONTENT_PAGES}}
        bits = []
        if i > 0:
            bits.append(f'<a href="{root}{order[i-1]}">← {html.escape(titles[order[i-1]])}</a>')
        else:
            bits.append("<span></span>")
        if i < len(order) - 1:
            bits.append(f'<a href="{root}{order[i+1]}">{html.escape(titles[order[i+1]])} →</a>')
        prev_next = f'<div class="pager">{"".join(bits)}</div>'
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>🇩🇪 {html.escape(title) if filename == "index.html" else html.escape(title) + " · telc Deutsch B2"}</title>
<link rel="icon" href="data:image/svg+xml,{FAVICON}">
<link rel="stylesheet" href="{root}assets/style.css">
<script>document.documentElement.dataset.theme = localStorage.getItem('telc-b2-theme') || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');</script>
</head>
<body data-root="{root}">
<button class="menu-btn" id="menu-btn" aria-label="Menü">☰</button>
<a class="mobile-brand" href="{root}index.html">{FLAG_SVG}telc B2</a>
<button class="theme-btn" id="theme-btn" aria-label="Dark/Light">◐</button>
{sidebar(root, filename, page_sections)}
<main>
<h1>{html.escape(title)}</h1>
{f'<p class="lead">{html.escape(lead)}</p>' if lead else ''}
{body}
{prev_next}
{FOOTER}
</main>
<script src="{root}assets/search-index.js"></script>
<script src="{root}assets/app.js"></script>
</body>
</html>
"""


# ----------------------------------------------------------------- generation
def build_content_pages(sections, id_map, search):
    used = set()
    for filename, title, desc, ids in ALL_CONTENT_PAGES:
        root = "../" if "/" in filename else ""
        body, toc = [], []
        for old in ids:
            s = sections[old]
            used.add(old)
            new = id_map[old]
            toc.append((new, s["title"]))
            body.append(f'<section id="{new}"><h2>{html.escape(s["title"])}'
                        f'<a class="anchor" href="#{new}" aria-label="Link">#</a></h2>\n{s["body"]}\n</section>')
            search.append({"p": filename, "a": new, "t": s["title"], "pg": title,
                           "x": re.sub(r"\s+", " ", strip_tags(s["body"]))})
        if filename == "pruefung.html":
            body.insert(0, PRUEFUNG_NOTICE)
        (ROOT / filename).parent.mkdir(parents=True, exist_ok=True)
        (ROOT / filename).write_text(page(root, filename, title, "\n".join(body), toc, desc), encoding="utf-8")
    missing = set(sections) - used
    if missing:
        sys.exit(f"Sections not assigned to any page: {sorted(missing)}")


def resolve_refs(ref_html, sections, id_map, page_of):
    """Turn a 'Referenz' cell's text into hyperlinks to the reference pages."""
    text = norm(ref_html)
    if text.startswith("übungstest"):
        return ref_html  # external material, not part of this repo
    if text.startswith("step3"):
        key = STEP3_REFS.get(text.split("→", 1)[-1].strip())
        if key and key in STEP3_ANCHORS:
            f, aid, label = STEP3_ANCHORS[key]
            return f'<a href="{f}#{aid}">Step3 → {html.escape(label)}</a>'
        print(f"  ! unresolved Step3 reference: {text!r}")
        return ref_html
    targets = []
    if text in REF_OVERRIDES:
        targets = REF_OVERRIDES[text]
    else:
        for sid, s in sections.items():
            if base(s["title"]) == base(text) or norm(s["title"]).startswith(text):
                targets.append(sid)
                break
    if not targets:
        print(f"  ! unresolved checklist reference: {text!r}")
        return ref_html
    links = []
    for sid in targets:
        label = sections[sid]["title"]
        links.append(f'<a href="{page_of[sid]}#{id_map[sid]}">{html.escape(label)}</a>')
    return "<br>".join(links)


def build_checklist(sections, id_map, page_of, search):
    h = pandoc(SRC / "telc_B2_Grammatik_Checkliste.docx")
    h = clean_tables(h)
    # intro heading paragraph -> page lead, phase paragraphs -> h2
    h = re.sub(r"<p><strong>Grammatik-Checkliste[^<]*</strong></p>\s*", "", h)
    h = re.sub(r"<p><strong>(PHASE [^<]*)</strong></p>",
               lambda m: f'<h2 id="{slug(m.group(1).split("·")[0])}">{m.group(1)}</h2>', h)
    h = h.replace("Start: ______________", 'Start: <input type="date" id="start-date" aria-label="Startdatum">')
    phases = re.findall(r'<h2 id="([^"]*)">([^<]*)</h2>', h)

    def fix_row(m):
        row = m.group(0)
        tds = re.findall(r"<td[^>]*>.*?</td>", row, re.S)
        if len(tds) != 6 or "☐" not in tds[0]:
            return row
        n = strip_tags(tds[1]).strip()
        cells = [
            f'<td class="c"><input type="checkbox" class="chk" data-n="{n}" aria-label="Einheit {n} erledigt"></td>',
            f'<td class="c">{n}</td>',
            re.sub(r"^<td[^>]*>", "<td>", tds[2]),
            "<td>" + resolve_refs(re.sub(r"^<td[^>]*>|</td>$", "", tds[3]), sections, id_map, page_of) + "</td>",
            re.sub(r"^<td[^>]*>", "<td>", tds[4]),
            f'<td class="done-date" data-n="{n}"></td>',
        ]
        return f'<tr class="unit" data-n="{n}">' + "".join(cells) + "</tr>"

    h = re.sub(r"<tr>.*?</tr>", fix_row, h, flags=re.S)
    units = len(re.findall(r'class="chk"', h))
    progress = ('<div class="progress-box"><div class="progress"><div id="progress-bar"></div></div>'
                f'<span id="progress-text" data-total="{units}">0 / {units}</span>'
                '<button id="reset-progress" type="button">Zurücksetzen</button></div>')
    note = ('<p class="note">Der Fortschritt wird nur lokal in diesem Browser gespeichert (localStorage). '
            'Der Link in „Referenz“ springt zum passenden Abschnitt.</p>')
    body = progress + note + h
    toc = [(i, t.split("·")[0].strip().title()) for i, t in phases]
    toc = [(i, t) for i, t in toc]
    filename, title, desc = CHECKLIST
    (ROOT / filename).write_text(page("", filename, "Grammatik-Checkliste – telc Deutsch B2", body, toc, desc),
                                 encoding="utf-8")
    search.append({"p": filename, "a": "", "t": "Grammatik-Checkliste", "pg": "Checkliste",
                   "x": re.sub(r"\s+", " ", strip_tags(h))})
    return units


def build_index(units):
    cards = ['<section class="cards">',
             f'<a class="card" href="checkliste.html"><h3>Checkliste</h3><p>{units} Einheiten in 3 Phasen mit '
             f'Output-Aufgaben.</p><div class="progress"><div id="home-progress-bar"></div></div>'
             f'<small id="home-progress-text" data-total="{units}"></small></a>', "</section>"]
    g = ['<h2>Grammatik</h2><section class="cards">']
    for f, t, d, _ in GRAMMAR_PAGES:
        g.append(f'<a class="card" href="{f}"><h3>{html.escape(t)}</h3><p>{html.escape(d)}</p></a>')
    g.append("</section><h2>Prüfungsteile</h2><section class=\"cards\">")
    for f, t, d, _ in SKILL_PAGES:
        g.append(f'<a class="card" href="{f}"><h3>{html.escape(t)}</h3><p>{html.escape(d)}</p></a>')
    g.append("</section>")
    body = ("<h2>Studienplan</h2>" + "\n".join(cards) + "\n".join(g) +
            '<p class="note">Quellen: <code>source/DB2CS_v3.docx</code>, '
            '<code>source/telc_B2_Grammatik_Checkliste.docx</code>. Seiten werden mit '
            '<code>python tools/build.py</code> generiert.</p>'
            '<h2>Weiterführend</h2>'
            '<p><a href="https://github.com/kalaiguna/deutsch-lernpaket">deutsch-lernpaket</a> – Claude-Skills '
            'für tägliche Übung, Wiederholung und telc-Prüfungssimulation (Notion-Fortschritt, Dashboard).</p>')
    (ROOT / "index.html").write_text(
        page("", "index.html", "telc Deutsch B2 – Companion", body, (),
             "Lernbegleiter für die telc-Prüfung Deutsch B2: Grammatik, Sprechen, Schreiben, Lesen, Hören."),
        encoding="utf-8")


def main():
    sections = parse_reference()
    s3, anchors = parse_step3()
    STEP3_ANCHORS.update(anchors)
    id_map = {old: slug(s["title"]) for old, s in sections.items()}
    id_map.update({k: v["id"] for k, v in s3.items()})
    sections.update(s3)
    assert len(set(id_map.values())) == len(id_map), "slug collision"
    page_of = {sid: f for f, _, _, ids in ALL_CONTENT_PAGES for sid in ids}
    # checklist links are relative to site root; content pages are in root or grammatik/
    search = []
    build_content_pages(sections, id_map, search)
    units = build_checklist(sections, id_map, page_of, search)
    build_index(units)
    (ROOT / "assets").mkdir(exist_ok=True)
    (ROOT / "assets" / "search-index.js").write_text(
        "window.SEARCH_INDEX = " + json.dumps(search, ensure_ascii=False) + ";\n", encoding="utf-8")
    print(f"Built {len(ALL_CONTENT_PAGES) + 2} pages, {len(sections)} sections, {units} checklist units.")


if __name__ == "__main__":
    main()
