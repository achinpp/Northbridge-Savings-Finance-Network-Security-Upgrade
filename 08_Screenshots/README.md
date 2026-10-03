# Screenshot Evidence

Evidence for the eight hardening configurations, captured in Packet Tracer against the
topology in `06_Topology/topology-spec.md`. The authoritative list of what to capture, in
order, is `06_Topology/screenshot-capture-guide.md`.

## Naming convention

```
08_Screenshots/<member>-cfg<n>-<name>/<shot>-<what-it-shows>.png
```

Example: `M1-cfg2-ssh-mgmt/1.11-show-ip-ssh.png`

The shot number matches the capture guide, so a marker can trace any screenshot in the report
back to the step that produced it, and back to the plain-text script in that member's
`configs/` folder.

## Folders

| Folder | Member | Configuration | Plan-linked? |
|---|---|---|---|
| `00-BEFORE/` | — | Baseline state before any control was applied | — |
| `M1-cfg2-ssh-mgmt/` | 1 | SSH and management-plane hardening | Free choice |
| `M1-cfg1-aaa/` | 1 | AAA with TACACS+ and RADIUS | **Plan-linked** |
| `M2-cfg3-vlan-acl/` | 2 | VLAN segmentation with inter-VLAN ACLs | **Plan-linked** |
| `M2-cfg4-port-security/` | 2 | Switchport port security | Free choice |
| `M3-cfg5-edge-firewall/` | 3 | Internet edge firewall (static PAT + edge ACL) | **Plan-linked** |
| `M3-cfg6-dhcp-snoop-dai/` | 3 | DHCP snooping and Dynamic ARP Inspection | Free choice |
| `M4-cfg7-netflow/` | 4 | NetFlow export (flow-based detection) | **Plan-linked** |
| `M4-cfg8-syslog-ntp/` | 4 | Centralised syslog and NTP | Free choice |

## `00-BEFORE/` — why it exists

These three show the baseline network *working* in ways it should not, before any control was
applied:

| File | Shows |
|---|---|
| `guest-to-coredb.png` | A guest Wi-Fi client reaching the core banking database (T4) |
| `internet-to-staff.png` | An internet host reaching an internal staff workstation (T5) |
| `dmz-to-coredb.png` | The public web portal reaching the core banking database (T5) |

Each pairs with an "after" shot where the same test is refused — 2.9, 3.10 and 3.8
respectively. The brief does not require before/after pairs, but a control demonstrated
against a measured baseline is stronger evidence than an "after" screenshot alone.

## The twelve headline shots

These show a control actually catching something rather than merely being configured. If time
runs short, these are the minimum that evidence each configuration as working.

| Shot | Configuration | Proves |
|---|---|---|
| 1.7 | M1 — AAA | Login succeeds for a user that exists **only** on the AAA server |
| 1.16 | M1 — SSH | Telnet is **refused** |
| 2.10 | M2 — ACLs | `deny…log` match counters incremented by real blocked traffic |
| 2.16 | M2 — Port security | Port in `Secure-shutdown`, violation count 1 |
| 3.8 | M3 — Edge FW | Internet cannot reach an internal staff host |
| 3.9 | M3 — Edge FW | Edge ACL deny counters incremented by refused traffic |
| 3.19 | M3 — DHCP snooping | Rogue DHCP server present and failing |
| 3.20 | M3 — DHCP snooping | Snooping drop counters incremented |
| 4.5 | M4 — NetFlow | Flow cache recording real sessions |
| 4.7 | M4 — NetFlow | Reconnaissance fan-out: one source, many destinations |
| 4.16 | M4 — Syslog | Messages arriving with correct source and timestamp |
| 4.19 | M4 — Syslog | Two devices' events in one ordered timeline |

## Capture rules

1. **The device hostname must be visible in the prompt.** `Switch#` is worth far less than
   `HQ-SW1#`, because the marker cannot tell which device produced the output.
2. **Capture counters immediately after the traffic that moved them.** ACL match counts,
   port-security violations, DHCP snooping bindings and IPsec packet counters all read zero
   before the test and are the entire point afterwards.
3. **A real block is 4 of 4 packets lost, repeatably.** A single first-packet timeout is ARP
   resolution or tunnel negotiation, not a control working.
4. **Maximise the CLI window before capturing** — a downscaled screenshot is unreadable in a
   printed report.
