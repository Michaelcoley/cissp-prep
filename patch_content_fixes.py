#!/usr/bin/env python3
"""Patch the four content errors flagged in the Top-12 review.

D4-002 — TLS layer: was L7, should be Session/L5 per Sybex/CBK
D5-035 — AAL3: FIDO2 isn't "the only" option; PIV/CAC also qualify
D6-004 — NIST 800-115: clarify 3-vs-4 phase model framing
D7-007 — Forensic hashing: drop the "MD5 acceptable" assertion
"""
import json
from pathlib import Path

P = Path("/Users/mike/cissp/questions.json")
QS = json.loads(P.read_text())

FIXES = {
    "D4-002": {
        "stem": "At which OSI layer does TLS PRIMARILY operate?",
        "choices": [
            "Layer 4 (Transport)",
            "Layer 5 (Session)",
            "Layer 6 (Presentation)",
            "Layer 7 (Application)",
        ],
        "correct": 1,
        "explanation": (
            "TLS operates at the Session layer (L5) per ISC2 and Sybex — it manages encrypted "
            "sessions ABOVE TCP at the Transport layer and BELOW applications. Some "
            "references place it at L6 (Presentation) due to its encoding role, and you may "
            "occasionally see it described as 'between L4 and L7', but the exam's canonical "
            "answer is Session. L4 is wrong because TLS depends on TCP — it does not replace "
            "the Transport layer. L6 is the second-most-defensible choice but loses to L5 on "
            "ISC2 conventions. L7 is wrong because applications consume TLS sessions; they "
            "don't provide them."
        ),
    },
    "D5-035": {
        "explanation": (
            "AAL3 requires hardware-backed cryptographic authenticators with verifier-impersonation "
            "resistance. FIDO2/WebAuthn is the modern consumer-grade answer; PIV/CAC smart cards "
            "have met AAL3 since the standard was first published and remain the dominant federal "
            "AAL3 authenticator. Choice A (single-factor password) is AAL1. Choice B (password + "
            "SMS OTP) is AAL2 at best — SMS is in fact RESTRICTED in 800-63B because of SS7 / "
            "SIM-swap risk. Choice D (knowledge-based questions) doesn't qualify at any AAL — "
            "800-63B explicitly discourages KBA."
        ),
    },
    "D6-004": {
        "explanation": (
            "NIST 800-115 frames the methodology as Planning → Execution → Post-Execution at "
            "the high level, with Execution typically split into Discovery and Attack — yielding "
            "the 4-stage Planning, Discovery, Attack, Reporting model commonly cited on the "
            "exam. PTES uses 7 phases. Either way, 'Compliance certification' is never a phase "
            "of the methodology — that's an outcome of an audit, not a pen test. Planning, "
            "Discovery, and Attack/Exploitation are all real phases."
        ),
    },
    "D7-007": {
        "explanation": (
            "Hash comparison provides cryptographic proof of identical content — current "
            "forensic standards (SWGDE, NIST IR 8387) require SHA-256 minimum, with dual-hash "
            "(SHA-256 + SHA-1) as a defensive practice in case one is later challenged. MD5 "
            "is no longer accepted in court because of publicized chosen-prefix collisions. "
            "Visual inspection (A) misses subtle changes — a single bit flip is invisible. "
            "File listing comparison (C) confirms names but not content. Booting the image "
            "(D) is destructive — it modifies registry hives and timestamps, breaking the "
            "chain of custody."
        ),
    },
}


def main() -> None:
    fixed = 0
    for q in QS:
        if q["id"] in FIXES:
            for k, v in FIXES[q["id"]].items():
                q[k] = v
            fixed += 1
    P.write_text(json.dumps(QS, indent=2))
    print(f"[+] Patched {fixed}/{len(FIXES)} questions in {P}")


if __name__ == "__main__":
    main()
