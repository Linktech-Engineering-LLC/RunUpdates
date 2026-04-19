# RunUpdates — Architecture & Design
RunUpdates is a deterministic, operator‑grade update orchestrator for Linux hosts.
Its design emphasizes reproducibility, clarity, and audit‑friendly execution across heterogeneous environments.

This document describes the internal architecture, execution model, inventory system, and integration with PythonTools.

## 🧱 1. Architectural Overview
RunUpdates is composed of five primary subsystems:

```
main.py
 └── UpdateOrchestrator
      ├── InventoryProcessor
      ├── HostSelector
      ├── HostConnector
      │     ├── local (sudo_run)
      │     └── SSHSession
      └── HostExecutor
```

### Subsystem Responsibilities

| Component | Responsibility |
|-----------|----------------|
| InventoryProcessor | Loads, validates, and flattens the YAML inventory |
| HostSelector | Determines which hosts should run based on CLI filters |
| HostConnector | Chooses local vs remote execution and initializes sessions |
| HostExecutor | Runs the deterministic update pipeline for each host |
| PythonTools | Provides execution primitives, session layer, and logging injection |
| InventoryProcessor |	Loads, validates, and flattens the YAML inventory |
| HostSelector |	Determines which hosts should run based on CLI filters |
| HostConnector |	Chooses local vs remote execution and initializes sessions |
| HostExecutor |	Runs the deterministic update pipeline for each host |
| PythonTools |	Provides execution primitives, session layer, and logging injection |

## ⚙️ 2. Execution Model

RunUpdates uses a unified execution model built on PythonTools.

### Local Execution

Local commands run through:

```code
sudo_run(command)
```

Characteristics:

* Uses the injected sudo password
* Redacts sensitive data from logs
* Provides deterministic return structure
* No LocalSession class is used

### Remote Execution

Remote commands run through:

```code
SSHSession.run(command)
```

Authentication model:

1. keyfile (preferred)
2. password (fallback)

SSHSession is responsible for:

* connection lifecycle
* command execution
* stdout/stderr capture
* exit‑code retrieval
* error normalization

### Unified Return Structure

Both local and remote execution return:

```python
{
  "stdout": "...",
  "stderr": "...",
  "exit_code": 0,
  "ok": True/False
}
```

This allows HostExecutor to remain distro‑agnostic.

## 📦 3. Inventory & YAML Model

RunUpdates uses a declarative YAML inventory that defines:

* distro families
* package manager commands
* exit‑code interpretation
* host lists
* connection parameters

### Inventory Hierarchy

```Code
family
 └── distro
       ├── packages
       │     ├── commands
       │     └── exit_codes
       └── hosts
```

### Flattening Model

InventoryProcessor merges:

* family defaults
* distro defaults
* host overrides

…into a single deterministic host object.

## 🧩 4. Distro Model & Exit‑Code Interpretation

Each distro defines:

### Commands

```yaml
packages:
  check: "zypper refresh && zypper patch-check --with-optional"
  refresh: "zypper refresh"
  update: "zypper up -y"
  clean: "zypper clean"
```

### Exit Codes

```yaml
exit_codes:
  check:
    up_to_date: [0]
    patches_available: [101]
    error: ["*"]
```

### Interpretation Rules

* The **command key** (e.g., check) must match the exit‑code key
* "*" matches any unspecified exit code
* HostExecutor uses the exit‑code map to classify results deterministically

This allows RunUpdates to support:

* openSUSE
* RedHat
* Ubuntu
* future distros

…without modifying Python code.

## 🚀 5. Deterministic Update Pipeline

Each host runs the following steps:

1. check
2. refresh
3. update
4. clean
5. reboot (optional)

Each step:

* runs the distro‑defined command
* interprets exit codes via YAML
* logs stdout/stderr
* never hides failures
* never stops the overall run

This ensures predictable, audit‑friendly behavior.

## 🔐 6. Secrets Model

Secrets are injected at startup and include:

```yaml
username: "ssh username"
password: "optional ssh + sudo password"
keyfile: "/path/to/private/key"
```

Rules:

* At least one authentication method must be available
* Password is used for both SSH fallback and sudo
* Secrets are never logged

Secrets are injected into PythonTools, not stored internally

## 🧰 7. PythonTools Integration

PythonTools provides:

* sudo_run
* local_command
* SSHSession
* injected logging
* injected secrets
* reusable helpers (in progress)

PythonTools is currently internal to RunUpdates but will eventually be extracted into a standalone Linktech Engineering library.

### Design Constraints

PythonTools must remain:

* project‑agnostic
* YAML‑agnostic
* inventory‑agnostic
* logging‑agnostic
* secrets‑agnostic

RunUpdates injects everything PythonTools needs.

## 🧪 8. Error Handling & Logging

RunUpdates uses an operator‑grade logging model:

* structured logs
* timestamps
* command start/end events
* redacted secrets
* deterministic error classification

PythonTools uses:

* injected logger
* _NullLogger fallback
* no internal logging initialization

This ensures consistent behavior across all tools in the suite.

## 🛠 9. Future Work

* Extract PythonTools into standalone repo
* Add secrets injection to PythonTools
* Add reusable helpers to PythonTools
* Expand distro support
* Add inventory validation schema
* Add parallel execution (optional)
