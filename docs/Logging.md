# RunUpdates — Logging Architecture
RunUpdates uses a deterministic, operator‑grade logging model designed for audit transparency, reproducibility, and cross‑tool consistency.
Logging is intentionally explicit, structured, and free of hidden behavior.

This document describes:

* how logging works
* how PythonTools integrates with RunUpdates logging
* what is logged
* what is never logged
* how command execution is recorded
* how errors are classified and reported

## 🧱 1. Logging Philosophy

RunUpdates follows these principles:

* **Append Only** - log entries are never overwritten or deleted
* **Deterministic** — logs always reflect the exact sequence of operations
* **Structured** — consistent formatting across all hosts and commands
* **Audit‑friendly** — timestamps, exit codes, and classifications are always present
* **Redacted** — secrets and sensitive data are never logged
* **Operator‑grade** — logs are readable, actionable, and suitable for incident review
* **Cross‑tool compatible** — consistent with NMS_Tools, VSCode-Updater, and future Linktech tools

Logging is not optional and not configurable — it is a core part of the system’s correctness model.

## 🧩 2. Logging Components

RunUpdates uses two layers:

### 2.1 RunUpdates Logging Layer (project‑specific)
Responsible for:
* resolving log paths
* initializing the logger
* formatting messages
* writing structured entries
* redacting sensitive fields

RunUpdates fully controls logging behavior.

### 2.2 PythonTools Logging Interface (project‑agnostic)

Responsible for:
* receiving an injected logger
* providing _NullLogger fallback
* exposing a minimal logging API
* never initializing logging itself

PythonTools does not know:
* where logs are stored
* how logs are formatted
* what the project’s logging policy is

RunUpdates controls all of that.

## 🔌 3. Logger Injection Model
At startup, RunUpdates injects its logger into PythonTools:

```python
from PythonTools.logging import set_logger
set_logger(runupdates_logger)
```

This ensures:

* all local commands (sudo_run)
* all remote commands (SSHSession.run)
* all helpers

…log through the same unified interface.

**PythonTools never initializes logging.**
It only uses what RunUpdates provides.

## 🧰 4. _NullLogger Fallback
If RunUpdates does not inject a logger (e.g., during testing), PythonTools uses _NullLogger.

_NullLogger characteristics:

* implements .debug(), .info(), .warning(), .error()
* implements .command_start(), .command_end(), .command_error()
* all methods are no‑ops
* produces zero output

This ensures PythonTools is safe to use in:

* unit tests
* standalone scripts
* early development
* environments without logging

## 🛠 5. Command Logging Model
Every command executed by RunUpdates is logged with:

### Command Start

```Code
[2026-04-19 14:55:12] [host=Lab-Suse-01] [step=check] START: zypper refresh && zypper patch-check --with-optional
```

### Command End

```Code
[2026-04-19 14:55:13] [host=Lab-Suse-01] [step=check] END: exit_code=101 classification=patches_available
```

### Command Error

```Code
[2026-04-19 14:55:13] [host=Lab-Suse-01] [step=check] ERROR: exit_code=255 stderr="SSH connection failed"
```

### Captured Fields

* timestamp
* host
* step (check/refresh/update/clean/reboot)
* command string
* exit code
* stdout (Stdout is truncated to prevent log bloat and ensure logs remain readable and diff‑friendly.)
* stderr
* classification (from YAML exit‑code model)

This ensures complete auditability.

### Note on Summaries

Per‑host summaries are planned, but not yet implemented.
Operator logs are currently the authoritative record of execution.

## 🔐 6. Redaction Rules

RunUpdates **never logs**:

* passwords
* sudo prompts
* SSH authentication failures containing sensitive text
* private key contents
* vault file contents
* raw secrets
* environment variables containing secrets

If a command contains a password (rare), it is redacted before logging.

## 📦 7. Logging in PythonTools

PythonTools exposes a minimal logging API:

```Python
logger.debug(...)
logger.info(...)
logger.warning(...)
logger.error(...)

logger.command_start(host, step, command)
logger.command_end(host, step, exit_code, classification)
logger.command_error(host, step, exit_code, stderr)
```

### PythonTools responsibilities:

* call the logger at the correct times
* pass structured data
* never format messages itself
* never write files
* never store logs

### RunUpdates responsibilities:

* define formatting
* define log file location
* define rotation policy
* define redaction rules

This separation keeps PythonTools reusable and clean.

## 🧪 8. Error Logging

Errors are logged deterministically:

### Connection Errors

```Code
ERROR: SSH connection failed (timeout)
```

### Command Errors

```Code
ERROR: exit_code=1 stderr="zypper: repository not found"
```

### Inventory Errors

```Code
ERROR: Missing required field: packages.update
```

### Secrets Errors

```Code
ERROR: No valid authentication method available
```

Errors never stop the pipeline unless they occur before execution begins.

## 🧭 9. Log File Structure

RunUpdates writes logs to a stable, non‑timestamped log file:

Code

```Code
logs/
  runupdates.log
```

This file is append‑only and persists across runs.

### Log Rotation and Archival
Timestamped log files are **only created when logs are archived**.

Archived logs use date‑only filenames in the format:

`logs/archive/runupdates-YYYYMMDD.log`

Examples:

`runupdates-20260522.log`
`runupdates-20260523.log`

This ensures:
* deterministic naming
* clean daily grouping
* predictable sorting
* consistency with other Linktech Engineering tools

RunUpdates does not currently perform automatic rotation; archival support is planned for a future release.

### Determinism Guarantees
* Each run appends to the same active log file
* Archived logs preserve the exact state of the file at the time of rotation
* Ordering is strictly chronological
* No log entries are overwritten

Parallel execution (future) will preserve ordering per host, even if cross‑host interleaving occurs.

### Parallel Execution Ordering Guarantees

When parallel execution is introduced, RunUpdates will maintain strict ordering **per host**.  
Even if multiple hosts run concurrently, each host’s log entries will remain internally ordered and deterministic.  
Cross‑host interleaving may occur, but never within a single host’s sequence.


## 🔮 10. Future Enhancements

* JSON log output (optional)
* structured event IDs
* parallel execution log grouping
* log streaming for UI integrations
