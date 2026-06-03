# RunUpdates — Architecture & Design
RunUpdates is a deterministic, operator‑grade update orchestrator for Linux hosts.
Its design emphasizes reproducibility, clarity, and audit‑friendly execution across heterogeneous environments.

This document describes the internal architecture, execution model, inventory system, and integration with PythonTools.

## 🧱 1. Architectural Overview
RunUpdates is composed of five primary subsystems:

`
main.py
 └── UpdateOrchestrator
      ├── InventoryProcessor
      ├── HostSelector
      ├── HostConnector
      │     ├── local (sudo_run)
      │     └── SSHSession
      └── HostExecutor
`

For a detailed explanation of the repository layout, see
[Directory_Structure](Directory_Structure.md)

### Subsystem Responsibilities

| Component | Responsibility |
|-----------|----------------|
| InventoryProcessor | Loads, validates, and flattens the YAML inventory |
| HostSelector | Determines which hosts should run based on CLI filters |
| HostConnector | Chooses local vs remote execution and initializes sessions |
| HostExecutor | Runs the deterministic update pipeline for each host |
| PythonTools | Provides execution primitives, session layer, and logging injection |

### SSHSession Behavior

SSHSession implements a two‑stage authentication model:
1. Keyfile authentication (preferred)
2. Password authentication (fallback) using sudo_user + sudo_pass

This ensures RunUpdates can operate even if key‑based authentication is unavailable.


## ⚙️ 2. Execution Model

RunUpdates uses a unified execution model built on PythonTools.

For a step‑by‑step breakdown of the update pipeline, see
[Execution_Flow](Execution_Flow.md)

### 2.1 Local Execution
Local commands run through:

`sudo_run(command)`

Characteristics:

* Uses the injected sudo password
* Redacts sensitive data from logs
* Provides deterministic return structure
* No LocalSession class is used

### 2.2 Remote Execution
Remote commands run through:

`SSHSession.run(command)`

### 2.3 Authentication Model
SSHSession uses a two‑stage strategy:

#### Primary: Keyfile Authentication 

If [keyfile] exists and is readable:
* SSHSession authenticates using the private key
* SSH user is implicitly root
* No password is used

#### Fallback: Password Authentication 

If keyfile authentication is unavailable:
* SSHSession authenticates using:
  
  `
  ssh_user = sudo_user
  ssh_password = sudo_pass
  `
* This allows RunUpdates to operate even without key‑based auth

### 2.4 Sudo Behavior

If the SSH user is not root:
* Commands requiring privilege escalation use:
  
  `
  sudo -S <command>
  `
* sudo_pass is used for stdin‑based sudo authentication

### 2.5 Unified Return Structure

Both local and remote execution return:
```Python
{
  "stdout": "...",
  "stderr": "...",
  "exit_code": 0,
  "ok": True/False
}
```

## 📦 3. Inventory & YAML Model

RunUpdates uses a declarative YAML inventory that defines:

* distro families
* package manager commands
* exit‑code interpretation
* host lists
* connection parameters

For the full YAML schema and validation rules, see
[Schema_Reference](Schema_Reference.md)
For examples and contributor guidance, see
[Inventory](Inventory.md)

### 3.1 Inventory Hierarchy

`
family
 └── distro
       ├── packages
       │     ├── commands
       │     └── exit_codes
       └── hosts
`

### 3.2 Flattening Model

InventoryProcessor merges:

* family defaults
* distro defaults
* host overrides

…into a single deterministic host object.

### 3.3 Deterministic Host Object Example

```yaml
host:
  name: web01
  family: opensuse
  distro: opensuse-leap
  packages:
    check: "zypper patch-check --with-optional"
    refresh: "zypper refresh"
    update: "zypper up -y"
    clean: "zypper clean"
  exit_codes:
    check:
      up_to_date: [0]
      patches_available: [101]
      error: ["*"]
  connection:
    hostname: web01.example.com
    port: 22
    keyfile: ~/.ssh/runupdates
    sudo_user: root
    sudo_pass: REDACTED
```

### 3.4 Determinism Rules

* No implicit defaults
* No environment‑dependent behavior
* No randomization
* All behavior must be defined in YAML

## 🧩 4. Distro Model & Exit‑Code Interpretation

For deterministic error categories and classification rules, see
[Error_Classification](Error_Classification.md)
Each distro defines:

### Repo Health Detection  

RunUpdates analyzes stderr from the distro’s check command to detect repository metadata failures.
If repo metadata cannot be retrieved, the host is marked repo_broken and updates are skipped unless [--force] is used.

### 4.1 Commands

```yaml
packages:
  check: "zypper refresh && zypper patch-check --with-optional"
  refresh: "zypper refresh"
  update: "zypper up -y"
  clean: "zypper clean"
```

### 4.2 Exit Codes

```yaml
exit_codes:
  check:
    up_to_date: [0]
    patches_available: [101]
    error: ["*"]
```

### 4.3 Interpretation Rules

* The **command key** (e.g., check) must match the exit‑code key
* "*" matches any unspecified exit code
* HostExecutor uses the exit‑code map to classify results deterministically

### 4.4 Universal Stdout‑Based Update Detection

RunUpdates includes a distro‑agnostic fallback:
* If stdout contains indicators like "upgradable" or "updates available"
* HostExecutor classifies the host as having updates

This ensures consistent behavior across distros without requiring custom commands.

## 🚀 5. Deterministic Update Pipeline

Each host runs the following steps:

1. check
2. refresh
3. update
4. clean
5. reboot (optional)

### 5.1 Pipeline State Machine

`CHECK → REFRESH → UPDATE → CLEAN → REBOOT (optional)`

Rules:

* Each step produces a deterministic classification
* Failures never abort the pipeline
* All transitions are logged
* No hidden failures
* No swallowed exceptions

## 🔐 6. Secrets Model

RunUpdates receives its secrets from an external vault.

```Yaml
runupdates:
  keyfile: "~/.ssh/runupdates"
  sudo_user: "root"
  sudo_pass: "CHANGE_ME"
```

### Rules:

* If [keyfile] exists → SSH uses keyfile auth as root.
* If [keyfile] is missing → SSH uses [sudo_user] + [sudo_pass].
* sudo_pass is also used for <sudo -S>
* Secrets are never logged.
* Secrets are injected into PythonTools at startup.


## 🧰 7. PythonTools Integration

PythonTools provides:

* <sudo_run>
* <local_command>
* <SSHSession>
* injected logging
* injected secrets
* reusable helpers (in progress)

### 7.1 Design Constraints

PythonTools must remain:

* project‑agnostic
* YAML‑agnostic
* inventory‑agnostic
* logging‑agnostic
* secrets‑agnostic

RunUpdates injects everything PythonTools needs.

### 7.2 Import Rules

* PythonTools must never import RunUpdates
* RunUpdates may import PythonTools
* No circular imports allowed

## 🧪 8. Error Handling & Logging

RunUpdates uses an operator‑grade logging model:

* structured logs
* timestamps
* command start/end events
* redacted secrets
* deterministic error classification

For the complete logging event model and redaction rules, see
[Logging](Logging.md)

PythonTools uses:

* injected logger
* _NullLogger fallback
* no internal logging initialization

For integration details and shared execution primitives, see
[PythonTools](PythonTools.md)

This ensures consistent behavior across all tools in the suite.


## 🖥️ 9. CLI Modes & Execution Flags

RunUpdates supports the following modes:

* --dry-run
  * Executes pipeline logic without running commands
* header audit
  * Audits headers across the repo
* --wait-for-reboot
  * Waits for host to return after reboot

## 🧑‍💻 10. Developer Tooling Model

RunUpdates uses two helper scripts during development:

| Script | Purpose | Canonical Home | In Repo |
| --- | --- | --- | --- |
| **build.py** | Build Python projects; used by CI/CD | PythonTools/scripts | **Copied** (required for GitHub Actions) |

Rules:

* GitHub Actions cannot follow cross‑repo symlinks → build.py must be copied
* Canonical versions always live in PythonTools

## 🛠 11. Future Work

* Add secrets injection to PythonTools
* Add reusable helpers to PythonTools
* Expand distro support
* Add inventory validation schema
* Add parallel execution (optional)

For troubleshooting and recovery procedures, see
[Troubleshooting](Troubleshooting.md)