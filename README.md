# IE3122 Network Security — Northbridge Savings & Finance Security Upgrade

Group assignment, Year 3 Semester 1, 2026. 100 marks, 30% of the final grade.
Report submission + compulsory physical viva.

**Replace every `[Member N — Full Name / IT Number]` placeholder before submission.**
They appear in `07_Final_Report/00-cover-page.md` and at the top of each member folder.

---

## How the work is divided

The brief splits this into 60 individual marks and 40 group marks. The folders mirror
that split exactly: each `0X_Member_X/` folder is one person's independently assessed
work, and `05_Group/` is the combined output that is only written *after* all four
individual folders are complete.

| Folder | Owner | Contents | Marks |
|---|---|---|---|
| `00_Brief/` | — | Extracted brief + requirements checklist | — |
| `01_Member_1/` | Member 1 | 2 threat models (identity & remote access), 4 tech proposals, 2 configs | 60 |
| `02_Member_2/` | Member 2 | 2 threat models (segmentation & Layer 2), 4 tech proposals, 2 configs | 60 |
| `03_Member_3/` | Member 3 | 2 threat models (perimeter, application & third-party), 4 tech proposals, 2 configs | 60 |
| `04_Member_4/` | Member 4 | 2 threat models (human, physical & resilience), 4 tech proposals, 2 configs | 60 |
| `05_Group/` | All | Layered plan, 3 tables, minimisation write-up, 4 comparative selections | 40 |

The 60 is **per member, not shared**: the brief assesses threat modelling (20), individual
technology recommendations (20) and hardening configurations (20) individually, so each member
earns their own 60 from their own folder, plus the same 40 group marks as everyone else. A weak
member folder costs that member 60 marks and nobody else — which is why the four folders are
kept genuinely separate rather than blended.
| `06_Topology/` | All | Shared Packet Tracer topology spec + screenshot capture guide | — |
| `07_Final_Report/` | Group leader | Cover page, assembly order, build instructions | — |

### Threat allocation (8 threats, no overlap)

| Threat | Member | Theme |
|---|---|---|
| T1 | 1 | Shared VPN account with no MFA → external remote compromise |
| T2 | 1 | Password reuse/sharing with no central AAA or audit trail → credential abuse and privilege escalation |
| T3 | 2 | Flat unsegmented network → ransomware propagation from a branch workstation to the core banking database |
| T4 | 2 | Guest Wi-Fi sharing the branch Layer 2 domain → rogue DHCP / ARP spoofing man-in-the-middle |
| T5 | 3 | Internet-exposed banking portal behind only a router ACL → SQL injection against the customer database |
| T6 | 3 | Third-party payment processor integration with no vendor assessment → trusted-connection abuse |
| T7 | 4 | Vishing with no awareness training or incident response process → credential disclosure |
| T8 | 4 | Unmonitored server room and unlocked branch cabinets → physical compromise, worsened by untested backups |

### Configuration allocation (8 distinct configurations — brief forbids duplicates)

| # | Member | Configuration | Plan-linked? | Implements |
|---|---|---|---|---|
| 1 | 1 | AAA with TACACS+/RADIUS and local fallback | **Yes** | Control 1 — addresses T2 |
| 2 | 1 | SSH and management-plane hardening | No (free choice) | — |
| 3 | 2 | VLAN segmentation + inter-VLAN extended ACLs | **Yes** | Control 5 — addresses T3, T4 |
| 4 | 2 | Switchport port security (sticky MAC + violation shutdown) | No (free choice) | — |
| 5 | 3 | Zone-Based Policy Firewall (Outside / DMZ / Inside) | **Yes** | Control 5 + 6 — addresses T5, T6 |
| 6 | 3 | DHCP snooping + Dynamic ARP Inspection | No (free choice) | — |
| 7 | 4 | Site-to-site IPsec VPN, head office ↔ branch | **Yes** | Control 12 — addresses T4 |
| 8 | 4 | Centralised syslog + NTP time synchronisation | No (free choice) | — |

### Technology proposals — 16 individual, 4 group selections

Each member proposed independently for all four areas. The group then ran a head-to-head.
Winners (full reasoning in `05_Group/04-group-technology-evaluation.md`):

| Area | Adopted | From |
|---|---|---|
| VPN | Cisco Secure Client (AnyConnect) IKEv2/IPsec on the Secure Firewall pair, per-user certificate + MFA + posture | Member 1 |
| AAA | Cisco ISE — RADIUS for network access, TACACS+ for device administration | Member 1 |
| Network architecture | Dual-firewall DMZ-sandwich with a dedicated Partner-Extranet zone and out-of-band management | Member 3 |
| IDS/IPS | Inline Firepower IPS at zone boundaries + Secure Network Analytics flow-based detection | Member 4 |

Member 2's proposals were not adopted outright; its cost analysis drove the three-phase
rollout, and the reasons each proposal lost are stated explicitly in the evaluation.

---

## What still needs a human

1. **Packet Tracer screenshots.** The eight configuration scripts are complete and
   verified-by-design, but the screenshots of commands and verification output have to be
   taken by hand in Packet Tracer. `06_Topology/screenshot-capture-guide.md` lists every
   shot, in order, with the exact command to run and what the output should show.
2. **Build the `.pkt` file** from `06_Topology/topology-spec.md`.
3. **Names and IT numbers** — find and replace the placeholders.
4. **Assemble the report** — follow `07_Final_Report/01-assembly-order.md`.
