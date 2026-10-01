# Shared Packet Tracer Topology Specification

All eight hardening configurations are carried out on this one topology, so build it once and
save it as `Northbridge-NS.pkt` before any member starts configuring. Save a copy per
configuration as you go (`Northbridge-NS-cfg1.pkt`, `-cfg2.pkt`, …) so a mistake in one does
not destroy the evidence for another.

The topology is a **representative** cut of Northbridge's estate, as the brief allows: head
office plus **one** branch rather than six, because one branch demonstrates every control and
six would only multiply the clicking.

---

## 1. Device list

| Device | Model | Role |
|---|---|---|
| `HQ-R1` | **ISR 2911** | Head-office edge router, inter-VLAN routing, perimeter firewall (ZPF), IPsec endpoint, NTP master |
| `HQ-SW1` | **2960-24TT** | Head-office access switch |
| `MGMT-SW1` | 2960-24TT | Out-of-band management switch |
| `BR1-R1` | **ISR 2911** | Branch 1 router, IPsec endpoint |
| `BR1-SW1` | 2960-24TT | Branch 1 access switch |
| `ISP-R1` | 1941 or 2911 | Simulated internet |
| `CORE-DB` | Server | Core banking database |
| `CORE-APP` | Server | Core banking application |
| `WEB-PORTAL` | Server | Online banking portal (DMZ), HTTP/HTTPS service on |
| `AAA-SRV` | Server | AAA service (RADIUS + TACACS+) |
| `SYSLOG-SRV` | Server | Syslog service |
| `PC-ADMIN` | PC | Administrator jump host |
| `PC-HQ1`, `PC-HQ2` | PC | Head-office staff workstations |
| `PC-GUEST` | PC | Guest Wi-Fi client (wired stand-in) |
| `PC-BR1` | PC | Branch 1 staff workstation |
| `PC-BR1-GUEST` | PC | Branch 1 guest client |
| `PC-INTERNET` | PC | External attacker / public internet client |
| `ROGUE-DHCP` | Server | **Added only for Configuration 6's rogue-DHCP test**, then removed |
| `PC-ROGUE` | PC | **Added only for Configuration 4's port-security violation test** |

> **The router model matters.** Zone-Based Policy Firewall (Configuration 5) and IPsec crypto
> (Configuration 7) both require an **ISR 2911** with the `securityk9` technology package. They
> are unavailable on the 1941 and on the generic router in most Packet Tracer versions. Use the
> 2911 for `HQ-R1` and `BR1-R1` or those two configurations cannot be completed.

## 2. VLAN plan

### Head office (on `HQ-SW1`)

| VLAN | Name | Subnet | Gateway | Ports on HQ-SW1 |
|---|---|---|---|---|
| 10 | `STAFF-HQ` | 10.10.10.0/24 | 10.10.10.1 | Fa0/1 – Fa0/4 |
| 20 | `CORE-BANKING` | 10.10.20.0/24 | 10.10.20.1 | Fa0/5 – Fa0/8 |
| 30 | `DMZ` | 10.10.30.0/24 | 10.10.30.1 | Fa0/9 |
| 40 | `GUEST` | 10.10.40.0/24 | 10.10.40.1 | Fa0/10 |
| 99 | `MGMT-OOB` | 10.10.99.0/24 | 10.10.99.1 | Fa0/11 – Fa0/12 |
| 999 | `BLACKHOLE-UNUSED` | — (no gateway) | — | Fa0/13 – Fa0/24, shut; also the trunk native VLAN |

### Branch 1 (on `BR1-SW1`)

| VLAN | Name | Subnet | Gateway | Ports on BR1-SW1 |
|---|---|---|---|---|
| 110 | `STAFF-BR1` | 192.168.1.0/24 | 192.168.1.1 | Fa0/1 – Fa0/4 |
| 140 | `GUEST-BR1` | 192.168.14.0/24 | 192.168.14.1 | Fa0/10 |
| 999 | `BLACKHOLE-UNUSED` | — | — | Fa0/13 – Fa0/24, shut; trunk native VLAN |

## 3. Addressing

### Router interfaces

| Device | Interface | Address | Notes |
|---|---|---|---|
| `HQ-R1` | `Loopback0` | 10.10.1.1/32 | **Management address.** Used by Member 1's SSH config and Member 4's `logging source-interface` |
| `HQ-R1` | `Gi0/0` | no IP | Trunk to `HQ-SW1 Gi0/1` |
| `HQ-R1` | `Gi0/0.10` | 10.10.10.1/24 | `encapsulation dot1Q 10` |
| `HQ-R1` | `Gi0/0.20` | 10.10.20.1/24 | `encapsulation dot1Q 20` |
| `HQ-R1` | `Gi0/0.30` | 10.10.30.1/24 | `encapsulation dot1Q 30` |
| `HQ-R1` | `Gi0/0.40` | 10.10.40.1/24 | `encapsulation dot1Q 40` |
| `HQ-R1` | `Gi0/0.99` | 10.10.99.1/24 | `encapsulation dot1Q 99` |
| `HQ-R1` | `Gi0/1` | 203.0.113.2/30 | To `ISP-R1`. Zone `OUTSIDE` |
| `HQ-R1` | `Gi0/2` | 10.10.255.1/30 | WAN to `BR1-R1`. IPsec crypto map applied here |
| `BR1-R1` | `Loopback0` | 10.10.2.1/32 | Management address |
| `BR1-R1` | `Gi0/0` | no IP | Trunk to `BR1-SW1 Gi0/1` |
| `BR1-R1` | `Gi0/0.110` | 192.168.1.1/24 | `encapsulation dot1Q 110` |
| `BR1-R1` | `Gi0/0.140` | 192.168.14.1/24 | `encapsulation dot1Q 140` |
| `BR1-R1` | `Gi0/1` | 10.10.255.2/30 | WAN to `HQ-R1`. IPsec crypto map applied here |
| `ISP-R1` | `Gi0/0` | 203.0.113.1/30 | To `HQ-R1` |
| `ISP-R1` | `Gi0/1` | 198.51.100.1/24 | To `PC-INTERNET` |

### Hosts and servers

| Host | VLAN | Address | Gateway | Connected to |
|---|---|---|---|---|
| `CORE-DB` | 20 | 10.10.20.10/24 | 10.10.20.1 | `HQ-SW1 Fa0/5` |
| `CORE-APP` | 20 | 10.10.20.11/24 | 10.10.20.1 | `HQ-SW1 Fa0/6` |
| `WEB-PORTAL` | 30 | 10.10.30.10/24 | 10.10.30.1 | `HQ-SW1 Fa0/9` |
| `PC-HQ1` | 10 | 10.10.10.50/24 (DHCP) | 10.10.10.1 | `HQ-SW1 Fa0/1` |
| `PC-HQ2` | 10 | 10.10.10.51/24 (DHCP) | 10.10.10.1 | `HQ-SW1 Fa0/2` |
| `PC-GUEST` | 40 | 10.10.40.50/24 (DHCP) | 10.10.40.1 | `HQ-SW1 Fa0/10` |
| `MGMT-SW1` | 99 | — | — | `HQ-SW1 Fa0/11` (access VLAN 99) |
| `AAA-SRV` | 99 | 10.10.99.10/24 | 10.10.99.1 | `MGMT-SW1 Fa0/1` |
| `SYSLOG-SRV` | 99 | 10.10.99.11/24 | 10.10.99.1 | `MGMT-SW1 Fa0/2` |
| `PC-ADMIN` | 99 | 10.10.99.50/24 | 10.10.99.1 | `MGMT-SW1 Fa0/3` |
| `PC-BR1` | 110 | 192.168.1.50/24 (DHCP) | 192.168.1.1 | `BR1-SW1 Fa0/1` |
| `PC-BR1-GUEST` | 140 | 192.168.14.50/24 | 192.168.14.1 | `BR1-SW1 Fa0/10` |
| `PC-INTERNET` | — | 198.51.100.50/24 | 198.51.100.1 | `ISP-R1 Gi0/1` |

> `MGMT-SW1` hangs off `HQ-SW1 Fa0/11` as a VLAN 99 access port. This keeps the three
> management hosts on the out-of-band segment without needing extra VLAN 99 ports on `HQ-SW1`,
> which Member 2's Configuration 3 assigns as Fa0/11–Fa0/12 only. It also mirrors the real
> design, where management lives on its own switch.

## 4. Routing

Static routes are sufficient and avoid a routing protocol becoming a variable in the tests.

```
! On HQ-R1
ip route 192.168.1.0 255.255.255.0 10.10.255.2
ip route 192.168.14.0 255.255.255.0 10.10.255.2
ip route 0.0.0.0 0.0.0.0 203.0.113.1

! On BR1-R1
ip route 10.10.0.0 255.255.0.0 10.10.255.1
ip route 0.0.0.0 0.0.0.0 10.10.255.1

! On ISP-R1
ip route 10.10.0.0 255.255.0.0 203.0.113.2
```

> **Routing must work before the security configurations are applied.** Build the topology,
> confirm end-to-end reachability everywhere, save that as your clean baseline, and only then
> start configuring controls. Otherwise a failed `ping` during a negative test is ambiguous:
> you cannot tell whether the control blocked it or the routing was never there.

## 5. DHCP

Head-office pools on `HQ-R1`, so that Member 3's DHCP snooping has a real DHCP exchange to
inspect on `HQ-SW1`.

```
ip dhcp excluded-address 10.10.10.1 10.10.10.49
ip dhcp excluded-address 10.10.40.1 10.10.40.49
ip dhcp pool STAFF-HQ
 network 10.10.10.0 255.255.255.0
 default-router 10.10.10.1
 dns-server 10.10.20.11
 exit
ip dhcp pool GUEST
 network 10.10.40.0 255.255.255.0
 default-router 10.10.40.1
 exit
```

The branch pool goes on **`BR1-R1`**, not here, so that no DHCP relay is needed across the WAN:

```
! On BR1-R1
ip dhcp excluded-address 192.168.1.1 192.168.1.49

ip dhcp pool STAFF-BR1
 network 192.168.1.0 255.255.255.0
 default-router 192.168.1.1
 exit
```

`PC-HQ1`, `PC-HQ2`, `PC-GUEST` and `PC-BR1` set to **DHCP**. Servers and `PC-ADMIN` set to
**static**, which is what makes Member 3's ARP ACL necessary — a statically addressed server
never produces a DHCP snooping binding entry, so Dynamic ARP Inspection would otherwise drop
its ARP replies.

## 6. MAC addresses used in configurations

Member 2's Configuration 4 pins a static MAC on the server port, and Member 3's Configuration 6
builds an ARP ACL from server MACs. **The placeholders below must be replaced with the real
values from your build.**

| Host | Placeholder in the scripts | Get the real value with |
|---|---|---|
| `CORE-DB` | `0001.AAAA.0010` | `show mac address-table interface Fa0/5` on HQ-SW1 |
| `CORE-APP` | `0001.AAAA.0011` | `show mac address-table interface Fa0/6` |
| `WEB-PORTAL` | `0001.AAAA.0030` | `show mac address-table interface Fa0/9` |

Alternatively, set each server's MAC manually in Packet Tracer (Config → FastEthernet0 → MAC
Address) to the placeholder values, so the scripts work unmodified. That is the lower-effort
route and is worth doing.

## 7. Which configuration touches which device

| Config | Member | Devices | Conflicts to watch |
|---|---|---|---|
| 1 — AAA (TACACS+/RADIUS) | 1 | `HQ-R1`, `AAA-SRV` | Must be applied **after** Config 2, or admin credentials cross the network in plaintext |
| 2 — SSH / management plane | 1 | `HQ-R1`, `HQ-SW1` | Apply **first**. The VTY `access-class` restricts management to 10.10.99.0/24 — configure from `PC-ADMIN`, not `PC-HQ1` |
| 3 — VLANs + inter-VLAN ACLs | 2 | `HQ-SW1`, `HQ-R1` | The `STAFF-IN` ACL denies staff → MGMT. Do not configure devices from `PC-HQ1` after this |
| 4 — Port security | 2 | `HQ-SW1`, `BR1-SW1` | `maximum 1` on Fa0/1–4. Do not also hang a switch off those ports |
| 5 — Zone-Based Policy Firewall | 3 | `HQ-R1` | Leave `Gi0/0.99` **out** of any zone or management access breaks. Needs `securityk9` + reload |
| 6 — DHCP snooping + DAI | 3 | `HQ-SW1`, `BR1-SW1` | Trust **only** `Gi0/1`. Servers need the ARP ACL or they go unreachable |
| 7 — Site-to-site IPsec | 4 | `HQ-R1`, `BR1-R1` | Static routes must exist first. Crypto ACLs must be exact mirrors. Needs `securityk9` |
| 8 — Syslog + NTP | 4 | all routers and switches | `Loopback0` must exist before `logging source-interface`. Syslog service must be On |

## 8. Build order

1. Place all devices, cable them, and set host addressing.
2. Configure VLANs, trunks, subinterfaces, static routes and DHCP.
3. **Verify full end-to-end reachability.** Save as `Northbridge-NS-baseline.pkt`.
4. Apply **Configuration 2** (SSH / management plane) — the prerequisite for everything else.
5. Apply **Configuration 1** (AAA).
6. Apply **Configuration 3**, then **4** (Member 2).
7. Apply **Configuration 6**, then **5** (Member 3). DHCP snooping before the firewall, so the
   binding table is populated while reachability is still unrestricted.
8. Apply **Configuration 7**, then **8** (Member 4).
9. Capture screenshots per `screenshot-capture-guide.md` as you complete each one — **not at
   the end.** Several verification outputs (ACL match counters, port-security violation
   counters, DHCP snooping bindings, IPsec packet counters) are only meaningful immediately
   after the test traffic that produced them.
