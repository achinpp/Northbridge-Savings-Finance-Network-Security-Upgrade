# Final Report — Assembly Order and Build Instructions

The brief requires one submitted report, with the individual technology proposals as "clearly
labelled appendices" and the group's comparative evaluation "in the main body". This file maps
the repository onto that structure.

---

## 1. Report structure

| § | Section | Source file | Marks |
|---|---|---|---|
| — | Cover page | `07_Final_Report/00-cover-page.md` | — |
| — | Table of contents | generate on build | — |
| 1 | Executive summary | write last — see Section 3 below | — |
| 2 | Scope, assumptions and risk rating method | `05_Group/01-layered-security-plan.md` §1.1 preamble | — |
| 3 | Northbridge context and key assets | summarise from the brief | — |
| **4** | **Individual threat modelling — 8 threats** | | **20 (per member)** |
| 4.1 | Member 1 — T1, T2 | `01_Member_1/01-threat-models.md` | |
| 4.2 | Member 2 — T3, T4 | `02_Member_2/01-threat-models.md` | |
| 4.3 | Member 3 — T5, T6 | `03_Member_3/01-threat-models.md` | |
| 4.4 | Member 4 — T7, T8 | `04_Member_4/01-threat-models.md` | |
| **5** | **Combined layered security plan** | `05_Group/01-layered-security-plan.md` | **7** |
| 5.1 | Threat reconciliation | §1 of that file | |
| 5.2 | Master list of 18 controls | §2 | |
| 5.3 | Residual risk after the plan | §3 | |
| 5.4 | Implementation phasing | §4 | |
| **6** | **Mapping and classification tables** | `05_Group/02-control-mapping-tables.md` | **7** |
| 6.1 | Control-to-Threat / Attack mapping | Table A | |
| 6.2 | Function × Category dual-axis table | Table B + placement notes | |
| **7** | **Control minimisation justification** | `05_Group/03-control-minimisation.md` | **6** |
| **8** | **Individual network hardening configurations** | | **20 (per member)** |
| 8.1 | Member 1 — Configurations 1 and 2 | `01_Member_1/03-configurations.md` + screenshots | |
| 8.2 | Member 2 — Configurations 3 and 4 | `02_Member_2/03-configurations.md` + screenshots | |
| 8.3 | Member 3 — Configurations 5 and 6 | `03_Member_3/03-configurations.md` + screenshots | |
| 8.4 | Member 4 — Configurations 7 and 8 | `04_Member_4/03-configurations.md` + screenshots | |
| **9** | **Group technology evaluation and selection** | `05_Group/04-group-technology-evaluation.md` | **20** |
| 9.1 | VPN | §1 | 5 |
| 9.2 | AAA | §2 | 5 |
| 9.3 | Network architecture | §3 | 5 |
| 9.4 | IDS/IPS | §4 | 5 |
| 9.5 | Note on Member 2's contributions | §5 | |
| 10 | Topology used for the configurations | `06_Topology/topology-spec.md` | — |
| — | **Appendix A1** — Member 1's four technology proposals | `01_Member_1/02-tech-proposals.md` | **20 (per member)** |
| — | **Appendix A2** — Member 2's four technology proposals | `02_Member_2/02-tech-proposals.md` | |
| — | **Appendix A3** — Member 3's four technology proposals | `03_Member_3/02-tech-proposals.md` | |
| — | **Appendix A4** — Member 4's four technology proposals | `04_Member_4/02-tech-proposals.md` | |
| — | **Appendix B** — Configuration scripts as plain text | all eight `configs/*.txt` files | — |
| — | **Appendix C** — Screenshot evidence | per `06_Topology/screenshot-capture-guide.md` | — |

> **Why the proposals go in appendices and the evaluation in the main body.** The brief is
> explicit: "Individual technology proposals (16 in total: 4 members × 4 areas) should be
> included as clearly labelled appendices, with the group's final comparative evaluation and
> selection for each of the 4 areas in the main body." Section 9 and Appendices A1–A4 are
> therefore deliberately separated, and Section 9 cross-references the appendix paragraph
> numbers (A1.1, A2.1, …) so a marker can follow the comparison back to the source proposal.

## 2. Steps to produce the submission

1. **Replace every placeholder.** Search the whole folder for `[Member` and fill in names and
   IT numbers. They appear in the cover page and at the top of each of the twelve member
   documents.
   ```
   grep -rn "\[Member" .
   ```
2. **Build the Packet Tracer topology** from `06_Topology/topology-spec.md`. Follow the build
   order in §8 of that file. Save `Northbridge-NS-baseline.pkt` before applying any control.
3. **Apply the eight configurations** in the order given, and **capture screenshots as you go**
   using `06_Topology/screenshot-capture-guide.md`. Several verification outputs are only
   meaningful immediately after the test traffic that produced them, so this cannot be done
   retrospectively.
4. **Record any command substitutions.** Each configuration write-up ends with a Packet Tracer
   limitations table. Where you had to substitute or omit a command, update the plain-text
   script in that member's `configs/` folder so the script matches the screenshots — the brief
   asks for the exact syntax used.
5. **Paste the screenshots into Section 8**, each directly beneath the command it verifies, with
   a one-line caption naming the device and what the output shows.
6. **Write the executive summary** (Section 1) last, once everything else is final.
7. **Convert to the submission format.** The group leader submits the soft copy via the Course
   Web link.

## 3. Executive summary — what to put in it

Write this last, and keep it to one page. It should state, in this order:

- What was reviewed and why — a security review commissioned by the CTO before the payment
  processor integration proceeds.
- The headline finding: **all eight modelled threats fall in the critical band**, because
  Northbridge currently has no control in place that any of the eight attack chains would have
  to defeat.
- The three highest risks and their scores: T1 (shared VPN account, 25), T3 (ransomware across
  the flat network, 25), and T5 (SQL injection against the public portal, 20).
- The response: eighteen controls, reduced from an initial twenty-six, structured so that no
  threat depends on a single control.
- The four technology recommendations, named.
- The deadline-driven conclusion: **Phase 1 must complete before the payment processor
  integration goes live**, because the integration extends trust outside Northbridge's
  infrastructure for the first time, and the cost of retrofitting partner controls rises once
  the partners have built against whatever Northbridge ships.
- The two cheapest, highest-value actions, which can start immediately and need no procurement:
  auditable access control and camera coverage on the server room, and one successful
  restoration test of the core banking database. Together they take T8 out of the critical
  band on their own.

## 4. Pre-submission checklist

Against the brief's own submission requirements:

- [ ] Cover page lists all 4 members **and** which threats, technology proposals and
      configurations each is individually responsible for
- [ ] All **eight** threat modelling exercises present, each using
      asset → vulnerability → threat → exploit → attack → impact → risk
- [ ] Each threat's risk rating justified with **Northbridge-specific** reasoning
- [ ] Numbered master control list present
- [ ] Control-to-Threat mapping table present and accurate
- [ ] Function × Category dual-axis table present, with multi-cell controls placed in **every**
      cell they belong in
- [ ] Control Minimisation justification present and written as **prose, not a table**
- [ ] **Sixteen** individual technology proposals present as clearly labelled appendices
      (4 members × 4 areas)
- [ ] Group comparative evaluation for all **four** areas in the **main body**, each explicitly
      stating why the chosen option beat the other **three** member proposals
- [ ] Screenshots for all **eight** configurations, showing commands **and** verification output
- [ ] Configuration scripts included as **plain text** as well as screenshots
- [ ] No two members submitted the same configuration — verify against the allocation table in
      the root `README.md`
- [ ] At least one configuration per member is linked to a control in the group plan, and names
      the specific threat it addresses
- [ ] All placeholders replaced
- [ ] All four members confirmed for the viva

## 5. Known gaps in this package

Stated plainly so nothing is assumed complete that is not:

1. **Screenshots are not produced.** All eight configuration scripts, their verification
   sequences and a 77-shot capture guide are written, but the screenshots themselves require
   Packet Tracer and must be taken by hand.
2. **The `.pkt` file is not built.** `06_Topology/topology-spec.md` fully specifies it —
   devices, models, VLANs, addressing, routing, DHCP and build order — but the file has to be
   assembled in Packet Tracer.
3. **Member names and IT numbers are placeholders.**
4. **MAC addresses in two configurations are placeholders** (`0001.AAAA.0010` and similar).
   Either replace them with the values from your build, or set each server's MAC manually in
   Packet Tracer to match, which is quicker. See §6 of the topology spec.
5. **Command substitutions are unverified.** Each configuration lists the commands most likely
   to be rejected by Packet Tracer along with substitutions, but which ones your specific
   version accepts can only be established by typing them.
