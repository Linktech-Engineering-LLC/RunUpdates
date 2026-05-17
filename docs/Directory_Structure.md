# RunUpdates — Directory Structure

This document describes the directory layout of the RunUpdates repository.  
It explains the purpose of each folder and file, how components relate to one another, and the conventions used throughout the project.

RunUpdates follows a deterministic, operator‑grade structure designed for clarity, maintainability, and future expansion.

---

# 1. Repository Overview

RunUpdates/
operations/
inventory/
docs/
main.py
README.md
ARCHITECTURE.md
CONTRIBUTING.md
CHANGELOG.md
SECURITY.md


Each directory has a single, explicit responsibility.  
There are no hidden behaviors, no implicit defaults, and no auto‑generated structure.

---

# 2. `operations/` — Core Execution Engine

This directory contains the core logic of RunUpdates.  
Each module has a narrow, well‑defined responsibility.

operations/
selector.py
connector.py
executor.py
orchestrator.py
sessions.py


### 2.1 `selector.py`
Responsible for:

- loading and flattening the inventory  
- resolving family → distro → host relationships  
- validating host entries  
- building HostExecutionPlan objects  

### 2.2 `connector.py`
Responsible for:

- creating sessions  
- managing SSH connections  
- handling authentication  
- providing a unified interface for command execution  

### 2.3 `executor.py`
Responsible for:

- running distro‑specific update commands  
- running pre‑ and post‑update list commands  
- capturing exit codes and output  
- detecting reboot requirements  
- producing HostResult objects  

### 2.4 `orchestrator.py`
Responsible for:

- coordinating the entire update lifecycle  
- iterating through hosts  
- writing logs  
- writing per‑host summaries  
- returning aggregated results  

### 2.5 `sessions.py`
Defines:

- `LocalSession`  
- `SSHSession`  

Both expose:

run(command) → (exit_code, stdout, stderr)

---

# 3. `inventory/` — Sample Inventories and Templates

inventory/
sample-inventory.yaml


This directory contains:

- example inventory files  
- placeholder‑only templates  
- reference structures for contributors  

No real addresses, ports, or usernames are ever stored here.

---

# 4. `docs/` — Subsystem Documentation

docs/
Logging.md
Schema_Reference.md
Execution_Flow.md
Directory_Structure.md


This directory contains detailed subsystem documentation that supports:

- contributors  
- maintainers  
- future tooling integrations  

Each document focuses on a single aspect of the system.

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

python_tools/      (external dependency once extracted)
tests/             (unit and integration tests)
examples/          (safe placeholder inventories)
scripts/           (developer utilities)


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
