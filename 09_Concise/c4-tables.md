# 5. Control Mapping and Classification

## 5.1 Control to Threat mapping

| # | Control | Threats addressed |
|---|---|---|
| 1 | Centralised AAA | T1 shared account compromise, T2 credential replay and escalation, T4 unauthenticated device joining a trusted segment via 802.1X, T7 use of a vished credential |
| 2 | Multi factor authentication | T1, T2, T7. Caps the value of any disclosed or replayed password |
| 3 | Named accounts and lifecycle | T1 abolishes the shared account itself, T2 removes shared infrastructure credentials and standing privilege, T7 limits the reach of one compromised identity |
| 4 | Enterprise remote access VPN | T1 replaces the vulnerable access path, T2 removes the VPN's independent credential store |
| 5 | Zoned architecture | T3 breaks lateral movement, T4 separates guest Wi-Fi from staff, T5 isolates the compromised web tier, T6 terminates partner trust behind a broker, T8 limits what an intruder in the server room can reach |
| 6 | Layer 2 hardening baseline | T3 blocks rogue devices and limits propagation at the access layer, T4 defeats rogue DHCP and ARP spoofing directly |
| 7 | Inline IPS and flow detection | T1 detects anomalous activity after VPN entry, T2 detects replay patterns, T3 detects and blocks reconnaissance and lateral movement, T5 blocks injection payloads at the edge, T6 detects anomalous partner traffic, T8 detects an implant or unexpected host |
| 8 | Central logging, SIEM, NTP | **All eight.** Every threat contains a step whose success depends on nobody noticing, and every control's output is worth less without an ordered attributable timeline |
| 9 | Secure management plane | T2 stops credential capture on the management path and enforces command authorisation, T4 removes management reachability from a user segment, T8 limits what console access yields |
| 10 | Patch and vulnerability management | T3 removes the unpatched workstation entry route, T5 remediates known portal and platform vulnerabilities |
| 11 | Web application protection | T5, the primary control, blocks and remediates the injection flaw itself |
| 12 | Cryptographic standard | T4 renders intercepted branch traffic useless and makes modification detectable, T5 protects data in transit and limits what extracted records yield, T6 mutual TLS authenticates the partner, T8 encryption at rest defeats drive and media theft |
| 13 | Endpoint protection and BYOD baseline | T2 detects credential harvesting tooling, T3 blocks the ransomware payload at the endpoint, T7 blocks follow on malware delivery |
| 14 | Awareness programme | T7, the primary control, reduces the disclosure rate and establishes a verified callback path. T1 reduces the phishing route to the shared credential, T2 attacks the sharing and reuse culture, T3 reduces the phishing click that starts the chain |
| 15 | Policy set | T1 credential policy prohibits sharing, T2 prohibits reuse and closes the unmanaged device gap, T6 third party policy mandates assessment, T7 establishes the rule that IT will never ask for a password, T8 physical policy mandates auditable access and visitor control |
| 16 | IR, DR, tested backups | T3 caps the ransomware impact by proving recovery is possible, T5 enables integrity restoration after tampering, T6 names in advance who may sever the partner connection, T7 converts a reported attempt into an organisational warning, T8 the control that moves this from potentially unrecoverable to survivable |
| 17 | Physical security upgrade | T4 locked cabinets and enforced visitor control remove the physical entry route, T8 the primary control, auditable access, cameras, deterrence and attribution |
| 18 | Third party assurance | T1 brings both IT contractors into an assessment regime, T6 the primary control, assessment, contracts, mutual TLS, allow listing, broker validation and anomaly alerting |

### Coverage check

| Threat | Controls | Count |
|---|---|---|
| T1 | 1, 2, 3, 4, 7, 8, 14, 15, 18 | 9 |
| T2 | 1, 2, 3, 4, 7, 8, 9, 13, 14, 15 | 10 |
| T3 | 5, 6, 7, 8, 10, 13, 14, 16 | 8 |
| T4 | 1, 5, 6, 8, 9, 12, 17 | 7 |
| T5 | 5, 7, 8, 10, 11, 12, 16 | 7 |
| T6 | 5, 7, 8, 12, 15, 16, 18 | 7 |
| T7 | 1, 2, 3, 8, 13, 14, 15, 16 | 8 |
| T8 | 5, 7, 8, 9, 12, 15, 16, 17 | 8 |

All eight threats are addressed by multiple layers. No threat relies on a single control, which
is the point of a layered plan. Every threat must defeat a preventive control, evade a detective
control, and survive a recovery control before causing lasting harm.

## 5.2 Function by Category classification

A control serving more than one function, or spanning more than one category, appears in every
cell it genuinely belongs in. Multi cell placements are justified below, because a placement
without a reason is indistinguishable from a guess.

| | Administrative | Technical | Physical |
|---|---|---|---|
| **Preventive** | 3, 10, 11, 12, 14, 15, 17, 18 | 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 18 | 17 |
| **Detective** | 3, 10, 11, 18 | 1, 6, 7, 8, 11, 13, 18 | 17 |
| **Deterrent** | 14, 15 | 8, 9 | 17 |
| **Corrective** | 16 | 6, 7, 13 | 16 |
| **Recovery** | 16 | 16 | 16 |
| **Compensating** | 3, 14 | 2, 5, 7, 11 | 17 |

### Why the multi cell controls sit where they do

**Control 11, web application protection, five cells, the widest in the plan.**
Technical Preventive, the WAF blocks the payload. Administrative Preventive, the secure
development lifecycle and code review are process controls. Technical Detective, WAF logging
surfaces attempted attacks. Administrative Detective, the annual penetration test is a scheduled
process that finds flaws. Technical Compensating, the WAF compensates for code not yet
remediated, which is why it deploys first and the code is fixed second.

**Control 17, physical security, five cells across two categories.**
Physical Preventive, badge readers and locked cabinets stop entry. Physical Detective, cameras
and the access log record who entered and when, the exact gap the brief identifies. Physical
Deterrent, visible signage and cameras discourage the attempt, which the brief names explicitly
as absent, so it is a distinct function rather than a side effect. Administrative Preventive,
enforced visitor sign in and escort is a process, not a device. Physical Compensating, cameras
compensate at sites where auditable badge access cannot be retrofitted, such as leased branch
premises where the door hardware is not Northbridge's to change.

**Control 16, IR, DR and tested backups, four cells, the only control in all three categories.**
Administrative Corrective, the IR plan governs actions taken to contain an incident in progress.
Administrative Recovery, the DR plan is the documented route back to service. Technical Recovery,
the backup system, its immutable copies and the quarterly restoration test. Physical Recovery,
the requirement to hold backup media away from the server room is a physical control, and it is
the specific thing that defeats T8's chain B, where one visit destroys both the primary systems
and their only backups. Physical Corrective, the IR plan's physical response procedures, securing
the site, escorting an intruder out, preserving the scene.

**Control 3, named accounts and lifecycle, four cells.**
Administrative Preventive, the joiner, mover and leaver process and the least privilege standard
are written policy. Technical Preventive, the account configuration and RBAC enforcement that
implement it. Administrative Detective, quarterly access recertification is a detective activity,
it finds accounts that should no longer exist. Administrative Compensating, during Phase 1 before
Control 1 provides a single deprovisioning point, manual access review compensates for the
absence of automated revocation.

**Control 7, IPS and flow detection, four cells.**
Technical Preventive, inline mode blocks the exploit before it lands. Technical Detective, flow
analytics alerts on behaviour no signature covers. Technical Corrective, an inline drop
terminates an in progress session, which is corrective action on live traffic rather than
prevention of a future event. Technical Compensating, virtual patching signatures compensate for
known unpatched branch software until Control 10 catches up, which is the textbook definition of
a compensating control.

**Control 18, third party assurance, four cells.**
Administrative Preventive, the assessment process and contractual requirements. Technical
Preventive, mutual TLS, certificate pinning, IP allow listing and broker validation.
Administrative Detective, the contractual right to audit and the reassessment cycle. Technical
Detective, transaction rate and value anomaly alerting.

**Control 6, Layer 2 baseline, three cells.**
Technical Preventive, 802.1X, port security and DHCP snooping stop the attack. Technical
Detective, violation counters and logged ARP inspection failures record attempts. Technical
Corrective, the violation shutdown action err disables the port, an automated corrective response
to an attack in progress rather than prevention of a future one.

**Control 10, patch management, three cells.** Administrative Preventive, the programme, SLAs and
exception register. Technical Preventive, the patches themselves. Administrative Detective,
monthly vulnerability scanning is a scheduled detective process that finds what needs patching.

**Control 13, EDR, three cells.** Technical Preventive, application allow listing blocks
execution. Technical Detective, EDR telemetry and alerting. Technical Corrective, automated
quarantine and rollback acts on a compromise already in progress.

**Control 14, awareness programme, three cells.** Administrative Preventive, training reduces the
chance of disclosure. Administrative Deterrent, a publicised reporting culture and measured
simulation programme deters the attacker, because attempts get reported and a campaign dies after
its first call rather than running through a staff list unimpeded. Administrative Compensating,
training compensates where no technical control can apply at all, which is the case for a
telephone call, there is no firewall for a phone.

**Control 2, MFA, two cells.** Technical Preventive is the primary placement. Technical
Compensating, because MFA is explicitly deployed to compensate for the password reuse and sharing
culture, which cannot be eliminated quickly. A second factor makes a shared password insufficient
while Controls 14 and 15 work on the underlying behaviour over a much longer timescale.

**Control 5, zoned architecture, two cells.** Technical Preventive, default deny between zones.
Technical Compensating, segmentation compensates for the unpatched branch systems. Northbridge
cannot patch them immediately, so containing them is what reduces the risk in the interim, the
same logic as Control 7's virtual patching applied at the network layer.

**Control 8, logging and SIEM, two cells.** Technical Detective is the obvious placement.
Technical Deterrent, because logging that staff and contractors know exists deters insider
misuse. This is why Control 9's banner states that activity is logged and monitored, a deterrent
requires that the subject knows about it, which is what makes it a deterrent rather than merely a
detective control.

**Control 9, management plane, two cells.** Technical Preventive, SSH only, VTY ACLs, timeouts
and throttling prevent access. Technical Deterrent, the legal banner is a deterrent in the strict
sense, it changes nothing technically, and exists to discourage and to establish that access was
unauthorised.

**Control 12, cryptographic standard, two cells.** Administrative Preventive, the standard
document specifying minimum algorithms, key lengths and rotation. Technical Preventive, the TLS,
IPsec and at rest encryption configurations that implement it.

**Control 15, policy set, two cells.** Administrative Preventive, the policies themselves.
Administrative Deterrent, the disciplinary consequences attached to breach, which are the only
lever available against deliberate password sharing once staff have been trained and still
choose to share.

### Note on the distribution

Technical Preventive is the most populated cell with thirteen controls, and the Physical column
the least. That reflects the brief rather than an oversight, since Northbridge already has
physical security capability and the plan adds only what it is missing. The Recovery row is the
thinnest, holding only Control 16, and splitting backups out as a separate control was considered
and deliberately rejected, for the reasons given in Section 6.

---

# 6. Control Minimisation Justification

*Written as prose, as the brief requires. No tables are used in this section.*

## The goal and the approach

The brief sets efficiency as an explicit design goal, asking that the plan minimise the total
number of distinct controls by preferring controls that address multiple threats over narrow
single purpose ones. This was treated as a constraint on the design, not a presentational
preference, and it changed the plan materially.

The first pass produced twenty six controls. It was built the obvious way, with each member
bringing the controls their own two threats needed. The result was inefficient in a recognisable
way. Because four people independently analysed eight threats in the same organisation, the same
underlying weakness appeared under several different names. Member 1 proposed abolishing the
shared VPN account, Member 4 proposed abolishing the shared server room key, and Member 2
proposed abolishing shared switch passwords. Those were three controls in the first draft. They
are one idea, stop using shared credentials, and in the final plan they are Control 3 and Control
17, because the first two are credentials and the third is a physical key.

Twenty six was reduced to eighteen over two passes.

## Controls chosen because they are broad

Control 8, centralised logging with SIEM, alerting and authenticated NTP, is the most efficient
control in the plan. It is the only control mapping to all eight threats. The reason is
structural rather than lucky. Every one of the eight chains contains a step whose success depends
on nobody noticing, because the brief states there is no centralised logging or audit trail
anywhere. A control supplying the missing observer therefore touches every chain at once.

The narrow alternative was explicit in the first draft, and can be priced exactly. Four separate
controls had been written, central log collection, a SIEM correlation and alerting capability,
NTP time synchronisation, and infrastructure configuration change logging. Keeping them separate
would have cost three extra controls for no analytical gain, because none of the four is useful
without the others. Log collection without correlation is a disk full of text nobody reads.
Correlation without synchronised time produces a pile of records rather than a timeline, which is
the point Member 4 argued, and the reason syslog and NTP were submitted as one configuration
rather than two.

Control 5, the zoned architecture, absorbed the largest number of first draft entries. The first
pass contained five separate controls which are the same control seen from five threat models,
DMZ isolation for the public portal from T5, internal segmentation between users and core banking
from T3, branch to branch containment from T3, guest Wi-Fi isolation from T4, and a partner
extranet zone from T6. Each member had correctly identified that their threat needed a boundary.
Nobody had noticed it was the same boundary programme. Consolidating cost nothing in coverage,
since the mapping table shows Control 5 addressing five threats, and removed four controls. It
also improved quality, because specifying the zones once as a complete set forced a decision about
how the zones relate to each other. Five separately authored segmentation controls would almost
certainly have contradicted each other about where guest Wi-Fi terminates.

Control 6, the Layer 2 baseline, was chosen as a single control over six narrow ones. The first
draft listed port security, DHCP snooping, Dynamic ARP Inspection, BPDU guard, 802.1X and unused
port hardening separately, which is how the labs teach them and how it is tempting to write them.
Specifying them as one baseline applied to every access switch at all seven sites removed five
controls. More importantly it reflects how the control is deployed and operated. Nobody rolls out
DHCP snooping to seven sites as one project and Dynamic ARP Inspection as another, and as
Configuration 6 shows, DAI does not even function without DHCP snooping's binding table. Two
features that cannot work apart are not two controls.

Control 15 and Control 16 each replaced a cluster. Control 15 absorbed six separately drafted
policies into one board approved set, removing five controls. Control 16 absorbed four, the
incident response plan, the disaster recovery plan, the backup programme and restoration testing,
removing three. In both cases the merge is justified by how the work is actually done. Policies
are approved, published and acknowledged as a set, and a disaster recovery plan whose backups
have never been restoration tested is not a plan, which is exactly the finding the brief records
about Northbridge today.

Control 7 was kept as one control despite being two technologies, and this was the most debated
merge. The argument for splitting was that signature based inline prevention and flow based
anomaly detection are different products, bought separately, with different deployment models.
The argument for merging, which won, is that they are a single detection capability with two
sensors. The IPS covers north south traffic crossing a boundary using known exploit signatures,
and the flow analytics covers east west traffic that never crosses a boundary using behavioural
baselines. Northbridge needs both to have detection coverage at all, and specifying them
separately would invite the organisation to buy one and defer the other, which given a board
making its first security capital request is a realistic risk. The merge also absorbed virtual
patching, which had been a seventh draft control.

## What was rejected in favour of a broader control

Three narrow controls were considered seriously and deliberately dropped rather than merged.

A dedicated VPN account management control was considered, because the shared account is the
single worst finding in the brief and there is a presentational argument for giving it its own
number. It was rejected because it would be a control defined by a symptom rather than a cause.
Member 1's own threat modelling made this argument, that T1 and T2 share one root cause. A control
aimed at the VPN account alone would leave the same weakness on every switch, router, server and
application, each with its own local accounts. Controls 1, 3 and 4 fix the cause, and the shared
VPN account disappears as a consequence.

A separate guest Wi-Fi security control was considered, since that is how most practitioner
checklists list it. It was rejected because everything it would contain is already Control 5,
guest terminating on the external firewall tier with no internal route, or Control 6, client
isolation, port security on the access point port, and DHCP snooping. A guest Wi-Fi control would
have been a cross reference wearing a control number.

Splitting backups out of Control 16 as a nineteenth control was considered, and this one is worth
recording because the incentive ran the other way. The Recovery row of the Function by Category
table holds only Control 16, and a separate backup control would have populated that row more
convincingly to a reader. The decision was that padding a table is not a reason to create a
control, and that the honest statement, that this plan has exactly one recovery control and it is
therefore load bearing, is more useful to Northbridge than a cosmetically fuller grid. The
thinness of that row is flagged explicitly instead.

## Where redundancy was kept deliberately

Minimisation is not elimination, and three overlaps were kept on purpose.

Controls 5 and 6 both address T4, and both were kept. This is the clearest deliberate redundancy
in the plan. Control 5's segmentation stops a guest on the guest VLAN attacking a staff
workstation, because they are no longer in the same broadcast domain. It does nothing against an
attacker already inside the staff segment, and the brief makes that realistic, recording branch
cabinets found unlocked in at least two locations and visitor sign in inconsistently enforced.
Someone who patches a laptop into a staff port is inside the segment, and segmentation has
nothing left to say. Control 6 is what defeats that attacker. The two look redundant on the
mapping table and are not redundant in the threat model, which is precisely the case where a
mapping table misleads and the prose has to carry the reasoning.

Controls 2 and 14 both address T7, and both were kept, because they act on different terms of the
risk equation. Control 14's training reduces the likelihood that a staff member discloses a
password. Control 2's MFA reduces the impact if they do, because a password alone stops being
sufficient. Neither substitutes for the other, since training will never reach 100 percent of 450
staff reliably, and MFA does not stop an attacker who talks a user through approving the second
factor. They were also both kept because of a timing argument Member 2 raised, that MFA can be
delivered in weeks while training takes a year to change behaviour. In the interim MFA is doing
the work alone, and after the interim training is what reduces the number of MFA prompts an
attacker gets to try.

Controls 7 and 11 overlap most awkwardly, and this is the redundancy the group is least
comfortable with. Control 7's inline IPS inspects traffic to the DMZ with web and database
protection signatures. Control 11's web application firewall inspects the same traffic with
application specific rules. Both would block a straightforward injection payload against the
portal, so a reviewer could reasonably say Northbridge is paying twice. Both were kept for two
reasons, and the cost is accepted. First, they fail differently. An IPS matches known attack
signatures, while a WAF understands the application's expected input structure and can block a
novel payload no signature covers. Second, Control 7's IPS is procured as part of the firewall
tiers in Phase 2, and Control 11's WAF sits in the DMZ in front of the portal, so the overlap buys
defence in depth on the one asset the brief identifies as both the most critical and the most
exposed. If budget forced a cut, the WAF stays and the IPS's web signature set is what would be
narrowed, because T5 is an application attack and the WAF is the control shaped for it.

## What minimisation cost

One honest consequence is that several of the eighteen controls are large. Control 15 is six
policies, Control 6 is a baseline containing six switch features, and Control 16 is four distinct
programmes of work. Expressed as projects rather than controls, the plan is bigger than eighteen
items suggests, and a reader who mistakes control count for implementation effort will
underestimate it. That was judged the right trade, since the brief asks for a minimal set of
controls that each address multiple threats, and grouping work that is genuinely delivered
together is more honest than inflating the count to look granular. The phasing section exists to
make the real sequence and effort visible, because the control list alone does not.
