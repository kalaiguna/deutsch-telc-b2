# telc Deutsch B2 – Companion

Personal study companion for the **telc Deutsch B2 (allgemein)** exam: grammar tables, speaking/writing templates, reading/listening strategies and a unit-by-unit study checklist, as cross-linked static HTML pages.

Open `index.html` in a browser (no server needed) or publish the repo root with GitHub Pages.

## Pages

| Page | Content |
|---|---|
| `index.html` | Start page, links, checklist progress |
| `checkliste.html` | 50 units in 3 phases; checkboxes + dates saved locally (browser `localStorage`); "Referenz" links jump to the reference section |
| `grammatik/*.html` | Grundlagen & Zeiten · Konnektoren · Präpositionen · Infinitivkonstruktionen · Passiv, Relativsätze & Stil |
| `sprechen.html`, `schreiben.html`, `lesen.html`, `hoeren.html` | Exam parts |
| `pruefung.html` | Prüfungsschicht: exam structure, scoring, Schreiben templates, Sprechen pitfalls, telc traps (checklist Phase 3 links here) |

Features: sidebar navigation, full-text search, dark mode, print stylesheet, mobile layout.

## Sources and regeneration

The Word files in `source/` are the source of truth:

- `source/DB2CS_v3.docx` – reference tables
- `source/telc_B2_Grammatik_Checkliste.docx` – study checklist
- `source/telc_B2_Pruefungsschicht_Step3.docx` – exam layer (structure, scoring, templates, traps)

The HTML pages are **generated** – don't edit them by hand. After changing a `.docx`:

```
python tools/build.py
```

Requires [Pandoc](https://pandoc.org/) on `PATH` and Python 3 (standard library only; tested on 3.14). The script also rebuilds `assets/search-index.js`.

## Layout

```
index.html  checkliste.html  pruefung.html  sprechen.html  schreiben.html  lesen.html  hoeren.html   (generated)
grammatik/                                                                                       (generated)
assets/style.css  assets/app.js      hand-written; assets/search-index.js is generated
tools/build.py                       converter
source/                              original .docx files
```

## Related

- [deutsch-lernpaket](https://github.com/kalaiguna/deutsch-lernpaket) – Claude skills for daily practice, weekly review and telc mock exams (Notion progress tracking, dashboard). This repo is the static reference/checklist companion; the two are kept separate on purpose.

## Roadmap

Planned work (e.g. vocabulary pages by word class and CEFR level) is tracked in [BACKLOG.md](BACKLOG.md).

## Sources and attribution

- `pruefung.html` (from `telc_B2_Pruefungsschicht_Step3.docx`) summarises the *telc Deutsch B2 Handbuch* (8th ed., 2019) and the official telc exam page. Rights to the handbook and telc exam materials belong to telc gGmbH / its publisher; nothing here claims otherwise. The page carries a notice to this effect.
- Grammar and skills reference (`DB2CS_v3.docx`) is the author's own compilation during their preparation. Grammar rules themselves are not copyrightable.

## License

[MIT](LICENSE) © 2026 Gunasekaran Chandrasekaran. The MIT licence covers the author's own work only, not third-party material (see above). telc® is a registered trademark of telc gGmbH; this project is not affiliated with telc.

## Changes

See [CHANGELOG.md](CHANGELOG.md).
