# 4. Combined Layered Security Plan

## 4.1 Reconciliation

The brief requires the eight threats to be genuinely reconciled, with overlaps merged and
contradictions resolved, rather than listed one after another. This section records that work,
because the control list is a product of it.

### Overlaps merged

**T1 and T2 share one root cause.** Both reduce to the absence of a central identity and
accounting authority. T1 is that absence exploited remotely, T2 the same absence exploited
internally. They are treated as one remediation programme, Controls 1 to 4, which is why there
is no separate VPN account management control.

**T5's pivot and T3's lateral movement are the same mechanism.** T5 escalates from a compromised
web tier into the flat network, T3 propagates from a compromised branch workstation into the
same flat network. The entry point differs, everything after it is identical. Control 5 carries
both, so there are no separate DMZ isolation and internal segmentation controls.

**T4's physical entry and T8's branch exposure are one finding.** Both rely on unlocked branch
cabinets and unenforced visitor sign in. Control 17 covers the physical dimension for both,
Control 6 the Layer 2 consequence.

**T7 is an input to T1, T2 and T3, not a parallel threat.** A vished credential supplies the
shared VPN compromise, the credential replay chain, and the ransomware foothold. Control 14 is
therefore treated as a likelihood reducing control across four threats, and Control 2 is what
caps T7's impact.

**The detection gap is common to six threats.** T1 to T6 each contain a step whose success
depends on nobody noticing. Controls 7 and 8 are specified once and mapped against all six.

### Contradictions resolved

Four genuine disagreements surfaced between members' proposals. Recording them matters, because
the brief asks for contradictions resolved rather than smoothed over.

**1. Is the detection control preventive or detective?** Member 2 proposed open source sensors
in detection mode internally, arguing commercial inline subscriptions across seven sites were
unaffordable. Member 4 argued that Member 2's own T3 contains the phrase "spread rapidly", that
Northbridge has no 24 hour operations capability, and that a control nobody is awake to read is
not a control.

*Resolved in favour of prevention.* Member 2's own threat model is the strongest evidence
against Member 2's proposal, since the plan cannot rate T3 at likelihood 5 and then rely on a
morning shift analyst. Control 7 is inline prevention plus flow based detection, which is Member
4's design. Member 2's cost objection was accepted as valid, and is answered by the phasing in
Section 4.4 rather than by weakening the control.

**2. Commercial or open source AAA?** Members 1 and 4 proposed commercial platforms, Member 3 an
open source stack, arguing against concentrating all access decisions in one appliance pair at
an organisation whose backups have never been restored. Member 2 proposed the fastest option,
which has no TACACS+ at all.

*Resolved in favour of a commercial platform, with Member 3's objection accepted as a design
requirement rather than rejected.* Control 1 explicitly requires a redundant pair, a documented
and tested rebuild procedure, and local fallback credentials on every device. That last point is
why Member 1's Configuration 1 was built with `group tacacs+ local` and includes a fallback
test. Member 2's objection that MFA is needed in weeks was also accepted, and is answered by
splitting Control 2 out as a separate control deliverable in Phase 1.

**3. How many firewalls?** Member 2 proposed a single cluster plus distribution layer ACLs,
arguing a team with no firewall experience is more likely to misconfigure four firewalls than be
defeated through two. Members 1, 3 and 4 proposed two tiers.

*Resolved in favour of two tiers.* The brief requires multiple firewalls, and Member 2
acknowledged this was the weakest point of their proposal. Member 2's operational risk argument
was accepted in a specific form, Control 5 requires the internal tier to carry a deliberately
small and static rule set, so the device needing most care needs least change.

**4. Replace the VPN or modernise it?** Member 4 proposed replacing network level VPN with ZTNA,
arguing that placing a user on the network is meaningless while the network is flat. Members 1,
2 and 3 proposed conventional VPNs.

*Resolved in favour of a conventional VPN now, with ZTNA as a phase 3 item.* Member 4's argument
is correct about today's flat network, but self defeating once Control 5 exists, since ZTNA's
advantage shrinks as segmentation improves. Member 4 also raised the counter argument
themselves, that routing a regulated bank's authentication through an unassessed third party
broker is exactly the risk T6 identifies as critical. The group agreed an organisation with no
vendor assessment process should not make a vendor its authentication path.

### Gaps no threat covered

Three brief weaknesses are not the primary subject of any threat model. No patch process
appears as a vulnerability inside T3 and T5, and warrants its own control, Control 10. BYOD and
work from home appear inside T2 and T7's attack surface, covered by Controls 13 and 15. No data
classification policy appears as an impact amplifier in T5 and T8, covered by Controls 12 and
15. Controls were added for these rather than retrofitting threats to justify them, because
inventing threats after the fact would misrepresent the individual work.

## 4.2 Master control list

Eighteen controls, reduced from twenty six. Where a control is implemented by one of the eight
Packet Tracer configurations, that is noted.

| # | Control | Summary | Built by |
|---|---|---|---|
| 1 | Centralised AAA | Redundant policy servers, RADIUS for network access, TACACS+ with per command authorisation and accounting for device administration, federated to the existing directory, all records to Control 8, local fallback on every device | Config 1 |
| 2 | Multi factor authentication | On remote access, all administrative and privileged accounts, webmail, and the portal's staff interface. Specified separately from Control 1 so it can land in weeks, not quarters | |
| 3 | Named accounts and lifecycle | Abolition of every shared and generic account, role based least privilege, just in time elevation replacing standing privilege, documented joiner, mover and leaver process, quarterly recertification | Config 1 (part) |
| 4 | Enterprise remote access VPN | Per user authentication against Control 1, per user certificates, MFA, posture assessment before internal zones are reachable, separate pools and policy for staff, contractors and administrators | |
| 5 | Zoned architecture, two firewall tiers | Zones OUTSIDE, DMZ, PARTNER-EXTRANET, INTEGRATION-BROKER, CORE-BANKING, INTERNAL-USERS, GUEST, MGMT-OOB. Default deny with explicit owned allow rules. Internal tier carries a small static rule set. Per branch VLAN sets. Guest terminates on the external tier with no internal route | Configs 3, 5 |
| 6 | Layer 2 hardening baseline | One standard applied to every access switch at all seven sites: 802.1X fed by Control 1, port security with per role violation actions, DHCP snooping, Dynamic ARP Inspection with ARP ACLs for static servers, BPDU guard, unused ports shut and parked, native VLAN moved off VLAN 1, DTP disabled | Configs 4, 6 |
| 7 | Inline IPS and flow based detection | Signature IPS in prevention mode at the internet edge and the internal tier, with a 30 day detection only burn in, and virtual patching for known branch CVEs. Plus NetFlow from existing switches and routers at all seven sites, baselining normal behaviour and alerting on deviation | Config 7 (flow half) |
| 8 | Central logging, SIEM, NTP | All device, server, application, firewall, IPS and AAA logs to one platform with defined retention. Authenticated NTP so records can be ordered. Defined severities, escalation path, named on call responsibility | Config 8 |
| 9 | Secure management plane | SSH only with Telnet disabled, out of band management network reachable only from a hardened jump host, VTY access restricted by ACL, idle timeouts, brute force throttling, legal banners, TACACS+ command authorisation | Config 2 |
| 10 | Patch and vulnerability management | Asset inventory, monthly authenticated scanning, severity based SLAs, an emergency path for actively exploited vulnerabilities, explicit remediation of outdated branch software, time bound risk accepted exceptions | |
| 11 | Web application protection | WAF in front of the portal and mobile API, secure development lifecycle with mandatory code review and parameterised queries, pre release testing, annual independent penetration test, least privilege database accounts | |
| 12 | Cryptographic standard | TLS 1.2 minimum for customer facing and internal web traffic, IPsec with AES-256, SHA-256 and DH group 14 or better for branch links and the partner integration, encryption at rest for the database, its backups and endpoint disks, certificates preferred over pre shared keys | None, see note |
| 13 | Endpoint protection and BYOD baseline | Managed EDR on all owned endpoints and servers, application allow listing on branch workstations and point of service equipment, a defined minimum baseline for personal devices enforced by Control 4's posture check | |
| 14 | Awareness and anti social engineering | Mandatory induction and annual refresher for all 450 staff with role specific branch content, simulated phishing and vishing with measured outcomes, a published rule that IT will never request a password, a verified callback procedure, one publicised reporting route, recognition for reporting rather than blame | |
| 15 | Information security policy set | Data classification and handling, acceptable use, credential policy prohibiting sharing and reuse with a password manager provided, BYOD and work from home, third party and vendor security, physical security. Board approved, published, acknowledged, reviewed annually | |
| 16 | Incident response, disaster recovery, tested backups | Documented IR plan with roles, severity classification, escalation and notification paths including regulator and partner, and named authority to sever the partner connection. Documented DR plan with agreed RTO and RPO. At least one immutable or offline backup copy held away from the primary site, with mandatory quarterly restoration testing and documented evidence. Both plans exercised annually | |
| 17 | Physical security upgrade | Auditable individual badge access replacing the shared server room key, with access log and out of hours alerting. Cameras on the server room and entry points at all seven sites. Lockable, locked branch cabinets with individually issued keys. Enforced visitor sign in with escort. Visible signage. Backup media removed from the server room | |
| 18 | Third party and partner assurance | Vendor assessment of both processors and both IT contractors before go live, with questionnaire, evidence of certification or independent audit, and documented risk acceptance by a named owner. Contractual breach notification timeframes and right to audit. Mutual TLS with certificate pinning, IP allow listing, partner traffic terminating in PARTNER-EXTRANET and reaching the core only through the validating broker, input validation on every partner message, transaction rate and value anomaly alerting | Config 5 (part) |

**Note on Control 12.** No Packet Tracer configuration demonstrates this control. The platform
used for the practical work has no cryptographic feature set, `crypto isakmp` is absent from the
parser and `securityk9` cannot be activated, as evidenced in Section 6.4. The control stands as
a recommendation. It is recorded here as the one control in the plan with no implementation
evidence behind it.

## 4.3 Residual risk

| Threat | Before | After | What remains |
|---|---|---|---|
| T1 | 25 Critical | 4 Low | Compromise of one account with MFA bypass, now detectable and attributable |
| T2 | 20 Critical | 4 Low | Insider abuse within authorised role, now fully audited by command accounting |
| T3 | 25 Critical | 8 Medium | Foothold still possible, propagation contained to one branch VLAN, detected by flow analysis, recovery proven by tested backups |
| T4 | 16 Critical | 4 Low | An attacker on a segment is isolated to it, and blocked by DAI and port security |
| T5 | 20 Critical | 8 Medium | An application flaw may still exist, WAF, DMZ isolation and least privilege database accounts cap the outcome |
| T6 | 15 Critical | 6 Medium | Partner compromise remains outside Northbridge's control, broker validation and anomaly alerting cap the outcome |
| T7 | 20 Critical | 6 Medium | Humans remain targetable, MFA caps the value of a disclosed password, training reduces the disclosure rate |
| T8 | 15 Critical | 4 Low | Physical intrusion still possible, now deterred, detected, attributable, and survivable through tested offline backups |

No threat reduces to zero, and none is claimed to. T3, T5, T6 and T7 remain Medium because each
depends on something Northbridge cannot fully control: a user clicking, an undiscovered
application flaw, a partner's own security, or human susceptibility to persuasion.

## 4.4 Implementation phasing

Phasing is driven by the integration go live deadline, and by T6's argument that retrofitting
partner controls becomes sharply more expensive once the partners have built against whatever
Northbridge shipped.

**Phase 1, before the integration, weeks 1 to 12.** Controls 2, 3, 5, 9, 16, 17 and 18. Controls
16 and 17 come first because they are the cheapest in the plan and they take T8 out of the
critical band on their own.

**Phase 2, consolidation, quarters 2 to 3.** Controls 1, 4, 6, 7, 8, 10, 11, 14 and 15.

**Phase 3, maturity, quarter 4 onward.** Control 12 at rest encryption, Control 13 EDR and BYOD
baseline, 802.1X enforcement after a monitor mode period, plus the micro segmentation and ZTNA
items held over from Members 3 and 4.

One sequencing dependency is worth stating, because getting it wrong is how organisations lock
themselves out. **Control 9 must precede Control 1.** Putting individual administrator
credentials onto a management plane still running Telnet would broadcast those credentials in
plaintext, making the identity control worse than useless. This is why Member 1's two
configurations were designed as a pair, and why the free choice one is the prerequisite for the
plan linked one.

## 4.5 A gap the practical work exposed

Controls 1, 2, 3 and 9 all specify every router, switch and firewall. The build demonstrates
them on `HQ-R1` only. During Configuration 7's branch test, `BR1-R1` was found to have no
authentication at all, `enable` returns a privileged prompt with no password, no AAA, no VTY
access class and no banner.

That is not a defect in the configurations, it is the controls not yet having been rolled out
estate wide. It is recorded because the branch is the worst place for it to be true. The brief
states branch cabinets were found unlocked and visitor sign in is inconsistently enforced, so
the device with no authentication sits at the site with the weakest physical control, which is
the compound exposure T2 and T8 describe.

It also illustrates why Control 1 specifies a central authority rather than per device accounts.
With local credentials, hardening seven sites is seven separate pieces of work that can each be
forgotten. With a central platform, a device either enrols or it does not, and those that have
not are visible in one place. Remediation is Member 1's Configurations 1 and 2 applied to the
remaining four devices as a Phase 2 task, with an enrolment checklist per device.
