# Member 3 — Individual Technology Proposals (Appendix A3)

**Member:** [Member 3 — Full Name / IT Number]

> These four proposals were reasoned independently, before any group discussion, as the brief
> requires. They are individually assessed. The group's comparative evaluation appears in the
> main body of the report.

My overall design stance is **architectural rather than product-led**. Northbridge's problem
is not that it bought the wrong firewall; it is that it has no structure — no boundaries, no
inspection points, no separation of management from data. So in each area I have asked what
*shape* the solution needs first and treated the vendor choice as secondary and replaceable.
A consequence of that stance is that two of my four picks are open-source: where the shape is
what matters and the operational burden is acceptable, I would rather spend Northbridge's
limited budget on the areas where commercial support genuinely buys risk reduction.

---

## A3.1 — VPN solution for secure remote access

### Options considered

| Option | Fit for Northbridge |
|---|---|
| **WireGuard on a hardened Linux gateway pair, with per-user keys and MFA enforced at an authentication proxy** | Smallest attack surface of any option; modern cryptography only; very high throughput per core |
| Cisco Secure Client / AnyConnect on a Cisco firewall | Mature, supported, posture-capable; highest cost |
| OpenVPN Community or Access Server | Flexible, well understood, large and complex codebase |
| IPsec/IKEv2 with native OS clients | No client to deploy, but awkward per-user policy and weak posture |

### Selection

**WireGuard, deployed on a redundant pair of hardened Linux gateways in the DMZ**, with:

- **Per-user public keys** — no shared secret exists anywhere in the design, which is the
  direct structural answer to the shared VPN account.
- **A modern, fixed cipher suite** (Curve25519, ChaCha20-Poly1305, BLAKE2s). WireGuard has no
  cipher negotiation, so there is no downgrade attack and no weak-suite misconfiguration
  possible — a class of vulnerability that simply does not exist in this design.
- **MFA enforced at a reverse authentication step**: the user authenticates to the central
  AAA service with username, password and second factor to obtain a short-lived WireGuard
  configuration, rather than holding a permanent tunnel credential.
- **Per-user `AllowedIPs`**, which is cryptographic routing rather than policy routing — a
  contractor's key is mathematically incapable of carrying traffic to an address outside its
  allowed set, independent of any firewall rule.
- **Audit trail** from the authentication proxy and the gateway handshake log, shipped to the
  central SIEM.
- **Roughly 4,000 lines of code in the kernel module**, against hundreds of thousands in a
  commercial SSL VPN appliance. Over the past several years, SSL VPN appliances from every
  major vendor have been among the most actively exploited products on the internet,
  precisely because they are large, internet-facing and highly privileged. A smaller codebase
  is a smaller target.

### The alternative I seriously considered, and why I rejected it

**Cisco Secure Client (AnyConnect) on a Cisco firewall** is the option I would choose for most
banks, and I want to state plainly what rejecting it costs: WireGuard has **no posture
assessment**. It cannot check whether a connecting laptop is patched, encrypted or running
endpoint protection. For Northbridge that is a real loss, because the brief says staff use
their own personal machines and phones for work with no guidance in place, and because the
two external IT contractors' devices are completely unassessed.

I rejected it anyway on a specific, checkable Northbridge fact: the brief says Northbridge has
**no dedicated firewall at all** and a **newly formed** security team. An enterprise SSL VPN
appliance is one of the most exposed devices an organisation can own — it is internet-facing,
it terminates privileged tunnels, and its vulnerabilities are exploited within days of
disclosure. Operating one safely requires a disciplined patch process applied under time
pressure, and the brief states in plain terms that Northbridge has **no formal patch
management process**. Handing a team with no patch process a product whose safety depends
entirely on patching speed is, in my judgement, the wrong risk to take. WireGuard's
attack surface is small enough that a slow patch cycle is survivable.

I would mitigate the posture gap with device certificates issued only to managed endpoints
plus endpoint-protection enforcement at the endpoint management layer — but I accept this is
weaker than a posture engine, and it is the honest cost of my choice.

### Why this fits Northbridge specifically

Two Northbridge facts drive this. First, the organisation's remote-access failure is
*credential sharing*, and per-user public keys make sharing structurally difficult: a
WireGuard key is a file, not a phrase, so it cannot be read out over the phone in the way the
brief's vishing incident describes. Second, Northbridge has no patch process and no firewall
operations experience, so the option whose security depends least on operational discipline
is the one most likely to still be secure in a year.

---

## A3.2 — AAA solution for centralised authentication

### Options considered

| Option | Fit for Northbridge |
|---|---|
| **FreeRADIUS with an OpenLDAP directory and privacyIDEA for TOTP/MFA, plus `tac_plus` for device administration** | No licence cost; full protocol coverage including TACACS+; complete control over policy |
| Cisco ISE | Most capable single product; highest cost; longest deployment |
| Microsoft NPS with the Entra MFA extension | Fastest to MFA; no TACACS+ |
| Aruba ClearPass | Capable mid-market option; third vendor |

### Selection

**An open-source AAA stack**: FreeRADIUS as the RADIUS server, OpenLDAP as the identity
directory, privacyIDEA as the MFA/TOTP authority, and `tac_plus` (or `tac_plus-ng`) providing
TACACS+ for network device administration. Deployed as:

- **Two FreeRADIUS nodes** at head office in active/active, serving VPN authentication,
  802.1X on the wired access layer, and wireless.
- **Per-user TOTP enrolment** in privacyIDEA, with hardware token support for the small
  number of privileged administrator accounts.
- **TACACS+ with per-command authorisation and accounting** on every router, switch and
  firewall — which is the control T2's accountability gap needs.
- **802.1X with dynamic VLAN assignment**, mapping an authenticated identity to the correct
  zone from Member 2's segmentation design.
- **All RADIUS and TACACS+ accounting written to the central SIEM.**
- **Configuration held in version control** and deployed by configuration management, so the
  policy is reviewable and auditable as text rather than as clicks in a web console.

### The alternative I seriously considered, and why I rejected it

**Cisco ISE** is the stronger product and I considered it most seriously, because it collapses
RADIUS, TACACS+, profiling, posture and guest onboarding into one supported platform with one
support contract — and for a regulated financial institution, "there is a vendor on the other
end of the phone at 3 a.m." has genuine value that I am choosing to give up.

I rejected it on a specific structural concern rather than on cost. ISE becomes the
authentication authority for *every* network access decision in the organisation — VPN,
wired, wireless, and device administration. If ISE is unavailable, and the policy is set to
fail closed, nobody can authenticate anywhere; if it is set to fail open, the control
evaporates exactly when the organisation is already in trouble. That concentration is
acceptable in an organisation with mature change control and a tested DR plan. The brief
states Northbridge has **no documented disaster recovery plan** and **backups that have never
been tested for restoration**. Making a single appliance pair the gate on all network access,
in an organisation that cannot demonstrate it can restore anything, concentrates availability
risk in a way I am not willing to recommend. The open-source stack distributes that risk
across four independent, individually recoverable services, each of which can be rebuilt from
a configuration file in version control rather than restored from a backup nobody has tested.

### Why this fits Northbridge specifically

The decisive detail is the untested backups. Northbridge's governance weaknesses are not
evenly distributed — it is specifically weak at *recovery*, and that should shape which
architectures it is given. A stack that is rebuilt from text under version control has a
recovery story that does not depend on the one capability the brief says Northbridge has
never verified. Secondly, by choosing software with no licence cost in this area, I keep
budget available for the controls the brief shows Northbridge needs and which have no product
to buy at all: awareness training, backup restoration testing, and the vendor security
assessment process the payment integration requires.

I acknowledge the counter-argument, and I think it is strong: four open-source components
need in-house expertise that a newly formed security team may not have, and a bank's regulator
may expect commercial support for a control this central. If the group judges that
expectation binding, my proposal should lose on that ground.

---

## A3.3 — Secure network architecture with multiple firewalls and defined zones

### Options considered

| Option | Fit for Northbridge |
|---|---|
| **Dual-firewall DMZ sandwich with a dedicated partner extranet zone and a physically separate out-of-band management network** | Strongest structural separation; internal boundary survives compromise of the external one; management plane unreachable from the data plane |
| Single-vendor three-tier design | Clean, simpler to operate, one vendor's CVE affects both tiers |
| Collapsed single NGFW with multiple legs | Cheapest; one device is the entire perimeter |
| Micro-segmentation over a flat core | Finest granularity; requires an asset inventory Northbridge does not have |

### Selection

**A dual-firewall "DMZ sandwich" with seven named zones and an out-of-band management
network.** The design has three properties I regard as non-negotiable for this organisation.

**Property 1 — the DMZ sits between two independent firewalls.** The external firewall faces
the internet and permits only published HTTPS to the DMZ. The internal firewall separates the
DMZ from everything internal and permits only named application flows. Public traffic
therefore crosses **two** policy enforcement points, enforced by **two different firewall
platforms**, before anything internal is reachable.

**Property 2 — the management plane is physically separate.** All infrastructure management
interfaces live on a dedicated out-of-band network reachable only from a hardened jump host.
No path exists from the user data plane to a device's management interface at all.

**Property 3 — the partner integration terminates in its own zone, at a broker.** The two
payment processors connect to a dedicated extranet zone containing an integration broker. The
broker is the only system permitted to speak to the core banking environment, and the
partners are never permitted to address the database directly.

| Zone | Position | Policy summary |
|---|---|---|
| OUTSIDE | External of FW-EXT | Deny all inbound except published HTTPS |
| DMZ | Between FW-EXT and FW-INT | Reverse proxy + WAF, portal front end, mobile API gateway. No DMZ-initiated path inward except named application flows; no direct egress |
| PARTNER-EXTRANET | Dedicated FW-EXT interface | Mutual TLS, IP allow-listed, to the integration broker only |
| INTEGRATION-BROKER | Dedicated FW-INT interface | The only system permitted to reach CORE-BANKING from the partner side; validates and normalises every message |
| CORE-BANKING | Internal of FW-INT | Named application flows only. No internet path in either direction |
| INTERNAL-USERS | Internal of FW-INT | Per-site VLANs; internet via proxy; core banking by application port |
| GUEST | Dedicated FW-EXT interface | Internet only, client isolation, no internal route |
| MGMT-OOB | Separate network, not a firewall zone | Reachable only from the jump host; administrators authenticated by TACACS+ |

**Heterogeneous platforms.** FW-EXT and FW-INT are deliberately from **different vendors**. A
critical vulnerability in one vendor's firewall — a regular occurrence across the industry —
then compromises one tier, not the boundary.

### The alternative I seriously considered, and why I rejected it

**A single-vendor three-tier design** — the same zone structure, but both firewall tiers from
one vendor — is the option I spent longest on, and on most criteria it is better than mine. One
management console, one policy syntax, one upgrade process, one support relationship, one
skill set to recruit and train for. For a team that has never operated a firewall, that
simplicity reduces the chance of the misconfiguration that is statistically the most likely
cause of a perimeter failure.

I rejected it for one Northbridge-specific reason: **the asset concentration here is unusually
extreme.** Most organisations' critical data is spread across many systems, so the loss of one
boundary is partial. Northbridge's most critical asset is a single customer database in a
single on-premises data centre, and that database is reachable — directly or via the portal —
from the internet. Everything depends on one boundary holding. When a single boundary carries
that much weight, correlated failure is the risk that matters most, and two tiers of the same
vendor fail together on one CVE. The internet-facing firewall is the device most likely to
have an exploited vulnerability, and it is the one I least want sharing a codebase with the
device protecting the database.

I accept that this doubles the operational skill requirement and that a misconfiguration
becomes more likely, which is the honest cost. I mitigate it by proposing that the internal
firewall carry a deliberately small and static rule set — a handful of named application flows
that change rarely — so the device that needs the most care needs the least change.

### Why this fits Northbridge specifically

Every zone traces to a stated weakness, not to a reference diagram. The
**INTEGRATION-BROKER** zone exists because the brief says the payment integration extends
trust beyond Northbridge's infrastructure for the first time and that no vendor assessment
process exists — so the design must assume the partner is untrustworthy, which means the
partner must never address the database. The **MGMT-OOB** network exists because there is no
centralised authentication and management interfaces currently sit on the same flat network as
guest Wi-Fi. The **GUEST** zone on the external firewall, rather than internally, exists
because guest traffic should never traverse an internal device at all. And the **two-firewall
DMZ sandwich** exists because the brief's two most severe threats — the internet-facing portal
and the internal ransomware spread — approach that boundary from opposite sides, and a single
device defending both directions is the single point of failure in this environment.

---

## A3.4 — IDS/IPS solution

### Options considered

| Option | Fit for Northbridge |
|---|---|
| **Suricata in IPS mode inline at zone boundaries, plus Zeek sensors for protocol metadata, both feeding a Wazuh/ELK SIEM** | Prevention and investigation data in one design; no per-sensor licence; the SIEM also closes the central-logging gap |
| Commercial inline IPS on the firewalls | Supported, vendor-tuned, lowest operational effort, recurring subscription |
| Snort 3 on SPAN ports | Free, detection-only, needs a sensor per site |
| Flow-based anomaly detection only | Full east-west coverage, weak on known exploits |

### Selection

**A two-layer open-source detection and prevention design:**

- **Suricata in inline IPS mode** on the DMZ sandwich path and in front of CORE-BANKING,
  using Emerging Threats rule sets, with HTTP, TLS and SQL-protocol rule groups enabled —
  specifically chosen because T5 is a web application attack and T6 arrives over a trusted
  connection, and both need content inspection rather than flow inspection.
- **Zeek sensors** on the same taps, producing structured protocol logs — connection records,
  HTTP transactions, TLS certificate details, DNS queries, file hashes — rather than alerts.
  This is the part I consider most valuable for Northbridge and it is the part a pure IPS does
  not provide.
- **Wazuh with an Elastic backend** as the SIEM, ingesting Suricata alerts, Zeek logs, host
  logs, firewall logs and the AAA accounting records from A3.2. **The same deployment closes
  the "no centralised logging or audit trail" finding**, which is why I treat the SIEM as part
  of the IDS/IPS proposal rather than as a separate project.
- **Virtual patching rules** for the known CVEs on the outdated branch software the brief
  describes, as a holding control until a patch programme exists.
- **A 30-day detection-only burn-in** before enabling inline blocking, so the false-positive
  profile is measured against real Northbridge traffic before it can affect the banking
  portal's availability.

### The alternative I seriously considered, and why I rejected it

**Commercial inline IPS licensed on the firewalls** is the lower-effort answer, and the
honest comparison is uncomfortable for my proposal: a vendor IPS arrives pre-tuned, with
curated signature feeds, vendor support when a rule breaks a production application, and no
sensors to build. Suricata and Zeek need someone to deploy, tune and operate them, and
Northbridge's security team is new.

I rejected it on what it does *not* give. A commercial IPS produces **alerts**. It does not
produce the comprehensive connection-level record that an investigation needs. Northbridge's
position is unusually bad here: the brief says there is **no centralised logging or audit
trail across systems**, so if a breach is discovered next year, Northbridge currently has no
way to establish when it started, what was reached, or what left. That question — *scope* — is
the one a regulator and the payment partners will both ask, and an IPS alert feed cannot
answer it. Zeek's connection and transaction logs can. I chose the design that answers the
scope question because, given the brief's catalogue of weaknesses, my judgement is that
Northbridge is more likely to need to investigate a breach than to prevent all of them.

I also note the practical point: licensing commercial IPS at the two firewall tiers, plus a
separate SIEM product, is two subscriptions. The open-source design delivers prevention,
investigation data and central logging from one deployment effort.

### Why this fits Northbridge specifically

Three details decide it. First, **no centralised logging** — so the IDS/IPS choice is the
natural moment to fix logging, and choosing a design that includes the SIEM avoids running
two projects where one will do. Second, **a single data centre with six branches
back-hauling over dedicated links** — so inline sensors at the head-office zone boundaries see
essentially all traffic that matters, with no branch deployment. Third, **the regulatory
dimension**: a licensed financial institution will be asked to demonstrate what happened, and
retained protocol logs are the evidence. Buying alerts without evidence would leave
Northbridge able to say it was attacked but not able to say what was taken — which, for a bank,
is the more expensive of the two failures.
