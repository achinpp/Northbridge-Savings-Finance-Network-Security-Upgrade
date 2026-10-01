# Member 1 — Individual Threat Modelling

**Member:** [Member 1 — Full Name / IT Number]
**Allocated theme:** Identity and remote access
**Threats modelled:** T1 (shared VPN account), T2 (password reuse without central AAA)

> This section is individually authored and individually assessed. The two threats below are
> my own work. They feed into the group's combined layered security plan but remain
> attributable to me.

## Risk rating method used

Risk = Likelihood × Impact, each scored 1–5, giving a 1–25 score.

| Score | Band |
|---|---|
| 1–4 | Low |
| 5–9 | Medium |
| 10–14 | High |
| 15–25 | Critical |

Likelihood is scored against *Northbridge as it stands today*, not against a hardened bank,
because the brief describes the current state with no compensating controls in place.

---

## Threat Model T1 — Compromise of the shared VPN account

### Asset

The **core banking application and customer database** hosted in the on-premises head-office
data centre, reached through the remote-access VPN. Secondary asset: the internal email
system and the staff credentials the VPN protects. The brief names customer financial and
personal data as Northbridge's most critical asset, so this is the highest-value target in
the environment.

### Vulnerability

A **single shared VPN account** used interchangeably by all remote staff and both external IT
support contractors, with **no multi-factor authentication** and **no individual
accountability**. Three properties make this worse than a generic weak-credential finding:

1. The credential is known to people outside Northbridge's employment (two contractors).
2. It cannot be rotated on a leaver event without disrupting every remote user at once, so in
   practice it is almost certainly long-lived.
3. There is no centralised authentication system and no centralised audit trail, so use of
   the credential produces no attributable log record.

### Threat

An **external attacker**, or a former contractor employee who retains the password, seeking
authenticated network-level access into Northbridge's internal network. A secondary actor is
a credential broker: shared VPN credentials for financial-sector targets have resale value
independent of the broker's own offensive capability.

### Exploit

The attacker obtains the shared password by any of the paths the current environment leaves
open:

- **Phishing or vishing a remote user.** The brief records a real vishing attempt against a
  Northbridge staff member, stopped only by that individual's instinct. There is no awareness
  training programme, so the next attempt has a reasonable chance of succeeding.
- **Credential reuse.** Password reuse and sharing are described as common among branch
  staff. If the shared VPN password has ever been reused on an external service that was
  later breached, it is already in a public combolist.
- **Contractor-side leakage.** The password sits in two external organisations' hands, in
  whatever form they store it — ticket systems, shared password notes, personal devices.
  Northbridge has no vendor security assessment process and therefore no visibility of this.

No software exploit is required. The exploit is the *legitimate use of a valid credential by
the wrong person*, which is exactly what MFA and per-user identity exist to stop.

### Attack

1. The attacker authenticates to the internet-facing VPN with the shared credential. The
   connection is indistinguishable from a legitimate remote worker because the account is, by
   design, used by many people from many locations.
2. The VPN places the attacker inside the **flat internal network**. The brief states head
   office systems, branch systems, guest Wi-Fi and point-of-service equipment share the same
   network space, so there is no internal boundary left to cross.
3. Internal reconnaissance follows — host and port sweeps, SMB and database service
   discovery. Northbridge has **no IDS/IPS anywhere**, so this scanning raises no alert.
4. The attacker locates the core banking database and the portal's back end and harvests
   further credentials from systems that each hold their own local accounts. Because every
   device and application maintains its own account set, no central view would show an
   account being used abnormally.
5. Exfiltration of customer financial and personal data, and/or ransomware deployment against
   the core banking environment.

### Impact

- **Confidentiality:** mass disclosure of customer financial and personal records — the worst
  outcome available in this environment.
- **Integrity:** the attacker holds legitimate network access and can alter transaction or
  account records. With no centralised audit trail, Northbridge cannot prove what was or was
  not changed.
- **Availability:** if the intrusion ends in ransomware, the core banking application and the
  customer-facing portal and mobile app go down. Backups exist but have **never been tested
  for successful restoration**, so recovery time is unknown.
- **Regulatory and reputational:** Northbridge is a licensed financial institution, and the
  brief states its ability to keep operating depends as much on customer and regulator
  confidence as on any single system staying online. A breach of customer financial data is
  reportable, and the payment processor integration due to go live within two quarters would
  very likely be suspended by the partners.
- **Forensic:** with no central logging and a shared account, Northbridge cannot answer the
  first question a regulator will ask — *who accessed what, and when*. That absence is itself
  an impact, because it forces worst-case assumptions about breach scope.

### Risk

**Likelihood 5 / Impact 5 → Score 25 → CRITICAL.**

Likelihood is the maximum available, and the reasoning is specific to Northbridge rather than
generic. Three independent routes to the credential are already open — phishing against staff
with no awareness training, reuse given documented password sharing, and contractor-side
leakage with no vendor assessment. There is no second factor to stop a stolen credential
being used, and no detective control that would notice the credential being used from an
anomalous location. A control is only as strong as its weakest independent bypass, and here
every bypass is unmitigated.

Impact is the maximum because the asset reached is the bank's own most critical asset, the
flat network means VPN access and core-banking reachability are effectively the same
privilege, and the untested backups remove the one control that would otherwise cap the
availability impact.

This is the highest risk I identified and, in my assessment, the one that must be remediated
*before* the payment processor integration is allowed to proceed — that integration extends
trust outward from a network which currently cannot identify its own remote users.

---

## Threat Model T2 — Credential abuse and privilege escalation through password reuse and the absence of central AAA

### Asset

**Staff credentials** across the estate and, through them, the **core banking application**,
the **internal email system**, and the **network and server infrastructure** itself. The brief
lists the internal email system and staff credentials as assets every employee relies on to
do their job, which makes credentials a *hinge* asset: compromising them yields all the
others.

### Vulnerability

Four documented weaknesses compound into one:

1. **No centralised authentication system** — every device and application maintains its own
   local set of user accounts.
2. **Password reuse and password sharing are common among branch office staff.**
3. **No centralised logging or audit trail**, so even where activity is recorded nobody would
   notice unusual behaviour in time to act on it.
4. **No joiner/mover/leaver process**, which follows from (1): with accounts held locally on
   every device and application, there is no single place to disable a departing user.

The architectural consequence is that Northbridge cannot answer "which accounts does this
person have?" or "has this account been disabled everywhere?" for any individual.

### Threat

Two actors, both realistic here:

- A **malicious or disgruntled insider** — branch staff, or an IT support contractor with
  legitimate device access — who wants access beyond their role.
- An **external attacker** who already holds one low-value staff credential (for example via
  the vishing route modelled in T7, or a breach of an external site where the password was
  reused) and wants to escalate from it.

### Exploit

**Credential replay across trust boundaries.** Because the same password is reused across
systems and no central identity ties them together, one credential is tested against every
system that has a login: the branch workstation, the core banking application, webmail, the
switch and router CLIs, and local administrator accounts in the server room. Where sharing
has occurred, a single branch password may already be valid for several colleagues' accounts,
widening the attack surface with no technical exploitation at all.

Network device access is the highest-value variant. The brief records no centralised
authentication for infrastructure either, which implies shared local enable and console
passwords on switches and routers — the classic pattern where one password opens the entire
network estate.

### Attack

1. The attacker obtains one working credential — their own legitimate branch account, a shared
   password from a colleague, or a reused password recovered from an external breach.
2. They replay it horizontally against other staff accounts and vertically against
   application and infrastructure logins. No account lockout policy is described and there is
   no central authentication service to correlate repeated failures across systems, so this
   testing is effectively risk-free for the attacker.
3. A hit on an infrastructure device or an application administrative account yields
   privileged control. On a flat network with no segmentation, device-level access is enough
   to reach the core banking environment.
4. The attacker then operates using valid credentials over an extended period. With no central
   audit trail and no IDS/IPS, dwell time is bounded only by the attacker's own carelessness.
5. Outcome: fraudulent transactions, customer data extraction, or quiet positioning ahead of
   a larger event such as the payment processor integration going live.

### Impact

- **Integrity first, confidentiality second.** Unlike T1, the defining impact here is *fraud*.
  An insider with core banking access can move money or alter account records, and Northbridge
  has no audit trail to detect it or later prove it. For a savings and finance provider that
  is direct financial loss, not only a disclosure event.
- **Non-repudiation collapses entirely.** With shared and reused passwords and no central
  accounting, no action can be attributed to any individual. Even a correctly suspected
  insider may be undismissable and unprosecutable on the available evidence.
- **Leaver risk becomes permanent.** Every departed employee and every rotated contractor
  engineer potentially retains valid access, because there is no single place from which
  access was ever revoked.
- **Regulatory:** segregation of duties and individual accountability for privileged access
  are baseline expectations for a financial institution. This is an audit finding in its own
  right, independent of whether it is ever exploited.
- **Operational:** remediating this after an incident costs far more than before one, because
  every local account on every device and application must then be enumerated by hand under
  time pressure.

### Risk

**Likelihood 4 / Impact 5 → Score 20 → CRITICAL.**

Likelihood is 4 rather than 5 because exploitation requires the attacker to already hold one
credential — one step more than T1 needs. It is not lower than 4 because the brief states
password reuse and sharing are *already happening*: the precondition for this attack is not
hypothetical, it is documented current practice, and a 450-staff population spread across
seven sites makes at least one reused or shared credential a near certainty rather than a
possibility.

Impact is 5 because the fraud and non-repudiation consequences are specific to a bank. An
organisation that cannot attribute a transaction to a person has lost the property its
regulatory standing rests on. The absence of central logging is what moves this from a
hygiene issue to a critical one: a bank with password reuse but sound audit trails can detect
and prove abuse, whereas Northbridge can do neither.

My assessment is that T1 and T2 share a single root cause — the absence of a central identity
and accounting authority — and should be remediated by one control programme rather than two.
That was the argument I took into the group's control minimisation discussion.
