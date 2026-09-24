# RunUpdates Architecture

**Suite:** Linktech Engineering Tools Suite  
**Maintainer:** Leon McClatchey, Linktech Engineering LLC  
**License:** MIT (source) • Proprietary (binaries)  
**Requires:** Python 3.12+  
**Version:** 1.0.0 (Stable) • Nightly: latest  
**Packaging:** DEB • RPM • TGZ • ZIP  
**PythonTools:** 0.2.0  
**Last Updated:** 2026‑09‑24

---

## 📘 Table of Contents
1. [Overview](#-1-overview)  
2. [Design Principles](#-2-design-principles)  
3. [High‑Level Architecture](#-3-high-level-architecture)  
    1. [3.1 Inventory Loader](#31-inventory-loader-inventoryloaderpy)  
    2. [3.2 Orchestrator](#32-orchestrator-operationsorchestratorpy)  
    3. [3.3 Selector](#33-selector-operationsselectorpy)  
    4. [3.4 Connector](#34-connector-operationsconnectorpy)  
    5. [3.5 Executor](#35-executor-operationsexecutorpy)  
        1. [3.5.1 Exit‑Code Interpretation Model](#351-exit-code-interpretation-model)  
4. [Execution Pipeline](#-4-execution-pipeline)  
    1. [4.1 Exit‑Code Interpretation (Cross‑Link)](#41-exit-code-interpretation-cross-link)  
5. [Inventory Model](#-5-inventory-model)  
6. [PythonTools Integration](#-6-pythontools-integration)  
7. [Future Enhancements](#-7-future-enhancements)  
8. [Summary](#-8-summary)

---

## 🔍 1. Overview

RunUpdates is a deterministic, YAML‑driven update orchestrator for Linux hosts.  
Its architecture emphasizes clarity, reproducibility, and operator‑grade behavior.

This document describes the internal structure of RunUpdates, the execution pipeline, and the responsibilities of each component.

For installation, configuration, and operator usage, see the companion document:  
**[QuickStart](QuickStart.md)**.

---

## 🧭 2. Design Principles

RunUpdates is built around:

* **Deterministic execution** — no hidden behavior, no implicit defaults  
* **Explicit configuration** — all behavior originates from `hosts.yml`  
* **Minimal dependencies** — PythonTools + standard libraries  
* **Structured logging** — predictable, machine‑readable output  
* **Separation of concerns** — each module has a single responsibility  
* **Audit‑friendly operation** — logs and summaries reflect exactly what happened  

---

## 🧱 3. High‑Level Architecture

RunUpdates is composed of five primary layers, executed in this order:

`Inventory → Orchestrator → Selector → Connector → Executor`

### 3.1 Inventory Loader (inventory/loader.py)

The **RunUpdatesInventoryLoader** is responsible for:
* loading `hosts.yml`
* schema validation
* inheritance merging
* vault merging
* normalization into flattened host entries

It produces two representations:
* `raw_yaml` — used for list operations
* `normalized` — used for orchestration

For details on creating the configuration directory and populating `hosts.yml`,
see **QuickStart → Configuration Directory Setup**.

#### Key Behaviors

* `address` is always normalized to a list
* vault secrets override inventory fields
* family/distro/host inheritance is deterministic
* validation is strict and fail‑fast

The loader fully replaces the old `InventoryProcessor`.

---

### 3.2 Orchestrator (operations/orchestrator.py)

The orchestrator coordinates the entire run:
1. Receive normalized inventory
2. Select hosts
3. Create sessions
4. Execute lifecycle
5. Collect per‑host results
6. Write final summary
7. Return aggregated status

### Final Summary (Implemented)

The orchestrator writes:
`summary.json`

containing:

* run start/end
* duration
* total hosts
* completed
* failed
* skipped
* repo_broken
* reboot_required
* per‑host status map

**Orchestrator Does NOT:**

* flatten inventory
* merge inheritance
* run commands directly

It is a clean, minimal coordinator.

---

### 3.3 Selector (operations/selector.py)

Responsible for:

* filtering normalized hosts based on CLI arguments
* validating that selected hosts exist
* returning a list of host execution targets

The selector operates **only** on normalized data.

It does **not**:

* merge inheritance
* perform vault operations
* modify host definitions

---

### 3.4 Connector (operations/connector.py)

Responsible for establishing execution sessions.

RunUpdates uses PythonTools for all execution primitives.

#### Local Execution

Uses:

PythonTools.sudo_run

There is **no LocalSession class**.

#### Remote Execution

Uses:

PythonTools.SSHSession

#### Unified Interface

Both local and remote execution expose:

```python
session.run(command) → (exit_code, stdout, stderr)
```

The executor does not know or care whether the session is local or remote.

#### Connector Responsibilities

* choose local vs remote session
* initialize the session
* log connection lifecycle
* return a ready‑to‑use session object

For SSH and privilege requirements, see **QuickStart → Vault Setup**

---

### 3.5 Executor (operations/executor.py)

Responsible for running the deterministic lifecycle:

`refresh → check → update? → clean → reboot detection`


The executor:

* runs distro‑defined commands
* interprets exit codes
* detects reboot requirements
* logs each stage
* records lifecycle events
* writes per‑host summaries

For the operator‑facing summary format, see **QuickStart → Runtime Directories**.

#### Per‑Host Summary (Implemented)

After all stages complete, the executor writes:

Code
```
<hostname>.json
```

containing:
* lifecycle status
* update status
* repo health
* exit codes
* stdout/stderr
* timestamps
* reboot requirement
* lifecycle events

For the operator‑facing summary directory layout, see
**QuickStart → Runtime Directories**.

---

### 3.5.1 Exit‑Code Interpretation Model

RunUpdates does not hardcode any package‑manager exit codes.  
Different distros (APT, DNF, YUM, Zypper, Pacman, etc.) return different exit
codes for the same semantic meaning, and even the same distro may return
different codes depending on the command being executed.

To support this variability, RunUpdates uses a fully declarative exit‑code
model defined in the inventory under:

```yaml
exit_codes:
  check:
    up_to_date: [...]
    patches_available: [...]
    reboot_required: [...]
    error: ["*"]
```

#### Key Properties
* **Distro‑specific**
  Each distro defines its own exit‑code rules in its inventory section.

* **Command‑specific**
  Exit‑code rules are defined per lifecycle step (``refresh``, ``check``, ``update``,
  ``clean``), not globally.

* **Host‑overrideable**
  Hosts may override distro defaults. The loader merges family → distro → host
  definitions, with host values taking precedence.

* **Deterministic interpretation**
  The executor calls ``classify_exit_code(step, exit_code, rules, host)`` to
  determine the semantic meaning of each exit code.

* **No implicit assumptions**
  RunUpdates never assumes that a particular exit code means “updates available”
  or “reboot required”. All semantics originate from the inventory.

This model ensures that RunUpdates remains fully distro‑agnostic and that adding
support for a new distro requires no code changes—only inventory definitions.

---

## 🔄 4. Execution Pipeline

Each host follows the same deterministic sequence:
1. refresh
2. check
3. exit‑code interpretation
4. update (only if needed)
5. clean
6. reboot detection
7. per‑host summary

### 4.1 Exit‑Code Interpretation (Cross‑Link)

RunUpdates does not hardcode any package‑manager exit codes.  
Different distros return different codes for the same semantic meaning, and even
the same distro may vary by command.

Exit‑code semantics are defined declaratively in the inventory under:

```yaml
exit_codes:
  check:
    up_to_date: [...]
    patches_available: [...]
    reboot_required: [...]
    error: ["*"]
```

The executor calls ``classify_exit_code(step, exit_code, rules, host)`` to interpret
each exit code using the merged host configuration.

For a high‑level explanation of orchestrator exit codes (distinct from
package‑manager exit codes), see **QuickStart.md → Exit Codes**.

#### Not Yet Implemented (Future)

* pre‑update list
* post‑update list
* update count diffing

These remain roadmap items.

---

## 📁 5. Inventory Model

The inventory supports a hierarchical model:

```yaml
linux:
  opensuse:
    hosts:
      sample-node:
        address: ["192.0.2.10"]
        port: 2222
```

The loader merges:

* family defaults
* distro defaults
* host overrides
* vault secrets

…into normalized host entries.

### Current Behavior

* openSUSE Leap and Tumbleweed share the opensuse distro
* splitting them requires only inventory changes, not code changes

### Future Enhancements

* schema versioning
* repo definitions
* GPG key imports
* host grouping and tags

---

## 🧩 6. PythonTools Integration

RunUpdates uses PythonTools as its execution substrate:
* ``sudo_run`` for privileged local execution
* ``local_command`` for non‑privileged local execution
  * (available in PythonTools but is not used by RunUpdates today)
* ``SSHSession`` for remote execution
* structured logging injection
* secrets injection
* consistent return structures

PythonTools is a standalone micro‑library shared across:
* RunUpdates
* BotScanner
* TimerDeck
* future tools

RunUpdates relies on PythonTools for all execution‑layer behavior.

---

## 🛣 7. Future Enhancements

Planned architectural improvements include:

* **backend‑specific check parsing**  
  Structured parsing of `check` output for distros that provide machine‑readable formats (e.g., Zypper XML, DNF JSON). 

* **pre/post list operations**  
  Hooks for listing packages before and after updates.

* **update count diffing**  
  Deterministic comparison of package lists.

* **concurrency limits for parallel execution**  
  Operator‑controlled maximum parallel hosts.

* **rollback hooks**  
  Optional user‑defined rollback commands.

* **package‑level filtering**  
  Include/exclude specific packages or groups.

* **pluggable execution backends**  
  Support for alternate execution engines.

* **optional diagnostics endpoints**  
  Health and metrics endpoints.

* **optional web dashboard (read‑only)**  
  A lightweight UI for browsing logs, summaries, and run history.

For installation and configuration details referenced here, see
**QuickStart → Configuration Directory Setup** and  
**QuickStart → Vault Setup**.

## 📄 8. Summary

RunUpdates is designed to be:

* predictable
* auditable
* maintainable
* extensible
* operator‑grade

The architecture ensures that each component has a clear responsibility and that the entire execution pipeline remains deterministic and transparent.
