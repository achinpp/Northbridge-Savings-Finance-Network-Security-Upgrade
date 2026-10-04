# IE3122: Network Security, Group Assignment

## Northbridge Savings & Finance, Network Security Upgrade

Department of Computer Systems Engineering, Faculty of Computing
Sri Lanka Institute of Information Technology
Year 3 Semester 1, 2026

### Group members and individual responsibility

| | Name | IT Number | Threats | Technology proposals | Configurations |
|---|---|---|---|---|---|
| 1 | [Member 1 Full Name] | [IT Number] | T1, T2 | A1.1 to A1.4 | 1, 2 |
| 2 | [Member 2 Full Name] | [IT Number] | T3, T4 | A2.1 to A2.4 | 3, 4 |
| 3 | [Member 3 Full Name] | [IT Number] | T5, T6 | A3.1 to A3.4 | 5, 6 |
| 4 | [Member 4 Full Name] | [IT Number] | T7, T8 | A4.1 to A4.4 | 7, 8 |

| Member | Theme | Threats modelled | Configurations built |
|---|---|---|---|
| 1 | Identity and remote access | T1 shared VPN account, T2 credential abuse | 1 AAA with TACACS+ and RADIUS (plan linked), 2 SSH and management plane hardening |
| 2 | Segmentation and Layer 2 | T3 ransomware propagation, T4 rogue DHCP and ARP spoofing | 3 VLAN segmentation with inter VLAN ACLs (plan linked), 4 switchport port security |
| 3 | Perimeter, application, third party | T5 SQL injection, T6 payment processor abuse | 5 internet edge firewall (plan linked), 6 DHCP snooping and Dynamic ARP Inspection |
| 4 | Human, physical, resilience | T7 vishing, T8 physical compromise | 7 NetFlow export (plan linked), 8 centralised syslog and NTP |

### Group technology selections

| Area | Adopted solution | Proposed by |
|---|---|---|
| VPN | Cisco Secure Client IKEv2/IPsec on a Secure Firewall pair, per user certificate, MFA, posture | Member 1 |
| AAA | Cisco ISE, RADIUS for network access, TACACS+ for device administration | Member 1 |
| Network architecture | Dual firewall DMZ sandwich, partner extranet, integration broker, out of band management | Member 3 |
| IDS/IPS | Inline IPS at zone boundaries, plus flow based detection from existing switch NetFlow | Member 4 |

### Declaration

We declare that this report is our own work. The individual threat models, technology proposals
and hardening configurations attributed above were produced independently by the named member
before group discussion, as the brief requires. The combined plan, the classification tables,
the minimisation justification and the comparative evaluation are joint work.

Facts about Northbridge come from the IE3122 assignment brief. Risk ratings, control selections
and recommendations are our own analysis.

| Member | Signature | Date |
|---|---|---|
| [Member 1 Full Name] | | |
| [Member 2 Full Name] | | |
| [Member 3 Full Name] | | |
| [Member 4 Full Name] | | |

All four members confirm attendance at the scheduled viva.

---

# 1. Executive Summary

Northbridge Savings & Finance commissioned this review before its integration with two payment
processors proceeds. The report contains eight individually modelled threats, a combined plan of
eighteen controls, four technology recommendations chosen by comparative evaluation, and eight
hardening configurations built and evidenced in Cisco Packet Tracer.

## The headline finding

All eight threats fall in the critical band. This is not score inflation, it is the arithmetic
result of an organisation with no dedicated firewall, no intrusion detection, no multi factor
authentication, no central authentication, no central logging, no patch process, no
segmentation, no awareness training, and no tested backups. For six of the eight threats, there
is no control in place that the attack chain must defeat at any point.

We did differentiate inside the band. Scores run from 15 to 25, and three likelihood ratings
were held at 3 or 4 rather than inflated.

| Threat | Summary | Score |
|---|---|---|
| T1 | Shared VPN account used by all remote staff and both contractors, no MFA, no accountability | 25 Critical |
| T3 | Ransomware spreading from one unpatched branch workstation across the flat network | 25 Critical |
| T5 | SQL injection against the public banking portal, which shares trust space with the database | 20 Critical |

T3 carries particular weight. The brief records that a regional industry association observed
this exact pattern, a single compromised branch workstation spreading rapidly across an
unsegmented network, several times against Northbridge's peer group in the past year.

## The response

Eighteen controls, reduced from an initial twenty six by preferring controls that address
several threats over narrow single purpose ones. No threat depends on one control. Each must
defeat a preventive control, evade a detective control, and survive a recovery control before
it causes lasting harm.

The most efficient single control is centralised logging with authenticated time
synchronisation. It maps to all eight threats, because every chain contains a step whose success
depends on nobody noticing.

## The deadline that shapes the plan

The payment processor integration goes live within two quarters, and the brief states the CTO
commissioned this review before it proceeds. That sequencing should be held to.

Threat T6 carries the lowest likelihood in the report, because the integration is not yet live.
On go live day that score rises, and the cost of retrofitting a partner zone, mutual TLS, input
validation and a vendor assessment process rises with it. Phase 1 must therefore complete first.

## Two actions to start immediately

Both are cheap, need no procurement, and together they remove the report's only non recoverable
outcome.

1. Auditable badge access and a camera on the head office server room. Northbridge already buys
   cameras, for branch cash handling, but not for the room holding the customer database.
2. One successful restoration test of the core banking database from an offline copy. Backups
   exist but have never been restored, so they are a hypothesis, not a control.

Threat T8 scores impact 5 because physical intrusion and unverified backups compound. One visit
could destroy the primary systems and their only copies. With these two actions complete, that
impact falls to 3 and T8 leaves the critical band.

## On the practical work

Eight configurations were built and verified, with screenshot evidence of commands and
verification output.

Two required substitution. Packet Tracer 8.2 on the ISR 2911 implements no stateful firewall and
no cryptography. The commands `zone security`, `ip inspect`, reflexive ACLs and `crypto` are all
rejected on the keyword itself, and the `securityk9` package has no activation path. This was
established by direct test, not assumed, and the rejections are evidenced in Section 8. The
zone based firewall became a NAT and edge ACL perimeter firewall, and the IPsec VPN became
NetFlow export, which implements the flow based half of the adopted IDS/IPS recommendation.

Both original designs stand as recommendations. Control 12, the cryptographic standard for data
in transit, therefore has no implementing configuration. It is recorded in the plan as the one
control with no implementation evidence behind it.

---

# 2. Scope, Method and Context

## 2.1 Scope

This review covers Northbridge's network and information security posture across its head office
and branch estate, as described in the brief. Out of scope: source code review, formal
penetration testing, physical site survey, vendor pricing, and procurement. Where the plan
recommends these, they are recommendations, not activities performed here.

## 2.2 Risk rating method

All four members used the same method, agreed before individual work began, so the eight scores
would be comparable at reconciliation.

Risk = Likelihood x Impact, each scored 1 to 5.

| Score | Band |
|---|---|
| 1 to 4 | Low |
| 5 to 9 | Medium |
| 10 to 14 | High |
| 15 to 25 | Critical |

Likelihood is assessed against Northbridge as it stands today, with no compensating controls
assumed, because the brief describes the current state as having none. This is the most
important methodological choice in the report. A threat is not rated on how likely it would be
at a well defended bank, but on how likely it is here.

Impact is assessed on the asset actually reached, not the worst imaginable consequence. Where
severe outcomes arise from a follow on threat, impact is scored on the immediate consequence and
the escalation is noted. This avoids counting the same harm several times. Member 4's T7 is the
clearest case, its direct impact is one compromised account, scored 4, while its significance is
that it supplies the credential three other threats depend on.

## 2.3 The organisation

Northbridge is a mid sized regional financial services provider offering personal banking, small
business loans and digital payment services. It runs a head office and six branches, employing
around 450 staff. Core banking and the customer database are hosted on premises at head office,
alongside an online banking portal and mobile app exposed to the internet. Branches connect over
dedicated links. Remote staff and two external IT contractors need regular remote access.
Integration with two payment processors goes live within two quarters.

## 2.4 Key assets

| Asset | Why it matters |
|---|---|
| Customer financial and personal data | Named in the brief as the most critical asset, with direct financial and regulatory consequences |
| Online banking portal and mobile app | Give customers direct account access, and are the only systems deliberately reachable from the internet |
| Branch to head office connectivity | Core banking availability depends on it through the business day |
| Internal email and staff credentials | Credentials are a hinge asset, compromising them yields the others |
| Payment processor integrations | Will shortly become a critical dependency, extending trust outside Northbridge for the first time |
| Regulatory standing and reputation | The brief states the ability to operate depends as much on confidence as on any system staying online |

## 2.5 Why Northbridge is in this position

Security investment has gone almost entirely into physical measures, vaults, alarms and branch
cameras, rather than IT. The network grew organically over more than a decade with no
segmentation strategy.

That history matters for how the recommendations read. This is not a careless organisation, it
is one that spent its budget on the risks it could see. The plan's physical controls are
deliberately modest for that reason. Control 17 largely asks Northbridge to apply existing
competence to the server room, rather than build a capability from nothing.

## 2.6 The two events that prompted the review

1. A regional industry association reported a sharp rise in ransomware against mid sized
   financial firms, several beginning with one compromised branch workstation and spreading
   across an unsegmented network.
2. A staff member received a call from someone claiming to be IT Helpdesk, urgently requesting
   their password. The employee grew suspicious and did not comply. The attempt was logged, with
   no process to escalate it, warn others, or rotate the credential being sought.

Both appear in the threat models, as T3 and T7. Neither is hypothetical.

## 2.7 Current weaknesses

**Technical.** No MFA anywhere. A single shared VPN account for all remote staff and both
contractors. No meaningful segmentation, so guest Wi-Fi, branch systems and core banking sit
within reach of each other. No IDS or IPS. No patch management, with several branch systems
running outdated software. No central logging or audit trail. No central authentication, every
device and application holds its own local accounts.

**Physical.** The server room is secured by a single shared key, with no camera coverage.
Visitor sign ins are inconsistently enforced. No site has signage, badge checking or cameras at
entry points. Network cabinets were found unlocked in at least two branches.

**Administrative.** No data classification policy. No vendor security assessment process. Work
from home and personal devices are permitted with no guidance. Password reuse and sharing are
common among branch staff. Backups exist but have never been restored. No documented disaster
recovery or incident response plan. No security awareness training at all.
