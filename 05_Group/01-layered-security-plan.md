# Combined Layered Security Plan (Group)

**Northbridge Savings & Finance — Network Security Upgrade**
Group deliverable. All four members contributed; the reconciliation decisions below were taken
jointly after each member's individual threat modelling was complete.

---

## 1. How the eight individual threats were reconciled

The brief requires that the eight individually modelled threats be "genuinely reconciled
(overlapping threats merged, contradictions resolved) rather than just listed one after
another". This section records that work before the control list is presented, because the
control list is a product of it.

### 1.1 The eight threats as submitted

| ID | Owner | Threat | L | I | Score | Band |
|---|---|---|---|---|---|---|
| T1 | Member 1 | Compromise of the shared VPN account | 5 | 5 | 25 | Critical |
| T2 | Member 1 | Credential abuse and privilege escalation via password reuse, no central AAA | 4 | 5 | 20 | Critical |
| T3 | Member 2 | Ransomware propagation from a branch workstation across the flat network | 5 | 5 | 25 | Critical |
| T4 | Member 2 | Rogue DHCP / ARP spoofing man-in-the-middle from guest Wi-Fi and unlocked cabinets | 4 | 4 | 16 | Critical |
| T5 | Member 3 | SQL injection against the internet-facing online banking portal | 4 | 5 | 20 | Critical |
| T6 | Member 3 | Abuse of the third-party payment processor connection | 3 | 5 | 15 | Critical |
| T7 | Member 4 | Social engineering (vishing) against staff credentials | 5 | 4 | 20 | Critical |
| T8 | Member 4 | Physical compromise of the server room, with unrecoverable outage | 3 | 5 | 15 | Critical |

All four members used the same Likelihood × Impact method and the same bands, which was agreed
before individual work began specifically so the scores would be comparable at this stage.
Every threat lands in the critical band. That is not score inflation — it is a consequence of
the brief describing an organisation with no dedicated firewall, no IDS/IPS, no MFA, no central
authentication, no central logging, no patch process, no segmentation, no awareness training,
no incident response plan and no tested backups. There is no control in place for any of these
chains to have to defeat.

### 1.2 Overlaps identified and merged

**Merge 1 — T1 and T2 share one root cause.** Member 1 flagged this in their own submission.
Both threats reduce to the absence of a central identity and accounting authority: T1 is that
absence exploited remotely, T2 is the same absence exploited internally. We treated them as one
remediation programme (**Controls 1–4**) rather than two, which is why there is no separate
"VPN account management" control in the list.

**Merge 2 — T5's pivot step and T3's lateral movement are the same mechanism.** Member 3's T5
chain escalates from a compromised web tier into the flat network; Member 2's T3 chain
propagates from a compromised branch workstation into the same flat network. The attacker's
entry point differs; everything after it is identical. One control (**Control 5**) therefore
carries both, and we did not write separate "DMZ isolation" and "internal segmentation"
controls.

**Merge 3 — T4's physical entry route and T8's branch exposure are one finding.** Member 2's
T4 relies on unlocked branch cabinets and unenforced visitor sign-in to put the attacker on
the segment; Member 4's T8 names the same unlocked cabinets as a sub-case of its own
vulnerability. Rather than duplicating, **Control 17** covers the physical dimension for both
and **Control 6** covers the Layer 2 consequence for both.

**Merge 4 — T7 is an input to T1, T2 and T3, not a parallel threat.** Member 4 made this point
explicitly. A vished credential is the *supply* for the shared-VPN compromise, the credential
replay chain and the ransomware foothold. We resolved this by treating **Control 14** as a
likelihood-reducing control across four threats rather than as a standalone control for T7,
and by noting in the mapping that **Control 2 (MFA)** is what caps T7's impact — a disclosed
password with MFA in place is far less useful than one without.

**Merge 5 — the detection gap is common to six of the eight threats.** T1, T2, T3, T4, T5 and
T6 all contain a step whose success depends on nobody noticing. Rather than adding a detection
control per threat, **Controls 7 and 8** are specified once and mapped against all six.

### 1.3 Contradictions between members' submissions, and how we resolved them

Four genuine disagreements surfaced. Recording them matters because the brief asks for
contradictions resolved, not smoothed over.

**Contradiction 1 — is the plan's detection control preventive or detective?** Member 2's
IDS/IPS proposal (A2.4) specified open-source sensors on SPAN ports in *detection* mode
internally, arguing that commercial inline subscriptions across seven sites were unaffordable
and that the ransomware staging window runs over days. Member 4's proposal (A4.4) argued that
Member 2's own T3 chain contains "spread rapidly", that Northbridge has no 24×7 operations
capability, and that a control nobody is awake to read is not a control.

*Resolved in favour of prevention.* Member 2's own threat model is the strongest evidence
against Member 2's proposal here — the brief says incidents "spread rapidly", and the plan
cannot simultaneously rate T3 at likelihood 5 and rely on a morning-shift analyst. Control 7
is therefore specified as **inline prevention at zone boundaries plus flow-based behavioural
detection**, which is Member 4's design. Member 2's cost objection was accepted as valid and
is answered by the phasing in Section 4 rather than by weakening the control.

**Contradiction 2 — commercial or open-source AAA?** Member 1 and Member 4 proposed commercial
platforms (ISE, ClearPass); Member 3 proposed an open-source stack, arguing that concentrating
all network access decisions in one appliance pair is unwise in an organisation whose backups
have never been test-restored. Member 2 proposed the cheapest and fastest option (NPS), which
has no TACACS+ at all.

*Resolved in favour of a commercial platform (Control 1), with Member 3's objection accepted
as a design requirement rather than rejected.* Member 3's availability concern is legitimate,
so the control explicitly requires a redundant pair, a documented and tested rebuild
procedure, and — this is the point we took directly from Member 3 — **local fallback
credentials on every device**, which is why Member 1's Configuration 1 was built with
`group tacacs+ local` and a fallback test in its verification sequence. Member 2's objection
that MFA is needed in weeks rather than quarters was also accepted, and is answered by
splitting Control 2 (MFA) out as a separate control that can be delivered on the VPN ahead of
the full AAA deployment.

**Contradiction 3 — how many firewalls?** Member 2 proposed a single HA cluster plus
distribution-layer ACLs, arguing that a team with no firewall experience is more likely to
misconfigure four firewalls than to be defeated through two. Members 1, 3 and 4 all proposed
two tiers.

*Resolved in favour of two tiers.* The brief requires "multiple firewalls", and Member 2
acknowledged in their own submission that this was the weakest point of their proposal.
Member 2's operational-risk argument was accepted in a specific form: Control 5 requires the
**internal tier to carry a deliberately small and static rule set**, so the device that needs
the most care needs the least change. That mitigation came from Member 3's submission and was
adopted jointly.

**Contradiction 4 — replace the VPN or modernise it?** Member 4 proposed replacing
network-level VPN with ZTNA, arguing that putting a user "on the network" is meaningless
protection while the network is flat. Members 1, 2 and 3 all proposed conventional VPNs.

*Resolved in favour of a conventional VPN now (Control 4), with ZTNA as a phase 3 roadmap
item.* Member 4's argument is correct about today's flat network but self-defeating once
Control 5 is in place: ZTNA's advantage shrinks as segmentation improves. Member 4 also raised
the counter-argument themselves — that routing a regulated bank's authentication through an
unassessed third-party broker is exactly the risk their colleague's T6 identifies as critical.
The group agreed that an organisation with no vendor assessment process should not make a
vendor its authentication path, and that this is a sequencing problem rather than a
disagreement about the destination.

### 1.4 Gaps none of the eight threats covered, and what we did about them

Honest accounting: three weaknesses in the brief are not the primary subject of any of the
eight threat models.

- **No formal patch management process.** It appears as a *vulnerability* inside T3 and T5
  rather than as a threat of its own. It is significant enough to warrant its own control
  (**Control 10**).
- **BYOD and work-from-home with no guidance.** Appears inside T2's and T7's attack surface.
  Covered by **Control 13** and **Control 15**.
- **No data classification policy.** Appears as an impact amplifier in T5 and T8 — it is why a
  successful extraction likely yields plaintext. Covered by **Control 12** and **Control 15**.

We chose to add controls for these rather than retrofit threats to justify them, because
inventing a ninth and tenth threat after the fact would misrepresent the individual work.

---

## 2. Master list of proposed controls

Eighteen controls. The number is the result of the minimisation exercise written up separately
in `03-control-minimisation.md`; an earlier draft had twenty-six.

Each control is numbered for use in the mapping tables. **Where a control is implemented by one
of the group's eight Packet Tracer configurations, that is noted — this is the evidence that we
can implement what we recommend, not only describe it.**

---

### Identity and access (Controls 1–4)

**Control 1 — Centralised AAA service (RADIUS + TACACS+)**
A redundant pair of policy servers providing RADIUS for all network access (VPN, 802.1X wired
and wireless, guest onboarding) and TACACS+ with per-command authorisation and accounting for
administration of every router, switch and firewall. Federated to the existing user directory
rather than becoming a new account store. All authentication, authorisation and accounting
records forwarded to Control 8. Every device retains local fallback credentials and a
documented rebuild procedure.
*Implemented by Configuration 1 (Member 1).*

**Control 2 — Multi-factor authentication on all remote, administrative and privileged access**
MFA enforced on the remote-access VPN, on all administrative and privileged accounts, on
webmail, and on the staff-facing administration interface of the online banking portal.
Specified as a separate control from Control 1 deliberately, so that it can be delivered on the
VPN in weeks rather than waiting on the full AAA programme.

**Control 3 — Individual named accounts, least-privilege RBAC, and an account lifecycle process**
Abolition of every shared and generic account, starting with the shared VPN account and the
shared local credentials on network devices. Role-based access with least privilege, standing
privilege replaced by just-in-time elevation for administrative roles, and a documented
joiner / mover / leaver process with a single point from which access is revoked. Quarterly
access review and recertification.
*Partly implemented by Configuration 1 (Member 1).*

**Control 4 — Enterprise remote-access VPN replacing the shared account**
Per-user authentication against Control 1, per-user certificates in addition to
username/password, MFA via Control 2, endpoint posture assessment before the tunnel is admitted
to internal zones, and separate address pools and policy sets for staff, contractors and
administrators. Split tunnelling disabled for sessions that reach the core banking zone.

### Network architecture and segmentation (Controls 5–6)

**Control 5 — Zoned network architecture with two firewall tiers and default-deny inter-zone policy**
Two firewall tiers, with the DMZ between them, replacing the flat network. Zones: `OUTSIDE`,
`DMZ`, `PARTNER-EXTRANET`, `INTEGRATION-BROKER`, `CORE-BANKING`, `INTERNAL-USERS` (per-site
VLANs), `GUEST`, `MGMT-OOB`. Default-deny between all zones with explicit, owned, review-dated
allow rules. The internal tier carries a deliberately small and static rule set. Branch sites
receive their own VLAN sets so that a compromise at one branch is contained to that branch.
Guest Wi-Fi terminates on the external tier and has no route to any internal zone.
*Implemented by Configuration 3 (Member 2) at the internal zone boundaries, and Configuration 5
(Member 3) at the internet perimeter.*

**Control 6 — Layer 2 access hardening baseline on every access switch**
A single standard configuration applied to every access switch at all seven sites: 802.1X
authentication fed by Control 1, port security with per-role violation actions, DHCP snooping,
Dynamic ARP Inspection with ARP ACLs for statically addressed servers, BPDU guard and PortFast
on access ports, unused ports administratively shut and parked in an unused VLAN, native VLAN
moved off VLAN 1, and DTP negotiation disabled.
*Implemented by Configuration 4 (Member 2) and Configuration 6 (Member 3).*

### Detection and monitoring (Controls 7–8)

**Control 7 — Inline IPS at zone boundaries plus flow-based behavioural detection**
Signature-based inline IPS in prevention mode on the internet edge for DMZ-bound traffic and on
the internal tier for core-banking-bound traffic, with a 30-day detection-only burn-in measured
against real traffic before blocking is enabled, and explicit virtual-patching coverage for the
known CVEs on the outdated branch software until Control 10 catches up. In addition, NetFlow
telemetry exported from the switches and routers Northbridge already owns at all seven sites
into a flow analytics collector that baselines normal behaviour and alerts on deviation —
internal host sweeps, protocols appearing on paths they have never used, unprecedented egress
volumes, and periodic beaconing.

**Control 8 — Centralised logging, SIEM and alerting, with authenticated NTP**
All device, server, application, firewall, IPS and AAA logs shipped to a central platform with
defined retention. Authenticated NTP across the estate so that records can be ordered into a
timeline. Defined alert severities with a documented escalation path and named on-call
responsibility. Configuration-change logging on all infrastructure.
*Implemented by Configuration 8 (Member 4).*

**Control 9 — Secure management plane**
SSH-only management with Telnet disabled, a separate out-of-band management network reachable
only from a hardened jump host, VTY access restricted by ACL to the management subnet, session
idle timeouts, brute-force throttling, legal banners, and TACACS+ command authorisation from
Control 1.
*Implemented by Configuration 2 (Member 1).*

### Hardening and resilience of systems (Controls 10–13)

**Control 10 — Patch and vulnerability management programme**
A formal process with an asset inventory, monthly authenticated vulnerability scanning,
severity-based remediation SLAs, a defined emergency patch path for actively exploited
vulnerabilities, and explicit remediation of the outdated operating systems and applications
on branch systems. Exceptions registered, risk-accepted by a named owner, and time-bound.

**Control 11 — Web application protection for the online banking portal and mobile API**
A web application firewall in front of the portal and the mobile API gateway, a secure
development lifecycle with mandatory code review and parameterised queries, pre-release
security testing, and an annual independent penetration test of the internet-facing estate.
Database accounts used by the application restricted to least privilege.

**Control 12 — Cryptographic standard for data in transit and at rest**
TLS 1.2 minimum (1.3 preferred) for all customer-facing and internal web traffic; IPsec with
AES-256, SHA-256 and DH group 14 or better for all site-to-site branch links and the partner
integration; encryption at rest for the core banking database, its backups and all endpoint
disks. Certificate-based authentication preferred over pre-shared keys. Key management and
rotation documented.
*No Packet Tracer configuration demonstrates this control. The platform used for the practical
work has no cryptographic feature set — `crypto isakmp` is absent from the parser and the
`securityk9` package cannot be activated, as evidenced in Member 4's Configuration 7 write-up.
The control stands as a recommendation; it is recorded here as the one control in the plan with
no implementation evidence behind it.*
*Flow-based half implemented by Configuration 7 (Member 4) on HQ-R1 and BR1-R1.*

**Control 13 — Endpoint protection and EDR, with a BYOD baseline**
Managed endpoint detection and response on all Northbridge-owned endpoints and servers, with
application allow-listing on branch workstations and point-of-service equipment. A defined
minimum baseline for personal devices used for work — disk encryption, screen lock, supported
OS version, endpoint protection — enforced as a condition of access by Control 4's posture
check.

### Governance, people and third parties (Controls 14–16, 18)

**Control 14 — Security awareness and anti-social-engineering programme**
Mandatory induction and annual refresher training for all 450 staff, with role-specific content
for branch staff. Simulated phishing and vishing exercises with measured outcomes. A published,
enforced rule that IT will never request a password, together with a **verified callback
procedure** giving staff a safe way to check. A single, publicised reporting route, with
positive recognition for reporting rather than blame for being targeted.

**Control 15 — Information security policy set**
Data classification and handling policy; acceptable use policy; credential policy prohibiting
sharing and reuse, with enforced complexity and a password manager provided; BYOD and
work-from-home policy; third-party and vendor security policy; physical security policy.
Board-approved, published, acknowledged by every member of staff, and reviewed annually.

**Control 16 — Incident response and disaster recovery plans, with tested backups**
A documented incident response plan with defined roles, severity classification, escalation
and communication paths (including regulator and partner notification), and the authority to
sever the partner connection named in advance. A documented disaster recovery plan with agreed
recovery time and recovery point objectives. A backup programme with at least one immutable or
offline copy held away from the primary site, and **mandatory quarterly restoration testing of
the core banking database with documented evidence of success**. Both plans exercised annually
by tabletop and at least once technically.

**Control 17 — Physical security upgrade**
Auditable individual badge access replacing the shared server-room key, with an access log and
alerting on out-of-hours entry. Camera coverage of the server room and of entry points at all
seven sites. Lockable, locked network cabinets at every branch with keys issued individually.
Enforced visitor sign-in with escort for unaccompanied visitors. Visible security signage at
all sites. Removal of backup media from the server room to a separate secured location.

**Control 18 — Third-party and partner security assurance**
A vendor security assessment process applied to both payment processors and to the two IT
support contractors before the integration goes live: due diligence questionnaire, evidence of
certification or independent audit, and a documented risk acceptance by a named owner.
Contractual security requirements including breach notification timeframes and a right to
audit. Technically: mutual TLS with certificate pinning, IP allow-listing, partner traffic
terminating in `PARTNER-EXTRANET` and reaching the core only through the validating integration
broker, input validation on every partner-supplied message, and transaction rate and value
anomaly alerting into Control 8.
*Technical half partly implemented by Configuration 5 (Member 3), whose published-socket model
stands in for the partner extranet on a two-interface router.*

---

## 3. Residual risk after the plan

| Threat | Before | After full implementation | What remains |
|---|---|---|---|
| T1 | 25 Critical | 4 Low | Compromise of an individual account with MFA bypass; now detectable and attributable |
| T2 | 20 Critical | 4 Low | Insider abuse within authorised role; now fully audited via TACACS+ accounting |
| T3 | 25 Critical | 8 Medium | Initial foothold still possible; propagation contained to one branch VLAN, detected by flow analysis, recovery proven by tested backups |
| T4 | 16 Critical | 4 Low | Attacker on a segment is isolated to that segment and blocked by DAI/port security |
| T5 | 20 Critical | 8 Medium | An application flaw may still exist; WAF, DMZ isolation and least-privilege DB accounts cap the outcome |
| T6 | 15 Critical | 6 Medium | Partner compromise remains outside Northbridge's control; broker validation and anomaly alerting cap the outcome |
| T7 | 20 Critical | 6 Medium | Humans remain targetable; MFA caps the value of a disclosed password, training reduces disclosure rate |
| T8 | 15 Critical | 4 Low | Physical intrusion still possible but now deterred, detected, attributable, and survivable through tested offline backups |

No threat is reduced to zero, and we have not claimed that. T3, T5, T6 and T7 remain at Medium
because each depends on something Northbridge cannot fully control — a user clicking, an
undiscovered application flaw, a partner's own security, human susceptibility to persuasion.

## 4. Implementation phasing

The brief establishes a hard deadline: the payment processor integration goes live within two
quarters, and the CTO commissioned this review "before the integration proceeds". Phasing is
driven by that constraint and by Member 3's T6 argument that the cost of retrofitting partner
controls rises sharply once the partners have built against whatever Northbridge ships.

**Phase 1 — before the integration (weeks 1–12), non-negotiable**
Controls 2 (MFA on remote access), 3 (abolish the shared VPN account), 5 (zones and both
firewall tiers, including `PARTNER-EXTRANET`), 9 (secure management plane), 16 (backup
restoration testing and the incident response plan), 17 (server room badge access and camera),
18 (vendor assessment of both payment processors). Controls 16 and 17 are first because they
are the cheapest in the plan and they take T8 out of the critical band on their own.

**Phase 2 — consolidation (quarters 2–3)**
Controls 1 (full AAA with TACACS+), 4 (enterprise VPN), 6 (Layer 2 baseline across all seven
sites), 7 (IPS and flow analytics), 8 (SIEM and NTP), 10 (patch programme), 11 (WAF and secure
SDLC), 14 (awareness programme), 15 (policy set).

**Phase 3 — maturity (quarter 4 onward)**
Control 12 at-rest encryption completion, Control 13 EDR and BYOD baseline, 802.1X enforcement
following a monitor-mode period, and the micro-segmentation and ZTNA items held over from
Members 4's and 3's proposals.

> One sequencing dependency is worth stating explicitly, because getting it wrong is how
> organisations lock themselves out: **Control 9 must precede Control 1.** Putting individual
> administrator credentials onto a management plane that still runs Telnet would broadcast
> those credentials in plaintext across the network, making the identity control worse than
> useless. This is why Member 1's two configurations were designed as a pair, and why the
> free-choice one is the prerequisite for the plan-linked one.
