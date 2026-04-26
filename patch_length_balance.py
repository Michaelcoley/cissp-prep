#!/usr/bin/env python3
"""Length-rebalance test-wise-vulnerable questions.

A question is test-wise-vulnerable when the LONGEST choice is the CORRECT one
AND it's significantly longer than the shortest distractor — letting a
test-wise candidate pick correctly without reading the stem.

Strategy:
1. Score each question's vulnerability.
2. For high-vulnerability questions, trim parenthetical asides from the
   correct answer where doing so doesn't change meaning.
3. Where parentheticals can't be safely removed, expand the shortest
   distractor with a meaning-preserving qualifier so the lengths align.
4. Always preserve choice ordering and the correct index.
"""
import json
import re
from pathlib import Path

P = Path("/Users/mike/cissp/questions.json")
QS = json.loads(P.read_text())


def vulnerability_ratio(q):
    L = [len(c) for c in q["choices"]]
    longest_is_correct = max(range(4), key=lambda i: L[i]) == q["correct"]
    if not longest_is_correct:
        return 0.0
    other = sorted(L[i] for i in range(4) if i != q["correct"])
    longest_other = other[-1]
    correct_len = L[q["correct"]]
    if correct_len <= longest_other * 1.5:
        return 0.0
    return correct_len / max(1, longest_other)


PARENTHETICAL = re.compile(r"\s*\([^)]{8,}\)")
EM_DASH_ASIDE = re.compile(r"\s+—\s+[^—]{10,}$")
PADDING_QUALIFIERS = [
    " in most operational contexts",
    " when applied to standard enterprise environments",
    " as a baseline configuration",
    " across the relevant policy framework",
    " under typical compliance requirements",
    " for general production deployments",
]


def trim_correct(text: str) -> tuple[str, bool]:
    """Try to shrink the text without changing meaning by removing one
    parenthetical aside or em-dash aside. Returns (new_text, changed)."""
    # Remove the LONGEST parenthetical first
    parens = list(PARENTHETICAL.finditer(text))
    if parens:
        # Take the longest one
        target = max(parens, key=lambda m: m.end() - m.start())
        new = text[:target.start()] + text[target.end():]
        return new.rstrip().rstrip(",.;") + (text[-1] if text and text[-1] in ".!?" else ""), True
    # Try em-dash aside
    m = EM_DASH_ASIDE.search(text)
    if m:
        return text[:m.start()].rstrip(), True
    return text, False


def pad_shortest_distractor(q, target_len: int) -> bool:
    """Append a meaning-preserving qualifier to the shortest distractor so
    its length approaches target_len. Returns True if changed."""
    distractor_indexes = [i for i in range(4) if i != q["correct"]]
    distractor_indexes.sort(key=lambda i: len(q["choices"][i]))
    shortest_i = distractor_indexes[0]
    cur = q["choices"][shortest_i]
    if len(cur) >= target_len * 0.6:
        return False
    # Don't pad obvious one-word answers (would look forced)
    if len(cur.split()) <= 2:
        return False
    qualifier = PADDING_QUALIFIERS[hash(q["id"]) % len(PADDING_QUALIFIERS)]
    if qualifier in cur:
        return False
    new = cur.rstrip(".") + qualifier
    q["choices"][shortest_i] = new
    return True


def main() -> None:
    vulnerable = [(q, vulnerability_ratio(q)) for q in QS]
    vulnerable = [(q, r) for q, r in vulnerable if r > 0]
    vulnerable.sort(key=lambda kv: -kv[1])
    print(f"Test-wise-vulnerable questions (longest = correct, ≥1.5x shortest): {len(vulnerable)}")
    trimmed = 0
    padded = 0
    skipped = 0
    for q, ratio in vulnerable:
        # First try to trim the correct answer
        new_correct, changed = trim_correct(q["choices"][q["correct"]])
        if changed and len(new_correct) >= 12:
            q["choices"][q["correct"]] = new_correct
            trimmed += 1
            continue
        # Otherwise pad the shortest distractor
        if pad_shortest_distractor(q, len(q["choices"][q["correct"]])):
            padded += 1
            continue
        skipped += 1
    P.write_text(json.dumps(QS, indent=2))
    print(f"  Trimmed correct answers: {trimmed}")
    print(f"  Padded shortest distractors: {padded}")
    print(f"  Skipped (couldn't safely modify): {skipped}")
    # Recompute vulnerability after fixes
    still_vulnerable = sum(1 for q in QS if vulnerability_ratio(q) > 0)
    print(f"  Still vulnerable after pass: {still_vulnerable}/{len(QS)}")


if __name__ == "__main__":
    main()
