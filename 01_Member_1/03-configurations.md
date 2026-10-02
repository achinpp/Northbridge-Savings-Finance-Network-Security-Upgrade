# Member 1 — Individual Network Hardening Configurations

**Member:** [Member 1 — Full Name / IT Number]
**Configurations:** #1 AAA with TACACS+/RADIUS (plan-linked) · #2 SSH and management-plane hardening (free choice)

Both are carried out on the shared group topology described in `06_Topology/topology-spec.md`.
Plain-text scripts: `configs/cfg-1-aaa-tacacs-radius.txt`, `configs/cfg-2-ssh-mgmt-hardening.txt`.
Screenshot sequence: `06_Topology/screenshot-capture-guide.md`, shots 1.1–1.18.

---

## Configuration 1 — AAA with TACACS+ and RADIUS, with local fallback

**Device:** `HQ-R1` (head-office edge router), plus `HQ-SW1` for the RADIUS/802.1X side
**AAA server:** `AAA-SRV` at 10.10.99.10 in the MGMT-OOB zone

### What this configuration achieves

It moves authentication, authorisation and accounting for device administration off the
device and onto a central server, so that:

- Every administrator logs in as **themselves**, not with a shared enable password.
- The AAA server, not the router, decides whether a login is allowed — so disabling a leaver
  in one place disables them on every device at once.
- Every login and every privileged command generates an **accounting record** on the central
  server, producing the audit trail Northbridge currently does not have.
- A **local fallback account** survives loss of the AAA server, so an outage of the
  management network does not lock the team out of its own routers. The method list order
  `group tacacs+ local` is what delivers this, and it is the single most important detail in
  the script — reversing it, or omitting `local`, is how teams lock themselves out.

### Plan linkage and threats addressed

This implements **Control 1 (Centralised AAA — Cisco ISE with RADIUS and TACACS+)** and
contributes to **Control 3 (individual named accounts, no shared accounts)** and **Control 9
(secure management plane)** from the group's combined layered security plan.

It addresses **T2 (credential abuse and privilege escalation through password reuse and the
absence of central AAA)** directly: T2's core finding is that Northbridge cannot attribute a
privileged action to an individual, because every device holds its own local accounts and
infrastructure logins are shared. TACACS+ command accounting is the specific control that
closes that gap. It also partially addresses **T1**, because the same AAA service is what the
remote-access VPN authenticates against, removing the shared VPN account's independent
credential store.

### Command sequence

Entered on `HQ-R1`. The full script with comments is in
`configs/cfg-1-aaa-tacacs-radius.txt`.

```
enable
configure terminal

! --- local fallback account FIRST, before AAA is enabled ---
username netadmin privilege 15 secret Fallb@ck-NB-2026
enable secret NBenable-2026

! --- enable the AAA subsystem ---
aaa new-model

! --- define the TACACS+ server (device administration) ---
tacacs-server host 10.10.99.10 key NBtac$2026

! --- define the RADIUS server (network access / 802.1X / VPN) ---
radius-server host 10.10.99.10 auth-port 1645 acct-port 1646 key NBrad$2026

! --- authentication: try TACACS+, fall back to the local database ---
aaa authentication login default group tacacs+ local
aaa authentication enable default group tacacs+ enable

! --- authorisation: who may enter exec mode, and which commands ---
aaa authorization exec default group tacacs+ local
aaa authorization commands 15 default group tacacs+ local

! --- accounting: the audit trail Northbridge is missing ---
aaa accounting exec default start-stop group tacacs+
aaa accounting commands 15 default start-stop group tacacs+

! --- apply to the management lines ---
line console 0
 login authentication default
 exec-timeout 5 0
 logging synchronous
 exit
line vty 0 4
 login authentication default
 exec-timeout 5 0
 transport input ssh
 exit

end
write memory
```

### Verification commands and expected output

Run each immediately after the configuration, in this order. This is the
command-then-verify pattern used in the lab guides.

| # | Verification command | What the output must show |
|---|---|---|
| 1 | `show running-config \| include aaa` | Every `aaa` line present, with `group tacacs+ local` on the authentication line |
| 2 | `show running-config \| include tacacs\|radius` | Both server hosts at 10.10.99.10 with keys present (encrypted if `service password-encryption` is on) |
| 3 | `show tacacs` | Server 10.10.99.10 listed; socket opens and closes reported |
| 4 | `show radius statistics` | Access-request / access-accept counters incrementing after a test login |
| 5 | **Live test:** from `PC-ADMIN`, `ssh -l alice.perera 10.10.1.1` | Login succeeds using a user that exists **only on the AAA server**, never in the router's local config — this is the proof that central AAA is actually in force |
| 6 | **Negative test:** attempt login with a user that exists nowhere | Rejected, and the rejection is recorded on the AAA server |
| 7 | **Fallback test:** shut `AAA-SRV`'s interface, then log in as `netadmin` | Login succeeds via the local database, proving the fallback path works |

> **Why test 7 matters for the marks.** The rubric rewards verification output that "clearly
> shows the expected result". Showing only a successful central login proves half the control.
> Showing that the fallback also works proves the configuration is safe to deploy, which is
> the difference between a working lab and a deployable control.

### AAA server setup (on `AAA-SRV`, Packet Tracer Server device)

1. Services → **AAA** → Service **On**.
2. Network Configuration: add client `HQ-R1`, Client IP `10.10.99.1`, Secret `NBtac$2026`,
   ServerType **TACACS**. Add a second entry for RADIUS with secret `NBrad$2026`.
3. User Setup: add `alice.perera` / `Str0ng-Pass-1`, and a second user `bob.silva` /
   `Str0ng-Pass-2` so the accounting records show two distinguishable identities.

---

## Configuration 2 — SSH and management-plane hardening (free choice)

**Device:** `HQ-R1` and `HQ-SW1`

### What this configuration achieves and the real-world problem it solves

Central AAA decides *who* may log in. It does nothing about *how* the login travels. On a
default Cisco device, management is Telnet — plaintext, so the username and password cross
the network in the clear, and on Northbridge's flat network any host in the same broadcast
domain can read them with a packet capture. Enabling central AAA over Telnet would mean
every administrator's individual credential is now sniffable, which makes the identity
control worse than useless: it creates a single high-value credential and then broadcasts it.

This configuration solves that by making the management plane itself trustworthy:

- **SSHv2 only**, Telnet refused — management traffic is encrypted and the device is
  authenticated to the administrator by its host key.
- **Password storage hardened** — `enable secret` rather than `enable password`, and
  `service password-encryption` so configuration backups and screenshots do not leak
  plaintext secrets.
- **Idle sessions time out** (`exec-timeout`), so an unattended session in a branch back
  office — where the brief notes cabinets were found unlocked — does not stay privileged
  indefinitely.
- **Brute-force throttling** (`login block-for`), which matters directly because the brief
  describes password reuse as common, making credential-stuffing against device logins a
  realistic path.
- **An access-class ACL on the VTY lines**, so management is only reachable from the MGMT-OOB
  jump host subnet rather than from anywhere on the network.
- **A legal banner**, which is both a deterrent control and, in many jurisdictions, a
  precondition for acting on unauthorised access.

This is the free-choice configuration. It is not one of the controls in the group plan's
numbered list as a standalone item, but it is the prerequisite that makes Configuration 1
safe, which is why I chose it as my second.

### Command sequence

```
enable
configure terminal

hostname HQ-R1
ip domain-name northbridge.lk

! --- password hygiene ---
enable secret NBenable-2026
service password-encryption
security passwords min-length 10

! --- local administrator account ---
! SSH refuses connections if the VTY lines have no authentication
! method at all. This configuration precedes the AAA configuration,
! so the local database is what authenticates SSH until TACACS+ exists.
! The same account is re-stated in Configuration 1 as the AAA local
! fallback, which is the point: it keeps the device reachable if the
! AAA server is unavailable.
username netadmin privilege 15 secret Fallb@ck-NB-2026

! --- generate the SSH host key (1024 bits or more enables SSHv2) ---
crypto key generate rsa general-keys modulus 1024

! --- force SSH version 2 and tighten the handshake ---
ip ssh version 2
ip ssh time-out 60
ip ssh authentication-retries 2

! --- restrict which source addresses may even attempt management ---
ip access-list standard MGMT-HOSTS
 permit 10.10.99.0 0.0.0.255
 deny any
 exit

! --- brute-force throttling ---
login block-for 120 attempts 3 within 60
login on-failure log
login on-success log

! --- legal banner (deterrent control) ---
banner motd #
*********************************************************
  Northbridge Savings & Finance - AUTHORISED ACCESS ONLY
  Activity on this device is logged and monitored.
  Disconnect immediately if you are not an authorised user.
*********************************************************
#

! --- apply to the management lines ---
line vty 0 4
 login local
 transport input ssh
 access-class MGMT-HOSTS in
 exec-timeout 5 0
 logging synchronous
 exit

line console 0
 exec-timeout 5 0
 logging synchronous
 exit

! --- shut the unused aux line ---
line aux 0
 no exec
 exit

end
write memory
```

### Verification commands and expected output

| # | Verification command | What the output must show |
|---|---|---|
| 1 | `show ip ssh` | `SSH Enabled - version 2.0`, authentication retries 2, timeout 60 |
| 2 | `show crypto key mypubkey rsa` | An RSA key pair named `HQ-R1.northbridge.lk`, 1024 bits or more |
| 3 | `show running-config \| begin line vty` | `transport input ssh`, `access-class MGMT-HOSTS in`, `exec-timeout 5 0` |
| 4 | `show access-lists MGMT-HOSTS` | The permit for 10.10.99.0/24 and the logged deny |
| 5 | **Positive test:** from `PC-ADMIN` (10.10.99.x), `ssh -l netadmin 10.10.1.1` | Banner displays, login succeeds |
| 6 | **Negative test:** from the same PC, `telnet 10.10.1.1` | Connection refused — proves Telnet is genuinely disabled, not merely unused |
| 7 | **Negative test:** from `PC-BR1` (a branch user subnet), `ssh -l netadmin 10.10.1.1` | Blocked by `access-class`; `show access-lists` deny counter increments |
| 8 | `show login failures` | Records the failed attempts from the blocked tests |

> Shot 6 and shot 7 are the two that earn the marks. Anyone can screenshot a successful SSH
> login; showing that Telnet is *refused* and that an out-of-zone host is *blocked* is what
> demonstrates the hardening actually took effect.

### Commands to check on your Packet Tracer build

Packet Tracer's IOS command coverage is not complete. If a command is rejected, note it and
use the stated substitute — the brief asks for the exact syntax used, so record what you
actually entered.

| Command | If unsupported in your PT version |
|---|---|
| `login block-for 120 attempts 3 within 60` | Omit; state in the write-up that it is part of the production configuration but unsupported in Packet Tracer |
| `security passwords min-length 10` | Omit if rejected |
| `ip access-list standard MGMT-HOSTS` | Use the classic form: `access-list 10 permit 10.10.99.0 0.0.0.255` then `access-class 10 in` |
| `show login failures` | Use `show running-config` and the live negative tests as the evidence instead |
| `aaa authorization commands 15 default group tacacs+ local` | Accepted on most PT router images; if rejected, keep the exec authorisation and accounting lines and note the limitation |
