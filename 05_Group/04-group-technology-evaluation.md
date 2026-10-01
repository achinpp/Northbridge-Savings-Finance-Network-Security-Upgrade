# Group Technology Evaluation and Selection

**Main body deliverable.** The sixteen individual proposals (4 members × 4 areas) are in
Appendices A1–A4. This section is the group's comparative evaluation of them and the final
recommendation for Northbridge in each of the four mandatory areas.

## Method

Each member completed all four of their proposals independently and submitted them before the
group met, as the brief requires. At the evaluation meeting we did four things in order, for
each area separately:

1. Agreed the **evaluation criteria** for that area *before* re-reading the proposals, so the
   criteria could not be reverse-engineered from a preferred answer.
2. Scored all four proposals against the same criteria, head to head.
3. Selected one.
4. Recorded, for each of the three rejected proposals, the **specific** reason it lost — and,
   where a rejected proposal contained something the winner did not, recorded what we adopted
   from it anyway.

Scoring is **1–5 per criterion, higher is better**. The scores are a device for forcing direct
comparison; the reasoning below each table is what actually decided it.

Summary of outcomes:

| Area | Adopted | From | Runner-up |
|---|---|---|---|
| VPN | Cisco Secure Client (AnyConnect) IKEv2/IPsec on a Cisco Secure Firewall pair | **Member 1** | Member 2 (FortiGate) |
| AAA | Cisco ISE — RADIUS for network access, TACACS+ for device administration | **Member 1** | Member 4 (Aruba ClearPass) |
| Network architecture | Dual-firewall DMZ sandwich, dedicated partner extranet and integration broker, out-of-band management | **Member 3** | Member 1 (single-vendor three-tier) |
| IDS/IPS | Inline Firepower IPS at zone boundaries **plus** flow-based behavioural detection from existing switch NetFlow | **Member 4** | Member 3 (Suricata/Zeek/SIEM) |

Member 2's proposals were not adopted in any area. That is recorded plainly rather than
softened, and Section 5 sets out what Member 2's submissions did change about the plan, because
their influence on the phasing and on Control 2 was substantial.

---

## 1. VPN solution for secure remote access

### The four proposals

- **Member 1 (A1.1)** — Cisco Secure Client (AnyConnect) IKEv2/IPsec remote-access VPN on a
  redundant Cisco Secure Firewall pair. Per-user certificates plus password plus MFA, RADIUS
  delegation to the central AAA service, posture assessment, per-group tunnel policy for staff
  / contractors / administrators, split tunnelling disabled for core banking.
- **Member 2 (A2.1)** — FortiGate NGFW pair with FortiClient SSL/IPsec VPN, RADIUS
  authentication with app-based MFA, separate portals per user class, FortiClient compliance
  gating. Chosen primarily because one bundled licence covers VPN, NGFW, IPS and web filtering.
- **Member 3 (A3.1)** — WireGuard on a hardened Linux gateway pair, per-user public keys, fixed
  modern cipher suite with no negotiation, MFA at an authentication proxy issuing short-lived
  configurations, per-user `AllowedIPs` as cryptographic routing.
- **Member 4 (A4.1)** — Zero Trust Network Access via a cloud broker, outbound-only connectors
  with no published inbound port, per-application rather than per-network authorisation,
  continuous session re-evaluation, site-to-site IPsec retained for branches only.

### Head-to-head against agreed criteria

| Criterion | M1 | M2 | M3 | M4 |
|---|---|---|---|---|
| Eliminates the shared credential structurally | 5 | 4 | **5** | 5 |
| Endpoint posture assessment (contractor devices) | **5** | 4 | 1 | 5 |
| Integrates with the chosen AAA service | **5** | 4 | 3 | 3 |
| Operable by a newly formed team with no firewall experience | 4 | 4 | 3 | **5** |
| Resilience to the organisation's absent patch process | 2 | 2 | **5** | 5 |
| Avoids introducing a new unassessed third-party dependency | **5** | 5 | 5 | 1 |
| Commercial support and audit evidence for a regulator | **5** | 5 | 2 | 4 |
| Deliverable within Phase 1 (12 weeks) | 4 | **5** | 4 | 3 |
| **Total (of 40)** | **35** | 33 | 28 | 31 |

### Selection: Member 1's proposal

Adopted because it is the only proposal that scores at or near the top on **both** of the two
criteria the group judged decisive for this area — posture assessment of unmanaged devices, and
integration with the central AAA service — without introducing a new problem elsewhere.

The posture criterion is decisive because of a specific fact in the brief: two **external IT
support contractors** need regular access to internal systems, and Northbridge has no vendor
security assessment process, so these are the least-known devices that will touch the network.
The AAA integration criterion is decisive because T1 and T2 share one root cause — the absence
of a central identity authority — and a VPN that keeps its own account store recreates that
problem on the most exposed device in the estate.

### Why each rejected proposal lost

**Member 2's FortiGate lost narrowly, and on vendor coherence rather than on capability.** It
scored equal or better than Member 1 on deliverability and equal on support, and its central
argument — that one bundled licence frees budget for the controls that have no product attached
— was accepted by the group as correct and is reflected in the phasing. What it lost on was
this: Member 2's own proposal acknowledged that splitting the VPN away from a Cisco-based
switching estate means two management planes for a team that has never run one, and the group
had by then selected a Cisco-based AAA platform and a Cisco-based IPS. Member 2 was right that
when two products both fully solve the stated problem the deciding factor is what else the
money buys; the group's judgement was that for a team of this maturity, *one* vendor
relationship across VPN, firewall, IPS and AAA buys more risk reduction than the licence
saving does. Had the AAA decision gone the other way, this proposal would have won.

**Member 3's WireGuard lost on posture assessment, which Member 3 identified themselves.**
Member 3 stated plainly that WireGuard has no posture capability and that this is a real loss
given personal devices and unassessed contractor machines. The group agreed, and weighted it
higher than Member 3 did. Member 3's strongest argument — that giving an organisation with no
patch process an internet-facing appliance whose safety depends on patching promptly is the
wrong risk — is genuinely strong, and it scored 5 where Member 1 scored 2. It did not carry the
decision because the group concluded the correct response is to fix the patch process
(Control 10) rather than to choose an architecture around its absence, and because for a
licensed financial institution the absence of commercial support and compliance reporting on
the remote-access path is difficult to defend to a regulator. We did adopt one element: the
observation that a key file cannot be read out over the telephone the way a password can is the
reason **Control 4 requires per-user certificates in addition to a password**, not merely MFA.

**Member 4's ZTNA lost on the third-party dependency, which Member 4 also identified
themselves.** It scored highest of the four on operability and on patch-process resilience, and
its central argument — that putting a user "on the network" is meaningless protection while the
network is flat — is correct about Northbridge today. Two things defeated it. First, it is
self-defeating once Control 5 is implemented: ZTNA's advantage shrinks precisely as segmentation
improves, and segmentation is Phase 1. Second, and decisively, it would route a regulated
bank's authentication through a cloud broker that Northbridge has no process to assess — which
is exactly the unassessed transitive trust that Member 3's T6 rates critical. The group would
not recommend that an organisation whose vendor assessment process does not yet exist should
make a vendor its authentication path. **ZTNA is retained as a Phase 3 roadmap item**, because
the group accepted the destination and disagreed only about the sequence.

---

## 2. AAA solution for centralised authentication

### The four proposals

- **Member 1 (A1.2)** — Cisco ISE, redundant pair, federated to the existing directory. RADIUS
  for network access, TACACS+ with per-command authorisation and accounting for device
  administration, 802.1X with dynamic VLAN and dACL assignment, profiling and posture.
- **Member 2 (A2.2)** — Microsoft Entra ID as identity authority with Windows NPS as the RADIUS
  front end and the Entra MFA NPS extension. Conditional Access for BYOD/WFH, Privileged
  Identity Management for just-in-time elevation. No TACACS+; RADIUS plus configuration-change
  logging offered as a compensating control for device administration.
- **Member 3 (A3.2)** — FreeRADIUS, OpenLDAP, privacyIDEA for TOTP and `tac_plus` for TACACS+.
  Configuration under version control, rebuilt from text rather than restored from backup.
- **Member 4 (A4.2)** — Aruba ClearPass Policy Manager, redundant pair. RADIUS and TACACS+ in
  one platform, with device profiling and fingerprinting as the headline capability, plus
  OnGuard posture, OnBoard BYOD provisioning and ClearPass Guest.

### Head-to-head against agreed criteria

| Criterion | M1 | M2 | M3 | M4 |
|---|---|---|---|---|
| TACACS+ per-command authorisation and accounting (closes T2) | **5** | 1 | 4 | **5** |
| Device profiling — builds the missing asset inventory | 4 | 2 | 1 | **5** |
| Enables the 802.1X dynamic segmentation Control 5/6 needs | **5** | 3 | 3 | 4 |
| Answer for unmanaged personal devices (BYOD / work from home) | 4 | **5** | 1 | 4 |
| Time to deliver MFA on remote access | 3 | **5** | 3 | 3 |
| Availability risk, given untested backups and no DR plan | 3 | 4 | **5** | 3 |
| Commercial support appropriate to a regulated institution | **5** | 5 | 1 | 5 |
| Avoids pre-committing the other three technology decisions | 2 | 4 | **5** | 4 |
| Total cost of ownership | 2 | **5** | 4 | 3 |
| **Total (of 45)** | **33** | 34 | 27 | **36** |

### Selection: Member 1's proposal (Cisco ISE)

**This is the one area where the group selected a proposal that did not score highest**, and
the reasoning needs stating because it is a judgement rather than an arithmetic result.
Member 4's ClearPass scored 36 and Member 2's NPS scored 34, against Member 1's 33.

Two criteria were re-weighted after scoring, by agreement. First, **"avoids pre-committing the
other three technology decisions"** turned out to be a criterion about the *order* of our own
meeting rather than about Northbridge. By the time the AAA decision was taken, the group had
already selected a Cisco-based VPN on its own merits, and the architecture discussion was
heading toward a design that the AAA platform does not constrain. Member 4's concern about
lock-in was legitimate when they wrote it and had largely dissolved by the time we decided.

Second, **"enables the 802.1X dynamic segmentation Control 5/6 needs"** was re-weighted upward.
The plan's two highest-rated threats, T1 and T3, are defeated by identity and segmentation
acting together: 802.1X assigning a device to a zone based on who it is, rather than on which
socket it is plugged into. ISE's integration with Cisco switching does that more directly than a
vendor-neutral platform speaking standard RADIUS, and the access layer in the group topology is
Cisco.

ISE therefore wins on the combination of TACACS+ accounting (which closes T2's accountability
gap, the single clearest audit finding in the brief) and tight 802.1X integration with the
segmentation programme, with profiling and posture as capable second-tier capabilities.

### Why each rejected proposal lost

**Member 4's ClearPass lost the closest contest in the whole evaluation, and lost on a
criterion that had decayed.** On capability it is ISE's equal, and on the criterion Member 4
weighted most — device profiling to build the asset inventory Northbridge does not have — it is
genuinely better, scoring 5 against ISE's 4. Member 4's argument that "the first thing
Northbridge needs is not enforcement, it is to find out what is on its network" was accepted by
the group as correct, and it changed the plan: **Control 1 now requires a monitor-mode
discovery period before any 802.1X enforcement**, and Control 6's 802.1X rollout is placed in
Phase 3 behind that discovery, which is Member 4's sequencing applied to Member 1's platform.
What ClearPass lost on was the vendor-neutrality advantage that was its main differentiator,
which was worth much less once the VPN and IPS decisions had both gone to Cisco — at which
point a vendor-neutral platform's benefit is theoretical and its looser fabric integration is
real.

**Member 2's NPS lost on TACACS+, decisively and on the single criterion that matters most
here.** It scored highest of the four on cost and on time-to-MFA, and best on the BYOD question
— Conditional Access conditions access on the state of a device the organisation does not own,
which is a genuinely better answer for the brief's work-from-home gap than a NAC posture engine
is. Member 2 was honest that their compensating control for device administration — RADIUS plus
configuration-change logging — is weaker, recording that it captures *that* a configuration
changed, not *who typed which command*, and that it can be defeated by an administrator who
disables logging first. The group agreed and treated that as disqualifying. T2's central
finding is that Northbridge cannot attribute a privileged action to an individual; an AAA
proposal that cannot fix that for infrastructure is solving the loud problem and leaving the
audit finding. We did adopt Member 2's two best arguments: **Control 2 (MFA) was split out as a
separate control specifically so it can be delivered in Phase 1 without waiting for the full
AAA programme**, which is Member 2's time-to-MFA point, and **Control 3 requires just-in-time
elevation rather than standing privilege**, which is Member 2's PIM proposal.

**Member 3's open-source stack lost on support and operational burden.** It scored top of the
four on availability risk, and that argument was the sharpest in the whole evaluation: making a
single appliance pair the gate on all network access, in an organisation whose backups have
never been test-restored and which has no documented disaster recovery plan, concentrates
availability risk badly. The group accepted it and did not reject it — **Control 1 explicitly
requires a redundant pair, a documented and tested rebuild procedure, and local fallback
credentials on every device**, which is why Member 1's Configuration 1 was built with
`group tacacs+ local` and includes a fallback test in its verification sequence. The proposal
itself lost because four separately operated open-source components require in-house expertise
a newly formed team does not have, and because a regulator examining the central authentication
control of a deposit-taking institution will expect commercial support and a vendor
accountability chain. Member 3 named this counter-argument themselves and judged it
non-binding; the group judged it binding.

---

## 3. Secure network architecture with multiple firewalls and defined zones

### The four proposals

- **Member 1 (A1.3)** — Three-tier single-vendor design: internet-edge firewall pair plus
  internal/core firewall pair, seven named zones including `PARTNER-EXTRANET` and `MGMT-OOB`,
  default-deny with owned and review-dated rules.
- **Member 2 (A2.3)** — One HA NGFW cluster carrying all externally facing zones, with the
  internal trust boundary enforced one layer down by VLAN segmentation and inter-VLAN ACLs on
  the distribution switches. Per-branch VLAN sets so a compromise at one branch is contained.
- **Member 3 (A3.3)** — Dual-firewall DMZ sandwich with **heterogeneous vendors** on the two
  tiers, a dedicated `PARTNER-EXTRANET` plus a separate `INTEGRATION-BROKER` zone, and a
  physically separate out-of-band management network reachable only from a jump host.
- **Member 4 (A4.3)** — Two firewall tiers for north-south traffic plus identity-based
  **micro-segmentation inside the core banking zone**, enforced by host and hypervisor policy
  with a discovery and monitor phase before blocking.

### Head-to-head against agreed criteria

| Criterion | M1 | M2 | M3 | M4 |
|---|---|---|---|---|
| Satisfies the brief's "multiple firewalls" requirement literally | **5** | 2 | **5** | **5** |
| Internal boundary survives compromise of the external one | 4 | 2 | **5** | 4 |
| Resists a single-vendor critical vulnerability | 2 | 1 | **5** | 2 |
| Contains the branch-to-core ransomware path (T3) | 4 | 4 | 4 | **5** |
| Isolates the compromised public web tier (T5) | 4 | 3 | **5** | 4 |
| Terminates partner trust safely before go-live (T6) | 4 | 3 | **5** | 4 |
| Protects the management plane from the data plane | 4 | 2 | **5** | 4 |
| Operable by a team with no firewall experience | 4 | **5** | 2 | 1 |
| Implementable within Phase 1 (12 weeks) | 4 | **5** | 3 | 1 |
| **Total (of 45)** | 35 | 27 | **39** | 30 |

### Selection: Member 3's proposal

Adopted, with one modification. The DMZ-sandwich structure, the `PARTNER-EXTRANET` plus
`INTEGRATION-BROKER` separation, and the out-of-band management network are adopted in full.
The **heterogeneous-vendor requirement is adopted as a preference rather than a constraint**,
to be decided at procurement — the group accepted Member 3's correlated-failure argument but
weighed it against Member 3's own admission that it doubles the operational skill requirement
for a team that has never run one firewall.

Member 3's proposal won on the two criteria that trace most directly to the brief's own
emphasis. The `INTEGRATION-BROKER` zone — a validating intermediary that is the only system
permitted to speak to the core banking environment, so the partners never address the database
— is a design element no other proposal contained, and it is the structural answer to the
brief's statement that the integration extends trust beyond Northbridge's infrastructure for
the first time with no vendor assessment process in place. The physically separate out-of-band
management network is the other: it is the only proposal that removes *all* paths from the user
data plane to a device's management interface, which matters in an organisation where
management interfaces currently share a flat network with guest Wi-Fi.

We also adopted Member 3's own mitigation for the complexity it introduces: **Control 5
requires the internal firewall tier to carry a deliberately small and static rule set**, so the
device needing the most care needs the least change.

### Why each rejected proposal lost

**Member 1's single-vendor three-tier design lost on correlated failure, and only on that.**
It is the runner-up and it scored within four points. Its zone model is excellent — the group
adopted Member 1's zone naming and the requirement that every allow rule carries an owner and a
review date. What it lost on is the criterion Member 3 built their proposal around: two tiers
of the same vendor fail together on one critical vulnerability, and Northbridge's risk is
unusually concentrated, with a single customer database in a single data centre reachable from
the internet. When one boundary carries that much weight, the device most likely to have an
exploited vulnerability — the internet-facing one — is the one you least want sharing a codebase
with the device protecting the database. Member 1's design scored 2 on that criterion against
Member 3's 5, and that gap is the whole margin.

**Member 2's collapsed cluster lost on the brief's literal requirement, which Member 2
anticipated.** Member 2 stated that reading an HA cluster plus a distinct second enforcement
layer as satisfying "multiple firewalls" was the weakest point of their proposal and that a
reader might judge it as not satisfying the requirement. The group did so judge it. Beyond
compliance, it scored lowest on the criterion that matters most for the brief's own lead
scenario: the ransomware path starts *inside* the perimeter, and a collapsed design puts the
internal user LAN and the core banking environment on two legs of the same device — so the one
policy engine that must stop internal lateral movement is also the device exposed to the
internet. Member 2's operational-risk argument was nonetheless the most important thing anyone
said about this area, and it was adopted in the specific form described above. **Member 2's
per-branch VLAN sets were also adopted into Control 5**, because containing branches from each
other — not merely from the data centre — is what breaks the brief's documented attack pattern,
and no other proposal specified it.

**Member 4's micro-segmentation lost on sequencing, which Member 4 identified themselves.**
It scored highest on containing the branch-to-core path and its central observation is correct
and uncomfortable: zone-based segmentation filters traffic *between* zones and does nothing to
traffic *within* a zone, so once `CORE-BANKING` is a zone, an attacker who reaches any host in
it can reach them all — and T8's intruder starts inside that zone. The group accepted the gap
is real. It lost because micro-segmentation requires an accurate map of which system talks to
which on which port, and Northbridge has no asset inventory, no documented architecture and a
decade of organic growth. Getting that map wrong breaks the core banking application in
production. Member 4's own judgement — that this is the right Phase 3 and the wrong Phase 1 —
was accepted. **The east-west gap is now named explicitly in the residual risk table**, which
is what Member 4 asked for, and micro-segmentation is a Phase 3 item.

---

## 4. IDS/IPS solution

### The four proposals

- **Member 1 (A1.4)** — Inline Firepower (Snort 3) IPS with Talos feeds, licensed on both
  firewall tiers. Prevention mode at the edge for DMZ traffic and on the internal tier for
  core-banking traffic, 30-day detection-only burn-in, virtual patching for the known branch
  CVEs, all events to the SIEM.
- **Member 2 (A2.4)** — The NGFW's bundled inline IPS at the edge in prevention mode, plus
  open-source Snort 3 sensors on internal SPAN ports at head office in detection mode. Branch
  coverage deferred on the grounds that branch traffic traverses the head-office aggregation
  uplink.
- **Member 3 (A3.4)** — Suricata inline at zone boundaries plus Zeek sensors for protocol
  metadata, both feeding a Wazuh/Elastic SIEM, with the SIEM deployment also closing the
  centralised-logging gap.
- **Member 4 (A4.4)** — Inline Firepower IPS at zone boundaries **plus flow-based behavioural
  detection from NetFlow exported by the switches and routers Northbridge already owns**, at
  all seven sites, into a flow analytics collector that baselines normal behaviour.

### Head-to-head against agreed criteria

| Criterion | M1 | M2 | M3 | M4 |
|---|---|---|---|---|
| Prevents, not merely detects, at zone boundaries | **5** | 3 | **5** | **5** |
| East-west / intra-zone visibility (T3, T7, T8) | 1 | 2 | 3 | **5** |
| Detects an authenticated attacker using valid credentials | 1 | 1 | 3 | **5** |
| Branch coverage without new hardware at six sites | 3 | 2 | 2 | **5** |
| Works on day one with no security operations analyst | **5** | 2 | 3 | 4 |
| Produces evidence that answers "what was the breach scope?" | 2 | 2 | **5** | 4 |
| Nothing new to patch, given the absent patch process | 4 | 1 | 1 | **5** |
| Commercial support and tuning | **5** | 3 | 1 | **5** |
| Total cost of ownership | 2 | **5** | 4 | 3 |
| **Total (of 45)** | 28 | 21 | 27 | **41** |

### Selection: Member 4's proposal

Adopted, and it is the clearest margin in the evaluation. Member 4's design is the only one
that covers both halves of Northbridge's detection problem, and the group concluded that the
second half is the larger one.

The first half is **known exploits crossing a boundary**, which an inline signature IPS handles
and which three of the four proposals handle equivalently. The second half is **an attacker
already inside, using valid credentials and legitimate protocols**, which no signature engine
detects because there is no signature for "Alice's account is behaving unlike Alice". Of the
eight threats this group modelled, that second category covers T1, T2, T7 and T8 outright and
most of T3's propagation phase — because Northbridge's weaknesses are overwhelmingly credential
and access weaknesses rather than software vulnerabilities. Flow-based behavioural detection is
the only proposed mechanism that sees it.

The decisive practical argument is the branch one. Northbridge has **six branches with no
security staff**, and the brief's lead ransomware scenario *starts* at a branch workstation.
NetFlow export is a configuration line on switches Northbridge already owns, so visibility
exists at every branch on day one with no appliance to install, manage or patch — in an
organisation the brief says has no formal patch management process.

### Why each rejected proposal lost

**Member 1's IPS-only design lost on intra-zone blindness.** It scored top on day-one
operability, which is a real advantage for a team with no analyst, and its 30-day burn-in
before enabling blocking was adopted verbatim into Control 7 because it is the right way to
avoid taking the banking portal offline with a false positive. It lost because an inline IPS is
structurally blind to traffic that does not cross the device: it scored 1 on east-west
visibility and 1 on detecting an authenticated attacker, against Member 4's 5 on both. Member 4
put the objection precisely — an IPS-only design gives Northbridge good coverage of attacks
coming through the front door and no coverage of attacks already inside, which is most of the
eight threats modelled here. Member 1's inline IPS component **is** the first half of the
adopted design, so this proposal was not rejected so much as found incomplete.

**Member 2's SPAN-based design lost on being detection-only where prevention was needed, and
Member 2 conceded the point in advance.** Member 2 wrote that "a detection-only internal sensor
does nothing without someone reading it", that Northbridge has no incident response process and
no 24×7 capability, and that an internal Snort alert at 2 a.m. may sit unread until morning —
judging that acceptable because the ransomware staging phase runs over days. The group rejected
that judgement on the strength of Member 2's **own** threat model, which rates T3 at likelihood
5 and quotes the brief's phrase "spread rapidly". The plan cannot rate a threat at maximum
likelihood on the basis that it moves fast and then rely on a morning-shift analyst to catch
it. Two further problems: a SPAN sensor design needs an appliance, a SPAN session and a
management path at every site where visibility is wanted, which is seven unpatched appliances
in an organisation with no patch process; and its branch-coverage argument — that branch traffic
is visible at the head-office aggregation uplink — covers branch-to-core traffic but not
branch-internal lateral movement, which is where T3 begins.

**Member 3's Suricata/Zeek/SIEM design lost on operational burden, but contributed the single
most valuable idea in this area.** It scored top equal on prevention and highest of all four on
the criterion "produces evidence that answers what was the breach scope?", and Member 3's
argument for it is one the group found persuasive: Northbridge has no centralised logging at
all, so if a breach is discovered next year it has no way to establish when it started or what
left, and that is the question a regulator and the payment partners will both ask. An IPS alert
feed cannot answer it. The proposal lost because Suricata, Zeek and a self-built Elastic stack
require deployment, tuning and operation by a brand-new security team with no analyst, scoring
1 on commercial support and 1 on "nothing new to patch". But its central insight was adopted:
**Member 3's argument is why Control 8 exists as a first-class control with its own number**,
why the SIEM is specified as ingesting flow records and protocol metadata rather than only
alerts, and why Control 8 maps to all eight threats. Member 3 was right that the IDS/IPS
decision is the natural moment to fix logging; the group simply chose to fix it with a separate
numbered control rather than by adopting the whole open-source stack.

---

## 5. What Member 2's proposals changed, despite not being adopted

Member 2 did not win any of the four areas, and the group wants to record what their
submissions actually changed, because a reader comparing the outcome table against the
appendices would otherwise conclude their work had no effect.

Member 2's overall stance — that Northbridge's board "approves spending it can picture", that a
programme needing a large capital approval before anything improves is a programme that stalls,
and that budget should be weighed across four controls rather than concentrated in one — is the
reasoning behind the **three-phase implementation plan** in `01-layered-security-plan.md`, and
behind the decision to place Controls 16 and 17 first on the explicit grounds that they are the
cheapest in the plan and remove T8 from the critical band on their own.

Three specific adoptions:

- **Control 2 (MFA) exists as a separate control from Control 1 (AAA)** because of Member 2's
  argument that Northbridge needs MFA on remote access in weeks, not after a NAC programme.
  Closing T1 two quarters earlier is worth more than closing T2's accountability gap two
  quarters sooner than otherwise.
- **Control 5 requires per-branch VLAN sets**, from Member 2's architecture proposal. No other
  member specified branch-from-branch containment, and it is what breaks the brief's documented
  pattern of a single branch workstation spreading across the network.
- **Control 3 requires just-in-time elevation rather than standing privilege**, from Member 2's
  Privileged Identity Management proposal.

Member 2's proposals lost consistently on one axis — each optimised for cost and speed at the
expense of a capability the group judged non-negotiable (TACACS+ accounting, multiple
firewalls, inline internal prevention). That is a coherent pattern rather than four unrelated
misses, and it reflects a defensible position that the group weighed and overruled, not an
absence of analysis.
