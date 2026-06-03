# RunUpdates — Directory Structure

This document describes the directory layout of the RunUpdates repository.  
It explains the purpose of each folder and file, how components relate to one another, and the conventions used throughout the project.

RunUpdates follows a deterministic, operator‑grade structure designed for clarity, maintainability, and future expansion.

---

## 1. Repository Overview

RunUpdates/
    operations/
    scripts/
    docs/
    main.py
    README.md
    DESIGN.md
    ARCHITECTURE.md
    CONTRIBUTING.md
    CHANGELOG.md
    SECURITY.md


Each directory has a single, explicit responsibility.  
There are no hidden behaviors, no implicit defaults, and no auto‑generated structure.

---

## 2. <operations/> — Core Execution Engine

This directory contains the core logic of RunUpdates.  
Each module has a narrow, well‑defined responsibility.

operations/
    selector.py
    connector.py
    executor.py
    orchestrator.py
    sessions.py

### 2.1 <selector.py>

Responsible for:
* loading and flattening the inventory  
* resolving family → distro → host relationships  
* validating host entries  
* building HostExecutionPlan objects  

### 2.2 <connector.py>

Responsible for:
* creating sessions  
* managing SSH connections  
* handling authentication  
* providing a unified interface for command execution  

### 2.3 <executor.py>

Responsible for:
* running distro‑specific update commands  
* running pre‑ and post‑update list commands  
* capturing exit codes and output  
* detecting reboot requirements  
* producing HostResult objects  

### 2.4 <orchestrator.py>

Responsible for:
* coordinating the entire update lifecycle  
* iterating through hosts  
* writing logs  
* writing per‑host summaries  
* returning aggregated results  

### 2.5 <sessions.py>

Defines:

* <SSHSession> (remote execution only)

Local execution is handled by PythonTools’ <sudo_run> and does not use a LocalSession class.

---

## 3. <scripts/> — Build & CI/CD Utilities

`
scripts/
    build.py
`

This directory contains **only the scripts required for CI/CD.**

### 3.1 build.py

* A **copied** version of the canonical script in PythonTools
* Required by GitHub Actions (symlinks are not supported)
* Used exclusively for building RunUpdates
* Not part of the RunUpdates runtime architecture
* Not imported by RunUpdates
* No other scripts live here.

---

## 4. <docs/> — Subsystem Documentation

docs/
    Design.md
    Directory_Structure.md
    Error_Classification.md
    Execution_Flow.md
    Inventory.md
    Logging.md
    Operation.md
    PythonTools.md
    Schema_Reference.md
    Troubleshooting.md

Each document focuses on a single aspect of the system.

| File | Purpose |
| --- | --- |
| **Design.md** | Core architectural and subsystem design — the authoritative technical overview. |
| **Directory_Structure.md** | Repository layout and file responsibility map. |
| **Error_Classification.md** | Defines deterministic error categories and logging behavior. |
| **Execution_Flow.md** | Describes the update pipeline sequence (check → refresh → update → clean → reboot). |
| **Inventory.md** | Documents YAML inventory format, hierarchy, and flattening rules. |
| **Logging.md** | Specifies structured logging, redaction, and event sequencing. |
| **Operation.md** | Operator‑grade usage guide — how to run, interpret results, and handle reboots. |
| **PythonTools.md** | Integration notes for the shared PythonTools layer (sudo_run, SSHSession, etc.). |
| **Schema_Reference.md** | Formal YAML schema reference for validation and contributor guidance. |
| **Troubleshooting.md** | Diagnostic procedures, common failure modes, and recovery steps. |

---

# 5. Root‑Level Documents

These documents define the project’s identity, policies, and architecture.

### 5.1 `README.md`
High‑level overview, quickstart, and operator guidance.

### 5.2 `ARCHITECTURE.md`
Describes the internal structure and design principles.

### 5.3 `CONTRIBUTING.md`
Defines contribution rules, coding standards, and schema stability.

### 5.4 `CHANGELOG.md`
Tracks version history and notable changes.

### 5.5 `SECURITY.md`
Defines security expectations, reporting procedures, and safe handling of secrets.

### 5.6 `main.py`
Entry point for the CLI.

---

# 6. Future Directories (Reserved)

To avoid namespace collisions, the following directories are reserved for future expansion:

tests/             (unit and integration tests)
examples/          (safe placeholder inventories)


These directories may be introduced in future releases.

---

# 7. Summary

The RunUpdates directory structure is:

- explicit  
- deterministic  
- stable  
- operator‑grade  
- easy to navigate  

Each component has a clear purpose, and the layout is designed to support long‑term maintainability and future growth.
