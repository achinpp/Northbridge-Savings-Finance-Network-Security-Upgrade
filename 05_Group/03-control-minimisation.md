# Control Minimisation Justification (Group)

*Written as prose, as the brief requires. No tables are used in this section.*

---

## The design goal and how we approached it

The brief sets efficiency as an explicit design goal: the plan "should minimize the total
number of distinct controls used by preferring controls that address multiple threats at once
over a large number of narrow, single-purpose ones". We took that seriously as a constraint on
the design rather than as a presentational preference, and it changed the plan materially.

Our first pass produced **twenty-six controls**. It was built the obvious way — each member
brought the controls their own two threats needed, and we collected them. The result was
inefficient in a specific and recognisable way: because four people had independently analysed
eight threats in the same organisation, the same underlying weakness appeared under several
different names. Member 1 had proposed abolishing the shared VPN account; Member 4 had proposed
abolishing the shared server-room key; Member 2 had proposed abolishing shared switch
passwords. These were three controls in the first draft. They are one control — *stop using
shared credentials* — and in the final plan they are Control 3 and Control 17 respectively,
because the first two are credentials and the third is a physical key.

We reduced twenty-six to **eighteen** over two passes. The rest of this write-up explains
which controls were deliberately chosen because they are broad, what the narrower alternatives
would have cost us in control count, and where we kept redundancy on purpose.

## Controls chosen specifically because they are broad

**Control 8 (centralised logging, SIEM, alerting and authenticated NTP) is the single most
efficient control in the plan.** It is the only control that maps to all eight threats. The
reason is structural rather than lucky: every one of the eight attack chains contains a step
whose success depends on nobody noticing, because the brief states Northbridge has no
centralised logging or audit trail anywhere. A control that supplies the missing observer
therefore touches every chain at once.

The narrow alternative was explicit in our first draft and we can price it exactly. We had
drafted *four* separate controls: central log collection, a SIEM correlation and alerting
capability, NTP time synchronisation, and infrastructure configuration-change logging. Keeping
them separate would have cost three extra controls for no analytical gain, because none of the
four is useful without the others. Log collection without correlation is a disk full of text
nobody reads. Correlation without synchronised time produces a pile of records rather than a
timeline, which is the point Member 4 argued in their Configuration 8 write-up and the reason
syslog and NTP were submitted as one configuration rather than two. We merged them and
required the dependency in the control's own definition.

**Control 5 (zoned architecture with two firewall tiers and default-deny) absorbed the largest
number of first-draft entries.** The first pass contained five separate controls that are all
the same control seen from five threat models: DMZ isolation for the public portal (from T5),
internal segmentation between users and core banking (from T3), branch-to-branch containment
(from T3), guest Wi-Fi isolation (from T4), and a partner extranet zone (from T6). Each member
had correctly identified that their threat needed a boundary; nobody had noticed that it was
the same boundary programme. Consolidating them cost nothing in coverage — the mapping table
shows Control 5 addressing T3, T4, T5, T6 and T8 — and removed four controls. It also improved
the plan's quality, because specifying the zones **once**, as a complete set, forced us to
decide how the zones relate to each other. Five separately authored segmentation controls would
almost certainly have contained contradictions about where guest Wi-Fi terminates.

**Control 6 (Layer 2 access hardening baseline) was chosen as a single control over six narrow
ones.** The first draft listed port security, DHCP snooping, Dynamic ARP Inspection, BPDU
guard, 802.1X, and unused-port hardening as separate entries — which is how the module's labs
teach them and how it is tempting to write them. Specifying them as one *baseline configuration
applied to every access switch at all seven sites* removed five controls. More importantly, it
reflects how the control is actually deployed and operated: nobody rolls out DHCP snooping to
seven sites as one project and Dynamic ARP Inspection as another, and as Member 3's
Configuration 6 shows, DAI does not even function without DHCP snooping's binding table. Two
features that cannot work apart are not two controls.

**Control 15 (the information security policy set) and Control 16 (incident response, disaster
recovery and tested backups) each replaced a cluster.** Control 15 absorbed six separately
drafted policies — data classification, acceptable use, credentials, BYOD and work-from-home,
third-party security, and physical security — into one board-approved, annually reviewed
document set, removing five controls. Control 16 absorbed four — the incident response plan,
the disaster recovery plan, the backup programme and restoration testing — removing three. In
both cases the merge is justified by how the work is actually done: policies are approved,
published and acknowledged as a set, and a disaster recovery plan whose backups have never been
restoration-tested is not a plan, which is exactly the finding the brief records about
Northbridge today.

**Control 7 (inline IPS plus flow-based behavioural detection) was kept as one control
despite being two technologies**, and this was the most debated merge. The argument for
splitting was that signature-based inline prevention and flow-based anomaly detection are
different products, bought separately, with different deployment models. The argument for
merging, which won, is that they are a single detection capability with two sensors: the IPS
covers north-south traffic crossing a boundary with known-exploit signatures, and the flow
analytics covers east-west traffic that never crosses a boundary, with behavioural baselines.
Northbridge needs both to have *detection coverage*, and specifying them separately would have
invited the organisation to buy one and defer the other — which, given the brief's description
of a board making its first IT security capital request, is a realistic risk. The merge also
let us absorb virtual patching, which had been a seventh draft control in its own right.

## What we rejected in favour of a broader control

Three narrow controls were considered seriously and deliberately dropped, rather than merged.

We considered a **dedicated "VPN account management" control** addressing the shared account
specifically, because it is the single worst finding in the brief and there is a presentational
argument for giving it its own number. We rejected it because it would be a control defined by
a symptom rather than a cause. Member 1's own threat modelling made this argument: T1 and T2
share one root cause, the absence of a central identity and accounting authority. A control
aimed at the VPN account alone would have left the same weakness in place on every switch,
router, server and application, each with its own local accounts. Controls 1, 3 and 4 fix the
cause, and the shared VPN account disappears as a consequence.

We considered a **separate "guest Wi-Fi security" control**, which is how most practitioner
checklists would list it. We rejected it because everything it would contain is already
Control 5 (guest terminates on the external firewall tier with no internal route) or Control 6
(client isolation, port security on the access-point port, DHCP snooping). A guest Wi-Fi
control would have been a cross-reference wearing a control number.

We considered **splitting backups out of Control 16 as a nineteenth control**, and this one is
worth recording because the incentive ran the other way. The Recovery row of the Function ×
Category table holds only Control 16, and a separate backup control would have populated that
row more convincingly to a reader. We decided that padding a table is not a reason to create a
control, and that the honest statement — that this plan has exactly one recovery control, and
that it is therefore load-bearing — is more useful to Northbridge than a cosmetically fuller
grid. We have instead flagged the thinness of that row explicitly in the table's closing note.

## Where we kept redundancy deliberately, and why

Minimisation is not the same as elimination, and three overlaps were kept on purpose.

**Controls 5 and 6 both address T4, and we kept both.** This is the clearest deliberate
redundancy in the plan. Control 5's segmentation stops a guest on the guest VLAN attacking a
staff workstation, because they are no longer in the same broadcast domain. It does nothing
against an attacker who is already *inside* the staff segment — and the brief makes that
realistic, recording branch network cabinets found unlocked in at least two locations and
visitor sign-in inconsistently enforced. Someone who patches a laptop into a staff port is
inside the segment, and segmentation has nothing left to say. Control 6 is what defeats that
attacker. The two controls look redundant on the mapping table and are not redundant in the
threat model, which is precisely the case where a mapping table misleads and the prose has to
carry the reasoning.

**Controls 2 and 14 both address T7, and we kept both** because they act on different terms of
the risk equation. Control 14's awareness training reduces the *likelihood* that a staff member
discloses a password. Control 2's MFA reduces the *impact* if they do, because a password alone
stops being sufficient. Neither substitutes for the other: training will never reach 100% of
450 staff reliably, and MFA does not stop an attacker who talks a user through approving the
second factor. We also kept both because of a timing argument Member 2 raised during the
technology evaluation — MFA can be delivered in weeks and training takes a year to change
behaviour, so in the interim MFA is doing the work alone, and after the interim training is
what reduces the number of MFA prompts an attacker gets to try.

**Controls 7 and 11 overlap most awkwardly, and this is the redundancy we are least
comfortable with.** Control 7's inline IPS inspects traffic to the DMZ with web and
database-protection signatures. Control 11's web application firewall inspects the same traffic
with web-application-specific rules. Both would block a straightforward SQL injection payload
against the online banking portal, so a reviewer could reasonably say Northbridge is paying
twice. We kept both for two reasons and we accept the cost. First, they fail differently: an
IPS matches known attack signatures, while a WAF understands the application's own expected
input structure and can block a novel payload that no signature covers. Second, and more
practically, Control 7's IPS is being procured as part of the firewall tiers in Phase 2 and
Control 11's WAF sits in the DMZ in front of the portal, so the overlap buys defence in depth
on the one asset the brief identifies as both the most critical and the most exposed — the
internet-facing portal into the customer database. If budget forced a cut, the WAF stays and
the IPS's web signature set is the thing we would narrow, because T5 is an application attack
and the WAF is the control shaped for it.

## A note on what minimisation cost us

One honest consequence of this exercise is that several of our eighteen controls are large.
Control 15 is six policies, Control 6 is a baseline containing six switch features, and
Control 16 is four distinct programmes of work. Expressed as projects rather than as controls,
the plan is bigger than eighteen items suggests, and a reader who mistakes control count for
implementation effort will under-estimate it. We judged this the right trade: the brief asks
for a minimal set of controls that each address multiple threats, and grouping work that is
genuinely delivered together is more honest than inflating the count to look granular. The
phasing section of the layered security plan exists to make the real sequence and effort
visible, because the control list alone does not.
