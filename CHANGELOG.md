# Changelog

All notable changes to this project are documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [SemVer](https://semver.org/).

## [Unreleased]

### Added
- Repository scaffolding: `README.md`, `CHANGELOG.md`, `BACKLOG.md`, `LICENSE` (MIT), `.gitignore`.
- Source documents in `source/`: `DB2CS_v3.docx` (reference), `telc_B2_Grammatik_Checkliste.docx` (study checklist) and `telc_B2_Pruefungsschicht_Step3.docx` (exam layer).
- `tools/build.py`: converts the Word sources to static HTML via Pandoc.
- Generated pages: start page, checklist, 5 grammar pages, Sprechen, Schreiben, Lesen, Hören, Prüfungsschicht.
- Checklist with local progress tracking (localStorage), start date, and hyperlinks from each unit to its reference section.
- Sidebar navigation, full-text search, dark mode, print stylesheet, responsive layout.
- Cross-link to the `deutsch-lernpaket` repository in the README and on the start page.
- Source attribution and telc trademark notice (README and `pruefung.html`).
- Checklist Phase 3 `Step3 →` references link to the matching sections of `pruefung.html`.
- German flag branding: SVG flag in the sidebar brand and in a mobile top bar, SVG favicon, and 🇩🇪 in page titles.
- Site footer with copyright, license and repository links.
- README section on reporting errors via GitHub issues.
