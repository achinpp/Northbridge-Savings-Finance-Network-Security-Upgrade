# 2. Scope, Assumptions and Method

## 2.1 Scope

This review covers Northbridge Savings & Finance's network and information security posture
across its head office and branch estate, as described in the IE3122 2026 Semester 2 assignment
brief. It delivers:

- Eight individually modelled threats, two per group member
- A combined layered security plan reconciling all eight into a single set of controls
- Control-to-threat mapping and a Function × Category classification of every control
- A written justification of how the control count was minimised
- Sixteen individual technology proposals across four mandatory areas, and the group's
  comparative selection for each
- Eight network hardening configurations implemented on a representative topology, with
  verification evidence

**Out of scope:** application source code review, formal penetration testing, physical site
survey, vendor pricing, and procurement. Where the plan recommends these — Control 11 specifies
an annual independent penetration test, Control 18 a vendor security assessment — they are
recommendations, not activities performed here.

## 2.2 Sources and attribution

Facts about Northbridge are drawn from the assignment brief. Where the brief is silent, an
assumption is stated explicitly at the point it is made rather than presented as fact. Risk
ratings, control selections, architecture decisions and recommendations are the group's own
analysis.

Each member's threat models, technology proposals and hardening configurations are individually
attributable and are labelled as such throughout, as the brief requires. The combined plan, the
classification tables, the minimisation justification and the comparative technology evaluation
are joint work.

## 2.3 Risk rating method

All four members used the same method, agreed before individual work began so that the eight
resulting scores would be directly comparable at the reconciliation stage.

**Risk = Likelihood × Impact**, each scored 1–5.

| Score | Band |
|---|---|
| 1–4 | Low |
| 5–9 | Medium |
| 10–14 | High |
| 15–25 | Critical |

**Likelihood is assessed against Northbridge as it stands today**, with no compensating controls
assumed, because the brief describes the current state as having none. This is the single most
important methodological choice in the report: a threat is not rated on how likely it would be
at a well-defended bank, but on how likely it is here.

**Impact is assessed on the asset actually reached**, not on the worst imaginable consequence.
Where a threat's severe outcomes arise from a *follow-on* threat, the impact is scored on the
immediate consequence and the escalation is noted — this avoids double-counting the same harm
across several threat models. Member 4's T7 is the clearest example: its direct impact is one
compromised account, scored 4, while its strategic significance is that it supplies the
credential three other threats depend on.

## 2.4 Reconciliation method

The eight threats were produced independently and then reconciled before the control list was
written. Five overlaps were merged and four genuine contradictions between members' proposals
were resolved. Both are recorded in Section 5.1, including which member's position was overruled
and why, because the brief asks for threats "genuinely reconciled... rather than just listed one
after another".

---

# 3. Northbridge Context and Key Assets

## 3.1 The organisation

Northbridge Savings & Finance is a mid-sized regional financial services provider offering
personal banking, small business loans and digital payment services. It operates a head office
and **six branch offices**, employing approximately **450 staff**.

Its core banking application and customer database are hosted in an **on-premises data centre at
the head office**, alongside an online banking portal and mobile app exposed to the public
internet. Branch offices connect to head office over dedicated links. A small number of remote
and travelling staff, plus **two external IT support contractors**, require regular remote
access. Integration with **two third-party payment processing partners** is due to go live
within two quarters.

## 3.2 Key assets

| Asset | Why it matters |
|---|---|
| **Customer financial and personal data** in the core banking database | The brief names this as Northbridge's most critical asset. Direct financial and regulatory consequences if compromised |
| **Online banking portal and mobile app** | Give customers direct access to their accounts, and are the only systems deliberately reachable from the internet |
| **Branch-to-head-office connectivity** | Core banking availability depends on it throughout the business day |
| **Internal email and staff credentials** | Relied on by every employee; credentials are a *hinge* asset — compromising them yields the others |
| **The payment processor integrations** | Will shortly become a critical dependency, extending trust beyond Northbridge's own infrastructure for the first time |
| **Regulatory standing and public reputation** | The brief states Northbridge's ability to operate depends as much on customer and regulator confidence as on any single system staying online |

## 3.3 Why the organisation is in this position

Northbridge's security investment has historically gone almost entirely into **physical
measures** — vaults, alarm systems, branch cameras — rather than IT infrastructure. The network
has grown organically over more than a decade with no formal segmentation strategy.

That history explains the pattern in the findings, and it matters for how the recommendations
should be read: this is not an organisation that is careless about security. It is one that has
applied its security budget to the risks it could see. The plan's physical controls are
deliberately modest for that reason — Northbridge already knows how to run cameras and access
control, and Control 17 largely asks it to apply existing competence to the server room rather
than build a capability from nothing.

## 3.4 The two events that prompted this review

1. **A regional industry association reported a sharp rise in ransomware incidents** against
   mid-sized financial firms over the past year, several of which began with a single
   compromised branch workstation and spread rapidly across an unsegmented network.
2. **A staff member received a telephone call** from someone claiming to be from "IT Helpdesk",
   urgently requesting their password. The employee grew suspicious partway through and did not
   comply, but the attempt was logged with no process to escalate it, warn other staff, or
   rotate the credential being sought.

Both appear directly in the threat models: the first as Member 2's T3, the second as Member 4's
T7. Neither is hypothetical.

## 3.5 Summary of current weaknesses

**Technical.** No MFA anywhere. A single shared VPN account for all remote staff and both
contractors. No meaningful network segmentation — guest Wi-Fi, branch systems and core banking
within reach of one another. No IDS or IPS. No formal patch management, with several branch
systems known to be running outdated software. No centralised logging or audit trail. No
centralised authentication: every device and application holds its own local accounts.

**Physical.** The head-office server room is secured by a single shared key with no camera
coverage. Visitor sign-ins are inconsistently enforced. No site has security signage,
badge-checking presence or camera coverage at entry points. Network cabinets were found unlocked
in at least two branch locations during a recent walkthrough.

**Administrative.** No data classification policy. No vendor security assessment process. Work
from home and personal device use are permitted with no guidance. Password reuse and sharing are
common among branch staff. Backups exist but have never been tested for successful restoration.
No documented disaster recovery or incident response plan. **No security awareness training
programme at all** — the brief's own framing is that the recent social-engineering attempt was
stopped by one individual's instinct, "not by any policy, training, or process the organisation
had in place".
