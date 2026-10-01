# Control Mapping and Classification Tables (Group)

Control numbers refer to the master list in `01-layered-security-plan.md`.
Threat IDs refer to the eight individually modelled threats, listed in Section 1.1 of that
document and authored in the four member folders.

---

## Table A — Control-to-Threat / Attack Mapping

| # | Control | Threats / attacks addressed |
|---|---|---|
| 1 | Centralised AAA (RADIUS + TACACS+) | **T1** shared VPN account compromise · **T2** credential replay and privilege escalation · **T4** unauthenticated device joining a trusted segment (via 802.1X) · **T7** use of a vished credential |
| 2 | Multi-factor authentication | **T1** · **T2** · **T7** — caps the value of any disclosed or replayed password |
| 3 | Individual named accounts, least-privilege RBAC, account lifecycle | **T1** abolishes the shared account itself · **T2** removes shared infrastructure credentials and standing privilege · **T7** limits the reach of one compromised identity |
| 4 | Enterprise remote-access VPN | **T1** replaces the vulnerable access path · **T2** removes the VPN's independent credential store |
| 5 | Zoned architecture, two firewall tiers, default-deny | **T3** breaks ransomware lateral movement · **T4** separates guest Wi-Fi from staff segments · **T5** isolates the compromised web tier (no DMZ→internal, no DMZ→outbound) · **T6** terminates partner trust in its own zone behind a broker · **T8** limits what an intruder inside the server room can reach |
| 6 | Layer 2 access hardening baseline | **T3** blocks rogue devices and limits propagation at the access layer · **T4** defeats rogue DHCP and ARP spoofing directly |
| 7 | Inline IPS plus flow-based behavioural detection | **T1** detects anomalous internal activity after VPN entry · **T2** detects credential replay patterns · **T3** detects and blocks internal reconnaissance and lateral movement · **T5** blocks injection payloads at the edge · **T6** detects anomalous partner traffic · **T8** detects an implant or unexpected host on the network |
| 8 | Centralised logging, SIEM, alerting, authenticated NTP | **All eight (T1–T8).** Every threat contains a step whose success depends on nobody noticing, and every control's output is worth less without an ordered, attributable timeline |
| 9 | Secure management plane | **T2** stops credential capture on the management path and enforces command authorisation · **T4** removes management reachability from a user segment · **T8** limits what console access yields |
| 10 | Patch and vulnerability management | **T3** removes the unpatched branch workstation entry route · **T5** remediates known portal and platform vulnerabilities |
| 11 | Web application protection (WAF, secure SDLC, penetration testing) | **T5** the primary control — blocks and remediates the injection flaw itself |
| 12 | Cryptographic standard, in transit and at rest | **T4** renders intercepted branch traffic useless and makes modification detectable · **T5** protects data in transit and limits what extracted records yield · **T6** mutual TLS authenticates the partner connection · **T8** encryption at rest defeats drive and backup-media theft |
| 13 | Endpoint protection / EDR, with BYOD baseline | **T2** detects credential harvesting tooling · **T3** blocks the ransomware payload at the endpoint · **T7** blocks follow-on malware delivery after a disclosed credential |
| 14 | Security awareness and anti-social-engineering programme | **T7** the primary control — reduces the disclosure rate and establishes a verified callback path · **T1** reduces the phishing route to the shared credential · **T2** attacks the password sharing and reuse culture · **T3** reduces the phishing click that starts the chain |
| 15 | Information security policy set | **T1** credential policy prohibits sharing · **T2** prohibits reuse; BYOD/WFH policy closes the unmanaged-device gap · **T6** third-party policy mandates assessment · **T7** establishes the "IT will never ask for your password" rule · **T8** physical security policy mandates auditable access and visitor control |
| 16 | Incident response and disaster recovery plans, with tested backups | **T3** caps the ransomware impact by proving recovery is possible · **T5** enables integrity restoration after database tampering · **T6** names in advance who may sever the partner connection · **T7** converts a reported attempt into an organisational warning · **T8** the control that moves this threat from potentially unrecoverable to survivable |
| 17 | Physical security upgrade | **T4** locked cabinets and enforced visitor control remove the physical entry route · **T8** the primary control — auditable access, camera coverage, deterrence and attribution |
| 18 | Third-party and partner security assurance | **T1** brings the two IT support contractors into an assessment regime · **T6** the primary control — assessment, contracts, mutual TLS, allow-listing, broker validation and anomaly alerting |

### Coverage check

| Threat | Controls addressing it | Count |
|---|---|---|
| T1 | 1, 2, 3, 4, 7, 8, 14, 15, 18 | 9 |
| T2 | 1, 2, 3, 4, 7, 8, 9, 13, 14, 15 | 10 |
| T3 | 5, 6, 7, 8, 10, 13, 14, 16 | 8 |
| T4 | 1, 5, 6, 8, 9, 12, 17 | 7 |
| T5 | 5, 7, 8, 10, 11, 12, 16 | 7 |
| T6 | 5, 7, 8, 12, 15, 16, 18 | 7 |
| T7 | 1, 2, 3, 8, 13, 14, 15, 16 | 8 |
| T8 | 5, 7, 8, 9, 12, 15, 16, 17 | 8 |

All eight individually modelled threats are addressed by multiple layers. No threat relies on
a single control, which is the point of a layered plan: every threat must defeat a preventive
control, be missed by a detective control, and survive a recovery control before it causes
lasting harm.

---

## Table B — Dual-Axis Classification: Function × Category

Functions: Preventive, Detective, Deterrent, Corrective, Recovery, Compensating.
Categories: Administrative, Technical, Physical.

**A control that serves more than one function, or spans more than one category, appears in
every cell it genuinely belongs in.** Multi-cell placements are justified in the notes below
the table, because a placement without a reason is indistinguishable from a guess.

| | **Administrative** | **Technical** | **Physical** |
|---|---|---|---|
| **Preventive** | 3, 10, 11, 12, 14, 15, 17, 18 | 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 18 | 17 |
| **Detective** | 3, 10, 11, 18 | 1, 6, 7, 8, 11, 13, 18 | 17 |
| **Deterrent** | 14, 15 | 8, 9 | 17 |
| **Corrective** | 16 | 6, 7, 13 | 16 |
| **Recovery** | 16 | 16 | 16 |
| **Compensating** | 3, 14 | 2, 5, 7, 11 | 17 |

### Why each multi-cell control sits where it does

**Control 3 — individual accounts, RBAC, account lifecycle: 4 cells.**
*Administrative-Preventive* — the joiner/mover/leaver process and the least-privilege standard
are written policy. *Technical-Preventive* — the account configuration and RBAC enforcement
that implement it. *Administrative-Detective* — the quarterly access review and recertification
is a detective activity: it finds accounts that should no longer exist.
*Administrative-Compensating* — during Phase 1, before Control 1 provides a single
deprovisioning point, the manual access review is what compensates for the absence of
automated revocation.

**Control 7 — inline IPS plus flow-based detection: 4 cells.**
*Technical-Preventive* — inline mode blocks the exploit before it lands.
*Technical-Detective* — flow analytics alerts on behaviour that no signature covers.
*Technical-Corrective* — an inline drop terminates an in-progress session, which is corrective
action on live traffic rather than prevention of a future event. *Technical-Compensating* — the
virtual-patching signatures explicitly compensate for the known-unpatched branch software until
Control 10 catches up, which is the textbook definition of a compensating control.

**Control 11 — web application protection: 5 cells, the widest in the plan.**
*Technical-Preventive* — the WAF blocks the payload. *Administrative-Preventive* — the secure
development lifecycle and mandatory code review are process controls. *Technical-Detective* —
WAF logging surfaces attempted attacks. *Administrative-Detective* — the annual penetration test
is a scheduled process that finds flaws. *Technical-Compensating* — the WAF compensates for
application code that has not yet been remediated, which is precisely why it is deployed first
and the code fixed second.

**Control 17 — physical security upgrade: 4 cells, and the only control in the Physical column
other than 16.**
*Physical-Preventive* — badge readers and locked cabinets stop entry.
*Physical-Detective* — cameras and the access log record who entered and when, which is the
exact gap the brief identifies ("no record of who it was or when it happened").
*Physical-Deterrent* — visible signage and visible cameras discourage the attempt in the first
place; the brief names this explicitly as "no visible deterrent to discourage them from trying
in the first place", so it is a distinct function rather than a side effect.
*Administrative-Preventive* — enforced visitor sign-in and escort is a process, not a device.
*Physical-Compensating* — camera coverage compensates at the sites where auditable badge access
cannot be retrofitted, for example leased branch premises where the door hardware is not
Northbridge's to change.

**Control 16 — incident response, disaster recovery, tested backups: 4 cells, and the only
control appearing in all three categories.**
*Administrative-Corrective* — the incident response plan governs the actions taken to contain
and correct an incident in progress. *Administrative-Recovery* — the disaster recovery plan is
the documented route back to service. *Technical-Recovery* — the backup system, its immutable
copies and the quarterly restoration test are the technical means of recovery.
*Physical-Recovery* — the requirement to hold backup media away from the server room in a
separate secured location is a physical control, and it is the specific thing that defeats T8's
Chain B, where one visit to one room destroys both the primary systems and their only backups.
*Physical-Corrective* — the incident response plan's physical response procedures (securing the
site, escorting an intruder out, preserving the scene) are corrective actions in the physical
category.

**Control 8 — centralised logging, SIEM, NTP: 2 cells.**
*Technical-Detective* — the obvious and primary placement. *Technical-Deterrent* — logging that
staff and contractors know exists deters insider misuse. This is why Control 9's legal banner
states that activity is logged and monitored: the deterrent effect requires that the subject
knows about it, which is what makes it a deterrent rather than merely a detective control.

**Control 9 — secure management plane: 2 cells.**
*Technical-Preventive* — SSH-only, VTY ACLs, timeouts and throttling prevent access.
*Technical-Deterrent* — the legal banner is a deterrent control in the strict sense: it changes
nothing technically, it exists to discourage and to establish that access was unauthorised.

**Control 2 — multi-factor authentication: 2 cells.**
*Technical-Preventive* — the primary placement. *Technical-Compensating* — MFA is explicitly
deployed as a compensating control for the password reuse and sharing culture the brief
describes, which cannot be eliminated quickly. A second factor makes a shared or reused
password insufficient while Controls 14 and 15 work on the underlying behaviour over a much
longer timescale.

**Control 5 — zoned architecture: 2 cells.**
*Technical-Preventive* — default-deny between zones. *Technical-Compensating* — segmentation
compensates for the unpatched branch systems: Northbridge cannot patch them immediately, so
containing them is what reduces the risk in the interim. This is the same logic as Control 7's
virtual patching, applied at the network layer.

**Control 10 — patch and vulnerability management: 3 cells.**
*Administrative-Preventive* — the programme, the SLAs and the exception register are process.
*Technical-Preventive* — the patches themselves. *Administrative-Detective* — monthly
vulnerability scanning is a scheduled detective process that finds what needs patching.

**Control 12 — cryptographic standard: 2 cells.**
*Administrative-Preventive* — the standard document that specifies minimum algorithms, key
lengths and rotation. *Technical-Preventive* — the TLS, IPsec and at-rest encryption
configurations that implement it.

**Control 13 — endpoint protection / EDR: 3 cells.**
*Technical-Preventive* — application allow-listing blocks execution.
*Technical-Detective* — EDR telemetry and alerting. *Technical-Corrective* — automated
quarantine and rollback acts on a compromise already in progress.

**Control 18 — third-party assurance: 4 cells.**
*Administrative-Preventive* — the assessment process and the contractual security requirements.
*Technical-Preventive* — mutual TLS, certificate pinning, IP allow-listing and broker
validation. *Administrative-Detective* — the contractual right to audit and the periodic
reassessment cycle. *Technical-Detective* — transaction rate and value anomaly alerting.

**Control 6 — Layer 2 hardening baseline: 3 cells.**
*Technical-Preventive* — 802.1X, port security and DHCP snooping stop the attack.
*Technical-Detective* — violation counters and logged ARP inspection failures record attempts.
*Technical-Corrective* — the `violation shutdown` action err-disables the port, which is an
automated corrective response to an attack in progress rather than prevention of a future one.

**Control 14 — awareness programme: 3 cells.**
*Administrative-Preventive* — training reduces the chance of disclosure.
*Administrative-Deterrent* — a publicised reporting culture and measured simulation programme
deters the attacker, because attempts get reported and a campaign dies after its first call
rather than running through a staff list unimpeded. *Administrative-Compensating* — training
compensates where no technical control can be applied at all, which is the case for a voice
telephone call: there is no firewall for a phone.

**Control 15 — policy set: 2 cells.**
*Administrative-Preventive* — the policies themselves. *Administrative-Deterrent* — the
disciplinary consequences attached to policy breach are a deterrent, and are the only lever
available against deliberate password sharing once staff have been trained and still choose to
share.

### Note on the distribution

The Technical-Preventive cell is the most populated (13 controls) and the Physical column the
least (2 controls across 6 cells). That is a deliberate reflection of the brief rather than an
oversight: Northbridge's security investment "has gone almost entirely into physical measures
(vaults, alarm systems, branch cameras)", so the organisation already has physical security
capability — the plan adds the specific physical controls it is missing (server-room access
control and cameras, locked branch cabinets, offsite backup media) rather than rebuilding a
physical security programme from nothing.

The Recovery row is the thinnest, holding only Control 16. We considered splitting backups out
as a separate control to populate the row more fully, and deliberately did not; the reasoning
is in the minimisation write-up.
