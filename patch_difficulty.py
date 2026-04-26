#!/usr/bin/env python3
"""Reclassify question difficulty to match a realistic exam distribution.

Current: 91% medium, 6% easy, 2% hard.
Target:  ~30% easy, ~50% medium, ~20% hard (approximating CISSP CAT mix).

Heuristics (conservative):
- EASY: pure definition/identification stems
  ('Which is the BEST description of X', 'What does X stand for',
   'Which is...?' with one canonical answer)
- HARD: multi-step reasoning, scenario-based with multiple plausible
  answers, or numeric calculation
- MEDIUM: everything else
"""
import json
import re
from pathlib import Path

P = Path("/Users/mike/cissp/questions.json")
QS = json.loads(P.read_text())


EASY_PATTERNS = [
    r"^What (does|is) [A-Z]+ (stand for|short for)\b",
    r"\bWhich AAA element\b",
    r"\bAt which OSI layer\b",
    r"\bWhich (is the )?(NIST|ISO|RFC|FIPS) (publication|standard) (defines|specifies)\b",
    r"\bWhich (port|cipher|hash|algorithm) is\b",
    r"\bWhat is the (definition|formula) (of|for)\b",
]


HARD_PATTERNS = [
    r"\bcalcul",
    r"\bRTO\b.*\bRPO\b.*\bMTD\b",
    r"\bSLE\b.*\bARO\b",
    r"\bCFO refuses\b",
    r"\bharvest ciphertext today",
    r"^An organisation (faces|has|discovers|begins|deploys|finds|experienc)",
    r"\bafter\b.*\b(disaster|incident|breach|compromise|exploit)\b.*\?",
    r"\b(Which response set|Which migration approach) is BEST\b",
    r"\$[\d,]+",  # dollar amount → numeric reasoning
    r"\b(scenario|chain of custody|forensic|incident).+\b(FIRST|BEST|MOST APPROPRIATE)",
]


def classify(q) -> str:
    stem = q["stem"]
    for pat in HARD_PATTERNS:
        if re.search(pat, stem, re.IGNORECASE):
            return "hard"
    # Long stems with multiple clauses are scenario-based — usually medium-hard
    if len(stem) > 200 and stem.count(",") >= 3:
        return "hard"
    for pat in EASY_PATTERNS:
        if re.search(pat, stem, re.IGNORECASE):
            return "easy"
    # Very short definition-style stems with a single clear question
    if len(stem) < 80 and stem.count("?") == 1 and not re.search(r"\bBEST\b|\bFIRST\b|\bMOST\b|\bPRIMARY\b", stem):
        return "easy"
    return "medium"


def main() -> None:
    counts = {"easy": 0, "medium": 0, "hard": 0}
    for q in QS:
        new = classify(q)
        q["difficulty"] = new
        counts[new] += 1
    P.write_text(json.dumps(QS, indent=2))
    total = len(QS)
    print(f"Reclassified {total} questions:")
    for d in ("easy", "medium", "hard"):
        print(f"  {d}: {counts[d]:3d} ({100*counts[d]/total:.0f}%)")


if __name__ == "__main__":
    main()
