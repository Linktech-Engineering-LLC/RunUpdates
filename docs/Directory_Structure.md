# Directory Structure — RunUpdates

**Part of:** RunUpdates
**Document:** Directory Structure Reference
**Author:** Leon McClatchey, Linktech Engineering LLC
**License:** MIT
**Requires:** RunUpdates Source Tree
**Last Updated:** 2026-11-26

## Table of Contents
1. [Overview](#1-overview)
2. [Repository Overview](#2-repository-overview)
3. [Core Execution Engine](#3-core-execution-engine)
4. [Build & CI/CD Utilities](#4--build--cicd-utilities)
5. [Documentation Structure](#5-subsystem-documentation)
6. [Root-Level Documents](#6-rootlevel-documents)
7. [Reserved Directories](#7-future-directories-reserved)
8. [Summary](#8-summary)

---

## 1. Overview

This document describes the directory layout of the
RunUpdates repository.

It explains the purpose of each folder and file, how
components relate to one another, and the conventions
used throughout the project.

RunUpdates follows a deterministic, operator-grade
structure designed for clarity, maintainability, and
future expansion.

The repository is organized around explicit subsystem
boundaries. Each directory and file has a well-defined
responsibility and is intended to support deterministic,
auditable operation.

---

## 2. Repository Overview

The repository is organized into dedicated functional
areas.
```text
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
```

Each directory has a single, explicit responsibility.  
There are no hidden behaviors, no implicit defaults, and no auto‑generated structure.

---

## 3. Core Execution Engine

This directory contains the core logic of RunUpdates.  
Each module has a narrow, well‑defined responsibility.

```text
operations/
    selector.py
    connector.py
    executor.py
    orchestrator.py
    sessions.py
```

### 3.1 <selector.py>

Responsible for:
* loading and flattening the inventory  
* resolving family → distro → host relationships  
* validating host entries  
* building HostExecutionPlan objects  

### 3.2 <connector.py>

Responsible for:
* creating sessions  
* managing SSH connections  
* handling authentication  
* providing a unified interface for command execution  

### 3.3 <executor.py>

Responsible for:
* running distro‑specific update commands  
* running pre‑ and post‑update list commands  
* capturing exit codes and output  
* detecting reboot requirements  
* producing HostResult objects  

### 3.4 <orchestrator.py>

Responsible for:
* coordinating the entire update lifecycle  
* iterating through hosts  
* writing logs  
* writing per‑host summaries  
* returning aggregated results  

### 3.5 <sessions.py>

Defines:

* <SSHSession> (remote execution only)

Local execution is handled by PythonTools’ <sudo_run> and does not use a LocalSession class.

---

## 4.  Build & CI/CD Utilities

```text
scripts/
    build.py
```

This directory contains **only the scripts required for CI/CD.**

### 4.1 build.py

* A **copied** version of the canonical script in PythonTools
* Required by GitHub Actions (symlinks are not supported)
* Used exclusively for building RunUpdates
* Not part of the RunUpdates runtime architecture
* Not imported by RunUpdates
* No other scripts live here.

---

## 5. Subsystem Documentation

```text
docs/
    [Build.md](Build.md)
    [Design.md](Design.md)
    Directory_Structure.md - This Document
    [Error_Classification.md](Error_Classification.md)
    [Execution_Flow.md](Execution_Flow.md)
    [Inventory.md](Inventory.md)
    [Logging.md](Logging.md)
    [Operation.md](Operation.md)
    [PythonTools.md](PythonTools.md)
    [Schema_Reference.md](Schema_Reference.md)
    [Troubleshooting.md](Troubleshooting.md)
```

Each document focuses on a single aspect of the system.

| File | Purpose |
| --- | --- |
| **Build.md** | Build environment, toolchain requirements, and packaging workflow. |
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

Together, these documents provide a complete technical reference for the project.

---

## 6. Root‑Level Documents

These documents define the project’s identity, policies, and architecture.

### 6.1 [README.md](../README.md)
Provides:
* Project overview
* Feature summary
* Quick-start information
* Operator guidance

### 6.2 [CONTRIBUTING.md](../CONTRIBUTING.md)
Defines:
* Contribution procedures
* Coding standards
* Documentation requirements
* Review expectations

### 6.3 [CHANGELOG.md](../CHANGELOG.md)
Tracks:
* Releases
* Version history
* Notable changes

### 6.4 [SECURITY.md](../SECURITY.md)
Documents:
* Security expectations
* Vulnerability reporting procedures
* Secret-handling requirements

### 6.5 `main.py`
The primary application entry point.

Responsibilities include:
* CLI initialization
* Configuration processing
* Orchestrator startup
* Program termination handling

---

## 7. Future Directories (Reserved)

To avoid namespace collisions, the following directories are reserved for future expansion:

### 7.1 tests/

Reserved for:
* Unit tests
* Integration tests
* Validation workflows

### 7.2 examples/

Reserved for:
* Example inventories
* Demonstration configurations
* Safe reference environments

These directories may be introduced in future releases as project requirements evolve.

---

## 8. Summary

The RunUpdates directory structure is:

* explicit  
* deterministic  
* stable  
* operator‑grade  
* easy to navigate  

Each component has a clearly defined responsibility.

The layout is intentionally designed to support long-term maintainability, predictable behavior, audit-friendly operation, and future growth without introducing unnecessary complexity.