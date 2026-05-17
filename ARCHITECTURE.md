# RunUpdates Architecture

RunUpdates is a deterministic, YAML‑driven update orchestration engine designed for Linux hosts.  
Its architecture emphasizes clarity, reproducibility, and operator‑grade behavior.

This document describes the internal structure of RunUpdates, the execution pipeline, and the responsibilities of each component.

---

## 1. Design Principles

RunUpdates is built around:

- **Deterministic execution** — no hidden behavior, no implicit defaults  
- **Explicit configuration** — all behavior originates from `hosts.yml`  
- **Minimal dependencies** — pure Python + standard libraries where possible  
- **Structured logging** — predictable, machine‑readable output  
- **Separation of concerns** — each module has a single responsibility  
- **Audit‑friendly operation** — logs and summaries reflect exactly what happened  

---

## 2. High‑Level Architecture

RunUpdates is composed of four primary layers:

Inventory → Selector → Connector → Executor → Orchestrator

Each layer transforms structured input into structured output, with no side effects outside its scope.

### 2.1 Inventory Layer (`hosts.yml`)
The inventory defines:

- families (e.g., `debian-family`)
- distros (e.g., `ubuntu`, `opensuse-tumbleweed`)
- hosts (address, port, username, enabled flag)
- optional repo and key definitions (future)

The inventory is parsed into a normalized internal structure before execution begins.

### 2.2 Selector Layer (`operations/selector.py`)
Responsible for:

- flattening the inventory hierarchy  
- resolving family → distro → host relationships  
- filtering hosts based on CLI arguments  
- validating host entries  

The selector produces a list of **HostExecutionPlan** objects, each containing:

- host metadata  
- distro metadata  
- resolved commands  
- connection parameters  

### 2.3 Connector Layer (`operations/connector.py`)
Responsible for establishing sessions:

- `LocalSession` for local testing  
- `SSHSession` for remote hosts  

Each session provides a unified interface:

```python
session.run(command) → (exit_code, stdout, stderr)
```

The executor does not know or care whether the session is local or remote.

### 2.4 Executor Layer (operations/executor.py)
Responsible for:

- running distro‑specific update commands
- running pre‑ and post‑update “list updates” commands
- capturing exit codes
- detecting reboot requirements
- collecting structured execution data

The executor produces a HostResult object containing:

- Exit code
- stdout/stderr
- package counts (before/after)
- updated_count
- reboot_required
- timestamps

### 2.5 Orchestrator Layer (operations/orchestrator.py)

The orchestrator coordinates the entire run:

1. Load and validate inventory
2. Build execution plans
3. Iterate through hosts
4. Create sessions
5. Execute update pipeline
6. Write logs
7. Write per‑host summaries (JSON)
8. Return aggregated results

The orchestrator is the only component aware of the full lifecycle.

## 3. Execution Pipeline

Each host follows the same deterministic sequence:

1. Pre‑update list (count available updates)
2. Update execution
3. Post‑update list (count remaining updates)
4. Reboot detection
5. Summary generation
6. Logging

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
  debian-family:
    ubuntu:
      hosts:
        - address: nnn.nnn.nnn.nnn
          port: nn

Future enhancements include:

- schema versioning
- repo definitions
- GPG key imports
- host grouping and tags

## 5. PythonTools Integration

RunUpdates currently uses internal helper modules that will eventually be extracted into a standalone repository:

- command helpers
- parsing utilities
- SSH abstractions
- logging helpers

Once extracted, RunUpdates will import PythonTools as an external dependency.

## 6. Future Enhancements

Planned architectural improvements:

- concurrency limits for parallel execution
- pluggable execution backends (local, SSH, containerized)
- rollback hooks
- package‑level filtering
- optional read‑only diagnostics endpoints
- optional web dashboard (read‑only)

## 7. Summary

RunUpdates is designed to be:

- predictable
- auditable
- maintainable
- extensible
- operator‑grade

The architecture ensures that each component has a clear responsibility and that the entire execution pipeline remains deterministic and transparent.
