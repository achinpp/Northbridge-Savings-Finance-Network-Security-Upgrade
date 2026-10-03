# Screenshot Capture Guide

**This is the part of the assignment that cannot be produced for you.** Everything else in this
repository is written; the brief requires "screenshots of the exact commands entered and the
corresponding verification command output", and those have to be taken by hand in Packet
Tracer against the topology you build.

This guide makes that mechanical. Every shot is listed in order, with the exact command and
what the output must show. Work through it top to bottom.

---

## Rules that apply to every shot

1. **Command-then-verify, in one frame.** The brief says to follow "the same command-then-verify
   pattern used in this semester's lab guides". Where possible, capture the configuration
   command and its verification output in the **same** screenshot, or in two consecutive
   screenshots with the command visible in the first.
2. **Show the device hostname in the prompt.** A screenshot reading `Switch#` is worth much less
   than one reading `HQ-SW1#`, because the marker cannot tell which device it came from.
   Configure hostnames before capturing anything.
3. **Capture counters immediately after the traffic that moved them.** ACL match counts,
   port-security violation counts, DHCP snooping bindings and IPsec packet counters all read
   zero before the test and are the entire point after it. A `show access-lists` taken before
   any traffic proves nothing.
4. **Negative tests are worth more than positive ones.** Anyone can screenshot a successful
   ping. Showing that the thing which *should* be blocked **is** blocked is what demonstrates
   the control works. Shots marked **★** below are the ones that carry the marks.
5. **Name the files predictably** so they can be dropped into the report in order:
   `M1-cfg1-shot03-show-tacacs.png`.
6. **Keep the window large enough to read.** Maximise the CLI window before capturing;
   a downscaled screenshot of a full-screen terminal is unreadable in a printed report.

---

## Member 1 — Configuration 1: AAA with TACACS+ and RADIUS

Prerequisite: `AAA-SRV` configured first (Services → AAA → On; clients `HQ-R1` at 10.10.1.1
with secrets `NBtac$2026`/TACACS and `NBrad$2026`/RADIUS; users `alice.perera` /
`Str0ng-Pass-1` and `bob.silva` / `Str0ng-Pass-2`).

| Shot | Where | Command | Must show |
|---|---|---|---|
| 1.1 | `AAA-SRV` GUI | Services → AAA | Service On, both client entries, both users |
| 1.2 | `HQ-R1` | The configuration being entered (`aaa new-model` onward) | The command block as typed |
| 1.3 | `HQ-R1` | `show running-config \| include aaa` | Every `aaa` line, with `group tacacs+ local` on the authentication line |
| 1.4 | `HQ-R1` | `show running-config \| include tacacs\|radius` | Both servers at 10.10.99.10 |
| 1.5 | `HQ-R1` | `show tacacs` | Server listed, socket open/close counts |
| 1.6 | `HQ-R1` | `show radius statistics` | Access-request / access-accept counters |
| 1.7 ★★ | `PC-ADMIN` | `ssh -l alice.perera 10.10.1.1` | Login succeeds for a user that exists **only** on the AAA server |
| 1.8 | `PC-ADMIN` | `ssh -l nosuchuser 10.10.1.1` | Rejected |
| 1.9 ★ | `PC-ADMIN` | Shut `AAA-SRV`'s port, then `ssh -l netadmin 10.10.1.1` | Succeeds via the **local fallback** — proves the control is safe to deploy |

## Member 1 — Configuration 2: SSH and management-plane hardening

| Shot | Where | Command | Must show |
|---|---|---|---|
| 1.10 | `HQ-R1` | `crypto key generate rsa general-keys modulus 1024` | Key generation output |
| 1.11 | `HQ-R1` | `show ip ssh` | `SSH Enabled - version 2.0`, retries 2, timeout 60 |
| 1.12 | `HQ-R1` | `show crypto key mypubkey rsa` | Key pair `HQ-R1.northbridge.lk`, ≥1024 bits |
| 1.13 | `HQ-R1` | `show running-config \| begin line vty` | `transport input ssh`, `access-class MGMT-HOSTS in`, `exec-timeout 10 0` |
| 1.14 | `HQ-R1` | `show access-lists MGMT-HOSTS` | Permit for 10.10.99.0/24 and the logged deny |
| 1.15 | `PC-ADMIN` | `ssh -l netadmin 10.10.1.1` | Banner displays, login succeeds |
| 1.16 ★★ | `PC-ADMIN` | `telnet 10.10.1.1` | **Connection refused** — Telnet genuinely disabled |
| 1.17 ★ | `PC-HQ1` | `ssh -l netadmin 10.10.1.1` | **Blocked** by `access-class` from a non-management subnet |
| 1.18 | `HQ-R1` | `show access-lists MGMT-HOSTS` (again) | Deny counter has **incremented** after shot 1.17 |

## Member 2 — Configuration 3: VLAN segmentation with inter-VLAN ACLs

| Shot | Where | Command | Must show |
|---|---|---|---|
| 2.1 | `HQ-SW1` | `show vlan brief` | All six VLANs, correct port membership, Fa0/13–24 in VLAN 999 |
| 2.2 | `HQ-SW1` | `show interfaces trunk` | Gi0/1 trunking, allowed 10,20,30,40,99, **native VLAN 999** |
| 2.3 | `HQ-SW1` | `show interfaces status` | Unused ports `disabled`, not `notconnect` |
| 2.4 | `HQ-R1` | `show ip interface brief` | All five subinterfaces up/up with correct gateways |
| 2.5 | `HQ-R1` | `show ip route` | Five connected routes |
| 2.6 | `HQ-R1` | `show access-lists` | All four named lists, rules in order |
| 2.7 | `PC-HQ1` | `telnet 10.10.20.10 1521` | Connects — the permitted application flow still works |
| 2.8 ★ | `PC-HQ1` | `ping 10.10.20.10` | **Fails.** ICMP is not permitted, so the implicit deny catches it — proof of default-deny |
| 2.9 ★ | `PC-GUEST` | `ping 10.10.20.10` then `ping 10.10.10.50` | **Both fail** — guest reaches neither core banking nor staff |
| 2.10 ★★ | `HQ-R1` | `show access-lists` (again, straight after 2.8 and 2.9) | **Match counters on the `deny … log` lines have incremented.** The single most valuable shot in this configuration |

## Member 2 — Configuration 4: Port security

| Shot | Where | Command | Must show |
|---|---|---|---|
| 2.11 | `HQ-SW1` | `show port-security` | Summary: ports, max, current, violations, action |
| 2.12 | `HQ-SW1` | `show port-security interface Fa0/1` | `Enabled`, `Secure-up`, `Shutdown`, `Maximum: 1` |
| 2.13 | `HQ-SW1` | `show port-security address` | Sticky MACs with type `SecureSticky` and correct VLAN |
| 2.14 | `HQ-SW1` | `show running-config interface Fa0/1` | The sticky MAC **written into the running config** |
| 2.15 | Topology view | Replace `PC-HQ1` on Fa0/1 with `PC-ROGUE` and ping the gateway | The swapped device, for context |
| 2.16 ★★ | `HQ-SW1` | `show port-security interface Fa0/1` | `Secure-shutdown`, `SecurityViolation count: 1` |
| 2.17 ★ | `HQ-SW1` | `show interfaces Fa0/1 status` | `err-disabled` |
| 2.18 | `HQ-SW1` | `show interfaces Fa0/1` | Violation logged with the offending MAC |
| 2.19 | `HQ-SW1` | Re-attach `PC-HQ1`, then `shutdown` / `no shutdown` | Returns to `Secure-up` |

## Member 3 — Configuration 5: Internet edge firewall (static PAT + default-deny edge ACL)

Substituted for the intended Zone-Based Policy Firewall: Packet Tracer 8.2 on the ISR 2911
implements no stateful firewall (`zone security`, `ip inspect` and reflexive ACLs are all
rejected, and the `securityk9` licence command is a no-op). See the configuration write-up.

| Shot | Where | Command | Must show |
|---|---|---|---|
| 3.1 | `HQ-R1` | `zone security INSIDE` / `ip inspect name X http` / `ip ?` | **The rejections.** Evidence for the documented substitution — worth capturing, not hiding |
| 3.2 | `HQ-R1` | `show version` | `security / disable / None` after reload, proving the licence command had no effect |
| 3.3 | `HQ-R1` | The configuration being entered | NAT boundary, static PAT, `NAT-ALLOWED`, `EDGE-IN` |
| 3.4 | `HQ-R1` | `show ip nat statistics` | Inside and outside interfaces listed |
| 3.5 | `HQ-R1` | `show running-config \| include ip nat` | Static PAT entry and the overload entry |
| 3.6 | `HQ-R1` | `show access-lists EDGE-IN` | All rules in order, **counters at zero** — the "before" half |
| 3.7 | `PC-INTERNET` | Browse `https://203.0.113.2` | Portal loads — the one published service is reachable |
| 3.8 ★★ | `PC-INTERNET` | `ping 10.10.10.50` then `ping 10.10.20.10` | **Both fail.** No path from the internet to any internal host |
| 3.9 ★★ | `HQ-R1` | `show access-lists EDGE-IN` | `deny ip any 10.10.0.0 0.0.255.255` with a **non-zero** match count. Before/after with 3.6 |
| 3.10 ★ | `HQ-R1` | `show ip nat translations` | The live translation carrying the portal session |
| 3.11 | `PC-HQ1` | `ping 198.51.100.50`, then `show ip nat translations` on `HQ-R1` | Outbound PAT hiding internal addressing |

## Member 3 — Configuration 6: DHCP snooping and Dynamic ARP Inspection

| Shot | Where | Command | Must show |
|---|---|---|---|
| 3.12 | `HQ-SW1` | `show ip dhcp snooping` | Enabled, VLAN list, **Gi0/1 the only trusted interface**, rate limits |
| 3.13 | `HQ-SW1` | `show ip dhcp snooping binding` | Binding entries — take this **after** the PCs have leases |
| 3.14 | `HQ-SW1` | `show ip arp inspection` | DAI enabled, validation checks, forwarded/dropped counters |
| 3.15 | `HQ-SW1` | `show ip arp inspection interfaces` | Gi0/1 trusted, access ports untrusted with rate limits |
| 3.16 | `HQ-SW1` | `show ip arp inspection vlan 10` | Per-VLAN stats; ARP ACL shown for VLANs 20 and 30 |
| 3.17 | `PC-HQ1` | `ipconfig /renew` then `ping 10.10.10.1` | Lease obtained, gateway reachable — the control is not breaking the network |
| 3.18 | Topology view | Attach `ROGUE-DHCP` to Fa0/3, DHCP service On, scope offering itself as gateway | The rogue server in place, for context |
| 3.19 ★★ | `PC-HQ1` | `ipconfig /renew` then `ipconfig /all` | **The legitimate** gateway and lease. The rogue `OFFER` was dropped |
| 3.20 ★★ | `HQ-SW1` | `show ip dhcp snooping` (again) | Drop counters **incremented** on the untrusted interface |
| 3.21 ★ | `HQ-SW1` | `show ip arp inspection` (again) | `Dropped` counter non-zero |

## Member 4 — Configuration 7: NetFlow export (flow-based behavioural detection)

Substituted for the intended site-to-site IPsec VPN: Packet Tracer 8.2 on the ISR 2911 has no
cryptographic feature set (`crypto isakmp policy 10` is rejected on the `crypto` keyword, and
`license ?` offers only `boot`, with no activation path). See the configuration write-up.

| Shot | Where | Command | Must show |
|---|---|---|---|
| 4.1 | `HQ-R1` | `crypto isakmp policy 10` and `license ?` | **The rejections.** Evidence for the documented substitution |
| 4.2 | `HQ-R1` | The configuration being entered | Export destination, version, source, and `ip flow ingress` on each interface |
| 4.3 | `HQ-R1` | `show ip flow export` | Destination `10.10.99.11:2055`, version 9, source `Loopback0` |
| 4.4 | `HQ-R1` | `show ip flow interface` | Every interface with flow collection enabled |
| 4.5 ★★ | `HQ-R1` | `show ip cache flow` after normal traffic | Individual flow records — source, destination, protocol, port, packet count |
| 4.6 | `PC-HQ1` | Ping six different internal hosts in sequence | The reconnaissance pattern being generated |
| 4.7 ★★ | `HQ-R1` | `show ip cache flow` | **Many records sharing one source, differing destinations** — the fan-out signature of internal reconnaissance |
| 4.8 ★ | `BR1-R1` | `show ip cache flow` after a ping from `PC-BR1` | Branch visibility with **nothing deployed at the branch** |

## Member 4 — Configuration 8: Centralised syslog and NTP

Prerequisite: `SYSLOG-SRV` Services → SYSLOG set **On**, and reachable (ping it from each
device first).

| Shot | Where | Command | Must show |
|---|---|---|---|
| 4.10 | `HQ-R1` | `show clock detail` | Time, timezone, source |
| 4.11 | `HQ-SW1` | `show clock detail` | **The same time** as 4.10, to the second |
| 4.12 | `BR1-SW1` | `show ntp status` | **`Clock is synchronized`**, stratum 4, reference 10.10.1.1 |
| 4.13 | `BR1-SW1` | `show ntp associations` | 10.10.1.1 with `*` marking the synchronised peer |
| 4.14 | `HQ-R1` | `show logging` | `Trap logging: level informational`, host 10.10.99.11, messages sent |
| 4.15 | `HQ-R1` | `shutdown` / `no shutdown` on an unused interface | The commands as entered |
| 4.16 ★★ | `SYSLOG-SRV` GUI | Services → SYSLOG | The link-down / link-up messages **with correct timestamp and source device** |
| 4.17 | `PC-ADMIN` | SSH with a deliberately wrong password | The failed attempt |
| 4.18 ★ | `SYSLOG-SRV` GUI | Services → SYSLOG | The failed-login message, attributed to the right device |
| 4.19 ★★ | `SYSLOG-SRV` GUI | Generate events on `BR1-SW1` and `HQ-R1` within a few seconds | **Both in the same view, in the correct order, with agreeing timestamps.** This demonstrates the actual objective — one ordered timeline across the estate |

---

## Totals

| Member | Config 1 (plan-linked) | Config 2 (free choice) | Shots |
|---|---|---|---|
| 1 | AAA TACACS+/RADIUS | SSH / management plane | 18 |
| 2 | VLAN segmentation + ACLs | Port security | 19 |
| 3 | Zone-Based Policy Firewall | DHCP snooping + DAI | 21 |
| 4 | Site-to-site IPsec | Syslog + NTP | 19 |
| | | | **77** |

Seventy-seven is more than you strictly need. If time is short, the **★★** shots are the
minimum that will still evidence each configuration as working — there are twelve of them, and
they are the ones that show a control actually catching something rather than merely being
configured. The **★** shots are the next priority. The unmarked shots are the configuration
evidence the brief also asks for, and are quick to take once you are already at the prompt.

## If a command is rejected by your Packet Tracer version

Each configuration write-up ends with a table of substitutions. Use them, and **record what you
actually typed** — the brief asks for "the configuration script/commands as plain text as well
as screenshots, so the exact syntax used can be checked independently of image quality", so a
documented substitution is fine and an undocumented mismatch between your script and your
screenshot is not.

Where a control genuinely cannot be demonstrated in Packet Tracer (NTP authentication, ARP
ACLs, `errdisable recovery`), say so explicitly in the write-up and state what the production
configuration would be. That converts a tool limitation into evidence that you understand the
control, which is worth more than silently dropping the line.
