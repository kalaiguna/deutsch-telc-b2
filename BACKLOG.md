# Backlog

Ideas and planned work, roughly in priority order. Move finished items to [CHANGELOG.md](CHANGELOG.md).

## Next

### Vocabulary reference pages (Wortschatz)
Quick-reference and refresher pages for telc B2 prep: vocabulary classified by **word class** and intersected with **CEFR level**.

- **Word classes:** Nomen, Verben, Adjektive, Adverbien, plus Präpositionen, Konjunktionen/Konnektoren and feste Wendungen.
- **Levels:** A1, A2, B1, B2, each with a filter or tab, so a word class page can show one level or all.
- **Per entry (nouns):** Artikel + Wort, Plural, Bedeutung (EN), Beispielsatz. Optional: Themenbereich.
- **Per entry (verbs):** Infinitiv, Präteritum, Perfekt (haben/sein), Rektion (Kasus/Präposition), Beispielsatz. Link to the Verben-mit-Präpositionen table where it applies.
- **Per entry (adjectives/adverbs):** Wort, Steigerung where relevant, Gegenteil, Beispielsatz.
- **Open design questions:**
  - Data source: hand-written lists, an open wordlist (check licence; Goethe-Institut lists are the usual A1–B1 reference), or export from the user's own notes.
  - Format: one CSV/JSON/Markdown file per word class under `data/`, rendered by `tools/build.py`, so lists stay easy to edit and are not hand-written HTML.
  - Pages: `wortschatz/index.html` + one page per word class (`nomen.html`, `verben.html`, `adjektive.html`, `adverbien.html`), each filterable by level.
  - Features: client-side filter and search, hide/show translation for self-testing, optional "gelernt" marks stored in `localStorage` like the checklist.
  - Overlap with `deutsch-lernpaket` (it has a B2 vocabulary reference organised by telc Themenbereiche): link to it or reuse its themes rather than duplicating.
- Add vocabulary to the sidebar and start page, and a checklist-style progress counter if useful.

## Later / maybe
- Vocabulary by **Themenbereich** (the 16 official telc topics, see `pruefung.html`) as a second view of the same data.
- Printable flashcard view (print stylesheet already exists for the other pages).
- Link vocabulary entries back to grammar pages (Rektion, Konnektoren, Funktionsverbgefüge).
- Publish via GitHub Pages.
- Link back to this repo from `deutsch-lernpaket`.

## Housekeeping
- Browser check of all generated pages (merged-cell tables in particular).
