# Member 3 — Individual Network Hardening Configurations

**Member:** [Member 3 — Full Name / IT Number]
**Configurations:** #5 Zone-Based Policy Firewall (plan-linked) · #6 DHCP snooping and Dynamic ARP Inspection (free choice)

Carried out on the shared group topology in `06_Topology/topology-spec.md`.
Plain-text scripts: `configs/cfg-5-zone-based-firewall.txt`, `configs/cfg-6-dhcp-snooping-dai.txt`.
Screenshot sequence: `06_Topology/screenshot-capture-guide.md`, shots 3.1–3.21.

---

## Configuration 5 — Zone-Based Policy Firewall (OUTSIDE / DMZ / INSIDE)

**Device:** `HQ-R1`, acting as the head-office perimeter firewall
**Requires:** an ISR router model (2911 or similar) with the `securityk9` technology package

### What this configuration achieves

It converts the head-office router from a packet forwarder with an access list into a
**stateful firewall with named trust zones**. The difference is not cosmetic. An access list
evaluates each packet independently against a static rule; a zone-based policy firewall
**inspects** a session, builds state for it, and automatically permits the return traffic
belonging to that session while denying unsolicited traffic in the same direction.

Three consequences matter for Northbridge:

1. **Return traffic no longer needs a rule.** With ACLs, permitting outbound HTTP requires a
   matching inbound permit for the replies — and that inbound permit is a hole an attacker can
   use. With inspection, the reply is permitted because it belongs to a tracked session, and
   nothing else is.
2. **Default-deny becomes the structural default.** In the zone-based model, traffic between
   two zones is dropped unless a `zone-pair` exists and its policy permits it. The absence of
   a rule is a denial, not an accident. Northbridge currently has the inverse: a flat network
   where the absence of a rule is permission.
3. **Zones are named after trust levels, not interfaces.** A new branch interface added to the
   `INSIDE` zone inherits the whole policy immediately, rather than needing its own ACL —
   which matters for an organisation with six branches and no change-control discipline.

The policy implemented:

| Zone pair | Direction | Policy |
|---|---|---|
| `INSIDE → OUTSIDE` | Outbound | Inspect HTTP, HTTPS, DNS, ICMP — staff internet access, stateful |
| `INSIDE → DMZ` | Inbound to DMZ | Inspect HTTPS only — staff may use the portal |
| `OUTSIDE → DMZ` | Public access | Inspect HTTPS **to the portal host only** — the one published service |
| `DMZ → INSIDE` | — | **No zone-pair.** Implicitly and completely denied |
| `OUTSIDE → INSIDE` | — | **No zone-pair.** Implicitly and completely denied |
| `DMZ → OUTSIDE` | — | **No zone-pair.** A compromised web server cannot call home |
| Self zone | Management | SSH from `MGMT-OOB` only |

The three deliberately absent zone-pairs are the most important part of this configuration,
and they should be called out explicitly in the report: **a policy you do not write is a
policy that denies.** `DMZ → INSIDE` being absent is what stops T5's pivot step, and
`DMZ → OUTSIDE` being absent is what stops a compromised portal from exfiltrating or
retrieving a second-stage payload.

### Plan linkage and threats addressed

This implements **Control 5 (zoned network architecture with two firewall tiers and
default-deny inter-zone policy)** from the group's combined layered security plan, and
contributes to **Control 18 (third-party and partner security assurance)**, whose technical
half requires partner traffic to terminate in its own zone rather than on the internal
network. It is the Packet Tracer realisation of the DMZ-sandwich architecture the group
adopted from my proposal A3.3.

> A note on control numbering, since the group plan went through a minimisation pass. My
> original submission referenced a separate control for "next-generation firewall policy with
> default-deny between zones". That control was merged into Control 5 during minimisation,
> because the zone structure and the default-deny policy that governs it are one deployment
> and not two — the reasoning is recorded in the minimisation write-up. This configuration
> implements both halves of the merged control.

- **T5 (SQL injection against the online banking portal):** this configuration does not fix
  the injectable parameter — only code remediation and a WAF do that. What it fixes is **every
  step after step 3 of T5's attack chain.** T5's escalation depends on the web tier sitting in
  the same trust space as the internal network; placing the portal in a `DMZ` zone with no
  `DMZ → INSIDE` and no `DMZ → OUTSIDE` zone-pair means a fully compromised web server is a
  dead end. The database breach remains possible; the network foothold and the outbound
  exfiltration channel do not.
- **T6 (abuse of the third-party payment processor connection):** the same structure gives the
  partner connection somewhere to terminate that is not the internal network. The `DMZ` zone
  in this Packet Tracer build stands in for the `PARTNER-EXTRANET` and
  `INTEGRATION-BROKER` zones of the full design, which a two-interface router cannot represent
  separately.

### Command sequence

```
enable
configure terminal

! --- licensing: ZPF requires the security technology package ---
! (run once, then reload; skip if already active)
license boot module c2900 technology-package securityk9

! =========== STEP 1: define the zones ===========
zone security INSIDE
 description Trusted internal staff and server networks
 exit
zone security OUTSIDE
 description Untrusted - the public internet
 exit
zone security DMZ
 description Semi-trusted - public facing online banking portal
 exit

! =========== STEP 2: classify the traffic ===========
class-map type inspect match-any CM-INSIDE-TO-OUT
 match protocol http
 match protocol https
 match protocol dns
 match protocol icmp
 exit

class-map type inspect match-any CM-WEB-ONLY
 match protocol https
 exit

! Only the published portal host, and only HTTPS.
ip access-list extended ACL-PORTAL
 permit tcp any host 10.10.30.10 eq 443
 exit

class-map type inspect match-all CM-OUT-TO-PORTAL
 match access-group name ACL-PORTAL
 match protocol https
 exit

! =========== STEP 3: define the policies ===========
policy-map type inspect PM-INSIDE-TO-OUT
 class type inspect CM-INSIDE-TO-OUT
  inspect
  exit
 class class-default
  drop log
  exit
 exit

policy-map type inspect PM-INSIDE-TO-DMZ
 class type inspect CM-WEB-ONLY
  inspect
  exit
 class class-default
  drop log
  exit
 exit

policy-map type inspect PM-OUT-TO-DMZ
 class type inspect CM-OUT-TO-PORTAL
  inspect
  exit
 class class-default
  drop log
  exit
 exit

! =========== STEP 4: bind policies to zone pairs ===========
zone-pair security ZP-INSIDE-OUT source INSIDE destination OUTSIDE
 service-policy type inspect PM-INSIDE-TO-OUT
 exit

zone-pair security ZP-INSIDE-DMZ source INSIDE destination DMZ
 service-policy type inspect PM-INSIDE-TO-DMZ
 exit

zone-pair security ZP-OUT-DMZ source OUTSIDE destination DMZ
 service-policy type inspect PM-OUT-TO-DMZ
 exit

! NOTE: ZP-DMZ-INSIDE, ZP-DMZ-OUT and ZP-OUT-INSIDE are
! DELIBERATELY NOT CREATED. Traffic in those directions is dropped
! by the zone-based model's implicit default. This is the control.

! =========== STEP 5: assign interfaces to zones ===========
interface GigabitEthernet0/1
 description To ISP - untrusted
 ip address 203.0.113.2 255.255.255.252
 zone-member security OUTSIDE
 no shutdown
 exit

interface GigabitEthernet0/0.10
 description STAFF-HQ
 zone-member security INSIDE
 exit

interface GigabitEthernet0/0.20
 description CORE-BANKING
 zone-member security INSIDE
 exit

interface GigabitEthernet0/0.30
 description DMZ - online banking portal
 zone-member security DMZ
 exit

end
write memory
```

> **A trap worth knowing and worth writing up.** The moment an interface is placed in a zone,
> all traffic to and from it is denied unless a zone-pair permits it — *including* traffic to
> the router itself, unless the `self` zone is handled. Two interfaces in the **same** zone
> pass traffic freely with no policy, which is why `STAFF-HQ` and `CORE-BANKING` both being in
> `INSIDE` means this configuration does **not** filter between them. That is intentional
> here: internal segmentation between those two is Member 2's Configuration 3 (inter-VLAN
> ACLs) and, in the full design, the internal firewall tier. Stating this division of labour
> in the report shows the two configurations were designed to complement rather than duplicate
> each other.

### Verification commands and expected output

| # | Verification command | What the output must show |
|---|---|---|
| 1 | `show zone security` | All three zones with their member interfaces listed |
| 2 | `show zone-pair security` | Exactly three zone-pairs, each with its service-policy — and visibly **no** DMZ-to-INSIDE pair |
| 3 | `show class-map type inspect` | All three inspect class-maps with their match criteria |
| 4 | `show policy-map type inspect` | The three policies, each ending in `class-default → drop log` |
| 5 | **Positive test:** from `PC-HQ1` (INSIDE), browse `https://10.10.30.10` | Portal loads — the permitted INSIDE→DMZ flow works |
| 6 | **Positive test:** from `PC-INTERNET` (OUTSIDE), browse `https://10.10.30.10` | Portal loads — the published service is reachable from the internet |
| 7 | **Negative test (the key shot):** from `WEB-PORTAL` in the DMZ, `ping 10.10.20.10` | **Fails.** No `DMZ → INSIDE` zone-pair exists. This is T5's pivot step being blocked |
| 8 | **Negative test:** from `WEB-PORTAL`, `ping 8.8.8.8` | **Fails.** No `DMZ → OUTSIDE` zone-pair. A compromised portal cannot call home |
| 9 | **Negative test:** from `PC-INTERNET`, `ping 10.10.10.50` | Fails — no `OUTSIDE → INSIDE` pair |
| 10 | `show policy-map type inspect zone-pair sessions` | Active inspected sessions listed with their state, after the positive tests — this is the proof that **stateful inspection** is running, not just filtering |

> Shot 10 is the one that distinguishes this configuration from an ACL. Shots 7 and 8 are the
> ones that demonstrate the deliberately-absent zone-pairs are doing real work.

### Packet Tracer requirements and limitations

| Item | Note |
|---|---|
| Router model | Must be an ISR (2911 recommended). ZPF is **not** available on the 1941 or on the generic router in some PT versions |
| `license boot module c2900 technology-package securityk9` | Required once, followed by `write memory` and `reload`. Verify with `show version` — look for `securityk9` as Active |
| `match protocol` names | PT supports a subset. If `https` is rejected, match an access-group on TCP 443 instead |
| `drop log` | If `log` is rejected, use plain `drop` and note the substitution |
| `self` zone policy | PT support is inconsistent. If management access to the router breaks after zoning, leave the management subinterface **out** of any zone — an unzoned interface is unaffected by zone policy — and state this as a Packet Tracer accommodation |
| `show policy-map type inspect zone-pair sessions` | If unsupported, use `show policy-map type inspect zone-pair` and rely on the live positive/negative tests |

---

## Configuration 6 — DHCP snooping and Dynamic ARP Inspection (free choice)

**Devices:** `HQ-SW1` and `BR1-SW1`

### What this configuration achieves and the real-world problem it solves

DHCP and ARP are both unauthenticated by design. Any host on a segment can answer a DHCP
request, and any host can assert that it owns any IP address. On a default switch
configuration, both assertions are believed. These two features make the switch verify them
instead.

**DHCP snooping** makes the switch inspect DHCP messages and divide ports into two classes.
On an **untrusted** port — every access port where users live — DHCP *server* messages
(`OFFER`, `ACK`) are dropped outright. Only the **trusted** uplink toward the real DHCP server
may carry them. As it inspects legitimate exchanges, the switch builds a **binding table**
recording which MAC address legitimately holds which IP address on which port in which VLAN.

**Dynamic ARP Inspection** then uses that binding table. Every ARP reply arriving on an
untrusted port is checked against it: if a host claims an IP address that the binding table
says belongs to a different MAC on a different port, the ARP packet is dropped and the event
logged. DAI without DHCP snooping has no table to check against, which is why these two are
one configuration and not two.

The real-world problem is the attack described in Member 2's T4, and it is worth being precise
about the division of labour. Member 2's VLAN segmentation stops a guest on the guest VLAN
from attacking a staff workstation, because they are no longer in the same broadcast domain.
It does **not** stop an attacker who is *inside* the staff segment — which the brief makes
realistic, since **branch network cabinets were found unlocked in at least two locations** and
visitor sign-in is inconsistently enforced. Someone who patches a laptop into a staff port is
in the staff broadcast domain, and segmentation has nothing left to say. DHCP snooping and DAI
are what defeat that attacker.

This is my free-choice configuration. It supports **Control 6 (Layer 2 access hardening
baseline)** and addresses **T4** directly, although T4 is Member 2's threat rather than mine —
which is itself a useful point for the report, since it demonstrates the controls are shared
across the group rather than owned per member.

### Command sequence

```
enable
configure terminal

! =========== DHCP SNOOPING ===========
ip dhcp snooping
ip dhcp snooping vlan 10,20,30,40,99

! Option 82 insertion often breaks relay through a router that is
! not configured to expect it. Disable unless the DHCP server needs it.
no ip dhcp snooping information option

! --- the uplink toward the real DHCP server is the ONLY trusted port ---
interface GigabitEthernet0/1
 description TRUNK to HQ-R1 - trusted for DHCP
 ip dhcp snooping trust
 exit

! --- user access ports: untrusted, and rate limited ---
! The rate limit blunts DHCP starvation, where an attacker exhausts
! the scope by requesting every address.
interface range FastEthernet0/1-4
 ip dhcp snooping limit rate 10
 exit

interface FastEthernet0/10
 description GUEST AP - untrusted, higher rate for many clients
 ip dhcp snooping limit rate 30
 exit

! =========== DYNAMIC ARP INSPECTION ===========
ip arp inspection vlan 10,20,30,40,99

! Additional sanity checks on the ARP packet itself: that the
! Ethernet source MAC matches the ARP sender MAC, that the
! destination MAC matches, and that the IP is not 0.0.0.0 or multicast.
ip arp inspection validate src-mac dst-mac ip

! --- trust only the uplink; every access port is inspected ---
interface GigabitEthernet0/1
 ip arp inspection trust
 exit

interface range FastEthernet0/1-12
 ip arp inspection limit rate 15
 exit

! --- static ARP ACL for the server ports, which do not use DHCP ---
! Servers have static addresses, so there is no DHCP exchange to
! snoop and therefore no binding entry. Without this, DAI would
! drop legitimate server ARP replies.
arp access-list ARP-STATIC-SERVERS
 permit ip host 10.10.20.10 mac host 0001.AAAA.0010
 permit ip host 10.10.20.11 mac host 0001.AAAA.0011
 permit ip host 10.10.30.10 mac host 0001.AAAA.0030
 exit

ip arp inspection filter ARP-STATIC-SERVERS vlan 20
ip arp inspection filter ARP-STATIC-SERVERS vlan 30

! --- automatic recovery from a DAI-triggered err-disable ---
errdisable recovery cause arp-inspection
errdisable recovery cause dhcp-rate-limit
errdisable recovery interval 300

end
write memory
```

> **The static-server ARP ACL is the detail that separates a working configuration from one
> that breaks production.** DAI validates against the DHCP snooping binding table. Statically
> addressed servers never perform a DHCP exchange, so they have no binding entry, so DAI drops
> their ARP replies and the servers become unreachable. Anyone who enables DAI on a server
> VLAN without an ARP ACL has just taken the core banking servers offline. Explaining this in
> the report demonstrates understanding of *why* the control is configured this way, which is
> what the rubric's "explanation makes clear what real-world problem this configuration
> solves" is asking for.
>
> **Why trust only the uplink.** Trust is the entire mechanism. A single wrongly trusted access
> port reopens the whole attack, and the common mistake is trusting a port because a device on
> it "stopped working" after the control was enabled.

### Verification commands and expected output

| # | Verification command | What the output must show |
|---|---|---|
| 1 | `show ip dhcp snooping` | Snooping enabled; VLAN list correct; `Gi0/1` the only trusted interface; rate limits per port |
| 2 | `show ip dhcp snooping binding` | Binding entries — MAC, IP, lease, VLAN, interface — for each DHCP client. **Take this after the PCs have obtained leases**, or the table is empty |
| 3 | `show ip arp inspection` | DAI enabled on the VLAN list; validation checks enabled; forwarded and dropped counters |
| 4 | `show ip arp inspection interfaces` | `Gi0/1` trusted, all access ports untrusted with their rate limits |
| 5 | `show ip arp inspection vlan 10` | Per-VLAN statistics, with the ARP ACL shown for VLANs 20 and 30 |
| 6 | **Positive test:** `PC-HQ1` → `ipconfig /renew`, then `ping 10.10.10.1` | Lease obtained and gateway reachable — legitimate DHCP and ARP still work |
| 7 | **Rogue DHCP test (the key shot):** add a second DHCP server to `Fa0/3` with a scope offering itself as gateway, then renew on `PC-HQ1` | `PC-HQ1` receives the **legitimate** lease. The rogue server's `OFFER` is dropped on the untrusted port |
| 8 | `show ip dhcp snooping` (after the rogue test) | Drop counters incremented on the untrusted interface |
| 9 | `show ip arp inspection` (after the tests) | `Dropped` counter non-zero, proving DAI is actively discarding invalid ARP |
| 10 | `show ip arp inspection log` | Logged violations with source MAC, claimed IP and ingress port |

> Shots 7 and 8 together are the demonstration that earns the marks: a rogue DHCP server
> physically present on the segment and *failing*. Shots 1–5 only prove the configuration was
> entered.

### Packet Tracer requirements and limitations

| Command | If unsupported in your PT version |
|---|---|
| `ip arp inspection validate src-mac dst-mac ip` | Frequently unsupported — omit and note it as production configuration |
| `arp access-list` / `ip arp inspection filter` | Support varies. If rejected, set the server ports to `ip arp inspection trust` instead and **explain in the report that this is a Packet Tracer accommodation, and that an ARP ACL is the correct production answer** — this turns a tool limitation into evidence of understanding |
| `errdisable recovery cause arp-inspection` | Often unsupported — omit, recover manually |
| `no ip dhcp snooping information option` | Supported on 2960; keep it, as leaving option 82 on is a common cause of DHCP failing through a relay |
| `show ip arp inspection log` | If unsupported, use the `show ip arp inspection` drop counters plus the live rogue-server test |
| DHCP server | Either a Packet Tracer Server device with the DHCP service on, or `ip dhcp pool` on `HQ-R1`. If the pool is on the router, `Gi0/1` on the switch is still the correct trusted port |
