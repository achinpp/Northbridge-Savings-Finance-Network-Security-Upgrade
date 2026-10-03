# Member 4 — Individual Network Hardening Configurations

**Member:** [Member 4 — Full Name / IT Number]
**Configurations:** #7 NetFlow export — flow-based behavioural detection (plan-linked) · #8 Centralised syslog and NTP (free choice)

Carried out on the shared group topology in `06_Topology/topology-spec.md`.
Plain-text scripts: `configs/cfg-7-netflow-export.txt`, `configs/cfg-8-syslog-ntp.txt`.
Screenshot sequence: `06_Topology/screenshot-capture-guide.md`, shots 4.1–4.19.

---

## Configuration 7 — NetFlow export: flow-based behavioural detection

**Devices:** `HQ-R1` and `BR1-R1`

### A note on what was intended, and why this differs

Configuration 7 was specified as a **site-to-site IPsec VPN** between head office and Branch 1,
implementing **Control 12** (cryptographic standard for data in transit).

**Packet Tracer 8.2 on the ISR 2911 has no cryptographic feature set.** Established by direct
test, not assumed:

| Command | Result |
|---|---|
| `crypto isakmp policy 10` | `% Invalid input detected` — the caret falls on `crypto` itself, so the entire command family is absent from the parser |
| `license boot module c2900 technology-package securityk9` | accepted silently; after **two** reloads `show version` still reports `security / disable / None / None` |
| `license ?` (config mode) | offers only `boot`. No `accept`, `install` or `right-to-use` — there is no activation path in this build |

The same absence removed Zone-Based Policy Firewall, which is why Member 3's Configuration 5
was also substituted.

**Control 12 therefore has no configuration demonstrating it**, and that is recorded as a gap
rather than concealed. The IPsec design remains the recommendation in the group plan and in the
cryptographic standard; it simply cannot be built on this platform.

### Why NetFlow is the right substitute, not a consolation

The group adopted **Member 4's IDS/IPS proposal (A4.4)**, whose second half specifies exactly
this: *"NetFlow is exported from the switches and routers Northbridge already owns, at head
office and at all six branches, into a flow analytics collector that baselines normal behaviour
and alerts on deviation."*

Configuring it here implements the recommendation the group actually adopted, on the real
topology — and it tests the proposal's central practical claim, that **branch visibility needs
no appliance**, because the configuration is applied to `BR1-R1` with nothing deployed at the
branch.

### What this configuration achieves

It makes the routers record **who talked to whom, when, how much, and for how long**, and
export those records to a central collector.

The distinction from a signature engine is the whole argument:

- **A signature engine matches known exploits.** It cannot detect an authenticated attacker
  using legitimate credentials and legitimate protocols — which is what T1, T2, T7 and T8 all
  produce. There is no signature for *"Alice's account is behaving unlike Alice"*.
- **Flow records describe behaviour**, and none of it is hidden by encryption. Internal
  reconnaissance — one host connecting to many hosts in a short window — is the clearest
  possible signal in flow data, and it appears **before any payload executes**.

That is the earliest detection point in T3's chain, and it is available from telemetry
Northbridge can turn on this week.

### Plan linkage and threats addressed

Implements the flow-based half of **Control 7**, and feeds **Control 8** (the central platform
that receives both flow records and logs).

- **T3 — ransomware propagation.** The detection point. T3's chain runs *foothold → discovery →
  credential harvesting → lateral movement → detonation*, and the brief states Northbridge is
  "blind to reconnaissance or active compromise until damage is already visible". The discovery
  step is a host sweeping the address space, which is the single clearest pattern in flow data.
- **T7 and T8 — an attacker already inside.** Both produce an actor using valid credentials and
  normal protocols, on traffic that may never cross a firewall. Flow analysis is the only
  proposed mechanism that sees that class of activity at all.

### Command sequence

Full script with comments: `configs/cfg-7-netflow-export.txt`.

**On `HQ-R1`:**

```
enable
configure terminal
ip flow-export destination 10.10.99.11 2055
ip flow-export version 9
ip flow-export source Loopback0
interface GigabitEthernet0/0.10
 ip flow ingress
 exit
interface GigabitEthernet0/0.20
 ip flow ingress
 exit
interface GigabitEthernet0/0.30
 ip flow ingress
 exit
interface GigabitEthernet0/0.40
 ip flow ingress
 exit
interface GigabitEthernet0/0.99
 ip flow ingress
 exit
interface GigabitEthernet0/1
 ip flow ingress
 ip flow egress
 exit
interface GigabitEthernet0/2
 ip flow ingress
 ip flow egress
 exit
end
write memory
```

**On `BR1-R1` — the point of the whole proposal:**

```
enable
configure terminal
ip flow-export destination 10.10.99.11 2055
ip flow-export version 9
ip flow-export source Loopback0
interface GigabitEthernet0/0.110
 ip flow ingress
 exit
interface GigabitEthernet0/0.140
 ip flow ingress
 exit
interface GigabitEthernet0/1
 ip flow ingress
 ip flow egress
 exit
end
write memory
```

> **Nothing is deployed *at* the branch.** No sensor, no SPAN session, no appliance to patch —
> three configuration lines on a router Northbridge already owns. The brief states Northbridge
> has six branches, no security staff at any of them, and no formal patch management process. A
> design requiring hardware at each branch would mean seven appliances to install, manage and
> patch, and those appliances would themselves become unpatched network-attached devices.
>
> **Why `ip flow-export source Loopback0`.** Same reasoning as `logging source-interface` in
> Configuration 8: one device, one address, in every record. Without it the exporter's address
> changes with the egress interface and the collector cannot attribute records reliably.
>
> **Why ingress on every internal subinterface.** This captures traffic as it *enters* the
> router from each zone, which is where movement between VLANs becomes visible — the placement
> that detects T3's propagation.

### Verification commands and expected output

| # | Verification command | What the output must show |
|---|---|---|
| 1 | `show ip flow export` | Destination `10.10.99.11` port 2055, version 9, source `Loopback0`, and the export counters |
| 2 | `show ip flow interface` | Every interface with flow collection enabled, and whether ingress, egress or both |
| 3 | `show ip cache flow` **before traffic** | A largely empty flow cache — the "before" half of the pair |
| 4 | **Generate normal traffic:** from `PC-HQ1`, `ping 10.10.20.11` and browse `https://10.10.20.11` | — |
| 5 | `show ip cache flow` | Individual flow records with source, destination, protocol, port and packet count. The router is recording who talked to whom, with **no agent on any endpoint and no signature database** |
| 6 | **Generate a reconnaissance pattern:** from `PC-HQ1`, ping `10.10.20.10`, `10.10.20.11`, `10.10.30.10`, `10.10.99.10`, `10.10.99.11`, `10.10.40.50` in sequence | — |
| 7 | `show ip cache flow` | **Many flow records sharing one source address with differing destinations.** That fan-out is exactly what a flow analytics collector baselines against, and it is the signature of internal reconnaissance in T3's chain |
| 8 | `show ip cache flow` on `BR1-R1`, after a ping from `PC-BR1` | Branch flow records — visibility at a site where nothing was deployed |

> **Steps 5 and 7 carry the marks.** Step 7 in particular: note what is *not* required to see
> the pattern — no malware signature, no agent on the endpoint, no decryption. It is visible in
> metadata alone, which is precisely why the technique works against an attacker using
> legitimate credentials and encrypted protocols.

### Packet Tracer limitations

| Item | Note |
|---|---|
| Crypto / IPsec | Entirely absent; see the table above |
| `ip flow-export version 9` | If rejected, use `version 5` and note the substitution |
| `ip flow-export source` | If rejected, omit — records are then sourced from the egress interface. Note it as a production requirement |
| `ip flow egress` | Support is less consistent than `ip flow ingress`. Ingress on every interface still captures every flow once |
| No collector | Packet Tracer has no NetFlow collector service, so records cannot be shown *arriving* at `SYSLOG-SRV`. The evidence is the router's own flow cache — which is the data that would be exported |

---

## Configuration 8 — Centralised syslog and NTP time synchronisation (free choice)

**Devices:** `HQ-R1`, `HQ-SW1`, `BR1-R1`, `BR1-SW1`
**Syslog server:** `SYSLOG-SRV` at 10.10.99.11 · **NTP master:** `HQ-R1`

### What this configuration achieves and the real-world problem it solves

It makes every network device send its log messages to one server, with accurate,
synchronised timestamps.

The real-world problem is stated directly in the brief: **"There is no centralized logging or
audit trail across systems, meaning that even where activity is technically recorded, nobody
would necessarily notice unusual behaviour in time to act on it."** Logs that live only on the
device that produced them have three fatal properties:

- **They are lost when they matter most.** A router's log buffer is in RAM. It is cleared by a
  reboot — and rebooting the device is one of the first things both an attacker and a
  troubleshooting engineer will do.
- **They are deletable by the attacker.** Someone who compromises a device can clear its local
  log. Once a message has been sent to a separate server, deleting it requires compromising
  that server too.
- **They cannot be correlated.** An attack that crosses a branch switch, a branch router, the
  WAN, the head-office router and a core switch leaves five fragments on five devices. Nobody
  reconstructs that by logging into five devices in sequence.

**Why NTP is in the same configuration and not a separate one.** Correlation requires a common
clock. If the branch switch thinks it is 09:14 and the head-office router thinks it is 11:47,
the collected logs cannot be placed in order, and an ordered sequence of events is the entire
value of central logging. Worse, timestamps that cannot be shown to be accurate are weak
evidence — which matters for a bank that may need to demonstrate to a regulator what happened
and when. Central logging without time synchronisation produces a pile of records rather than
a timeline. They are one control.

This is my free-choice configuration. It also directly supports **Control 8 (centralised
logging, SIEM and alerting with NTP time synchronisation)** in the group plan, and it is the
control that makes every *detective* control in the plan actually usable — an IPS alert, an
ACL deny log and a port-security violation are all worth considerably less if they cannot be
placed on a shared timeline.

### Command sequence

**On `HQ-R1` (the NTP master and the reference for the site):**

```
enable
configure terminal

! === TIME FIRST. Logging without accurate time is of little use. ===
clock timezone IST 5 30
end

! Set the clock manually before enabling the NTP master
clock set 09:00:00 1 October 2026

configure terminal

! --- act as the authoritative time source for the estate ---
ntp master 3

! --- authenticate NTP, so a rogue host cannot feed false time ---
ntp authentication-key 1 md5 NBntpKey2026
ntp trusted-key 1
ntp authenticate

! === LOGGING ===
! timestamp every message to the millisecond, in UTC-offset-aware
! local time. Without "datetime", messages are stamped with device
! uptime, which is useless for correlation.
service timestamps log datetime msec localtime show-timezone
service timestamps debug datetime msec localtime show-timezone

! --- send to the central server ---
logging host 10.10.99.11

! --- severity 6 (informational) captures interface state changes,
! --- login attempts and ACL denies without the volume of debug ---
logging trap informational

! --- stamp every message with a consistent source address, so the
! --- server attributes it to the right device regardless of which
! --- interface it left by ---
logging source-interface Loopback0

! --- keep a local buffer as well, for when the server is unreachable
logging buffered 16384 informational

! --- do not let log output interleave with CLI typing
line console 0
 logging synchronous
 exit
line vty 0 4
 logging synchronous
 exit

! --- log configuration changes and login activity explicitly ---
archive
 log config
  logging enable
  logging size 200
  notify syslog
  exit
 exit

login on-failure log
login on-success log

end
write memory
```

**On `HQ-SW1`, `BR1-R1` and `BR1-SW1` (NTP clients):**

```
enable
configure terminal

clock timezone IST 5 30

! --- synchronise to HQ-R1, with authentication ---
ntp authentication-key 1 md5 NBntpKey2026
ntp trusted-key 1
ntp authenticate
ntp server 10.10.1.1 key 1

service timestamps log datetime msec localtime show-timezone
service timestamps debug datetime msec localtime show-timezone

logging host 10.10.99.11
logging trap informational
logging buffered 16384 informational

line console 0
 logging synchronous
 exit

login on-failure log
login on-success log

end
write memory
```

> **Why `logging source-interface Loopback0`.** A device with several interfaces will source
> syslog from whichever interface the route to the server happens to use, so the same device
> can appear in the logs under different addresses — or its address can change when a link
> fails. A loopback is always up and always the same, so every message from `HQ-R1` is
> attributable to `HQ-R1`. For a bank that may need to produce logs as evidence, consistent
> device attribution is not a cosmetic detail.
>
> **Why severity `informational` and not `debugging`.** Severity 7 includes debug output and
> will flood both the link and the server, which in practice gets logging turned off within a
> month. Severity 6 captures what matters for security — interface state changes, login
> successes and failures, ACL deny hits, port-security violations, configuration changes —
> at manageable volume. Choosing a severity deliberately, and being able to say why, is the
> judgement worth marks here.
>
> **Why NTP authentication.** An attacker who can feed a device false time can make its log
> entries land at the wrong point in a timeline, or outside the window anyone examines. It is
> a cheap, rarely configured control, and one line of explanation shows the control was chosen
> rather than copied.

### Verification commands and expected output

| # | Verification command | What the output must show |
|---|---|---|
| 1 | `show clock detail` (on each device) | The same time, to the second, with the timezone shown and the source identified as NTP on the clients |
| 2 | `show ntp status` (on a client) | **`Clock is synchronized`**, stratum 4, reference `10.10.1.1`. `Clock is unsynchronized` means the configuration is not yet working — wait, as NTP takes a few minutes to converge |
| 3 | `show ntp associations` | The server at 10.10.1.1 with a `*` in the leftmost column, indicating the synchronised peer |
| 4 | `show logging` | `Trap logging: level informational`, the host 10.10.99.11 listed, and a count of messages sent |
| 5 | **Generate an event:** `shutdown` then `no shutdown` on an unused interface | — |
| 6 | **On `SYSLOG-SRV`:** open Services → SYSLOG | The link-down and link-up messages, **with the correct timestamp and the correct source device**. This is the central screenshot of the configuration |
| 7 | **Generate a security event:** attempt an SSH login with a wrong password | — |
| 8 | **On `SYSLOG-SRV`** | The failed-login message recorded, from the device it occurred on |
| 9 | **Correlation proof (the best shot available):** generate events on `BR1-SW1` and `HQ-R1` within a few seconds of each other | Both appear in the **same** syslog view, in the **correct order**, with timestamps that agree. This demonstrates the actual objective — a single ordered timeline across the estate — rather than merely that logging is switched on |
| 10 | `show archive log config all` | The record of configuration changes made, with the user who made them |

> Shot 9 is the one that distinguishes this from a configuration that merely compiles. Shots
> 1–4 show the commands were accepted; shot 9 shows the control delivering the thing it exists
> for.

### Packet Tracer requirements and limitations

| Command | If unsupported in your PT version |
|---|---|
| `logging source-interface Loopback0` | Requires `interface Loopback0` to exist first (`10.10.1.1/32` on HQ-R1). Omit if rejected |
| `ntp authentication-key` / `ntp trusted-key` / `ntp authenticate` | Support varies. If rejected, use plain `ntp server 10.10.1.1` and note NTP authentication as a production requirement |
| `archive` / `log config` | Frequently unsupported in PT — omit and note it |
| `service timestamps log datetime msec localtime show-timezone` | Usually supported. If `show-timezone` is rejected, drop that keyword only |
| `logging trap informational` | Supported; `logging trap 6` is equivalent if the word form is rejected |
| Syslog server | A PT Server device with Services → SYSLOG switched **On**. It must be reachable — check with a ping from each device before expecting messages |
| NTP server | Either `ntp master` on HQ-R1 as above, or a PT Server with Services → NTP on. If using the server, point the clients at the server's address instead |
