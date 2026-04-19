# RunUpdates — Operation Guide
This document describes the runtime behavior of RunUpdates, including host selection, connection logic, command execution, exit‑code interpretation, logging, and error handling.
It reflects the current architecture using PythonTools, sudo_run, and SSHSession.

## 🧭 1. Overview
RunUpdates executes a deterministic update pipeline across one or more Linux hosts.
Each host is processed independently using:

* a flattened inventory object
* a unified execution model
* a YAML‑driven distro command set
* a YAML‑driven exit‑code interpretation model
* injected secrets and logging

The orchestrator ensures predictable, audit‑friendly behavior regardless of distro or environment.

## 🧩 2. Inventory Processing
The inventory is loaded and normalized by InventoryProcessor.

### Flattening Rules

For each host:

1. Family defaults
2. Distro defaults
3. Host overrides

…are merged into a single deterministic object:

```python
{
  "family": "linux",
  "distro": "opensuse",
  "address": ["192.168.0.67"],
  "port": 2222,
  "packages": {...},
  "exit_codes": {...},
  "enabled": true
}
```

This flattened host object is passed to HostSelector, HostConnector, and HostExecutor.

## 🎯 3. Host Selection
Host selection is performed by HostSelector, based on CLI filters:

* --family
* --distro
* --host
* --list-* operations

Rules:

* Disabled hosts are skipped
* Hosts must match all provided filters
* If no filters are provided, all enabled hosts run

Dry‑run mode (--dry-run) still performs selection but does not execute commands.

## 🔌 4. Connection Model (HostConnector)
HostConnector determines whether a host is executed locally or remotely.

### Local Execution
Triggered when:

* the host address matches localhost, 127.0.0.1, or the machine’s own IP
* OR the host explicitly sets local: true

Local commands use:

```Code
sudo_run(command)
```

### Remote Execution

Triggered when:

* the host has an address list
* OR the host is not local

Remote commands use:

```Code
SSHSession(address, port, username, keyfile, password)
```

### Authentication Rules

1. keyfile → primary SSH authentication
2. password → fallback SSH authentication
3. password → sudo password for privileged commands

If no authentication method is available, the host is marked as failed before execution begins.

## 🛠 5. Execution Pipeline (HostExecutor)

Each host runs the following deterministic sequence:

1. check
2. refresh
3. update
4. clean
5. reboot (optional)

Commands are defined in the inventory under:

```yaml
packages:
  check: ...
  refresh: ...
  update: ...
  clean: ...
  reboot: ...
```

### Execution Rules

* Commands are executed in order
* Each command is logged before and after execution
* Failures do not stop the pipeline
* stdout, stderr, and exit code are captured
* Exit codes are interpreted using the YAML model

If --dry-run is enabled, commands are printed but not executed.

## 📦 6. YAML‑Driven Exit‑Code Interpretation

Each distro defines exit‑code behavior:

```yaml
exit_codes:
  check:
    up_to_date: [0]
    patches_available: [101]
    error: ["*"]
```

### Interpretation Rules

* The command key (e.g., check) must match the exit‑code key
* Lists define explicit matches
* "*" matches any unspecified exit code
* The first matching category is used
* Categories are passed to the orchestrator for reporting

**Example**

If check returns exit code 101:

* patches_available matches
* HostExecutor logs the classification
* The pipeline continues normally

If exit code is unrecognized:

* "*" → error
* The error is logged
* The pipeline continues

This ensures deterministic behavior across distros.

## 🧰 7. PythonTools Integration

RunUpdates uses PythonTools for all command execution.

### Local Execution

```python
result = sudo_run(command)
```

### Remote Execution

```python
session = SSHSession(address, port, username, keyfile, password)
result = session.run(command)
```

### Return Structure

Both local and remote execution return:

```python
{
  "stdout": "...",
  "stderr": "...",
  "exit_code": 0,
  "ok": True/False
}
```

### Logging & Secrets

* PythonTools receives an injected logger
* PythonTools receives injected secrets
* PythonTools never initializes logging
* PythonTools never loads YAML
* PythonTools never stores secrets

This keeps the execution layer reusable and project‑agnostic.

## 📜 8. Logging Behavior

RunUpdates uses an operator‑grade logging model:

### Logged for each command

* timestamp
* host
* command name
* command string
* exit code
* stdout
* stderr
* classification (from exit‑code model)

### Redaction Rules

* passwords
* sudo prompts
* SSH authentication failures
* sensitive inventory fields

…are never logged.

### PythonTools Logging

PythonTools uses:

* injected logger
* _NullLogger fallback if none is provided

## 🧪 9. Error Handling
RunUpdates is designed to be deterministic and resilient.

### Command Errors

If a command fails:

* the error is logged
* the exit‑code classification is applied
* the pipeline continues

### Connection Errors

If SSHSession cannot connect:

* the host is marked as failed
* the pipeline is skipped
* the error is logged

### Inventory Errors

If the inventory is invalid:

* RunUpdates exits before execution
* errors are printed with context

## 🚦 10. Dry‑Run Mode

Dry‑run mode prints:

* selected hosts
* commands that would run
* connection type (local/remote)
* no commands are executed
* no SSH connections are made

This is ideal for validation and audit review.

## 🔮 11. Future Enhancements

* parallel execution
* richer exit‑code categories
* inventory schema validation
* PythonTools extraction into standalone repo

additional distro support