# Member 4 — Individual Technology Proposals (Appendix A4)

**Member:** [Member 4 — Full Name / IT Number]

> These four proposals were reasoned independently, before any group discussion, as the brief
> requires. They are individually assessed. The group's comparative evaluation appears in the
> main body of the report.

My overall design stance follows from my threat modelling. T7 and T8 are both cases where
Northbridge's problem is **not knowing what happened** — who called, who disclosed, who
entered the room, who used which credential. So in each of the four areas I have weighted
**visibility and accountability** above raw blocking capability, and I have preferred designs
that assume the perimeter will be bypassed, because both of my threats bypass it by
construction: one walks through the front door, the other asks politely over the phone.

---

## A4.1 — VPN solution for secure remote access

### Options considered

| Option | Fit for Northbridge |
|---|---|
| **Zero Trust Network Access (ZTNA) — identity-aware application proxy replacing network-level VPN** | Grants access to named applications, not to the network; per-session verification; no inbound firewall exposure |
| Cisco Secure Client on a Cisco firewall | Mature, posture-capable, places the user on the network |
| FortiGate SSL/IPsec VPN | Cost-effective bundle, places the user on the network |
| WireGuard on a Linux gateway | Minimal attack surface, places the user on the network |

### Selection

**A Zero Trust Network Access service as the primary remote-access method**, with a
conventional IPsec site-to-site VPN retained only for branch connectivity. The design:

- **Lightweight connectors deployed inside Northbridge's network** establish outbound tunnels
  to the ZTNA broker. **No inbound port is published to the internet at all** — there is no VPN
  concentrator for an attacker to scan, fingerprint or exploit.
- **Access is granted per application, not per network.** A remote user is authorised to the
  core banking application; they are not placed on a subnet from which anything else is
  reachable. A contractor is authorised to the three systems they support and nothing else.
- **Every session is evaluated against identity, device posture, location and risk signals**
  at the moment of access, and re-evaluated continuously, rather than once at tunnel
  establishment.
- **MFA is enforced by the broker** on every application access, not once per tunnel.
- **A full per-user, per-application access log** is produced by the broker as a structural
  by-product of the architecture.
- **Branch sites keep IPsec site-to-site tunnels** over their existing dedicated links, since
  branch connectivity is a network-to-network problem that ZTNA does not address.

### The alternative I seriously considered, and why I rejected it

**Cisco Secure Client (AnyConnect) on a Cisco Secure Firewall** is the conventional answer and
I expect it to be the group's choice. It is mature, it is supported, its posture engine is
excellent, and it is what the module's labs teach. I rejected it as *my* proposal for one
specific structural reason.

A conventional VPN's job is to put a remote user **on the network**. In an organisation with a
properly segmented network, that is fine, because the network has internal boundaries. In
Northbridge's network — which the brief describes as flat, with head office systems, branch
systems, guest Wi-Fi and point-of-service equipment sharing the same space — putting a user
"on the network" is equivalent to granting them access to everything. A VPN with MFA fixes
*who* gets on, which is a real improvement over the shared account. It does not change the
fact that whoever gets on can reach the customer database. My colleague's T1 model makes this
point directly: the VPN and the flat network together mean remote access and core-banking
reachability are the same privilege.

ZTNA is the only one of the four options that does not have that property, because it never
puts anyone on the network. And it has a second property that matters specifically here: it
publishes **no inbound service**. Enterprise SSL VPN appliances have been among the most
actively exploited internet-facing products in recent years, and the brief states Northbridge
has **no formal patch management process**. Giving an organisation that cannot patch promptly
an internet-facing appliance whose safety depends on patching promptly is the risk I am
choosing to avoid.

**I will state the honest counter-argument**, because it is strong and it is the reason I
expect to lose this one. ZTNA means routing Northbridge's remote access through a third-party
cloud broker. For a regulated financial institution with an on-premises data centre, that
introduces a new third-party dependency and a data-residency question — and the brief makes
clear Northbridge has **no vendor security assessment process** with which to evaluate that
provider. I would be recommending that the bank take on exactly the kind of unassessed
third-party trust that my colleague's T6 threat model identifies as critical. There is a real
tension between my two arguments, and a reasonable reviewer may conclude that a bank which
cannot yet assess a vendor should not make a vendor its authentication path.

### Why this fits Northbridge specifically

The contractor case is what makes this concrete. Northbridge has **two external IT support
contractors** needing regular access to internal systems, on devices Northbridge does not own
and has never assessed. With a conventional VPN, the best available control is an address pool
plus firewall rules — which must be maintained correctly, forever, by a brand-new security
team. With ZTNA, the contractor is authorised to named applications and is structurally
incapable of reaching anything else, with a per-application audit trail attached. That
difference maps directly onto T1's finding that Northbridge has "no reliable way of knowing
who actually accessed its systems remotely at any given time".

---

## A4.2 — AAA solution for centralised authentication

### Options considered

| Option | Fit for Northbridge |
|---|---|
| **Aruba ClearPass Policy Manager** | Vendor-neutral NAC with the strongest device profiling and guest/BYOD onboarding of the four |
| Cisco ISE | Equivalent capability, tighter Cisco integration, higher cost |
| Microsoft NPS with the Entra MFA extension | Cheapest and fastest, no TACACS+, weak profiling |
| FreeRADIUS + LDAP + TOTP | No licence cost, highest operational burden |

### Selection

**Aruba ClearPass Policy Manager** as the central AAA and network access control platform,
deployed as a redundant pair at head office:

- **RADIUS and TACACS+ in one platform** — RADIUS for 802.1X, wireless and VPN; TACACS+ with
  per-command authorisation and accounting for network device administration.
- **Device profiling and fingerprinting** as the headline reason for this choice. ClearPass
  identifies and classifies every device that touches the network by DHCP fingerprint, MAC
  OUI, HTTP user-agent and active probing — producing the asset inventory Northbridge does not
  currently have.
- **OnGuard posture assessment** for managed endpoints and **OnBoard** for BYOD certificate
  provisioning, which addresses the work-from-home and personal-device gap the brief
  describes.
- **ClearPass Guest** for the guest Wi-Fi, replacing a shared guest password with sponsored,
  time-limited, individually identified guest accounts.
- **Vendor-neutral enforcement**, so the same policy platform works across Cisco switching,
  any wireless vendor, and any firewall — which matters because the group has not yet decided
  its firewall vendor and this choice does not constrain it.
- **All accounting to the central SIEM.**

### The alternative I seriously considered, and why I rejected it

**Cisco ISE** is the obvious alternative and is functionally very close. It has tighter
integration with Cisco switching — TrustSec and SGT-based segmentation in particular — and if
Northbridge's access layer is Cisco throughout, ISE can do things with the network fabric that
ClearPass cannot.

I rejected it on **vendor lock-in at the wrong moment**. Northbridge is about to make its
first ever firewall purchase, its first VPN purchase and its first IDS/IPS purchase, and the
group has four different proposals on the table for each. ISE's advantage is realised when
the whole estate is Cisco; its value falls when it is not, and TACACS+ aside, ISE managing a
non-Cisco firewall or a non-Cisco wireless estate is a lowest-common-denominator RADIUS
relationship. Choosing ISE now is, in effect, also choosing Cisco for the other three areas
before those decisions have been argued on their own merits. ClearPass gives equivalent
capability with no such coupling, so the AAA decision does not pre-commit the other three.

My secondary reason is the one I weight most from my own threat modelling: ClearPass's
profiling is, in my assessment, the better answer to a specific Northbridge problem. The brief
describes **point-of-service support equipment** on the network that nobody has an inventory
of, plus personal machines and phones used for work with no guidance in place. The first thing
Northbridge needs is not enforcement — it is **to find out what is on its network**.
ClearPass's profiling and its monitor mode deliver that inventory before any policy is
enforced, which is also the safest possible way to begin an 802.1X rollout in an organisation
that does not know what will break.

### Why this fits Northbridge specifically

Two details. First, the guest Wi-Fi: the brief has guest Wi-Fi sharing network space with core
systems, and ClearPass Guest replaces an anonymous shared password with individually
sponsored, time-limited access — so a guest-originated incident is attributable to a person
rather than to "someone on the guest network". Second, the unknown device population:
Northbridge cannot write a sensible access policy for devices it has not enumerated, and
profiling is the control that enumerates them. In an organisation with no asset inventory, the
AAA platform that doubles as a discovery tool is worth more than the one with the tighter
fabric integration.

---

## A4.3 — Secure network architecture with multiple firewalls and defined zones

### Options considered

| Option | Fit for Northbridge |
|---|---|
| **Two firewall tiers plus identity-based micro-segmentation inside the core, enforced by host firewalls and network policy rather than by VLAN boundaries alone** | Contains lateral movement *within* a zone, not only between zones; policy follows the workload |
| Three-tier zoned design with firewall pairs | Strong and conventional; east-west traffic inside a zone remains unfiltered |
| Dual-vendor DMZ sandwich | Resists single-vendor CVEs; same east-west gap |
| Single collapsed NGFW | Cheapest; insufficient for the brief's requirement |

### Selection

**Two firewall tiers for north-south traffic, plus micro-segmentation for east-west traffic
inside the core banking zone.**

- **Tier 1 and Tier 2 firewalls** establish the conventional zone structure — OUTSIDE, DMZ,
  PARTNER, INTERNAL-USERS, CORE-BANKING, GUEST, MGMT-OOB — with default-deny between zones.
- **Inside CORE-BANKING, workloads are micro-segmented**: the database server accepts
  connections only from the named application servers on the named database port, and the
  application servers accept connections only from the DMZ reverse proxy. Enforcement is by
  host-based firewall policy and hypervisor-level network policy, centrally managed, rather
  than by placing each server in its own VLAN.
- **Default-deny east-west within the zone**, so a compromised application server cannot
  enumerate or reach its neighbours.
- **Policy is attached to workload identity**, not to IP address, so it survives
  re-addressing, migration and rebuilds.
- **A discovery and monitor phase first**: flows are mapped and policy is run in alert-only
  mode before any blocking, so the real application dependencies are measured rather than
  guessed.
- **Branches get per-site VLANs** with inter-VLAN filtering, as the lower-cost equivalent of
  the same containment principle.

### The alternative I seriously considered, and why I rejected it

**The conventional three-tier zoned design with firewall pairs** is the alternative, and it is
what I expect the group to adopt. It is well understood, it is operationally simpler, it is
what the labs teach, and it genuinely solves the brief's stated problem — the flat network
becomes a set of zones with filtering between them.

I rejected it as my proposal because of a gap it leaves that my threat models care about
specifically. Zone-based segmentation filters traffic **between** zones. It does not filter
traffic **within** a zone. Once CORE-BANKING is a zone containing the database server, the
application servers and whatever else lives in the data centre, an attacker who reaches any
one of them can reach all of them — the firewall never sees that traffic, because it never
crosses a zone boundary. T8's attack chain arrives *inside* the server room, which is to say
inside that zone, and from there a zone-based design offers nothing at all. The same is true
of T7's credential path once it reaches a server. Zoning solves the branch-to-core problem in
my colleagues' T3 and T4; it does not solve the inside-the-core problem in mine.

**The honest cost, and why I expect to lose this one.** Micro-segmentation requires an accurate
map of which system talks to which, on which port. Northbridge has no asset inventory, no
documented architecture and a decade of organic growth — the brief says so. Building that map
is months of discovery work, and getting it wrong means breaking the core banking application
in production. A reviewer can reasonably say that Northbridge needs the boundaries it does not
have before it needs the fine-grained policy it cannot yet specify, and that micro-segmentation
is the right phase 3 and the wrong phase 1. I think that argument is correct on sequencing; I
put the proposal forward because the east-west gap is real and should be named in the plan
rather than discovered later.

### Why this fits Northbridge specifically

The database is the reason. Northbridge's most critical asset is **a single customer database
in a single on-premises data centre**, which is an unusually concentrated risk profile. When
one system matters that much more than the others, the control that matters most is the one
closest to it. Micro-segmentation puts a default-deny boundary around that one server, so that
every other compromise in the environment — branch workstation, web portal, server room
intrusion, disclosed credential — still has to defeat one more specific control before reaching
the thing that actually matters. For an asset that concentrated, I would rather have one more
boundary at the asset than one more boundary at the perimeter.

---

## A4.4 — IDS/IPS solution

### Options considered

| Option | Fit for Northbridge |
|---|---|
| **Inline Firepower (Snort 3) IPS at the zone boundaries, plus flow-based behavioural detection from NetFlow telemetry off the existing switches** | Signature prevention north-south *and* behavioural detection east-west, with no sensors to deploy at branches |
| Inline IPS on the firewalls only | Prevention where traffic crosses a boundary; blind to traffic that does not |
| Snort or Suricata sensors on SPAN ports | Needs a sensor, a SPAN session and a management path per site |
| Zeek metadata plus SIEM only | Excellent investigation data, no prevention |

### Selection

**A two-part design combining signature-based inline prevention with flow-based behavioural
detection.**

**Part 1 — inline IPS at the zone boundaries.** Firepower/Snort 3 with Talos feeds, in
prevention mode on the internet edge for DMZ-bound traffic and on the internal tier for
CORE-BANKING-bound traffic. Policies tuned for web and database protection, with explicit
virtual-patching coverage for the known CVEs on the outdated branch software the brief
describes. A 30-day detection-only burn-in before blocking is enabled, measured against real
Northbridge traffic.

**Part 2 — flow-based behavioural detection across the whole estate.** NetFlow is exported
**from the switches and routers Northbridge already owns**, at head office and at all six
branches, into a flow analytics collector that baselines normal behaviour and alerts on
deviation: a workstation suddenly connecting to hundreds of internal hosts, SMB traffic
appearing on a path it has never used, data volumes leaving the core banking zone at an
unprecedented rate, or a host beaconing to an external address at regular intervals.

- **No sensor, SPAN session or appliance is deployed at any branch.** The telemetry comes from
  the existing network devices, which is the decisive practical advantage.
- **Encrypted traffic is still analysable**, because flow records describe who talked to whom,
  when, how much and for how long — none of which encryption hides.
- **Everything feeds the central SIEM**, with defined severities and an escalation path.

### The alternative I seriously considered, and why I rejected it

**Inline IPS on the firewalls alone** is the alternative, and it is cheaper, simpler and
entirely defensible. It puts prevention exactly where traffic crosses a trust boundary, which
is where most attacks must pass.

I rejected it because of what it cannot see, and the gap is the one my threat models land in.
An inline IPS inspects traffic that **crosses the device**. It is structurally blind to
traffic that does not — east-west movement within a zone, within a branch, or between two
servers in the data centre. T8's intruder is inside the server room, which means inside the
zone, on the wrong side of every inline inspection point in the design. T7's disclosed
credential is used by an attacker who, once inside, moves between hosts that never traverse
the firewall. And my colleague's T3 ransomware spreads host-to-host, much of which is
intra-zone. An IPS-only design would leave Northbridge with good coverage of the attacks that
come through the front door and no coverage of the attacks that are already inside — which,
of the eight threats this group modelled, is most of them.

The second reason is signature coverage. Signatures catch known exploits. They do not catch an
authenticated attacker using legitimate credentials and legitimate protocols, which is exactly
what T1, T2, T7 and T8 all produce. There is no signature for "Alice's account is behaving
unlike Alice". Behavioural flow analysis is the only one of the four options that detects
that class of attack, and that class is the dominant one in this environment because
Northbridge's weaknesses are overwhelmingly credential and access weaknesses rather than
software vulnerabilities.

### Why this fits Northbridge specifically

The branch problem decides it. Northbridge has **six branch offices and no security staff at
any of them**, and the brief's lead ransomware scenario begins at a branch workstation. Any
design requiring hardware at each branch means seven deployments to install, manage and
patch, in an organisation the brief says has **no formal patch management process** — so those
sensors would themselves become unpatched internet-adjacent appliances. NetFlow export is a
configuration line on switches Northbridge already owns. It gives visibility at every branch
on day one, at no hardware cost, with nothing new to patch.

The second specific fit is detection of the thing Northbridge most needs to detect. The brief
says the bank is "blind to reconnaissance or active compromise until damage is already
visible". Internal reconnaissance — one host scanning many — is the single clearest signal in
flow data and appears in it immediately, before any payload executes. That is the earliest
possible detection point in the ransomware chain my colleague modelled in T3, and it is
available from telemetry Northbridge can turn on this week.
