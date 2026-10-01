# IE3122: Network Security — Group Assignment

## Northbridge Savings & Finance — Network Security Upgrade

**Department of Computer Systems Engineering**
**Faculty of Computing**
**Sri Lanka Institute of Information Technology**

Year 3, Semester 1 — 2026
Assignment mode: Report submission + physical viva
Maximum marks: 100 · Contribution to final grade: 30%

---

## Group members

> **Replace the placeholders below before submission.** The brief requires that the cover page
> "must list the details of all 4 group members, clearly indicating which threats, technology
> proposals, and configurations each member is individually responsible for."

| | Name | IT Number | Role |
|---|---|---|---|
| 1 | [Member 1 — Full Name] | [IT Number] | Group leader / submitting member |
| 2 | [Member 2 — Full Name] | [IT Number] | Member |
| 3 | [Member 3 — Full Name] | [IT Number] | Member |
| 4 | [Member 4 — Full Name] | [IT Number] | Member |

---

## Individual responsibility statement

### Member 1 — [Full Name] · [IT Number]
**Theme:** Identity and remote access

- **Threat models (Section 4.1):** **T1** — Compromise of the shared VPN account.
  **T2** — Credential abuse and privilege escalation through password reuse and the absence of
  central AAA.
- **Technology proposals (Appendix A1):** VPN — Cisco Secure Client (AnyConnect) IKEv2/IPsec on
  a Cisco Secure Firewall pair. AAA — Cisco ISE with RADIUS and TACACS+. Architecture —
  three-tier single-vendor zoned design. IDS/IPS — inline Firepower IPS on both firewall tiers.
- **Hardening configurations (Section 8.1):** **Configuration 1 (plan-linked)** — AAA with
  TACACS+ and RADIUS and local fallback, implementing Control 1. **Configuration 2 (free
  choice)** — SSH and management-plane hardening.
- **Proposals adopted by the group:** VPN and AAA.

### Member 2 — [Full Name] · [IT Number]
**Theme:** Network segmentation and Layer 2 security

- **Threat models (Section 4.2):** **T3** — Ransomware propagation from a branch workstation to
  the core banking database across the flat network. **T4** — Rogue DHCP and ARP spoofing
  man-in-the-middle from the guest Wi-Fi and point-of-service equipment.
- **Technology proposals (Appendix A2):** VPN — FortiGate NGFW with FortiClient SSL/IPsec.
  AAA — Microsoft Entra ID with NPS and the MFA extension. Architecture — single HA NGFW cluster
  with distribution-layer VLAN segmentation and inter-VLAN ACLs. IDS/IPS — bundled edge IPS
  plus internal Snort 3 sensors on SPAN ports.
- **Hardening configurations (Section 8.2):** **Configuration 3 (plan-linked)** — VLAN
  segmentation with inter-VLAN extended ACLs, implementing Control 5. **Configuration 4 (free
  choice)** — switchport port security.
- **Contributions adopted by the group:** the three-phase implementation plan, the separation of
  Control 2 (MFA) from Control 1, per-branch VLAN containment in Control 5, and just-in-time
  privilege elevation in Control 3.

### Member 3 — [Full Name] · [IT Number]
**Theme:** Internet perimeter, application security and third-party trust

- **Threat models (Section 4.3):** **T5** — SQL injection against the internet-facing online
  banking portal. **T6** — Abuse of the third-party payment processor connection.
- **Technology proposals (Appendix A3):** VPN — WireGuard on hardened Linux gateways.
  AAA — FreeRADIUS, OpenLDAP, privacyIDEA and `tac_plus`. Architecture — dual-firewall DMZ
  sandwich with a partner extranet, integration broker and out-of-band management network.
  IDS/IPS — Suricata inline plus Zeek metadata feeding a Wazuh/Elastic SIEM.
- **Hardening configurations (Section 8.3):** **Configuration 5 (plan-linked)** — Zone-Based
  Policy Firewall across OUTSIDE / DMZ / INSIDE, implementing Control 5.
  **Configuration 6 (free choice)** — DHCP snooping and Dynamic ARP Inspection.
- **Proposals adopted by the group:** network architecture. Also adopted: the requirement for
  local fallback credentials and a tested rebuild procedure in Control 1, the small-and-static
  internal rule set in Control 5, and the argument that established Control 8 as a first-class
  control.

### Member 4 — [Full Name] · [IT Number]
**Theme:** Human factors, physical security and operational resilience

- **Threat models (Section 4.4):** **T7** — Social engineering (vishing) against staff
  credentials. **T8** — Physical compromise of the head-office server room, and the
  unrecoverable outage that follows.
- **Technology proposals (Appendix A4):** VPN — Zero Trust Network Access. AAA — Aruba ClearPass
  Policy Manager. Architecture — two firewall tiers plus identity-based micro-segmentation
  inside the core. IDS/IPS — inline Firepower IPS plus flow-based behavioural detection from
  existing switch NetFlow.
- **Hardening configurations (Section 8.4):** **Configuration 7 (plan-linked)** — site-to-site
  IPsec VPN between head office and Branch 1, implementing Control 12. **Configuration 8 (free
  choice)** — centralised syslog and NTP time synchronisation.
- **Proposals adopted by the group:** IDS/IPS. Also adopted: the monitor-mode discovery period
  before 802.1X enforcement, and the explicit naming of the east-west visibility gap in the
  residual risk assessment.

---

## Group deliverables (joint work)

| Deliverable | Section |
|---|---|
| Threat reconciliation — overlaps merged, contradictions resolved | 5.1 |
| Numbered master list of 18 controls | 5.2 |
| Control-to-Threat / Attack mapping | 6.1 |
| Function × Category dual-axis classification table | 6.2 |
| Control Minimisation justification (prose) | 7 |
| Comparative technology evaluation and final selection, 4 areas | 9 |
| Residual risk assessment and three-phase implementation plan | 5.3, 5.4 |

## Group technology selections

| Area | Adopted solution | Proposed by |
|---|---|---|
| VPN | Cisco Secure Client (AnyConnect) IKEv2/IPsec on a Cisco Secure Firewall pair, per-user certificate + MFA + posture | Member 1 |
| AAA | Cisco ISE — RADIUS for network access, TACACS+ for device administration | Member 1 |
| Network architecture | Dual-firewall DMZ sandwich with partner extranet, integration broker and out-of-band management | Member 3 |
| IDS/IPS | Inline Firepower IPS at zone boundaries plus flow-based behavioural detection from existing switch NetFlow | Member 4 |

---

## Declaration

We declare that this report is our own work. The individual threat models, technology proposals
and hardening configurations attributed above were produced independently by the named member
before group discussion, as the assignment brief requires. The combined layered security plan,
the classification tables, the minimisation justification and the comparative technology
evaluation are the joint work of all four members.

Facts about Northbridge Savings & Finance are drawn from the IE3122 2026 Semester 2 group
assignment brief. Risk ratings, control selections and recommendations are our own analysis.

| Member | Signature | Date |
|---|---|---|
| [Member 1 — Full Name] | | |
| [Member 2 — Full Name] | | |
| [Member 3 — Full Name] | | |
| [Member 4 — Full Name] | | |

---

*All four members confirm they will attend the scheduled viva. The brief states that any student
who fails to attend will have their submission treated as a non-submission and awarded 0 marks.*
