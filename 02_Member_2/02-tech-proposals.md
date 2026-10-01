# Member 2 — Individual Technology Proposals (Appendix A2)

**Member:** [Member 2 — Full Name / IT Number]

> These four proposals were reasoned independently, before any group discussion, as the brief
> requires. They are individually assessed. The group's comparative evaluation appears in the
> main body of the report.

My overall design stance differs deliberately from a best-practice reference build. Northbridge
has spent a decade investing in vaults and cameras rather than IT, which tells me the board
approves spending it can picture. A security programme that needs a large capital approval
before anything improves is a programme that stalls at the first budget review. So I have
optimised each choice for **time-to-first-control and total cost of ownership**, accepting a
lower technical ceiling where the cheaper option still defeats the modelled attack.

---

## A2.1 — VPN solution for secure remote access

### Options considered

| Option | Fit for Northbridge |
|---|---|
| **FortiGate next-generation firewall with FortiClient SSL/IPsec remote-access VPN** | VPN, firewall, IPS and web filtering bundled in one licence; strong price/performance |
| Cisco Secure Client on a Cisco Secure Firewall pair | Technically excellent, highest licence and training cost |
| Microsoft Always On VPN | Deep Windows integration, no third-party client, but Windows-only and complex PKI |
| OpenVPN Access Server | Cheap, cross-platform, weak posture and reporting |

### Selection

**A FortiGate next-generation firewall pair at the head-office internet edge, terminating
FortiClient remote-access VPN**, with:

- **SSL VPN in tunnel mode** for staff on managed laptops and **IPsec/IKEv2** for the branch
  site-to-site tunnels, both on the same appliance pair.
- **Per-user authentication against the central AAA service over RADIUS**, with the **second
  factor delivered by the organisation's authenticator app** — no local account store on the
  firewall.
- **Separate SSL VPN portals** for staff, contractors and administrators, each mapped to a
  different firewall policy set, so contractor sessions reach only the systems they support.
- **FortiClient endpoint telemetry and compliance rules** gating tunnel establishment on OS
  patch level and antivirus status.
- **One bundled licence covering VPN, NGFW policy, IPS and web filtering** — the commercial
  core of this proposal.

### The alternative I seriously considered, and why I rejected it

**Cisco Secure Client (AnyConnect) on a Cisco Secure Firewall pair** is the stronger product
and I expect it to be the group's instinct, because the module's labs are Cisco-based. Its
posture engine is more mature, and its integration with Cisco ISE is tighter than FortiGate's
RADIUS relationship can be.

I rejected it on cost structure, and specifically on how Northbridge's cost structure differs
from a large bank's. Cisco's remote-access VPN requires per-user client licensing on top of
the appliance, and the IPS subscription is a separate line item again. Northbridge is a
450-staff bank whose security budget has historically gone almost entirely to physical
measures — this is an organisation making its first real IT security capital request, and the
brief makes clear the board has only just put this on its agenda. A bundle that delivers VPN,
firewall, IPS and web filtering under one subscription is far easier to get approved, and
leaves budget for the controls that are pure cost with no product attached: awareness
training, backup restoration testing, and the vendor assessment process the payment processor
integration needs. My judgement is that spending the available money on four controls rather
than one reduces Northbridge's total risk more than buying the better VPN does.

I accept the trade-off this creates: FortiGate's posture checking is good but not Cisco's
equal, and splitting VPN away from the Cisco-based switching estate means two management
planes for a team that has never run one.

### Why this fits Northbridge specifically

The brief's remote-access problem is a single shared account with no MFA — a problem any
competent enterprise VPN solves. There is no Northbridge-specific requirement that only Cisco
can meet: no existing AnyConnect estate, no Cisco firewall to extend, no legacy
configuration to preserve. When two products both fully solve the stated problem, the
deciding factor should be what else the money buys, and that points to the bundle.

---

## A2.2 — AAA solution for centralised authentication

### Options considered

| Option | Fit for Northbridge |
|---|---|
| **Microsoft Entra ID with the NPS extension for RADIUS and MFA** | Reuses the directory and licences Northbridge almost certainly already owns; fastest path to MFA |
| Cisco ISE | Most capable, includes TACACS+; highest cost and longest deployment |
| FreeRADIUS with an LDAP backend and a TOTP module | No licence cost, no support contract |
| Aruba ClearPass | Capable, a third vendor, mid-range cost |

### Selection

**Microsoft Entra ID as the identity authority, with Windows Server NPS acting as the RADIUS
front end and the Entra MFA NPS extension providing the second factor.** Deployment:

- **A redundant pair of NPS servers** at head office, joined to the existing directory,
  serving RADIUS to the VPN, the wireless controllers and 802.1X on the wired access layer.
- **Entra ID MFA** enforced via Conditional Access on all remote access, all administrative
  accounts and the online banking portal's staff-facing administration interface.
- **Entra Conditional Access policies** doing the work that a NAC posture engine would
  otherwise do: device compliance state, sign-in risk and named-location rules — which
  usefully covers the BYOD and work-from-home gap the brief describes, where the device is
  not Northbridge's but the identity is.
- **Privileged Identity Management** for just-in-time elevation of administrative roles,
  replacing standing privilege.
- **Sign-in and audit logs exported to the central SIEM**, giving a single identity audit
  trail.
- **For network device administration**, where NPS cannot provide TACACS+, I propose RADIUS
  authentication with privilege-level authorisation plus mandatory `logging` of configuration
  changes to the SIEM as a **compensating control**.

### The alternative I seriously considered, and why I rejected it

**Cisco ISE** is the better product for this problem and I want to be explicit that I know
what I am giving up. ISE provides TACACS+ with per-command authorisation and accounting,
which is the only clean way to produce a per-administrator record of every command typed on a
network device. My compensating control — RADIUS plus configuration-change logging — is
genuinely weaker: it records *that* a configuration changed, not *who typed which command*,
and it can be defeated by an administrator who disables logging first.

I rejected ISE on deployment risk rather than on capability. ISE is a project: profiling,
policy sets, certificate infrastructure, and a phased 802.1X rollout that typically runs in
monitor mode for months before enforcement. Northbridge has a *newly formed* security team,
no existing central authentication of any kind, and a payment processor integration going
live within two quarters. The organisation needs MFA on remote access in weeks, not after a
NAC programme. NPS with the Entra extension can be delivering MFA on the VPN inside a sprint,
using a directory and licence entitlement the bank very likely already holds for its email
system. Closing T1 — my colleague's critical-rated shared-VPN threat — two quarters earlier is
worth more than closing T2's infrastructure accountability gap two quarters sooner than
otherwise. I would revisit ISE as a phase 2 once segmentation is in place and 802.1X has
something meaningful to assign devices to.

### Why this fits Northbridge specifically

Two details decide it. First, the brief names the internal email system as an asset every
employee relies on, which means an enterprise mail platform and therefore, in all likelihood,
a directory and an existing licence estate — so the identity authority is a configuration
exercise rather than a procurement. Second, the brief says Northbridge "allows work from home
and has allowed staff to use their own personal machines and phones for work, but no guidance
or rules are in place". Conditional Access is designed exactly for that case: it conditions
access on the state of a device the organisation does not own. A RADIUS-only NAC approach has
no answer for an unmanaged personal laptop at home.

---

## A2.3 — Secure network architecture with multiple firewalls and defined zones

### Options considered

| Option | Fit for Northbridge |
|---|---|
| **One NGFW cluster with multiple segmented interfaces, plus VLAN segmentation and inter-VLAN ACLs at the distribution layer as the second enforcement tier** | Lowest cost and lowest operational load; satisfies "multiple firewalls" through the HA cluster plus distribution-layer filtering |
| Two separate physical firewall tiers | Cleanest separation, roughly double the cost and the policy surface |
| Heterogeneous dual-vendor sandwich | Resists single-vendor CVEs, needs two skill sets |
| Cloud-delivered security edge | Modern, but routes a regulated bank's traffic through a third party |

### Selection

**A single highly available NGFW cluster at the internet edge carrying all externally facing
zones, with the internal trust boundary enforced one layer down by VLAN segmentation and
inter-VLAN access control lists on the distribution switches.**

| Zone | Enforced by | Policy summary |
|---|---|---|
| OUTSIDE | NGFW cluster | Deny all inbound except published HTTPS |
| DMZ | NGFW cluster, dedicated interface | Internet → reverse proxy only; DMZ cannot initiate to internal |
| PARTNER | NGFW cluster, dedicated interface | Mutual TLS, IP allow-listed, to an integration broker only |
| REMOTE-VPN | NGFW cluster, per-portal policy | Staff / contractor / admin pools with separate rule sets |
| GUEST | NGFW cluster, dedicated interface + wireless client isolation | Internet only; no route to any internal VLAN |
| CORE-BANKING | Distribution-layer VLAN + inter-VLAN ACL | Named application ports from STAFF only; no internet, no branch-initiated access |
| STAFF (per site) | Per-site VLANs + inter-VLAN ACL | Internet via proxy; core banking by application port only |
| MGMT | Separate VLAN + ACL restricted to the jump host | Infrastructure management only |

The design principle is that **every branch gets its own VLAN set rather than sharing one
flat space**, so a compromise at Branch 3 is contained to Branch 3's VLANs even before it
reaches a firewall.

### The alternative I seriously considered, and why I rejected it

**Two separate physical firewall tiers** — an edge pair and an internal core pair — is the
textbook answer and the one I would choose for a larger bank. It means the internal boundary
survives compromise of the external device, and it keeps the two policy sets independent so
an edge change cannot accidentally open an internal path.

I rejected it for Northbridge on operational-risk grounds, and this is the point where I
disagree with the reference design on purpose. Northbridge currently has **no dedicated
firewall and no firewall team**. Four firewalls across two tiers means four policy sets, two
HA pairs, two upgrade cycles and two change windows, operated by a team that has never
managed one. In my judgement the most likely failure mode for Northbridge in year one is not
"the attacker defeated the edge firewall and the internal firewall did not exist" — it is "a
misconfiguration in an overlarge rule set left a path open that nobody noticed". A smaller
configuration surface that the team genuinely understands is, for this specific organisation,
more likely to be correct. Inter-VLAN ACLs at the distribution layer still provide the second
enforcement point that stops T3's lateral movement, on hardware that is already being bought
for the access layer and using a skill the team exercised in this module's labs.

I also considered that the brief explicitly asks for "multiple firewalls". I read an HA
cluster plus a distinct second enforcement layer as meeting the intent, but I acknowledge
this is the weakest point of my proposal and that a reader may judge it as not satisfying the
requirement literally.

### Why this fits Northbridge specifically

The branch-per-VLAN decision comes straight from the brief's ransomware pattern: incidents
"began with a single compromised branch workstation and spread rapidly across an unsegmented
network". Containing branches from each other — not just branches from the data centre — is
what breaks that specific chain. The separate GUEST interface with client isolation comes from
guest Wi-Fi currently sharing space with core systems, and the PARTNER interface exists
because the payment processor integration extends trust outside Northbridge for the first
time and needs a terminating point that is not the internal network.

---

## A2.4 — IDS/IPS solution

### Options considered

| Option | Fit for Northbridge |
|---|---|
| **Snort 3 IDS sensors on SPAN/mirror ports at head office, with managed rule sets, plus the NGFW's bundled inline IPS at the perimeter** | Zero licence cost for the internal sensors; inline prevention already paid for at the edge |
| Commercial inline IPS licensed on every firewall tier | Best protection, recurring per-tier subscription |
| Suricata plus Zeek feeding an open-source SIEM | Richest investigation data, highest build effort |
| Flow-based anomaly detection from switch telemetry | Full coverage, no signatures, needs tuning time |

### Selection

**A two-part design: the NGFW's bundled inline IPS at the internet edge in prevention mode,
plus open-source Snort 3 sensors monitoring internal SPAN ports at head office in detection
mode.**

- **Edge, inline, prevention:** the IPS subscription included in the NGFW bundle from A2.1,
  tuned to a web-and-database protection policy for the online banking portal and mobile API.
- **Internal, passive, detection:** two Snort 3 sensors at head office — one on a SPAN of the
  core banking VLAN uplink, one on a SPAN of the inter-branch aggregation uplink. These are
  the two chokepoints where T3's lateral movement must appear.
- **Virtual patching rules** for the specific known CVEs affecting the outdated branch
  software, applied at the edge and alerted on internally, as a holding control until the
  patch programme catches up.
- **All events, from both parts, into the central SIEM** with a defined severity-to-action
  mapping.
- **Branch coverage** deferred to phase 2, on the grounds that branch traffic to head office
  traverses the aggregation uplink and is therefore already visible to the internal sensor.

### The alternative I seriously considered, and why I rejected it

**Licensing commercial inline IPS on every firewall tier and at every branch** is the stronger
answer, and it would give prevention rather than detection on internal east-west traffic —
which is exactly where T3 does its damage. I rejected it because the recurring subscription
across seven sites is the single largest line item in any of my four proposals, and it is the
one I am least able to defend to a board that has never bought an IPS. The internal sensors
cost staff time instead of subscription fees, and staff time is the resource Northbridge has
just allocated by forming a security team.

I also recognise the honest weakness in what I have chosen: **a detection-only internal
sensor does nothing without someone reading it.** Northbridge has no incident response
process and no 24×7 operations capability, so an internal Snort alert at 2 a.m. may sit
unread until morning. I regard that as acceptable only because the plan pairs it with the
central SIEM and alerting control, and because ransomware's staging phase in this scenario
runs over days rather than minutes — the brief's own description has the attacker harvesting
credentials and locating backups before detonating, which is a window a morning-shift analyst
can still act within. If the group judges that window too optimistic, the correct answer is
inline prevention internally, and my proposal should lose on that point.

### Why this fits Northbridge specifically

The SPAN placement is chosen from the brief's own architecture, not from a template.
Northbridge has one data centre and six branches connecting back over dedicated links, so
**all** branch-to-core traffic funnels through head office. Two sensors at the right two
uplinks therefore see every flow that matters for T3's propagation path, without deploying
anything to a branch — which is the difference between a design the new security team can
actually operate and seven appliances nobody has time to patch, in an organisation the brief
says has no patch management process at all.
