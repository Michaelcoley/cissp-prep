#!/usr/bin/env python3
"""Second batch of explanation rewrites — 50 more questions targeted to the
next-worst-offender pile (200-400 char explanations that don't address
distractors)."""
import json
from pathlib import Path

P = Path("/Users/mike/cissp/questions.json")
QS = json.loads(P.read_text())

REWRITES = {
    "D1-031": (
        "DREAD = Damage, Reproducibility, Exploitability, Affected users, "
        "Discoverability — Microsoft's threat-severity SCORING method, often paired "
        "with STRIDE (which categorises) for end-to-end threat modeling. Choice B "
        "invents 'Reach/Exposure/Awareness/Detection'. Choice C is a generic "
        "incident-response acronym. Choice D blends real and invented words. "
        "Mnemonic: Damage you do, can it be Reproduced, Exploited, who's Affected, "
        "and how Discoverable is it?"
    ),
    "D1-035": (
        "Job rotation cross-trains staff (resilience benefit) AND surfaces ongoing "
        "fraud or shortcuts when a substitute takes the role — that's the security "
        "purpose. Choice A (turnover) is HR. Choice C (compensation) is HR. Choice "
        "D is wrong — rotation COMPLEMENTS separation of duties, never replaces it. "
        "The exam pattern: rotation + SoD + mandatory vacation form a triad of "
        "fraud-detection personnel controls."
    ),
    "D1-040": (
        "Policy exceptions must be FORMALLY APPROVED, TIME-BOUND, DOCUMENTED, and "
        "carry COMPENSATING CONTROLS — anything less and the auditor flags the "
        "policy as unenforceable. Choice B (undocumented override) destroys "
        "auditability. Choice C (verbal agreement) leaves no record. Choice D "
        "(standing exemption) creates a permanent gap. The exam tests this: "
        "exceptions are not policy violations IF properly documented."
    ),
    "D1-048": (
        "An alerting IDS detects suspicious activity but takes no preventive action "
        "— that's a DETECTIVE control. Choice A (preventive) would describe an IPS "
        "(in-line, blocking). Choice C (corrective) restores after damage. Choice D "
        "(compensating) substitutes when a primary control isn't feasible. "
        "Memorise: IDS → detective; IPS → preventive; the difference is in-line "
        "blocking capability."
    ),
    "D1-049": (
        "NIST CSF 1.1 organised outcomes in 5 functions / 23 categories / 108 "
        "subcategories — and CSF 2.0 added a 6th function (Govern) in Feb 2024. "
        "Choice B (ISO 27002:2022) has 93 controls organised differently. Choice C "
        "(CIS Controls v8) has 18 controls + 153 safeguards. Choice D (OWASP SAMM) "
        "is a software-security maturity model with 5 business functions × 4 "
        "maturity levels. Each framework has distinct structure — memorise their "
        "shape, not just their names."
    ),
    "D2-030": (
        "NIST SP 800-60 maps information types to FIPS 199 categorisation (Low/"
        "Moderate/High impact for C, I, A separately). Choice A (800-37) is the "
        "Risk Management Framework process. Choice C (800-88) is media sanitisation. "
        "Choice D (800-30) is risk assessment. The pair {FIPS 199, NIST 800-60} "
        "drives the RMF Categorise step — memorise that pair as the categorisation "
        "anchor."
    ),
    "D2-038": (
        "GDPR Article 6 enumerates SIX lawful bases for processing personal data: "
        "Consent, Contract, Legal obligation, Vital interest, Public task, "
        "Legitimate interest. Without ONE of these, processing is unlawful. Choice "
        "A (convenience) is not a basis. Choice C (storage capacity) is operational. "
        "Choice D (vendor recommendation) is meaningless. The exam consistently "
        "tests that you know the lawful basis pre-conditions all GDPR processing."
    ),
    "D2-039": (
        "Multi-function devices retain scanned/printed/faxed documents on internal "
        "storage that is routinely overlooked — sanitisation per NIST 800-88 MUST "
        "precede any disposal/donation/sale. Choice A (donate) leaks data with the "
        "device. Choice C (sell) does the same and may violate compliance. Choice D "
        "(power off) doesn't erase NAND/disk storage. The exam tests this because "
        "MFP data leaks have caused real-world breaches (notably Affinity Health "
        "Plan in 2013)."
    ),
    "D2-033": (
        "Software/firmware version + patch level lets you map an asset against "
        "published CVEs — the foundational join key for vulnerability management. "
        "Choice A (purchase date) is depreciation/finance. Choice C (depreciation "
        "schedule) is finance. Choice D (vendor support contract) matters for "
        "support but doesn't drive vuln matching. CIS Control 1 (asset inventory) "
        "and 2 (software inventory) explicitly call out version data as the "
        "vulnerability-management prerequisite."
    ),
    "D8-040": (
        "NIST SP 800-218 (SSDF) defines four practice groups: Prepare the "
        "Organisation (PO), Protect the Software (PS), Produce Well-Secured "
        "Software (PW), Respond to Vulnerabilities (RV). Choice A (800-115) is "
        "technical security testing. Choice B (800-37) is the RMF. Choice D "
        "(800-53) is the controls catalogue. Memorise the 800-series numbers: "
        "30-risk, 37-RMF, 53-controls, 60-categorisation, 61-IR, 88-sanitisation, "
        "115-testing, 207-zero-trust, 218-SSDF."
    ),
    "D6-044": (
        "Independent third-party Type II audits evaluate operating effectiveness "
        "over a period — the gold standard for relying parties (regulators, "
        "customers, boards). Choice A (vendor self-attestation) carries no third-"
        "party validation. Choice C (informal internal review) lacks rigor and "
        "independence. Choice D (marketing whitepaper) is sales material, not "
        "assurance. Pattern: independence + period-based testing + opinion = "
        "highest assurance."
    ),
    "D6-019": (
        "Independence eliminates conflict of interest and increases the weight "
        "third parties (regulators, customers, boards) place on findings. Choice A "
        "(lower cost) — independent audits typically cost MORE, not less. Choice C "
        "(faster) — they're often slower due to scoping rigor. Choice D (less "
        "paperwork) — they require MORE evidence. Pattern: independence is about "
        "credibility and reliance, not efficiency."
    ),
    "D5-049": (
        "SAML metadata (XML document) declares the entity's endpoints, signing/"
        "encryption certificates, name ID formats, and supported bindings — both "
        "IdP and SP exchange metadata to establish trust mechanically. Choice A "
        "(logging) is a runtime concern, not metadata. Choice C (user training) "
        "isn't a SAML artefact. Choice D (business hours) is operational. The "
        "exam: metadata = the federation 'business card' that enables protocol "
        "interoperation."
    ),
    "D5-003": (
        "Two pieces of 'something you know' (password + security question) are "
        "SAME-FACTOR — both knowledge. Real MFA combines DISTINCT factor categories: "
        "something you know + something you have + something you are (+ optional "
        "somewhere you are). Choice A (password + token) = know + have. Choice B "
        "(password + fingerprint) = know + are. Choice D (smart card + PIN) = have "
        "+ know. The trap is that 'two things' looks like MFA but factor diversity "
        "is what defines it."
    ),
    "D4-015": (
        "SDN's defining characteristic is decoupling the CONTROL plane (decision-"
        "making intelligence) from the DATA plane (forwarding hardware), with "
        "centralised programmatic control. Choice A (hardware-only) is the "
        "OPPOSITE of SDN. Choice C (mandatory IPv6) is unrelated. Choice D (read-"
        "only) — SDN is about programmatic control, the polar opposite of read-"
        "only. The exam: SDN = control/data separation + centralised control + "
        "open APIs (e.g., OpenFlow)."
    ),
    "D4-025": (
        "IDS = passive (detect + alert). IPS = inline (detect + actively block "
        "traffic). Choice A is wrong — both come in hardware and software/virtual "
        "form. Choice C is wrong — IPS introduces small inline latency but isn't "
        "fundamentally slower. Choice D is wrong — they're explicitly different "
        "categories. The exam: the in-line blocking capability is the defining "
        "difference, not form factor."
    ),
    "D4-027": (
        "S/MIME and PGP provide END-TO-END encryption and digital signatures for "
        "email message CONTENT — protecting the body and attachments. Choice A "
        "(SPF), B (DKIM), and D (DMARC) all address ENVELOPE-level anti-spoofing "
        "(can the sender's domain authorise this IP, are the headers signed, what "
        "policy applies on alignment failure). Pattern: SPF/DKIM/DMARC = sender "
        "authentication; S/MIME/PGP = content confidentiality + integrity + "
        "non-repudiation."
    ),
    "D4-033": (
        "SD-WAN tunnels (typically IPsec or VXLAN) provide point-to-point "
        "confidentiality but lack inline security inspection — without a paired "
        "security stack (SASE, secure web gateway, CASB), traffic inside the tunnel "
        "is opaque to enterprise security tools. Choice A (physical theft) is "
        "unrelated. Choice C (loss of routing) is wrong — SD-WAN provides routing. "
        "Choice D (no multicast) is technically wrong and irrelevant. The exam "
        "pattern: SD-WAN + SASE = secure modern WAN."
    ),
    "D4-035": (
        "Dedicated IoT VLAN with restrictive ACLs and outbound-only allow-listing "
        "limits the blast radius when (not if) an IoT device is compromised. Choice "
        "A (flat network) lets a compromised IoT device pivot east-west into high-"
        "value systems. Choice C (disable all IoT) is operationally infeasible. "
        "Choice D (encrypt at rest only) ignores network-borne lateral movement, "
        "which is the actual IoT threat vector."
    ),
    "D4-040": (
        "NTP keeps all systems' clocks in sync — large skew breaks Kerberos "
        "(ticket validity windows), TLS certificate validation, log correlation "
        "across systems, and forensic timelines. Choice B (DHCP) provides IP "
        "addresses, not time. Choice C (SNMP) is for monitoring/management. Choice "
        "D (SMB) is file sharing. The exam tests NTP because candidates underweight "
        "infrastructure protocols — yet broken time can break authentication "
        "entirely."
    ),
    "D4-043": (
        "DMARC has THREE policy values: p=none (monitor and report only), "
        "p=quarantine (treat as suspicious — typically spam folder), p=reject "
        "(drop the message). 'p=accept' is invented — DMARC doesn't have it. "
        "Mature deployment progresses: none → quarantine → reject as confidence "
        "in alignment grows. The exam pattern: DMARC policy values are tested "
        "directly because they're often confused with spam-filter actions."
    ),
    "D5-013": (
        "OIDC adds an AUTHENTICATION layer on top of OAuth 2.0 — the ID token "
        "(a JWT) carries identity claims. Choice A is wrong — OIDC complements "
        "OAuth, never replaces it. Choice C is wrong — OIDC uses JSON tokens "
        "(JWTs), not XML. Choice D is wrong — OIDC works equally well in cloud, "
        "on-prem, and mobile. The exam: OAuth = authorisation (delegation); "
        "OIDC = authentication (identity) on top of OAuth."
    ),
    "D5-033": (
        "JWT (RFC 7519) is the JSON-based token format used in OIDC and many "
        "OAuth 2.0 flows. Compact (base64url-encoded), URL-safe, signed (JWS) "
        "or encrypted (JWE). Choice A is wrong — JWTs are text, not binary. "
        "Choice C (backup format) is invented. Choice D — JWTs are not specifically "
        "OIDC and not binary. Common pitfalls: don't store secrets in JWT (it's "
        "decodable), validate the alg (beware 'none'), enforce expiry."
    ),
    "D6-007": (
        "Type I = design effectiveness at a POINT IN TIME (snapshot). Type II = "
        "design + OPERATING effectiveness over a PERIOD (typically 6-12 months). "
        "Choice A (Type II is shorter) is wrong — Type II covers a longer testing "
        "window. Choice C (Type I covers more) is wrong — both have the same scope, "
        "Type II just adds time-based testing. Choice D is wrong — Type II requires "
        "EXTENSIVE testing across the period. Customers prefer Type II for its "
        "operating-effectiveness assurance."
    ),
    "D6-011": (
        "Log review supports both DETECTION (alerting on suspicious patterns) and "
        "FORENSIC INVESTIGATION (post-incident reconstruction). Choice A (save disk "
        "space) inverts the purpose — logs cost storage, they don't save it. "
        "Choice C is wrong — logs complement network monitoring, neither replaces "
        "the other. Choice D (document software versions) is inventory, not log "
        "review. The exam: detect + investigate, not file management."
    ),
    "D6-013": (
        "Synthetic transactions are SCRIPTED requests that simulate user actions "
        "to monitor availability and correctness — verifying endpoints respond "
        "correctly within SLA from external probe locations. Choice A (passive "
        "real-user monitoring, RUM) is the OPPOSITE technique. Choice C (database "
        "backups) is unrelated. Choice D (fake user accounts) might support "
        "synthetic monitoring but aren't the technique itself. Pattern: synthetic "
        "= active probing; RUM = passive observation."
    ),
    "D6-026": (
        "Discovery encompasses BOTH passive (OSINT, public records, DNS, social "
        "media) AND active (port scans, banner grabs, web crawling, DNS "
        "enumeration) reconnaissance. Choice A (Planning) sets scope and rules of "
        "engagement before discovery. Choice C (Attack) exploits findings from "
        "discovery. Choice D (Reporting) communicates outcomes. The exam pattern: "
        "Discovery is the information-gathering phase that informs Attack."
    ),
    "D6-029": (
        "BAS (Breach and Attack Simulation) platforms automate execution of real "
        "attacker techniques against the production stack on a continuous basis — "
        "validating that detection and prevention controls actually fire. Choice A "
        "(random pen-tests) confuses BAS with traditional pen testing. Choice C "
        "(replace SOC) — BAS COMPLEMENTS the SOC, doesn't replace human analysts. "
        "Choice D (compliance reports) is incidental, not the primary value. "
        "Examples: SafeBreach, Cymulate, AttackIQ."
    ),
    "D6-033": (
        "Pen-test reports must deliver ACTIONABLE findings prioritised by business "
        "risk, with reproduction steps and concrete remediation guidance — that's "
        "what the customer pays for. Choice A (executive cover) is window dressing. "
        "Choice C (tools used) belongs in methodology, not findings. Choice D "
        "(personal opinions) reduces credibility. Manager-mindset: the report's "
        "value is in actionability, not page count or aesthetics."
    ),
    "D6-036": (
        "MITRE ATT&CK catalogues real-world adversary tactics (TA: the goal — "
        "Initial Access, Execution, etc.), techniques (T: the how), and procedures "
        "— the standard reference for detection engineering. Choice B (CVSS) "
        "scores vulnerability severity, not adversary behaviour. Choice C (ISO "
        "27001) is the ISMS standard. Choice D (FIPS 199) is impact categorisation. "
        "The exam consistently associates ATT&CK with detection engineering and "
        "purple-teaming."
    ),
    "D7-004": (
        "Lessons learned must translate into concrete CHANGES — updated playbooks, "
        "added detections, closed control gaps, refreshed training. Choice A "
        "(congratulations) is morale, not improvement. Choice C (closing tickets "
        "without writeup) destroys institutional learning. Choice D (archive and "
        "forget) ensures the next incident recurs. NIST 800-61 r3 explicitly "
        "weaves continuous improvement throughout the lifecycle, not just at the "
        "end."
    ),
    "D7-006": (
        "Chain of custody is a documented record proving evidence integrity from "
        "seizure through court — every transfer, every location, every access "
        "logged with date/time/who. Choice A (informal passes) breaks the chain. "
        "Choice C (shared drive) loses the named-custody record. Choice D "
        "(skipping documentation) destroys admissibility. A single gap in custody "
        "can render the evidence inadmissible — that's why this is tested heavily."
    ),
    "D7-012": (
        "Differential backups capture changes since the LAST FULL — so restoring "
        "needs only the full + the most recent differential (Friday's). Choice A "
        "(every diff Mon-Fri) confuses differential with incremental. Choice C "
        "blends 'differential' and 'incremental' which is technically inconsistent. "
        "Choice D ignores the full backup. Pattern: differential = simpler restore, "
        "slower backup; incremental = faster backup, longer restore chain."
    ),
    "D7-013": (
        "Incrementals capture changes since the previous backup OF ANY TYPE — "
        "fastest to back up, slowest to restore (need full + every incremental in "
        "the chain). Choice A (full) backs up everything. Choice B (differential) "
        "captures since last full only. Choice D (snapshot) is a point-in-time "
        "copy. Pattern: incrementals trade backup speed for restore complexity, "
        "differentials trade the opposite way."
    ),
    "D7-014": (
        "3-2-1 = THREE copies of data, on TWO different media types, with ONE "
        "copy offsite. Modern variants: 3-2-1-1-0 adds an immutable copy and "
        "verified zero-error restoration. Choice B (3 backups/day) misframes as "
        "frequency. Choice C (admins/sites/passwords) invents. Choice D (3 daily/"
        "2 weekly/1 monthly) is a different retention pattern. The exam tests "
        "this rule directly."
    ),
    "D7-017": (
        "Baselines define the APPROVED, secure starting state for systems — "
        "configuration management tools (Ansible, Puppet, Chef, GPO) detect "
        "drift from baseline and remediate. Choice A (energy) is unrelated. "
        "Choice C (license compliance) is inventory. Choice D is wrong — baselines "
        "complement patch management, neither replaces the other. The exam: "
        "baselines + drift detection + remediation = configuration assurance."
    ),
    "D7-018": (
        "SOAR (Security Orchestration, Automation, and Response) extends SIEM "
        "with PLAYBOOKS that automatically execute response actions across tools "
        "— containment (isolate host), enrichment (look up IOC), ticket creation, "
        "user notifications. Choice A (logging) is the SIEM job. Choice C "
        "(vulnerability scanning) is a separate tool category. Choice D (endpoint "
        "protection) is EDR/AV. Pattern: SIEM correlates events; SOAR orchestrates "
        "response."
    ),
    "D7-024": (
        "Internet-facing surfaces change constantly — monthly is the modern "
        "minimum, with continuous scanning increasingly common (PCI-DSS requires "
        "quarterly external + scans after any significant change). Choice A "
        "(annually) misses ~11 months of new exposure. Choice C (every 5 years) "
        "is essentially negligence. Choice D (only after a breach) is "
        "post-incident, not prevention. The exam pattern: external surfaces "
        "deserve more scanning frequency than internal ones."
    ),
    "D8-002": (
        "Agile (Scrum, Kanban, XP, SAFe) emphasises ITERATION (short sprints), "
        "CUSTOMER FEEDBACK (working software each iteration), and incremental "
        "delivery — codified in the 2001 Agile Manifesto. Choice A (Waterfall) is "
        "sequential, no iteration. Choice B (Big Bang) means deploy everything at "
        "once — opposite of incremental. Choice D (V-Model) is sequential with "
        "verification phases mirroring development phases — also non-iterative."
    ),
    "D8-012": (
        "CSRF defence stack: anti-CSRF tokens (synchroniser pattern — token in "
        "form, validated on POST) PLUS SameSite cookies (Lax or Strict — browser "
        "blocks cross-site cookie attachment). Choice A (Referer alone) is "
        "unreliable — proxies strip it, mobile apps don't send it. Choice C "
        "(user-agent) is trivially spoofable. Choice D (HTTPS alone) doesn't help "
        "— CSRF works fine over HTTPS. Modern apps use both tokens AND SameSite "
        "for defence in depth."
    ),
    "D8-015": (
        "Layered defence: SCA (find known-CVE deps), SBOM (machine-readable "
        "inventory), provenance verification (sigstore/SLSA), pinning to known-"
        "good versions, and private registry mirrors. Choice A (trust public "
        "registries) is exactly how SolarWinds and 3CX-style attacks succeed. "
        "Choice C (disable package managers) is operationally impossible. Choice "
        "D (one library) doesn't address the supply chain. SLSA framework "
        "(Supply-chain Levels for Software Artifacts) formalises this."
    ),
    "D8-017": (
        "Inference attacks combine individually-AUTHORISED queries to deduce "
        "information the user is NOT authorised to see directly — e.g., averaging "
        "salaries by department to infer an individual's pay. Choice A (SQL "
        "injection) attacks query construction, not query result composition. "
        "Choice C (brute force) tries credentials. Choice D (SYN flood) is a "
        "network DoS. Mitigations for inference: query restriction, "
        "polyinstantiation, differential privacy, statistical noise."
    ),
    "D8-021": (
        "OAuth 2.0 client_credentials grant with SHORT-LIVED tokens (or mTLS for "
        "workload identity) is the modern service-to-service standard. Choice A "
        "(API keys in URLs) leaks them in proxy logs and browser history. Choice C "
        "(basic auth without TLS) sends credentials in cleartext. Choice D "
        "(hardcoded passwords) is the secret-sprawl pattern. Modern stacks: "
        "service mesh + workload identity + short-lived tokens."
    ),
    "D8-023": (
        "Avoid shells entirely — use parameterised APIs (e.g., subprocess with "
        "argv list, NOT shell=True) so input cannot break out of arguments into "
        "command syntax. If shell is unavoidable, strict allow-lists on input. "
        "Choice A (concatenate carefully) is the bug — careful concatenation still "
        "fails. Choice C (trust authenticated input) confuses authentication with "
        "authorisation. Choice D (hash input first) destroys legitimate input. "
        "CWE-78 captures OS command injection."
    ),
    "D8-030": (
        "SBOM-driven inventory + risk-based prioritisation (which services use "
        "the vulnerable lib, what's their exposure) + accelerated change "
        "management + verification is the manager-mindset answer. Choice A "
        "(quarterly window) accumulates risk. Choice C (disable logging) is "
        "anti-pattern. Choice D (overnight rewrite) introduces fresh untested "
        "code under pressure. The Log4Shell response in 2021 was the textbook "
        "example of this workflow."
    ),
    "D8-032": (
        "Cloud IAM least privilege requires: scoped roles (no '*' permissions), "
        "automated drift detection (IAM Access Analyzer, AWS Config rules), and "
        "JIT elevation via PAM for privileged operations. Choice A (grant '*' for "
        "convenience) is the #1 cloud misconfiguration per CSA. Choice C (disable "
        "IAM logging) destroys forensic capability. Choice D (share root keys) "
        "violates every IAM principle. Pattern: least privilege + drift + JIT = "
        "modern cloud IAM."
    ),
}


def main() -> None:
    rewritten = 0
    for q in QS:
        if q["id"] in REWRITES:
            q["explanation"] = REWRITES[q["id"]]
            rewritten += 1
    P.write_text(json.dumps(QS, indent=2))
    print(f"[+] Rewrote {rewritten}/{len(REWRITES)} additional explanations.")
    addressed = 0
    for q in QS:
        e = q["explanation"].lower()
        if any(s in e for s in ('choice a', 'choice b', 'choice c', 'choice d', 'wrong', 'incorrect', 'distractor')):
            addressed += 1
    print(f"  Total explanations addressing distractors: {addressed}/{len(QS)} ({100*addressed/len(QS):.0f}%)")


if __name__ == "__main__":
    main()
