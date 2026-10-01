# Member 2 — Individual Network Hardening Configurations

**Member:** [Member 2 — Full Name / IT Number]
**Configurations:** #3 VLAN segmentation with inter-VLAN extended ACLs (plan-linked) · #4 Switchport port security (free choice)

Carried out on the shared group topology in `06_Topology/topology-spec.md`.
Plain-text scripts: `configs/cfg-3-vlan-segmentation-acl.txt`, `configs/cfg-4-port-security.txt`.
Screenshot sequence: `06_Topology/screenshot-capture-guide.md`, shots 2.1–2.19.

---

## Configuration 3 — VLAN segmentation with inter-VLAN extended ACLs

**Devices:** `HQ-SW1` (VLANs, access ports, trunk) and `HQ-R1` (router-on-a-stick
subinterfaces, inter-VLAN ACLs)

### What this configuration achieves

It replaces Northbridge's single flat network with five separate Layer 3 segments and then
places a filtering point between them, so that reaching another segment requires passing a
rule rather than merely sending a packet.

Two distinct things are happening and both are necessary:

1. **Segmentation (VLANs).** Guest Wi-Fi, staff machines, the core banking servers, the DMZ
   and the management network are moved into separate broadcast domains. This alone stops
   every Layer 2 attack from crossing between them — a rogue DHCP server on the guest VLAN
   can no longer answer a staff workstation's `DHCPDISCOVER`, because the two are not in the
   same broadcast domain any more.
2. **Filtering (extended ACLs on the subinterfaces).** VLANs on their own only force traffic
   through the router; they do not restrict it. The ACLs are what turn the router from a
   transit point into a policy enforcement point, implementing default-deny between zones
   with explicit, named allowances.

The policy encoded in the ACLs:

| From | To CORE-BANKING | To STAFF | To MGMT | To Internet |
|---|---|---|---|---|
| **STAFF (VLAN 10)** | Application ports only (1521, 443) | — | Denied | Permitted |
| **GUEST (VLAN 40)** | Denied | Denied | Denied | Permitted only |
| **DMZ (VLAN 30)** | App port to CORE-APP only | Denied | Denied | Denied (no DMZ-initiated egress) |
| **CORE-BANKING (VLAN 20)** | — | Denied (servers do not initiate to users) | Denied | Denied |
| **MGMT (VLAN 99)** | Permitted | Permitted | — | Permitted |

The **GUEST deny-to-everything-internal** rule and the **DMZ-cannot-initiate-outbound** rule
are the two that matter most, and both are inversions of the current state.

### Plan linkage and threats addressed

This implements **Control 5 (zoned network architecture with default-deny inter-zone policy)**
and **Control 6 (Layer 2 access hardening baseline)** in part, from the group's combined
layered security plan.

- **T3 (ransomware propagation across the flat network):** this is the control that breaks
  T3's propagation step. T3's attack chain depends on a branch workstation being able to
  enumerate and reach head-office servers with nothing in between. Once STAFF and
  CORE-BANKING are separate VLANs with an ACL permitting only ports 1521 and 443 to named
  server addresses, the lateral movement protocols ransomware relies on — SMB on 445, RPC on
  135, WMI, RDP on 3389 — are denied by the implicit deny at the end of the list. The
  foothold still happens; the spread does not.
- **T4 (rogue DHCP and ARP spoofing from guest Wi-Fi):** separating GUEST into its own VLAN
  removes the shared broadcast domain that T4's entire attack depends on. An ARP or DHCP
  attack is confined to a segment containing only other guests.

### Command sequence

**Part A — on `HQ-SW1`:**

```
enable
configure terminal

! --- create the zones ---
vlan 10
 name STAFF-HQ
 exit
vlan 20
 name CORE-BANKING
 exit
vlan 30
 name DMZ
 exit
vlan 40
 name GUEST
 exit
vlan 99
 name MGMT-OOB
 exit

! --- a deliberately unused VLAN to park dead ports in ---
vlan 999
 name BLACKHOLE-UNUSED
 exit

! --- access ports, assigned to zones ---
interface range FastEthernet0/1-4
 switchport mode access
 switchport access vlan 10
 description STAFF-HQ workstations
 exit

interface range FastEthernet0/5-8
 switchport mode access
 switchport access vlan 20
 description CORE-BANKING servers
 exit

interface FastEthernet0/9
 switchport mode access
 switchport access vlan 30
 description DMZ web portal
 exit

interface FastEthernet0/10
 switchport mode access
 switchport access vlan 40
 description GUEST wifi AP
 exit

interface range FastEthernet0/11-12
 switchport mode access
 switchport access vlan 99
 description MGMT-OOB - AAA, syslog, jump host
 exit

! --- park every unused port in the blackhole VLAN and shut it ---
interface range FastEthernet0/13-24
 switchport mode access
 switchport access vlan 999
 shutdown
 description UNUSED - administratively down
 exit

! --- trunk to the router, with an explicit allowed list ---
interface GigabitEthernet0/1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30,40,99
 switchport trunk native vlan 999
 switchport nonegotiate
 description TRUNK to HQ-R1
 exit

end
write memory
```

> **Why `native vlan 999` and `nonegotiate`.** The default native VLAN is 1, and VLAN 1 is
> also where every unconfigured port lands. Leaving the native VLAN at 1 means a frame sent
> untagged by an attacker on an access port can be delivered into the trunk's native VLAN —
> the VLAN hopping attack. Moving the native VLAN to an unused one, and disabling DTP
> negotiation so an attacker cannot talk a port into becoming a trunk, closes both. These two
> lines are the ones a marker looks for to distinguish segmentation from *secure*
> segmentation.

**Part B — on `HQ-R1` (router-on-a-stick plus the inter-VLAN policy):**

```
enable
configure terminal

interface GigabitEthernet0/0
 no ip address
 no shutdown
 exit

interface GigabitEthernet0/0.10
 encapsulation dot1Q 10
 ip address 10.10.10.1 255.255.255.0
 description STAFF-HQ gateway
 exit
interface GigabitEthernet0/0.20
 encapsulation dot1Q 20
 ip address 10.10.20.1 255.255.255.0
 description CORE-BANKING gateway
 exit
interface GigabitEthernet0/0.30
 encapsulation dot1Q 30
 ip address 10.10.30.1 255.255.255.0
 description DMZ gateway
 exit
interface GigabitEthernet0/0.40
 encapsulation dot1Q 40
 ip address 10.10.40.1 255.255.255.0
 description GUEST gateway
 exit
interface GigabitEthernet0/0.99
 encapsulation dot1Q 99
 ip address 10.10.99.1 255.255.255.0
 description MGMT-OOB gateway
 exit

! ================= POLICY =================

! --- STAFF: core banking by application port only, no management ---
ip access-list extended STAFF-IN
 remark Permit DNS and DHCP infrastructure
 permit udp any any eq 53
 permit udp any any eq 67
 remark Core banking - named servers, named ports only
 permit tcp 10.10.10.0 0.0.0.255 host 10.10.20.10 eq 1521
 permit tcp 10.10.10.0 0.0.0.255 host 10.10.20.11 eq 443
 remark Deny all other access to the core banking zone
 deny   ip 10.10.10.0 0.0.0.255 10.10.20.0 0.0.0.255 log
 remark Staff must never reach the management network
 deny   ip 10.10.10.0 0.0.0.255 10.10.99.0 0.0.0.255 log
 remark Internet and everything else
 permit ip 10.10.10.0 0.0.0.255 any
 exit

! --- GUEST: internet only. Nothing internal, at all. ---
ip access-list extended GUEST-IN
 permit udp any any eq 53
 permit udp any any eq 67
 deny   ip 10.10.40.0 0.0.0.255 10.0.0.0 0.255.255.255 log
 deny   ip 10.10.40.0 0.0.0.255 192.168.0.0 0.0.255.255 log
 permit ip 10.10.40.0 0.0.0.255 any
 exit

! --- DMZ: may reach the app server, may not initiate anywhere else ---
ip access-list extended DMZ-IN
 permit tcp host 10.10.30.10 host 10.10.20.11 eq 443
 deny   ip 10.10.30.0 0.0.0.255 10.0.0.0 0.255.255.255 log
 deny   ip 10.10.30.0 0.0.0.255 192.168.0.0 0.0.255.255 log
 deny   ip any any log
 exit

! --- CORE-BANKING: servers reply, they do not initiate inwards ---
ip access-list extended CORE-IN
 permit tcp 10.10.20.0 0.0.0.255 any established
 permit udp any any eq 53
 permit ip 10.10.20.0 0.0.0.255 host 10.10.99.11
 deny   ip 10.10.20.0 0.0.0.255 10.10.10.0 0.0.0.255 log
 deny   ip 10.10.20.0 0.0.0.255 10.10.40.0 0.0.0.255 log
 deny   ip any any log
 exit

! --- apply inbound on each subinterface, closest to the source ---
interface GigabitEthernet0/0.10
 ip access-group STAFF-IN in
 exit
interface GigabitEthernet0/0.40
 ip access-group GUEST-IN in
 exit
interface GigabitEthernet0/0.30
 ip access-group DMZ-IN in
 exit
interface GigabitEthernet0/0.20
 ip access-group CORE-IN in
 exit

end
write memory
```

> **Why inbound, not outbound.** An ACL applied inbound on the source subinterface drops the
> packet before the router routes it, so the denied traffic never consumes a routing lookup
> and never reaches another interface's queue. Applying the same policy outbound would work
> but filters later and makes the rule set harder to read, because one outbound list has to
> carry rules for every possible source. Filtering closest to the source is the standard
> practice the labs use and it is worth stating in the report.

### Verification commands and expected output

| # | Verification command | What the output must show |
|---|---|---|
| 1 | `show vlan brief` (on HQ-SW1) | All six VLANs present with the right ports in each; Fa0/13–24 in VLAN 999 |
| 2 | `show interfaces trunk` (on HQ-SW1) | Gi0/1 trunking, allowed VLANs 10,20,30,40,99, native VLAN 999 |
| 3 | `show interfaces status` (on HQ-SW1) | Unused ports `disabled`, not `notconnect` |
| 4 | `show ip interface brief` (on HQ-R1) | All five subinterfaces up with the correct gateway addresses |
| 5 | `show ip route` (on HQ-R1) | Five connected routes, one per VLAN |
| 6 | `show access-lists` (on HQ-R1) | All four named lists with their rules in the right order |
| 7 | **Positive test:** from `PC-HQ1` (10.10.10.50), `telnet 10.10.20.10 1521` | Connects — the permitted application flow still works |
| 8 | **Negative test (the key shot):** from `PC-HQ1`, `ping 10.10.20.10` | **Fails.** ICMP is not in the permit list, so the implicit deny catches it. This proves default-deny is in force rather than assumed |
| 9 | **Negative test:** from `PC-GUEST` (10.10.40.50), `ping 10.10.20.10` and `ping 10.10.10.50` | Both fail — guest cannot reach core banking or staff |
| 10 | `show access-lists` again, immediately after the failed tests | **Match counters on the `deny ... log` lines have incremented.** This is the single most valuable screenshot in the configuration: it shows the ACL actively denying real traffic, not merely existing in the configuration |

> Step 10 is the difference between "Good" and "Excellent" on this rubric row. A screenshot of
> `show access-lists` taken before any traffic shows zero matches and proves nothing about
> whether the list works.

---

## Configuration 4 — Switchport port security (free choice)

**Devices:** `HQ-SW1` and `BR1-SW1` access ports

### What this configuration achieves and the real-world problem it solves

VLAN segmentation decides which zone a *port* belongs to. It says nothing about which
*device* is allowed to use that port. Port security binds the two together: a port configured
for the staff VLAN will only carry traffic for the MAC address that is supposed to be there,
and will shut itself down if a different device appears.

The real-world problem is the one the brief describes directly: **"physical access to
networking equipment in branch back offices is similarly uncontrolled, with cabinets left
unlocked in at least two locations during a recent informal walkthrough"**, alongside visitor
sign-ins that are inconsistently enforced and no camera coverage at branch entry points. In
that environment an unlocked cabinet is an open network port in a trusted VLAN. Port security
turns that port from a free connection into an alarm.

Three concrete attacks it defeats:

- **Rogue device connection.** A visitor's laptop plugged into a staff port is denied and the
  port is disabled, rather than silently joining the staff VLAN.
- **MAC flooding / CAM table overflow.** The `maximum` limit caps how many MAC addresses a
  port may learn. A flooding tool trying to exhaust the switch's CAM table — which would force
  the switch to behave like a hub and expose all traffic to a sniffer — trips the violation
  action on the first port it tries.
- **Unauthorised hub or switch.** A small unmanaged switch added under a desk to share a port
  is detected as a second MAC address on the port.

This is my free-choice configuration. It is not a separately numbered control in the group
plan, but it is the enforcement mechanism that makes Control 6's Layer 2 baseline real, and it
directly addresses the physical-access weakness that T4 relies on.

### Command sequence

```
enable
configure terminal

! --- STAFF access ports: one device per port, learned and remembered ---
interface range FastEthernet0/1-4
 switchport mode access
 switchport access vlan 10
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address sticky
 switchport port-security violation shutdown
 switchport port-security aging time 0
 spanning-tree portfast
 spanning-tree bpduguard enable
 exit

! --- CORE-BANKING server ports: static MAC, never learned dynamically ---
! A server's MAC does not change, so pinning it is both safe and stronger
! than sticky learning - there is no learning window to race.
interface FastEthernet0/5
 switchport mode access
 switchport access vlan 20
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address 0001.AAAA.0010
 switchport port-security violation shutdown
 exit

! --- GUEST AP port: multiple MACs are legitimate behind an AP, but capped ---
interface FastEthernet0/10
 switchport mode access
 switchport access vlan 40
 switchport port-security
 switchport port-security maximum 20
 switchport port-security violation restrict
 exit

! --- automatic recovery, so a violation is not a site visit ---
errdisable recovery cause psecure-violation
errdisable recovery interval 300

end
write memory
```

> **Why the violation action differs per port type.** `shutdown` on staff and server ports —
> a violation there is almost certainly an attack or an unauthorised device, and the port
> should stop. `restrict` on the guest AP port — a violation there is most likely the
> twenty-first guest phone associating, and taking the whole access point offline would be a
> self-inflicted denial of service. Choosing the action per role rather than applying one
> setting everywhere is the judgement the rubric is looking for, and it is worth saying so
> explicitly in the report.
>
> **Why `aging time 0` on staff ports.** Sticky addresses that age out create a window in
> which a new device can claim the port. Zero means never age, so the first legitimate device
> holds the port until an administrator clears it.
>
> **Why `errdisable recovery`.** Without it, a tripped port in Branch 5 stays down until
> someone drives there. Five minutes of automatic recovery keeps the security benefit (the
> attack is interrupted and logged) without creating an operational burden that would get the
> control switched off within a month.

### Verification commands and expected output

| # | Verification command | What the output must show |
|---|---|---|
| 1 | `show port-security` | Summary table: every secured port, max count, current count, violation count and action |
| 2 | `show port-security interface FastEthernet0/1` | `Port Security: Enabled`, `Port Status: Secure-up`, `Violation Mode: Shutdown`, `Maximum: 1` |
| 3 | `show port-security address` | The sticky MAC addresses learned, with `SecureSticky` type and the correct VLAN |
| 4 | `show running-config interface FastEthernet0/1` | The sticky MAC now written into the running configuration — proof that `sticky` persisted the learned address |
| 5 | **Violation test:** in Packet Tracer, delete `PC-HQ1` from Fa0/1 and connect a different PC to the same port, then send traffic | — |
| 6 | `show port-security interface FastEthernet0/1` (after the violation) | `Port Status: Secure-shutdown`, `SecurityViolation count: 1` |
| 7 | `show interfaces FastEthernet0/1 status` | `err-disabled` |
| 8 | `show interfaces FastEthernet0/1` | Log line recording the security violation with the offending MAC address |
| 9 | **Recovery test:** `shutdown` then `no shutdown` on the port after re-attaching the original PC | Port returns to `Secure-up` |

> Shots 6 and 7 are the ones that earn the marks. Screenshots 1–4 only show the configuration
> was typed; shot 6 shows it actually caught something. The brief's rubric specifically wants
> "verification output ... clearly shows the expected result", and a violation counter moving
> from 0 to 1 is that result.

### Commands to check on your Packet Tracer build

| Command | If unsupported in your PT version |
|---|---|
| `interface range FastEthernet0/1-4` | Supported on most PT switch models; otherwise configure each port individually |
| `switchport port-security aging time 0` | Omit if rejected; aging is off by default |
| `errdisable recovery cause psecure-violation` | Often unsupported in PT — omit and recover manually with `shutdown` / `no shutdown`, noting it as production configuration |
| `switchport trunk native vlan 999` | Supported; make sure VLAN 999 exists on both ends or the trunk logs a mismatch |
| `permit tcp ... established` | Supported on PT router images; if rejected, replace with explicit permits for the reply ports and note the substitution |
| `remark` lines inside a named ACL | Supported in most PT images; harmless to omit |
