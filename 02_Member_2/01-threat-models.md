# Member 2 — Individual Threat Modelling

**Member:** [Member 2 — Full Name / IT Number]
**Allocated theme:** Network segmentation and Layer 2 security
**Threats modelled:** T3 (ransomware propagation across the flat network), T4 (guest Wi-Fi sharing the branch Layer 2 domain)

> This section is individually authored and individually assessed. The two threats below are
> my own work and remain attributable to me in the combined group plan.

## Risk rating method used

Risk = Likelihood × Impact, each scored 1–5, giving a 1–25 score. Bands: 1–4 Low, 5–9
Medium, 10–14 High, 15–25 Critical. Likelihood is assessed against Northbridge's current
state, with no compensating controls assumed.

---

## Threat Model T3 — Ransomware propagation from a branch workstation to the core banking database

### Asset

The **core banking application and customer database** in the head-office data centre, and
the **continuous branch-to-head-office connectivity** that the brief says the bank depends on
to keep core banking services available throughout the day. Availability is the asset under
threat here, more than confidentiality — a bank that cannot process transactions for a day
has a crisis even if no data leaves the building.

### Vulnerability

Three weaknesses stack, and the stacking is what makes this the brief's own worst case:

1. **No segmentation.** The brief states the network "has grown organically over more than a
   decade without a formal segmentation strategy", and that head office systems, branch
   systems, guest Wi-Fi and point-of-service support equipment "largely share the same flat
   network space".
2. **No patch management process**, with several branch systems "known informally to be
   running outdated software versions of both applications and operating systems".
3. **No IDS/IPS anywhere**, leaving the bank blind to reconnaissance or active compromise
   "until damage is already visible", and **no centralised logging** to notice it either.

Individually each is a common finding. Together they describe a network where an initial
foothold has unrestricted reach, a reliable way in, and no observer.

### Threat

A **ransomware operator or ransomware-as-a-service affiliate** targeting mid-sized financial
firms. This is not a speculative actor: the brief states a regional industry association
reported a sharp rise in ransomware incidents against mid-sized financial firms over the past
year, "several of which began with a single compromised branch workstation and spread rapidly
across an unsegmented network". The threat actor, the entry point and the propagation method
are all documented as active against Northbridge's exact peer group.

### Exploit

Entry is through the **unpatched branch workstation**:

- A phishing email with a malicious attachment or link reaches a branch user. There is no
  awareness training programme, so the probability of a click is whatever the untrained
  baseline is.
- The payload exploits a **known, already-patched-upstream vulnerability** in the outdated
  operating system or application on that workstation. This is the key point: the attacker
  needs no novel capability, because Northbridge has no patch process, so publicly documented
  exploits with public tooling remain live on its estate.

Propagation then exploits the **flat network** itself. The vulnerability being exploited at
this stage is architectural, not a software bug: file-sharing and remote-management protocols
that are safe within a trust boundary become a propagation fabric when there is no boundary.
Common mechanisms are SMB-based lateral movement, remote service creation over RPC, and reuse
of locally harvested credentials — and the credential reuse the brief describes among branch
staff means one harvested password is likely to work on several other machines.

### Attack

1. **Day 0 — foothold.** Branch workstation at Branch 3 is compromised. No alert is raised:
   no IDS/IPS exists and no central logging would show the anomaly.
2. **Day 0 to 2 — discovery.** The malware enumerates the flat address space. Because branch
   and head-office systems share it, discovery reaches head-office servers from a branch PC
   without crossing a single filtering device.
3. **Day 1 to 5 — credential harvesting and lateral movement.** Local administrator hashes
   and cached credentials are collected and replayed. The brief's documented password reuse
   across branch staff makes this unusually productive.
4. **Day 2 to 7 — privilege escalation and staging.** The operator reaches server
   infrastructure, identifies the core banking database and, critically, **locates and deletes
   or encrypts the backups**. This is standard modern ransomware practice and Northbridge is
   especially exposed: the brief says backups exist but have never been tested for
   restoration, which strongly implies they are online and reachable rather than offline or
   immutable.
5. **Day 7 — detonation.** Simultaneous encryption across branch endpoints, head-office
   servers and the core banking database. The online banking portal and mobile app fail with
   their back end.
6. **Aftermath.** Northbridge has **no documented disaster recovery or incident response
   plan**, so the response is improvised during the worst week in its history.

### Impact

- **Availability — the dominant impact.** Core banking, the customer portal and the mobile app
  stop. Seven sites and roughly 450 staff cannot serve customers. For a savings and finance
  provider, a multi-day outage is itself a solvency and liquidity event, not merely an IT
  problem.
- **Recovery is unbounded.** Backups have never been test-restored, so Northbridge genuinely
  does not know whether it can recover, or how long it would take. An untested backup is a
  hypothesis, not a control. If the backups were also reachable from the flat network, they
  are likely encrypted too.
- **Confidentiality.** Modern ransomware exfiltrates before encrypting, so this is
  simultaneously a customer-data breach with a published-leak threat attached.
- **Regulatory.** A licensed bank that cannot process transactions must notify its regulator,
  and the absence of any tested DR plan is a finding independent of the incident.
- **The payment processor integration.** Due to go live within two quarters. No partner
  completes a technical integration with a bank mid-ransomware-recovery, so the project — and
  whatever commercial commitments sit behind it — is lost or deferred.
- **Reputational.** The brief notes Northbridge's ability to operate depends on customer and
  regulator confidence. Branch-level deposit flight after a visible multi-day outage is a
  realistic consequence.

### Risk

**Likelihood 5 / Impact 5 → Score 25 → CRITICAL.**

Likelihood is the maximum, and specifically so rather than generically. The brief does not
merely leave the door open; it reports that this exact attack pattern — compromise of a single
branch workstation, rapid spread across an unsegmented network — has already been observed
"several" times against Northbridge's own peer group within the past year. Northbridge has
every precondition present at once: a reliable entry route (unpatched branch systems plus
untrained staff), unrestricted propagation (no segmentation), productive credential reuse, and
no detection to shorten the dwell time. There is no single control in place that this attack
chain would have to defeat.

Impact is the maximum because of the untested backups specifically. If Northbridge had a
tested, offline backup, I would score impact 4 — a bad outage with a known recovery path. It
does not, so the worst case is permanent loss of the core banking database of a financial
institution, which is an existential outcome rather than a severe one.

This threat is the reason I argued in the group discussion that segmentation should be
treated as the single highest-priority technical control, ahead of anything perimeter-facing:
the attack starts inside, so a perimeter control does not touch it.

---

## Threat Model T4 — Rogue DHCP and ARP spoofing man-in-the-middle from the guest Wi-Fi and point-of-service equipment

### Asset

**Staff credentials and in-session banking data at branch offices**, and the integrity of the
branch LAN path to head office. The brief lists staff credentials as an asset every employee
relies on, and the branch-to-head-office path as something core banking availability depends
on.

### Vulnerability

The specific vulnerability is that **guest Wi-Fi, branch systems and point-of-service support
equipment share the same Layer 2 broadcast domain** as staff machines. That has consequences
beyond general "flatness", because several Layer 2 protocols are trusting by design:

- **DHCP has no authentication.** Any host on the segment can answer a `DHCPDISCOVER`, and
  the client accepts whichever offer arrives first.
- **ARP has no authentication.** Any host can send unsolicited ARP replies and rewrite its
  neighbours' ARP caches.
- **Switch ports are untrusted-by-default in the wrong direction.** Without `switchport
  port-security`, any device plugged into any socket joins the segment; without **DHCP
  snooping** every port is treated as a legitimate DHCP server port; without **Dynamic ARP
  Inspection** every ARP reply is believed.

Compounding factors from the brief: **physical access to networking equipment in branch back
offices is uncontrolled, with cabinets left unlocked in at least two locations**, and
**visitor sign-ins are inconsistently enforced** with no badge-checking presence. So the
attacker does not even need the Wi-Fi — they can plug into a switch.

### Threat

- An **opportunistic intruder or malicious visitor** at a branch, who has walked in without a
  reliably enforced sign-in and found an unlocked network cabinet.
- A **guest Wi-Fi user** — any member of the public within range — who needs no physical
  access at all, only the guest password.
- A **compromised point-of-service support device**, which sits on the same segment and is
  maintained by someone other than Northbridge.

### Exploit

Two chained Layer 2 exploits, both achievable with standard, freely available tooling:

1. **Rogue DHCP server.** The attacker runs a DHCP service offering itself as the default
   gateway, usually with a shorter lease and faster response than the legitimate server.
   Branch workstations renewing a lease, or booting, accept it. All of their off-subnet
   traffic — including traffic bound for head office and the core banking application — is now
   routed through the attacker.
2. **ARP cache poisoning (Dynamic ARP Inspection absent).** For hosts that already hold a
   lease, the attacker gratuitously asserts the gateway's IP address with its own MAC address,
   and asserts the host's IP to the gateway. This inserts the attacker bidirectionally into
   the path without touching DHCP at all.

With the path captured, the attacker performs credential harvesting from any protocol not
end-to-end encrypted, and attempts TLS interception against the rest. TLS stripping or a
forged certificate produces a browser warning — but the brief states there is no security
awareness training programme, so the chance of a branch user clicking through a certificate
warning is materially higher than in a trained organisation. That is the detail that turns a
partially mitigated attack into a working one.

### Attack

1. Attacker gains the segment: guest Wi-Fi association, or an RJ45 patch into an unlocked
   branch cabinet during business hours while visitor sign-in goes unenforced.
2. Rogue DHCP server started; ARP poisoning run in parallel for already-leased hosts.
3. Branch workstation traffic flows through the attacker's host.
4. Harvest: plaintext protocol credentials, session cookies, internal hostnames and the
   address of the core banking application, plus any certificate-warning click-through that
   yields decrypted banking session content.
5. Pivot: harvested staff credentials are replayed against head-office systems. The flat
   network means no boundary stands between the branch segment and those systems, and no
   IDS/IPS observes the replay.
6. Persistence: the attacker leaves a small implant on the segment, or simply returns, since
   the cabinet is still unlocked and nothing recorded the first visit — the brief notes no
   camera coverage at entry points.

### Impact

- **Confidentiality of credentials and live banking sessions.** Captured staff credentials
  grant authenticated access to internal systems, which is a complete bypass of the perimeter.
- **Integrity of the branch-to-head-office path.** A man-in-the-middle can alter as well as
  read. Modification of transaction data in flight is the worst-case variant and the hardest
  for Northbridge to detect, since there is no centralised logging to compare against.
- **Availability.** The same position allows selective denial of service against the branch,
  and a misconfigured rogue DHCP scope can take a branch offline by accident.
- **It is an undetectable precursor.** This attack's realistic purpose is not itself but what
  it enables — it is the cheapest way to obtain the valid credentials that T2 and T3 then use.
- **Accountability.** With no port-level identity, no centralised logging and no camera
  coverage of branch entry points or cabinets, Northbridge would have no evidence that it
  happened, let alone who did it.
- **Regulatory.** An unauthenticated member of the public being able to reach the same Layer 2
  segment as systems that handle customer financial data is a straightforward audit failure,
  and one the payment processors' own vendor assessment would be expected to find.

### Risk

**Likelihood 4 / Impact 4 → Score 16 → CRITICAL (low end).**

Likelihood is 4, not 5. It is high because the attack needs no sophistication, the tooling is
public, and Northbridge has removed every obstacle at once: shared Layer 2 with guest Wi-Fi,
no DHCP snooping, no DAI, no port security, unlocked cabinets in at least two branches, and
unenforced visitor sign-in. It is not 5 because exploitation still requires either physical
presence at a branch or Wi-Fi proximity, which bounds the attacker population to people who
turn up — unlike T1 and T3, which are reachable from anywhere on the internet.

Impact is 4 rather than 5 because the attack by itself yields credentials and session data
rather than direct control of the core banking database; the maximum-impact outcomes come
from the follow-on use of what is captured. Scoring it 5 would double-count T2's and T3's
impact. Equally it is not lower than 4, because the credentials captured here are the ones
that make the critical threats work, and the integrity exposure on the branch-to-head-office
path is a direct hit on an asset the brief names explicitly.

My assessment is that T3 and T4 both argue for the same fix — moving Northbridge from one
trust space to many — and that the Layer 2 hardening baseline in the group plan is where T4
is actually defeated, because segmentation alone does not stop an attacker who is already
inside the segment with his victims.
