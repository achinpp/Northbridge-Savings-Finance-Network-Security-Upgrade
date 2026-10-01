# Member 4 — Individual Network Hardening Configurations

**Member:** [Member 4 — Full Name / IT Number]
**Configurations:** #7 Site-to-site IPsec VPN, head office ↔ branch (plan-linked) · #8 Centralised syslog and NTP (free choice)

Carried out on the shared group topology in `06_Topology/topology-spec.md`.
Plain-text scripts: `configs/cfg-7-site-to-site-ipsec.txt`, `configs/cfg-8-syslog-ntp.txt`.
Screenshot sequence: `06_Topology/screenshot-capture-guide.md`, shots 4.1–4.19.

---

## Configuration 7 — Site-to-site IPsec VPN between head office and Branch 1

**Devices:** `HQ-R1` and `BR1-R1`, across the WAN link

### What this configuration achieves

It builds an encrypted, authenticated, integrity-protected tunnel for all traffic between the
branch LAN and the head-office LAN, so that the branch-to-head-office path no longer depends
on trusting the carrier.

Three distinct protections, and it is worth separating them in the report because they map to
three different attacks:

1. **Confidentiality** — AES-256 encryption of the payload. Anyone intercepting traffic on the
   dedicated link, at the carrier, or at any intermediate hop sees ciphertext.
2. **Integrity** — SHA-256 HMAC on every packet. Traffic cannot be modified in transit without
   detection, which is the protection against a man-in-the-middle who can see the path but
   not break the cryptography.
3. **Peer authentication** — each router proves its identity to the other before any traffic
   flows. A device that injects itself into the path cannot complete the IKE exchange, so it
   cannot become a tunnel endpoint.

The brief states that "branch offices connect back to the head office over dedicated links".
A dedicated link is a contractual arrangement, not a security control: the traffic still
crosses a carrier's equipment, is reachable by the carrier's staff, and traverses physical
infrastructure Northbridge does not own or inspect. For a bank carrying core banking traffic
over that path, encrypting it is the baseline, and the brief gives no indication it is
currently encrypted.

### Plan linkage and threats addressed

This implements **Control 12 (cryptographic standard — TLS 1.2+/1.3 and IPsec for data in
transit)** and supports **Control 5 (zoned network architecture)**, because the tunnel is what
allows a branch to be treated as an extension of a defined internal zone rather than as an
untrusted network.

- **T4 (rogue DHCP and ARP spoofing man-in-the-middle):** this is the plan-linked threat. T4's
  attack succeeds by inserting the attacker into the path between a branch workstation and
  head office, then reading or modifying what passes. IPsec does not stop the attacker
  capturing the packets — nothing on the wire can — but it makes the captured traffic
  cryptographically useless, and the integrity check makes modification detectable. Note
  precisely what this does and does not cover: the tunnel protects traffic **between the two
  routers**, so an attacker positioned on the branch LAN segment *inside* the tunnel endpoint
  still sees plaintext. That intra-LAN exposure is what Member 3's DHCP snooping and DAI
  configuration and Member 2's port security address. Stating this boundary explicitly is
  important — it shows the control's limit is understood rather than overclaimed.
- **T3 (ransomware propagation):** supported indirectly. Defining the tunnel with a crypto ACL
  that names exactly which subnets may communicate means traffic outside that definition is
  not carried, which is an additional constraint on branch-to-core reachability.

### Command sequence

**On `HQ-R1`:**

```
enable
configure terminal

! --- security technology package required for crypto ---
license boot module c2900 technology-package securityk9

! === PHASE 1: IKE policy - how the peers authenticate and
! === establish the secure channel in which Phase 2 is negotiated
crypto isakmp policy 10
 encryption aes 256
 hash sha256
 authentication pre-share
 group 14
 lifetime 3600
 exit

! --- pre-shared key, bound to the specific peer address ---
crypto isakmp key NB-HQ-BR1-PSK-2026! address 10.10.255.2

! === PHASE 2: transform set - how the data itself is protected
! ESP for encryption, SHA-HMAC for integrity, tunnel mode
crypto ipsec transform-set TS-NB-AES256 esp-aes 256 esp-sha-hmac
 mode tunnel
 exit

crypto ipsec security-association lifetime seconds 3600

! === CRYPTO ACL: defines which traffic is "interesting",
! === i.e. which traffic the tunnel carries.
! === This must be an exact MIRROR of the ACL on the peer.
ip access-list extended VPN-TRAFFIC
 remark Branch 1 staff LAN to HQ staff LAN
 permit ip 10.10.10.0 0.0.0.255 192.168.1.0 0.0.0.255
 remark Branch 1 staff LAN to HQ core banking
 permit ip 10.10.20.0 0.0.0.255 192.168.1.0 0.0.0.255
 exit

! === CRYPTO MAP: ties peer, transform set and crypto ACL together
crypto map CMAP-NB 10 ipsec-isakmp
 description IPsec tunnel to Branch 1
 set peer 10.10.255.2
 set transform-set TS-NB-AES256
 set pfs group14
 match address VPN-TRAFFIC
 exit

! === APPLY to the WAN interface facing the branch
interface GigabitEthernet0/2
 description WAN to BR1-R1
 ip address 10.10.255.1 255.255.255.252
 crypto map CMAP-NB
 no shutdown
 exit

end
write memory
```

**On `BR1-R1` — the mirror configuration.** Phase 1 and Phase 2 parameters must match
exactly, the peer address is reversed, and **the crypto ACL is the exact mirror**: source and
destination swapped.

```
enable
configure terminal

license boot module c2900 technology-package securityk9

crypto isakmp policy 10
 encryption aes 256
 hash sha256
 authentication pre-share
 group 14
 lifetime 3600
 exit

crypto isakmp key NB-HQ-BR1-PSK-2026! address 10.10.255.1

crypto ipsec transform-set TS-NB-AES256 esp-aes 256 esp-sha-hmac
 mode tunnel
 exit

crypto ipsec security-association lifetime seconds 3600

! MIRRORED crypto ACL - source and destination swapped
ip access-list extended VPN-TRAFFIC
 permit ip 192.168.1.0 0.0.0.255 10.10.10.0 0.0.0.255
 permit ip 192.168.1.0 0.0.0.255 10.10.20.0 0.0.0.255
 exit

crypto map CMAP-NB 10 ipsec-isakmp
 description IPsec tunnel to Head Office
 set peer 10.10.255.1
 set transform-set TS-NB-AES256
 set pfs group14
 match address VPN-TRAFFIC
 exit

interface GigabitEthernet0/1
 description WAN to HQ-R1
 ip address 10.10.255.2 255.255.255.252
 crypto map CMAP-NB
 no shutdown
 exit

end
write memory
```

> **The three mistakes that break this configuration, worth naming in the report.**
>
> 1. **Non-mirrored crypto ACLs.** If one side says `10.10.10.0 → 192.168.1.0` and the other
>    says `192.168.1.0 → 10.10.0.0/16`, Phase 2 fails with a proxy identity mismatch even
>    though Phase 1 came up cleanly. This is the single most common fault.
> 2. **Mismatched Phase 1 or Phase 2 parameters.** Encryption, hash, DH group and
>    authentication method must agree. A mismatch leaves Phase 1 in `MM_NO_STATE`.
> 3. **Forgetting to apply the crypto map to the interface.** Everything is configured, nothing
>    is encrypted, and all the `show` commands look plausible until you check
>    `show crypto map`.
>
> **Why `group 14` and not `group 2`.** Diffie-Hellman group 2 is a 1024-bit modulus and is no
> longer considered adequate. Group 14 (2048-bit) is the minimum defensible choice for a
> financial institution, and choosing it deliberately — rather than accepting the lab default —
> is worth one sentence in the write-up. Likewise `set pfs group14` enables Perfect Forward
> Secrecy, so compromise of the pre-shared key does not permit decryption of previously
> captured sessions.
>
> **On the pre-shared key.** A PSK is used here because it is what Packet Tracer supports. The
> production recommendation is **certificate-based peer authentication** from an internal CA:
> a PSK is a shared secret, and Northbridge's documented problem is shared secrets. This
> should be stated explicitly in the report — it demonstrates awareness that the lab
> configuration and the production recommendation differ, and why.

### Verification commands and expected output

Traffic must be generated first: IPsec tunnels are built on demand, so until interesting
traffic matches the crypto ACL there is nothing to show.

| # | Verification command | What the output must show |
|---|---|---|
| 1 | **Generate traffic:** from `PC-BR1` (192.168.1.50), `ping 10.10.10.50` | First one or two pings may time out while the tunnel negotiates, then success. **This expected initial loss is itself worth capturing and explaining** |
| 2 | `show crypto isakmp sa` | Phase 1 SA in state **`QM_IDLE`** with `ACTIVE` status. Anything else (`MM_NO_STATE`, `MM_KEY_EXCH`) means Phase 1 did not complete |
| 3 | `show crypto ipsec sa` | Phase 2 SAs with the local and remote proxy identities, the inbound and outbound SPIs, and — critically — **non-zero `#pkts encaps` and `#pkts decaps` counters**. These counters are the proof that traffic is actually being encrypted, not merely that a tunnel exists |
| 4 | `show crypto map` | The crypto map with its peer, transform set and `match address VPN-TRAFFIC`, and confirmation that it is applied to the WAN interface |
| 5 | `show crypto ipsec transform-set` | `esp-aes 256`, `esp-sha-hmac`, tunnel mode |
| 6 | `show crypto isakmp policy` | AES-256, SHA-256, pre-share, DH group 14 |
| 7 | `show access-lists VPN-TRAFFIC` | Match counters incremented by the test traffic |
| 8 | **Negative test:** from `PC-BR1`, ping a destination **not** in the crypto ACL (for example `10.10.40.50`, the guest VLAN) | Traffic is not encrypted. `show crypto ipsec sa` encap counters do not increase for that flow — proving the tunnel carries only the defined traffic |
| 9 | **Packet-level proof:** Packet Tracer **Simulation Mode**, send a ping from `PC-BR1` to `10.10.10.50`, open the PDU on the WAN link and inspect it | The inbound PDU shows the original IP header; the PDU on the WAN link shows an **ESP header with an encrypted payload**. This is the strongest possible evidence and is unique to Packet Tracer — take it |

> Shot 3 and shot 9 are the two that earn the marks. Shot 3's `#pkts encaps` counter proves
> traffic is being encrypted; shot 9 shows the encrypted packet itself. A screenshot of
> `show crypto isakmp sa` alone proves only that two routers agreed to talk.

### Packet Tracer requirements and limitations

| Item | Note |
|---|---|
| Router model | ISR 2911 or similar with `securityk9`. Crypto is unavailable on the 1941 in some PT versions |
| `encryption aes 256` | If rejected, use `encryption aes 192` or `aes`, and note the substitution |
| `hash sha256` | Older PT images support only `hash sha`. Use `sha` and state that SHA-256 is the production recommendation |
| `group 14` | If rejected, `group 5` (1536-bit) is the next best; avoid `group 2` and say why |
| `set pfs group14` | Omit if rejected; note PFS as a production requirement |
| `crypto ipsec security-association lifetime` | Usually supported; omit if not |
| Routing | A route to the far-side LAN must exist **before** the tunnel will come up. Add static routes on both routers, or the crypto ACL will never match |

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
