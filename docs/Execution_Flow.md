# RunUpdates — Execution Flow

This document describes the full execution lifecycle of RunUpdates, from startup to final result aggregation.  
It complements `ARCHITECTURE.md` by focusing on *when* each component runs and *how* the system behaves during a complete update cycle.

RunUpdates is designed to be deterministic, predictable, and operator‑grade.  
The execution flow reflects these principles.

---

# 1. Purpose

The goal of this document is to:

- explain the exact sequence of operations during a run  
- clarify how inventory, sessions, logging, and summaries interact  
- define error‑handling behavior  
- document determinism guarantees  
- prepare for future parallel execution  

This is the authoritative reference for understanding how RunUpdates performs updates.

---

# 2. High‑Level Lifecycle

A full RunUpdates execution follows this sequence:

1. Load inventory
2. Validate schema
3. Build execution plans
4. Initialize logging
5. Iterate through hosts
6. Create session (local or SSH)
7. Pre‑update list
8. Update execution
9. Post‑update list
10. Reboot detection
11. Summary generation
12. Logging
13. Final aggregation


Each step is deterministic and produces structured output.

---

# 3. Detailed Execution Flow

## 3.1 Load Inventory

RunUpdates loads `hosts.yml` and parses it into an internal structure.

Actions:

- read YAML  
- normalize hierarchy  
- prepare family/distro/host mappings  

Failures here stop execution immediately.

---

## 3.2 Validate Schema

Validation ensures:

- required fields exist  
- types are correct  
- no unknown keys  
- no empty blocks  
- no invalid ports  
- no missing usernames  
- no disabled hosts selected for execution  

If validation fails:

- an error is logged  
- execution stops before any host is contacted  

---

## 3.3 Build Execution Plans

The selector constructs a **HostExecutionPlan** for each enabled host.

Each plan contains:

- host metadata  
- distro metadata  
- resolved commands  
- connection parameters  

This step is deterministic and produces a stable ordering.

---

## 3.4 Initialize Logging

RunUpdates:

- creates a timestamped log file  
- injects its logger into PythonTools  
- writes initial lifecycle entries  

PythonTools never initializes logging on its own.

---

## 3.5 Iterate Through Hosts

Hosts are processed in deterministic order:

- as defined by the inventory  
- with no parallelism (current version)  

Future versions will allow concurrency while preserving per‑host ordering.

---

## 3.6 Create Session

For each host:

- `LocalSession` is used for local mode  
- `SSHSession` is used for remote hosts  

Session creation logs:

- connection attempt  
- success or failure  
- authentication method used (non‑sensitive)  

If session creation fails:

- the host is marked as failed  
- execution continues to the next host  

---

## 3.7 Pre‑Update List

RunUpdates executes the distro’s “list updates” command.

Examples:

- `zypper lu`
- `apt list --upgradable`
- `dnf check-update`

Captured:

- `available_before`  
- exit code  
- stdout/stderr  

This establishes a baseline for update counts.

---

## 3.8 Update Execution

RunUpdates executes the distro’s update command.

Examples:

- `zypper --non-interactive up --auto-agree-with-licenses --recommends --replacefiles --allow-vendor-change`
- `apt upgrade -y`
- `dnf upgrade -y`

Captured:

- exit code  
- stdout/stderr  
- classification (from exit‑code model)  

Failures here do **not** stop execution for other hosts.

---

## 3.9 Post‑Update List

RunUpdates executes the list command again.

Captured:

- `available_after`  
- `updated_count = before - after`  

This provides deterministic update metrics.

---

## 3.10 Reboot Detection

RunUpdates checks distro‑specific reboot indicators:

- openSUSE: zypper exit codes or `/var/run/reboot-required`
- Debian/Ubuntu: `/var/run/reboot-required`
- RedHat-family: `needs-restarting -r`

Captured:

- `reboot_required: true/false`

---

## 3.11 Summary Generation

A structured JSON summary is written per host:

/var/log/runupdates/summaries/<hostname>.json


Contains:

- host metadata  
- timestamps  
- exit code  
- package counts  
- reboot_required  
- errors (if any)  

Summaries are designed for:

- dashboards  
- monitoring systems  
- external automation  

They are separate from operator logs.

---

## 3.12 Logging

Every stage logs:

- command start  
- command end  
- exit codes  
- errors  
- timing  
- classifications  

Logs are chronological and append‑only.

### Parallel Execution Ordering Guarantee (Future)

When concurrency is introduced:

- each host’s log entries remain internally ordered  
- cross‑host interleaving may occur  
- determinism is preserved per host  

---

## 3.13 Final Aggregation

RunUpdates aggregates all host results into a final in‑memory structure:

- total hosts  
- successes  
- failures  
- reboot_required list  
- update counts  

This is returned to the caller (CLI or API wrapper).

---

# 4. Error Handling Flow

RunUpdates uses deterministic error handling.

## 4.1 Inventory Errors

- stop execution immediately  
- no hosts are contacted  

## 4.2 Connection Errors

- host marked as failed  
- execution continues  

## 4.3 Command Errors

- logged with classification  
- host continues through remaining steps  

## 4.4 Summary Errors

- logged  
- do not affect other hosts  

RunUpdates never silently ignores errors.

---

# 5. Determinism Guarantees

RunUpdates guarantees:

- stable host ordering  
- stable command ordering  
- stable logging format  
- no implicit defaults  
- no hidden behavior  
- reproducible results  

Given the same inventory and environment, RunUpdates produces the same output.

---

# 6. Parallel Execution (Future)

Parallel execution will introduce:

- concurrency limits  
- per‑host execution threads  
- grouped logging  
- deterministic ordering per host  

The execution flow remains the same; only scheduling changes.

---

# 7. Example Timeline (Abstract)

```
14:00:01 Load inventory
14:00:01 Validate schema
14:00:02 Build execution plans
14:00:02 Initialize logging

14:00:03 Host A: session start
14:00:03 Host A: pre‑update list
14:00:04 Host A: update execution
14:00:20 Host A: post‑update list
14:00:21 Host A: reboot detection
14:00:21 Host A: summary written

14:00:22 Host B: session start
```


This example uses placeholders only.

---

# 8. Summary

The RunUpdates execution flow is:

- explicit  
- deterministic  
- auditable  
- operator‑grade  

This document defines the authoritative lifecycle for all update operations.
