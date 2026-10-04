# 8. Group Technology Evaluation and Selection

The sixteen individual proposals are in Appendix A. This section is the group's comparative
evaluation of them and the final recommendation in each area.

## 8.1 Method

Each member completed all four proposals independently and submitted them before the group met,
as the brief requires. For each area separately, the group then agreed the evaluation criteria
before re reading the proposals, so the criteria could not be reverse engineered from a preferred
answer, scored all four head to head, selected one, and recorded for each rejected proposal the
specific reason it lost.

Scoring is 1 to 5 per criterion, higher is better. The scores force direct comparison, and the
reasoning below each table is what actually decided it.

| Area | Adopted | From | Runner up |
|---|---|---|---|
| VPN | Cisco Secure Client IKEv2/IPsec on a Secure Firewall pair | Member 1 | Member 2, FortiGate |
| AAA | Cisco ISE, RADIUS and TACACS+ | Member 1 | Member 4, Aruba ClearPass |
| Network architecture | Dual firewall DMZ sandwich with partner extranet and out of band management | Member 3 | Member 1, single vendor three tier |
| IDS/IPS | Inline IPS plus flow based detection from existing switch NetFlow | Member 4 | Member 3, Suricata, Zeek and SIEM |

Member 2's proposals were not adopted in any area. That is recorded plainly rather than softened,
and Section 8.6 sets out what their submissions did change.

## 8.2 VPN solution

| Criterion | M1 | M2 | M3 | M4 |
|---|---|---|---|---|
| Eliminates the shared credential structurally | 5 | 4 | 5 | 5 |
| Endpoint posture assessment for contractor devices | 5 | 4 | 1 | 5 |
| Integrates with the chosen AAA service | 5 | 4 | 3 | 3 |
| Operable by a team with no firewall experience | 4 | 4 | 3 | 5 |
| Resilience to the absent patch process | 2 | 2 | 5 | 5 |
| Avoids a new unassessed third party dependency | 5 | 5 | 5 | 1 |
| Commercial support and audit evidence | 5 | 5 | 2 | 4 |
| Deliverable within Phase 1 | 4 | 5 | 4 | 3 |
| **Total of 40** | **35** | 33 | 28 | 31 |

**Adopted: Member 1.** It is the only proposal scoring at or near the top on both criteria the
group judged decisive, posture assessment of unmanaged devices and integration with the central
AAA service, without introducing a new problem elsewhere. Posture matters because two external IT
contractors need regular access on devices Northbridge does not own and has never assessed. AAA
integration matters because T1 and T2 share one root cause, and a VPN keeping its own account
store recreates that problem on the most exposed device in the estate.

**Member 2 lost narrowly, on vendor coherence rather than capability.** It scored equal or better
on deliverability and support, and its central argument, that one bundled licence frees budget
for controls with no product attached, was accepted as correct and shaped the phasing. What it
lost on is that Member 2's own proposal acknowledged that splitting the VPN from a Cisco
switching estate means two management planes for a team that has never run one. With the AAA and
IPS decisions both Cisco, one vendor relationship buys more risk reduction for a team of this
maturity than the licence saving does. Had the AAA decision gone otherwise, this would have won.

**Member 3 lost on posture assessment, which Member 3 identified themselves.** They stated plainly
that WireGuard has no posture capability, and that this is a real loss given personal devices and
unassessed contractor machines. The group agreed and weighted it higher than Member 3 did. Their
strongest argument, that giving an organisation with no patch process an internet facing
appliance whose safety depends on patching promptly is the wrong risk, scored 5 where Member 1
scored 2. It did not carry the decision, because the correct response is to fix the patch process
through Control 10 rather than choose an architecture around its absence, and because the absence
of commercial support on the remote access path is difficult to defend to a regulator. One
element was adopted: the observation that a key file cannot be read out over the telephone the way
a password can is why Control 4 requires per user certificates in addition to a password.

**Member 4 lost on the third party dependency, which Member 4 also identified themselves.** It
scored highest on operability and patch process resilience, and its central argument, that placing
a user on the network is meaningless protection while the network is flat, is correct about
Northbridge today. Two things defeated it. It is self defeating once Control 5 exists, since
ZTNA's advantage shrinks as segmentation improves, and segmentation is Phase 1. Decisively, it
would route a regulated bank's authentication through a cloud broker Northbridge has no process
to assess, which is exactly the unassessed transitive trust T6 rates critical. ZTNA is retained as
a Phase 3 item, since the group accepted the destination and disagreed only about sequence.

## 8.3 AAA solution

| Criterion | M1 | M2 | M3 | M4 |
|---|---|---|---|---|
| TACACS+ per command authorisation and accounting | 5 | 1 | 4 | 5 |
| Device profiling, builds the missing asset inventory | 4 | 2 | 1 | 5 |
| Enables the 802.1X dynamic segmentation Controls 5 and 6 need | 5 | 3 | 3 | 4 |
| Answer for unmanaged personal devices | 4 | 5 | 1 | 4 |
| Time to deliver MFA on remote access | 3 | 5 | 3 | 3 |
| Availability risk given untested backups | 3 | 4 | 5 | 3 |
| Commercial support for a regulated institution | 5 | 5 | 1 | 5 |
| Avoids pre committing the other three decisions | 2 | 4 | 5 | 4 |
| Total cost of ownership | 2 | 5 | 4 | 3 |
| **Total of 45** | 33 | 34 | 27 | **36** |

**Adopted: Member 1, Cisco ISE.** This is the one area where the group selected a proposal that
did not score highest, and the reasoning needs stating because it is a judgement rather than an
arithmetic result.

Two criteria were re weighted after scoring, by agreement. First, "avoids pre committing the
other three decisions" turned out to be a criterion about the order of the group's own meeting
rather than about Northbridge. By the time the AAA decision was taken, a Cisco based VPN had been
selected on its own merits and the architecture discussion was heading toward a design the AAA
platform does not constrain. Member 4's lock in concern was legitimate when written and had
largely dissolved by the time of the decision. Second, 802.1X integration was re weighted upward,
because the two highest rated threats are defeated by identity and segmentation acting together,
with 802.1X assigning a device to a zone based on who it is rather than which socket it is
plugged into.

ISE therefore wins on the combination of TACACS+ accounting, which closes T2's accountability gap
and is the clearest audit finding in the brief, and tight 802.1X integration with the segmentation
programme.

**Member 4 lost the closest contest in the evaluation, on a criterion that had decayed.** On
capability ClearPass is ISE's equal, and on profiling, which Member 4 weighted most, it is better,
scoring 5 against 4. Member 4's argument that the first thing Northbridge needs is not enforcement
but to find out what is on its network was accepted, and it changed the plan. Control 1 now
requires a monitor mode discovery period before any 802.1X enforcement, and Control 6's rollout
sits in Phase 3 behind that discovery, which is Member 4's sequencing applied to Member 1's
platform. ClearPass lost its main differentiator, vendor neutrality, once the VPN and IPS
decisions had both gone to Cisco, at which point the benefit is theoretical and the looser fabric
integration is real.

**Member 2 lost on TACACS+, decisively and on the criterion that matters most here.** It scored
highest on cost and time to MFA, and best on BYOD, since Conditional Access conditions access on
the state of a device the organisation does not own, which is a better answer for the brief's work
from home gap than a posture engine. Member 2 was honest that their compensating control for
device administration, RADIUS plus configuration change logging, captures that a configuration
changed but not who typed which command, and can be defeated by an administrator who disables
logging first. The group treated that as disqualifying, since T2's central finding is the
inability to attribute a privileged action to an individual. Two of Member 2's arguments were
adopted: Control 2 was split out so MFA can be delivered in Phase 1 without waiting for the full
AAA programme, and Control 3 requires just in time elevation rather than standing privilege.

**Member 3 lost on support and operational burden.** It scored top on availability risk, and that
argument was the sharpest in the evaluation, that making one appliance pair the gate on all
network access, at an organisation whose backups have never been restored, concentrates
availability risk badly. The group accepted it rather than rejecting it. Control 1 explicitly
requires a redundant pair, a documented and tested rebuild procedure, and local fallback
credentials on every device, which is why Configuration 1 was built with `group tacacs+ local` and
includes a fallback test. The proposal itself lost because four separately operated open source
components require in house expertise a new team does not have, and because a regulator examining
the central authentication control of a deposit taking institution will expect commercial support
and a vendor accountability chain. Member 3 named this counter argument themselves and judged it
non binding, the group judged it binding.

## 8.4 Secure network architecture

| Criterion | M1 | M2 | M3 | M4 |
|---|---|---|---|---|
| Satisfies the multiple firewalls requirement literally | 5 | 2 | 5 | 5 |
| Internal boundary survives compromise of the external one | 4 | 2 | 5 | 4 |
| Resists a single vendor critical vulnerability | 2 | 1 | 5 | 2 |
| Contains the branch to core ransomware path, T3 | 4 | 4 | 4 | 5 |
| Isolates the compromised public web tier, T5 | 4 | 3 | 5 | 4 |
| Terminates partner trust safely before go live, T6 | 4 | 3 | 5 | 4 |
| Protects the management plane from the data plane | 4 | 2 | 5 | 4 |
| Operable by a team with no firewall experience | 4 | 5 | 2 | 1 |
| Implementable within Phase 1 | 4 | 5 | 3 | 1 |
| **Total of 45** | 35 | 27 | **39** | 30 |

**Adopted: Member 3, with one modification.** The DMZ sandwich structure, the partner extranet
plus integration broker separation, and the out of band management network are adopted in full.
The heterogeneous vendor requirement is adopted as a preference rather than a constraint, to be
decided at procurement, since the group accepted the correlated failure argument but weighed it
against Member 3's own admission that it doubles the operational skill requirement.

Member 3 won on the two criteria tracing most directly to the brief's emphasis. The integration
broker, a validating intermediary that is the only system permitted to speak to core banking so
the partners never address the database, is a design element no other proposal contained, and it
is the structural answer to the brief's statement that the integration extends trust outside
Northbridge with no assessment process in place. The physically separate out of band management
network is the other, being the only proposal that removes all paths from the user data plane to a
device's management interface.

Member 3's own mitigation for the complexity it introduces was also adopted, that Control 5
requires the internal tier to carry a deliberately small and static rule set, so the device
needing most care needs least change.

**Member 1 lost on correlated failure, and only on that.** It is the runner up within four points,
and its zone model is excellent, so the group adopted Member 1's zone naming and the requirement
that every allow rule carries an owner and a review date. It lost on the criterion Member 3 built
their proposal around. Two tiers of the same vendor fail together on one critical vulnerability,
and Northbridge's risk is unusually concentrated, with a single customer database in a single data
centre reachable from the internet. When one boundary carries that much weight, the device most
likely to have an exploited vulnerability, the internet facing one, is the one you least want
sharing a codebase with the device protecting the database. Member 1 scored 2 on that criterion
against Member 3's 5, which is the whole margin.

**Member 2 lost on the brief's literal requirement, which Member 2 anticipated.** They stated that
reading an HA cluster plus a distinct second enforcement layer as satisfying "multiple firewalls"
was the weakest point of their proposal, and the group so judged it. Beyond compliance, it scored
lowest on the criterion mattering most for the brief's lead scenario, since the ransomware path
starts inside the perimeter and a collapsed design puts the internal user LAN and core banking on
two legs of the same device, so the one policy engine that must stop internal lateral movement is
also the device exposed to the internet. Member 2's operational risk argument was nonetheless the
most important contribution to this area and was adopted in the form described above. Member 2's
per branch VLAN sets were also adopted into Control 5, since containing branches from each other
rather than merely from the data centre is what breaks the brief's documented attack pattern, and
no other proposal specified it.

**Member 4 lost on sequencing, which Member 4 identified themselves.** It scored highest on
containing the branch to core path, and its central observation is correct and uncomfortable, that
zone based segmentation filters traffic between zones and does nothing to traffic within a zone,
so once core banking is a zone an attacker reaching any host in it can reach them all, and T8's
intruder starts inside that zone. The group accepted the gap is real. It lost because micro
segmentation requires an accurate map of which system talks to which on which port, and
Northbridge has no asset inventory, no documented architecture and a decade of organic growth, so
getting the map wrong breaks core banking in production. Member 4's own judgement, that this is the
right Phase 3 and the wrong Phase 1, was accepted. The east west gap is now named explicitly in
the residual risk table, which is what Member 4 asked for.

## 8.5 IDS/IPS solution

| Criterion | M1 | M2 | M3 | M4 |
|---|---|---|---|---|
| Prevents rather than merely detects at zone boundaries | 5 | 3 | 5 | 5 |
| East west and intra zone visibility, T3, T7, T8 | 1 | 2 | 3 | 5 |
| Detects an authenticated attacker using valid credentials | 1 | 1 | 3 | 5 |
| Branch coverage without new hardware at six sites | 3 | 2 | 2 | 5 |
| Works on day one with no security operations analyst | 5 | 2 | 3 | 4 |
| Produces evidence answering what the breach scope was | 2 | 2 | 5 | 4 |
| Nothing new to patch given the absent patch process | 4 | 1 | 1 | 5 |
| Commercial support and tuning | 5 | 3 | 1 | 5 |
| Total cost of ownership | 2 | 5 | 4 | 3 |
| **Total of 45** | 28 | 21 | 27 | **41** |

**Adopted: Member 4**, the clearest margin in the evaluation. It is the only proposal covering
both halves of Northbridge's detection problem, and the group concluded the second half is the
larger one.

The first half is known exploits crossing a boundary, which an inline signature IPS handles and
three of the four proposals handle equivalently. The second half is an attacker already inside,
using valid credentials and legitimate protocols, which no signature engine detects because there
is no signature for the statement that Alice's account is behaving unlike Alice. Of the eight
threats modelled, that second category covers T1, T2, T7 and T8 outright and most of T3's
propagation phase, because Northbridge's weaknesses are overwhelmingly credential and access
weaknesses rather than software vulnerabilities. Flow based behavioural detection is the only
proposed mechanism that sees it.

The decisive practical argument is the branch one. Northbridge has six branches with no security
staff, and the brief's lead ransomware scenario starts at a branch workstation. NetFlow export is
a configuration line on switches Northbridge already owns, so visibility exists at every branch on
day one, with no appliance to install, manage or patch, at an organisation the brief says has no
patch management process.

**Member 1 lost on intra zone blindness.** It scored top on day one operability, a real advantage
for a team with no analyst, and its 30 day burn in before enabling blocking was adopted verbatim
into Control 7 because it is the right way to avoid taking the banking portal offline with a false
positive. It lost because an inline IPS is structurally blind to traffic that does not cross the
device, scoring 1 on east west visibility and 1 on detecting an authenticated attacker, against
Member 4's 5 on both. Member 1's inline IPS component is the first half of the adopted design, so
this proposal was not so much rejected as found incomplete.

**Member 2 lost on being detection only where prevention was needed, and conceded the point in
advance.** Member 2 wrote that a detection only internal sensor does nothing without someone
reading it, that Northbridge has no incident response process and no 24 hour capability, and that
an internal alert at 2 a.m. may sit unread until morning, judging that acceptable because the
ransomware staging phase runs over days. The group rejected that judgement on the strength of
Member 2's own threat model, which rates T3 at likelihood 5 and quotes the brief's phrase "spread
rapidly". The plan cannot rate a threat at maximum likelihood on the basis that it moves fast and
then rely on a morning shift analyst to catch it. Two further problems: a SPAN design needs an
appliance, a SPAN session and a management path at every site, which is seven unpatched appliances
at an organisation with no patch process, and its branch coverage argument, that branch traffic is
visible at the head office aggregation uplink, covers branch to core traffic but not branch
internal lateral movement, which is where T3 begins.

**Member 3 lost on operational burden, but contributed the most valuable idea in this area.** It
scored top equal on prevention and highest on the criterion of producing evidence answering what
the breach scope was, and the argument for it was persuasive, that Northbridge has no centralised
logging at all, so if a breach is discovered next year it has no way to establish when it started
or what left, and that is the question a regulator and the payment partners will both ask, which
an alert feed cannot answer. The proposal lost because Suricata, Zeek and a self built stack
require deployment, tuning and operation by a brand new team with no analyst, scoring 1 on
commercial support and 1 on nothing new to patch. Its central insight was adopted, and is why
Control 8 exists as a first class control with its own number, why the SIEM is specified as
ingesting flow records and protocol metadata rather than only alerts, and why Control 8 maps to
all eight threats. Member 3 was right that the IDS/IPS decision is the natural moment to fix
logging, the group simply chose to fix it with a separate numbered control.

## 8.6 What Member 2's proposals changed

Member 2 did not win any area, and the group records what their submissions actually changed,
because a reader comparing the outcome table against the appendices would otherwise conclude their
work had no effect.

Member 2's overall stance, that Northbridge's board approves spending it can picture, that a
programme needing a large capital approval before anything improves is a programme that stalls,
and that budget should be weighed across four controls rather than concentrated in one, is the
reasoning behind the three phase implementation plan, and behind placing Controls 16 and 17 first
on the explicit grounds that they are the cheapest in the plan and remove T8 from the critical
band on their own.

Three specific adoptions. Control 2 exists as a separate control from Control 1 because of Member
2's argument that Northbridge needs MFA in weeks rather than after a NAC programme, since closing
T1 two quarters earlier is worth more than closing T2's accountability gap two quarters sooner
than otherwise. Control 5 requires per branch VLAN sets, from Member 2's architecture proposal,
and no other member specified branch from branch containment. Control 3 requires just in time
elevation rather than standing privilege, from Member 2's privileged identity management proposal.

Member 2's proposals lost consistently on one axis. Each optimised for cost and speed at the
expense of a capability the group judged non negotiable, TACACS+ accounting, multiple firewalls,
and inline internal prevention. That is a coherent pattern rather than four unrelated misses, and
it reflects a defensible position that was weighed and overruled, not an absence of analysis.
