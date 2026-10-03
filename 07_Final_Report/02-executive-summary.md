# 1. Executive Summary

Northbridge Savings & Finance commissioned this security review before its integration with two
third-party payment processors proceeds. This report presents eight individually modelled
threats, a combined layered security plan of eighteen controls, four technology recommendations
selected by comparative evaluation, and eight network hardening configurations implemented and
evidenced on a representative Cisco Packet Tracer topology.

## The headline finding

**All eight modelled threats fall in the critical band.** That is not score inflation. It is the
arithmetic consequence of an organisation that currently has no dedicated firewall, no
intrusion detection, no multi-factor authentication, no centralised authentication, no
centralised logging, no patch management process, no network segmentation, no security
awareness training, no incident response plan and no tested backups. For six of the eight
threats, there is no control in place that the attack chain would have to defeat at any point.

The three highest-rated risks:

| | Threat | Score |
|---|---|---|
| **T1** | Compromise of the single shared VPN account used by all remote staff and both external contractors, with no MFA and no individual accountability | **25 — Critical** |
| **T3** | Ransomware propagating from one unpatched branch workstation across the flat network to the core banking database | **25 — Critical** |
| **T5** | SQL injection against the internet-facing online banking portal, which sits in the same trust space as the database it queries | **20 — Critical** |

T3 deserves particular weight: the brief records that a regional industry association observed
this exact pattern — a single compromised branch workstation spreading rapidly across an
unsegmented network — several times against Northbridge's own peer group within the past year.
Northbridge has every precondition present simultaneously.

## The response

**Eighteen controls**, reduced from an initial twenty-six by deliberately preferring controls
that address multiple threats over narrow single-purpose ones. No threat depends on a single
control: each must defeat a preventive control, evade a detective control, and survive a
recovery control before it causes lasting harm.

The single most efficient control is **centralised logging with authenticated time
synchronisation**, which maps to all eight threats — because every one of the eight attack
chains contains a step whose success depends on nobody noticing.

## Technology recommendations

| Area | Adopted | Proposed by |
|---|---|---|
| VPN | Cisco Secure Client (AnyConnect) IKEv2/IPsec on a Cisco Secure Firewall pair, per-user certificate + MFA + posture assessment | Member 1 |
| AAA | Cisco ISE — RADIUS for network access, TACACS+ with per-command accounting for device administration | Member 1 |
| Network architecture | Dual-firewall DMZ sandwich with a dedicated partner extranet, a validating integration broker, and an out-of-band management network | Member 3 |
| IDS/IPS | Inline IPS at zone boundaries **plus** flow-based behavioural detection from NetFlow exported by existing switches and routers | Member 4 |

Each selection was made by scoring all four members' proposals against criteria agreed before
the proposals were re-read, and each records specifically why the other three lost.

## The deadline that shapes everything

The payment processor integration goes live within two quarters, and the brief states the CTO
commissioned this review *before the integration proceeds*. That sequencing is correct and
should be held to.

Member 3's threat model T6 carries the lowest likelihood score in this report — the integration
is not yet live, so there is nothing to abuse. But on the day it goes live that score rises,
and the cost of retrofitting a partner zone, mutual TLS, input validation and a vendor
assessment process rises sharply with it, because by then the partners will have built against
whatever Northbridge shipped.

**Phase 1 must therefore complete before go-live**: MFA on remote access, abolition of the
shared VPN account, the zoned architecture including the partner extranet, the secure
management plane, backup restoration testing, the incident response plan, server-room access
control, and vendor assessment of both payment processors.

## Two actions that should start immediately

They require no procurement, no architecture decision and no budget approval of consequence,
and together they remove the report's most severe non-recoverable outcome:

1. **Auditable badge access and camera coverage on the head-office server room.** The brief
   notes Northbridge already invests in cameras — for branch cash handling, but not for the
   room containing the customer database. One door reader and one camera.
2. **One successful restoration test of the core banking database from an offline copy.**
   Backups exist but have never been test-restored, which means they are a hypothesis rather
   than a control.

Threat T8's impact rating is 5 specifically because physical intrusion and unverified backups
compound: a single visit could destroy both the primary systems and their only copies. With
those two actions complete, T8's impact drops to 3 and it leaves the critical band entirely.

They are also the two cheapest items in the entire plan.

## On the practical work

The eight hardening configurations were implemented and verified on a working topology, with
ninety screenshots of commands and verification output.

Two configurations required substitution. Packet Tracer 8.2 on the ISR 2911 implements no
stateful firewall and no cryptography — `zone security`, `ip inspect`, reflexive ACLs and
`crypto` are all absent from the command parser, and the `securityk9` technology package has no
activation path. This was established by direct test rather than assumed, and is evidenced in
the report. The Zone-Based Policy Firewall became a NAT and edge-ACL perimeter firewall; the
site-to-site IPsec VPN became NetFlow export, which implements the flow-based half of the
group's adopted IDS/IPS recommendation.

Both original designs stand as recommendations. **Control 12, the cryptographic standard for
data in transit, consequently has no implementing configuration**, and is recorded in the plan
as the one control with no implementation evidence behind it.
