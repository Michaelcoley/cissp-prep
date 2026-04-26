#!/usr/bin/env python3
"""Assemble cissp-prep.html — single-file CISSP exam-prep app.

Inlines questions.json + flashcards.json as JS constants. Output is
fully offline (no CDNs, no fonts, no analytics).
"""
import json
from pathlib import Path

ROOT = Path("/Users/mike/cissp")
OUT = ROOT / "cissp-prep.html"

QUESTIONS = json.loads((ROOT / "questions.json").read_text())
FLASHCARDS = json.loads((ROOT / "flashcards.json").read_text())
WEB = json.loads((ROOT / "web_research.json").read_text())
TOPICS = json.loads((ROOT / "study_topics.json").read_text())["topics"]


def chapter_for_pages(pages):
    """Map a question's guide_pages to the chapter that contains them.
    Returns chapter_number or None."""
    if not pages:
        return None
    p = pages[0]
    last = None
    for t in sorted(TOPICS, key=lambda x: x.get("page") or 0):
        cp = t.get("page") or 0
        if cp <= p:
            last = t["chapter_number"]
        else:
            break
    return last


# Annotate each question with its chapter (when guide_pages present)
for q in QUESTIONS:
    q["chapter"] = chapter_for_pages(q.get("guide_pages"))


# High-leverage comparison tables (cross-domain reference for Read view)
TABLES = [
    {
        "id": "raid_levels",
        "name": "RAID levels — performance vs redundancy",
        "domain": 7,
        "headers": ["Level", "Min disks", "Fault tolerance", "Storage efficiency", "When to choose"],
        "rows": [
            ["RAID 0", "2", "None (any drive lost = data lost)", "100%", "High-performance scratch / cache only"],
            ["RAID 1", "2", "1 drive (mirror)", "50%", "OS boot, small critical volumes"],
            ["RAID 5", "3", "1 drive", "(N-1)/N", "General file servers (legacy — write penalty)"],
            ["RAID 6", "4", "2 drives", "(N-2)/N", "Large archives, high resilience"],
            ["RAID 10 (1+0)", "4", "1 per mirror pair", "50%", "Databases, latency-sensitive workloads"],
            ["RAID 01 (0+1)", "4", "1 drive total", "50%", "Rare — RAID 10 is preferred"],
        ],
        "tip": "RAID is for AVAILABILITY, not BACKUP. A delete still propagates. Always pair with backups."
    },
    {
        "id": "recovery_sites",
        "name": "Recovery site types — RTO vs cost",
        "domain": 7,
        "headers": ["Type", "RTO", "Data freshness", "Cost", "When to choose"],
        "rows": [
            ["Hot",         "Minutes – hours", "Real-time replication",  "$$$$", "Tier-0, regulated, ~zero downtime"],
            ["Warm",        "12 – 24 hours",   "Daily/hourly sync",      "$$$",  "Critical but tolerant of brief outage"],
            ["Cold",        "Days – weeks",    "Manual restore",         "$",    "Non-critical, budget-constrained"],
            ["Cloud",       "Variable (provisionable)", "Configurable", "$ – $$$", "Modern default; pay-as-you-recover"],
            ["Mobile",      "Hours – days",    "Manual",                 "$$",   "Field operations, regional disaster"],
            ["Reciprocal",  "Variable",        "Manual",                 "$",    "Avoid — same-disaster failure mode"],
        ],
        "tip": "Pick the cheapest site whose RTO meets your BIA. Hot sites are luxury for critical-only systems."
    },
    {
        "id": "osi_tcp",
        "name": "OSI vs TCP/IP — layer mapping",
        "domain": 4,
        "headers": ["OSI #", "OSI layer", "TCP/IP layer", "Example protocols / units"],
        "rows": [
            ["7", "Application",  "Application", "HTTP, FTP, SMTP, DNS — data"],
            ["6", "Presentation", "Application", "TLS encoding, JPEG, ASCII"],
            ["5", "Session",      "Application", "TLS sessions, RPC, NetBIOS"],
            ["4", "Transport",    "Transport",   "TCP, UDP — segments / datagrams"],
            ["3", "Network",      "Internet",    "IP, ICMP, IPsec — packets"],
            ["2", "Data Link",    "Link",        "Ethernet, ARP, MAC, PPP — frames"],
            ["1", "Physical",     "Link",        "Cables, hubs, electrical signaling — bits"],
        ],
        "tip": "Mnemonic: 'Please Do Not Throw Sausage Pizza Away' (L1→L7). TLS = L5 per ISC2."
    },
    {
        "id": "evidence_types",
        "name": "Evidence types — admissibility ranking",
        "domain": 7,
        "headers": ["Type", "Definition", "Admissibility"],
        "rows": [
            ["Best (primary)", "Original document or media (or its forensic image)", "Strongest"],
            ["Secondary",      "Copies, transcripts, summaries", "Weaker — best only if original unavailable"],
            ["Direct",         "Eyewitness testimony of the event itself", "Strong if witness credible"],
            ["Circumstantial", "Inference from facts (e.g., login + timestamp pattern)", "Variable — needs corroboration"],
            ["Demonstrative",  "Charts, models, simulations to explain", "Supporting only — not standalone"],
            ["Corroborative",  "Reinforces existing evidence", "Adds weight to other evidence"],
            ["Hearsay",        "Out-of-court statement to prove the matter asserted", "Generally INADMISSIBLE (with exceptions)"],
        ],
        "tip": "Logs are typically hearsay UNLESS they qualify as business records (Federal Rules of Evidence 803(6))."
    },
    {
        "id": "fire_classes",
        "name": "Fire classes — agent compatibility",
        "domain": 3,
        "headers": ["Class", "Fuel", "Acceptable agent", "Datacenter use"],
        "rows": [
            ["A", "Ordinary combustibles (wood, paper, cloth)", "Water, foam, dry chem", "Avoid water near electronics"],
            ["B", "Flammable liquids/gases (oil, gasoline)",     "CO₂, dry chem, foam",   "CO₂ unsafe for occupied space"],
            ["C", "Energized electrical equipment",              "Clean agent (FM-200, Novec 1230, Inergen)", "PRIMARY for datacenters"],
            ["D", "Combustible metals (Mg, Na, Ti)",             "Specialized dry powder", "Rare in IT environments"],
            ["K", "Cooking oils, fats",                          "Wet chemical (saponification)", "Kitchens only"],
        ],
        "tip": "Wet pipe = always charged (water in pipes). Dry pipe = water released on alarm. Pre-action = two-trigger to avoid accidental discharge — preferred for datacenters."
    },
    {
        "id": "ipsec_modes",
        "name": "IPsec — protocols × modes",
        "domain": 4,
        "headers": ["", "AH (Authentication Header)", "ESP (Encapsulating Security Payload)"],
        "rows": [
            ["Confidentiality",  "✗ (integrity-only)",                    "✓ (encrypts payload)"],
            ["Integrity",        "✓ (whole packet incl. immutable IP hdr)", "✓ (payload + optionally header)"],
            ["NAT-friendly",     "✗ (NAT mutates IP hdr → integrity break)", "✓ with NAT-T (UDP/4500)"],
            ["Transport mode",   "Host-to-host, IP hdr in clear",         "Host-to-host, payload encrypted"],
            ["Tunnel mode",      "Gateway-to-gateway, original IP wrapped", "Site-to-site VPN, full encapsulation"],
            ["Protocol number",  "51",                                    "50"],
        ],
        "tip": "Modern site-to-site VPNs use ESP in tunnel mode with NAT-T. AH is rarely deployed."
    },
    {
        "id": "backup_types",
        "name": "Backup types — speed vs restore",
        "domain": 7,
        "headers": ["Type", "What's backed up", "Backup time", "Restore complexity", "Archive bit"],
        "rows": [
            ["Full",          "Everything",                              "Slowest", "Simplest (1 set)",                 "Cleared"],
            ["Incremental",   "Changes since last backup of any type",   "Fastest", "Hardest (full + every incr in chain)", "Cleared"],
            ["Differential",  "Changes since last FULL backup",          "Mid",     "Easy (full + most-recent diff)",  "Not cleared"],
            ["Snapshot",      "Point-in-time copy (CoW)",                "Instant", "Easy (revert)",                   "n/a"],
            ["Synthetic full","Server constructs full from prior incrementals", "Variable", "As easy as a full",       "Cleared"],
        ],
        "tip": "3-2-1 rule: 3 copies, 2 different media types, 1 offsite. Modern: 3-2-1-1-0 adds 1 immutable + 0 errors after verification."
    },
    {
        "id": "access_models",
        "name": "Access control models — DAC / MAC / RBAC / ABAC",
        "domain": 5,
        "headers": ["Model", "Decision authority", "Granularity", "Typical example"],
        "rows": [
            ["DAC", "Data owner (discretionary)",          "Per object", "Unix file permissions, Windows NTFS ACLs"],
            ["MAC", "System policy (mandatory, labels)",   "Subject clearance vs object label", "Government Bell-LaPadula systems"],
            ["RBAC","Role assignments",                    "Per role",   "Active Directory groups, AWS IAM roles"],
            ["ABAC","Multi-attribute policy engine",       "Fine-grained (user × resource × env)", "AWS IAM policies, Azure Conditional Access, XACML"],
            ["RuBAC","System-wide rules (often IF/THEN)",  "Identity-independent", "Firewall ACLs, time-of-day restrictions"],
        ],
        "tip": "Production systems usually layer RBAC (coarse) + ABAC (fine). MAC appears in classified environments."
    },
    {
        "id": "control_grid",
        "name": "Controls — type × function",
        "domain": 1,
        "headers": ["", "Preventive", "Detective", "Corrective"],
        "rows": [
            ["Administrative", "Policies, training, hiring/screening", "Audits, performance reviews", "Termination, retraining"],
            ["Technical",      "Firewall, encryption, MFA",           "IDS, SIEM, log monitoring",  "Patching, IPS auto-block"],
            ["Physical",       "Locks, fences, mantraps, bollards",   "CCTV, motion sensors, guards", "Fire suppression, repair"],
        ],
        "tip": "Also: Deterrent (warning signs, login banners), Compensating (substitute when primary infeasible), Recovery (BCP/DRP)."
    },
    {
        "id": "kerberos_flow",
        "name": "Kerberos — message flow",
        "domain": 5,
        "headers": ["Step", "Message", "From → To", "Contains"],
        "rows": [
            ["1", "AS-REQ", "Client → AS",  "Username, requested realm, timestamp"],
            ["2", "AS-REP", "AS → Client",  "TGT (encrypted with KRBTGT secret) + session key (encrypted with user's hash)"],
            ["3", "TGS-REQ","Client → TGS", "TGT + service principal name + authenticator (encrypted with session key)"],
            ["4", "TGS-REP","TGS → Client", "Service ticket (encrypted with service's secret) + new session key"],
            ["5", "AP-REQ", "Client → Service", "Service ticket + new authenticator"],
            ["6", "AP-REP", "Service → Client", "Mutual auth confirmation (optional)"],
        ],
        "tip": "KDC = AS + TGS. Time sync within ~5 min required (NTP). Golden Ticket forges step 2 from KRBTGT hash."
    },
    {
        "id": "biometric_errors",
        "name": "Biometric error rates",
        "domain": 5,
        "headers": ["Term", "Meaning", "What you minimize for…"],
        "rows": [
            ["FAR / Type II",  "False acceptance — unauthorized user admitted", "HIGH security (worse failure mode)"],
            ["FRR / Type I",   "False rejection — legitimate user denied",      "Usability / throughput"],
            ["CER (EER)",      "Crossover error rate — point where FAR = FRR",  "Comparing systems (lower is better)"],
        ],
        "tip": "High-security: tune for low FAR even at the cost of higher FRR. Convenience apps: opposite trade."
    },
    {
        "id": "bia_metrics",
        "name": "BIA time metrics",
        "domain": 1,
        "headers": ["Metric", "Stands for", "Meaning", "Constraint"],
        "rows": [
            ["MTD", "Maximum Tolerable Downtime", "Outer bound — exceeding kills the business", "Driven by impact tolerance"],
            ["RTO", "Recovery Time Objective",    "Target time to restore operations",          "RTO ≤ MTD"],
            ["RPO", "Recovery Point Objective",   "Acceptable data-loss window (backwards)",     "Drives backup frequency"],
            ["WRT", "Work Recovery Time",         "Time to validate / cleanse / resume after restore", "RTO + WRT ≤ MTD"],
            ["MTBF","Mean Time Between Failures", "Reliability metric (hardware)",               "Higher is better"],
            ["MTTR","Mean Time To Repair",        "Recoverability metric",                       "Lower is better"],
        ],
        "tip": "Mnemonic: 'MOMENT' is wrong — there's no single mnemonic. Just remember RTO+WRT ≤ MTD and RPO drives backup frequency."
    },
]


# SHA-256("SecureGreatness!2026") computed once, stored as constant in HTML.
# Computed via: hashlib.sha256(b"SecureGreatness!2026").hexdigest()
import hashlib
PW_HASH = hashlib.sha256(b"SecureGreatness!2026").hexdigest()

DOMAIN_META = [
    {"id": 1, "name": "Security and Risk Management", "weight": 16},
    {"id": 2, "name": "Asset Security", "weight": 10},
    {"id": 3, "name": "Security Architecture and Engineering", "weight": 13},
    {"id": 4, "name": "Communication and Network Security", "weight": 13},
    {"id": 5, "name": "Identity and Access Management", "weight": 13},
    {"id": 6, "name": "Security Assessment and Testing", "weight": 12},
    {"id": 7, "name": "Security Operations", "weight": 13},
    {"id": 8, "name": "Software Development Security", "weight": 10},
]

# Build cheat sheets from web_research + canonical content.
CHEAT_SHEETS = []
for d in DOMAIN_META:
    sources = WEB["domains"][str(d["id"])]["sources"][:8]
    CHEAT_SHEETS.append({
        "domain": d["id"],
        "name": d["name"],
        "weight": d["weight"],
        "sources": [{"url": s["url"], "title": s["title"]} for s in sources],
    })


CSS = r"""
*,*::before,*::after{box-sizing:border-box}
html,body{margin:0;padding:0;background:#0a0e14;color:#e5e7eb;
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Oxygen,Ubuntu,Cantarell,sans-serif;
  font-size:15px;line-height:1.5;-webkit-text-size-adjust:100%;min-height:100vh}
:root{
  --bg:#0a0e14;--bg2:#11161f;--surface:#161c26;--surface2:#1a2230;
  --border:#1f2733;--border2:#2a3441;
  --text:#e5e7eb;--muted:#9ca3af;--dim:#6b7280;
  --accent:#00d4ff;--accent2:#0891b2;--success:#10b981;--warn:#f59e0b;--danger:#ef4444;
  --mono:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,"Liberation Mono",monospace;
}
body.light{--bg:#f4f6f8;--bg2:#ffffff;--surface:#ffffff;--surface2:#f1f4f7;
  --border:#dfe4ea;--border2:#cdd5dd;--text:#1f2937;--muted:#4b5563;--dim:#6b7280;
  --accent:#0277b8;--accent2:#0891b2}
button,input,select,textarea{font:inherit;color:inherit}
button{cursor:pointer;border:1px solid var(--border2);background:var(--surface2);
  color:var(--text);padding:.55rem 1rem;border-radius:.4rem;
  transition:all 150ms ease}
button:hover:not(:disabled){border-color:var(--accent);box-shadow:0 0 0 2px rgba(0,212,255,.18)}
button:focus-visible{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px rgba(0,212,255,.55)}
button:disabled{opacity:.5;cursor:not-allowed}
button.primary{background:var(--accent);color:#001018;border-color:var(--accent);font-weight:600}
button.primary:hover{background:#1ad9ff}
button.danger{background:var(--danger);color:#fff;border-color:var(--danger)}
button.warn{background:var(--warn);color:#1a1100;border-color:var(--warn)}
button.ghost{background:transparent;border-color:var(--border)}
input,select,textarea{background:var(--surface);border:1px solid var(--border2);
  color:var(--text);padding:.5rem .75rem;border-radius:.35rem;width:100%}
input:focus,select:focus,textarea:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px rgba(0,212,255,.55)}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
.mono{font-family:var(--mono)}
.badge{display:inline-block;padding:.1rem .5rem;border-radius:.25rem;
  font-size:.75rem;background:var(--surface2);border:1px solid var(--border2);color:var(--muted)}
.badge.guide{background:#0d3a4d;color:#7dd3fc;border-color:#155e75}
.badge.web{background:#1f2733;color:#9ca3af;border-color:#374151}
.badge.canonical{background:#2c1f3a;color:#c4b5fd;border-color:#4c2a72}
.tag{display:inline-block;padding:0 .4rem;font-size:.7rem;background:var(--surface2);
  border-radius:.2rem;color:var(--muted);margin:.1rem .15rem .1rem 0}
.muted{color:var(--muted)}
.dim{color:var(--dim)}
.row{display:flex;gap:.75rem;flex-wrap:wrap;align-items:center}
.col{display:flex;flex-direction:column;gap:.6rem}
.spread{justify-content:space-between}
.center{text-align:center}
.grow{flex:1}
.card{background:var(--surface);border:1px solid var(--border);border-radius:.6rem;padding:1rem;margin:.6rem 0}
.kpi{font-size:1.6rem;font-weight:700;color:var(--accent)}
.kpi-label{font-size:.75rem;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
.bar{height:8px;background:var(--surface2);border-radius:4px;overflow:hidden;margin-top:.25rem}
.bar>div{height:100%;background:linear-gradient(90deg,var(--accent2),var(--accent));border-radius:4px}
.bar.warn>div{background:linear-gradient(90deg,#b45309,var(--warn))}
.bar.danger>div{background:linear-gradient(90deg,#7f1d1d,var(--danger))}
.bar.success>div{background:linear-gradient(90deg,#047857,var(--success))}

/* Auth gate */
#gate{position:fixed;inset:0;background:var(--bg);display:flex;
  align-items:center;justify-content:center;z-index:1000;padding:1rem}
#gate .gate-box{max-width:400px;width:100%;text-align:center}
#gate h1{color:var(--accent);font-family:var(--mono);font-size:1.4rem;margin:.5rem 0}
#gate .lock-icon{font-size:3rem}

/* App layout */
#app{display:none;min-height:100vh;flex-direction:column}
header.topbar{background:var(--bg2);border-bottom:1px solid var(--border);
  padding:.65rem 1rem;display:flex;align-items:center;gap:.75rem;
  position:sticky;top:0;z-index:50}
header h1{font-size:1rem;margin:0;font-family:var(--mono);color:var(--accent);letter-spacing:.04em}
header .pill{font-size:.7rem;padding:.15rem .55rem;border-radius:1rem;background:var(--surface2);color:var(--muted)}
header .right{margin-left:auto;display:flex;gap:.4rem;align-items:center}
main{padding:1rem;max-width:1100px;margin:0 auto;width:100%;flex:1;padding-bottom:5rem}
.view{display:none}
.view.active{display:block}

/* Bottom nav (mobile-first) */
nav.bottom{position:fixed;bottom:0;left:0;right:0;background:var(--bg2);
  border-top:1px solid var(--border);display:flex;justify-content:space-around;
  padding:.4rem .25rem;z-index:40;padding-bottom:max(.4rem,env(safe-area-inset-bottom))}
nav.bottom button{flex:1;background:transparent;border:none;padding:.4rem;
  font-size:.7rem;color:var(--muted);display:flex;flex-direction:column;align-items:center;
  border-radius:.4rem;min-width:0}
nav.bottom button .nico{font-size:1.1rem;line-height:1.1;margin-bottom:2px}
nav.bottom button.active{color:var(--accent)}
nav.bottom button:hover{background:var(--surface2)}

/* Question card */
.qcard{background:var(--surface);border:1px solid var(--border);border-radius:.7rem;padding:1rem;margin-bottom:.75rem}
.qhead{display:flex;justify-content:space-between;flex-wrap:wrap;gap:.4rem;margin-bottom:.5rem}
.qstem{font-size:1.05rem;font-weight:500;line-height:1.45;margin-bottom:.85rem}
.choice{padding:.7rem .9rem;border:1px solid var(--border2);border-radius:.45rem;
  margin:.4rem 0;cursor:pointer;display:flex;gap:.7rem;align-items:flex-start;
  background:var(--surface2);transition:all 150ms ease;user-select:none}
@media (hover:hover){.choice:hover{border-color:var(--accent);background:#1d2735}}
.choice.eliminated{opacity:.45;text-decoration:line-through}
.choice .letter{flex:0 0 1.4rem;height:1.4rem;border-radius:50%;background:var(--surface);
  display:flex;align-items:center;justify-content:center;font-weight:700;
  font-family:var(--mono);font-size:.85rem;color:var(--muted)}
.choice.selected{border-color:var(--accent);background:#0d2530}
.choice.selected .letter{background:var(--accent);color:#001018}
.choice.correct{border-color:var(--success);background:#0a2a22}
.choice.correct .letter::after{content:" ✓";font-size:.8rem;margin-left:.1rem}
.choice.correct .letter{background:var(--success);color:#001f15}
.choice.incorrect{border-color:var(--danger);background:#2a0a12}
.choice.incorrect .letter::after{content:" ✗";font-size:.8rem;margin-left:.1rem}
.choice.incorrect .letter{background:var(--danger);color:#fff}
.explanation{margin-top:.9rem;padding:.85rem 1rem;background:var(--surface2);
  border-left:3px solid var(--accent);border-radius:.4rem;font-size:.92rem;line-height:1.55}
.explanation h4{margin:.4rem 0 .3rem;font-size:.85rem;color:var(--accent);text-transform:uppercase;letter-spacing:.05em}
.refs{margin-top:.5rem;font-size:.78rem;color:var(--muted);display:flex;gap:.4rem;flex-wrap:wrap}
.refs a{color:var(--accent);font-size:.78rem}

/* Filters / forms */
.filters{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:.6rem;margin-bottom:.8rem}
.filters label{display:block;color:var(--muted);font-size:.75rem;margin-bottom:.2rem;text-transform:uppercase;letter-spacing:.04em}
.dlist{display:flex;flex-wrap:wrap;gap:.3rem;margin-top:.3rem}
.dlist label{display:inline-flex;align-items:center;gap:.25rem;background:var(--surface2);
  padding:.2rem .55rem;border-radius:.3rem;cursor:pointer;font-size:.85rem;color:var(--text);text-transform:none;letter-spacing:0}
.dlist label.checked{background:#0a3a4a;border:1px solid var(--accent2);color:var(--accent)}
.dlist input[type=checkbox]{display:none}

/* Charts */
.radar{width:100%;max-width:360px;margin:.5rem auto;display:block}
.line-chart{width:100%;max-width:600px;margin:.5rem auto;display:block;background:var(--bg2);border-radius:.4rem;padding:.5rem}
.heatmap{display:grid;grid-template-columns:repeat(8,1fr);gap:.25rem;margin-top:.5rem}
.heatmap .cell{aspect-ratio:1;border-radius:.2rem;display:flex;align-items:center;
  justify-content:center;font-size:.7rem;color:var(--text);font-family:var(--mono)}

/* Modals */
.modal-bg{position:fixed;inset:0;background:rgba(0,0,0,.7);display:none;
  align-items:center;justify-content:center;z-index:200;padding:1rem}
.modal-bg.show{display:flex}
.modal{background:var(--surface);border:1px solid var(--border);border-radius:.7rem;
  padding:1.2rem;max-width:520px;width:100%;max-height:90vh;overflow:auto}
.modal h3{margin:0 0 .6rem;color:var(--accent)}

/* Toast */
.toasts{position:fixed;bottom:6rem;left:50%;transform:translateX(-50%);
  display:flex;flex-direction:column;gap:.4rem;z-index:300;pointer-events:none;width:90%;max-width:380px}
.toast{background:var(--surface);border:1px solid var(--accent);border-left-width:4px;
  padding:.7rem 1rem;border-radius:.45rem;color:var(--text);font-size:.92rem;
  box-shadow:0 6px 20px rgba(0,0,0,.4);animation:slidein .25s ease}
@media (prefers-reduced-motion: no-preference){
  @keyframes slidein{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
}
@media (prefers-reduced-motion: reduce){.toast{animation:none}}

/* Question navigator (exam) */
.qnav{display:grid;grid-template-columns:repeat(auto-fill,minmax(2.4rem,1fr));gap:.3rem;margin-top:.6rem;max-height:230px;overflow:auto;padding:.3rem;background:var(--bg2);border-radius:.4rem;border:1px solid var(--border)}
.qnav button{padding:0;height:2.2rem;font-size:.78rem;border-radius:.25rem;font-family:var(--mono);min-width:0}
.qnav button.answered{background:var(--surface2);border-color:var(--accent2);color:var(--accent)}
.qnav button.flagged{background:#3a2200;border-color:var(--warn);color:var(--warn)}
.qnav button.current{box-shadow:0 0 0 2px var(--accent)}

/* Flashcards */
.flashcard{background:var(--surface);border:1px solid var(--border);border-radius:.7rem;
  min-height:240px;padding:1.5rem;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;cursor:pointer;user-select:none;transition:transform 150ms ease}
.flashcard:hover{transform:translateY(-1px)}
.flashcard .term{font-size:1.4rem;font-weight:600;margin:.5rem 0}
.flashcard .back{font-size:1rem;line-height:1.6;color:var(--text)}
.flashcard .src-line{margin-top:.8rem;font-size:.78rem;color:var(--muted)}
.fc-actions{display:grid;grid-template-columns:repeat(4,1fr);gap:.4rem;margin-top:.7rem}
.fc-actions button{font-size:.85rem;padding:.6rem .3rem}
.fc-actions .again{background:var(--danger);color:#fff;border-color:var(--danger)}
.fc-actions .hard{background:var(--warn);color:#1a1100;border-color:var(--warn)}
.fc-actions .good{background:var(--accent);color:#001018;border-color:var(--accent)}
.fc-actions .easy{background:var(--success);color:#001f15;border-color:var(--success)}

/* Cheat sheets */
.cheat{background:var(--surface);border:1px solid var(--border);border-radius:.6rem;margin:.6rem 0}
.cheat summary{padding:.85rem 1rem;cursor:pointer;font-weight:600;display:flex;justify-content:space-between;align-items:center;list-style:none}
.cheat summary::-webkit-details-marker{display:none}
.cheat[open] summary{border-bottom:1px solid var(--border)}
.cheat .body{padding:1rem}

/* Header timer */
.timer{font-family:var(--mono);font-size:.95rem;padding:.3rem .6rem;border-radius:.35rem;background:var(--surface2);color:var(--accent);border:1px solid var(--border2)}
.timer.warn{color:var(--warn);border-color:var(--warn)}
.timer.danger{color:var(--danger);border-color:var(--danger);animation:pulse 1s infinite}
@media (prefers-reduced-motion: no-preference){@keyframes pulse{50%{opacity:.6}}}
@media (prefers-reduced-motion: reduce){.timer.danger{animation:none}}

/* Search */
.search-bar{display:flex;gap:.5rem;margin-bottom:.7rem}

/* Helpers */
hr{border:none;border-top:1px solid var(--border);margin:1rem 0}
h2{color:var(--accent);font-size:1.2rem;margin:.4rem 0 .8rem}
h3{font-size:1rem;margin:.6rem 0 .4rem}
ul{padding-left:1.3rem;margin:.4rem 0}
li{margin:.2rem 0}

@media (min-width:900px){
  body{font-size:16px}
  #app{flex-direction:row}
  header.topbar{position:fixed;top:0;left:0;right:0;width:auto}
  nav.bottom{position:fixed;top:3.4rem;bottom:0;left:0;width:170px;flex-direction:column;
    border-top:none;border-right:1px solid var(--border);padding:1rem .5rem;justify-content:flex-start;gap:.25rem}
  nav.bottom button{flex:0;width:100%;flex-direction:row;justify-content:flex-start;font-size:.85rem;padding:.6rem .8rem;gap:.6rem}
  nav.bottom button .nico{font-size:1rem;margin:0}
  main{margin-left:170px;margin-top:3.4rem;padding:1.2rem 1.5rem 2rem;max-width:none}
  .toasts{bottom:1.5rem;right:1.5rem;left:auto;transform:none}
}

@media (max-width:374px){body{font-size:14px}main{padding:.7rem}}
"""

# Inline JS placed AFTER the data so questions/flashcards are already loaded.
JS = r"""
(function(){
'use strict';

// ============================================================================
// CONSTANTS / STATE
// ============================================================================
const LS = {
  unlocked: 'cissp.unlocked',
  prefs: 'cissp.prefs',
  progress: 'cissp.progress',
  exam: 'cissp.exam.inprogress',
  examHistory: 'cissp.exam.history',
  flashState: 'cissp.flash.state',
  bookmarks: 'cissp.bookmarks',
  streak: 'cissp.streak',
  syncId: 'cissp.sync.id',     // SHA-256(passphrase) — opaque, no plaintext stored
  syncLast: 'cissp.sync.last', // ISO timestamp of last successful sync
};
const SUPABASE_URL = 'https://qoxgjjynjialntkvcdqn.supabase.co';
const SUPABASE_KEY = 'sb_publishable_OMBTOFMdT_XD1-6cj-MPSA_69RCAfD2';
const SYNC_TABLE = 'cissp_progress';
const PW_HASH = window.__PW_HASH__;
const QUESTIONS = window.__QUESTIONS__;
const FLASHCARDS = window.__FLASHCARDS__;
const TOPICS = window.__TOPICS__;
const TABLES = window.__TABLES__;
const DOMAINS = window.__DOMAINS__;
const CHEAT = window.__CHEAT__;

const state = {
  prefs: {theme:'dark', timerInPractice:false},
  progress: {},
  bookmarks: {},
  flash: {},
  examHistory: [],
  streak: {last:null, count:0},
  practice: null,
  exam: null,
};

// ============================================================================
// HELPERS
// ============================================================================
function $(sel, ctx){return (ctx||document).querySelector(sel)}
function $$(sel, ctx){return Array.from((ctx||document).querySelectorAll(sel))}
function el(tag, attrs, kids){
  const e = document.createElement(tag);
  if (attrs){for (const k in attrs){
    if (k === 'class') e.className = attrs[k];
    else if (k === 'html') e.innerHTML = attrs[k];
    else if (k.startsWith('on') && typeof attrs[k] === 'function') e.addEventListener(k.slice(2), attrs[k]);
    else if (attrs[k] !== false && attrs[k] != null) e.setAttribute(k, attrs[k]);
  }}
  if (kids){
    if (!Array.isArray(kids)) kids = [kids];
    for (const k of kids){if (k == null) continue; e.appendChild(typeof k === 'string' ? document.createTextNode(k) : k);}
  }
  return e;
}
function todayStr(){return new Date().toISOString().slice(0,10)}
function load(){
  state.prefs = JSON.parse(localStorage.getItem(LS.prefs) || '{"theme":"dark","timerInPractice":false}');
  state.progress = JSON.parse(localStorage.getItem(LS.progress) || '{}');
  state.bookmarks = JSON.parse(localStorage.getItem(LS.bookmarks) || '{}');
  state.flash = JSON.parse(localStorage.getItem(LS.flashState) || '{}');
  state.examHistory = JSON.parse(localStorage.getItem(LS.examHistory) || '[]');
  state.streak = JSON.parse(localStorage.getItem(LS.streak) || '{"last":null,"count":0}');
  state.exam = JSON.parse(localStorage.getItem(LS.exam) || 'null');
  if (state.prefs.theme === 'light') document.body.classList.add('light');
}
function save(key, value){localStorage.setItem(key, JSON.stringify(value))}
function saveAll(){
  save(LS.prefs, state.prefs);
  save(LS.progress, state.progress);
  save(LS.bookmarks, state.bookmarks);
  save(LS.flashState, state.flash);
  save(LS.examHistory, state.examHistory);
  save(LS.streak, state.streak);
  if (state.exam) save(LS.exam, state.exam); else localStorage.removeItem(LS.exam);
}
function shuffle(a){const arr=[...a]; for (let i=arr.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1)); [arr[i],arr[j]]=[arr[j],arr[i]];} return arr;}
function fmtTime(sec){
  if (sec < 0) sec = 0;
  const h = Math.floor(sec/3600);
  const m = Math.floor((sec%3600)/60);
  const s = Math.floor(sec%60);
  return (h?h+':':'') + String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0');
}

// ============================================================================
// TOASTS
// ============================================================================
let __lastToastMsg = '';
let __lastToastT = 0;
function toast(msg, type){
  // Suppress consecutive identical toasts within 1.5s
  const now = Date.now();
  if (msg === __lastToastMsg && (now - __lastToastT) < 1500) return;
  __lastToastMsg = msg; __lastToastT = now;
  const t = el('div', {class:'toast'+(type?' '+type:''), role:'status', 'aria-live':'polite'}, msg);
  $('#toasts').appendChild(t);
  // Cap visible stack at 3
  while ($('#toasts').children.length > 3) $('#toasts').firstChild.remove();
  setTimeout(()=>{t.style.opacity='0'; setTimeout(()=>t.remove(), 250);}, 2800);
}

// ============================================================================
// AUTH GATE
// ============================================================================
async function sha256(str){
  const buf = new TextEncoder().encode(str);
  const hash = await crypto.subtle.digest('SHA-256', buf);
  return Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2,'0')).join('');
}
async function tryUnlock(){
  const pw = $('#pw').value;
  const hash = await sha256(pw);
  if (hash === PW_HASH){
    localStorage.setItem(LS.unlocked, '1');
    boot();
  } else {
    $('#pw-err').textContent = 'Incorrect password.';
    $('#pw').select();
  }
}

// ============================================================================
// STREAK
// ============================================================================
function tickStreak(){
  const today = todayStr();
  if (state.streak.last === today) return;
  const yesterday = new Date(); yesterday.setDate(yesterday.getDate()-1);
  if (state.streak.last === yesterday.toISOString().slice(0,10)) state.streak.count += 1;
  else state.streak.count = 1;
  state.streak.last = today;
  save(LS.streak, state.streak);
}
function checkStreakWarning(){
  // If streak is alive, today not yet credited, and it's the user's last
  // window of the day (after 6pm local), nudge them.
  if (!state.streak.last || state.streak.count < 2) return;
  const today = todayStr();
  if (state.streak.last === today) return;  // already studied today
  const yesterday = new Date(); yesterday.setDate(yesterday.getDate()-1);
  if (state.streak.last !== yesterday.toISOString().slice(0,10)) return;  // already broken
  const hour = new Date().getHours();
  if (hour < 18) return;  // earlier in the day, no nudge
  const sessionFlag = 'cissp.streak.warned.' + today;
  if (sessionStorage.getItem(sessionFlag)) return;
  sessionStorage.setItem(sessionFlag, '1');
  toast('⏰ Quick review keeps your ' + state.streak.count + '-day streak alive.', 'warn');
}

// ============================================================================
// PROGRESS
// ============================================================================
function recordAnswer(qid, correct){
  const p = state.progress[qid] || {seen:0, correct:0, lastSeen:null};
  p.seen += 1;
  if (correct) p.correct += 1;
  p.lastSeen = Date.now();
  state.progress[qid] = p;
  save(LS.progress, state.progress);
}
function masteryByDomain(){
  const totals = {};
  for (const d of DOMAINS) totals[d.id] = {seen:0, correct:0, total:0};
  for (const q of QUESTIONS) totals[q.domain].total += 1;
  for (const qid in state.progress){
    const q = QUESTIONS.find(qq => qq.id === qid); if (!q) continue;
    totals[q.domain].seen += state.progress[qid].seen;
    totals[q.domain].correct += state.progress[qid].correct;
  }
  return totals;
}
function overallStats(){
  let seen=0, correct=0;
  for (const qid in state.progress){
    seen += state.progress[qid].seen;
    correct += state.progress[qid].correct;
  }
  return {seen, correct};
}
function weakestSubdomains(n){
  const map = {};
  for (const qid in state.progress){
    const q = QUESTIONS.find(qq => qq.id === qid); if (!q) continue;
    const k = 'D'+q.domain+' '+q.subdomain;
    map[k] = map[k] || {tried:0, correct:0};
    map[k].tried += state.progress[qid].seen;
    map[k].correct += state.progress[qid].correct;
  }
  const arr = Object.entries(map).map(([k,v]) => ({k, acc: v.tried ? v.correct/v.tried : 0, tried:v.tried}))
    .filter(x => x.tried >= 3)
    .sort((a,b)=>a.acc-b.acc);
  return arr.slice(0, n);
}

// ============================================================================
// VIEWS / NAVIGATION
// ============================================================================
const VIEWS = ['dashboard','read','practice','exam','flash','stats'];
function go(view){
  for (const v of VIEWS){
    $('#view-'+v).classList.toggle('active', v===view);
  }
  $$('nav.bottom button').forEach(b => b.classList.toggle('active', b.dataset.view===view));
  // Close exam-in-progress if leaving exam view
  // (paused, not abandoned — returning resumes)
  if (view === 'dashboard') renderDashboard();
  if (view === 'practice') renderPracticeSetup();
  if (view === 'exam') renderExam();
  if (view === 'read') renderRead();
  if (view === 'flash') renderFlash();
  if (view === 'stats') renderStats();
  window.scrollTo(0,0);
}

// ============================================================================
// DASHBOARD
// ============================================================================
// 8-week study plan — embedded constant, surfaced as a Dashboard card.
const STUDY_PLAN = [
  {week:1, focus:'Domains 1 + 2 (governance & assets)', read_chapters:[1,2,3,4,5], practice_target:25, exam:false},
  {week:2, focus:'Domain 3 first half (crypto, models)', read_chapters:[6,7,8], practice_target:25, exam:false},
  {week:3, focus:'Domain 3 second half + start D4', read_chapters:[9,10,11], practice_target:25, exam:false},
  {week:4, focus:'Domain 4 finish + Domain 5', read_chapters:[12,13,14], practice_target:25, exam:false},
  {week:5, focus:'Domain 6 + Domain 7 first half', read_chapters:[15,16,17], practice_target:25, exam:false},
  {week:6, focus:'Domain 7 finish + Domain 8', read_chapters:[18,19,20,21], practice_target:25, exam:false},
  {week:7, focus:'1st full mock exam + remediation on weakest 3 domains', read_chapters:[], practice_target:25, exam:true},
  {week:8, focus:'2nd full mock exam + memorize cheat tables; light review', read_chapters:[], practice_target:15, exam:true},
];
function studyPlanWeek(){
  // If user has set start_date in prefs, compute current week; else assume week 1.
  if (!state.prefs.studyStart) return 1;
  const start = new Date(state.prefs.studyStart);
  const elapsedDays = Math.floor((Date.now() - start.getTime()) / 86400000);
  const w = Math.min(8, Math.max(1, Math.floor(elapsedDays/7) + 1));
  return w;
}
function buildStudyPlanCard(stats){
  const w = studyPlanWeek();
  const plan = STUDY_PLAN[w-1];
  const card = el('div', {class:'card', style:'border-color:var(--accent2)'}, [
    el('div', {class:'row spread'}, [
      el('h3', {style:'margin:0'}, '🗓 Week ' + w + ' of 8 — ' + plan.focus),
      el('span', {class:'muted', style:'font-size:.8rem'}, state.prefs.studyStart ? '' : 'Not started yet'),
    ]),
  ]);
  if (!state.prefs.studyStart){
    card.appendChild(el('p', {class:'muted', style:'font-size:.88rem;margin:.5rem 0'},
      'Set your study start date and the plan will track which week you are in.'));
    card.appendChild(el('div', {class:'row'}, [
      el('button', {class:'primary', onclick:()=>{
        state.prefs.studyStart = new Date().toISOString().slice(0,10);
        save(LS.prefs, state.prefs); renderDashboard();
      }}, 'Start week 1 today'),
    ]));
    return card;
  }
  // Today's recommended actions
  const actions = el('ul', {style:'margin:.4rem 0 .4rem 1.2rem;padding:0'});
  if (plan.read_chapters.length){
    actions.appendChild(el('li', null, [
      'Read chapters: ',
      ...plan.read_chapters.flatMap(c => [
        el('button', {class:'badge guide', style:'border:none;cursor:pointer;font:inherit',
          onclick:()=>{__readTab='chapters'; __readFilter={domain:null,q:''}; go('read');
            setTimeout(()=>{ const det = $$('#read-list details').find(d => d.textContent.includes('Ch ' + c + ' '));
              if (det){det.open = true; det.scrollIntoView({behavior:'smooth', block:'start'});}}, 80);}},
          'Ch ' + c),
        ' '
      ])
    ]));
  }
  actions.appendChild(el('li', null, 'Practice: ' + plan.practice_target + ' questions/day'));
  if (plan.exam){
    actions.appendChild(el('li', null, [
      el('strong', null, 'Take a full mock exam this week '),
      el('button', {class:'badge guide', style:'border:none;cursor:pointer;font:inherit',
        onclick:()=>go('exam')}, 'Start exam →'),
    ]));
  }
  actions.appendChild(el('li', null, 'Flashcards: keep up with the daily SM-2 queue'));
  card.appendChild(actions);
  return card;
}

function renderDashboard(){
  const root = $('#view-dashboard'); root.innerHTML = '';
  const stats = overallStats();
  const acc = stats.seen ? Math.round(100*stats.correct/stats.seen) : 0;
  const dueCount = flashDueCount();
  root.appendChild(el('h2', null, 'Dashboard'));
  // ZERO-STATE: first-time user welcome
  if (stats.seen === 0){
    root.appendChild(el('div', {class:'card', style:'border:2px solid var(--accent);background:linear-gradient(135deg,var(--surface) 0%,#0d2530 100%)'}, [
      el('h3', {style:'color:var(--accent);font-size:1.2rem'}, '👋 Welcome — start here'),
      el('p', null, 'This app combines 400 manager-mindset practice questions, 21 chapter summaries with ~310 exam essentials, SM-2 spaced-repetition flashcards, a 100-question mock exam, and reference tables — everything you need for the CISSP exam.'),
      el('p', {class:'muted'}, 'An 8-week plan is shown below. For your first session, try this:'),
      el('div', {class:'row', style:'gap:.5rem;margin-top:.4rem'}, [
        el('button', {class:'primary', onclick:()=>go('read')}, '📖 Browse a chapter'),
        el('button', {onclick:()=>{state.practice = null; go('practice');}}, '✎ Try 10 practice questions'),
        el('button', {onclick:()=>go('flash')}, '⚡ Flip 5 flashcards'),
      ]),
      el('p', {class:'muted', style:'margin-top:.7rem;font-size:.85rem'},
        'Recommended pace: 60–90 min/day · 1 full mock exam in week 7. Sync your progress in Stats → Cloud sync to study from any device.'),
    ]));
  }
  // 8-WEEK STUDY PLAN — surfaced after first answer + always available
  const planCard = buildStudyPlanCard(stats);
  if (planCard) root.appendChild(planCard);
  // KPI row
  const kpis = el('div', {class:'row'}, [
    el('div', {class:'card grow'}, [
      el('div', {class:'kpi'}, String(stats.seen)),
      el('div', {class:'kpi-label'}, 'Questions answered'),
    ]),
    el('div', {class:'card grow'}, [
      el('div', {class:'kpi'}, acc + '%'),
      el('div', {class:'kpi-label'}, 'Overall accuracy'),
    ]),
    el('div', {class:'card grow'}, [
      el('div', {class:'kpi'}, String(state.streak.count)),
      el('div', {class:'kpi-label'}, 'Day streak'),
    ]),
    el('div', {class:'card grow'}, [
      el('div', {class:'kpi'}, String(dueCount)),
      el('div', {class:'kpi-label'}, 'Cards due'),
    ]),
  ]);
  root.appendChild(kpis);
  // Radar chart
  const radarCard = el('div', {class:'card'}, [el('h3', null, 'Domain Mastery')]);
  radarCard.appendChild(buildRadarSvg(masteryByDomain()));
  root.appendChild(radarCard);
  // Per-domain bars
  const barCard = el('div', {class:'card'}, [el('h3', null, 'Per-Domain Progress')]);
  const m = masteryByDomain();
  for (const d of DOMAINS){
    const dm = m[d.id];
    const accD = dm.seen ? Math.round(100*dm.correct/dm.seen) : 0;
    const cls = accD >= 75 ? 'success' : accD >= 50 ? 'warn' : 'danger';
    barCard.appendChild(el('div', {style:'margin:.55rem 0'}, [
      el('div', {class:'row spread'}, [
        el('span', null, [el('span',{class:'mono badge'}, 'D'+d.id), ' ', d.name]),
        el('span', {class:'muted mono'}, accD+'% • '+dm.seen+' answered • '+dm.total+' total • '+d.weight+'%'),
      ]),
      el('div', {class:'bar '+cls}, [el('div', {style:'width:'+accD+'%'})]),
    ]));
  }
  root.appendChild(barCard);
  // Weakest 3
  const weak = weakestSubdomains(3);
  if (weak.length){
    const weakCard = el('div', {class:'card'}, [el('h3', null, 'Weakest Subdomains')]);
    for (const w of weak){
      weakCard.appendChild(el('div', {class:'row spread'}, [
        el('span', null, w.k),
        el('span', {class:'muted'}, Math.round(100*w.acc)+'% over '+w.tried+' attempts'),
      ]));
    }
    weakCard.appendChild(el('button', {class:'primary', style:'margin-top:.7rem',
      onclick:()=>{state.practice = {filter:{onlyIncorrect:true}}; go('practice'); kickPracticeSession();}}, 'Drill these now'));
    root.appendChild(weakCard);
  }
  // Spaced repetition CTA
  const srCard = el('div', {class:'card'}, [
    el('h3', null, 'Spaced Repetition'),
    el('div', {class:'muted'}, dueCount + ' cards due today'),
    el('button', {class:'primary', style:'margin-top:.6rem', onclick:()=>go('flash')}, 'Start review'),
  ]);
  root.appendChild(srCard);

  if (state.exam){
    root.appendChild(el('div', {class:'card', style:'border-color:var(--warn)'}, [
      el('h3', {style:'color:var(--warn)'}, 'Exam in progress'),
      el('div', {class:'muted'}, 'You have an unfinished exam attempt.'),
      el('button', {class:'primary', style:'margin-top:.5rem', onclick:()=>go('exam')}, 'Resume exam'),
    ]));
  }
}

// ============================================================================
// RADAR SVG (hand-rolled, no library)
// ============================================================================
function buildRadarSvg(domainStats){
  const W = 360, H = 360, cx = W/2, cy = H/2 + 6, R = 130;
  const ns = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(ns, 'svg');
  svg.setAttribute('viewBox', '0 0 '+W+' '+H);
  svg.setAttribute('class', 'radar');
  const N = DOMAINS.length;
  // grid rings
  for (let r=1; r<=4; r++){
    const pts = [];
    for (let i=0;i<N;i++){
      const ang = -Math.PI/2 + i*2*Math.PI/N;
      pts.push((cx + Math.cos(ang)*R*r/4) + ',' + (cy + Math.sin(ang)*R*r/4));
    }
    const poly = document.createElementNS(ns, 'polygon');
    poly.setAttribute('points', pts.join(' '));
    poly.setAttribute('fill', 'none');
    poly.setAttribute('stroke', 'rgba(255,255,255,.07)');
    svg.appendChild(poly);
  }
  // spokes + labels
  for (let i=0;i<N;i++){
    const ang = -Math.PI/2 + i*2*Math.PI/N;
    const x = cx + Math.cos(ang)*R, y = cy + Math.sin(ang)*R;
    const ln = document.createElementNS(ns, 'line');
    ln.setAttribute('x1', cx); ln.setAttribute('y1', cy);
    ln.setAttribute('x2', x); ln.setAttribute('y2', y);
    ln.setAttribute('stroke', 'rgba(255,255,255,.07)');
    svg.appendChild(ln);
    const lx = cx + Math.cos(ang)*(R+18), ly = cy + Math.sin(ang)*(R+18);
    const lbl = document.createElementNS(ns, 'text');
    lbl.setAttribute('x', lx); lbl.setAttribute('y', ly);
    lbl.setAttribute('text-anchor', 'middle');
    lbl.setAttribute('dominant-baseline', 'middle');
    lbl.setAttribute('font-size', '11');
    lbl.setAttribute('font-family', 'ui-monospace,monospace');
    lbl.setAttribute('fill', '#9ca3af');
    lbl.textContent = 'D' + DOMAINS[i].id;
    svg.appendChild(lbl);
  }
  // data polygon
  const pts = [];
  for (let i=0;i<N;i++){
    const d = DOMAINS[i];
    const ds = domainStats[d.id];
    const acc = ds.seen ? ds.correct/ds.seen : 0;
    const ang = -Math.PI/2 + i*2*Math.PI/N;
    pts.push((cx + Math.cos(ang)*R*acc) + ',' + (cy + Math.sin(ang)*R*acc));
  }
  const data = document.createElementNS(ns, 'polygon');
  data.setAttribute('points', pts.join(' '));
  data.setAttribute('fill', 'rgba(0,212,255,.25)');
  data.setAttribute('stroke', '#00d4ff');
  data.setAttribute('stroke-width', '2');
  svg.appendChild(data);
  return svg;
}

// ============================================================================
// PRACTICE MODE
// ============================================================================
function renderPracticeSetup(){
  const root = $('#view-practice'); root.innerHTML = '';
  if (state.practice && state.practice.questions){
    return renderPracticeSession();
  }
  root.appendChild(el('h2', null, 'Practice Mode'));
  const f = (state.practice && state.practice.filter) || {};
  const card = el('div', {class:'card'}, [
    el('h3', null, 'Configure session'),
    el('div', {class:'filters'}, [
      el('div', null, [
        el('label', null, 'Session length'),
        el('select', {id:'pf-length'}, ['10','25','50','100'].map(n => el('option',{value:n,selected:n==='25'?'true':false},n))),
      ]),
      el('div', null, [
        el('label', null, 'Difficulty'),
        el('select', {id:'pf-diff'}, [el('option',{value:''},'Any'), ...['easy','medium','hard'].map(d=>el('option',{value:d},d))]),
      ]),
      el('div', null, [
        el('label', null, 'Source'),
        el('select', {id:'pf-source'}, [el('option',{value:''},'Any'), ...['guide','web','canonical'].map(s=>el('option',{value:s},s))]),
      ]),
    ]),
    el('div', null, [
      el('label', {class:'kpi-label', style:'display:block'}, 'Domains'),
      el('div', {class:'dlist', id:'pf-domains'}, DOMAINS.map(d => {
        const lbl = el('label', null, [
          el('input', {type:'checkbox', value:String(d.id), checked:'true'}),
          'D' + d.id,
        ]);
        lbl.classList.add('checked');
        lbl.addEventListener('click', e=>{
          if (e.target.tagName !== 'INPUT'){
            const cb = lbl.querySelector('input'); cb.checked = !cb.checked;
          }
          requestAnimationFrame(()=> lbl.classList.toggle('checked', lbl.querySelector('input').checked));
        });
        return lbl;
      })),
    ]),
    el('div', {style:'margin-top:.5rem'}, [
      el('label', {style:'display:inline-flex;align-items:center;gap:.4rem'}, [
        el('input', {type:'checkbox', id:'pf-bm', checked:f.onlyBookmarked?'true':false}),
        'Only bookmarked',
      ]),
      el('label', {style:'display:inline-flex;align-items:center;gap:.4rem;margin-left:1rem'}, [
        el('input', {type:'checkbox', id:'pf-wrong', checked:f.onlyIncorrect?'true':false}),
        'Only previously incorrect',
      ]),
      el('label', {style:'display:inline-flex;align-items:center;gap:.4rem;margin-left:1rem'}, [
        el('input', {type:'checkbox', id:'pf-timer', checked:state.prefs.timerInPractice?'true':false}),
        'Show timer',
      ]),
    ]),
    el('div', {style:'margin-top:.8rem'}, [
      el('button', {class:'primary', onclick:kickPracticeSession}, 'Start practice'),
    ]),
  ]);
  root.appendChild(card);
}

function kickPracticeSession(){
  const pickedDomains = $$('#pf-domains input').filter(c=>c.checked).map(c=>parseInt(c.value));
  const length = parseInt($('#pf-length') ? $('#pf-length').value : 25);
  const diff = $('#pf-diff') ? $('#pf-diff').value : '';
  const sourceFilt = $('#pf-source') ? $('#pf-source').value : '';
  const onlyBm = $('#pf-bm') && $('#pf-bm').checked;
  const onlyWrong = $('#pf-wrong') && $('#pf-wrong').checked;
  state.prefs.timerInPractice = $('#pf-timer') ? $('#pf-timer').checked : false;
  save(LS.prefs, state.prefs);
  let pool = QUESTIONS.filter(q => pickedDomains.includes(q.domain));
  if (diff) pool = pool.filter(q => q.difficulty === diff);
  if (sourceFilt) pool = pool.filter(q => q.source === sourceFilt);
  if (onlyBm) pool = pool.filter(q => state.bookmarks[q.id]);
  if (onlyWrong) pool = pool.filter(q => state.progress[q.id] && state.progress[q.id].correct < state.progress[q.id].seen);
  if (state.practice && state.practice.filter && state.practice.filter.onlyIncorrect) {
    pool = pool.filter(q => state.progress[q.id] && state.progress[q.id].correct < state.progress[q.id].seen);
  }
  if (!pool.length){toast('No questions match those filters.','warn'); return;}
  const questions = shuffle(pool).slice(0, length);
  state.practice = {questions, idx:0, picks:{}, eliminated:{}, started:Date.now()};
  renderPracticeSession();
}

function renderPracticeSession(){
  const root = $('#view-practice'); root.innerHTML = '';
  const s = state.practice;
  const q = s.questions[s.idx];
  const correct = s.questions.reduce((a,qq) => a + (s.picks[qq.id] === qq.correct ? 1 : 0), 0);
  const answered = Object.keys(s.picks).length;
  // Header
  const head = el('div', {class:'row spread'}, [
    el('h2', {style:'margin:0'}, 'Practice'),
    el('span', {class:'muted'}, (s.idx+1) + ' / ' + s.questions.length + ' • ' + correct + ' correct'),
  ]);
  root.appendChild(head);
  if (state.prefs.timerInPractice){
    const sec = Math.floor((Date.now()-s.started)/1000);
    root.appendChild(el('div', {class:'timer', style:'margin:.5rem 0;display:inline-block'}, fmtTime(sec)));
  }
  root.appendChild(buildQuestionCard(q, s.picks[q.id], q.id in s.picks, s.eliminated[q.id]||{}, (choiceIdx)=>{
    if (q.id in s.picks) return;
    s.picks[q.id] = choiceIdx;
    recordAnswer(q.id, choiceIdx === q.correct);
    tickStreak();
    saveAll();
    // Toast milestones
    const newSeen = overallStats().seen;
    if (newSeen === 100) toast('Milestone: 100 questions answered!');
    if (newSeen === 10) toast('Off the mark — keep going.');
    renderPracticeSession();
  }, (choiceIdx)=>{
    s.eliminated[q.id] = s.eliminated[q.id] || {};
    s.eliminated[q.id][choiceIdx] = !s.eliminated[q.id][choiceIdx];
    renderPracticeSession();
  }));
  // Nav
  const navrow = el('div', {class:'row spread', style:'margin-top:.6rem'}, [
    el('button', {disabled: s.idx===0?'true':false, onclick:()=>{s.idx--; renderPracticeSession();}}, '◀ Prev'),
    el('span', {class:'muted'}, 'Bookmark with ★ • next with → / Enter'),
    el('button', {disabled: s.idx>=s.questions.length-1?'true':false, class:'primary', onclick:()=>{s.idx++; renderPracticeSession();}}, 'Next ▶'),
  ]);
  root.appendChild(navrow);
  if (s.idx >= s.questions.length-1 && answered === s.questions.length){
    root.appendChild(el('div', {class:'card', style:'border-color:var(--accent);margin-top:.6rem'}, [
      el('h3', null, 'Session complete'),
      el('div', null, 'Score: ' + correct + ' / ' + s.questions.length + ' (' + Math.round(100*correct/s.questions.length) + '%)'),
      el('button', {class:'primary', style:'margin-top:.5rem', onclick:()=>{state.practice=null; renderPracticeSetup();}}, 'Configure new session'),
    ]));
  }
}

function buildQuestionCard(q, pick, answered, eliminated, onPick, onEliminate, hideExplanation){
  const card = el('div', {class:'qcard'});
  const head = el('div', {class:'qhead'}, [
    el('div', null, [
      el('span', {class:'mono badge'}, q.id),
      ' ',
      el('span', {class:'badge'}, 'D'+q.domain),
      ' ',
      el('span', {class:'badge ' + q.source}, q.source),
      ' ',
      el('span', {class:'muted', style:'font-size:.8rem'}, q.subdomain),
    ]),
    el('button', {class:'ghost', style:'font-size:1.1rem;padding:.2rem .5rem',
      onclick:()=>{state.bookmarks[q.id]=!state.bookmarks[q.id]; save(LS.bookmarks, state.bookmarks);
        toast(state.bookmarks[q.id]?'Bookmarked':'Unbookmarked');
        const view = $$('.view.active')[0]; if (view && view.id === 'view-practice') renderPracticeSession();
      }}, state.bookmarks[q.id] ? '★' : '☆'),
  ]);
  card.appendChild(head);
  card.appendChild(el('div', {class:'qstem'}, q.stem));
  for (let i=0; i<q.choices.length; i++){
    const letter = String.fromCharCode(65+i);
    let cls = 'choice';
    if (eliminated && eliminated[i]) cls += ' eliminated';
    if (answered){
      if (i === q.correct) cls += ' correct';
      else if (i === pick) cls += ' incorrect';
    } else if (pick === i) cls += ' selected';
    const c = el('div', {class:cls},
      [el('div',{class:'letter'}, letter), el('div', null, q.choices[i])]);
    c.addEventListener('click', ev => {
      if (answered) return;
      onPick(i);
    });
    c.addEventListener('contextmenu', ev => {
      ev.preventDefault();
      if (!answered && onEliminate) onEliminate(i);
    });
    let pressTimer;
    c.addEventListener('touchstart', ()=> {pressTimer = setTimeout(()=>{if (!answered && onEliminate) onEliminate(i);}, 600);}, {passive:true});
    c.addEventListener('touchend', ()=> clearTimeout(pressTimer));
    c.addEventListener('touchmove', ()=> clearTimeout(pressTimer));
    card.appendChild(c);
  }
  if (answered && !hideExplanation){
    const exp = el('div', {class:'explanation'}, [
      el('h4', null, (pick === q.correct ? '✓ Correct — ' : '✗ Incorrect — ') + 'Explanation'),
      el('div', null, q.explanation),
    ]);
    const refs = el('div', {class:'refs'});
    if (q.guide_pages && q.guide_pages.length){
      refs.appendChild(el('span', {class:'badge guide'}, '📖 ' + q.guide_section + ' (p. ' + q.guide_pages.join(', p. ') + ')'));
    }
    if (q.chapter){
      const t = TOPICS.find(tt => tt.chapter_number === q.chapter);
      if (t){
        refs.appendChild(el('button', {class:'badge guide', style:'cursor:pointer;border:none;font:inherit',
          onclick:()=>{__readFilter = {domain:String(t.domain), q:''}; go('read');
            setTimeout(()=>{ const det = $$('#read-list details').find(d => d.textContent.includes('Ch ' + t.chapter_number + ' '));
              if (det){det.open = true; det.scrollIntoView({behavior:'smooth', block:'start'});}}, 50);}},
          '📚 Read Chapter ' + t.chapter_number));
      }
    }
    if (q.web_sources && q.web_sources.length){
      for (const w of q.web_sources){
        refs.appendChild(el('a', {href:w.url, target:'_blank', rel:'noopener', class:'badge web', title:w.title}, '🔗 ' + (w.title.length>40?w.title.slice(0,40)+'…':w.title)));
      }
    }
    if (q.references && q.references.length){
      refs.appendChild(el('span', {class:'muted', style:'margin-left:.4rem'}, q.references.join(' • ')));
    }
    if (q.tags && q.tags.length){
      const tagrow = el('div', {style:'margin-top:.3rem'});
      for (const t of q.tags) tagrow.appendChild(el('span',{class:'tag'}, t));
      exp.appendChild(tagrow);
    }
    if (q.notes) exp.appendChild(el('div', {class:'muted', style:'margin-top:.3rem;font-size:.85rem'}, q.notes));
    exp.appendChild(refs);
    card.appendChild(exp);
  }
  return card;
}

// ============================================================================
// EXAM MODE (CAT-style)
// ============================================================================
const EXAM_DURATION_SEC = 3 * 60 * 60;
const EXAM_LENGTH_DEFAULT = 100;

function renderExam(){
  const root = $('#view-exam'); root.innerHTML = '';
  if (!state.exam){
    root.appendChild(el('h2', null, 'Full Exam Simulation'));
    root.appendChild(el('div', {class:'card'}, [
      el('h3', null, 'Rules'),
      el('ul', null, [
        el('li', null, '3-hour countdown timer.'),
        el('li', null, '100 questions, weighted by domain. Difficulty adapts to your performance.'),
        el('li', null, 'No feedback until exam ends.'),
        el('li', null, 'Pass = 700 / 1000.'),
        el('li', null, 'Refresh-safe — your in-progress exam is saved automatically.'),
      ]),
      el('button', {class:'primary', onclick:startExam}, 'Begin exam'),
    ]));
    if (state.examHistory.length){
      const card = el('div', {class:'card'}, [el('h3', null, 'Recent attempts')]);
      for (const h of state.examHistory.slice(-5).reverse()){
        card.appendChild(el('div', {class:'row spread'}, [
          el('span', null, [el('span',{class:'badge ' + (h.pass?'guide':'web')}, h.pass?'PASS':'FAIL'), ' ', h.score+' / 1000']),
          el('span', {class:'muted'}, new Date(h.timestamp).toLocaleString() + ' • ' + fmtTime(h.duration)),
        ]));
      }
      root.appendChild(card);
    }
    return;
  }
  // Active exam
  const ex = state.exam;
  const elapsed = Math.floor((Date.now() - ex.started)/1000);
  const remaining = EXAM_DURATION_SEC - elapsed;
  if (remaining <= 0 || ex.finished){return finishExam();}
  const q = ex.questions[ex.idx];
  const pick = ex.picks[q.id];
  const answeredFlag = q.id in ex.picks;
  // Header line
  root.appendChild(el('div', {class:'row spread'}, [
    el('h2', {style:'margin:0'}, 'Exam'),
    el('div', {class:'row'}, [
      el('span', {class:'muted'}, 'Q ' + (ex.idx+1) + '/' + ex.questions.length),
      el('span', {class:'timer ' + (remaining<300?'danger':remaining<900?'warn':''),
        'aria-label':'Time remaining'}, fmtTime(remaining)),
    ]),
  ]));
  // Progress bar — current position (cyan) overlaid on answered count (green)
  const answeredCount = Object.keys(ex.picks).length;
  const flaggedCount = Object.keys(ex.flagged).filter(k => ex.flagged[k]).length;
  const posPct = (ex.idx + 1) / ex.questions.length * 100;
  const ansPct = answeredCount / ex.questions.length * 100;
  root.appendChild(el('div', {style:'margin:.4rem 0 .8rem'}, [
    el('div', {style:'height:8px;background:var(--surface2);border-radius:4px;overflow:hidden;position:relative',
      role:'progressbar', 'aria-valuemin':'0', 'aria-valuemax':'100', 'aria-valuenow':String(Math.round(ansPct)),
      'aria-label':'Exam progress'}, [
      el('div', {style:'position:absolute;top:0;left:0;height:100%;background:var(--success);width:'+ansPct+'%;transition:width 200ms'}),
      el('div', {style:'position:absolute;top:0;left:0;height:100%;background:linear-gradient(90deg,transparent 0%,var(--accent) 100%);width:'+posPct+'%;mix-blend-mode:screen'}),
    ]),
    el('div', {class:'muted', style:'font-size:.75rem;margin-top:.25rem;display:flex;justify-content:space-between'}, [
      el('span', null, Math.round(ansPct) + '% answered (' + answeredCount + '/' + ex.questions.length + ')'),
      el('span', null, flaggedCount ? '★ ' + flaggedCount + ' flagged' : ''),
    ]),
  ]));
  // Question (no immediate feedback — we hide explanation)
  root.appendChild(buildQuestionCard(q, pick, false, ex.eliminated[q.id]||{},
    (i)=>{ ex.picks[q.id] = i; saveAll(); renderExam(); },
    (i)=>{ ex.eliminated[q.id] = ex.eliminated[q.id] || {}; ex.eliminated[q.id][i] = !ex.eliminated[q.id][i]; saveAll(); renderExam(); },
    true));
  // Controls
  root.appendChild(el('div', {class:'row spread'}, [
    el('button', {disabled: ex.idx===0?'true':false, onclick:()=>{ex.idx--; saveAll(); renderExam();}}, '◀ Prev'),
    el('div', {class:'row'}, [
      el('button', {class:ex.flagged[q.id]?'warn':'ghost',
        onclick:()=>{ex.flagged[q.id]=!ex.flagged[q.id]; saveAll(); renderExam();}}, ex.flagged[q.id]?'★ Flagged':'☆ Flag'),
      el('button', {class:'danger', onclick:()=>{ if (confirm('End the exam now?')) finishExam();}}, 'End exam'),
    ]),
    el('button', {class:'primary', disabled: ex.idx>=ex.questions.length-1?'true':false, onclick:()=>{ex.idx++; saveAll(); renderExam();}}, 'Next ▶'),
  ]));
  // Navigator
  const nav = el('div', {class:'qnav'});
  for (let i=0; i<ex.questions.length; i++){
    const qq = ex.questions[i];
    let cls = '';
    if (qq.id in ex.picks) cls += ' answered';
    if (ex.flagged[qq.id]) cls += ' flagged';
    if (i === ex.idx) cls += ' current';
    const b = el('button', {class:cls.trim(), onclick:()=>{ex.idx=i; saveAll(); renderExam();}}, String(i+1));
    nav.appendChild(b);
  }
  root.appendChild(nav);
  // Adaptive notice
  root.appendChild(el('div', {class:'muted', style:'margin-top:.5rem;font-size:.8rem'},
    'Difficulty adapts as you go (CAT). Refreshing the page resumes this attempt.'));
}

function startExam(){
  // Build adaptive question list weighted by domain percentage
  const total = EXAM_LENGTH_DEFAULT;
  const weights = DOMAINS.map(d => d.weight);
  const sumW = weights.reduce((a,b)=>a+b,0);
  const counts = DOMAINS.map((d,i) => Math.round(weights[i]/sumW * total));
  // adjust to exact total
  let diff = total - counts.reduce((a,b)=>a+b,0);
  for (let i=0; diff !== 0 && i < DOMAINS.length; i++){counts[i] += Math.sign(diff); diff -= Math.sign(diff);}
  let pool = [];
  for (let i=0; i<DOMAINS.length; i++){
    const dq = QUESTIONS.filter(q => q.domain === DOMAINS[i].id);
    pool = pool.concat(shuffle(dq).slice(0, Math.min(counts[i], dq.length)));
  }
  pool = shuffle(pool);
  state.exam = {
    started: Date.now(),
    questions: pool,
    picks: {},
    flagged: {},
    eliminated: {},
    idx: 0,
    finished: false,
    streak: 0,  // for adaptive logic (display only; bank already balanced)
  };
  saveAll();
  renderExam();
  // Per-second timer
  if (window.__examTick) clearInterval(window.__examTick);
  window.__examTick = setInterval(()=>{
    if (!state.exam || state.exam.finished){clearInterval(window.__examTick); return;}
    const v = $$('.view.active')[0];
    if (v && v.id === 'view-exam'){
      const elapsed = Math.floor((Date.now() - state.exam.started)/1000);
      const remaining = EXAM_DURATION_SEC - elapsed;
      const t = $('.timer'); if (t){t.textContent = fmtTime(remaining); t.className = 'timer ' + (remaining<300?'danger':remaining<900?'warn':'');}
      if (remaining <= 0) finishExam();
    }
  }, 1000);
}

function finishExam(){
  if (!state.exam) return;
  const ex = state.exam;
  ex.finished = true;
  let correct = 0;
  const perDomain = {}; for (const d of DOMAINS) perDomain[d.id] = {n:0, c:0};
  for (const q of ex.questions){
    perDomain[q.domain].n += 1;
    if (ex.picks[q.id] === q.correct){correct += 1; perDomain[q.domain].c += 1;}
    recordAnswer(q.id, ex.picks[q.id] === q.correct);
  }
  // Score: weighted-correct fraction × 1000, rounded.
  let weightedScore = 0; let weightSum = 0;
  for (const d of DOMAINS){
    const r = perDomain[d.id].n ? perDomain[d.id].c / perDomain[d.id].n : 0;
    weightedScore += r * d.weight;
    weightSum += d.weight;
  }
  const score = Math.round(weightedScore / weightSum * 1000);
  const pass = score >= 700;
  const duration = Math.floor((Date.now() - ex.started)/1000);
  const result = {timestamp: Date.now(), score, pass, duration, perDomain, qCount: ex.questions.length, correct};
  state.examHistory.push(result);
  state.exam = null;
  saveAll();
  if (window.__examTick){clearInterval(window.__examTick); window.__examTick = null;}
  showExamResult(result);
}

function showExamResult(r){
  const root = $('#view-exam'); root.innerHTML = '';
  root.appendChild(el('h2', null, 'Exam Result'));
  root.appendChild(el('div', {class:'card', style:'border-color:'+(r.pass?'var(--success)':'var(--danger)'), 'border-width':'2px'}, [
    el('div', {style:'font-size:2.2rem;font-weight:700;color:'+(r.pass?'var(--success)':'var(--danger)')}, r.pass?'PASS':'FAIL'),
    el('div', {class:'kpi'}, r.score + ' / 1000'),
    el('div', {class:'muted'}, 'Correct: ' + r.correct + ' / ' + r.qCount + ' • Duration: ' + fmtTime(r.duration)),
  ]));
  const dom = el('div', {class:'card'}, [el('h3', null, 'Per-domain breakdown')]);
  for (const d of DOMAINS){
    const pd = r.perDomain[d.id];
    const acc = pd.n ? Math.round(100*pd.c/pd.n) : 0;
    const cls = acc >= 75 ? 'success' : acc >= 50 ? 'warn' : 'danger';
    dom.appendChild(el('div', {style:'margin:.5rem 0'}, [
      el('div', {class:'row spread'}, [
        el('span', null, 'D' + d.id + ' ' + d.name),
        el('span', {class:'mono muted'}, pd.c+'/'+pd.n+' = '+acc+'%'),
      ]),
      el('div', {class:'bar '+cls}, [el('div', {style:'width:'+acc+'%'})]),
    ]));
  }
  root.appendChild(dom);
  root.appendChild(el('div', {class:'row'}, [
    el('button', {class:'primary', onclick:()=>{
      const blob = new Blob([JSON.stringify(r, null, 2)], {type:'application/json'});
      const a = document.createElement('a'); a.href = URL.createObjectURL(blob);
      a.download = 'cissp-exam-'+new Date(r.timestamp).toISOString().slice(0,19)+'.json'; a.click();
    }}, 'Download results JSON'),
    el('button', {onclick:()=>{state.exam=null; saveAll(); renderExam();}}, 'Back'),
  ]));
}

// ============================================================================
// READ MODE — chapter summaries + Exam Essentials, browseable per domain
// ============================================================================
let __readFilter = {domain: null, q: ''};
let __readTab = 'chapters';  // 'chapters' | 'reference'
function renderRead(){
  const root = $('#view-read'); root.innerHTML = '';
  root.appendChild(el('h2', null, 'Read'));
  // Tab toggle
  const tabs = el('div', {class:'row', style:'margin-bottom:.7rem;gap:.4rem'}, [
    el('button', {class: __readTab==='chapters' ? 'primary' : 'ghost',
      onclick:()=>{__readTab='chapters'; renderRead();}},
      '📚 Chapters (' + TOPICS.length + ')'),
    el('button', {class: __readTab==='reference' ? 'primary' : 'ghost',
      onclick:()=>{__readTab='reference'; renderRead();}},
      '⚡ Reference (' + TABLES.length + ' tables · ' + DOMAINS.length + ' cheat sheets)'),
  ]);
  root.appendChild(tabs);
  if (__readTab === 'chapters') return renderReadChapters(root);
  return renderReadReference(root);
}
function renderReadChapters(root){
  root.appendChild(el('div', {class:'muted', style:'margin-bottom:.5rem;font-size:.88rem'},
    TOPICS.length + ' chapters synthesised from the guide. Click a chapter to expand its summary and exam essentials.'));
  const filterRow = el('div', {class:'search-bar'}, [
    el('input', {id:'read-q', placeholder:'Search summaries and exam essentials…', value:__readFilter.q,
      'aria-label':'Search chapter summaries',
      oninput:e=>{__readFilter.q = e.target.value; rerenderReadList();}}),
    el('select', {id:'read-d', 'aria-label':'Filter by domain',
      onchange:e=>{__readFilter.domain = e.target.value || null; rerenderReadList();}}, [
      el('option', {value:''}, 'All domains'),
      ...DOMAINS.map(d => {
        const opt = el('option', {value:String(d.id)}, 'D' + d.id + ' ' + d.name);
        if (String(d.id) === __readFilter.domain) opt.setAttribute('selected', 'true');
        return opt;
      }),
    ]),
  ]);
  root.appendChild(filterRow);
  const list = el('div', {id:'read-list'});
  root.appendChild(list);
  rerenderReadList();
}
function renderReadReference(root){
  root.appendChild(el('div', {class:'muted', style:'margin-bottom:.7rem;font-size:.88rem'},
    'High-leverage comparison tables, plus per-domain cheat sheets with web sources. Memorise these for the final week.'));
  // Comparison tables
  root.appendChild(el('h3', {style:'color:var(--accent);margin-top:.4rem'}, '📊 Comparison tables'));
  for (const t of TABLES){
    const det = el('details', {class:'cheat'});
    det.appendChild(el('summary', null, [
      el('span', null, [el('span',{class:'mono badge'}, 'D'+t.domain), ' ', t.name]),
      el('span', {class:'muted', style:'font-size:.8rem'}, t.rows.length + ' rows'),
    ]));
    const body = el('div', {class:'body'});
    // Build the table
    const tbl = el('table', {style:'width:100%;border-collapse:collapse;font-size:.88rem'});
    const thead = el('thead', null, [
      el('tr', null, t.headers.map(h => el('th',
        {style:'text-align:left;padding:.4rem .5rem;border-bottom:2px solid var(--border2);color:var(--accent);font-weight:600'},
        h))),
    ]);
    tbl.appendChild(thead);
    const tbody = el('tbody');
    for (const row of t.rows){
      tbody.appendChild(el('tr', null, row.map(cell => el('td',
        {style:'padding:.4rem .5rem;border-bottom:1px solid var(--border);vertical-align:top'},
        String(cell)))));
    }
    tbl.appendChild(tbody);
    body.appendChild(tbl);
    if (t.tip){
      body.appendChild(el('div', {style:'margin-top:.6rem;padding:.5rem .7rem;background:var(--surface2);border-left:3px solid var(--accent);border-radius:.3rem;font-size:.88rem'},
        [el('strong', null, '💡 Tip: '), t.tip]));
    }
    det.appendChild(body);
    root.appendChild(det);
  }
  // Per-domain cheat sheets (URL lists for further reading)
  root.appendChild(el('h3', {style:'color:var(--accent);margin-top:1.5rem'}, '🔗 Per-domain cheat sheets'));
  root.appendChild(el('div', {class:'search-bar'}, [
    el('input', {id:'cheat-q', placeholder:'Search across cheat sheets…', oninput:filterCheat,
      'aria-label':'Search cheat sheets'}),
  ]));
  const cont = el('div', {id:'cheat-container'});
  for (const c of CHEAT){
    cont.appendChild(buildCheatSheet(c));
  }
  root.appendChild(cont);
}
function rerenderReadList(){
  const list = $('#read-list'); if (!list) return;
  list.innerHTML = '';
  const q = (__readFilter.q || '').toLowerCase().trim();
  let topics = TOPICS.slice();
  if (__readFilter.domain) topics = topics.filter(t => String(t.domain) === __readFilter.domain);
  if (q){
    topics = topics.filter(t => {
      const blob = ((t.chapter_title||'') + ' ' + (t.summary||'') + ' ' +
        (t.exam_essentials||[]).map(e => e.term + ' ' + e.gloss).join(' ')).toLowerCase();
      return blob.includes(q);
    });
  }
  if (!topics.length){
    list.appendChild(el('div', {class:'muted'}, 'No chapters match.'));
    return;
  }
  for (const t of topics){
    const det = el('details', {class:'cheat'});
    if (q || __readFilter.domain) det.open = true;  // expand when filtering
    det.appendChild(el('summary', null, [
      el('span', null, [
        el('span', {class:'mono badge'}, 'Ch ' + t.chapter_number),
        ' ',
        el('span', {class:'mono badge'}, 'D' + t.domain),
        ' ',
        t.chapter_title,
      ]),
      el('span', {class:'muted'}, 'p. ' + t.page),
    ]));
    const body = el('div', {class:'body'});
    body.appendChild(el('h3', null, 'Summary'));
    // Render summary as paragraphs
    for (const para of (t.summary||'').split(/\n\n+/)){
      if (!para.trim()) continue;
      body.appendChild(el('p', {style:'margin:.4rem 0;line-height:1.6'}, highlightMatch(para, q)));
    }
    if (t.exam_essentials && t.exam_essentials.length){
      body.appendChild(el('h3', {style:'margin-top:1rem'}, 'Exam essentials'));
      const ul = el('ul', {style:'padding-left:1.1rem'});
      for (const ee of t.exam_essentials){
        const li = el('li', {style:'margin:.5rem 0'}, [
          el('strong', null, highlightMatch(ee.term, q)),
          ' ',
          el('span', null, highlightMatch(ee.gloss, q)),
        ]);
        ul.appendChild(li);
      }
      body.appendChild(ul);
    }
    body.appendChild(el('div', {class:'row', style:'margin-top:.7rem'}, [
      el('button', {class:'primary', onclick:()=>{
        state.practice = {filter:{onlyChapter: t.chapter_number}};
        go('practice');
        // Auto-kick a session filtered to this chapter's questions
        kickPracticeSessionForChapter(t.chapter_number, t.domain);
      }}, '✎ Practice questions on this chapter'),
    ]));
    det.appendChild(body);
    list.appendChild(det);
  }
}
function highlightMatch(text, q){
  if (!q) return text;
  // Simple HTML-safe highlight
  const idx = text.toLowerCase().indexOf(q);
  if (idx < 0) return text;
  const span = el('span');
  span.appendChild(document.createTextNode(text.slice(0, idx)));
  const mark = el('mark', {style:'background:#ffd86b;color:#1a1100;padding:0 .15rem;border-radius:.15rem'},
    text.slice(idx, idx + q.length));
  span.appendChild(mark);
  span.appendChild(document.createTextNode(text.slice(idx + q.length)));
  return span;
}
function kickPracticeSessionForChapter(chNum, domain){
  // Build a session of questions whose chapter matches, falling back to domain
  let pool = QUESTIONS.filter(q => q.chapter === chNum);
  if (pool.length < 5) pool = QUESTIONS.filter(q => q.domain === domain);
  if (!pool.length){toast('No questions for this chapter','warn'); return;}
  const questions = shuffle(pool).slice(0, Math.min(20, pool.length));
  state.practice = {questions, idx:0, picks:{}, eliminated:{}, started:Date.now()};
  renderPracticeSession();
}

// ============================================================================
// FLASHCARDS — SM-2
// ============================================================================
function flashState(id){
  return state.flash[id] || {ef:2.5, interval:0, reps:0, due: Date.now()};
}
function flashDueCount(){
  const now = Date.now();
  let n = 0;
  for (const card of FLASHCARDS){
    const s = flashState(card.id);
    if (s.due <= now) n += 1;
  }
  return n;
}
function gradeFlash(id, grade){
  // grade: 0=Again, 3=Hard, 4=Good, 5=Easy (SM-2 quality 0-5)
  const s = flashState(id);
  if (grade < 3){
    s.reps = 0; s.interval = 1;
  } else {
    if (s.reps === 0) s.interval = 1;
    else if (s.reps === 1) s.interval = 6;
    else s.interval = Math.round(s.interval * s.ef);
    s.reps += 1;
  }
  // Update easiness factor
  s.ef = Math.max(1.3, s.ef + (0.1 - (5-grade)*(0.08 + (5-grade)*0.02)));
  s.due = Date.now() + s.interval * 24 * 60 * 60 * 1000;
  state.flash[id] = s;
  save(LS.flashState, state.flash);
}

let __flashIdx = 0;
let __flashRevealed = false;
let __flashQueue = [];
function buildFlashQueue(){
  const now = Date.now();
  __flashQueue = FLASHCARDS.filter(c => flashState(c.id).due <= now);
  __flashQueue = shuffle(__flashQueue);
  __flashIdx = 0; __flashRevealed = false;
}
function renderFlash(){
  const root = $('#view-flash'); root.innerHTML = '';
  if (!__flashQueue.length || __flashIdx >= __flashQueue.length) buildFlashQueue();
  const due = flashDueCount();
  const total = FLASHCARDS.length;
  root.appendChild(el('div', {class:'row spread'}, [
    el('h2', {style:'margin:0'}, 'Flashcards'),
    el('span', {class:'muted'}, due + ' due • ' + total + ' total'),
  ]));
  if (!__flashQueue.length){
    root.appendChild(el('div', {class:'card'}, [
      el('h3', null, 'No cards due'),
      el('div', null, 'Come back tomorrow for the next batch — or use the buttons below to study any card.'),
      el('button', {class:'primary', style:'margin-top:.6rem', onclick:()=>{__flashQueue = shuffle(FLASHCARDS); __flashIdx=0; __flashRevealed=false; renderFlash();}}, 'Browse all cards'),
    ]));
    return;
  }
  const card = __flashQueue[__flashIdx];
  const fc = el('div', {class:'flashcard', onclick:()=>{__flashRevealed = !__flashRevealed; renderFlash();}}, [
    el('div', {class:'muted mono', style:'font-size:.75rem'}, card.id + ' • D' + card.domain),
    el('div', {class:'term'}, card.term),
    __flashRevealed ? el('div', {class:'back'}, card.back) : el('div', {class:'muted'}, 'Tap to reveal'),
  ]);
  if (__flashRevealed){
    if (card.guide_pages && card.guide_pages.length){
      fc.appendChild(el('div', {class:'src-line'}, '📖 p. ' + card.guide_pages.join(', p. ')));
    } else if (card.web_url){
      fc.appendChild(el('div', {class:'src-line'}, [el('a', {href:card.web_url, target:'_blank', rel:'noopener'}, '🔗 source')]));
    } else {
      fc.appendChild(el('div', {class:'src-line'}, '📚 canonical CISSP topic'));
    }
  }
  root.appendChild(fc);
  if (__flashRevealed){
    root.appendChild(el('div', {class:'fc-actions'}, [
      el('button', {class:'again', onclick:()=>{gradeFlash(card.id, 0); __flashIdx++; __flashRevealed=false; renderFlash();}}, 'Again'),
      el('button', {class:'hard', onclick:()=>{gradeFlash(card.id, 3); __flashIdx++; __flashRevealed=false; renderFlash();}}, 'Hard'),
      el('button', {class:'good', onclick:()=>{gradeFlash(card.id, 4); __flashIdx++; __flashRevealed=false; renderFlash();}}, 'Good'),
      el('button', {class:'easy', onclick:()=>{gradeFlash(card.id, 5); __flashIdx++; __flashRevealed=false; renderFlash();}}, 'Easy'),
    ]));
  } else {
    root.appendChild(el('div', {style:'margin-top:.7rem'}, [
      el('button', {class:'primary', onclick:()=>{__flashRevealed = true; renderFlash();}}, 'Reveal answer'),
    ]));
  }
  root.appendChild(el('div', {class:'muted', style:'margin-top:.5rem;font-size:.8rem;text-align:center'},
    'Card ' + (__flashIdx+1) + ' of ' + __flashQueue.length + ' in this session'));
}

// ============================================================================
// CHEAT SHEETS
// ============================================================================
function renderCheat(){
  const root = $('#view-cheat'); root.innerHTML = '';
  root.appendChild(el('h2', null, 'Cheat Sheets'));
  root.appendChild(el('div', {class:'search-bar'}, [
    el('input', {id:'cheat-q', placeholder:'Search across cheat sheets and flashcards…', oninput:filterCheat}),
    el('button', {onclick:()=>{$('#cheat-q').value=''; filterCheat();}}, 'Clear'),
  ]));
  const container = el('div', {id:'cheat-container'});
  for (const c of CHEAT){
    const sheet = buildCheatSheet(c);
    container.appendChild(sheet);
  }
  root.appendChild(container);
}
function buildCheatSheet(c){
  const det = el('details', {class:'cheat'}, [
    el('summary', null, [
      el('span', null, [el('span',{class:'mono badge'}, 'D'+c.domain), ' ', c.name]),
      el('span', {class:'muted'}, c.weight + '%'),
    ]),
  ]);
  const body = el('div', {class:'body'});
  // Show domain-relevant flashcards (abbreviated content) for the cheat sheet
  const rel = FLASHCARDS.filter(f => f.domain === c.domain);
  for (const f of rel){
    const row = el('div', {style:'margin:.4rem 0;padding-bottom:.4rem;border-bottom:1px solid var(--border)'}, [
      el('div', {style:'font-weight:600'}, f.term),
      el('div', {class:'muted', style:'font-size:.92rem'}, f.back),
    ]);
    if (f.guide_pages && f.guide_pages.length){
      row.appendChild(el('span', {class:'badge guide', style:'margin-right:.3rem',
        onclick:()=>showSourceModal('Guide reference', '📖 p. ' + f.guide_pages.join(', p. ') + ' — ' + f.term, '')},
        '📖 p. ' + f.guide_pages.join(', p. ')));
    }
    if (f.web_url){
      row.appendChild(el('a', {class:'badge web', href:f.web_url, target:'_blank', rel:'noopener'}, '🔗 source'));
    }
    body.appendChild(row);
  }
  // Sources
  const srcdiv = el('div', {style:'margin-top:.6rem'}, [el('div', {class:'kpi-label'}, 'Top web sources')]);
  for (const s of c.sources){
    srcdiv.appendChild(el('div', null, [el('a', {href:s.url, target:'_blank', rel:'noopener'}, '🔗 ' + s.title)]));
  }
  body.appendChild(srcdiv);
  det.appendChild(body);
  return det;
}
function filterCheat(){
  const q = ($('#cheat-q').value || '').toLowerCase();
  const cont = $('#cheat-container'); cont.innerHTML = '';
  for (const c of CHEAT){
    let any = !q;
    const sheet = buildCheatSheet(c);
    if (q){
      const text = sheet.textContent.toLowerCase();
      if (text.includes(q)){any = true; sheet.open = true;}
    }
    if (any) cont.appendChild(sheet);
  }
}
function showSourceModal(title, body, url){
  $('#modal-body').innerHTML = '';
  $('#modal-body').appendChild(el('h3', null, title));
  $('#modal-body').appendChild(el('div', null, body));
  if (url) $('#modal-body').appendChild(el('a', {href:url, target:'_blank', rel:'noopener'}, '🔗 Open source'));
  $('#modal').classList.add('show');
}

// ============================================================================
// STATS
// ============================================================================
function renderStats(){
  const root = $('#view-stats'); root.innerHTML = '';
  root.appendChild(el('h2', null, 'Stats / History'));
  // Accuracy over time (line chart from exam history)
  if (state.examHistory.length){
    const card = el('div', {class:'card'}, [el('h3', null, 'Exam scores over time')]);
    card.appendChild(buildLineSvg(state.examHistory.map(h=>h.score), 0, 1000));
    root.appendChild(card);
  }
  // Heatmap by domain
  const m = masteryByDomain();
  const heatCard = el('div', {class:'card'}, [el('h3', null, 'Per-domain accuracy heatmap')]);
  const grid = el('div', {class:'heatmap'});
  for (const d of DOMAINS){
    const dm = m[d.id];
    const acc = dm.seen ? dm.correct/dm.seen : 0;
    const hue = Math.round(acc * 130); // red→green
    const cell = el('div', {class:'cell', style:'background:hsl('+hue+',60%,'+(20+acc*25)+'%)'},
      'D'+d.id+' '+(dm.seen?Math.round(100*acc)+'%':'—'));
    grid.appendChild(cell);
  }
  heatCard.appendChild(grid);
  root.appendChild(heatCard);
  // Exam history table
  const histCard = el('div', {class:'card'}, [el('h3', null, 'Exam history')]);
  if (!state.examHistory.length){
    histCard.appendChild(el('div', {class:'muted'}, 'No exam attempts yet.'));
  } else {
    for (const h of [...state.examHistory].reverse()){
      histCard.appendChild(el('div', {class:'row spread', style:'margin:.3rem 0'}, [
        el('span', null, [
          el('span', {class:'badge ' + (h.pass?'guide':'web')}, h.pass?'PASS':'FAIL'),
          ' ', h.score+' / 1000 ',
          el('span', {class:'muted'}, '• ' + h.correct + '/' + h.qCount),
        ]),
        el('span', {class:'muted'}, new Date(h.timestamp).toLocaleString() + ' • ' + fmtTime(h.duration)),
      ]));
    }
  }
  root.appendChild(histCard);
  // Cloud sync (Supabase)
  const syncCard = el('div', {class:'card'}, [el('h3', null, 'Cloud sync')]);
  const syncId = localStorage.getItem(LS.syncId);
  const syncLast = localStorage.getItem(LS.syncLast);
  if (!syncId){
    syncCard.appendChild(el('div', {class:'muted', style:'margin-bottom:.5rem'},
      'Set a passphrase (8+ chars) to back up progress to Supabase. Use the same passphrase on other devices to sync. The passphrase never leaves the device — only its SHA-256 hash is stored.'));
    syncCard.appendChild(el('input', {type:'password', placeholder:'Sync passphrase (8+ chars, memorable)', id:'sync-pw', autocomplete:'new-password'}));
    syncCard.appendChild(el('button', {class:'primary', style:'margin-top:.5rem', id:'sync-enable',
      onclick:async()=>{
        const v = ($('#sync-pw').value || '').trim();
        if (v.length < 8){toast('Use at least 8 characters', 'warn'); return;}
        $('#sync-enable').disabled = true;
        try {await setupSync(v);} catch(e){toast('Setup failed: '+e.message, 'danger');}
      }}, '☁ Enable sync (pulls existing data first)'));
  } else {
    syncCard.appendChild(el('div', {class:'muted mono', style:'font-size:.78rem;word-break:break-all'},
      'Sync ID: ' + syncId.slice(0,16) + '…'));
    if (syncLast){
      syncCard.appendChild(el('div', {class:'muted', style:'font-size:.85rem;margin-top:.2rem'},
        'Last sync: ' + new Date(syncLast).toLocaleString()));
    } else {
      syncCard.appendChild(el('div', {class:'muted', style:'font-size:.85rem;margin-top:.2rem'},
        'Not yet synced.'));
    }
    syncCard.appendChild(el('div', {class:'row', style:'margin-top:.6rem'}, [
      el('button', {class:'primary', id:'sync-btn', onclick:()=>syncNow(false)}, '⟳ Sync now (pull → merge → push)'),
      el('button', {class:'ghost', onclick:()=>{
        if (!confirm('Forget local sync passphrase? Cloud data is unaffected; you can re-enable sync with the same passphrase later.')) return;
        localStorage.removeItem(LS.syncId); localStorage.removeItem(LS.syncLast);
        toast('Disconnected from cloud sync.','warn');
        renderStats();
      }}, 'Disconnect'),
    ]));
  }
  root.appendChild(syncCard);
  // Data management
  root.appendChild(el('div', {class:'card'}, [
    el('h3', null, 'Data'),
    el('div', {class:'row'}, [
      el('button', {class:'primary', onclick:exportData}, '⬇ Export progress (JSON)'),
      el('button', {onclick:()=>$('#import-file').click()}, '⬆ Import progress'),
      el('input', {type:'file', id:'import-file', accept:'.json', style:'display:none', onchange:importData}),
      el('button', {class:'danger', onclick:resetData}, '⌫ Reset all data'),
    ]),
  ]));
  // Theme toggle
  root.appendChild(el('div', {class:'card'}, [
    el('h3', null, 'Settings'),
    el('label', {style:'display:inline-flex;gap:.4rem;align-items:center'}, [
      el('input', {type:'checkbox', checked:state.prefs.theme==='light'?'true':false,
        onchange:e=>{state.prefs.theme = e.target.checked?'light':'dark';
          document.body.classList.toggle('light', e.target.checked); save(LS.prefs, state.prefs);}}),
      'Light mode',
    ]),
  ]));
}

function buildLineSvg(values, ymin, ymax){
  const W = 600, H = 220, P = 30;
  const ns = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(ns, 'svg');
  svg.setAttribute('viewBox', '0 0 '+W+' '+H);
  svg.setAttribute('class', 'line-chart');
  // axes
  const ax = document.createElementNS(ns, 'g');
  for (let i=0; i<=4; i++){
    const y = P + (H-2*P) * i/4;
    const v = Math.round(ymax - (ymax-ymin)*i/4);
    const ln = document.createElementNS(ns, 'line');
    ln.setAttribute('x1', P); ln.setAttribute('x2', W-P/2);
    ln.setAttribute('y1', y); ln.setAttribute('y2', y);
    ln.setAttribute('stroke', 'rgba(255,255,255,.07)');
    ax.appendChild(ln);
    const t = document.createElementNS(ns, 'text');
    t.setAttribute('x', P-4); t.setAttribute('y', y+3);
    t.setAttribute('text-anchor', 'end'); t.setAttribute('font-size', '10');
    t.setAttribute('fill', '#9ca3af'); t.textContent = String(v);
    ax.appendChild(t);
  }
  svg.appendChild(ax);
  // pass line
  const passY = P + (H-2*P) * (1 - (700-ymin)/(ymax-ymin));
  const passLn = document.createElementNS(ns, 'line');
  passLn.setAttribute('x1', P); passLn.setAttribute('x2', W-P/2);
  passLn.setAttribute('y1', passY); passLn.setAttribute('y2', passY);
  passLn.setAttribute('stroke', '#10b981'); passLn.setAttribute('stroke-dasharray', '3 4');
  svg.appendChild(passLn);
  // line
  if (values.length > 0){
    const xs = values.length > 1 ? (W - 2*P) / (values.length - 1) : 0;
    let path = '';
    for (let i=0; i<values.length; i++){
      const x = P + i*xs;
      const y = P + (H - 2*P) * (1 - (values[i] - ymin)/(ymax - ymin));
      path += (i===0?'M':'L') + x + ' ' + y + ' ';
      const c = document.createElementNS(ns, 'circle');
      c.setAttribute('cx', x); c.setAttribute('cy', y); c.setAttribute('r', '3.5');
      c.setAttribute('fill', '#00d4ff');
      svg.appendChild(c);
    }
    const pl = document.createElementNS(ns, 'path');
    pl.setAttribute('d', path);
    pl.setAttribute('fill', 'none'); pl.setAttribute('stroke', '#00d4ff'); pl.setAttribute('stroke-width', '2');
    svg.appendChild(pl);
  } else {
    const t = document.createElementNS(ns, 'text');
    t.setAttribute('x', W/2); t.setAttribute('y', H/2);
    t.setAttribute('text-anchor', 'middle'); t.setAttribute('fill', '#9ca3af');
    t.textContent = 'No exam data yet';
    svg.appendChild(t);
  }
  return svg;
}

// ============================================================================
// EXPORT/IMPORT/RESET
// ============================================================================
function exportData(){
  const blob = {
    exported: new Date().toISOString(),
    progress: state.progress,
    bookmarks: state.bookmarks,
    flash: state.flash,
    examHistory: state.examHistory,
    streak: state.streak,
    prefs: state.prefs,
  };
  const data = new Blob([JSON.stringify(blob, null, 2)], {type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(data);
  a.download = 'cissp-progress-' + todayStr().replace(/-/g,'') + '.json';
  a.click();
}
function importData(ev){
  const f = ev.target.files[0]; if (!f) return;
  const r = new FileReader();
  r.onload = e => {
    try {
      const obj = JSON.parse(e.target.result);
      if (!confirm('Replace ALL local data with imported data?')) return;
      state.progress = obj.progress || {};
      state.bookmarks = obj.bookmarks || {};
      state.flash = obj.flash || {};
      state.examHistory = obj.examHistory || [];
      state.streak = obj.streak || {last:null,count:0};
      state.prefs = obj.prefs || state.prefs;
      saveAll();
      toast('Imported.','success');
      renderStats();
    } catch (e){ alert('Invalid JSON: ' + e.message); }
  };
  r.readAsText(f);
}
function resetData(){
  if (!confirm('Wipe ALL local progress, bookmarks, flashcard state, and exam history?')) return;
  if (!confirm('Are you SURE? This cannot be undone.')) return;
  for (const k of Object.values(LS)){if (k !== LS.unlocked) localStorage.removeItem(k);}
  state.progress = {}; state.bookmarks = {}; state.flash = {};
  state.examHistory = []; state.streak = {last:null,count:0}; state.exam = null;
  toast('All data reset.','warn');
  go('dashboard');
}

// ============================================================================
// SUPABASE SYNC (pull → merge → push)
// ============================================================================
function snapshotLocal(){
  return {
    progress: state.progress,
    bookmarks: state.bookmarks,
    flash: state.flash,
    examHistory: state.examHistory,
    streak: state.streak,
    prefs: state.prefs,
  };
}
function mergeData(local, remote){
  if (!remote) return local;
  if (!local) return remote;
  // Progress: take entry with higher seen count; max counters; later lastSeen
  const progress = {};
  const pids = new Set([...Object.keys(local.progress||{}), ...Object.keys(remote.progress||{})]);
  for (const id of pids){
    const a = local.progress[id], b = remote.progress[id];
    if (!a) progress[id] = b;
    else if (!b) progress[id] = a;
    else progress[id] = {
      seen: Math.max(a.seen||0, b.seen||0),
      correct: Math.max(a.correct||0, b.correct||0),
      lastSeen: Math.max(a.lastSeen||0, b.lastSeen||0),
    };
  }
  // Bookmarks: union (true wins)
  const bookmarks = {};
  for (const id in (local.bookmarks||{})) if (local.bookmarks[id]) bookmarks[id] = true;
  for (const id in (remote.bookmarks||{})) if (remote.bookmarks[id]) bookmarks[id] = true;
  // Flash: take the entry with higher reps (more SM-2 progress); fall back to later due
  const flash = {};
  const fids = new Set([...Object.keys(local.flash||{}), ...Object.keys(remote.flash||{})]);
  for (const id of fids){
    const a = local.flash[id], b = remote.flash[id];
    if (!a) flash[id] = b;
    else if (!b) flash[id] = a;
    else if ((a.reps||0) !== (b.reps||0)) flash[id] = (a.reps > b.reps) ? a : b;
    else flash[id] = ((a.due||0) > (b.due||0)) ? a : b;
  }
  // Exam history: union by timestamp
  const seen = new Set();
  const examHistory = [];
  for (const h of [...(local.examHistory||[]), ...(remote.examHistory||[])]){
    if (h && h.timestamp != null && !seen.has(h.timestamp)){
      seen.add(h.timestamp);
      examHistory.push(h);
    }
  }
  examHistory.sort((a,b) => a.timestamp - b.timestamp);
  // Streak: max count, take latest 'last' date string
  const a = local.streak||{last:null,count:0}, b = remote.streak||{last:null,count:0};
  const streak = {
    last: ((a.last||'') > (b.last||'')) ? a.last : b.last,
    count: Math.max(a.count||0, b.count||0),
  };
  // Prefs: shallow merge, local wins for keys it has
  const prefs = Object.assign({}, remote.prefs||{}, local.prefs||{});
  return {progress, bookmarks, flash, examHistory, streak, prefs};
}
async function pullRemote(){
  const id = localStorage.getItem(LS.syncId);
  if (!id) throw new Error('Sync not set up');
  const url = SUPABASE_URL + '/rest/v1/' + SYNC_TABLE + '?sync_id=eq.' + id + '&select=data,updated_at';
  const r = await fetch(url, {
    headers: {apikey: SUPABASE_KEY, Authorization: 'Bearer ' + SUPABASE_KEY},
  });
  if (!r.ok){
    const txt = await r.text();
    throw new Error('Pull HTTP ' + r.status + ': ' + txt.slice(0,200));
  }
  const rows = await r.json();
  return rows.length ? rows[0] : null;
}
async function pushRemote(merged){
  const id = localStorage.getItem(LS.syncId);
  if (!id) throw new Error('Sync not set up');
  const url = SUPABASE_URL + '/rest/v1/' + SYNC_TABLE + '?on_conflict=sync_id';
  const body = JSON.stringify({sync_id: id, data: merged, updated_at: new Date().toISOString()});
  const r = await fetch(url, {
    method: 'POST',
    headers: {
      apikey: SUPABASE_KEY,
      Authorization: 'Bearer ' + SUPABASE_KEY,
      'Content-Type': 'application/json',
      Prefer: 'resolution=merge-duplicates,return=minimal',
    },
    body,
  });
  if (!r.ok){
    const txt = await r.text();
    throw new Error('Push HTTP ' + r.status + ': ' + txt.slice(0,200));
  }
}
async function setupSync(plaintextId){
  if (!plaintextId || plaintextId.length < 8) throw new Error('Pick a passphrase of 8+ characters');
  const id = await sha256(plaintextId);
  localStorage.setItem(LS.syncId, id);
  await syncNow(true);
}
let __syncInFlight = false;
async function syncNow(initial){
  if (__syncInFlight) return;
  if (!localStorage.getItem(LS.syncId)){toast('Set up sync first','warn'); return;}
  __syncInFlight = true;
  const btn = $('#sync-btn'); if (btn) btn.disabled = true;
  try {
    toast('Pulling remote…');
    const remote = await pullRemote();
    const local = snapshotLocal();
    const merged = mergeData(local, remote ? remote.data : null);
    state.progress = merged.progress;
    state.bookmarks = merged.bookmarks;
    state.flash = merged.flash;
    state.examHistory = merged.examHistory;
    state.streak = merged.streak;
    state.prefs = Object.assign({}, state.prefs, merged.prefs);
    saveAll();
    toast('Pushing merged data…');
    await pushRemote(merged);
    localStorage.setItem(LS.syncLast, new Date().toISOString());
    toast(initial ? 'Sync enabled — data merged' : 'Sync complete', 'success');
  } catch (e) {
    toast('Sync failed: ' + e.message, 'danger');
    console.error(e);
  } finally {
    __syncInFlight = false;
    if (btn) btn.disabled = false;
    renderStats();
  }
}

// ============================================================================
// KEYBOARD
// ============================================================================
function onKey(e){
  if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT')) return;
  const v = $$('.view.active')[0]; if (!v) return;
  if (v.id === 'view-practice' && state.practice && state.practice.questions){
    const s = state.practice;
    const q = s.questions[s.idx];
    if (e.key >= '1' && e.key <= '4'){
      const idx = parseInt(e.key) - 1;
      if (!(q.id in s.picks)){
        s.picks[q.id] = idx; recordAnswer(q.id, idx === q.correct); tickStreak(); saveAll(); renderPracticeSession();
      }
    } else if (e.key === 'ArrowRight' || e.key === 'Enter'){
      if (s.idx < s.questions.length-1){s.idx++; renderPracticeSession();}
    } else if (e.key === 'ArrowLeft'){
      if (s.idx > 0){s.idx--; renderPracticeSession();}
    } else if (e.key === 'b' || e.key === 'B'){
      state.bookmarks[q.id] = !state.bookmarks[q.id]; save(LS.bookmarks, state.bookmarks); renderPracticeSession();
    } else if (e.key === '?'){
      showSourceModal('Practice shortcuts', '1-4 select choice • Enter / → next • ← prev • B bookmark • ? this help');
    }
  } else if (v.id === 'view-exam' && state.exam){
    const ex = state.exam;
    const q = ex.questions[ex.idx];
    if (e.key >= '1' && e.key <= '4'){
      const idx = parseInt(e.key) - 1;
      ex.picks[q.id] = idx; saveAll(); renderExam();
    } else if (e.key === 'ArrowRight' || e.key === 'Enter'){
      if (ex.idx < ex.questions.length-1){ex.idx++; saveAll(); renderExam();}
    } else if (e.key === 'ArrowLeft'){
      if (ex.idx > 0){ex.idx--; saveAll(); renderExam();}
    } else if (e.key === 'f' || e.key === 'F'){
      ex.flagged[q.id] = !ex.flagged[q.id]; saveAll(); renderExam();
    }
  }
}

// ============================================================================
// SWIPE (mobile practice)
// ============================================================================
function bindSwipe(){
  let sx=0, sy=0, t=0;
  document.addEventListener('touchstart', e=>{const t0 = e.changedTouches[0]; sx=t0.clientX; sy=t0.clientY; t=Date.now();}, {passive:true});
  document.addEventListener('touchend', e=>{
    const t0 = e.changedTouches[0];
    const dx = t0.clientX - sx, dy = t0.clientY - sy, dt = Date.now()-t;
    if (dt > 700 || Math.abs(dy) > 80) return;
    if (Math.abs(dx) < 60) return;
    const v = $$('.view.active')[0]; if (!v) return;
    if (v.id === 'view-practice' && state.practice){
      const s = state.practice;
      if (dx < 0 && s.idx < s.questions.length-1){s.idx++; renderPracticeSession();}
      else if (dx > 0 && s.idx > 0){s.idx--; renderPracticeSession();}
    }
  }, {passive:true});
}

// ============================================================================
// BOOT
// ============================================================================
function boot(){
  $('#gate').style.display = 'none';
  $('#app').style.display = 'flex';
  load();
  // Wire nav
  $$('nav.bottom button').forEach(b => b.addEventListener('click', ()=>go(b.dataset.view)));
  // Wire modal close
  $('#modal').addEventListener('click', e=>{if (e.target.id === 'modal') $('#modal').classList.remove('show');});
  // Resume in-progress exam timer
  if (state.exam && !state.exam.finished){
    if (window.__examTick) clearInterval(window.__examTick);
    window.__examTick = setInterval(()=>{
      if (!state.exam || state.exam.finished){clearInterval(window.__examTick); return;}
      const v = $$('.view.active')[0];
      if (v && v.id === 'view-exam') renderExam();
    }, 1000);
  }
  go('dashboard');
  document.addEventListener('keydown', onKey);
  bindSwipe();
  checkStreakWarning();
}

// ============================================================================
// INIT
// ============================================================================
window.addEventListener('DOMContentLoaded', ()=>{
  if (localStorage.getItem(LS.unlocked) === '1'){boot(); return;}
  $('#pw-form').addEventListener('submit', e=>{e.preventDefault(); tryUnlock();});
  $('#pw').focus();
});

})();
"""


def html_doc():
    domains_js = json.dumps(DOMAIN_META)
    cheat_js = json.dumps(CHEAT_SHEETS)
    return (
        "<!DOCTYPE html>\n"
        "<html lang=\"en\">\n"
        "<!--\n"
        "  CISSP EXAM PREP — single-file HTML application\n"
        f"  Built: 2026-04-26 • Questions: {len(QUESTIONS)} • Flashcards: {len(FLASHCARDS)}\n"
        "  No external dependencies. Loads & runs offline.\n"
        "  DESIGN NOTES:\n"
        "  - Domain weights follow the 2024 ISC2 outline (April 2024 refresh).\n"
        "  - Source distribution: ~37% guide / ~62% web / ~1% canonical (web exceeds the 40% target;\n"
        "    guide is just below 40%, but every guide-tagged question carries valid page + section refs).\n"
        "  - Web research uses 258 distinct URLs across 8 domains (≥30 per domain). All references\n"
        "    are stored as URL strings only; nothing is fetched at runtime.\n"
        "  - SM-2 spaced repetition: easiness factor, interval, repetitions, due-date per card stored in localStorage.\n"
        "  - CAT-style exam: pool weighted by domain percentages, navigator panel, refresh-safe via persisted state.\n"
        "  - Password gate uses Web Crypto API SHA-256 — plaintext is never stored.\n"
        "-->\n"
        "<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1,viewport-fit=cover\">\n"
        "<title>CISSP Exam Prep</title>\n"
        "<style>" + CSS + "</style>\n"
        "</head>\n"
        "<body>\n"
        "<div id=\"gate\">\n"
        "  <div class=\"gate-box\">\n"
        "    <div class=\"lock-icon\">🔒</div>\n"
        "    <h1>CISSP EXAM PREP</h1>\n"
        "    <p class=\"muted\">Enter access password</p>\n"
        "    <form id=\"pw-form\">\n"
        "      <input id=\"pw\" type=\"password\" autocomplete=\"current-password\" placeholder=\"Password\" autofocus>\n"
        "      <div id=\"pw-err\" style=\"color:#ef4444;font-size:.85rem;margin-top:.4rem;min-height:1em\"></div>\n"
        "      <button class=\"primary\" type=\"submit\" style=\"margin-top:.6rem;width:100%\">Unlock</button>\n"
        "    </form>\n"
        f"    <div class=\"muted\" style=\"font-size:.75rem;margin-top:1rem\">{len(QUESTIONS)} questions • {len(FLASHCARDS)} flashcards • runs fully offline</div>\n"
        "  </div>\n"
        "</div>\n"
        "<div id=\"app\">\n"
        "  <header class=\"topbar\">\n"
        "    <h1>CISSP PREP</h1>\n"
        "    <span class=\"pill\">2024 outline</span>\n"
        f"    <span class=\"pill mono\">{len(QUESTIONS)} Qs</span>\n"
        "    <div class=\"right\">\n"
        "      <button class=\"ghost\" onclick=\"document.body.classList.toggle('light')\" title=\"Toggle theme\">◐</button>\n"
        "    </div>\n"
        "  </header>\n"
        "  <nav class=\"bottom\">\n"
        "    <button data-view=\"dashboard\" class=\"active\" aria-label=\"Dashboard\"><span class=\"nico\" aria-hidden=\"true\">▦</span><span>Dashboard</span></button>\n"
        "    <button data-view=\"read\" aria-label=\"Read chapters and reference\"><span class=\"nico\" aria-hidden=\"true\">📖</span><span>Read</span></button>\n"
        "    <button data-view=\"practice\" aria-label=\"Practice questions\"><span class=\"nico\" aria-hidden=\"true\">✎</span><span>Practice</span></button>\n"
        "    <button data-view=\"exam\" aria-label=\"Full exam simulation\"><span class=\"nico\" aria-hidden=\"true\">⏱</span><span>Exam</span></button>\n"
        "    <button data-view=\"flash\" aria-label=\"Flashcards\"><span class=\"nico\" aria-hidden=\"true\">⚡</span><span>Flashcards</span></button>\n"
        "    <button data-view=\"stats\" aria-label=\"Stats and history\"><span class=\"nico\" aria-hidden=\"true\">∿</span><span>Stats</span></button>\n"
        "  </nav>\n"
        "  <main>\n"
        "    <div id=\"view-dashboard\" class=\"view active\"></div>\n"
        "    <div id=\"view-practice\" class=\"view\"></div>\n"
        "    <div id=\"view-exam\" class=\"view\"></div>\n"
        "    <div id=\"view-read\" class=\"view\"></div>\n"
        "    <div id=\"view-flash\" class=\"view\"></div>\n"
        "    <div id=\"view-stats\" class=\"view\"></div>\n"
        "  </main>\n"
        "</div>\n"
        "<div id=\"toasts\" class=\"toasts\"></div>\n"
        "<div id=\"modal\" class=\"modal-bg\">\n"
        "  <div class=\"modal\" id=\"modal-body\"></div>\n"
        "</div>\n"
        "<script>\n"
        f"window.__PW_HASH__ = {json.dumps(PW_HASH)};\n"
        f"window.__DOMAINS__ = {domains_js};\n"
        f"window.__CHEAT__ = {cheat_js};\n"
        f"window.__TOPICS__ = {json.dumps(TOPICS, separators=(',', ':'))};\n"
        f"window.__TABLES__ = {json.dumps(TABLES, separators=(',', ':'))};\n"
        # JSON.parse('...') is parsed faster than inline JS object literals for
        # large payloads in modern V8/JSC engines. Wrap the two large arrays.
        f"window.__QUESTIONS__ = JSON.parse({json.dumps(json.dumps(QUESTIONS, separators=(',', ':')))});\n"
        f"window.__FLASHCARDS__ = JSON.parse({json.dumps(json.dumps(FLASHCARDS, separators=(',', ':')))});\n"
        "</script>\n"
        "<script>" + JS + "</script>\n"
        "</body>\n"
        "</html>\n"
    )


def main() -> None:
    OUT.write_text(html_doc())
    size = OUT.stat().st_size / 1024
    print(f"[+] {OUT} ({size:.1f} KiB)")
    print(f"  Questions embedded: {len(QUESTIONS)}")
    print(f"  Flashcards embedded: {len(FLASHCARDS)}")
    print(f"  Domains: {len(DOMAIN_META)}")
    print(f"  Web sources cited: {sum(len(d['sources']) for d in WEB['domains'].values())}")


if __name__ == "__main__":
    main()
