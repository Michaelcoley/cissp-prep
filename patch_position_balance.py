#!/usr/bin/env python3
"""Position-balance test-wise-vulnerable questions.

If the longest choice = correct AND ratio > 1.5x shortest, the question is
test-wise-vulnerable. The two ways to fix it:

1. Make the choices closer in length (the patch_length_balance.py pass).
2. Or move the correct answer out of the 'longest' slot — by swapping its
   position with another choice. The bank already has correct distributed
   across A/B/C/D, but length-correlation is independent of position.
   This script picks vulnerable questions and swaps the correct-position
   with a different choice so the longest is no longer the correct one.

The catch: if we just shuffle, the correct answer remains the longest in
ABSOLUTE terms — what changes is whether 'longest position' = 'correct
position'. That's NOT what we want — we want the correct answer to NOT
be the longest. So this script DOES NOT actually swap; instead it expands
non-correct choices that are >50% shorter than correct.
"""
import json
from pathlib import Path

P = Path("/Users/mike/cissp/questions.json")
QS = json.loads(P.read_text())


def vuln_ratio(q):
    L = [len(c) for c in q["choices"]]
    if max(range(4), key=lambda i: L[i]) != q["correct"]:
        return 0.0
    other = sorted(L[i] for i in range(4) if i != q["correct"])
    if L[q["correct"]] <= other[-1] * 1.5:
        return 0.0
    return L[q["correct"]] / max(1, other[-1])


# Light meaning-preserving suffixes/prefixes for distractors (chosen so they
# don't mislead — vague-but-plausible qualifiers).
EXPANSIONS = [
    " in standard practice",
    " under typical operating conditions",
    " in most enterprise deployments",
    " given current best practices",
    " when properly implemented",
    " in commonly cited frameworks",
    " for the purposes of this question",
    " across the relevant control set",
]


def expand_distractor(text: str, target_len: int, salt: str) -> str:
    """Add a meaning-preserving expansion to bring text closer to target_len.
    Conservative — only adds one short clause."""
    if len(text) >= target_len * 0.7:
        return text
    qual = EXPANSIONS[hash(salt) % len(EXPANSIONS)]
    if qual.strip() in text.lower():
        return text  # already padded once
    # Drop trailing punctuation, append qualifier, restore punctuation
    end_punct = ""
    if text and text[-1] in ".!?":
        end_punct = text[-1]
        core = text[:-1]
    else:
        core = text
    new = core + qual + end_punct
    if len(new) > target_len * 1.1:
        # Don't overshoot; truncate qualifier to fit
        return text
    return new


def main() -> None:
    vuln = [q for q in QS if vuln_ratio(q) > 0]
    print(f"Test-wise-vulnerable BEFORE this pass: {len(vuln)}")
    fixed = 0
    for q in vuln:
        target = len(q["choices"][q["correct"]])
        # Expand each non-correct distractor that's <70% of correct length
        for i in range(4):
            if i == q["correct"]:
                continue
            new = expand_distractor(q["choices"][i], target, q["id"] + str(i))
            if new != q["choices"][i]:
                q["choices"][i] = new
        if vuln_ratio(q) == 0:
            fixed += 1
    P.write_text(json.dumps(QS, indent=2))
    still = sum(1 for q in QS if vuln_ratio(q) > 0)
    print(f"  Fixed: {fixed}")
    print(f"  Still vulnerable AFTER: {still}/{len(QS)} ({100*still/len(QS):.0f}%)")


if __name__ == "__main__":
    main()
