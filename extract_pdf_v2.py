#!/usr/bin/env python3
"""Deep PDF extraction: per-chapter summaries, key terms, glossary.

Produces study_topics.json — readable study content keyed to each chapter,
mapped to the 8 CISSP domains via guide_corpus.json.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path("/Users/mike/cissp")
RAW = (ROOT / "guide_raw.txt").read_text(encoding="utf-8")
CORPUS = json.loads((ROOT / "guide_corpus.json").read_text())
OUT = ROOT / "study_topics.json"


# Standard Sybex CISSP 9th edition chapter → domain mapping (authoritative).
# Used when the chapter number is detected; far more reliable than guessing
# from page ranges in the messy v1 corpus.
CHAPTER_DOMAIN = {
    1: 1, 2: 1, 3: 1, 4: 1,        # D1 Security & Risk Management
    5: 2,                          # D2 Asset Security
    6: 3, 7: 3, 8: 3, 9: 3, 10: 3, # D3 Architecture & Engineering
    11: 4, 12: 4,                  # D4 Network Security
    13: 5, 14: 5,                  # D5 IAM
    15: 6,                         # D6 Assessment & Testing
    16: 7, 17: 7, 18: 7, 19: 7,    # D7 Security Operations
    20: 8, 21: 8,                  # D8 Software Dev Security
}

# Build page → domain map from existing corpus (fallback only)
PAGE_DOMAIN: dict[int, int] = {}
for ch in CORPUS["chapters"]:
    if ch["domain"] is None:
        continue
    for p in range(ch["page_start"], ch["page_end"] + 1):
        PAGE_DOMAIN[p] = ch["domain"]


def page_for_offset(text_before: str) -> int:
    """Given the text up to a position, return the page number we are inside."""
    matches = re.findall(r"=== PAGE (\d+) ===", text_before)
    return int(matches[-1]) if matches else 1


def domain_for_page(page: int) -> int | None:
    if page in PAGE_DOMAIN:
        return PAGE_DOMAIN[page]
    # Search nearby pages
    for delta in range(1, 40):
        for p in (page - delta, page + delta):
            if p in PAGE_DOMAIN:
                return PAGE_DOMAIN[p]
    return None


# 1. Chapter title detection — find lines that are EXACTLY "Chapter N" (the
#    cover-page-style heading), then capture 1-3 following non-empty lines as
#    the title (titles can wrap across lines).
CHAPTER_LINE_RE = re.compile(r"^Chapter\s+(\d{1,2})$", re.MULTILINE)


def find_chapter_title(text: str) -> tuple[int | None, str | None]:
    """Look in the text (already trimmed to before Summary) for the
    most recent standalone 'Chapter N' header followed by the title."""
    matches = list(CHAPTER_LINE_RE.finditer(text))
    if not matches:
        return (None, None)
    m = matches[-1]
    after = text[m.end():m.end() + 400]
    # Skip page markers and capture next 1-3 non-empty lines
    title_lines: list[str] = []
    for ln in after.splitlines():
        ln = ln.strip()
        if not ln:
            if title_lines:
                break
            continue
        if ln.startswith("===") or ln.startswith("THE CISSP TOPICS"):
            if title_lines:
                break
            continue
        # Filter pure-numeric lines (page numbers)
        if ln.isdigit():
            continue
        # Real title lines are mostly title-case
        if not re.match(r"[A-Z]", ln):
            break
        title_lines.append(ln)
        if len(title_lines) >= 3:
            break
        # Also stop if line ends with a sentence terminator (already a complete title)
    title = " ".join(title_lines).strip().rstrip(":,.")
    if not title:
        return (int(m.group(1)), None)
    return (int(m.group(1)), title)


# 2. Find body-text Summary headers (skip TOC at start).
#    The Summary is on its own line and is followed by paragraph text.
SUMMARY_HEADER_RE = re.compile(r"^Summary$", re.MULTILINE)
TERMINATOR_RE = re.compile(
    r"^(?:Written Lab|Review Questions|Exam Essentials|Chapter\s+\d+\s*$)",
    re.MULTILINE,
)


def clean(block: str) -> str:
    """Normalise extracted body text — drop page markers, collapse whitespace."""
    block = re.sub(r"=== PAGE \d+ ===", "", block)
    # Drop running headers/footers if any (uppercase short lines)
    lines = []
    for ln in block.splitlines():
        ln = ln.rstrip()
        if not ln:
            lines.append("")
            continue
        # Skip obvious page headers/footers
        if re.fullmatch(r"\d+", ln.strip()):
            continue
        lines.append(ln)
    text = "\n".join(lines)
    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Re-join wrapped lines that don't end in a sentence terminator
    paragraphs = []
    cur = []
    for ln in text.split("\n"):
        if not ln.strip():
            if cur:
                paragraphs.append(" ".join(cur))
                cur = []
            continue
        cur.append(ln.strip())
    if cur:
        paragraphs.append(" ".join(cur))
    return "\n\n".join(paragraphs).strip()


# 3. Extract Exam Essentials items by detecting their characteristic
#    imperative-verb-led headers, which Sybex uses for every item in the
#    Exam Essentials section ("Understand …", "Know …", "Describe …", etc.).
#    The literal "Exam Essentials" label is missing in most chapters because
#    the PDF rendered it as styled text that didn't survive extraction.
EE_VERBS = (
    r"Understand|Know|Identify|Describe|Explain|Recognize|Comprehend|"
    r"Define|Discuss|List|Name|Be familiar with|Be able to"
)
# Detect imperative-led item headers wherever they appear in the chapter
# end-matter (the "Exam Essentials" label itself often didn't survive PDF
# extraction). Anchor: verb at start, period closing the header phrase.
EE_ANCHOR_RE = re.compile(
    rf"\b((?:{EE_VERBS})\b[^.\n]{{4,200}}\.)\s+",
)


def extract_exam_essentials(chapter_window: str) -> list[dict]:
    """Detect Exam Essentials items by their characteristic imperative
    headers. Items are isolated by splitting the post-Summary region at each
    detected anchor."""
    sm = re.search(r"^Summary$", chapter_window, re.MULTILINE)
    if not sm:
        return []
    region = chapter_window[sm.end():]
    end = re.search(r"^(?:Written Lab|Review Questions)$", region, re.MULTILINE)
    if end:
        region = region[:end.start()]
    cleaned = clean(region)
    # Find all anchor positions in the cleaned text.
    anchors = list(EE_ANCHOR_RE.finditer(cleaned))
    if len(anchors) < 3:
        # Fewer than 3 anchors usually means we caught false positives in the
        # summary prose rather than an actual EE section.
        return []
    items: list[dict] = []
    for i, a in enumerate(anchors):
        term = re.sub(r"\s+", " ", a.group(1)).strip()
        # Reject false positives: term phrases that contain too many sentences
        # (suggesting we matched mid-paragraph "Understand X. ..." prose).
        if term.count(". ") > 1:
            continue
        if not (10 <= len(term) <= 200):
            continue
        gloss_start = a.end()
        gloss_end = anchors[i + 1].start() if i + 1 < len(anchors) else len(cleaned)
        gloss = re.sub(r"\s+", " ", cleaned[gloss_start:gloss_end]).strip()
        if len(gloss) < 30:
            continue
        if len(gloss) > 800:
            cut = gloss.find(". ", 400)
            gloss = gloss[: cut + 1] if cut > 0 else gloss[:800] + "…"
        items.append({"term": term, "gloss": gloss})
    seen = set(); out = []
    for it in items:
        k = it["term"].lower()
        if k in seen: continue
        seen.add(k); out.append(it)
    return out


def build_chapter_headers() -> list[tuple[int, int, str]]:
    """Walk the document and return [(offset, ch_num, title), ...] in order."""
    headers = []
    for m in CHAPTER_LINE_RE.finditer(RAW):
        # Skip TOC area
        if m.start() < 4000:
            continue
        ch_num = int(m.group(1))
        # Capture next non-empty lines as title
        after = RAW[m.end():m.end() + 400]
        title_lines = []
        for ln in after.splitlines():
            ln = ln.strip()
            if not ln:
                if title_lines: break
                continue
            if ln.startswith("===") or ln.startswith("THE CISSP TOPICS"):
                if title_lines: break
                continue
            if ln.isdigit(): continue
            if not re.match(r"[A-Z]", ln): break
            title_lines.append(ln)
            if len(title_lines) >= 3: break
        title = " ".join(title_lines).strip().rstrip(":,.") or f"Chapter {ch_num}"
        headers.append((m.start(), ch_num, title))
    # Filter to monotonically increasing chapter numbers (ignore in-text mentions
    # like "Chapter 7 covers …" — those aren't standalone "Chapter N" lines, but
    # safety net in case of false matches).
    out = []
    last = 0
    for off, n, t in headers:
        if n == last + 1:
            out.append((off, n, t))
            last = n
    return out


CHAPTER_HEADERS = build_chapter_headers()


def chapter_for_offset(offset: int) -> tuple[int | None, str | None]:
    """Return the chapter (number, title) that contains the given offset."""
    last = (None, None)
    for off, n, t in CHAPTER_HEADERS:
        if off > offset:
            break
        last = (n, t)
    return last


def extract_summaries() -> list[dict]:
    """Return one topic per chapter Summary section."""
    topics = []
    for m in SUMMARY_HEADER_RE.finditer(RAW):
        # Skip TOC summaries
        if m.start() < 4000:
            continue
        ch_num, ch_title = chapter_for_offset(m.start())
        # Determine page
        page = page_for_offset(RAW[:m.start()])
        # Capture body until next terminator
        body_region = RAW[m.end():m.end() + 12000]
        term_match = TERMINATOR_RE.search(body_region)
        body = body_region[: term_match.start()] if term_match else body_region[:8000]
        body = clean(body)
        if len(body) < 200:
            # Probably a false positive (a sub-section "Summary" inside a chapter)
            continue
        # Cap length so the embedded JSON stays manageable
        if len(body) > 6000:
            body = body[:6000].rsplit(". ", 1)[0] + "."
        # Try to find Exam Essentials in the chapter body
        # (we look ahead from this Summary further into the chapter)
        ee_region_end = m.end() + 30000
        chapter_window = RAW[m.start():ee_region_end]
        essentials = extract_exam_essentials(chapter_window)
        domain = CHAPTER_DOMAIN.get(ch_num) or domain_for_page(page)
        topics.append({
            "chapter_number": ch_num,
            "chapter_title": ch_title or f"Chapter {ch_num or '?'}",
            "page": page,
            "domain": domain,
            "summary": body,
            "exam_essentials": essentials[:25],  # cap
        })
    return topics


# 4. Glossary extraction — find a "Glossary" section near end of book and
#    capture term: definition pairs. Sybex glossaries usually appear as
#    "TERM An explanation that may run multiple lines."
GLOSSARY_HEADER_RE = re.compile(r"^Glossary$", re.MULTILINE)


def extract_glossary() -> list[dict]:
    matches = list(GLOSSARY_HEADER_RE.finditer(RAW))
    if not matches:
        return []
    # Take the last match (TOC may include "Glossary" too)
    start = matches[-1].end()
    region = RAW[start:start + 600000]  # generous cap
    region = clean(region)
    entries = []
    # Heuristic: term lines start with a Capitalised word/acronym and the term
    # itself runs to the first period or first lowercase word.
    paragraphs = re.split(r"\n+", region)
    for para in paragraphs:
        para = para.strip()
        if not para or len(para) < 10:
            continue
        # Try to split term from gloss: term ends at a period followed by a space,
        # or at first sentence boundary, but term must be short (<= 60 chars).
        m = re.match(r"([A-Z][A-Za-z0-9\-/&\s\(\)]{2,60})\s+([A-Z].+)", para)
        if not m:
            continue
        term = m.group(1).strip().rstrip(":,.")
        gloss = m.group(2).strip()
        if len(term) > 60 or len(gloss) < 20:
            continue
        if not re.search(r"[A-Z]", term):
            continue
        entries.append({"term": term, "definition": gloss[:600]})
    # Dedupe by term
    seen = set(); out = []
    for e in entries:
        k = e["term"].lower()
        if k in seen: continue
        seen.add(k); out.append(e)
    return out


def main() -> None:
    topics = extract_summaries()
    glossary = extract_glossary()
    # Dedupe by (chapter_number, page-bucket) — keep first per chapter,
    # bucket pages by 50 to avoid mid-chapter sub-summary collisions.
    seen = set(); deduped = []
    for t in topics:
        key = (t["chapter_number"], t["page"] // 50)
        if key in seen: continue
        seen.add(key); deduped.append(t)
    payload = {
        "version": 2,
        "extracted_at": "2026-04-26",
        "topics": deduped,
        "glossary": glossary,
    }
    OUT.write_text(json.dumps(payload, indent=2))
    sz = OUT.stat().st_size / 1024
    print(f"[+] {OUT} ({sz:.1f} KiB)")
    print(f"  topics: {len(deduped)}")
    by_d = {}
    for t in deduped:
        by_d[t.get("domain")] = by_d.get(t.get("domain"), 0) + 1
    for d in sorted(by_d.keys(), key=lambda x: (x is None, x)):
        print(f"    domain {d}: {by_d[d]} topics")
    print(f"  glossary entries: {len(glossary)}")
    if topics:
        avg = sum(len(t["summary"]) for t in topics) / len(topics)
        print(f"  avg summary length: {avg:.0f} chars")
    # Sample
    if deduped:
        print()
        print("=== SAMPLE (first topic) ===")
        t = deduped[0]
        print(f"  chapter {t['chapter_number']}: {t['chapter_title']}  (p.{t['page']}, D{t['domain']})")
        print(f"  summary: {t['summary'][:300]}…")
        print(f"  exam_essentials: {len(t['exam_essentials'])} items")


if __name__ == "__main__":
    main()
