# 9. Topology Used for the Practical Work

A representative cut of Northbridge's estate, head office plus one branch, since one branch
demonstrates every control.

**Devices.** `HQ-R1` and `BR1-R1` are ISR 2911 routers. `HQ-SW1`, `MGMT-SW1` and `BR1-SW1` are
2960 switches, required rather than 2950 because DHCP snooping and Dynamic ARP Inspection are
needed. `ISP-R1` is a 1941 simulating the internet. Five servers, `CORE-DB`, `CORE-APP`,
`WEB-PORTAL`, `AAA-SRV` and `SYSLOG-SRV`, plus seven PCs covering staff, guest, management,
branch and an external attacker. Eighteen devices, seventeen cables.

![The Packet Tracer topology as built. Head office left and centre, the out of band management segment lower left, and Branch 1 on the right. Dashed links are cross over cables, solid links straight through.](06_Topology/topology-diagram.png)

**Zones and addressing.**

| VLAN | Name | Subnet | Gateway | Ports on HQ-SW1 |
|---|---|---|---|---|
| 10 | STAFF-HQ | 10.10.10.0/24 | 10.10.10.1 | Fa0/1 to Fa0/4 |
| 20 | CORE-BANKING | 10.10.20.0/24 | 10.10.20.1 | Fa0/5 to Fa0/8 |
| 30 | DMZ | 10.10.30.0/24 | 10.10.30.1 | Fa0/9 |
| 40 | GUEST | 10.10.40.0/24 | 10.10.40.1 | Fa0/10 |
| 99 | MGMT-OOB | 10.10.99.0/24 | 10.10.99.1 | Fa0/11, Fa0/12 |
| 999 | BLACKHOLE-UNUSED | none | none | Fa0/13 to Fa0/24 and Gi0/2, all shut |

Branch VLANs are 110 for staff on 192.168.1.0/24 and 140 for guest on 192.168.14.0/24.
Per branch VLAN sets are deliberate, implementing Member 2's branch containment argument.

`HQ-R1` uses router on a stick, one trunk carrying five subinterfaces. `Loopback0` at
10.10.1.1/32 is the permanent management identity. The WAN link to the branch is 10.10.255.0/30,
and the ISP link is 203.0.113.0/30. Switch management uses SVIs, `HQ-SW1` on VLAN 99 at
10.10.99.2, `MGMT-SW1` at 10.10.99.3, `BR1-SW1` on VLAN 110 at 192.168.1.2, each with
`ip default-gateway`. This was initially missed, and nothing on the switches could send NTP or
syslog until it was added.

**Platform constraint.** Packet Tracer 8.2 on the ISR 2911, running `C2900-UNIVERSALK9-M
15.1(4)M4`, implements no stateful firewall and no cryptography. `zone security`, `ip inspect`,
reflexive ACLs and `crypto` are all rejected on the keyword itself, and `license ?` in
configuration mode offers only `boot`, so `securityk9` has no activation path. This was verified
by direct test and required the substitutions described in Sections 7.3 and 7.4.

**Build order.** Devices and cabling, then VLANs, trunks, subinterfaces, routing and DHCP, then
full end to end reachability verified and saved as a baseline. Only then were the security
configurations applied, so that a later failed test is unambiguous. Configuration 2 precedes
Configuration 1, and Configuration 6 precedes Configuration 5, so the snooping binding table
builds while reachability is still unrestricted.

---

# Appendix A. Individual Technology Proposals

Sixteen proposals, four areas by four members, each reasoned independently before any group
discussion as the brief requires. Each names a credible alternative that was seriously
considered, and why it was rejected for a Northbridge specific reason. The group's comparative
evaluation is in Section 8.

## A1. Member 1

**A1.1 VPN. Selected: Cisco Secure Client IKEv2/IPsec on a redundant Cisco Secure Firewall pair.**
Per user X.509 certificates plus password plus a second factor, authentication delegated to the
central AAA service over RADIUS so the VPN holds no local account store, posture assessment before
the tunnel reaches internal zones, and per group tunnel policy so a contractor's session reaches
only the systems they support. Considered: clientless SSL portal, FortiGate, WireGuard.

*Rejected alternative: clientless SSL WebVPN.* Genuinely attractive for the two external
contractors, since it needs no software on devices Northbridge does not own. Rejected on a
specific brief detail: the contractors need access to internal systems, not to a web application,
and clientless proxies browser protocols well while SSH, RDP and database tooling are exactly what
IT support needs and exactly what it handles worst. More decisively, clientless cannot perform
posture assessment, and these are the two parties whose devices Northbridge has least visibility
of, since no vendor assessment process exists. Dropping posture for the highest uncertainty
devices inverts the risk priority.

**A1.2 AAA. Selected: Cisco ISE as central AAA and network access control.** Redundant pair,
federated to the existing directory rather than becoming a new account store. RADIUS for all
network access, TACACS+ with per command authorisation and accounting for every network device,
802.1X with dynamic VLAN and dACL assignment, profiling and posture, all records to the SIEM.
Considered: Microsoft NPS with Entra MFA, FreeRADIUS, Aruba ClearPass.

*Rejected alternative: Microsoft NPS with the Entra MFA extension.* A serious candidate, cheap,
familiar, reusing existing directory accounts, and able to deliver MFA on the VPN quickly, which
is the most urgent fix in T1. Rejected because of what T2 needs rather than what T1 needs. NPS
speaks RADIUS only and has no TACACS+, which is the control producing a per administrator record
of every command typed on a device. T2's central finding is that Northbridge cannot attribute
privileged action to a person, and NPS cannot fix that for infrastructure, leaving network devices
on shared local enable passwords. Choosing NPS solves the loud problem and leaves the audit
finding.

**A1.3 Architecture. Selected: three tier zone based design using two firewall layers.** Internet
edge pair carrying OUTSIDE, DMZ-PUBLIC, PARTNER-EXTRANET and GUEST; internal pair separating
INTERNAL-USERS from CORE-BANKING; MGMT-OOB reachable only from a jump host. Default deny between
all zones, every allow rule carrying an owner and a review date. Considered: single collapsed
NGFW, heterogeneous sandwich, host based micro segmentation.

*Rejected alternative: a single collapsed NGFW with several DMZ interfaces.* The option most mid
sized organisations buy, and for a team with no firewall experience the simplicity is a real
safety benefit. Rejected on two grounds. The brief explicitly requires multiple firewalls. More
substantively, the brief's lead ransomware scenario starts inside the perimeter, and a collapsed
design puts the internal user LAN and core banking on two legs of one device, so the policy engine
that must stop internal lateral movement is also the device exposed to the internet. Two tiers
means the internal boundary survives a failure of the external one.

**A1.4 IDS/IPS. Selected: inline IPS enforced on both firewall tiers.** Prevention mode at the
edge for DMZ traffic and on the internal tier for core banking traffic, a 30 day detection only
burn in measured against real traffic before blocking, virtual patching for the known CVEs on
outdated branch software, all events to the SIEM. Considered: open source Snort on SPAN, Suricata
with Zeek, flow based detection.

*Rejected alternative: open source Snort 3 on SPAN ports.* Expected to be the choice on cost
grounds, free, using the same detection engine. Rejected for two reasons rooted in Northbridge's
shape. With six branches, a SPAN design needs a sensor, a SPAN session and a management path at
every site, seven deployments to patch at an organisation with no patch process, whereas inline
adds a licence to firewall pairs being bought anyway. More importantly SPAN based Snort is
detection only, and the brief's worst case is ransomware that spread rapidly, measured in minutes,
at an organisation with no security operations team to act on an alert at 3 a.m. A control that
alerts but cannot block is the wrong shape when nobody is on the other end.

## A2. Member 2

**A2.1 VPN. Selected: FortiGate NGFW pair terminating FortiClient remote access VPN.** SSL tunnel
mode for staff and IPsec for branch links on the same appliance pair, RADIUS authentication with
app based MFA, separate portals per user class mapped to different policy sets, endpoint
compliance gating, and one bundled licence covering VPN, NGFW, IPS and web filtering. Considered:
Cisco AnyConnect, Microsoft Always On VPN, OpenVPN.

*Rejected alternative: Cisco Secure Client on a Cisco firewall pair.* The stronger product, with a
more mature posture engine and tighter AAA integration. Rejected on cost structure, specifically
how Northbridge's differs from a large bank's. Cisco requires per user client licensing on top of
the appliance, with the IPS subscription a separate line again, at an organisation making its
first real security capital request whose budget has historically gone to physical measures. A
bundle delivering four capabilities under one subscription is far easier to approve, and leaves
budget for the controls with no product attached, awareness training, restoration testing, and the
vendor assessment process the integration needs. Spending the available money on four controls
rather than one reduces total risk more than buying the better VPN does.

**A2.2 AAA. Selected: Microsoft Entra ID with Windows NPS as RADIUS front end and the Entra MFA
extension.** Redundant NPS pair joined to the existing directory, Entra MFA enforced by Conditional
Access on all remote access and administrative accounts, Conditional Access doing the work a
posture engine would otherwise do for BYOD and work from home, Privileged Identity Management for
just in time elevation, sign in logs to the SIEM. For device administration, where NPS has no
TACACS+, RADIUS authentication with privilege level authorisation plus mandatory configuration
change logging as a compensating control. Considered: Cisco ISE, FreeRADIUS, ClearPass.

*Rejected alternative: Cisco ISE.* The better product for this problem, and what is given up is
stated explicitly. ISE provides TACACS+ with per command authorisation and accounting, the only
clean way to produce a per administrator record of every command. The compensating control is
genuinely weaker, recording that a configuration changed rather than who typed which command, and
defeatable by an administrator who disables logging first. Rejected on deployment risk rather than
capability. ISE is a project, profiling, policy sets, certificate infrastructure and a phased
802.1X rollout typically running in monitor mode for months. Northbridge has a newly formed team,
no central authentication of any kind, and an integration going live within two quarters. It needs
MFA on remote access in weeks, not after a NAC programme, and NPS can deliver that inside a sprint
using entitlement the bank likely already holds for its email system.

**A2.3 Architecture. Selected: one highly available NGFW cluster at the internet edge carrying all
externally facing zones, with the internal trust boundary enforced one layer down by VLAN
segmentation and inter VLAN ACLs on the distribution switches.** Every branch gets its own VLAN
set, so a compromise at one branch is contained to that branch before it reaches a firewall.
Considered: two physical firewall tiers, heterogeneous sandwich, cloud delivered edge.

*Rejected alternative: two separate physical firewall tiers.* The textbook answer and the choice
for a larger bank, keeping the internal boundary alive if the external device is compromised, and
keeping the two policy sets independent. Rejected on operational risk, and this is a deliberate
disagreement with the reference design. Northbridge has no dedicated firewall and no firewall
team, so four firewalls across two tiers means four policy sets, two HA pairs, two upgrade cycles
and two change windows, operated by people who have never managed one. The most likely year one
failure is not that an attacker defeated the edge firewall while the internal one did not exist,
it is a misconfiguration in an oversized rule set that nobody noticed. A smaller configuration
surface the team genuinely understands is more likely to be correct. Acknowledged as the weakest
point of the proposal against the brief's explicit multiple firewalls requirement.

**A2.4 IDS/IPS. Selected: the NGFW's bundled inline IPS at the edge in prevention mode, plus open
source Snort 3 sensors on internal SPAN ports at head office in detection mode.** Two sensors at
the core banking VLAN uplink and the inter branch aggregation uplink, the two chokepoints where
T3's lateral movement must appear, with virtual patching rules at the edge and branch coverage
deferred since branch traffic traverses the aggregation uplink. Considered: commercial inline IPS
on every tier, Suricata with Zeek, flow based detection.

*Rejected alternative: licensing commercial inline IPS on every firewall tier and at every
branch.* The stronger answer, giving prevention rather than detection on east west traffic, which
is where T3 does its damage. Rejected because the recurring subscription across seven sites is the
single largest line item in any of these four proposals, and the hardest to defend to a board that
has never bought an IPS. Internal sensors cost staff time instead, which is the resource
Northbridge has just allocated by forming a security team. The honest weakness is acknowledged: a
detection only internal sensor does nothing without someone reading it, and with no incident
response process an alert at 2 a.m. may sit unread until morning. That is judged acceptable only
because the plan pairs it with the SIEM, and because the brief's own description has the attacker
harvesting credentials and locating backups over days before detonating.

## A3. Member 3

**A3.1 VPN. Selected: WireGuard on a redundant pair of hardened Linux gateways in the DMZ.** Per
user public keys so no shared secret exists anywhere, a fixed modern cipher suite with no
negotiation so downgrade attacks and weak suite misconfiguration are structurally impossible, MFA
enforced at a reverse authentication step issuing short lived configurations rather than permanent
tunnel credentials, and per user `AllowedIPs` which is cryptographic routing, so a contractor's key
is mathematically incapable of carrying traffic outside its allowed set regardless of firewall
rules. Considered: Cisco AnyConnect, OpenVPN, native IKEv2.

*Rejected alternative: Cisco Secure Client on a Cisco firewall.* The choice for most banks, and
what rejecting it costs is stated plainly: WireGuard has no posture assessment, so it cannot check
whether a connecting laptop is patched, encrypted or running endpoint protection. That is a real
loss given personal devices and unassessed contractor machines. Rejected anyway on a checkable
brief fact. Northbridge has no dedicated firewall and a newly formed team, and an enterprise SSL
VPN appliance is among the most exposed devices an organisation can own, internet facing,
terminating privileged tunnels, with vulnerabilities exploited within days of disclosure.
Operating one safely requires a disciplined patch process applied under time pressure, and the
brief states there is no formal patch management process. Handing a team with no patch process a
product whose safety depends entirely on patching speed is the wrong risk. WireGuard's attack
surface is small enough that a slow patch cycle is survivable.

**A3.2 AAA. Selected: an open source stack, FreeRADIUS, OpenLDAP, privacyIDEA for TOTP, and
`tac_plus` for TACACS+.** Two active active FreeRADIUS nodes, per user TOTP with hardware tokens
for privileged accounts, TACACS+ with per command authorisation and accounting on every device,
802.1X with dynamic VLAN assignment, all accounting to the SIEM, and configuration held in version
control and deployed by configuration management so policy is reviewable as text. Considered: Cisco
ISE, Microsoft NPS, Aruba ClearPass.

*Rejected alternative: Cisco ISE.* The stronger product, collapsing RADIUS, TACACS+, profiling,
posture and guest onboarding into one supported platform, and for a regulated institution having a
vendor on the phone at 3 a.m. has genuine value. Rejected on a structural concern rather than
cost. ISE becomes the authentication authority for every network access decision, so if it is
unavailable and policy fails closed nobody authenticates anywhere, and if it fails open the control
evaporates exactly when the organisation is already in trouble. That concentration is acceptable
with mature change control and a tested DR plan. The brief states Northbridge has no documented
disaster recovery plan and backups never tested for restoration. Making one appliance pair the
gate on all network access, at an organisation that cannot demonstrate it can restore anything,
concentrates availability risk unacceptably. An open source stack distributes that across four
independently recoverable services, each rebuildable from a configuration file in version control
rather than from a backup nobody has tested.

**A3.3 Architecture. Selected: a dual firewall DMZ sandwich with seven named zones and an out of
band management network.** Three non negotiable properties. The DMZ sits between two independent
firewalls from different vendors, so public traffic crosses two policy enforcement points on two
platforms before anything internal is reachable, and a critical vulnerability in one vendor's
firewall compromises one tier rather than the boundary. The management plane is physically
separate, reachable only from a hardened jump host, with no path from the user data plane to any
device's management interface. The partner integration terminates in its own zone at a validating
integration broker, which is the only system permitted to speak to core banking, so the partners
never address the database. Considered: single vendor three tier, collapsed NGFW, micro
segmentation.

*Rejected alternative: a single vendor three tier design.* The same zone structure with both tiers
from one vendor, and on most criteria it is better, one console, one policy syntax, one upgrade
process, one skill set to recruit for. For a team that has never operated a firewall, that
simplicity reduces the chance of the misconfiguration that is statistically the most likely cause
of a perimeter failure. Rejected for one Northbridge specific reason: the asset concentration is
unusually extreme. Most organisations' critical data is spread across many systems, so losing one
boundary is partial. Northbridge's most critical asset is a single database in a single data
centre, reachable directly or via the portal from the internet, so everything depends on one
boundary holding. When a single boundary carries that much weight, correlated failure is the risk
that matters most, and two tiers of the same vendor fail together on one CVE. Mitigated by
proposing the internal firewall carry a deliberately small static rule set.

**A3.4 IDS/IPS. Selected: Suricata in inline IPS mode at zone boundaries, plus Zeek sensors for
protocol metadata, both feeding a Wazuh and Elastic SIEM.** Suricata with Emerging Threats rule
sets and HTTP, TLS and SQL rule groups enabled, chosen because T5 is a web application attack and
T6 arrives over a trusted connection, and both need content inspection rather than flow
inspection. Zeek producing structured protocol logs rather than alerts, which is the part a pure
IPS does not provide. The same deployment closes the no centralised logging finding, which is why
the SIEM is part of this proposal rather than a separate project. Virtual patching for known branch
CVEs, and a 30 day detection only burn in. Considered: commercial inline IPS, Snort on SPAN, flow
based detection only.

*Rejected alternative: commercial inline IPS licensed on the firewalls.* The lower effort answer,
and the comparison is uncomfortable, since a vendor IPS arrives pre tuned with curated feeds and
vendor support when a rule breaks a production application, whereas Suricata and Zeek need someone
to deploy, tune and operate them at an organisation whose security team is new. Rejected on what it
does not give. A commercial IPS produces alerts, not the comprehensive connection level record an
investigation needs. The brief says there is no centralised logging or audit trail across systems,
so if a breach is discovered next year Northbridge has no way to establish when it started, what
was reached, or what left. That question, scope, is the one a regulator and the payment partners
will both ask, and an alert feed cannot answer it while Zeek's transaction logs can. Given the
brief's catalogue of weaknesses, Northbridge is more likely to need to investigate a breach than
to prevent all of them.

## A4. Member 4

**A4.1 VPN. Selected: Zero Trust Network Access as the primary remote access method**, with
conventional IPsec retained for branch links only. Lightweight connectors inside the network
establish outbound tunnels to the broker, so no inbound port is published and there is no VPN
concentrator for an attacker to scan or exploit. Access is granted per application rather than per
network, so a remote user is authorised to the core banking application and is not placed on a
subnet from which anything else is reachable, and a contractor is authorised to the three systems
they support. Every session is evaluated against identity, device posture, location and risk at
the moment of access and re evaluated continuously, with a full per user per application log as a
structural by product. Considered: Cisco AnyConnect, FortiGate, WireGuard.

*Rejected alternative: Cisco Secure Client on a Cisco Secure Firewall.* The conventional answer,
mature, supported, excellent posture engine, and what the module's labs teach. Rejected for one
structural reason. A conventional VPN's job is to put a remote user on the network, which is fine
in a properly segmented network because internal boundaries exist. In Northbridge's network, which
the brief describes as flat with guest Wi-Fi and point of service equipment sharing space with
core systems, putting a user on the network is equivalent to granting access to everything. MFA
fixes who gets on, a real improvement over a shared account, but does not change the fact that
whoever gets on can reach the database. ZTNA is the only option without that property. The honest
counter argument is stated: ZTNA routes a regulated bank's remote access through a third party
cloud broker, introducing exactly the unassessed vendor trust that T6 identifies as critical.

**A4.2 AAA. Selected: Aruba ClearPass Policy Manager**, redundant pair. RADIUS and TACACS+ in one
platform, with per command authorisation and accounting. Device profiling and fingerprinting as
the headline reason, identifying and classifying every device by DHCP fingerprint, MAC OUI, HTTP
user agent and active probing, producing the asset inventory Northbridge does not have. OnGuard
posture for managed endpoints, OnBoard for BYOD certificate provisioning, and ClearPass Guest
replacing a shared guest password with sponsored, time limited, individually identified accounts.
Vendor neutral, so the same platform works across any switching, wireless or firewall vendor.
Considered: Cisco ISE, Microsoft NPS, FreeRADIUS.

*Rejected alternative: Cisco ISE.* Functionally very close, with tighter integration to Cisco
switching, and if the access layer is Cisco throughout, ISE can do things with the fabric that
ClearPass cannot. Rejected on vendor lock in at the wrong moment. Northbridge is about to make its
first firewall, VPN and IDS/IPS purchases, with four competing proposals on the table for each.
ISE's advantage is realised when the whole estate is Cisco and falls when it is not, so choosing
ISE now is in effect also choosing Cisco for the other three areas before those decisions have been
argued on their merits. The secondary reason is weighted most: ClearPass profiling is the better
answer to a specific problem, since the brief describes point of service equipment nobody has an
inventory of, plus personal machines used for work. The first thing Northbridge needs is not
enforcement but to find out what is on its network, and profiling with monitor mode delivers that
inventory before any policy is enforced, which is also the safest way to begin an 802.1X rollout
at an organisation that does not know what will break.

**A4.3 Architecture. Selected: two firewall tiers for north south traffic, plus identity based
micro segmentation inside the core banking zone.** The conventional zone structure with default
deny between zones, and inside CORE-BANKING the database accepts connections only from named
application servers on the named port, and application servers only from the DMZ reverse proxy,
enforced by host based and hypervisor level policy rather than by placing each server in its own
VLAN. Policy attaches to workload identity rather than IP address, so it survives re addressing and
rebuilds, with a discovery and monitor phase mapping real flows before any blocking. Considered:
three tier zoned, dual vendor sandwich, collapsed NGFW.

*Rejected alternative: the conventional three tier zoned design with firewall pairs.* Well
understood, operationally simpler, what the labs teach, and it genuinely solves the brief's stated
problem. Rejected because of a gap it leaves that these threat models care about. Zone based
segmentation filters traffic between zones and does not filter traffic within a zone, so once
CORE-BANKING is a zone containing the database, the application servers and whatever else lives in
the data centre, an attacker reaching any one of them can reach all of them, because the firewall
never sees that traffic. T8's chain arrives inside the server room, which is inside that zone,
where a zone based design offers nothing. The honest cost is stated: micro segmentation needs an
accurate map of which system talks to which on which port, and Northbridge has no asset inventory,
no documented architecture and a decade of organic growth, so building that map is months of
discovery and getting it wrong breaks core banking in production. The proposal is put forward
because the east west gap is real and should be named in the plan rather than discovered later.

**A4.4 IDS/IPS. Selected: inline Firepower IPS at zone boundaries, plus flow based behavioural
detection from NetFlow telemetry off the existing switches.** Part one, signature prevention with
Talos feeds at the edge for DMZ traffic and on the internal tier for core banking traffic, with
explicit virtual patching for known branch CVEs and a 30 day burn in. Part two, NetFlow exported
from switches and routers Northbridge already owns, at head office and all six branches, into a
collector that baselines normal behaviour and alerts on deviation, a workstation suddenly
connecting to hundreds of hosts, SMB appearing on a path it has never used, unprecedented egress
volumes, or periodic beaconing. No sensor, SPAN session or appliance is deployed at any branch, and
encrypted traffic remains analysable because flow records describe who talked to whom, when, how
much and for how long, none of which encryption hides. Considered: inline IPS only, Snort or
Suricata on SPAN, Zeek with SIEM only.

*Rejected alternative: inline IPS on the firewalls alone.* Cheaper, simpler and entirely
defensible, placing prevention exactly where traffic crosses a trust boundary. Rejected because of
what it cannot see. An inline IPS inspects traffic that crosses the device and is structurally
blind to traffic that does not, east west movement within a zone, within a branch, or between two
servers in the data centre. T8's intruder is inside the server room, so inside the zone, on the
wrong side of every inspection point. T7's disclosed credential is used by an attacker moving
between hosts that never traverse the firewall. T3's ransomware spreads host to host, much of it
intra zone. An IPS only design would give good coverage of attacks arriving through the front door
and none of attacks already inside, which of the eight threats modelled is most of them. The second
reason is signature coverage: signatures catch known exploits and do not catch an authenticated
attacker using legitimate credentials and legitimate protocols, which is exactly what T1, T2, T7
and T8 produce, and that class is dominant here because Northbridge's weaknesses are overwhelmingly
credential and access weaknesses rather than software vulnerabilities.
