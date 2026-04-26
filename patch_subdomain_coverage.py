#!/usr/bin/env python3
"""Add 28 questions covering under-represented 2024-outline subdomains:
1.10 Personnel security policies      (was 4 → +5)
1.11 Supply chain risk management     (was 3 → +5)
4.6  ICS / OT / IoT                   (was 1 → +5)
5.5  Authorization mechanisms         (was 6 → +5)
7.16 Personnel safety / duress        (was 0 → +3)
8.6  Acquired software / SaaS         (was 2 → +5)
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


NEW = [
    # ===== 1.10 Personnel Security Policies =====
    Q("D1-068", 1, "1.10 Personnel Security", "medium",
      "Which is the BEST control to enforce that no single employee can complete a sensitive financial transaction end-to-end?",
      ["Background checks at hire",
       "Separation of duties combined with mandatory dual approval",
       "Annual ethics training",
       "Job rotation alone"],
      1,
      "Separation of duties (SoD) plus dual control prevents a single insider from completing a sensitive workflow alone. Choice A (background checks) screens at hire but doesn't prevent post-hire fraud. Choice C (training) raises awareness but doesn't enforce process. Choice D (job rotation) is detective — it surfaces ongoing fraud after the fact, while SoD is preventive.",
      source="canonical", tags=["sod", "personnel", "manager-mindset"]),

    Q("D1-069", 1, "1.10 Personnel Security", "medium",
      "An employee with privileged access to a financial system unexpectedly resigns. What should happen FIRST?",
      ["Schedule an exit interview for next week",
       "Immediately disable all access (accounts, badges, VPN, MFA tokens) at the moment of departure",
       "Wait 30 days to allow knowledge transfer",
       "Transfer their accounts to the manager"],
      1,
      "Privileged access must be revoked at the MOMENT of departure — even unexpected resignations create insider-threat windows. Choice A (exit interview later) leaves the access window open. Choice C (wait 30 days) is the textbook insider-threat enabler. Choice D (transfer to manager) violates accountability and creates orphan privilege. HR-triggered automated deprovisioning is the modern best practice.",
      source="canonical", tags=["termination", "personnel", "manager-mindset"]),

    Q("D1-070", 1, "1.10 Personnel Security", "medium",
      "Which screening practice is the BEST defence against insider threat from new hires in highly-privileged roles?",
      ["Reference checks only",
       "Layered screening: identity verification, criminal history, credit check (where lawful and relevant), drug screen, professional reference verification, and adverse-media check",
       "Trust the resume",
       "Check social media only"],
      1,
      "Layered screening reduces the chance of hiring someone with adverse history that materially elevates insider-threat risk. Choice A (references alone) is easily gamed (friends-as-references). Choice C (trust the resume) is no screening at all. Choice D (social media alone) misses formal records. Higher-trust roles warrant deeper screening per a documented standard.",
      source="canonical", tags=["screening", "personnel", "insider-threat"]),

    Q("D1-071", 1, "1.10 Personnel Security", "medium",
      "What is the PRIMARY purpose of a Non-Disclosure Agreement (NDA) signed at hire?",
      ["To intimidate the employee",
       "To establish a legally enforceable obligation to protect confidential information, with named consequences for breach",
       "To replace need-to-know access controls",
       "To allow unrestricted information sharing within the organisation"],
      1,
      "An NDA creates a legally enforceable confidentiality obligation with consequences (termination, civil liability) — necessary alongside technical controls because controls fail. Choice A is not a security purpose. Choice C is wrong — NDAs supplement, never replace, technical access controls. Choice D contradicts the NDA's purpose. The exam pattern: legal contracts complement technical controls; neither stands alone.",
      source="canonical", tags=["nda", "personnel"]),

    Q("D1-072", 1, "1.10 Personnel Security", "medium",
      "Which is the BEST practice for managing access during an internal job transfer?",
      ["Add new role's permissions and keep old role's permissions",
       "Remove all access, then re-provision per the new role (zero-baseline)",
       "Have the employee request what they need",
       "Wait 90 days before any change"],
      1,
      "Zero-baseline transfer (drop everything, re-provision per new role) is the only reliable way to prevent privilege creep during job changes. Choice A is the textbook accumulation pattern that produces over-privileged long-tenured staff. Choice C is unreliable (employees request what they're used to having). Choice D leaves stale privileges in place. The exam answer is always 'remove old, then add new' for transfers.",
      source="canonical", tags=["privilege-creep", "transfer", "personnel"]),

    # ===== 1.11 Supply Chain Risk Management =====
    Q("D1-073", 1, "1.11 Supply Chain Risk Management", "medium",
      "Which is the BEST FIRST step when onboarding a new SaaS vendor that will process customer PII?",
      ["Sign the contract immediately",
       "Conduct a vendor risk assessment scaled to the data sensitivity and access scope",
       "Disable security monitoring during onboarding",
       "Trust the vendor's marketing materials"],
      1,
      "Risk-based assessment determines depth of further diligence: SOC 2 Type II review, on-site audit, contract terms (DPA, breach notification, right-to-audit). Choice A is contract-before-due-diligence — exactly backwards. Choice C is anti-pattern. Choice D substitutes sales material for evidence. The exam pattern: assess first, then contract, then continuous monitor.",
      source="canonical", tags=["vendor-risk", "scrm", "manager-mindset"]),

    Q("D1-074", 1, "1.11 Supply Chain Risk Management", "medium",
      "Which clause should be REQUIRED in a vendor contract handling regulated data, regardless of vendor reputation?",
      ["A clause prohibiting the vendor from using your name in marketing",
       "Right-to-audit, breach notification timeline, data residency, return/destruction at termination, and subcontractor disclosure requirements",
       "A flat-fee billing structure",
       "A non-compete clause"],
      1,
      "Right-to-audit + breach notification + data residency + offboarding + subcontractor disclosure are the load-bearing security clauses for any regulated-data vendor. Choice A (marketing) is reputational, not security. Choice C (billing) is commercial. Choice D (non-compete) addresses competition, not data protection. GDPR Art. 28 codifies most of these requirements for processors.",
      source="canonical", tags=["vendor-contract", "scrm"]),

    Q("D1-075", 1, "1.11 Supply Chain Risk Management", "medium",
      "What is the PRIMARY purpose of a Software Bill of Materials (SBOM) in supply chain risk management?",
      ["Marketing differentiation",
       "Provide a structured, machine-readable inventory of components and dependencies so vulnerability impact can be quickly assessed",
       "Replace SCA tooling",
       "Generate license revenue"],
      1,
      "SBOM (SPDX or CycloneDX format) lets you answer 'are we affected by CVE-X?' in minutes, not days — critical when 0-days like Log4Shell or XZ Utils break. US Executive Order 14028 mandates SBOMs for federal software. Choice A is unrelated. Choice C is wrong — SBOMs feed SCA, they don't replace it. Choice D is wrong — SBOMs are governance artefacts.",
      source="canonical", tags=["sbom", "scrm"]),

    Q("D1-076", 1, "1.11 Supply Chain Risk Management", "medium",
      "An organisation discovers their primary cloud provider was compromised at the infrastructure level. Which BCP element directly addresses this scenario?",
      ["Single-cloud lock-in for cost efficiency",
       "Multi-cloud or hybrid-cloud architecture with workload portability and tested failover procedures",
       "Trusting the cloud provider's SLA",
       "Disabling all cloud services"],
      1,
      "Multi-cloud/hybrid architecture with TESTED failover removes the single-provider failure mode. Choice A optimises cost while concentrating risk. Choice C — SLAs pay credits, they don't restore service. Choice D throws out the operational benefit entirely. Manager-mindset: critical workloads should never depend on any single vendor's continued operation.",
      source="canonical", tags=["scrm", "cloud", "bcp"]),

    Q("D1-077", 1, "1.11 Supply Chain Risk Management", "hard",
      "A critical open-source library used in your product has been found to contain a maintainer-introduced backdoor (e.g., the XZ Utils incident pattern). Which response set is BEST?",
      ["Continue using the library and hope for the best",
       "Pin to a known-good version, audit your dependency graph for exposure, monitor advisories, and contribute to or sponsor critical upstreams to reduce future risk",
       "Re-implement everything in-house immediately",
       "Switch to a paid commercial fork without analysis"],
      1,
      "Defensive hygiene: version pinning + dependency-graph audit + advisory monitoring + ecosystem investment is the realistic answer. Choice A ignores the threat. Choice C is impractical and introduces fresh untested code. Choice D substitutes one trust assumption for another. The exam pattern: layered controls + community engagement, not all-or-nothing reactions.",
      source="canonical", tags=["xz-utils", "scrm", "supply-chain"]),

    # ===== 4.6 ICS / OT / IoT =====
    Q("D4-053", 4, "4.6 ICS / OT", "medium",
      "Which is the BEST mitigation for legacy ICS/SCADA devices that cannot be patched without operational disruption?",
      ["Expose them to the internet with a strong password",
       "Network segmentation (Purdue model), passive monitoring with OT-aware IDS, and protocol-aware firewalls between IT and OT",
       "Disable all logging to reduce noise",
       "Replace immediately with consumer IoT"],
      1,
      "OT environments require the Purdue Enterprise Reference Architecture: rigid segmentation between business IT (level 4-5) and process control (level 0-3), passive monitoring (Dragos/Claroty/Nozomi style), and protocol-aware firewalls. Choice A is the recipe for industrial sabotage. Choice C destroys forensic capability. Choice D introduces consumer-grade vulnerabilities into critical operations.",
      source="canonical", tags=["ics", "scada", "purdue"]),

    Q("D4-054", 4, "4.6 IoT", "medium",
      "What is the GREATEST risk from an unmanaged IoT device on a flat corporate network?",
      ["Battery drain on the IoT device",
       "Lateral movement: a compromised IoT device becomes a foothold to pivot into high-value systems on the same broadcast domain",
       "Excessive electricity consumption",
       "Aesthetic clutter"],
      1,
      "IoT devices typically run outdated firmware with default credentials and exposed management — the Mirai botnet pattern. Once compromised, they pivot east-west on flat networks (lateral movement) into high-value targets. Mitigation: dedicated IoT VLAN, restrictive ACLs, outbound-only allow-lists. Choices A, C, D are operational concerns, not security risks.",
      source="canonical", tags=["iot", "lateral-movement", "segmentation"]),

    Q("D4-055", 4, "4.6 IoT", "medium",
      "An organisation deploys 10,000 industrial IoT sensors. Which key management approach is BEST?",
      ["Hardcode a single shared key into all devices",
       "Per-device cryptographic identity (e.g., X.509 cert provisioned at manufacture) with centralised PKI rotation",
       "No keys — clear-text only",
       "User-supplied passwords on each device"],
      1,
      "Per-device cryptographic identity with centralised lifecycle management is the modern IoT pattern (e.g., DPS in Azure IoT, AWS IoT Core just-in-time provisioning). Choice A creates a single-key compromise that owns the entire fleet. Choice C abandons confidentiality. Choice D doesn't scale and creates user-credential reuse problems. The pattern: never share keys across devices at scale.",
      source="canonical", tags=["iot", "pki", "key-management"]),

    Q("D4-056", 4, "4.6 ICS Protocols", "medium",
      "Why is Modbus TCP particularly risky in modern ICS environments?",
      ["It's too fast for industrial use",
       "Modbus has no built-in authentication or encryption — any device on the segment can read or write registers",
       "It requires AES-256 by default which is too slow",
       "It only works over fibre"],
      1,
      "Modbus (1979 era) has no auth and no encryption — assumed deployment was a physically isolated control network. On modern routable IP networks, anyone with reach can read sensors and command actuators. Mitigation: strict segmentation, protocol-aware firewall (deny writes from IT), wrapping in VPN/IPsec. Choices A, C, D are factually wrong.",
      source="canonical", tags=["modbus", "ics-protocols"]),

    Q("D4-057", 4, "4.6 IoT Lifecycle", "medium",
      "Which is the BIGGEST long-term risk of consumer IoT devices in enterprise environments?",
      ["High purchase cost",
       "Vendor end-of-life (EOL) leaves devices unpatched with known CVEs, but they remain on the network for years",
       "Excessive feature richness",
       "Bandwidth saturation"],
      1,
      "Consumer IoT vendors abandon devices after 2-5 years; enterprises run them for 7-10. The orphan-device pattern produces accumulating known-CVE risk on the network. Mitigation: lifecycle policies that mandate replacement at EOL or quarantine into segmented networks. Choices A, C, D are not the dominant risk pattern.",
      source="canonical", tags=["iot", "eol", "lifecycle"]),

    # ===== 5.5 Authorization Mechanisms =====
    Q("D5-054", 5, "5.5 Authorization", "medium",
      "Which authorization architecture component MAKES the access decision in an ABAC system?",
      ["The user's browser",
       "The Policy Decision Point (PDP), which evaluates the policy against attributes",
       "The Policy Enforcement Point (PEP) — it only enforces, not decides",
       "The DNS resolver"],
      1,
      "ABAC architecture: PEP (gateway) intercepts the request → asks the PDP → PDP evaluates policy → returns decision → PEP enforces. Choice A is the requester, not a decision-maker. Choice C is wrong — PEP enforces but doesn't decide; the question asks who DECIDES. Choice D is unrelated. NIST SP 800-162 formalises this PEP/PDP/PIP/PAP pattern.",
      source="canonical", tags=["abac", "pdp", "pep"]),

    Q("D5-055", 5, "5.5 Authorization", "medium",
      "Which standard provides an XML-based language for expressing access control policies and the request/response between PEP and PDP?",
      ["SAML", "XACML", "OAuth", "OpenID Connect"],
      1,
      "XACML (eXtensible Access Control Markup Language, OASIS standard) is the policy language for fine-grained ABAC — defines policy structure, attributes, and the request/response between PEP and PDP. Choice A (SAML) carries assertions but doesn't express policy. Choice C (OAuth) handles authorization grants, not policy expression. Choice D (OIDC) is authentication on OAuth.",
      source="canonical", tags=["xacml", "abac"]),

    Q("D5-056", 5, "5.5 Authorization", "medium",
      "Which RBAC concept allows a user to be assigned both a junior and a senior role, but only ACTIVATE one at a time per session?",
      ["Static separation of duty (SSoD)",
       "Dynamic separation of duty (DSoD)",
       "Role hierarchy",
       "Mutual exclusion"],
      1,
      "DSoD permits assignment of conflicting roles but prevents simultaneous activation in a single session — useful when one user must perform both duties at different times but never together. Choice A (SSoD) prevents the assignment itself — too rigid for some cases. Choice C (hierarchy) is about inheritance. Choice D (mutual exclusion) is the underlying concept SSoD/DSoD implement. The exam tests SSoD vs DSoD distinction directly.",
      source="canonical", tags=["dsod", "rbac"]),

    Q("D5-057", 5, "5.5 Authorization", "medium",
      "Which is the BEST description of 'Policy as Code' in modern authorization?",
      ["Hardcoding access rules into the application",
       "Authoring authorization policies in a declarative, version-controlled language (e.g., Rego/OPA, Cedar) that's evaluated by an external decision engine",
       "Storing policies as plaintext files",
       "Asking each user for permission individually"],
      1,
      "Policy-as-Code (OPA/Rego, AWS Cedar, Styra) treats policy as a first-class artefact — version controlled, code reviewed, tested, deployed independently of applications. Choice A is the anti-pattern PaC fixes. Choice C is half-right (text format) but misses the key point: declarative + external evaluation + governance. Choice D is impossible to scale. Modern microservices pattern.",
      source="canonical", tags=["policy-as-code", "opa", "cedar"]),

    Q("D5-058", 5, "5.5 Authorization", "medium",
      "What is the PRIMARY security advantage of capability-based access control over an ACL approach?",
      ["Capabilities are easier to remember",
       "Capabilities couple permission to the holder; possessing the capability is sufficient — eliminates the confused deputy problem and ambient-authority issues",
       "Capabilities are required by law",
       "Capabilities are faster to type"],
      1,
      "Capabilities (unforgeable tokens conferring rights) eliminate ambient authority and the confused deputy problem (where a privileged process is tricked into using its rights on behalf of an attacker). ACLs check identity at the resource — vulnerable to deputy confusion. Modern: OAuth tokens are capability-style. Choices A, C, D are not security advantages.",
      source="canonical", tags=["capability", "confused-deputy"]),

    # ===== 7.16 Personnel Safety / Duress =====
    Q("D7-054", 7, "7.16 Personnel Safety", "medium",
      "What is the PRIMARY purpose of a duress code/PIN in physical or logical access systems?",
      ["A faster login shortcut",
       "Allow the user to silently signal coercion (e.g., armed robbery) while appearing to comply, triggering covert alarms",
       "A backup admin password",
       "A vendor support code"],
      1,
      "A duress code looks like a normal credential but covertly alerts security/police while granting controlled access — used in bank vaults, datacenter mantraps, alarm panels. Choice A misframes the purpose. Choice C is generic admin access (a different concept). Choice D is unrelated. The user's life takes precedence over assets — duress codes save lives without escalating the situation.",
      source="canonical", tags=["duress", "personnel-safety"]),

    Q("D7-055", 7, "7.16 Personnel Safety", "medium",
      "During an active workplace violence incident, what should always take PRIORITY?",
      ["Protect the data center",
       "Life safety — evacuate or shelter people, then call emergency services",
       "Document the event in the SIEM",
       "Notify the marketing department"],
      1,
      "Life safety always wins over technology, data, and assets — a recurring CISSP theme tested explicitly in physical security questions. Choice A inverts the priority. Choice C delays the action. Choice D is irrelevant in the moment. The pattern: people first, then property, then data — never the reverse.",
      source="canonical", tags=["life-safety", "manager-mindset"]),

    Q("D7-056", 7, "7.16 Personnel Safety", "medium",
      "An after-hours security guard discovers a flooded server room with rising water near energised equipment. What is the FIRST action?",
      ["Begin moving servers to dry ground",
       "Cut power to the affected area, then evacuate non-essential personnel and call emergency services",
       "Take photos for the insurance claim",
       "Restore data from backup immediately"],
      1,
      "Energised equipment + water = electrocution risk. Cut power (life safety) BEFORE attempting any equipment recovery. Choice A risks the guard's life. Choice C and D are post-event activities. CISSP physical-security questions consistently rank: protect life → prevent injury → minimise property damage → preserve evidence → restore operations.",
      source="canonical", tags=["life-safety", "physical"]),

    # ===== 8.6 Acquired Software / SaaS =====
    Q("D8-042", 8, "8.6 Acquired Software", "medium",
      "What is the BEST process for evaluating security of an acquired commercial software package before deployment?",
      ["Trust the vendor's marketing claims",
       "Vendor security questionnaire + SOC 2 Type II review + threat modeling against your environment + integration testing in an isolated environment",
       "Deploy directly to production and monitor",
       "Skip evaluation if the software is widely used"],
      1,
      "Layered evaluation: questionnaire (process), SOC 2 (controls), threat model (your context), isolated test (real behavior). Choice A is no evaluation. Choice C bypasses controls and risks production impact. Choice D ('widely used') is exactly how Log4Shell, MOVEit, and SolarWinds spread. The exam pattern: third-party software is your risk, regardless of who built it.",
      source="canonical", tags=["acquired-software", "vendor-risk"]),

    Q("D8-043", 8, "8.6 SaaS Security", "medium",
      "Which security responsibility ALWAYS remains with the customer in a SaaS arrangement?",
      ["Patching the underlying database",
       "Identity and access management for customer users + data classification + data ingest decisions + offboarding the data",
       "Maintaining the data center",
       "Hypervisor configuration"],
      1,
      "In SaaS, customers retain: who has access (IAM), what data goes in (classification), and how to exit (offboarding/data return). The provider handles infrastructure, platform, and most of the application. Choices A, C, D are provider responsibilities in SaaS. Knowing the responsibility split per service model (IaaS/PaaS/SaaS) is high-yield exam content.",
      source="canonical", tags=["saas", "shared-responsibility"]),

    Q("D8-044", 8, "8.6 Open Source", "medium",
      "Which is the BEST approach for evaluating an open-source library before adoption?",
      ["GitHub stars only",
       "Activity (recent commits, responsive maintainers), security history (CVEs, response time), community size, license compatibility, dependency footprint, and SBOM availability",
       "Whether it has a logo",
       "Use any library that compiles"],
      1,
      "Open-source evaluation is multi-dimensional: maintainer activity, security responsiveness, community, license, dependency footprint, SBOM. Choice A (stars) is trivially gameable. Choice C (logo) is irrelevant. Choice D (just compiles) is the supply-chain attack pathway. The XZ Utils backdoor passed all the trivial checks — only deep evaluation catches deliberate compromise.",
      source="canonical", tags=["open-source", "supply-chain"]),

    Q("D8-045", 8, "8.6 SaaS", "medium",
      "What is the BEST control for limiting blast radius if a SaaS vendor's API is compromised and starts requesting your customer data?",
      ["Trust the SaaS provider entirely",
       "Scope OAuth tokens and API keys to least-privilege resources, rotate regularly, and monitor data egress with anomaly detection",
       "Disable all integrations",
       "Use a single shared admin token across all integrations"],
      1,
      "Least-privilege scoped tokens + rotation + egress monitoring limits damage when (not if) a vendor is compromised. Choice A is no control. Choice C overcorrects and breaks operations. Choice D is the worst possible pattern — one compromised token = total exposure. The Snowflake/Twilio incidents in 2024 illustrate this perfectly: vendor compromise + over-scoped tokens = enterprise customer data leaks.",
      source="canonical", tags=["saas", "oauth", "least-privilege"]),

    Q("D8-046", 8, "8.6 Acquired Software", "medium",
      "An acquired enterprise application requires running with local admin privileges. What is the BEST mitigation?",
      ["Just give it admin and move on",
       "Application allowlisting + dedicated service account + privilege segmentation (run only the privileged components elevated) + close monitoring of the account's behaviour",
       "Disable the application entirely",
       "Run all workstations with admin privileges"],
      1,
      "When an app demands privilege, isolate the impact: dedicated service account (not user accounts), allowlisting (only this binary can execute), privilege segmentation (only the necessary component runs elevated), behaviour monitoring (alert on deviation). Choice A grants enterprise admin. Choice C overrides business need. Choice D inverts least privilege. Manager-mindset: when you can't fix the app, contain it.",
      source="canonical", tags=["least-privilege", "acquired-software"]),
]


def main() -> None:
    existing = {q["id"] for q in QS}
    added = 0
    for nq in NEW:
        if nq["id"] in existing:
            print(f"  skip {nq['id']} (already exists)")
            continue
        QS.append(nq)
        added += 1
    P.write_text(json.dumps(QS, indent=2))
    print(f"[+] Added {added} subdomain-coverage questions.")
    print(f"  Total questions now: {len(QS)}")
    by_d = {}
    for q in QS:
        by_d[q["domain"]] = by_d.get(q["domain"], 0) + 1
    for d in sorted(by_d):
        print(f"    D{d}: {by_d[d]} ({100*by_d[d]/len(QS):.1f}%)")


if __name__ == "__main__":
    main()
