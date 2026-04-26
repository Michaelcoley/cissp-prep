#!/usr/bin/env python3
"""Extract guide.pdf -> guide_corpus.json with page-numbered text and TOC index."""
import json
import re
import sys
import time
from pathlib import Path

import pdfplumber

PDF = Path("/Users/mike/cissp/guide.pdf")
OUT = Path("/Users/mike/cissp/guide_corpus.json")
RAW_TXT = Path("/Users/mike/cissp/guide_raw.txt")

# CISSP domain keyword map (used to assign chapters/sections to a domain).
DOMAIN_KEYWORDS = {
    1: [
        "security and risk management", "governance", "risk management", "compliance",
        "ethics", "policies", "business continuity", "personnel security",
        "due care", "due diligence", "threat modeling", "supply chain", "law",
        "regulation", "investigation", "professional ethics", "isc2 code",
    ],
    2: [
        "asset security", "data classification", "data lifecycle", "data owner",
        "data custodian", "data remanence", "data retention", "media",
        "asset retention", "tailoring", "scoping", "dlp", "data states",
        "information classification",
    ],
    3: [
        "security architecture", "engineering", "security models",
        "bell-lapadula", "biba", "clark-wilson", "trusted computing", "tcsec",
        "common criteria", "tpm", "hsm", "cryptography", "encryption",
        "symmetric", "asymmetric", "rsa", "aes", "pki", "hashing", "digital signature",
        "covert channel", "side channel", "facility", "fire suppression",
        "physical security", "secure design",
    ],
    4: [
        "communication and network", "network security", "osi", "tcp/ip",
        "firewall", "ipsec", "tls", "vpn", "wireless", "wpa", "802.1x",
        "dns", "voip", "sdn", "vlan", "zero trust", "microsegmentation",
        "ids", "ips", "nat", "cdn",
    ],
    5: [
        "identity and access management", "iam", "access control",
        "authentication", "authorization", "kerberos", "saml", "oauth",
        "oidc", "radius", "tacacs", "rbac", "abac", "dac", "mac",
        "single sign-on", "sso", "federated", "mfa",
    ],
    6: [
        "security assessment", "security testing", "audit", "penetration",
        "vulnerability assessment", "soc 2", "soc 1", "code review",
        "sast", "dast", "iast", "fuzzing", "kpis", "kris", "log review",
        "synthetic transaction",
    ],
    7: [
        "security operations", "incident response", "forensic", "chain of custody",
        "siem", "soar", "ueba", "patch management", "change management",
        "configuration management", "disaster recovery", "drp", "bcp",
        "raid", "hot site", "warm site", "cold site", "backup",
        "egress", "vulnerability management",
    ],
    8: [
        "software development security", "sdlc", "agile", "waterfall",
        "devsecops", "owasp", "secure coding", "ci/cd", "iac",
        "buffer overflow", "race condition", "toctou", "api security",
        "database security", "supply chain software", "code repository",
        "third-party libraries", "cmm", "samm", "bsimm",
    ],
}

CHAPTER_RE = re.compile(r"^\s*(chapter|appendix|part|domain)\s+([0-9ivxlc]+)[\s:.—–\-]+(.+?)\s*$", re.I)
SECTION_RE = re.compile(r"^\s*(\d+\.\d+(?:\.\d+)*)[\s\.—–\-]+(.+?)\s*$")


def classify_domain(text: str) -> int | None:
    text_l = text.lower()
    scores = {d: 0 for d in DOMAIN_KEYWORDS}
    for d, kws in DOMAIN_KEYWORDS.items():
        for kw in kws:
            if kw in text_l:
                scores[d] += 1
    best = max(scores.items(), key=lambda kv: kv[1])
    return best[0] if best[1] > 0 else None


def main() -> None:
    started = time.time()
    pages: list[dict] = []
    raw_lines: list[str] = []
    with pdfplumber.open(PDF) as pdf:
        total = len(pdf.pages)
        print(f"[+] Opening guide.pdf — {total} pages", flush=True)
        for i, p in enumerate(pdf.pages, start=1):
            text = p.extract_text() or ""
            pages.append({"page": i, "text": text})
            raw_lines.append(f"\n\n=== PAGE {i} ===\n{text}\n")
            if i % 100 == 0 or i == total:
                el = time.time() - started
                print(f"  page {i}/{total}  ({el:.1f}s)", flush=True)

    RAW_TXT.write_text("".join(raw_lines), encoding="utf-8")
    print(f"[+] Raw text written to {RAW_TXT} ({RAW_TXT.stat().st_size/1024/1024:.1f} MiB)")

    # Build TOC by scanning pages for chapter/section headings.
    chapters: list[dict] = []
    current_chapter = None
    for entry in pages:
        for line in entry["text"].splitlines():
            line_s = line.strip()
            if not line_s or len(line_s) > 200:
                continue
            m_ch = CHAPTER_RE.match(line_s)
            if m_ch:
                if current_chapter is not None:
                    current_chapter["page_end"] = entry["page"]
                    chapters.append(current_chapter)
                current_chapter = {
                    "kind": m_ch.group(1).lower(),
                    "number": m_ch.group(2),
                    "title": m_ch.group(3).strip(),
                    "page_start": entry["page"],
                    "page_end": entry["page"],
                    "domain": None,
                    "sections": [],
                }
                continue
            m_s = SECTION_RE.match(line_s)
            if m_s and current_chapter is not None:
                current_chapter["sections"].append({
                    "number": m_s.group(1),
                    "title": m_s.group(2).strip(),
                    "page": entry["page"],
                })
    if current_chapter is not None:
        current_chapter["page_end"] = pages[-1]["page"]
        chapters.append(current_chapter)

    # Assign domain to each chapter.
    for ch in chapters:
        title_blob = ch["title"] + " " + " ".join(s["title"] for s in ch["sections"][:5])
        if re.search(r"chapter\s+1\b|chapter\s+2\b|chapter\s+3\b", ch["title"], re.I):
            pass
        ch["domain"] = classify_domain(title_blob)

    # If a chapter is unmapped, scan its first page text body.
    page_lookup = {p["page"]: p["text"] for p in pages}
    for ch in chapters:
        if ch["domain"]:
            continue
        body = " ".join(page_lookup.get(pn, "") for pn in range(ch["page_start"], min(ch["page_start"] + 3, ch["page_end"] + 1)))
        ch["domain"] = classify_domain(body)

    # Per-domain coverage summary.
    per_domain = {d: [] for d in range(1, 9)}
    unmapped: list[dict] = []
    for ch in chapters:
        if ch["domain"] in per_domain:
            per_domain[ch["domain"]].append({
                "kind": ch["kind"],
                "number": ch["number"],
                "title": ch["title"],
                "page_start": ch["page_start"],
                "page_end": ch["page_end"],
                "section_count": len(ch["sections"]),
            })
        else:
            unmapped.append({
                "kind": ch["kind"],
                "number": ch["number"],
                "title": ch["title"],
                "page_start": ch["page_start"],
                "page_end": ch["page_end"],
            })

    out = {
        "pdf_path": str(PDF),
        "total_pages": len(pages),
        "chapters": chapters,
        "per_domain_chapter_count": {d: len(per_domain[d]) for d in per_domain},
        "unmapped": unmapped,
    }
    OUT.write_text(json.dumps(out, indent=2))
    print(f"[+] Corpus written to {OUT} ({OUT.stat().st_size/1024:.1f} KiB)")
    print()
    print("=== SUMMARY ===")
    print(f"Total pages: {len(pages)}")
    print(f"Chapters detected: {len(chapters)}")
    for d in range(1, 9):
        print(f"  Domain {d}: {len(per_domain[d])} chapters")
    print(f"Unmapped chapters: {len(unmapped)}")
    if unmapped[:8]:
        for u in unmapped[:8]:
            print(f"  - {u['kind']} {u['number']}: {u['title'][:60]} (p{u['page_start']})")
    print(f"Elapsed: {time.time() - started:.1f}s")


if __name__ == "__main__":
    main()
