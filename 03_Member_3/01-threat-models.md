# Member 3 — Individual Threat Modelling

**Member:** [Member 3 — Full Name / IT Number]
**Allocated theme:** Internet perimeter, application security and third-party trust
**Threats modelled:** T5 (SQL injection against the online banking portal), T6 (abuse of the third-party payment processor connection)

> This section is individually authored and individually assessed. The two threats below are
> my own work and remain attributable to me in the combined group plan.

## Risk rating method used

Risk = Likelihood × Impact, each scored 1–5, giving a 1–25 score. Bands: 1–4 Low, 5–9
Medium, 10–14 High, 15–25 Critical. Likelihood is assessed against Northbridge's current
state, with no compensating controls assumed.

---

## Threat Model T5 — SQL injection against the internet-facing online banking portal

### Asset

The **customer database** holding customer financial and personal data, reached through the
**online banking portal and mobile app** that the brief states are "exposed to the public
internet". The brief names both as prime targets "given the direct financial and regulatory
consequences of a compromise", and the portal is the only asset in the environment that is
deliberately reachable by anyone on the internet — which makes it the attack surface of first
resort.

### Vulnerability

The vulnerability has two layers, and the architectural layer is the one that makes the
application layer fatal.

**Application layer.** The brief does not state that the portal has any application security
assurance, and it describes an organisation with no data classification policy, no patch
management process and no secure development practice of any kind. There is no mention of
code review, penetration testing or a web application firewall. For a decade-old,
organically grown environment, the reasonable working assumption is that the portal and the
mobile app's API contain injectable input handling — unparameterised queries built by string
concatenation — because nothing in the organisation would have found it if they did.

**Architectural layer.** Three specific gaps turn a single injectable parameter into a full
database breach:

1. **No DMZ.** The brief describes a flat network where head office systems share space with
   everything else, and no dedicated firewall beyond "the basic firewall/router functionality
   built into its internet-facing router". The portal's web tier therefore sits in the same
   trust space as the database it queries, rather than behind a filtering boundary.
2. **No IDS/IPS anywhere**, so injection attempts generate no alert, and the attacker can
   iterate through hundreds of failed payloads without consequence.
3. **No centralised logging or audit trail**, so even a successful mass extraction leaves no
   correlated record anyone would examine.

A fourth factor compounds all three: **no data classification policy**, so "staff have no
guidance on which information needs to be encrypted". It is therefore likely that customer
financial data is stored unencrypted at rest, meaning a successful query returns usable
plaintext rather than ciphertext.

### Threat

An **external, unauthenticated attacker on the internet** — the broadest possible threat
population. This threat requires no insider, no physical access, no credential and no
proximity, which distinguishes it from every other threat modelled in this report. Realistic
actors span automated vulnerability scanners run indiscriminately against banking domains,
financially motivated criminal groups, and credential brokers harvesting customer records for
resale.

### Exploit

**SQL injection**, exploited in the standard progression:

1. **Discovery.** The attacker enumerates portal and mobile API parameters — login forms,
   account lookup fields, statement date ranges, transaction search — probing each with
   metacharacters and observing error messages or response-time differences. With no IPS and
   no rate limiting described, this reconnaissance is unlimited and silent.
2. **Confirmation.** A boolean-based or error-based response confirms that input reaches the
   query. The mobile app's API is often the softer target, because API endpoints are
   frequently built on the assumption that only the app will call them, and so receive less
   input validation than the web forms do.
3. **Exploitation.** `UNION`-based or blind extraction enumerates the schema, then the
   customer table. If the portal's database account is over-privileged — likely in an
   environment with no least-privilege policy — the attacker can also read other databases on
   the same instance, write files, or in some configurations execute operating-system
   commands through database extended procedures.

The exploit at the architectural level is the **absence of a boundary**: the web tier holds a
live, trusted connection to the customer database, and nothing inspects or constrains what
travels over it.

### Attack

1. Attacker reaches the portal over HTTPS from anywhere on the internet. Northbridge's
   internet-facing router passes the traffic — it is a legitimate connection to a published
   service, and a router ACL cannot inspect query content.
2. Injectable parameter located and confirmed. No IPS alert, no WAF block, no log review.
3. Schema and customer table enumerated. Extraction is paced to look like ordinary portal
   traffic; with no centralised logging and no baseline of normal volumes, there is nothing to
   compare it against.
4. **Bulk extraction of customer financial and personal records**, most likely in plaintext
   given the absence of a data classification or encryption policy.
5. **Escalation beyond the database.** Because the web tier is not isolated in a DMZ, the
   attacker's foothold is inside the flat network. From there the chain joins Member 2's T3:
   internal reconnaissance, credential harvesting, lateral movement, and potentially
   ransomware — all from an unauthenticated internet start.
6. Northbridge most likely learns of this from a third party — a regulator, a card scheme, or
   the records appearing for sale — rather than from its own monitoring.

### Impact

- **Confidentiality — maximum and irreversible.** Mass disclosure of customer financial and
  personal data. Unlike an availability incident, this cannot be undone by recovery; the
  records are gone.
- **Regulatory.** A breach of customer financial data at a licensed financial institution is
  reportable, investigable and penalty-bearing. The brief frames Northbridge's regulatory
  standing as something its ability to operate depends on.
- **Integrity.** SQL injection writes as well as reads. An attacker who can `UPDATE` account
  balances or `INSERT` transactions attacks the bank's ledger directly, and with no audit
  trail Northbridge cannot determine which records are trustworthy — potentially forcing a
  reconciliation of the entire customer base.
- **Availability.** `DROP` or mass `DELETE` is available to the same access, and the brief
  states backups have never been test-restored.
- **The payment processor integration fails its own assessment.** The integration is due to go
  live within two quarters, and payment partners conduct their own security assessments of a
  counterparty. An unpatched injectable public portal is exactly what such an assessment
  looks for.
- **Reputational — the worst variant available.** Customer financial data disclosed through a
  bank's *own online banking portal* is the most damaging possible framing: it is the one
  system every customer uses personally and the one they will judge the bank by.

### Risk

**Likelihood 4 / Impact 5 → Score 20 → CRITICAL.**

Likelihood is 4 and not 5 because, unlike T1's shared credential or T3's unpatched branch
workstation, the brief does not explicitly state that an injectable flaw exists — it is
inferred from the absence of every process that would have found one. I have scored it high
rather than maximum to be honest about that inference. It is not lower than 4 because the
*attempt* is certain, not probable: an internet-facing banking portal is scanned
continuously, automatically, by actors who need no reason to target Northbridge specifically.
And Northbridge has no control that would stop a successful attempt — no WAF, no IPS, no code
review, no penetration test, no DMZ, no logging. The likelihood of attempt is 5; the
likelihood of a flaw existing is the uncertainty, and an organisation that has never looked
is far more likely to have one than one that has.

Impact is 5, and the specific reason is the combination of **no data classification policy**
with **no DMZ**. Either alone would be serious. Together they mean a successful injection
returns plaintext customer financial data *and* delivers the attacker a foothold inside the
flat network, so the same attack simultaneously achieves the maximum confidentiality outcome
and the entry condition for the maximum availability outcome. There is no version of this
event that is merely bad.

This is the only critical threat in the report that an unauthenticated stranger can execute
from the internet with no prerequisite at all, which is why I argued in the group discussion
that the DMZ boundary should be treated as non-negotiable rather than as a phase 2 item.

---

## Threat Model T6 — Abuse of the third-party payment processor connection

### Asset

The **two third-party payment processing integrations** and, through them, the **core banking
database** and Northbridge's **ability to process digital transactions**. The brief states
these integrations "will shortly become a critical dependency in its own right, extending
trust beyond Northbridge's own infrastructure for the first time" — which is the precise
definition of a new attack surface.

### Vulnerability

1. **No vendor security assessment process has been defined** for the integration, which the
   brief states explicitly and flags as "a gap that will only become more pressing once the
   third-party payment integration goes live". Northbridge therefore has no basis on which to
   judge either partner's security posture.
2. **No network segmentation**, so a partner connection terminating today would terminate
   into the same flat space as everything else, with no partner zone to contain it.
3. **No IDS/IPS and no centralised logging**, so traffic arriving over a trusted partner link
   is neither inspected nor recorded.
4. **No data classification policy**, so there is no definition of what data may cross the
   integration boundary, in what form, or with what encryption.
5. **No incident response plan**, so there is no defined procedure for what Northbridge does
   when a partner notifies it of a breach — including the question of whether to sever the
   connection, and who has the authority to.

The underlying vulnerability is **unbounded transitive trust**: Northbridge is about to accept
a partner's security posture as its own without having measured it.

### Threat

- A **compromised third-party payment processor** — the attacker's actual victim is the
  partner, and Northbridge is the onward target. This is the supply-chain pattern.
- A **malicious or negligent insider at a partner**, with legitimate access to the
  integration.
- An **attacker who steals the integration's credentials or API keys** from the partner's
  environment and replays them against Northbridge from elsewhere.

The important property of all three is that traffic arrives over a connection Northbridge has
itself designated as trusted, which defeats perimeter controls by design rather than by
evasion.

### Exploit

The exploit is **abuse of legitimate authorised access**, and it takes three forms depending
on how the integration is built:

1. **Credential or API key replay.** If the integration authenticates with a static shared
   secret or API key — likely, since Northbridge has no PKI and no central identity, and its
   existing pattern is shared credentials — then an attacker holding that key is
   indistinguishable from the partner. There is no mutual TLS certificate to also need, and
   no IP allow-list described.
2. **Injection through the integration interface.** Transaction messages from a partner are
   parsed by Northbridge's systems. Without input validation on that interface — and with no
   secure development process anywhere — malformed messages are a direct path to the same
   class of flaw as T5, but arriving from a source that nothing inspects.
3. **Lateral movement from the integration endpoint.** Once the attacker has reached whatever
   system terminates the partner connection, the flat network gives that system the same
   reach as any other. A connection intended to carry payment messages becomes a route to the
   customer database.

### Attack

1. Partner A is compromised — by any means, and entirely outside Northbridge's control or
   visibility, because no vendor assessment process exists to have evaluated their controls.
2. The attacker locates the Northbridge integration credentials and endpoint details in the
   partner's environment.
3. The attacker connects to Northbridge's integration endpoint, authenticating as Partner A.
   Northbridge's router permits it: this is expected, authorised traffic from a trusted
   source.
4. **Path A — fraudulent transactions.** The attacker submits crafted payment instructions.
   Each is individually plausible, and the brief notes Northbridge has no centralised logging
   with which to spot anomalous volumes or patterns.
5. **Path B — pivot.** The attacker abuses the integration interface or the endpoint host to
   obtain execution on Northbridge's network, then moves laterally across the unsegmented
   space toward the core banking database — rejoining T3's and T5's chains with a trusted
   start point.
6. Detection depends entirely on Partner A noticing and telling Northbridge. There is no
   incident response plan governing what happens next, and no defined authority to sever the
   connection — so the likely initial response is an argument about whether to take the new
   digital payments service offline, during business hours, while the attack continues.

### Impact

- **Direct financial loss.** Unlike every other threat in this report, this one moves money
  rather than data. Fraudulent transaction processing is an immediate loss to Northbridge or
  its customers, and payment fraud is frequently irrecoverable once settled.
- **A critical new dependency becomes a liability.** The brief describes the integration as
  supporting "faster digital transactions" — a strategic commitment. Suspending it in response
  to an incident means losing the business capability the project was built for.
- **Confidentiality.** Payment integrations carry customer and transaction data by
  definition; a compromised partner connection is a disclosure channel.
- **Contagion in both directions.** Northbridge may be the route by which the attacker reaches
  the *other* partner, or other banks connected to the same processor, which escalates a
  Northbridge incident into an industry one and makes Northbridge the named cause.
- **Regulatory — specifically on third-party risk.** Financial regulators treat outsourcing
  and third-party risk management as a named obligation. The brief's statement that no vendor
  security assessment process exists is an audit finding on its own, and going live without
  one converts it into a breach of process at the point of an incident.
- **Attribution and dispute.** With no logging on Northbridge's side and no contractual right
  to audit, establishing whether the fraud originated at the partner or at Northbridge may be
  impossible — which determines who bears the loss.

### Risk

**Likelihood 3 / Impact 5 → Score 15 → CRITICAL (low end).**

Likelihood is 3 — **the lowest likelihood score I have assigned to any threat in this report**,
and deliberately so. Two reasons. First, the integration is not yet live; the brief says it is
"due to go live within the next two quarters", so there is currently no connection to abuse.
Second, exploitation requires the compromise of a third party that is itself a payment
processor — an organisation likely to be more security-mature than Northbridge, holding
regulatory obligations of its own. I will not inflate this to 4 or 5 simply because supply
chain attacks are topical; for *this* organisation on *today's* date the precondition is
genuinely not yet met.

Impact is 5 without qualification. It is the only threat here with a direct cash loss
mechanism, it compromises an asset the brief names as about to become a critical dependency,
and it carries a contagion dimension that extends the consequence beyond Northbridge's own
boundary — which no other modelled threat does.

The reason this still lands in the critical band despite the lowest likelihood in the report
is **timing, and timing is the whole point of this threat model.** Every other threat I could
remediate after an incident. This one has a fixed deadline: the integration goes live within
two quarters, and on the day it does, the likelihood score moves from 3 to at least 4 and the
cost of retrofitting a partner zone, mutual TLS, input validation and a vendor assessment
process rises sharply — because by then the partners' own integration is built against
whatever Northbridge shipped. The brief states the CTO commissioned this review "before the
integration proceeds". My assessment is that T6 is the threat that justifies that sequencing,
and the group plan should treat the partner-zone and vendor-assessment controls as having a
hard deadline rather than a priority ranking.
