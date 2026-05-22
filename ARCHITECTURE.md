# RunUpdates Architecture

RunUpdates is a deterministic, YAML‑driven update orchestrator for Linux hosts.
Its architecture emphasizes clarity, reproducibility, and operator‑grade behavior.

This document describes the internal structure of RunUpdates, the execution pipeline, and the responsibilities of each component.

---

## 1. Design Principles

RunUpdates is built around:

* **Deterministic execution** — no hidden behavior, no implicit defaults  
* **Explicit configuration** — all behavior originates from `hosts.yml`  
* **Minimal dependencies** — pure Python + standard libraries where possible  
* **Structured logging** — predictable, machine‑readable output  
* **Separation of concerns** — each module has a single responsibility  
* **Audit‑friendly operation** — logs and summaries reflect exactly what happened  

---

## 2. High‑Level Architecture

RunUpdates is composed of four primary layers:

Inventory → Selector → Connector → Executor → Orchestrator

Each layer transforms structured input into structured output, with no side effects outside its scope.

### 2.1 Inventory Loader ([inventory/loader.py])

The **RunUpdatesInventoryLoader** is responsible for:
* loading hosts.yml
* schema validation
* inheritance merging
* normalization into flattened host entries
* exposing both:
  * raw_yaml (for list operations)
  * normalized inventory (for orchestration)

This loader fully replaces the old InventoryProcessor.

### 2.2 Selector Layer ([operations/selector.py])

Responsible for:
* filtering normalized hosts based on CLI arguments
* validating that selected hosts exist
* returning a list of host execution targets

The selector **no longer performs flattening or inheritance resolution**.

### 2.3 Connector Layer ([operations/connector.py])

Responsible for establishing sessions:
* LocalSession (via PythonTools [sudo_run])
* SSHSession (via PythonTools SSH abstraction)

Each session provides a unified interface:

```python
session.run(command) → (exit_code, stdout, stderr)
```

The executor does not know or care whether the session is local or remote.

### 2.4 Executor Layer ([operations/executor.py])

Responsible for running the deterministic lifecycle:

[refresh → check → update? → clean → reboot?]

The executor:
* runs distro‑defined commands
* interprets exit codes
* detects reboot requirements
* logs each stage

Future versions will add:
* backend‑specific check parsing
* pre/post list operations
* per‑host summaries

### 2.5 Orchestrator Layer ([operations/orchestrator.py])

The orchestrator coordinates the entire run:
1. Receive normalized inventory
2. Select hosts
3. Create sessions
4. Execute lifecycle
5. Log results
6. Return aggregated status

The orchestrator no longer:
* flattens inventory
* merges inheritance
* builds execution plans
* writes per‑host summaries (planned)

It is now a clean, minimal coordinator.

## 3. Execution Pipeline

Each host follows the same deterministic sequence:

1. **refresh**
2. **check**
  * exit‑code interpretation
  * backend‑specific parsing (future)
3. **update** (only if needed)
4. **clean** (always runs)
5. **reboot detection**

Future enhancements:
* pre‑update list
* post‑update list
* per‑host summaries

### 3.1 Pre‑Update List

Runs the distro’s “list updates” command:

- zypper lu
- apt list --upgradable
- dnf check-update

Captures:

- available_before

### 3.2 Update Execution

Runs the distro’s update command:

- zypper --non-interactive up --auto-agree-with-licenses --recommends --replacefiles --allow-vendor-change
- apt upgrade -y
- dnf upgrade -y

Captures:

- exit code
- stdout
- stderr

### 3.3 Post‑Update List

Runs the list command again to capture:

- available_after
- updated_count = before - after

### 3.4 Reboot Detection

Distro‑specific mechanisms:

- openSUSE: zypper exit codes or /var/run/reboot-required
- Debian/Ubuntu: /var/run/reboot-required
- RedHat-family: needs-restarting -r

### 3.5 Summary Generation

A structured JSON file is written per host:

/var/log/runupdates/summaries/<hostname>.json

Contains:

- host metadata
- timestamps
- exit code
- package counts
- reboot_required
- errors (if any)

### 3.6 Logging

All stages produce structured logs:

- session lifecycle
- commands executed
- exit codes
- errors
- timing

## 4. Inventory Model

The inventory supports a hierarchical model:

linux:
  opensuse:
    hosts:
      sample:
        address: 192.168.1.10
        port: 2222

The loader merges:
* family defaults
* distro defaults
* host overrides

…into normalized host entries.

Future enhancements:
* schema versioning
* repo definitions
* GPG key imports
* host grouping and tags

## 5. PythonTools Integration

RunUpdates uses **PythonTools** as its execution substrate:
* sudo_run for privileged local execution
* local_command for non‑privileged execution
* SSHSession for remote execution
* structured logging injection
* secrets injection
* consistent return structures

PythonTools is now a standalone micro‑library shared across the Linktech Engineering Tools Suite.

## 6. Future Enhancements

Planned architectural improvements:
* backend‑specific check parsing
* per‑host JSON summaries
* pre/post list operations
* concurrency limits for parallel execution
* pluggable execution backends
* rollback hooks
* package‑level filtering
* optional diagnostics endpoints
* optional web dashboard (read‑only)

## 7. Summary

RunUpdates is designed to be:

- predictable
- auditable
- maintainable
- extensible
- operator‑grade

The architecture ensures that each component has a clear responsibility and that the entire execution pipeline remains deterministic and transparent.
