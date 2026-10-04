# 3. Individual Threat Modelling

Eight threats, two per member, each individually authored and individually attributable. All
four members used the common method set out in Section 2.2.

| ID | Member | Threat | L | I | Score |
|---|---|---|---|---|---|
| T1 | 1 | Compromise of the shared VPN account | 5 | 5 | 25 |
| T2 | 1 | Credential abuse and escalation without central AAA | 4 | 5 | 20 |
| T3 | 2 | Ransomware propagation across the flat network | 5 | 5 | 25 |
| T4 | 2 | Rogue DHCP and ARP spoofing from guest Wi-Fi | 4 | 4 | 16 |
| T5 | 3 | SQL injection against the online banking portal | 4 | 5 | 20 |
| T6 | 3 | Abuse of the third party payment processor connection | 3 | 5 | 15 |
| T7 | 4 | Social engineering against staff credentials | 5 | 4 | 20 |
| T8 | 4 | Physical compromise of the server room | 3 | 5 | 15 |

## 3.1 Member 1: identity and remote access

### T1. Compromise of the shared VPN account

**Asset.** The core banking application and customer database, reached through the remote access
VPN. The brief names customer financial data as the most critical asset, so this is the highest
value target in the environment.

**Vulnerability.** A single shared VPN account, used interchangeably by all remote staff and
both external contractors, with no MFA and no individual accountability. Three properties make
this worse than a generic weak credential. The credential is known to people outside
Northbridge's employment. It cannot be rotated on a leaver event without disrupting every remote
user, so in practice it is long lived. There is no central authentication and no audit trail, so
its use produces no attributable record.

**Threat.** An external attacker, or a former contractor employee who retains the password,
seeking authenticated network level access. A secondary actor is a credential broker, since
shared VPN credentials for financial targets have resale value.

**Exploit.** The attacker obtains the password by any of three routes the environment leaves
open. Phishing or vishing a remote user, which the brief shows has already been attempted and
for which there is no awareness training. Credential reuse, since password sharing is documented
as common. Contractor side leakage, since the password sits in two external organisations and
there is no vendor assessment process. No software exploit is required. The exploit is the
legitimate use of a valid credential by the wrong person.

**Attack.** The attacker authenticates to the VPN, indistinguishable from a legitimate remote
worker because the account is used by many people from many locations. The VPN places them inside
the flat network, so no internal boundary remains, and reconnaissance raises no alert since there
is no IDS. They locate the database, harvest further credentials, then exfiltrate data or deploy
ransomware.

**Impact.** Mass disclosure of customer financial records, the worst outcome available here.
Integrity loss, since the attacker holds legitimate access and no audit trail can prove what
changed. Availability loss if the intrusion ends in ransomware, with recovery time unknown
because backups have never been restored. A reportable regulatory event, which would very likely
suspend the payment processor integration. Forensically, Northbridge cannot answer who accessed
what and when, which forces worst case assumptions about scope.

**Risk: Likelihood 5, Impact 5, score 25, Critical.** Likelihood is maximum for reasons specific
to Northbridge, not generic. Three independent routes to the credential are already open, there
is no second factor to stop a stolen credential, and no detective control would notice it being
used from an anomalous location. A control is only as strong as its weakest independent bypass,
and here every bypass is unmitigated. Impact is maximum because the asset reached is the bank's
own most critical asset, the flat network makes VPN access and core banking reachability the
same privilege, and untested backups remove the one control that would cap availability impact.
This is the threat that must be remediated before the payment integration proceeds, because that
integration extends trust outward from a network which cannot identify its own remote users.

### T2. Credential abuse and privilege escalation without central AAA

**Asset.** Staff credentials, and through them the core banking application, internal email, and
the network infrastructure itself. Credentials are a hinge asset, compromising them yields the
others.

**Vulnerability.** Four weaknesses compound. No central authentication, so every device and
application holds its own local accounts. Password reuse and sharing are common among branch
staff. No central logging, so unusual behaviour would not be noticed in time. No joiner, mover
and leaver process, which follows from the first point. Northbridge cannot answer which accounts
a person holds, or whether a departing user has been disabled everywhere.

**Threat.** A malicious or disgruntled insider, or an external attacker who already holds one
low value credential and wants to escalate.

**Exploit.** Credential replay across trust boundaries. Because the same password is reused and
no central identity ties systems together, one credential is tested against every system with a
login. Network device access is the highest value variant, since no central authentication for
infrastructure implies shared local enable passwords, the classic pattern where one password
opens the whole estate.

**Attack.** The attacker obtains one working credential, then replays it horizontally against
other staff accounts and vertically against application and infrastructure logins. With no lockout
policy and no central service correlating failures, testing is effectively free of risk. A hit on
a switch, router or administrative account yields privileged control, which on a flat network is
enough to reach core banking.

**Impact.** Integrity first, confidentiality second. The defining impact is fraud, since an
insider with core banking access can move money or alter records, and no audit trail can detect
or prove it. Non repudiation collapses entirely, so even a correctly suspected insider may be
unprosecutable. Leaver risk becomes permanent, because access was never revoked from one place.
Segregation of duties and individual accountability are baseline regulatory expectations, so
this is an audit finding whether or not it is exploited.

**Risk: Likelihood 4, Impact 5, score 20, Critical.** Likelihood is 4 rather than 5 because
exploitation needs the attacker to already hold one credential, one step more than T1. It is not
lower, because password reuse and sharing are documented as already happening. The precondition
is current practice, not hypothesis, and 450 staff across seven sites makes at least one reused
credential a near certainty. Impact is 5 because the fraud and non repudiation consequences are
specific to a bank. An organisation that cannot attribute a transaction to a person has lost the
property its regulatory standing rests on. The absence of central logging is what moves this
from a hygiene issue to a critical one.

T1 and T2 share one root cause, the absence of a central identity and accounting authority, and
should be remediated by one control programme rather than two.

## 3.2 Member 2: segmentation and Layer 2

### T3. Ransomware propagation from a branch workstation to the core banking database

**Asset.** The core banking database, and the continuous branch to head office connectivity the
brief says core banking depends on. Availability is the asset under threat here more than
confidentiality.

**Vulnerability.** Three weaknesses stack, and the stacking is what makes this the brief's own
worst case. No segmentation, with head office systems, branch systems, guest Wi-Fi and point of
service equipment sharing the same network space. No patch process, with several branch systems
known to run outdated software. No IDS or IPS and no central logging, leaving the bank blind
until damage is visible. Individually each is common. Together they describe a network where a
foothold has unrestricted reach, a reliable way in, and no observer.

**Threat.** A ransomware operator or affiliate targeting mid sized financial firms. This is not
speculative. The brief states a regional association reported a sharp rise in such incidents,
several beginning with one compromised branch workstation and spreading across an unsegmented
network. The actor, the entry point and the propagation method are all documented as active
against Northbridge's peer group.

**Exploit.** Entry through the unpatched branch workstation. A phishing email reaches a branch
user, and with no awareness training the probability of a click is the untrained baseline. The
payload exploits a known, already patched upstream vulnerability. This is the key point, the
attacker needs no novel capability, because publicly documented exploits remain live on the
estate. Propagation then exploits the flat network itself, where file sharing and remote
management protocols become a propagation fabric in the absence of a trust boundary.

**Attack.** Day 0, a branch workstation is compromised, with no alert raised. Days 0 to 2, the
malware enumerates the flat address space, reaching head office servers from a branch PC without
crossing a filtering device. Days 1 to 5, local credentials are harvested and replayed, made
unusually productive by documented password reuse. Days 2 to 7, the operator reaches server
infrastructure, identifies the database, and locates and deletes the backups. This is standard
practice, and Northbridge is especially exposed, since backups have never been tested, which
implies they are online and reachable. Day 7, simultaneous encryption across branches, servers
and the database. The response is then improvised, since no incident response plan exists.

**Impact.** Availability is dominant. Core banking, the portal and the mobile app stop, and
seven sites cannot serve customers. For a savings and finance provider a multi day outage is a
solvency event, not an IT problem. Recovery is unbounded, since untested backups are a
hypothesis. Modern ransomware exfiltrates before encrypting, so this is simultaneously a data
breach. The payment integration is lost or deferred, since no partner completes a technical
integration with a bank mid recovery.

**Risk: Likelihood 5, Impact 5, score 25, Critical.** Likelihood is maximum specifically, not
generically. The brief does not merely leave the door open, it reports that this exact attack
pattern has been observed several times against Northbridge's own peer group within the past
year. Every precondition is present at once: a reliable entry route, unrestricted propagation,
productive credential reuse, and no detection to shorten dwell time. There is no single control
in place that this chain would have to defeat. Impact is maximum because of the untested backups
specifically. With a tested offline backup this would score impact 4, a bad outage with a known
recovery path. Without one, the worst case is permanent loss of a bank's customer ledger.

### T4. Rogue DHCP and ARP spoofing from guest Wi-Fi

**Asset.** Staff credentials and in session banking data at branches, and the integrity of the
branch to head office path.

**Vulnerability.** Guest Wi-Fi, branch systems and point of service equipment share the same
Layer 2 broadcast domain as staff machines. That matters beyond general flatness, because
several Layer 2 protocols are trusting by design. DHCP has no authentication, so any host can
answer a discover, and the client accepts whichever offer arrives first. ARP has no
authentication, so any host can rewrite its neighbours' caches. Without port security any device
joins the segment, without DHCP snooping every port is treated as a legitimate server port, and
without Dynamic ARP Inspection every ARP reply is believed. Compounding this, physical access to
branch networking equipment is uncontrolled, with cabinets found unlocked in at least two
locations, and visitor sign ins are inconsistently enforced.

**Threat.** An opportunistic intruder or malicious visitor at a branch, a guest Wi-Fi user who
needs no physical access, or a compromised point of service device maintained by someone else.

**Exploit.** Two chained Layer 2 exploits, both achievable with standard public tooling. A rogue
DHCP server offering itself as the default gateway, which branch workstations accept on renewal
or boot. ARP cache poisoning for hosts that already hold a lease, inserting the attacker
bidirectionally without touching DHCP. With the path captured, the attacker harvests credentials
from unencrypted protocols and attempts interception of the rest. TLS stripping produces a
browser warning, but with no awareness training the chance of a branch user clicking through is
materially higher. That detail turns a partially mitigated attack into a working one.

**Attack.** The attacker gains the segment by Wi-Fi association, or by patching into an unlocked
cabinet during business hours. A rogue DHCP server is started with ARP poisoning in parallel, so
branch traffic flows through the attacker, who harvests credentials, session cookies and the
address of the core banking application. Those credentials are replayed against head office, with
no boundary to stop them and no IDS to observe them.

**Impact.** Confidentiality of credentials and live banking sessions. Integrity of the branch to
head office path, since a man in the middle can alter as well as read, and no central logging
exists to compare against. Availability, since the same position allows selective denial of
service. Most importantly this is an undetectable precursor, the cheapest way to obtain the
valid credentials that T2 and T3 then use. An unauthenticated member of the public reaching the
same Layer 2 segment as systems handling customer financial data is also a straightforward audit
failure.

**Risk: Likelihood 4, Impact 4, score 16, Critical at the low end.** Likelihood is high because
the attack needs no sophistication, the tooling is public, and Northbridge has removed every
obstacle at once. It is not 5 because exploitation still requires physical presence or Wi-Fi
proximity, which bounds the attacker population to people who turn up, unlike T1 and T3 which
are reachable from the internet. Impact is 4 rather than 5 because the attack yields credentials
and session data rather than direct control of the database. The maximum impact outcomes come
from the follow on use of what is captured, and scoring 5 would double count T2 and T3. It is
not lower than 4 because the credentials captured here are the ones that make the critical
threats work.

T3 and T4 both argue for the same fix, moving Northbridge from one trust space to many. The
Layer 2 baseline is where T4 is actually defeated, because segmentation alone does not stop an
attacker who is already inside the segment with the victims.

## 3.3 Member 3: perimeter, application, third party

### T5. SQL injection against the internet facing banking portal

**Asset.** The customer database, reached through the online banking portal and mobile app that
the brief says are exposed to the public internet. The portal is the only asset deliberately
reachable by anyone on the internet, which makes it the attack surface of first resort.

**Vulnerability.** Two layers, and the architectural layer is what makes the application layer
fatal. At the application layer, the brief describes no application security assurance of any
kind, no code review, no penetration testing and no web application firewall. For a decade old
organically grown environment the reasonable working assumption is that injectable input
handling exists, because nothing in the organisation would have found it. At the architectural
layer, three gaps turn one injectable parameter into a full breach. There is no DMZ, so the web
tier sits in the same trust space as the database it queries. There is no IDS or IPS, so
injection attempts raise no alert and the attacker can iterate freely. There is no central
logging, so even mass extraction leaves no correlated record. A fourth factor compounds all
three. With no data classification policy, customer data is likely unencrypted at rest, so a
successful query returns usable plaintext.

**Threat.** An external, unauthenticated attacker on the internet, the broadest possible threat
population. This threat requires no insider, no physical access, no credential and no proximity,
which distinguishes it from every other threat here.

**Exploit.** SQL injection in the standard progression. Discovery, probing portal and API
parameters and observing error messages or timing differences, unlimited and silent with no IPS
or rate limiting. Confirmation, where the mobile API is often the softer target because
endpoints built on the assumption only the app will call them receive less validation.
Exploitation, enumerating the schema and then the customer table. If the portal's database
account is over privileged, likely with no least privilege policy, the attacker can also read
other databases or execute commands. At the architectural level the exploit is the absence of a
boundary.

**Attack.** The attacker reaches the portal over HTTPS from anywhere, and the router passes the
traffic, since it is a legitimate connection to a published service and a router ACL cannot
inspect query content. An injectable parameter is confirmed with no IPS alert, no WAF block and no
log review. The schema and customer table are enumerated, with extraction paced to look like
ordinary traffic. Because the web tier is not isolated, the foothold is inside the flat network
and the chain joins T3.

**Impact.** Confidentiality loss is maximum and irreversible, since unlike an outage the records
cannot be recovered. A breach of customer financial data at a licensed institution is
reportable, investigable and penalty bearing. Injection writes as well as reads, so an attacker
who can alter balances attacks the ledger directly, and with no audit trail Northbridge cannot
determine which records are trustworthy. The payment integration would fail the partners' own
assessment. Reputationally this is the worst available framing, customer data disclosed through
the bank's own portal.

**Risk: Likelihood 4, Impact 5, score 20, Critical.** Likelihood is 4 and not 5 because, unlike
T1's shared credential or T3's unpatched workstation, the brief does not state that an
injectable flaw exists. It is inferred from the absence of every process that would have found
one, and the score is held at 4 to be honest about that inference. It is not lower, because the
attempt is certain rather than probable. An internet facing banking portal is scanned
continuously by actors who need no reason to target Northbridge, and no control would stop a
successful attempt. Impact is 5 specifically because no data classification policy combines with
no DMZ. Either alone would be serious. Together they mean one injection returns plaintext
customer data and delivers a foothold inside the flat network, achieving the maximum
confidentiality outcome and the entry condition for the maximum availability outcome at once.

This is the only critical threat an unauthenticated stranger can execute from the internet with
no prerequisite, which is why the DMZ boundary should be non negotiable rather than a phase 2
item.

### T6. Abuse of the third party payment processor connection

**Asset.** The two payment processing integrations, and through them the core banking database
and the ability to process digital transactions. The brief states these will shortly become a
critical dependency, extending trust beyond Northbridge's infrastructure for the first time.

**Vulnerability.** No vendor security assessment process has been defined, which the brief states
explicitly. No segmentation, so a partner connection would terminate into the same flat space as
everything else. No IDS or IPS and no central logging, so traffic arriving over a trusted link is
neither inspected nor recorded. No data classification policy, so there is no definition of what
data may cross the boundary or in what form. No incident response plan, so there is no procedure
for a partner breach notification, including who may sever the connection. The underlying
vulnerability is unbounded transitive trust, Northbridge is about to accept a partner's security
posture as its own without having measured it.

**Threat.** A compromised payment processor, where the attacker's actual victim is the partner
and Northbridge is the onward target. A malicious or negligent insider at a partner. An attacker
who steals the integration credentials and replays them from elsewhere. All three share one
property, traffic arrives over a connection Northbridge has designated as trusted, which defeats
perimeter controls by design rather than by evasion.

**Exploit.** Abuse of legitimate authorised access, in three forms. Credential or API key
replay, likely since Northbridge has no PKI and its existing pattern is shared credentials, so
an attacker holding the key is indistinguishable from the partner. Injection through the
integration interface, since transaction messages are parsed by Northbridge systems and no
secure development process exists. Lateral movement from the integration endpoint, since the
flat network gives that system the same reach as any other.

**Attack.** Partner A is compromised by means entirely outside Northbridge's visibility, because
no assessment process exists to have evaluated their controls. The attacker locates the
integration credentials and endpoint, then connects authenticating as Partner A. The router
permits it, since this is expected traffic from a trusted source. From there the attacker either
submits crafted payment instructions, each individually plausible with no central logging to
spot anomalous volumes, or pivots from the endpoint host across the unsegmented network toward
the database. Detection depends entirely on Partner A noticing and saying so, and the likely
initial response is an argument about whether to take the new payments service offline.

**Impact.** Direct financial loss. Unlike every other threat here this one moves money rather
than data, and payment fraud is frequently irrecoverable once settled. A critical new dependency
becomes a liability, since suspending the integration means losing the capability the project
was built for. Confidentiality loss, since payment integrations carry customer and transaction
data by definition. Contagion in both directions, since Northbridge may be the route to the
other partner or to other banks, escalating a local incident into an industry one. Regulators
treat third party risk as a named obligation, so going live without an assessment process
converts an existing audit finding into a breach of process. With no logging and no contractual
right to audit, establishing whether fraud originated at the partner or at Northbridge may be
impossible, which determines who bears the loss.

**Risk: Likelihood 3, Impact 5, score 15, Critical at the low end.** Likelihood is 3, the lowest
in this report, and deliberately so. The integration is not yet live, so there is currently no
connection to abuse, and exploitation requires compromising a payment processor which is likely
more security mature than Northbridge and carries its own regulatory obligations. This is not
inflated to 4 or 5 simply because supply chain attacks are topical. Impact is 5 without
qualification, since it is the only threat with a direct cash loss mechanism, it compromises an
asset about to become a critical dependency, and it carries a contagion dimension no other
threat has.

The reason this still lands critical despite the lowest likelihood is timing, and timing is the
whole point. Every other threat could be remediated after an incident. This one has a fixed
deadline. On the day the integration goes live the likelihood moves to at least 4, and the cost
of retrofitting a partner zone, mutual TLS, input validation and an assessment process rises
sharply, because by then the partners have built against whatever Northbridge shipped. The brief
states the CTO commissioned this review before the integration proceeds. T6 is the threat that
justifies that sequencing.

## 3.4 Member 4: human, physical, resilience

### T7. Social engineering against staff credentials

**Asset.** Staff credentials, and through them core banking, internal email and the remote
access VPN. A secondary asset is the shared VPN password specifically, a single phrase which if
disclosed by any one holder grants network access, making it an unusually efficient target.

**Vulnerability.** Organisational, and stated plainly in the brief. No security awareness
training at all, with the brief noting the recent attempt was stopped by one individual's
instinct. No incident response process, so the reported attempt produced no escalation, no
warning to other staff, and no trigger to rotate the credential being sought. No policy stating
that IT will never ask for a password, and no verified callback procedure. Password sharing is
already normalised among branch staff, which is the detail that makes vishing far more likely to
succeed here. An organisation where colleagues routinely share passwords has trained its staff
that disclosing a password to someone who sounds legitimate is a normal act. No MFA anywhere, so
a disclosed password is sufficient on its own.

**Threat.** A social engineer conducting voice phishing, impersonating the IT Helpdesk. Not
hypothetical, the brief records an attempt that has already happened. A single documented attempt
also implies the caller may have been reconnaissance for a campaign, and that others may have
been called and either complied or not reported it, since no process made reporting routine.

**Exploit.** Human, and the brief describes the exact pretext. Authority, claiming to be
internal IT. Urgency, a supposed system issue which compresses decision time. Plausibility,
since with no central authentication, password problems on individual systems are a genuine
frequent occurrence, so the pretext matches the victim's lived experience. No safe verification
path, since with no policy and no published callback number the socially easier option is to
comply. The follow on exploit is credential reuse, so one successful call yields more than one
access.

**Attack.** The attacker builds a staff list from public sources, straightforward for a 450 staff
bank with seven public sites, then calls a target, likely a branch employee less likely to know
the IT team personally. The documented incident ended with the employee growing suspicious partway
through, but partway through means the pretext worked initially, and the attacker needs one
success out of several hundred attempts. The credential is tested against the portal, webmail and
the VPN, with no MFA anywhere, then reused elsewhere with no central lockout correlating
attempts.

**Impact.** The most important property is that T7 is the entry condition for the report's other
critical threats. A disclosed password feeds T1, T2 and T3. Its direct impact is modest, one
account, but its enabling impact is the maximum available, because there is no second factor, no
segmentation and no detection to absorb the consequences. Directly, it yields whatever that
employee could reach, including customer data for a branch role. Fraud is attributed to the
employee rather than the attacker, a serious secondary harm to an innocent person. Unlike a
software vulnerability this cannot be patched, so without training the organisation is equally
vulnerable next week.

**Risk: Likelihood 5, Impact 4, score 20, Critical.** Likelihood is maximum, and this needs
careful justification because the documented attempt failed. It failed because of one
individual's instinct, which is not a control, it is a coincidence, and it will not recur
reliably across 450 staff. Four Northbridge specific factors put this at 5. The attack has
already been attempted, so the actor and pretext are confirmed. There is no training, so no
baseline resistance. There is no incident response process, so the one reported attempt produced
no organisational learning. Decisively, password sharing is already common, so disclosing a
password to someone who sounds legitimate is already normal behaviour. The attacker does not
need to overcome a cultural norm, the norm is on their side. Impact is 4 rather than 5 because
the immediate consequence is one account at one privilege level, and scoring 5 would double count
impact already assessed in T1, T2 and T3. That said, 4 understates its strategic significance.
T7 is the cheapest, most reliable entry point in the environment, requiring no software exploit,
no physical access and no technical skill. In remediation priority it belongs above several
higher scoring threats, because removing it removes the input to three of them.

### T8. Physical compromise of the server room, and unrecoverable outage

**Asset.** The physical infrastructure hosting core banking and the customer database, the backup
media, and branch network equipment. This is the asset Northbridge has historically protected
best, since its investment went almost entirely into physical measures, which makes the server
room's exclusion the sharpest irony in the scenario.

**Vulnerability.** The brief is unusually specific, and every detail is a separate gap. The
server room is secured by a single shared key, which is the physical equivalent of the shared VPN
account, it cannot be revoked for one holder, cannot be audited, and nobody knows how many
copies exist. There is no camera coverage of the room at all, so an after hours entry would leave
no record of who or when, and no visible deterrent. Note that the bank has cameras, in branches,
for cash, but not on its most critical asset. No site has signage, badge checking or cameras at
entry points. Visitor sign ins are inconsistently enforced, so an unaccompanied stranger is
unremarkable. Branch cabinets were found unlocked in at least two locations. Finally, backups
exist but have never been tested, and no disaster recovery plan exists, which converts a physical
intrusion from an expensive incident into a potentially unrecoverable one.

**Threat.** An opportunistic intruder, which the brief implicitly describes by noting there is no
visible deterrent. A malicious insider or former employee holding a copy of the shared key, which
cannot be established since the key is shared. A targeted intruder using a pretext such as a
maintenance engineer, which needs little sophistication against unenforced sign in and no badge
checking. A malicious visitor at a branch exploiting the unlocked cabinets.

**Exploit.** Unaudited and undeterred physical access, which defeats controls logical access
cannot touch. Console access, since a directly attached keyboard bypasses network access
controls, and password recovery procedures are documented vendor processes requiring only a
reboot. Direct storage access, since drives can be removed, and with no data classification
policy there is no reason to believe the database is encrypted at rest. Backup media in the same
room can be taken or destroyed, which is the step that removes recovery. An implant placed inside
the server room provides persistent access on a flat network with no IDS to notice it. At
branches, the unlocked cabinet gives switch console access and an open port in a trusted VLAN,
which is the physical entry route for T4.

**Attack, chain A, data theft.** The intruder enters outside hours using a copy of the shared key,
or during hours via unenforced sign in. No signage deterred them, no badge check intercepted them,
no camera recorded them. Drives are removed, or console access is used to copy data, and backup
media is taken too. No record exists that anyone was there.

**Attack, chain B, destruction and failed recovery.** The intruder enters as above and destroys
the servers and storage, achievable in minutes and requiring no technical skill. Backup media in
the same room is destroyed or taken, so one visit defeats both. Core banking, the portal and the
mobile app stop. Recovery is attempted for the first time ever, so Northbridge discovers whether
its backups work during the worst week in its history, with no documented plan, determining the
sequence and the responsible people live. If the offsite copy is incomplete, corrupt, or was in
the same room, the result is permanent loss of a licensed bank's customer ledger.

**Impact.** Availability loss is potentially permanent. This is the only threat here whose worst
case is irrecoverable. Ransomware at least offers the attacker an incentive to decrypt, physical
destruction offers nothing, and untested backups mean no verified alternative exists.
Confidentiality loss, since removed drives or stolen media, most likely unencrypted, deliver the
complete database with no network trace. Forensic and accountability failure is total, since a
shared key with unknown copy count and no cameras means Northbridge cannot determine who entered,
when, or even that anyone did. Three regulatory findings stack: inadequate physical control over
a regulated data environment, no tested backups, and no documented disaster recovery plan. The
irony is itself a finding, since Northbridge demonstrably knows how to do physical security, so
choosing to protect cash and not the server room reads as negligence rather than oversight.

**Risk: Likelihood 3, Impact 5, score 15, Critical at the low end.** Likelihood is 3, and this
was the most debated score. Three arguments push it up: every barrier is confirmed absent, the
key holder population is unknown and unbounded, and the attack needs no technical skill. One
argument holds it down and is judged decisive, this attack requires the attacker to physically
attend a Northbridge building. That bounds the attacker population to people in the region
willing to accept personal physical risk, a far smaller and more deterred population than the
internet. Northbridge also has existing alarm systems which, while not covering the server room,
raise the general difficulty of after hours entry. It is scored 3 rather than 4 to stay honest
about that, rather than inflating it to match the impact. Impact is 5 without qualification, and
arguably beyond the top of the scale. Every other critical threat has a recovery path, even a
painful one. This one, in chain B, can end with the primary systems and the only copies destroyed
in a single visit, at an organisation with no tested restoration and no documented plan.

The reason this stays critical on the lowest likelihood in the report is the dependency between
the two halves. The physical gap and the untested backup gap are individually serious and jointly
existential. If Northbridge did nothing else but put auditable access control and a camera on the
server room, and prove once that it can restore the database from an offline copy, this threat's
impact falls from 5 to 3 and it leaves the critical band entirely. Those are also two of the
cheapest controls in the plan. That cost to risk ratio is why the plan treats restoration testing
as a control in its own right, rather than as an assumed property of the existing backup.
