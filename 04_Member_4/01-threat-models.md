# Member 4 — Individual Threat Modelling

**Member:** [Member 4 — Full Name / IT Number]
**Allocated theme:** Human factors, physical security and operational resilience
**Threats modelled:** T7 (social engineering / vishing), T8 (physical compromise of the head-office server room)

> This section is individually authored and individually assessed. The two threats below are
> my own work and remain attributable to me in the combined group plan.

## Risk rating method used

Risk = Likelihood × Impact, each scored 1–5, giving a 1–25 score. Bands: 1–4 Low, 5–9
Medium, 10–14 High, 15–25 Critical. Likelihood is assessed against Northbridge's current
state, with no compensating controls assumed.

A note on scope. My two threats are the ones that cannot be fixed by buying a product, and
both are easy to under-rate for that reason. The brief's technical weaknesses are extensive,
but the brief's own narrative opens with a *person* receiving a phone call and closes the
weaknesses section by stating that the attempt "was only stopped by that individual's own
instinct, not by any policy, training, or process the organisation had in place". I have
modelled the two threats where Northbridge's defence is currently a coincidence.

---

## Threat Model T7 — Social engineering (vishing) against staff credentials

### Asset

**Staff credentials**, and through them the **core banking application**, the **internal email
system** and the **remote-access VPN**. The brief lists the internal email system and staff
credentials among the assets every employee relies on to do their job. Credentials are the
asset here because they are the one asset an attacker can obtain by *asking*.

A secondary asset is the **shared VPN password specifically** — a single phrase that, if
disclosed by any one of a number of remote staff and two contractors, grants network access.
That makes it an unusually efficient vishing target: one successful call against any holder
yields the whole organisation's remote access.

### Vulnerability

The vulnerability is organisational and it is stated plainly in the brief:

1. **No security awareness training programme at all.** The brief uses the words "most
   fundamentally" to introduce this, and states the recent attempt "was only stopped by that
   individual's own instinct".
2. **No incident response process.** The employee reported the attempt internally and "the
   incident was logged", but there was no process to escalate it, no mechanism to warn other
   staff that a campaign was in progress, and no trigger to rotate the credential that was
   being asked for.
3. **No policy** that would have told the employee what to do — specifically, no policy
   stating that IT will never ask for a password, and no verified callback procedure giving
   staff a safe way to check.
4. **Password sharing is already normalised.** The brief says password sharing is common among
   branch office staff. This is the detail that makes vishing far more likely to succeed at
   Northbridge than elsewhere: an organisation where colleagues routinely share passwords has
   trained its staff that disclosing a password to someone who sounds legitimate is a normal
   act. The social norm the attacker needs is already in place.
5. **No MFA anywhere**, so a disclosed password is sufficient on its own. In an
   MFA-protected organisation, vishing a password yields much less.

### Threat

A **social engineer** conducting voice phishing, impersonating the IT Helpdesk. This is not a
hypothetical actor at Northbridge — the brief records an attempt that has already happened. A
single documented attempt also implies two further possibilities worth stating: that the
caller was reconnaissance for a larger campaign, and that other staff may have been called
and either complied or simply did not report it, since no process existed to make reporting
routine.

Realistic variants: a ransomware affiliate's access broker, who specialises only in obtaining
initial credentials; an attacker targeting the imminent payment processor integration; or an
opportunist working through a list of regional financial firms.

### Exploit

The exploit is **human**, and the brief describes the exact pretext used: a caller claiming to
be from "IT Helpdesk", "urgently requesting their password to fix a supposed system issue".
Its components are standard and effective:

- **Authority** — claiming to be internal IT, a role staff are conditioned to cooperate with.
- **Urgency** — "a supposed system issue", which compresses the victim's decision time and
  discourages verification.
- **Plausibility** — Northbridge has no centralised authentication, so password problems on
  individual systems are a genuine, frequent occurrence. The pretext matches the victim's
  lived experience, which is why it works.
- **No safe verification path** — with no policy and no published helpdesk callback number, a
  suspicious employee has no defined way to check, so the socially easier option is to
  comply.

The follow-on exploit is **credential reuse**, which the brief documents. A password disclosed
for one system is likely valid on others, so one successful call yields more than one access.

### Attack

1. **Reconnaissance.** The attacker builds a staff list from public sources — professional
   networking profiles, the bank's own website, branch listings. For a 450-staff regional bank
   with seven public sites, this is straightforward.
2. **Pretexting call.** The attacker calls a target, most likely a branch employee rather
   than a head-office one, as branch staff are less likely to know the IT team personally. The
   claim: a system issue requires their password immediately.
3. **Disclosure.** The target complies. The brief's documented incident ended with the
   employee growing suspicious "partway through the call" and not complying — but partway
   through means the pretext worked initially, and the attacker needs only one of several
   hundred attempts to succeed.
4. **Immediate use.** The credential is tested against the online banking portal's staff
   interface, webmail, and the remote-access VPN. No MFA stands anywhere, so a valid password
   is sufficient.
5. **Expansion.** Reuse is tested against other systems. Because each device and application
   holds its own local accounts, there is no central lockout correlating the attempts.
6. **No detection, and no warning to others.** No centralised logging would show a staff
   credential authenticating from an unusual location. No incident response process exists to
   convert the earlier reported attempt into a warning that would have put the next target on
   guard.
7. **Hand-off.** The access is used directly, or sold. In the ransomware economy the brief
   alludes to, initial access brokers obtain credentials precisely to sell them on — which
   means T7 is the *supply* side of Member 2's T3.

### Impact

- **T7 is the entry condition for the report's other critical threats.** This is its most
  important property and the reason it must not be under-rated. A disclosed password feeds
  T1 (shared VPN compromise), T2 (credential replay and escalation) and T3 (ransomware
  foothold). Its direct impact is modest — one account — but its enabling impact is the maximum
  available in the environment, because Northbridge has no second factor, no segmentation and
  no detection to absorb the consequences.
- **Confidentiality.** Immediate access to whatever that employee could reach, including
  customer data in the core banking application for a branch role.
- **Integrity and fraud.** A branch employee's credential permits transaction operations
  within their role. With no audit trail, the fraud is attributed to the employee, not the
  attacker — which is a serious secondary harm to an innocent person, and one worth naming.
- **Availability.** Only indirect, via the ransomware chain that this credential may start.
- **The repeatability problem.** Unlike a software vulnerability, this one cannot be patched.
  Without a training programme, the organisation is equally vulnerable to the same call next
  week, and each unreported attempt teaches the attacker what works.
- **Reputational and regulatory.** "Customer data disclosed because an employee gave a
  password to a caller, and the bank had no training programme" is a finding with no
  technical defence available in mitigation — the brief establishes that Northbridge knew,
  because the earlier attempt was logged.

### Risk

**Likelihood 5 / Impact 4 → Score 20 → CRITICAL.**

Likelihood is the maximum, and I want to justify that carefully because the brief's documented
attempt *failed*. It failed because of one individual's instinct, which is not a control — it
is a coincidence, and it will not recur reliably across 450 staff. Four Northbridge-specific
factors put this at 5 rather than 4. The attack has already been attempted, so the actor and
the pretext are confirmed rather than predicted. There is no training programme, so there is
no baseline resistance. There is no incident response process, so the one attempt that *was*
reported produced no organisational learning and no warning to anyone else. And — the factor I
regard as decisive — **password sharing is already common**, so disclosing a password to
someone who sounds legitimate is already normal behaviour at Northbridge. The attacker does
not need to overcome a cultural norm; the norm is already on their side.

Impact is 4 rather than 5 because the immediate consequence is the compromise of one account
at one privilege level, not direct control of the core banking database. Scoring it 5 would
double-count the impact already assessed in T1, T2 and T3, which is where the escalated
consequences properly sit. I note, however, that 4 understates its *strategic* significance:
T7 is the cheapest, most reliable entry point in the entire environment, requiring no
software exploit, no physical access and no technical skill. In remediation priority I would
place it above several higher-scoring threats, because removing it removes the input to three
of them.

---

## Threat Model T8 — Physical compromise of the head-office server room, and the unrecoverable outage that follows

### Asset

The **physical infrastructure hosting the core banking application and customer database** in
the on-premises head-office data centre, the **backup media**, and the **network equipment in
branch back offices**. This is the asset the brief says Northbridge has historically protected
best — its security investment "has gone almost entirely into physical measures (vaults, alarm
systems, branch cameras)" — which makes the server room's exclusion from that investment the
sharpest irony in the scenario and the reason I chose to model it.

### Vulnerability

The brief is unusually specific here, and every detail is a separate gap:

1. **The head-office server room is secured by a single shared key** rather than any auditable
   access mechanism. A shared key is the physical equivalent of the shared VPN account: it
   cannot be revoked for one holder, it cannot be audited, and nobody knows how many copies
   exist.
2. **There is no camera coverage of the room at all.** The brief states that if someone
   entered outside business hours "there would be no record of who it was or when it happened,
   and no visible deterrent to discourage them from trying in the first place". Note that the
   bank has cameras — in branches, for cash — but not on its most critical asset.
3. **No security signage, no badge-checking presence and no camera coverage at entry points**
   at any site, so nothing discourages an opportunistic intruder before they reach the door.
4. **Visitor sign-ins are inconsistently enforced**, so an unaccompanied stranger inside a
   Northbridge building is unremarkable.
5. **Branch network cabinets were found unlocked in at least two locations** during an informal
   walkthrough — so the same exposure exists at seven sites, not one.
6. **Backups exist but have never been tested for restoration**, and **no documented disaster
   recovery or incident response plan exists**. This is what converts a physical intrusion
   from an expensive incident into a potentially unrecoverable one.

### Threat

- An **opportunistic intruder** — the actor the brief implicitly describes with "no visible
  deterrent to discourage them from trying in the first place".
- A **malicious insider or former employee** holding a copy of the shared key, or a contractor
  who was once given access. Because the key is shared, there is no way to establish who holds
  one.
- A **targeted physical intruder** using a pretext — a maintenance engineer, a courier, a fire
  inspector. Against unenforced visitor sign-in, no badge checking and no signage, this needs
  little sophistication.
- A **malicious visitor at a branch**, exploiting the unlocked cabinets instead of the server
  room.

### Exploit

The exploit is **unaudited and undeterred physical access**, and physical access defeats
controls that logical access cannot touch:

- **Console access.** A directly attached keyboard bypasses network access controls entirely.
  Cisco password recovery via the configuration register, and equivalent single-user-mode
  procedures on servers, are documented vendor processes requiring only a reboot — no exploit
  and no credential.
- **Direct storage access.** Drives can be removed. With no data classification policy, the
  brief gives no reason to believe the core banking database is encrypted at rest, so removed
  drives yield plaintext customer financial data.
- **Backup media.** Backup media in the same unaudited room can be taken or destroyed. This
  is the step that removes recovery.
- **Implant placement.** A small device on the network inside the server room provides
  persistent remote access, on a flat network, with no IDS/IPS to notice it and no camera
  footage to later explain where it came from.
- **At branches**, the unlocked cabinet gives switch console access and an open port in a
  trusted VLAN — which is the physical entry route for Member 2's T4.

### Attack

Two chains; the second is the severe one.

**Chain A — data theft.** Intruder enters outside business hours using a copy of the shared
key, or during hours via unenforced visitor sign-in. No signage deterred them, no badge check
intercepted them, no camera recorded them. Drives are removed from the database server, or
console access is used to reset credentials and copy data. Backup media is taken as well, as
it is a complete copy of the same data in a more portable form. The intruder leaves. **No
record exists that anyone was ever there** — the brief says so explicitly — so Northbridge may
not know a breach occurred until the data surfaces.

**Chain B — destruction, and failed recovery.**
1. Intruder enters the server room as above.
2. Physical damage or deliberate destruction of the core banking servers and storage —
   achievable in minutes, and requiring no technical skill.
3. **Backup media in the same room is destroyed or taken.** An unaudited room containing both
   the primary systems and their backups means one visit defeats both.
4. Core banking, the online banking portal and the mobile app all stop. Seven sites and
   roughly 450 staff cannot serve customers.
5. **Recovery is attempted for the first time ever.** The brief states backups have never been
   tested for successful restoration, so Northbridge discovers whether its backups work during
   the worst week in its history. There is **no documented disaster recovery plan**, so the
   restoration sequence, the dependencies and the responsible people are all being determined
   live.
6. If the offsite copy is incomplete, corrupt, or was in the same room: **permanent loss of a
   licensed bank's customer ledger.**

### Impact

- **Availability — potentially permanent.** This is the only threat in this report whose
  worst case is *irrecoverable*. Ransomware at least offers the attacker's incentive to
  decrypt; physical destruction offers nothing, and untested backups mean no verified
  alternative exists.
- **Confidentiality.** Removed drives or stolen backup media, most likely unencrypted given the
  absence of a data classification policy, deliver the complete customer database at once —
  with no network trace of any kind.
- **Integrity.** Console access allows configuration and data changes that leave no network
  evidence, and no camera footage to establish who made them.
- **Forensic and accountability — total failure.** A shared key with unknown copy count and no
  camera coverage means Northbridge cannot determine who entered, when, or even that anyone
  did. An insider is effectively unidentifiable.
- **Regulatory — compounded.** Three separate findings stack: inadequate physical access
  control over a regulated data environment, no tested backups, and no documented disaster
  recovery plan. The third is often a licensing condition in its own right for a deposit-taking
  institution.
- **Business continuity.** A bank that cannot confirm customer balances cannot open. The brief
  frames continuous branch-to-head-office connectivity and customer confidence as conditions
  of operating; a multi-day or permanent outage is a solvency event.
- **The irony is itself a finding.** Northbridge demonstrably knows how to do physical
  security — it has vaults, alarms and branch cameras. Choosing to protect cash and not the
  server room is a risk-assessment failure that an auditor will characterise as negligence
  rather than as an oversight.

### Risk

**Likelihood 3 / Impact 5 → Score 15 → CRITICAL (low end).**

Likelihood is 3, and this is the score I debated longest. Three arguments push it up: the
brief confirms every barrier is absent (shared key, no cameras, no signage, no badge checking,
unenforced visitor sign-in, unlocked branch cabinets in at least two locations), the key
holder population is unknown and unbounded, and the attack needs no technical skill at all.
One argument holds it down, and I judge it decisive: unlike T1, T5 and T7, this attack
requires the attacker to **physically attend a Northbridge building**. That bounds the
attacker population to people in the region who are willing to accept personal physical risk,
which is a far smaller and far more deterred population than the internet. Northbridge also
has existing alarm systems, which, while not covering the server room, raise the general
difficulty of after-hours entry. I have scored 3 rather than 4 to stay honest about that,
rather than inflating it to match the impact.

Impact is 5 without qualification, and it is the only threat in this report where I would
argue the impact is *beyond* the top of the scale. Every other critical threat has a recovery
path, even a painful one. This one, in its Chain B form, can end with the primary systems and
the only copies of the data destroyed in a single visit, in an organisation with no tested
restoration and no documented disaster recovery plan. That is an existential outcome for a
deposit-taking institution.

**The reason this stays in the critical band on the lowest likelihood in the report is the
dependency between the two halves.** The physical gap and the untested-backup gap are
individually serious and jointly existential. If Northbridge did nothing else but
(a) put auditable access control and a camera on the server room and (b) prove once that it
can restore its core banking database from an offline copy, the impact of this threat drops
from 5 to 3 and it leaves the critical band entirely. Those are also two of the cheapest
controls in the group's whole plan — one is a door reader and a camera at an organisation that
already buys cameras, and the other is a scheduled test that buys no product at all. That
cost-to-risk ratio is the argument I brought to the group's control minimisation discussion,
and it is why the plan treats backup restoration testing as a control in its own right rather
than as an assumed property of the existing backup.
