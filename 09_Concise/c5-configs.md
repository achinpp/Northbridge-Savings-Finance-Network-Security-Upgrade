# 7. Individual Network Hardening Configurations

Eight distinct configurations, two per member, at least one of each pair implementing a control
from the plan. All were built and verified on the topology in Section 9. Plain text scripts are
in Appendix B, and screenshot evidence follows each write up.

| # | Member | Configuration | Plan linked | Implements | Threats |
|---|---|---|---|---|---|
| 1 | 1 | AAA with TACACS+ and RADIUS | Yes | Controls 1, 3, 9 | T2, T1 |
| 2 | 1 | SSH and management plane hardening | Free choice | Control 9 | prerequisite to 1 |
| 3 | 2 | VLAN segmentation with inter VLAN ACLs | Yes | Controls 5, 6 | T3, T4 |
| 4 | 2 | Switchport port security | Free choice | Control 6 | T4 |
| 5 | 3 | Internet edge firewall, NAT and edge ACL | Yes | Controls 5, 18 | T5, T6 |
| 6 | 3 | DHCP snooping and Dynamic ARP Inspection | Free choice | Control 6 | T4 |
| 7 | 4 | NetFlow export | Yes | Control 7 | T3, T7, T8 |
| 8 | 4 | Centralised syslog and NTP | Free choice | Control 8 | all |

## 7.1 Member 1

### Configuration 1, AAA with TACACS+ and RADIUS, plan linked

**What it achieves.** It moves authentication, authorisation and accounting off the device and
onto a central server. Every administrator logs in as themselves rather than with a shared enable
password. The server, not the router, decides whether a login is allowed, so disabling a leaver
in one place disables them everywhere. Every login and privileged command produces an accounting
record, which is the audit trail Northbridge does not have. A local fallback account survives
loss of the server, so a management network outage does not lock the team out of its own routers.

**Plan linkage.** Implements Control 1, and contributes to Controls 3 and 9. It addresses T2
directly, whose central finding is that Northbridge cannot attribute a privileged action to an
individual. TACACS+ command accounting is the control that closes that gap. It also partly
addresses T1, since the same service is what the remote access VPN authenticates against.

**Key commands.**

```
username netadmin privilege 15 secret Fallb@ck-NB-2026
aaa new-model
tacacs-server host 10.10.99.10 key NBtac$2026
radius server NB-RAD
 address ipv4 10.10.99.10
 key NBrad$2026
aaa authentication login default group tacacs+ local
aaa authentication enable default group tacacs+ enable
```

The method order is the whole control. `group tacacs+ local` tries the central server first, and
falls back to the local database only if it does not answer. Reversing the order means the local
account always wins, so central AAA never applies. Omitting `local` entirely means an AAA outage
locks every administrator out of every router, recoverable only by password recovery at each
device. That fallback is also the design requirement the group adopted from Member 3's objection
in Section 4.1.

**Verification and findings.** `show aaa sessions` lists the active session by user name, and
`show aaa user all` reports `Authen: service=LOGIN type=ASCII method=TACACS`, which is the router
stating that the login was authenticated by TACACS+ rather than by the local database. A user
holding no local account on the router logged in over SSH, and with the server's switch port
shut, the local fallback admitted `netadmin`.

One finding is worth recording. **Fallback triggers on error, not on failure.** With the server
online, `netadmin` is refused even though it exists locally, because TACACS+ answers no, which is
a failure rather than an error. Only accounts held on the server can log in. This is the
desirable behaviour, since a local account that remained usable while the central authority was
actively rejecting a user would make central deprovisioning meaningless.

**Platform limitations.** `show tacacs`, `show radius statistics` and `show aaa servers` are not
implemented in Packet Tracer 8.2. The two commands above are used instead, and are arguably
better evidence, since `show tacacs` reports only socket counters while `method=TACACS` names the
path actually taken. The legacy one line `radius-server host` form is rejected, and the modern
named server form is required, which is correct syntax on current IOS regardless.

### Configuration 2, SSH and management plane hardening, free choice

**What it achieves and why it comes first.** Central AAA decides who may log in. It does nothing
about how the login travels. On a default Cisco device management is Telnet, so the username and
password cross the network in clear text, and on a flat network any host in the same broadcast
domain can read them. Enabling central AAA over Telnet would make the identity control worse than
useless, since it creates a single high value credential and then broadcasts it. This
configuration is therefore the prerequisite for Configuration 1, which is why Controls 9 and 1
are sequenced that way in Section 4.4.

It enforces SSHv2 only with Telnet refused, hardens password storage, times out idle sessions,
throttles brute force attempts, restricts management to the out of band subnet by access list,
and displays a legal banner.

**Key commands.**

```
ip domain-name northbridge.lk
enable secret NBenable-2026
service password-encryption
username netadmin privilege 15 secret Fallb@ck-NB-2026
crypto key generate rsa general-keys modulus 1024
ip ssh version 2
ip access-list standard MGMT-HOSTS
 permit 10.10.99.0 0.0.0.255
 deny any
login block-for 120 attempts 3 within 60
line vty 0 4
 login local
 transport input ssh
 access-class MGMT-HOSTS in
 exec-timeout 5 0
```

A modulus of 1024 or more is required for SSHv2, and 512 would cause `ip ssh version 2` to be
rejected. Production would use 2048. `transport input ssh` is the single most important line,
since the default is `all`, which permits Telnet.

**Verification.** `show ip ssh` reports version 2.0. SSH from the management subnet succeeds and
shows the banner. Telnet from the same authorised host is refused, which proves the protocol is
disabled rather than the host filtered. SSH from a staff subnet is refused with no password
prompt, and the `MGMT-HOSTS` deny counter moves from zero to a non zero value, which is the same
access list shown before and after refusing real traffic.

**Platform limitations.** The `log` keyword is rejected on standard access lists, so it was
omitted. Match counters increment regardless, which is what the evidence needs. On production IOS
`deny any log` would additionally raise a syslog message per hit, feeding Control 8.
`exec-timeout` was set to 5 minutes rather than 10, because running config omits settings equal
to the IOS default, so a 10 minute timeout cannot be evidenced. Five minutes is both visible and
a tighter control.

## 7.2 Member 2

### Configuration 3, VLAN segmentation with inter VLAN ACLs, plan linked

**What it achieves.** Two distinct things, both necessary. Segmentation moves guest Wi-Fi, staff
machines, the core banking servers, the DMZ and the management network into separate broadcast
domains, which alone stops every Layer 2 attack from crossing between them. Filtering by extended
access lists on the subinterfaces is what turns the router from a transit point into a policy
enforcement point, implementing default deny between zones with explicit named allowances.

The policy permits staff to reach core banking on two named ports to two named servers and
nothing else, denies guest everything internal, prevents the DMZ initiating anywhere, and
prevents core banking servers initiating back into the user LAN.

**Plan linkage.** Implements Control 5 and part of Control 6. It breaks T3's propagation step,
since T3 depends on a branch workstation enumerating and reaching head office servers with
nothing in between. Once staff and core banking are separate VLANs with an access list permitting
only the named application ports, the SMB, RPC, WMI and RDP that ransomware moves on are caught
by the implicit deny. The foothold still happens, the spread does not. It also addresses T4, since
separating guest into its own VLAN removes the shared broadcast domain the attack depends on.

**Key commands.**

```
interface GigabitEthernet0/1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30,40,99
 switchport trunk native vlan 999
 switchport nonegotiate

ip access-list extended STAFF-IN
 permit udp any any eq 53
 permit udp any any eq 67
 permit tcp 10.10.10.0 0.0.0.255 host 10.10.20.10 eq 1521
 permit tcp 10.10.10.0 0.0.0.255 host 10.10.20.11 eq 443
 deny   ip 10.10.10.0 0.0.0.255 10.10.20.0 0.0.0.255
 deny   ip 10.10.10.0 0.0.0.255 10.10.99.0 0.0.0.255
 permit ip 10.10.10.0 0.0.0.255 any
```

Moving the native VLAN off VLAN 1 closes VLAN hopping. The native VLAN's frames cross a trunk
untagged, and by default that is VLAN 1, which is also where every unconfigured port sits. An
attacker can craft a double tagged frame whose outer tag is stripped at the first switch,
delivering the inner tag into a VLAN they should not reach. Moving the native VLAN to one with no
ports and no gateway removes the landing zone. `switchport nonegotiate` disables DTP, so an
attacker's laptop cannot talk an access port into trunking.

Order is the control. Access lists are evaluated top down, first match wins, so the permits for
1521 and 443 sit above the blanket deny to the core banking subnet. Moving the deny up one line
would stop core banking working entirely. ICMP is deliberately not permitted anywhere, since ping
is a reconnaissance tool and the first step of T3's chain.

**Verification.** Staff reach the core banking application over HTTPS, so the business flow
survives segmentation. Staff pinging core banking and the management network both fail with
`Destination host unreachable` from the gateway, which is the router actively refusing rather
than a timeout, so the packet was received and a decision was made. Guest reaches neither core
banking nor staff. The access list counters afterwards show 60 matches on the permitted HTTPS
flow and 8 on the internet to internal deny, corresponding exactly to the tests run. Applied
inbound on the source subinterface, so a denied packet is dropped before the router routes it.

**Finding.** The unused port range originally covered FastEthernet0/13 to 0/24 only, leaving
`GigabitEthernet0/2` enabled in VLAN 1. Gigabit uplink ports are the ones most often missed and
the most valuable to an attacker, because they are trunk capable. It was added to the hardening.

### Configuration 4, switchport port security, free choice

**What it achieves.** VLAN segmentation decides which zone a port belongs to. It says nothing
about which device may use that port. Port security binds the two, so a staff port carries traffic
only for the MAC address that belongs there, and shuts itself down if a different device appears.

The real world problem is stated in the brief, that physical access to branch networking
equipment is uncontrolled with cabinets left unlocked in at least two locations, alongside
inconsistently enforced visitor sign ins and no camera coverage. In that environment an unlocked
cabinet is an open port in a trusted VLAN. Three attacks are defeated: a visitor's laptop in a
staff port, MAC flooding to force the switch to behave like a hub, and an unmanaged switch added
under a desk.

**Key commands.**

```
interface range FastEthernet0/1-4
 switchport port-security
 switchport port-security maximum 1
 switchport port-security mac-address sticky
 switchport port-security violation shutdown
 switchport port-security aging time 0
 spanning-tree portfast
 spanning-tree bpduguard enable

interface FastEthernet0/10
 switchport port-security maximum 20
 switchport port-security violation restrict
```

The violation action differs per port type, and that is the judgement being made. `shutdown` on
staff ports, since a violation there is almost certainly an attack or an unauthorised device.
`restrict` on the guest access point port, since a violation there is most likely the twenty
first guest phone associating, and err disabling the access point would be a self inflicted
outage. `aging time 0` means the sticky address never ages out, because an aging window is a
window for a new device to claim the port. BPDU guard is free extra hardening, since an access
port should never receive a spanning tree BPDU, and if one arrives something is pretending to be
a switch.

**Verification.** Sticky learning captures nothing until a device sends traffic, so the secure
address table and the running configuration entries populate only after the attached hosts
generate frames. With that done, the learned MAC appears written into the running configuration,
which proves sticky persisted the address rather than merely permitting it in memory. An
unauthorised PC connected in place of the authorised workstation puts the port into
`Secure-shutdown` with violation count 1, and records the offending MAC in `Last Source Address`,
which is forensic attribution. The port recovers to `Secure-up` after the authorised device is
restored.

Note that `maximum 1` and `violation shutdown` do not appear in the running configuration,
because both are IOS defaults and running config omits defaults. `show port-security` evidences
them explicitly.

## 7.3 Member 3

### Configuration 5, internet edge firewall, plan linked

**What was intended, and why this differs.** Proposal A3.3 and the adopted architecture specify a
stateful dual firewall DMZ sandwich, and the intended implementation was a Zone Based Policy
Firewall. Packet Tracer 8.2 on the ISR 2911 implements no stateful firewall of any kind,
established by direct test rather than assumed.

| Command | Result |
|---|---|
| `zone security INSIDE` | `% Invalid input detected`, caret on `zone` |
| `ip inspect name FW-DMZ http` | `% Invalid input detected`, caret on `inspect` |
| `permit tcp any any reflect SESSIONS` | `% Invalid input detected`, caret on `reflect` |
| `ip ?` | no `inspect` keyword in the parser |
| `license boot module c2900 technology-package securityk9` | accepted silently, but `show version` still reports `security / disable / None` after two reloads |

This configuration implements the same perimeter policy using the tools the platform provides,
static PAT for publishing and an extended access list for default deny inbound.

**What the substitution costs, stated precisely.** A zone firewall inspects a session and permits
its return traffic automatically. A static access list cannot, so return traffic must be permitted
by rule using the `established` keyword, which only checks whether the TCP ACK or RST flag is set.
An attacker who crafts a packet with ACK set passes that rule, whereas a stateful firewall would
reject it because no matching session exists. UDP and ICMP are worse, having no equivalent, so
their return traffic must be permitted by protocol and type. That gap is why the plan specifies
next generation firewalls at both tiers rather than router access lists.

**What it achieves.** It establishes an explicit enforced boundary where previously the brief
describes only the basic firewall functionality built into the internet facing router. Three
mechanisms matter in combination. A declared NAT boundary makes the perimeter a property of the
configuration rather than something implied by routing. Publishing by exception maps one public
socket to one internal socket, so the portal becomes the only system with any inbound path, on
one port, and every other host is unreachable by construction, since no translation exists for
them. Default deny inbound permits the published service and return traffic, then explicitly
denies internet to internal and everything else.

Outbound translation deliberately excludes VLAN 20, since the core banking servers have no
business initiating connections to the internet.

**Key commands.**

```
ip nat inside source static tcp 10.10.30.10 443 203.0.113.2 443
ip nat inside source list NAT-ALLOWED interface GigabitEthernet0/1 overload

ip access-list extended EDGE-IN
 permit tcp any host 203.0.113.2 eq 443
 permit tcp any any established
 permit udp any eq 53 any
 permit icmp any any echo-reply
 permit icmp any any unreachable
 deny   ip any 10.10.0.0 0.0.255.255
 deny   ip any any
```

The explicit internet to internal deny is written separately, even though the final deny would
catch it, because the implicit deny has no visible match counter. Writing it as its own line
creates a countable rule, so it can be shown refusing real traffic.

**Plan linkage.** Implements Control 5 and the technical half of Control 18. For T5 it does not
fix the injectable parameter, only code remediation and a WAF do that, which is Control 11. What
it fixes is the blast radius, since the portal is published on one socket and a fully compromised
web server has no inbound path to pivot through. For T6 the same structure gives the partner
integration a controlled place to terminate.

**Verification and a finding.** The portal loads from an internet host on its public address, and
`show ip nat translations` shows the live session carrying traffic. Internet hosts are denied
access to internal staff and core banking, and the `EDGE-IN` counters afterwards show 60 matches
on the published HTTPS permit and 8 on the internet to internal deny, matching the tests exactly.

Publishing the portal exposed a real defect in the stateless design, found in testing rather than
predicted. Member 2's `DMZ-IN` list ends in `deny ip any any` to enforce that the DMZ may not
initiate outbound. Once the portal was published, that rule also dropped the portal's replies to
internet clients, and the browser showed Request Timeout even though `EDGE-IN` and the static PAT
were both correct. A static access list cannot distinguish a reply from an initiation. The fix
was `permit tcp host 10.10.30.10 any established` above the denies, which lets a SYN-ACK through
while a fresh SYN from the portal still fails, so the compromised portal calling home remains
blocked. A zone firewall would have needed no such rule, since the inbound session would already
be in its state table. This is the substitution's cost demonstrated rather than asserted.

**Division of labour.** Both this and Configuration 3 use extended access lists. Member 2's
filters internal zone to zone traffic on the router subinterfaces. This one filters traffic
crossing the internet perimeter on the WAN interface, and adds address translation. Different
interface, different threat direction, different mechanism.

### Configuration 6, DHCP snooping and Dynamic ARP Inspection, free choice

**What it achieves.** DHCP and ARP are both unauthenticated by design, and on a default switch
both assertions are believed. DHCP snooping divides ports into trusted and untrusted, dropping
DHCP server messages on untrusted ports, and builds a binding table recording which MAC
legitimately holds which IP on which port in which VLAN. Dynamic ARP Inspection validates every
ARP reply on an untrusted port against that table. DAI without snooping has no table to check
against, which is why these are one configuration and not two.

**Why this is needed in addition to segmentation.** Segmentation stops a guest on the guest VLAN
attacking a staff workstation, since they are in different broadcast domains. It does not stop an
attacker already inside the staff segment, which the brief makes realistic by recording unlocked
branch cabinets and unenforced visitor sign in. Someone who patches a laptop into a staff port is
in the staff broadcast domain, and segmentation has nothing left to say.

**Key commands.**

```
ip dhcp snooping
ip dhcp snooping vlan 10,20,30,40,99
no ip dhcp snooping information option
interface GigabitEthernet0/1
 ip dhcp snooping trust
 ip arp inspection trust
interface range FastEthernet0/1-4
 ip dhcp snooping limit rate 10
ip arp inspection vlan 10,40
```

Trust is the entire mechanism, and the uplink toward the real server is the only trusted port.
One wrongly trusted access port reopens the whole attack, and the common mistake is trusting a
port because a device on it stopped working. The rate limits blunt DHCP starvation, where an
attacker exhausts the scope by requesting every address.

DAI is applied to VLANs 10 and 40 only, the VLANs whose hosts obtain addresses by DHCP and
therefore have binding entries to validate against. VLANs 20 and 30 hold statically addressed
servers with no binding entry, which is what an ARP access list exists for. VLAN 99 is
deliberately excluded, being an out of band management segment reachable only from a controlled
jump host, where enabling DAI would risk cutting management access to the devices being managed.
Excluding a physically controlled out of band segment is a design decision, not an omission.

**Verification.** A rogue DHCP server was attached to an untrusted staff port, advertising itself
as default gateway and DNS. The victim still received the legitimate lease, gateway `10.10.10.1`
and DNS `10.10.20.11`, both from the real pool, and the binding table afterwards contains no rogue
sourced entry. The rogue server was live and correctly configured, which is evidenced separately,
so the attack failed rather than never having been attempted.

**What cannot be evidenced here.** DAI reports Enabled and Active on the protected VLANs, which
evidences the control is in force. However Packet Tracer does not increment the DAI statistics
counters. Forwarded, Dropped, DHCP Drops and ACL Drops all remain at zero even while ARP is
demonstrably being exchanged, so DAI cannot be shown catching traffic, and there is no ARP
spoofing tool to generate the attack. On production hardware a poisoned ARP reply on an untrusted
port would increment Dropped and raise a `%SW_DAI-4-DHCP_SNOOPING_DENY` message naming the
offending MAC, claimed IP and ingress port, which would feed Control 8. Also, `show ip dhcp
snooping` in Packet Tracer prints configuration only with no drop counters, so evidence comes
from the victim's retained configuration and the binding table instead.

## 7.4 Member 4

### Configuration 7, NetFlow export, plan linked

**What was intended, and why this differs.** Configuration 7 was specified as a site to site
IPsec VPN implementing Control 12. Packet Tracer 8.2 on the ISR 2911 has no cryptographic feature
set. `crypto isakmp policy 10` is rejected with the caret on `crypto` itself, so the entire
command family is absent from the parser. The `securityk9` package cannot be activated, since
`license ?` in configuration mode offers only `boot`, with no `accept`, `install` or
`right-to-use` option, and after two reloads `show version` still reports `security / disable /
None`. The same absence removed the Zone Based Policy Firewall from Configuration 5.

Control 12 therefore has no implementing configuration, recorded as a gap rather than concealed.
The IPsec design remains the recommendation.

**Why NetFlow is the right substitute rather than a consolation.** The group adopted Member 4's
IDS/IPS proposal A4.4, whose second half specifies exactly this, NetFlow exported from the
switches and routers Northbridge already owns, at head office and at all six branches, into a
collector that baselines normal behaviour and alerts on deviation. Configuring it here implements
the recommendation the group actually adopted, and it tests the proposal's central practical
claim, that branch visibility needs no appliance, because it is applied to `BR1-R1` with nothing
deployed at the branch.

**What flow data detects that signatures do not.** A signature engine matches known exploits. It
cannot detect an authenticated attacker using legitimate credentials and legitimate protocols,
which is what T1, T2, T7 and T8 all produce. There is no signature for the statement that Alice's
account is behaving unlike Alice. Flow records describe who talked to whom, when, how much and for
how long, none of which is hidden by encryption. Internal reconnaissance, one host connecting to
many hosts in a short window, is the clearest signal in flow data, and it appears before any
payload executes, which is the earliest detection point in T3's chain.

**Key commands.**

```
ip flow-export destination 10.10.99.11 2055
ip flow-export version 9
ip flow-export source Loopback0
interface GigabitEthernet0/0.10
 ip flow ingress
```

Ingress on every internal subinterface captures traffic as it enters the router from each zone,
which is where movement between VLANs becomes visible, and is the placement that detects T3's
propagation. Sourcing records from a fixed loopback gives one device one address in every record.
The export lines say where to send, and `ip flow ingress` says what to collect, which are two
separate things. A configuration with only the first looks correct while the cache stays empty.

**Verification.** The flow cache records individual flow records with source, destination,
protocol, port and packet count, with no agent on any endpoint and no signature database. After a
reconnaissance sequence, the cache shows records sharing one source address reaching different
destinations on different exit paths, with 153 ICMP flows in the aggregate counters. Branch flow
records appear on `BR1-R1` from `192.168.1.50`, at a site where nothing was installed.

The reconnaissance test also documented two other controls working. ICMP from staff to core
banking returned `Destination host unreachable` from `STAFF-IN`, and the return flow to
`203.0.113.2` corroborates the edge NAT in Configuration 5.

**Platform limitations.** `show ip flow export` and `show ip flow interface` are not implemented,
so verification uses `show running-config | include flow` for the configuration and `show ip cache
flow` for the cache, the latter being the better command anyway since it shows the records
themselves. `ip flow-cache timeout` is rejected, so the 15 second inactive window cannot be
extended, and individual records age out quickly, which is itself why the architecture exports
records to a collector rather than polling the router. Packet Tracer has no NetFlow collector
service, so records cannot be shown arriving at the server.

### Configuration 8, centralised syslog and NTP, free choice

**What it achieves.** It makes every network device send log messages to one server with
accurate, synchronised timestamps. The brief states the problem directly, that there is no
centralised logging or audit trail across systems, so even where activity is technically recorded
nobody would necessarily notice unusual behaviour in time to act.

Device local logs have three fatal properties. They are lost when they matter most, since the
buffer is in RAM and is cleared by a reboot, which is the first thing both an attacker and a
troubleshooter will do. They are deletable by whoever compromises the device, whereas deleting a
message already sent to a separate server requires compromising that server too. They cannot be
correlated, since an attack crossing a branch switch, branch router, WAN, head office router and
core switch leaves five fragments on five devices.

**Why NTP is part of the same configuration.** Correlation requires a common clock. If the branch
switch thinks it is 09:14 and the head office router thinks it is 11:47, the collected logs
cannot be ordered, and an ordered sequence of events is the entire value of central logging.
Timestamps that cannot be shown to be accurate are also weak evidence, which matters for a bank
that may have to demonstrate to a regulator what happened and when.

**Key commands.**

```
clock timezone IST 5 30
ntp master 3
ntp authentication-key 1 md5 NBntpKey2026
ntp trusted-key 1
ntp authenticate
service timestamps log datetime msec
logging host 10.10.99.11
logging buffered 16384
```

Without `datetime`, messages are stamped with device uptime, which is useless for correlation
across devices. NTP authentication matters more than it looks, since an attacker who can feed a
device false time can make its log entries land outside whatever window an investigator examines.
Severity 6, informational, is the default trap level and captures interface state changes, login
successes and failures, access list deny hits, port security violations and configuration changes.
Severity 7 includes debug output, floods both link and server, and in practice gets logging
switched off within a month.

**Verification.** All devices synchronise at stratum 4. Messages arrive at the collector with
millisecond timestamps and the correct source device, and events from `HQ-R1` and `BR1-SW1`
appear in the same view, in the correct order, with agreeing timestamps. That is one ordered
timeline across the estate, which is the brief's finding closed. The log also captures AAA login
successes for the TACACS+ user, showing Control 1's output landing in Control 8's platform, and
a failed login recorded centrally.

**A gap found in the build.** `HQ-SW1`, `MGMT-SW1` and `BR1-SW1` originally had no management IP
address. A Layer 2 switch needs a switched virtual interface to originate NTP and syslog traffic
at all, so all three applied the commands cleanly and then silently sent nothing. This surfaced
only when `show ntp associations` reported `reach 0`. Management SVIs were added on VLAN 99 at
head office and VLAN 110 at the branch, with `ip default-gateway`, after which both switches
reached the server and synchronised.

**Platform limitations.** `logging source-interface` and `ntp source` are both rejected, so there
is no way to pin a device's source address. The consequence is visible in the NTP output. Clients
configured with `ntp server 10.10.1.1`, the loopback, show `reach 0` against that address and a
second automatically created association against the router's egress interface address, which is
the one that works. Synchronisation still succeeds, but this is precisely the problem a fixed
source interface exists to solve, one device appearing under several addresses so a collector
cannot attribute records reliably. Also rejected: `logging trap`, which defaults to informational
so omitting it changes nothing, `archive` and `log config` for configuration change logging, and
the `localtime` and `show-timezone` timestamp keywords.
