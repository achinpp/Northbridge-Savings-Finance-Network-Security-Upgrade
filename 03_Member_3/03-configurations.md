# Member 3 — Individual Network Hardening Configurations

**Member:** [Member 3 — Full Name / IT Number]
**Configurations:** #5 Internet edge firewall — static PAT + default-deny edge ACL (plan-linked) · #6 DHCP snooping and Dynamic ARP Inspection (free choice)

Carried out on the shared group topology in `06_Topology/topology-spec.md`.
Plain-text scripts: `configs/cfg-5-edge-firewall-nat.txt`, `configs/cfg-6-dhcp-snooping-dai.txt`.
Screenshot sequence: `06_Topology/screenshot-capture-guide.md`, shots 3.1–3.21.

---

## Configuration 5 — Internet edge firewall: static PAT publishing and a default-deny edge ACL

**Device:** `HQ-R1`, interface `GigabitEthernet0/1` (OUTSIDE)

### A note on what was intended, and why this differs

My technology proposal (A3.3) and the group's adopted architecture specify a **stateful**
dual-firewall DMZ sandwich. The intended Packet Tracer implementation was a **Zone-Based Policy
Firewall** — `zone security`, `class-map type inspect`, `policy-map type inspect`, `zone-pair`.

**Packet Tracer 8.2 on the ISR 2911 implements no stateful firewall of any kind.** This was
established by direct test rather than assumed:

| Command | Result |
|---|---|
| `zone security INSIDE` | `% Invalid input detected` |
| `ip inspect name FW-DMZ http` | `% Invalid input detected` |
| `permit tcp any any reflect SESSIONS` | `% Invalid input detected` |
| `ip ?` | no `inspect` keyword in the parser |
| `license boot module c2900 technology-package securityk9` | accepted silently, but `show version` still reports `security / disable / None` for *Next reboot* after a reload — the command is a no-op |

This configuration therefore implements the **same perimeter policy** using the tools the
platform does provide: static PAT for publishing, and an extended ACL for default-deny inbound.

**What the substitution costs, stated precisely.** A zone firewall *inspects a session* and
permits its return traffic automatically. A static ACL cannot, so return traffic has to be
permitted by rule using the `established` keyword — which only checks whether the TCP ACK or
RST flag is set. An attacker who crafts a packet with ACK set passes that rule; a stateful
firewall would reject it, because no matching session exists in its state table. UDP and ICMP
are worse still, having no `established` equivalent, so their return traffic must be permitted
by protocol and type — broader than a session table would allow.

That gap is exactly why the group's plan specifies next-generation firewalls at both tiers
rather than router ACLs, and it is worth stating rather than glossing: the demonstrable
configuration is weaker than the recommended one, in a way I can name.

### What this configuration achieves

It establishes an explicit, enforced boundary between Northbridge and the internet, where
previously the brief describes only "the basic firewall/router functionality built into its
internet-facing router".

Three mechanisms, and they matter in combination:

1. **A declared NAT boundary.** `ip nat inside` and `ip nat outside` make the perimeter an
   explicit property of the configuration rather than something implied by routing.
2. **Publishing by exception.** Static PAT maps **one** public socket to **one** internal
   socket: `203.0.113.2:443 → 10.10.30.10:443`. The online banking portal becomes the only
   system in the estate with any inbound path from the internet, on one port. Every other
   internal host is unreachable from outside **by construction** — no translation exists for
   them, so an inbound packet has nowhere to be delivered even before the ACL is consulted.
3. **Default-deny inbound.** `EDGE-IN` permits the published service and return traffic, then
   explicitly denies internet-to-internal and everything else.

**Outbound PAT deliberately excludes VLAN 20.** The core banking servers have no business
initiating connections to the internet, so they are omitted from the `NAT-ALLOWED` list — the
same principle as the DMZ egress restriction in the group's design, applied at the perimeter.

### Plan linkage and threats addressed

Implements **Control 5** (zoned architecture with default-deny at the perimeter) and the
technical half of **Control 18** (partner traffic terminating at a controlled boundary rather
than on the internal network).

- **T5 — SQL injection against the online banking portal.** This does not fix the injectable
  parameter; only code remediation and a WAF do that (Control 11). What it fixes is the
  *blast radius*. The portal is published on one socket, so nothing else in the estate is
  internet-reachable, and a compromised web tier has no inbound path to pivot through.
- **T6 — abuse of the third-party payment processor connection.** The same structure gives the
  partner integration a controlled place to terminate. In the full design that is the
  `PARTNER-EXTRANET` zone and the integration broker; on a two-interface router the published-
  socket model stands in for it.

### Command sequence

Full script with comments: `configs/cfg-5-edge-firewall-nat.txt`.

```
enable
configure terminal

! --- declare the NAT boundary ---
interface GigabitEthernet0/1
 description OUTSIDE - to ISP - untrusted
 ip nat outside
 exit
interface GigabitEthernet0/0.10
 ip nat inside
 exit
interface GigabitEthernet0/0.20
 ip nat inside
 exit
interface GigabitEthernet0/0.30
 ip nat inside
 exit
interface GigabitEthernet0/0.40
 ip nat inside
 exit

! --- publish the portal, and nothing else ---
ip nat inside source static tcp 10.10.30.10 443 203.0.113.2 443

! --- outbound PAT: staff and guest only, never core banking ---
ip access-list extended NAT-ALLOWED
 remark Staff and guest may browse out; core banking may not
 permit ip 10.10.10.0 0.0.0.255 any
 permit ip 10.10.40.0 0.0.0.255 any
 deny   ip any any
 exit
ip nat inside source list NAT-ALLOWED interface GigabitEthernet0/1 overload

! --- the edge ACL: default-deny inbound ---
ip access-list extended EDGE-IN
 remark The only published service - online banking portal over HTTPS
 permit tcp any host 203.0.113.2 eq 443
 remark Return traffic for sessions initiated from inside
 permit tcp any any established
 permit udp any eq 53 any
 permit icmp any any echo-reply
 permit icmp any any unreachable
 permit icmp any any time-exceeded
 remark No path from the internet to any internal network
 deny   ip any 10.10.0.0 0.0.255.255
 remark Default deny
 deny   ip any any
 exit

interface GigabitEthernet0/1
 ip access-group EDGE-IN in
 exit

end
write memory
```

> **Why the explicit `deny ip any 10.10.0.0 0.0.255.255` when the final deny would catch it
> anyway.** The implicit deny at the end of every ACL has no visible match counter. Writing the
> internet-to-internal block as its own line creates a countable rule, so it can be *shown*
> refusing real traffic. That is the difference between evidencing a control and configuring
> one — the same reasoning behind the explicit denies in Member 2's Configuration 3.
>
> **Why the test is constructed as it is.** `ISP-R1` holds a static route for `10.10.0.0/16`,
> added when the topology was built. That is deliberate: without it, a ping from the internet to
> an internal host would fail because the ISP had nowhere to send it, which proves nothing about
> this firewall. With the route in place the packet genuinely arrives at `HQ-R1` and is refused
> there, so the only thing that can block it is the control being tested.

### Verification commands and expected output

| # | Verification command | What the output must show |
|---|---|---|
| 1 | `show ip nat statistics` | Inside and outside interfaces listed, with translation counts |
| 2 | `show running-config \| include ip nat` | The static PAT entry and the overload entry |
| 3 | `show access-lists EDGE-IN` | All rules in order, **counters at zero** — the "before" half of the pair |
| 4 | **Positive test:** from `PC-INTERNET`, browse `https://203.0.113.2` | The portal loads — the published service is reachable on its public socket |
| 5 | `show ip nat translations` | The static entry plus the live session, e.g. `tcp 203.0.113.2:443 10.10.30.10:443 198.51.100.50:1025`. Proof the translation is carrying traffic, not merely configured |
| 6 | **Negative test:** from `PC-INTERNET`, `ping 10.10.10.50` | **Fails** — denied by `EDGE-IN` |
| 7 | **Negative test:** from `PC-INTERNET`, `ping 10.10.20.10` | **Fails** — core banking unreachable from the internet |
| 8 | **Positive test:** from `PC-HQ1`, `ping 198.51.100.50` | Succeeds — outbound PAT plus the `echo-reply` permit |
| 9 | `show ip nat translations` | An ICMP translation from `10.10.10.50` to `203.0.113.2`, proving internal addressing is hidden on the way out |
| 10 | `show access-lists EDGE-IN` | `deny ip any 10.10.0.0 0.0.255.255` now has a **non-zero** match count from steps 6 and 7, and the 443 permit has counted the portal session. Paired with step 3 at zero, a complete before/after on one command |

> Steps 5 and 10 are the two that carry the marks. Step 5 shows address translation actually
> happening; step 10 shows the perimeter refusing real traffic.

### Division of labour with Member 2's Configuration 3

Worth stating explicitly, because both configurations use extended ACLs. Member 2's filters
**internal zone-to-zone** traffic on the router subinterfaces. This one filters traffic crossing
the **internet perimeter** on the WAN interface, and adds address translation. Different
interface, different threat direction, different mechanism — two complementary enforcement
points in one layered design, not duplicates.

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
ip arp inspection vlan 10,40

! Additional sanity checks on the ARP packet itself: that the
! Ethernet source MAC matches the ARP sender MAC, that the
! destination MAC matches, and that the IP is not 0.0.0.0 or multicast.
! ip arp inspection validate src-mac dst-mac ip   <- REJECTED by Packet Tracer 8.2

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
| `! ip arp inspection validate src-mac dst-mac ip   <- REJECTED by Packet Tracer 8.2` | Frequently unsupported — omit and note it as production configuration |
| `arp access-list` / `ip arp inspection filter` | Support varies. If rejected, set the server ports to `ip arp inspection trust` instead and **explain in the report that this is a Packet Tracer accommodation, and that an ARP ACL is the correct production answer** — this turns a tool limitation into evidence of understanding |
| `errdisable recovery cause arp-inspection` | Often unsupported — omit, recover manually |
| `no ip dhcp snooping information option` | Supported on 2960; keep it, as leaving option 82 on is a common cause of DHCP failing through a relay |
| `show ip arp inspection log` | If unsupported, use the `show ip arp inspection` drop counters plus the live rogue-server test |
| DHCP server | Either a Packet Tracer Server device with the DHCP service on, or `ip dhcp pool` on `HQ-R1`. If the pool is on the router, `Gi0/1` on the switch is still the correct trusted port |
