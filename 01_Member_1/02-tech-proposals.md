# Member 1 — Individual Technology Proposals (Appendix A1)

**Member:** [Member 1 — Full Name / IT Number]

> These four proposals were reasoned independently, before any group discussion, as the brief
> requires. They are individually assessed. The group's comparative evaluation of all four
> members' proposals appears in the main body of the report, not here.

My overall design stance: Northbridge's root problem is that it has **no identity authority**.
Every one of the four areas below is therefore chosen so that it can consume a single central
identity, because a VPN, a firewall and an IPS that each carry their own separate account
store would simply reproduce the "every device has its own local accounts" problem the brief
already describes.

---

## A1.1 — VPN solution for secure remote access

### Options considered

| Option | Fit for Northbridge |
|---|---|
| **Cisco Secure Client (AnyConnect) IKEv2/IPsec remote-access VPN terminated on a Cisco Secure Firewall (ASA/FTD) pair** | Per-user certificate + MFA, posture assessment, native RADIUS/TACACS+ integration, same platform as the perimeter firewall |
| Clientless SSL "WebVPN" portal on the same appliance | No client to deploy, but browser-only access and no posture check |
| FortiGate SSL/IPsec VPN with FortiClient | Comparable capability, lower licence cost, but a second vendor in a Cisco-based estate |
| WireGuard on a hardened Linux host | Excellent cryptography and throughput, but no commercial support, no posture, no native MFA |

### Selection

**Cisco Secure Client (AnyConnect) remote-access VPN, IKEv2/IPsec, terminated on a redundant
Cisco Secure Firewall pair at the head-office internet edge**, with:

- **Per-user X.509 certificates** issued from an internal CA, plus username/password, plus a
  **push/TOTP second factor** — a three-element authentication that directly replaces the
  single shared password.
- **Authentication delegated to the central AAA service over RADIUS**, so the VPN holds no
  local account store of its own.
- **Posture assessment** before the tunnel is allowed into the internal zones: OS patch
  level, disk encryption and endpoint-protection status.
- **Per-group tunnel policy** — staff, contractors and administrators land in different
  address pools subject to different firewall policy, so a contractor's VPN session can be
  restricted to the specific systems they support.
- **Split-tunnel disabled** for sessions that touch core banking, so traffic is inspected.
- Branch connectivity kept on **site-to-site IPsec** over the existing dedicated links as an
  encryption overlay, rather than trusting the carrier.

### The alternative I seriously considered, and why I rejected it

**Clientless SSL WebVPN** was genuinely attractive for Northbridge's two external IT support
contractors: it needs no software installed on a device Northbridge does not own and cannot
manage, which is otherwise the hardest part of a contractor VPN rollout.

I rejected it on a specific Northbridge detail. The brief says the contractors "require
regular remote access to internal systems" — not to a web application. Clientless VPN only
proxies browser-reachable protocols well; SSH, RDP and database administration tooling are
exactly what IT support contractors need and exactly what clientless handles worst. More
decisively, clientless access cannot perform posture assessment, and these are the two
parties whose devices Northbridge has least visibility of — the brief notes there is no
vendor security assessment process at all. Dropping posture for the *highest*-uncertainty
devices on the network inverts the risk priority. The full client, pushed to a
contractor-owned device as a condition of the support contract, keeps posture in place.

**FortiGate** was the strongest commercial alternative and is cheaper. I rejected it because
Northbridge has no existing firewall team — the brief states it has no dedicated firewall at
all — so every operational skill must be built from zero. Building that skill once, on one
vendor that also supplies the perimeter firewall and the IPS, is worth more to a 450-staff
bank than the licence saving of splitting across two vendors.

### Why this fits Northbridge specifically

Northbridge's remote-access failure is not a *tunnel* failure — the existing VPN presumably
encrypts fine. It is an *identity* failure: one account, no second factor, no accountability.
This proposal is chosen because every element attacks that specific failure. Certificates
make the credential non-shareable by construction (a password can be told to someone over the
phone; a private key cannot). RADIUS delegation means the VPN cannot become another local
account island. Posture addresses the contractor devices the bank has never assessed. And
per-group policy means that when the payment processor integration goes live, contractor
access can be fenced away from the partner zone without rebuilding the VPN.

---

## A1.2 — AAA solution for centralised authentication

### Options considered

| Option | Fit for Northbridge |
|---|---|
| **Cisco Identity Services Engine (ISE)** | RADIUS + TACACS+ + 802.1X + profiling + posture in one policy engine |
| Microsoft NPS with the Entra ID MFA extension | Cheap, familiar, uses the existing directory — but no TACACS+ |
| FreeRADIUS + OpenLDAP + a TOTP module | Zero licence cost, full control, no support contract |
| Aruba ClearPass | Technically close to ISE, but a third vendor |

### Selection

**Cisco ISE as the central AAA and network access control authority**, deployed as a
redundant pair at head office and federated to Northbridge's existing user directory rather
than becoming a new, separate account store. Specifically:

- **RADIUS** for all network access — VPN authentication, 802.1X wired and wireless
  authentication, and guest Wi-Fi onboarding.
- **TACACS+** for device administration on every router, switch and firewall, with **per-command
  authorisation and per-command accounting**.
- **802.1X with dynamic VLAN and dACL assignment**, so a device's identity determines which
  network segment it lands in rather than which socket it was plugged into.
- **Profiling and posture** to classify the point-of-service support equipment and BYOD
  devices the brief says are currently unmanaged.
- **All authentication, authorisation and accounting records forwarded to the central SIEM.**

### The alternative I seriously considered, and why I rejected it

**Microsoft NPS with the Entra ID MFA extension** was a serious candidate. It is inexpensive,
most IT teams already know it, it reuses the directory accounts that already exist, and it
would deliver MFA on the VPN — which is the single most urgent fix in T1. On cost-to-benefit
for that one problem, NPS wins.

I rejected it because of what T2 needs, not what T1 needs. NPS speaks RADIUS only; it has no
TACACS+. TACACS+ command authorisation and accounting is the control that produces a
per-administrator record of every command typed on a switch, router or firewall. T2's central
finding is that Northbridge cannot attribute privileged action to a person, and NPS cannot fix
that for infrastructure — it would leave the network devices on shared local enable passwords,
which is precisely the gap. NPS also has far weaker device profiling, which matters because
the brief describes point-of-service support equipment and personal devices on the network
that nobody currently has an inventory of. Choosing NPS would mean solving the loud problem
and leaving the quiet one, and the quiet one is the audit finding.

### Why this fits Northbridge specifically

Northbridge is not a greenfield network that needs an identity store; it is a decade-old flat
network that needs an *enforcement point*. ISE is proposed because it is simultaneously the
authentication authority for T1 and T2, the enrolment gate for the segmentation the network
needs, and the accounting source the bank needs for audit. One deployment closes the "every
device has its own accounts" finding, the "no individual accountability" finding and the "no
centralised audit trail" finding at the same time. For a bank facing a regulator and a
partner integration in two quarters, a single system that produces defensible access records
is worth more than its licence cost.

---

## A1.3 — Secure network architecture with multiple firewalls and defined zones

### Options considered

| Option | Fit for Northbridge |
|---|---|
| **Three-tier design: internet-edge firewall pair + internal/core firewall pair, seven named zones** | Full separation, defence in depth, explicit partner zone |
| Single collapsed NGFW with multiple DMZ legs | Cheapest, simplest to run, but one device is the whole perimeter |
| Heterogeneous dual-vendor DMZ sandwich | Resists a single-vendor CVE, doubles the skills needed |
| Host-based micro-segmentation over a flat core | Finest granularity, needs an asset inventory Northbridge lacks |

### Selection

**A three-tier, zone-based architecture using two firewall layers**, with traffic crossing at
least one firewall between any two trust levels and two firewalls between the internet and
core banking.

**Tier 1 — Internet edge firewall pair (active/standby).** Terminates the internet circuits,
the remote-access VPN and the branch site-to-site tunnels. Hosts the public-facing zones.

**Tier 2 — Internal/core firewall pair (active/standby).** Separates internal user space from
the regulated core banking environment. Nothing reaches the core banking database without
crossing this device.

**Tier 3 — Switched access layer** with 802.1X-assigned VLANs mapping endpoints into zones.

| Zone | Contents | Inbound policy summary |
|---|---|---|
| **OUTSIDE** | Internet circuits | Deny all except published services |
| **DMZ-PUBLIC** | Online banking portal front end, mobile app API gateway, reverse proxy / WAF | Internet → HTTPS only; no DMZ-initiated path to OUTSIDE except patching via proxy |
| **CORE-BANKING** | Core banking application servers, customer database | Only named application flows from DMZ-PUBLIC and INTERNAL-USERS; no internet path at all |
| **INTERNAL-USERS** | Head office and branch staff LANs, printers | Internet via proxy; core banking via published application ports only |
| **PARTNER-EXTRANET** | The two third-party payment processor connections | Mutual TLS, IP allow-listed, to a single integration broker — never directly to the database |
| **GUEST** | Guest Wi-Fi, point-of-service support equipment | Internet only, with client isolation; no route to any internal zone |
| **MGMT-OOB** | Management interfaces of all network and server infrastructure | Reachable only from a hardened jump host, administrators authenticated via TACACS+ |

Default inter-zone policy is **deny-all with explicit allow**, and every allow rule carries
an owner and a review date.

### The alternative I seriously considered, and why I rejected it

**A single collapsed next-generation firewall with several DMZ interfaces** is the option most
mid-sized organisations actually buy. One device, one licence, one policy to learn, and it can
technically express every zone above as a separate interface. For a bank that currently runs
on a router's built-in firewall, it would still be a transformational improvement, and for a
team with no firewall experience the simplicity is a real safety benefit.

I rejected it on two Northbridge-specific grounds. First, the brief explicitly requires an
architecture "incorporating multiple firewalls", so one device does not satisfy the
requirement. Second, and more substantively: the brief's lead ransomware scenario is a
*compromised branch workstation spreading across an unsegmented network*. That attack starts
**inside** the perimeter. A collapsed design puts the internal user LAN and the core banking
environment on two legs of the same device, so the one policy engine that must stop internal
lateral movement is also the device exposed to the internet — and if it is compromised or
misconfigured, nothing else stands between a branch PC and the customer database. Two tiers
means the internal boundary survives a failure of the external one. For an institution whose
most critical asset is a single database, that separation is worth the second appliance pair.

### Why this fits Northbridge specifically

Three details in the brief drove specific zones. The **PARTNER-EXTRANET** zone exists because
the integration with two payment processors is described as extending trust beyond
Northbridge's own infrastructure for the first time — that trust needs somewhere to terminate
other than the internal network. The **GUEST** zone exists because guest Wi-Fi and
point-of-service support equipment currently share space with core systems. The **MGMT-OOB**
zone exists because there is no centralised authentication and, today, management interfaces
sit on the same flat network as the users. Each zone traces to a stated weakness rather than
to a generic reference design.

---

## A1.4 — IDS/IPS solution

### Options considered

| Option | Fit for Northbridge |
|---|---|
| **Inline Cisco Firepower (Snort 3) IPS licensed on both firewall tiers** | Prevention not just detection, at every zone boundary, no new hardware |
| Open-source Snort 3 sensors on SPAN ports | Free, but detection-only and needs a sensor and an analyst per site |
| Suricata + Zeek sensors feeding a SIEM | Rich protocol metadata, strong for investigation, still passive |
| Flow-based anomaly detection from switch NetFlow | Full east-west coverage, no signatures, weaker on known exploits |

### Selection

**Inline IPS enforced on both firewall tiers using the Firepower/Snort 3 engine with Talos
signature feeds**, configured as follows:

- **Prevention mode inline** on the internet edge for traffic to DMZ-PUBLIC, tuned to a
  web-server and database-protection policy for the online banking portal.
- **Prevention mode inline** on the internal/core tier for all traffic entering CORE-BANKING,
  which is where the ransomware lateral-movement signatures matter most.
- **Detection mode first for 30 days** on internal segments before enabling blocking, to
  build a false-positive baseline against real Northbridge traffic rather than guessing.
- **Signature policy aligned to the actual estate**, with the branch systems the brief
  describes as running outdated software given explicit virtual-patching coverage for the
  relevant known CVEs until the patch programme catches up.
- **All events to the central SIEM** with defined alert severities and an on-call path.

### The alternative I seriously considered, and why I rejected it

**Open-source Snort 3 on SPAN ports** is the option I expected to choose on cost grounds, and
I spent the most time on it. It is free, it uses the same detection engine as the commercial
option, and community plus registered rule sets are good.

I rejected it for two reasons rooted in Northbridge's shape. First, Northbridge has **six
branch offices**. A SPAN-based sensor design needs a sensor appliance, a SPAN session and a
management path at every site where visibility is wanted — seven deployments, seven things to
patch, in an organisation that has no formal patch management process. The inline option adds
a licence to two firewall pairs that are being bought anyway, and covers branch traffic as it
crosses the tunnels into head office. Second, and more importantly, SPAN-based Snort is
**detection-only**. The brief's own worst-case scenario is ransomware that "spread rapidly" —
an attack measured in minutes. Northbridge has no security operations team and no incident
response process, so there is nobody to act on a detection at 3 a.m. A control that alerts
but cannot block is the wrong shape for an organisation with no one on the other end of the
alert; prevention has to be automatic here, not advisory.

I did keep one element of the rejected design. Passive protocol logging is genuinely better
for investigation than IPS alerts alone, so I recommend Zeek-style metadata collection be
revisited once central logging exists — as an addition to the SIEM, not as the IDS/IPS.

### Why this fits Northbridge specifically

The decisive Northbridge detail is the staffing one. The brief describes a newly formed IT
security team at a bank that has never had a firewall, an IDS, central logging or an incident
response process. Any proposal whose value depends on a human reading alerts quickly will
fail here in its first year. Choosing inline prevention on devices already in the design means
the control works on day one with no analyst, and the detection-mode burn-in period is
included precisely so that enabling blocking does not take down the online banking portal —
an availability risk I would not accept without it.
