#!/usr/bin/env python3
"""Currency patch — bring the question bank up to 2026 standards.

- NIST CSF 2.0 (Feb 2024) added Govern function — add 2 Qs testing Govern.
- NIST 800-61 Rev 3 (Apr 2025) restructured around continuous improvement — 1 Q.
- OWASP Top 10:2025 (Nov 2025) — 1 Q noting the move from 2021 cats.
- PCI-DSS v4.0.1 mandatory Mar 2025 — 1 Q on the v3.2.1 → v4 changes.
- FIPS 203/204/205 post-quantum standards (Aug 2024) — 2 Qs on PQC selection.
- NIST 800-63-4 (Aug 2024) — 1 Q on passkey/sync fabric guidance.

Also patches outdated text in existing questions where useful.
"""
import json
from pathlib import Path

P = Path("/Users/mike/cissp/questions.json")
QS = json.loads(P.read_text())


def Q(qid, domain, subdomain, difficulty, stem, choices, correct, explanation,
      source="canonical", guide_pages=None, guide_section=None,
      web_sources=None, references=None, tags=None, notes=""):
    return {
        "id": qid, "domain": domain, "subdomain": subdomain,
        "difficulty": difficulty, "stem": stem,
        "choices": list(choices), "correct": correct,
        "explanation": explanation, "source": source,
        "guide_pages": guide_pages or [],
        "guide_section": guide_section or "",
        "web_sources": web_sources or [],
        "references": references or [],
        "tags": tags or [], "notes": notes,
    }


# 8 NEW QUESTIONS
NEW = [
    Q("D1-065", 1, "1.5 Frameworks", "medium",
      "Which function was ADDED in NIST Cybersecurity Framework 2.0 (released February 2024) that did not exist in CSF 1.1?",
      ["Identify", "Govern", "Detect", "Recover"],
      1,
      "CSF 2.0 elevated 'Govern' to a sixth core function (joining Identify, Protect, Detect, Respond, Recover from v1.1). Govern covers organizational risk management strategy, roles and responsibilities, supply chain risk, and oversight — formalising what was previously scattered across Identify and the Implementation Tiers. Identify, Detect, and Recover all existed in CSF 1.1 — they were not added.",
      source="web",
      web_sources=[{"url":"https://www.nist.gov/cyberframework","title":"NIST CSF 2.0","captured":"2026-04-26"}],
      references=["NIST CSF 2.0"],
      tags=["nist-csf-2", "govern", "currency-2026"]),

    Q("D1-066", 1, "1.5 Frameworks", "medium",
      "Under NIST CSF 2.0's Govern function, which is the BEST description of what an organisation must do?",
      ["Implement technical controls only",
       "Establish, communicate, and monitor the cybersecurity risk management strategy, expectations, and policy — including supply chain oversight",
       "Replace the CISO function with the CFO",
       "Outsource all governance to third-party auditors"],
      1,
      "Govern in CSF 2.0 establishes WHO is accountable, the risk strategy, supply chain risk management, and the policies that drive everything else. It is fundamentally a leadership/oversight function. Choice A confuses Govern with Protect. Choice C is wrong — governance is broader than any single role and must be supported by board-level engagement. Choice D conflates audit (assurance) with governance (direction).",
      source="web",
      web_sources=[{"url":"https://www.nist.gov/cyberframework","title":"NIST CSF 2.0","captured":"2026-04-26"}],
      references=["NIST CSF 2.0 — Govern"],
      tags=["nist-csf-2", "govern", "currency-2026"]),

    Q("D7-053", 7, "7.1 IR Lifecycle", "medium",
      "NIST SP 800-61 Revision 3 (April 2025) reorganises incident response around what concept compared to Revision 2's four-phase lifecycle?",
      ["A single 'Eradicate-then-restore' phase",
       "Continuous improvement woven through ongoing functions (Govern, Identify, Protect, Detect, Respond, Recover) — aligned to NIST CSF 2.0",
       "Outsourcing all IR to MSSPs by default",
       "A two-phase 'Detect / Respond' model only"],
      1,
      "800-61 r3 abandons the strictly-sequential Prep → Detect → Containment/Eradication/Recovery → Post-Incident model. Instead it aligns with CSF 2.0's six functions and emphasises continuous improvement throughout the lifecycle (not just at the end). The four-phase r2 model is still useful conceptually but no longer the framework's primary structure. Choice A invents a phase. Choice C is unrelated to the standard. Choice D oversimplifies.",
      source="web",
      web_sources=[{"url":"https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r3.pdf","title":"NIST SP 800-61 r3","captured":"2026-04-26"}],
      references=["NIST SP 800-61 r3"],
      tags=["nist-800-61-r3", "currency-2026"]),

    Q("D8-041", 8, "8.4 OWASP Top 10", "medium",
      "Which is a NEW OWASP Top 10 category introduced in the 2025 release that was NOT in the 2021 release?",
      ["Broken Access Control",
       "Software Supply Chain Failures (an explicit category, not just dependency risk)",
       "Cross-Site Scripting (it was already #3 in 2021)",
       "SQL Injection (split out of Injection)"],
      1,
      "OWASP Top 10:2025 elevates Software Supply Chain Failures to its own category (covering build pipeline compromise, malicious dependencies, signed-artefact verification, SBOM hygiene), reflecting the reality of attacks like SolarWinds, 3CX, and the npm package compromises. Broken Access Control was already #1 in 2021. XSS was folded into Injection in 2021. SQL Injection was never split out as its own category in 2025.",
      source="web",
      web_sources=[{"url":"https://owasp.org/www-project-top-ten/","title":"OWASP Top 10","captured":"2026-04-26"}],
      references=["OWASP Top 10:2025"],
      tags=["owasp-2025", "supply-chain", "currency-2026"]),

    Q("D1-067", 1, "1.3 Compliance", "medium",
      "PCI-DSS v4.0 (mandatory March 31, 2025) introduced which significant change from v3.2.1?",
      ["Removed the requirement for cardholder data encryption",
       "Increased password minimum length to 12 characters and introduced 'targeted risk analysis' as an alternative to fixed compliance schedules",
       "Eliminated the requirement for quarterly vulnerability scans",
       "Made all organisations subject to Level 1 audits regardless of transaction volume"],
      1,
      "PCI-DSS v4.0 raised password minimums (from 7 to 12 characters for non-customer accounts) and introduced 'customised approach' / targeted risk analysis — letting organisations justify alternative control implementations against documented risk rather than meeting prescriptive timetables. Choices A, C, D are false: encryption is still required, scans are still mandatory, and merchant levels are unchanged.",
      source="web",
      web_sources=[{"url":"https://www.pcisecuritystandards.org/document_library/","title":"PCI-DSS v4.0","captured":"2026-04-26"}],
      references=["PCI-DSS v4.0.1"],
      tags=["pci-dss-v4", "currency-2026"]),

    Q("D3-053", 3, "3.3 Cryptography", "hard",
      "NIST finalised three post-quantum cryptography standards in August 2024. Which standard is the recommended general-purpose KEY ENCAPSULATION mechanism (replacing RSA/ECDH for key exchange)?",
      ["FIPS 203 — ML-KEM (formerly Kyber)",
       "FIPS 204 — ML-DSA (formerly Dilithium)",
       "FIPS 205 — SLH-DSA (formerly SPHINCS+)",
       "FIPS 197 — AES"],
      0,
      "FIPS 203 standardises ML-KEM (Module-Lattice-based KEM, previously Kyber) for post-quantum key encapsulation — directly replacing the role RSA and ECDH played in TLS handshakes and similar key-exchange contexts. FIPS 204 (ML-DSA / Dilithium) and FIPS 205 (SLH-DSA / SPHINCS+) are SIGNATURE schemes, not KEMs. FIPS 197 is AES (symmetric, not asymmetric, and not post-quantum-specific).",
      source="web",
      web_sources=[{"url":"https://csrc.nist.gov/pubs/fips/140/3/final","title":"NIST PQC Standards","captured":"2026-04-26"}],
      references=["FIPS 203"],
      tags=["post-quantum", "ml-kem", "kyber", "currency-2026"]),

    Q("D3-054", 3, "3.3 Cryptography", "medium",
      "An organisation begins migrating to post-quantum cryptography. Which migration approach is the BEST first step recommended by NIST?",
      ["Replace all classical algorithms with PQC immediately",
       "Adopt a HYBRID approach (e.g., classical ECDH + ML-KEM in TLS) so security holds even if one half is later broken",
       "Stop encrypting data until the standards are mature",
       "Use only FIPS 205 SLH-DSA because it has the strongest security assumptions"],
      1,
      "Hybrid post-quantum schemes combine a classical algorithm with a PQC algorithm so the connection remains secure if EITHER algorithm is later weakened. NIST and IETF have endorsed hybrid TLS during the transition (e.g., draft-ietf-tls-hybrid-design). Choice A is risky — early implementations of new algorithms historically have bugs. Choice C abandons defence. Choice D is wrong: SLH-DSA is signature-only, not a KEM, and significantly slower than ML-DSA.",
      source="web",
      web_sources=[{"url":"https://csrc.nist.gov/projects/post-quantum-cryptography","title":"NIST PQC migration","captured":"2026-04-26"}],
      tags=["post-quantum", "hybrid", "currency-2026"]),

    Q("D5-053", 5, "5.7 NIST 800-63-4", "medium",
      "NIST SP 800-63-4 (Initial Public Draft, August 2024) explicitly addresses which authentication trend that 800-63-3 did not?",
      ["Biometric template aging",
       "Synchronisable authenticators ('passkeys') and the trade-off between syncing across devices versus device-bound credentials",
       "Knowledge-based authentication (KBA)",
       "Single-factor SMS"],
      1,
      "800-63-4 directly addresses passkeys (syncable FIDO2 credentials) and explicitly differentiates 'syncable authenticators' from 'device-bound authenticators' — a concept that did not exist in 800-63-3. The trade-off is recoverability/UX (sync) vs cryptographic strength (device-bound is stronger). Biometric aging was always covered. KBA remains discouraged. SMS remains RESTRICTED.",
      source="web",
      web_sources=[{"url":"https://csrc.nist.gov/pubs/sp/800/63/4/2pd","title":"NIST SP 800-63-4","captured":"2026-04-26"}],
      references=["NIST SP 800-63-4"],
      tags=["passkeys", "nist-800-63-4", "currency-2026"]),
]


def main() -> None:
    # Update existing question explanations to reference current versions
    UPDATES = {
        "D1-030": (
            "NIST CSF 2.0 (Feb 2024) defines six core functions: Govern (NEW in 2.0), Identify, "
            "Protect, Detect, Respond, Recover. CSF 1.1's five functions (IPDRR) were extended "
            "with Govern to formalise leadership/oversight responsibilities including supply chain "
            "risk management. ISO 27001 uses ISMS clauses + Annex A controls. COBIT uses "
            "governance/management objectives. PCI-DSS uses 12 requirements."
        ),
        "D6-035": (
            "CVSS (Common Vulnerability Scoring System) is the prioritisation standard. CVSS v4.0 "
            "(Nov 2023) introduces Threat metrics (Exploit Maturity), Environmental modifiers, and "
            "Supplemental metrics (Safety, Recovery). CVE = unique identifier (e.g., CVE-2024-1234). "
            "CWE = weakness taxonomy (e.g., CWE-89 SQL injection). CCE = configuration enumeration. "
            "Modern practice combines CVSS + CISA KEV (Known Exploited Vulnerabilities) catalogue."
        ),
        "D8-008": (
            "OWASP Top 10:2021 categorised vulnerable libraries as A06: Vulnerable and Outdated "
            "Components — addressed by SCA tooling, SBOM hygiene, and dependency pinning. The 2025 "
            "release elevated Software Supply Chain Failures to a more comprehensive category. "
            "A05 Security Misconfiguration covers default creds, unnecessary features. "
            "A07 Identification and Authentication Failures covers session/auth flaws. "
            "A08 Software and Data Integrity Failures covers CI/CD compromise and unsigned updates."
        ),
    }
    updated = 0
    for q in QS:
        if q["id"] in UPDATES:
            q["explanation"] = UPDATES[q["id"]]
            updated += 1

    # Add new questions
    existing_ids = {q["id"] for q in QS}
    added = 0
    for nq in NEW:
        if nq["id"] in existing_ids:
            continue
        QS.append(nq)
        added += 1

    P.write_text(json.dumps(QS, indent=2))
    print(f"[+] Updated {updated} existing questions, added {added} new questions.")
    print(f"  Total questions now: {len(QS)}")
    by_d = {}
    for q in QS:
        by_d[q["domain"]] = by_d.get(q["domain"], 0) + 1
    for d in sorted(by_d):
        print(f"    D{d}: {by_d[d]} ({100*by_d[d]/len(QS):.1f}%)")


if __name__ == "__main__":
    main()
