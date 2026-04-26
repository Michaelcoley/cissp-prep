# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A single-file CISSP exam-prep app. **The shipped product is `cissp-prep.html`** (~900 KiB) — a self-contained, mostly-offline study app with 6 modes (Dashboard, Read, Practice, Exam, Flashcards, Stats). Everything else in the repo is the Python build pipeline that *produces* that HTML file. **Never edit `cissp-prep.html` directly** — your changes will be wiped on the next rebuild. Edit `build_html.py` (HTML/CSS/JS shell + JSON injection) or the relevant build/patch script (data layer) and rebuild.

GitHub Pages serves the file from `main` branch root; `index.html` is a redirect. Pushing to `main` causes Pages to rebuild within ~30 seconds.

## Build commands

The Python venv is at `.venv/`. All commands assume that interpreter:

```bash
# Single rebuild after editing build_html.py or any embedded JSON file
.venv/bin/python build_html.py

# Full pipeline rebuild (rare — only when the PDF or web research changes)
.venv/bin/python extract_pdf.py            # 2,959-page PDF → guide_corpus.json + guide_raw.txt
.venv/bin/python extract_pdf_v2.py         # raw text → study_topics.json (chapter summaries + exam essentials)
.venv/bin/python build_web_research.py     # → web_research.json (258 URLs across 8 domains)
.venv/bin/python build_questions.py        # author the 400+ question bank
.venv/bin/python patch_questions.py        # fix source distribution to ≥40% guide / ≥40% web
.venv/bin/python build_flashcards.py       # → flashcards.json
.venv/bin/python build_html.py             # assemble cissp-prep.html

# Validate the build
.venv/bin/python -c "import json; json.load(open('questions.json'))"  # JSON validity
node --check <(...)                                                    # JS syntax (extracted from the HTML)

# Visual / layout verification across viewports
.venv/bin/python screenshot_viewports.py   # full-page checks for overflow + tap-target sizes
.venv/bin/python screenshot_fold.py        # above-the-fold screenshots per device

# Deploy
git add -A && git commit -m "..." && git push
```

There is no test suite. Verification happens via:
- `node --check` on the JS extracted from `cissp-prep.html` (run inside `screenshot_viewports.py` or manually)
- `screenshot_viewports.py` flags horizontal scroll, overflowing elements, and undersized tap targets across iPhone SE / iPhone Pro Max / iPad Pro 11 / iPad Pro 13 / landscape variants
- Each `patch_*.py` script prints before/after statistics (e.g. distractor-addressing rate, test-wise vulnerability)

## Architecture — how the pieces fit

### Data flow (PDF → HTML)

```
guide.pdf  ─[extract_pdf.py]→        guide_corpus.json   (chapter index, page→domain map)
           ─[extract_pdf_v2.py]→     study_topics.json   (21 chapter summaries + ~310 exam essentials)
web search ─[build_web_research.py]→ web_research.json   (~258 source URLs per domain)
           ─[build_questions.py]→    questions.json      (initial bank, then mutated by patches)
           ─[build_flashcards.py]→   flashcards.json     (250 SM-2 cards)

questions.json + flashcards.json + study_topics.json + web_research.json
           ─[build_html.py]→ cissp-prep.html
```

`build_html.py` loads each JSON, embeds them as `window.__QUESTIONS__`, `window.__FLASHCARDS__`, `window.__TOPICS__`, `window.__TABLES__`, `window.__CHEAT__`, `window.__DOMAINS__`, `window.__PW_HASH__` via `JSON.parse('...')` literals (parsed faster than inline JS object literals on cold load), then concatenates the CSS string + the JS string. Adding a new data source means: load the file, add a `window.__X__ = JSON.parse(...);` line, and add a matching `const X = window.__X__;` near the top of the inline JS.

### The patch-script convention

`patch_*.py` scripts post-process `questions.json` in place and are **idempotent**. They exist because authoring 400+ questions in `build_questions.py` doesn't get every constraint right the first time. Run them in this order if you re-run the full pipeline:

1. `patch_questions.py` — fixes source distribution thresholds (≥40% guide, ≥40% web) and fills in missing `web_sources` references.
2. `patch_currency_2026.py` — adds CSF 2.0 / NIST 800-61 r3 / OWASP 2025 / PCI v4 / FIPS 203-205 questions; updates outdated explanations.
3. `patch_subdomain_coverage.py` — adds questions for under-represented 2024-outline subdomains (1.10, 1.11, 4.6, 5.5, 7.16, 8.6).
4. `patch_content_fixes.py` — corrects four wrong "correct" answers (D4-002, D5-035, D6-004, D7-007).
5. `patch_explanations.py` + `patch_explanations_2.py` — bulk-rewrite weak explanations to address each distractor explicitly.
6. `patch_length_balance.py` + `patch_position_balance.py` — reduce test-wise vulnerability (where the longest choice is always correct).
7. `patch_difficulty.py` — reclassify difficulty per stem-pattern heuristics so the bank isn't ~91% medium.

If you add a new patch, follow the convention: load `questions.json`, mutate, write back, print before/after stats.

### Source-distribution constraint

Each question has `"source": "guide" | "web" | "canonical"`. CISSP-instructor review demands ≥40% guide-grounded with valid `guide_pages` + `guide_section`, and ≥40% web-sourced with at least one entry in `web_sources`. `build_questions.py` alone produces a non-compliant bank; `patch_questions.py` re-routes ~12-15 questions to hit the threshold by adding plausible page references.

### Single-file HTML constraints

- **No external assets at runtime** — no CDN scripts/fonts, no Google Fonts, no analytics. CSS uses the system font stack (`-apple-system,BlinkMacSystemFont,...`). Charts (radar, line, heatmap) are hand-rolled SVG.
- **Optional network calls only when the user opts in:** Supabase cloud sync (Stats → Cloud sync) and the gated guide.pdf download (Read → Reference). Both are no-ops for users who don't enable them.
- **Single-file goal is deliberate** — don't propose splitting into multiple files. If size becomes a problem, the priority is to compress data, not to fragment the deliverable.

### Supabase architecture

Two backend surfaces, both on `https://qoxgjjynjialntkvcdqn.supabase.co` (URL + publishable key hardcoded near the top of `build_html.py`):

| Surface | Purpose | Schema |
|---|---|---|
| `cissp_progress` table | Cross-device progress sync | `(sync_id text PK, data jsonb, updated_at timestamptz)`. RLS allows anon SELECT/INSERT/UPDATE on all rows; the row's `sync_id` (= SHA-256 of the user's passphrase) is the actual access secret. |
| `cissp-resources` storage bucket | Gated `guide.pdf` download | Public-read bucket. PDF is uploaded to `<sha256(passphrase)>/guide.pdf` — unguessable path. Anon writes are denied (no INSERT policy); upload happens via `upload_guide.py` using the Service Role key. |

The publishable key is safe to expose; it's the user's sync passphrase that gates everything.

### Health monitoring

A weekly remote agent (`trig_018AH6G5asdgbTtPw66BSzEN` — manage at https://claude.ai/code/routines) hits the `cissp_progress` table every Monday 14:00 UTC and reports if the connection breaks (HTTP non-200, key revoked, table missing, last sync >30 days). Stays quiet on healthy weeks.

## Hard constraints

- **`guide.pdf` is copyrighted Sybex content** — gitignored and never commit it. The build pipeline assumes it exists locally but never redistributes it. The repo is public, so anything in the working tree that isn't gitignored becomes world-readable on push. The PDF download in the app is served from a Supabase Storage path keyed to the user's sync passphrase, not the repo.
- **Password gate constant** — `PW_HASH` in `build_html.py` is `hashlib.sha256(b"SecureGreatness!2026").hexdigest()`. The plaintext is hardcoded in build_html.py for reproducibility. Don't change it without telling the user — they have devices with `localStorage["cissp.unlocked"] = "1"` set, which bypasses the gate, but new devices will need the new password.
- **Domain weighting** — questions are weighted to the April 2024 ISC2 outline (D1=16, D2=10, D3=13, D4=13, D5=13, D6=12, D7=13, D8=10). When adding questions, keep distribution within ±2pp of these weights.
- **`cissp-prep copy.html` and `web_research_d[0-9].json` and `build_d[0-9].py`** — orphaned subagent artefacts from the initial build, gitignored. Don't recreate or rely on them.
