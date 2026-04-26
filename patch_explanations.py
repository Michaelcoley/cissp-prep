#!/usr/bin/env python3
"""Bulk rewrite the 39 worst-offender explanations to address every distractor.

Per-CISSP-instructor review, the largest content defect was that explanations
justified the correct answer but failed to teach why each wrong choice is
wrong — the actual elimination skill the exam tests.
"""
import json
from pathlib import Path

P = Path("/Users/mike/cissp/questions.json")
QS = json.loads(P.read_text())

REWRITES = {
    "D1-057": (
        "Pre-disaster targets: RTO 4h, RPO 15min, MTD 8h. Actual: recovery took 5h "
        "(0.5h longer than RTO target — RTO BREACHED), data restored is 30min stale "
        "(15min over RPO budget — RPO BREACHED), total downtime 5h is within the 8h "
        "MTD ceiling (MTD met). So both time- and data-objectives missed. "
        "Choice B (only RPO) misses the 1-hour RTO overrun. Choice C (only RTO) "
        "misses the 2x RPO miss. Choice D (MTD failed) is wrong — 5h ≤ 8h MTD."
    ),
    "D1-059": (
        "Inherent risk = the gross risk before any controls are applied. Choice A "
        "describes RESIDUAL risk (what remains after controls). Choice C describes "
        "SECONDARY risk (introduced by a control itself). Choice D is unrelated to "
        "risk-management terminology. Mature risk programs track all three: "
        "inherent → residual after treatment → secondary from new controls."
    ),
    "D5-036": (
        "Rule-Based Access Control (RuBAC) applies system-wide rules (often IF-THEN) "
        "regardless of user identity — firewall ACLs, time-of-day restrictions, "
        "geo-fencing. Choice A describes a simple ACL but lacks the system-wide rule "
        "concept. Choice C is RBAC (Role-Based, identity-driven). Choice D is DAC "
        "(Discretionary, owner-driven). Note the subtle distinction: RuBAC is "
        "rule-based, RBAC is role-based — exam writers love this trap."
    ),
    "D5-040": (
        "Kerberos uses TIME-BOUND tickets — clock skew beyond ~5 minutes (default) "
        "breaks authentication, so NTP synchronisation across all participants is "
        "essential. Choice A is wrong — Kerberos is IP-version-agnostic. Choice C "
        "is unrelated (BGP is for inter-AS routing, not internal directory traffic). "
        "Choice D is wrong — domain controllers can be on different L2 segments "
        "as long as they can route to each other and reach the KDC."
    ),
    "D5-052": (
        "OASIS (not IETF) standardised SAML 2.0, including the Web Browser SSO "
        "Profile that defines both SP-Initiated and IdP-Initiated flows. Choice A "
        "(RFC 6749) is OAuth 2.0 — different protocol entirely. Choice C (RFC 4120) "
        "is Kerberos. Choice D (CTAP) is the FIDO2 Client-to-Authenticator Protocol. "
        "Memorise the source body: SAML = OASIS, OAuth/OIDC = IETF/OpenID, Kerberos "
        "= IETF, FIDO = FIDO Alliance."
    ),
    "D6-008": (
        "ISAE 3402 is the international assurance standard for service-organisation "
        "controls over financial reporting — directly equivalent to SOC 1. Choice B "
        "(SOC 2) maps to ISAE 3000 + the AICPA Trust Services Criteria. Choice C "
        "(SOC 3) is the public-summary version of SOC 2 — has no separate ISAE "
        "equivalent. Choice D (SOC for cybersecurity) is a separate AICPA program "
        "with no ISAE equivalent. Memorise: ISAE 3402 ≈ SOC 1 (financial), ISAE "
        "3000 ≈ SOC 2 (operational/security)."
    ),
    "D6-030": (
        "Real-time forwarding to a centralised log store on a separately-administered "
        "system (with WORM/immutable storage or hash-chain integrity) survives even "
        "complete host compromise. Choice A keeps logs only on the host the attacker "
        "owns — they're trivially deletable. Choice C is unauditable and a privacy "
        "violation. Choice D destroys evidence. The exam pattern: separation of "
        "duties between log producer and log consumer beats every other answer."
    ),
    "D6-041": (
        "Separation-of-duties for log management means privileged users on the "
        "source system cannot administer the log destination — even if they "
        "compromise the host, they can't tamper with the forwarded logs. Choice A "
        "leaves the same admin in control of both — defeats SoD. Choice C ('trust') "
        "is a non-control. Choice D keeps logs on a system the privileged user "
        "controls. The pattern: production admins ≠ logging admins, always."
    ),
    "D6-042": (
        "Regression testing re-runs existing test suites after a code change to "
        "ensure previously-working features still work. Choice A is wrong — testing "
        "ONLY new features misses the whole point of regression. Choice C "
        "(compliance auditing) is unrelated to testing methodology. Choice D "
        "(performance benchmarking) measures speed, not correctness. CI/CD "
        "pipelines run regression suites on every commit to catch regressions early."
    ),
    "D7-015": (
        "A maintenance window is an authorised, communicated period during which "
        "changes that may impact availability or security may be applied — with "
        "stakeholder notification, change-management approval, and rollback plans. "
        "Choice A (vacation) is HR scheduling, not change management. Choice C "
        "(energy) is an operations concern. Choice D (physical inspection) is a "
        "facilities task. The exam consistently frames maintenance windows as "
        "change-management governance, not anything else."
    ),
    "D7-023": (
        "Recovery site selection is fundamentally a cost vs RTO trade-off: lower "
        "RTO requires more pre-positioned infrastructure (hot site = lowest RTO, "
        "highest cost; cold site = cheapest, longest RTO). Choices A (aesthetics), "
        "C (colour), and D (vendor preference) are not relevant criteria. The BIA "
        "drives the RTO requirement; cost determines what your organisation can "
        "afford. The exam's right answer is always 'risk-based business decision'."
    ),
    "D7-027": (
        "Layered physical/visual privacy controls (privacy filters, screen-lock "
        "policies, workspace orientation away from windows/walkways, clean-desk "
        "rules) reduce shoulder-surfing exposure. Choice A ('trust') is a non-"
        "control. Choice C (disabling login) is impractical and breaks operations. "
        "Choice D (headphones) addresses audio leakage, not visual. The exam "
        "expects defence-in-depth even for low-tech threats."
    ),
    "D7-031": (
        "Civil litigation uses 'preponderance of evidence' (more likely than not, "
        ">50%). Choice A ('beyond a reasonable doubt') is the criminal standard — "
        "much higher bar. Choice C ('clear and convincing') sits between, used in "
        "some administrative or termination cases. Choice D ('probable cause') is "
        "the threshold for warrants/arrests, not litigation outcomes. Memorise the "
        "ladder: probable cause < preponderance < clear and convincing < beyond "
        "reasonable doubt."
    ),
    "D7-032": (
        "Patches can break functionality, introduce regressions, or interact "
        "badly with custom configurations — testing in lower environments and "
        "staged rollouts catch this before production impact. Choice A "
        "(compliance penalties) is downstream — outage from a bad patch is the "
        "PRIMARY risk. Choice C (cost) is operational, not security. Choice D "
        "(user confusion) is minor. Manager-mindset: balance patch speed (security) "
        "against testing rigor (stability) per asset risk class."
    ),
    "D7-035": (
        "PAM session brokering provides credential vaulting, MFA enforcement, "
        "session recording, and time-bounded access — the core controls that turn "
        "privileged access from a trust assumption into a verifiable, auditable "
        "operation. Choice A grants unbounded standing access — exactly what PAM "
        "exists to prevent. Choices C (shared passwords) and D (local admins on "
        "every system) destroy attribution and rotation. PAM is the manager-mindset "
        "answer for any privileged-session question."
    ),
    "D7-037": (
        "Detection rules rot — environments change, attacker tradecraft evolves, "
        "false-positive ratios drift. Continuous tuning informed by threat intel, "
        "false-positive feedback, and ATT&CK coverage gap analysis keeps detections "
        "effective. Choice A ('set and forget') guarantees decay. Choice C "
        "(disabling noisy alerts) silently leaves blind spots. Choice D "
        "(outsourcing) doesn't address the core problem of rule maintenance — it "
        "just moves who does it."
    ),
    "D7-039": (
        "Tailored, sector-specific threat intelligence mapped to MITRE ATT&CK "
        "delivers actionable indicators and TTPs that reflect today's adversaries. "
        "Choice A (5-year-old whitepapers) is multiple attacker generations stale. "
        "Choice C (general news media) reports incidents long after the IOCs "
        "matter. Choice D is a joke distractor. Pattern: when an exam asks for "
        "the 'best' source of threat intel, pick the one that's current and "
        "industry-relevant."
    ),
    "D7-041": (
        "Compensating controls (network segmentation, WAF rules, IPS signatures, "
        "virtual patching) limit exposure while a vendor patch is in development. "
        "Choice A ('wait') accumulates risk. Choice C (disabling monitoring) "
        "removes visibility right when an active exploit may strike. Choice D "
        "(public disclosure first) violates responsible-disclosure norms and may "
        "weaponise the vulnerability. Manager-mindset: defence-in-depth means a "
        "single missing patch isn't immediately catastrophic."
    ),
    "D7-042": (
        "Excessive false positives are a SIGNAL — investigate the trigger context, "
        "narrow the rule to the patterns that matter, and tune thresholds. Choice "
        "A (disabling) silently leaves a detection gap. Choice C (raising volume) "
        "makes it worse. Choice D (ignoring) is alert-fatigue territory — eventually "
        "a real attack hides in the noise. The discipline is investigate-and-tune, "
        "never disable-and-forget."
    ),
    "D7-043": (
        "A documented decommissioning workflow with sanitisation per NIST 800-88, "
        "certificate of destruction, and dual sign-off is the audit-ready answer. "
        "Choice A ('trust technicians') is a non-control. Choice C (skipping "
        "sanitisation) is a textbook data-leakage event waiting to happen. Choice "
        "D (single shared bin) loses chain of custody. The pattern: any "
        "decommissioning question with a 'documented workflow + chain of custody' "
        "option will be the answer."
    ),
    "D7-047": (
        "The cleanest least-privilege pattern for admins: standard accounts for "
        "daily work (email, browsing) + named admin accounts for specific systems "
        "+ JIT elevation through PAM for the actual privileged operation. Choice A "
        "('root by default') is the antithesis of least privilege. Choice C "
        "(shared root) destroys attribution. Choice D (disabling user accounts) is "
        "operationally absurd. Three-tier separation + JIT is the modern best "
        "practice."
    ),
    "D7-048": (
        "The Business Impact Analysis (BIA) is the canonical document that "
        "enumerates critical processes and assigns RTO, RPO, MTD, WRT to each. "
        "Choice A (vendor contract) may reference SLAs but doesn't establish "
        "internal RTO/RPO. Choice C (network diagram) is technical inventory. "
        "Choice D (Code of Ethics) is unrelated. Any exam question about RTO/RPO "
        "documentation has BIA as the answer — memorise this association."
    ),
    "D7-050": (
        "HSMs and platform key vaults (AWS KMS, Azure Key Vault, GCP KMS) protect "
        "keys with hardware-rooted security and policy-controlled access — keys "
        "never leave the protected boundary. Choice A (keys in source) leaks them "
        "into git history, build artefacts, and developer machines. Choice C "
        "(email) is plaintext over a system designed to be archived. Choice D "
        "(paper) is a printed-out compromise — possibly fine for break-glass key "
        "shares with proper handling, but disastrous for runtime."
    ),
    "D7-051": (
        "Authoritative sources stack: vendor advisory (the truth) + CVE entry "
        "(the identifier) + CVSS scoring (severity context) + CISA KEV (known "
        "exploitation in the wild). Choice A (Twitter) is noisy and often wrong "
        "in the first 24h of a CVE. Choice C (helpdesk tickets) reflect symptoms, "
        "not vulnerability data. Choice D (marketing) is sales material. The "
        "modern triage workflow: confirm with vendor + CVE, prioritise by CVSS + "
        "KEV status."
    ),
    "D8-006": (
        "CMMI uses five maturity levels: Initial (1) → Managed (2) → Defined (3) "
        "→ Quantitatively Managed (4) → Optimising (5). Choice B (OWASP SAMM) uses "
        "FOUR maturity levels per practice (0–3). Choice C (BSIMM) is descriptive "
        "(observed activities at member firms) — not a numeric maturity scale. "
        "Choice D (ISO 27034) is application security guidance, not a maturity "
        "model. The 1-through-5 ladder is uniquely CMMI."
    ),
    "D8-013": (
        "Shift-left automation is the pattern: SAST + dependency scanning + "
        "secret scanning + IaC checks run as gates in the pipeline before code "
        "ships, catching issues at low cost. Choice A (manual review at the end) "
        "creates rubber-stamp behaviour and doesn't scale. Choice C (disabling "
        "failing tests) is a textbook anti-pattern. Choice D (skipping security "
        "on hot-fixes) is exactly when attackers exploit rushed code. Modern "
        "DevSecOps teaches: gate early, gate often, never skip."
    ),
    "D8-020": (
        "API rate limiting restricts the number of requests per identity/source "
        "per time window — defending against brute force, scraping, abuse, and "
        "accidental DoS. Choice A confuses 'rate' with 'tier' (subscription "
        "billing). Choice C ('encryption mode') is unrelated — that's TLS / "
        "cipher modes. Choice D ('logging level') is observability, not access "
        "control. Implement at the API gateway layer with per-key + per-IP + "
        "per-user buckets."
    ),
    "D8-022": (
        "An SBOM (Software Bill of Materials, in SPDX or CycloneDX format) lists "
        "components, versions, licences, and provenance — required for US federal "
        "software per Executive Order 14028. Choice A ('MD5 manifest') is just an "
        "integrity checksum, not a structured component list. Choice C (EULA) is "
        "the licence agreement — not an inventory. Choice D (architecture diagram) "
        "is design-time, not a machine-readable component list."
    ),
    "D8-024": (
        "Native serialization formats (Python pickle, Java ObjectInputStream, "
        ".NET BinaryFormatter) on untrusted input enable arbitrary code execution "
        "— mitigation is to avoid them entirely for untrusted data and use simple "
        "data formats (JSON, MessagePack) with strict schemas + integrity checks. "
        "Choice A explicitly recommends the dangerous primitives. Choice C ('trust "
        "input') is the underlying mistake. Choice D (disable encryption) is "
        "unrelated — encryption isn't the defense against deserialization RCE. "
        "CWE-502 captures this entire class."
    ),
    "D8-025": (
        "Layered defense: pre-commit hooks (catch before commit) + CI secret "
        "scanning (catch before merge) + a real secrets manager (no secrets in "
        "code) + git history rewrite + key rotation if a leak occurs. Choice A "
        "('trust developers') is a non-control — humans forget. Choice C "
        "(password file in root) is the bug we're trying to prevent. Choice D "
        "(emailing secrets) creates archived plaintext and is catastrophic. The "
        "rotation step is what most people miss — once a secret is in git history, "
        "removing the file doesn't help; assume compromised and rotate."
    ),
    "D8-026": (
        "Branch protection (required reviews, signed commits, CODEOWNERS approval, "
        "status checks) enforces that nothing reaches main without controlled "
        "review. Choice A (direct push) defeats the protection entirely. Choice C "
        "(disabling code review) removes the second pair of eyes that catches "
        "logic and security issues. Choice D (trusting senior engineers) violates "
        "separation of duties — even seniors should be reviewed. The exam pattern "
        "is always: separation + review + signed-artefact verification."
    ),
    "D8-027": (
        "Decomposing the application into data-flow diagrams (DFDs) with explicit "
        "trust boundaries is the canonical step where entry points, data crossings, "
        "and trust transitions become visible — required input to STRIDE-style "
        "threat modeling. Choice A (database architecture) is downstream design, "
        "not threat modeling. Choice C (marketing) is unrelated. Choice D "
        "(language choice) is implementation, not architecture. Microsoft's SDL "
        "documents the DFD-with-trust-boundaries technique formally."
    ),
    "D8-028": (
        "Defence-in-depth for containers: scan images at build (catch CVEs), sign "
        "images (provenance), use minimal base images (smaller attack surface), "
        "run as non-root (limit blast radius), and apply runtime image policies "
        "(only-signed-images-from-our-registry). Choice A ('trust upstream') is "
        "the source of supply-chain attacks. Choice C (root containers) gives an "
        "attacker the host. Choice D (disabling scanning) abandons your earliest "
        "detection layer. Tools: Trivy, Grype, Cosign, OPA/Gatekeeper."
    ),
    "D8-029": (
        "SSRF mitigation: explicit destination ALLOW-list (not deny-list), "
        "block private/loopback/link-local + cloud metadata endpoints "
        "(169.254.169.254 in AWS/GCP/Azure), and route all egress through a "
        "controlled proxy that enforces the allow-list. Choice A ('trust user "
        "URLs') is the SSRF root cause. Choice C ('open all egress') makes the "
        "vulnerability worse. Choice D (disabling DNS) breaks the application "
        "without preventing IP-literal SSRF. The metadata endpoint block is "
        "critical — that's how Capital One was breached in 2019."
    ),
    "D8-031": (
        "A security gate is a defined checkpoint where measurable security "
        "criteria must be met before the work progresses to the next phase — "
        "e.g., 'no critical SAST findings before merge', 'no high CVEs before "
        "deploy', 'threat model reviewed before architecture approval'. Choice A "
        "('physical door') is a literal misreading. Choice C (QA test) is one "
        "input but not the gate concept itself. Choice D (code review) is also "
        "an input. Gates are about CRITERIA, not activities."
    ),
    "D8-033": (
        "SaaS vendor onboarding requires: risk-based assessment + Data Processing "
        "Agreement (GDPR Art. 28) + audit evidence (SOC 2 Type II preferably) + "
        "scoped permissions in their tenant + a documented offboarding/data-return "
        "plan. Choice A ('skip due diligence') is the failure pattern that makes "
        "headlines. Choice C ('trust marketing') overlooks that vendors sell "
        "themselves. Choice D ('unrestricted sharing') violates least privilege. "
        "Manager-mindset: vendor risk = your risk, full stop."
    ),
    "D8-035": (
        "Fail-securely (Saltzer & Schroeder principle) means errors leave the "
        "system in a SECURE state by default — deny access, withhold sensitive "
        "error data from clients, log internally so operators can investigate. "
        "Choice A (crash on any error) impacts availability and isn't actually "
        "secure if the crash leaves resources accessible. Choice C ('always "
        "continue') ignores the error — exactly how injection vulnerabilities "
        "compound. Choice D (no logging) destroys forensic capability. The "
        "shape: deny-by-default + minimal external info + complete internal "
        "audit trail."
    ),
    "D8-038": (
        "Privacy-by-design (Ann Cavoukian's 7 principles, codified in GDPR "
        "Article 25) embeds privacy from inception: data minimisation by default, "
        "purpose limitation, transparent consent, default-private settings. "
        "Choice A ('notice at the end') is privacy theatre. Choice C ('encrypt "
        "after launch') treats privacy as a bolt-on. Choice D ('opt-out only') "
        "violates GDPR's affirmative-consent requirement. The practical test: if "
        "you can remove the privacy controls without rewriting the architecture, "
        "you didn't actually do privacy-by-design."
    ),
    "D8-039": (
        "The full mitigation: (1) remove the secret from code, (2) ROTATE the "
        "credential immediately (assume compromised — git history retains it), "
        "(3) move to a secrets manager, (4) scan history for additional leaks, "
        "(5) add pre-commit/CI scanning to prevent recurrence. Choice A "
        "('comment them out') leaves them in git history — useless. Choice C "
        "('trust git access controls') ignores forks, mirrors, and any prior "
        "exposure. Choice D ('encrypt the repo') doesn't address the leak path "
        "— the secret is already plaintext in commit history."
    ),
}


def main() -> None:
    rewritten = 0
    for q in QS:
        if q["id"] in REWRITES:
            q["explanation"] = REWRITES[q["id"]]
            rewritten += 1
    P.write_text(json.dumps(QS, indent=2))
    print(f"[+] Rewrote {rewritten}/{len(REWRITES)} explanations.")
    # Recheck how many now address distractors
    addressed = 0
    for q in QS:
        e = q["explanation"].lower()
        if any(s in e for s in ('choice a', 'choice b', 'choice c', 'choice d', 'wrong', 'incorrect', 'distractor')):
            addressed += 1
    print(f"  Explanations addressing distractors: {addressed}/{len(QS)} ({100*addressed/len(QS):.0f}%)")


if __name__ == "__main__":
    main()
