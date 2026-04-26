# CISSP Exam Prep

Single-file, mostly-offline CISSP study app: 400 manager-mindset practice questions, 191 SM-2 spaced-repetition flashcards, 21 chapter summaries with ~310 exam essentials extracted from the official Sybex study guide, hand-rolled SVG progress charts, full 100-question mock exam with adaptive scoring, and optional Supabase cloud sync.

The shipped app is one HTML file: open `cissp-prep.html` and you're studying. Initial password gate uses Web Crypto SHA-256.

## Features

| View | What it does |
|---|---|
| **Dashboard** | Radar chart of per-domain mastery, streak counter, accuracy %, weakest subdomains, daily flashcard queue size |
| **Read** | All 21 chapters of the guide as searchable summaries + Sybex "exam essentials" for each chapter, grouped by domain |
| **Practice** | Filterable session (domain × difficulty × source × bookmarked × previously-incorrect), instant explanation, bookmark/strike-through choices |
| **Exam** | 100-question mock with 3-hour timer, refresh-safe (saved to localStorage every interaction), per-domain breakdown on completion, downloadable JSON results |
| **Flashcards** | SM-2 spaced repetition (Again / Hard / Good / Easy); per-card EF, interval, due date persisted |
| **Cheat sheets** | Per-domain reference cards with citations to guide pages and ~258 web sources |
| **Stats** | Hand-rolled SVG line chart of exam scores over time, per-domain heatmap, exam history, **Supabase cloud sync**, JSON export/import |

## Build pipeline

```
guide.pdf
   │
   ├─ extract_pdf.py        → guide_corpus.json (chapter index)
   ├─ extract_pdf_v2.py     → study_topics.json (per-chapter summaries + exam essentials)
   │
   └─ web research
      └─ build_web_research.py → web_research.json (~258 URLs across 8 domains)

      build_questions.py    → questions.json (400 Qs)
      patch_questions.py    → fixes source distribution to ≥40% guide / ≥40% web
      build_flashcards.py   → flashcards.json (191 cards)
      build_html.py         → cissp-prep.html (single-file deliverable, ~740 KiB)
```

To rebuild from scratch:

```bash
python3 -m venv .venv
.venv/bin/pip install pdfplumber pypdf
.venv/bin/python extract_pdf.py
.venv/bin/python extract_pdf_v2.py
.venv/bin/python build_web_research.py
.venv/bin/python build_questions.py
.venv/bin/python patch_questions.py
.venv/bin/python build_flashcards.py
.venv/bin/python build_html.py
open cissp-prep.html
```

## Cloud sync (Supabase)

Optional. Enables cross-device study without manual export/import. To set up your own backend, run this SQL in the Supabase SQL editor:

```sql
create table if not exists public.cissp_progress (
  sync_id text primary key,
  data jsonb not null,
  updated_at timestamptz not null default now()
);

alter table public.cissp_progress enable row level security;

create policy "anon select cissp_progress" on public.cissp_progress for select to anon using (true);
create policy "anon insert cissp_progress" on public.cissp_progress for insert to anon with check (true);
create policy "anon update cissp_progress" on public.cissp_progress for update to anon using (true) with check (true);
```

Then update `SUPABASE_URL` and `SUPABASE_KEY` near the top of the JS section in `build_html.py` and rebuild.

In the app: **Stats** → **Cloud sync** → enter a passphrase (8+ chars). Pull → merge → push happens on enable and on every Sync. The passphrase never leaves the device — only its SHA-256 hash is stored.

## Source distribution

| Source | Count | % | What it means |
|---|---|---|---|
| Guide-grounded | 161 | 40.2% | Cites real chapter and page from `guide.pdf` |
| Web-sourced | 236 | 59.0% | Synthesised from harvested community/authoritative web research |
| Canonical | 3 | 0.8% | Foundational topics not well represented in either input |

## Coverage

| Domain | Weight | Questions |
|---|---|---|
| 1. Security and Risk Management | 16% | 64 |
| 2. Asset Security | 10% | 40 |
| 3. Security Architecture and Engineering | 13% | 52 |
| 4. Communication and Network Security | 13% | 52 |
| 5. Identity and Access Management | 13% | 52 |
| 6. Security Assessment and Testing | 12% | 48 |
| 7. Security Operations | 13% | 52 |
| 8. Software Development Security | 10% | 40 |
| **Total** | **100%** | **400** |

## What's NOT in this repo

- `guide.pdf` — the source Sybex study guide is copyrighted and excluded by `.gitignore`. The build pipeline re-runs against your own copy.
- `guide_raw.txt` — derived from `guide.pdf`; rebuilt by `extract_pdf.py`.

## Acknowledgements

- ISC2 CISSP exam outline (April 2024 refresh)
- Sybex CISSP Official Study Guide (9th edition) for chapter structure and exam-essentials phrasing
- Community-maintained question banks and prep authors cited per question (Wentz Wu, DestCert, ExamTopics, Sybex, NIST publications, RFCs, OWASP, etc.)
