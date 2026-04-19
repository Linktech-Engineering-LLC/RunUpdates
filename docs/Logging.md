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

* **Deterministic** — logs always reflect the exact sequence of operations
* **Structured** — consistent formatting across all hosts and commands
* **Audit‑friendly** — timestamps, exit codes, and classifications are always present
* **Redacted** — secrets and sensitive data are never logged
* **Operator‑grade** — logs are readable, actionable, and suitable for incident review
* **Cross‑tool compatible** — consistent with NMS_Tools, VSCode-Updater, and future Linktech tools

Logging is not optional and not configurable — it is a core part of the system’s correctness model.

## 🧩 2. Logging Components

RunUpdates uses two layers:

1. RunUpdates LoggingFactory (project‑specific)

Responsible for:

* creating the logger
* setting log file paths
* formatting messages
* writing structured entries
* redacting sensitive fields

2. PythonTools Logging Interface (project‑agnostic)

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
* stdout (truncated if large)
* stderr
* classification (from YAML exit‑code model)

This ensures complete auditability.

## 🔐 6. Redaction Rules

RunUpdates never logs:

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

```python
logger.debug(...)
logger.info(...)
logger.warning(...)
logger.error(...)

logger.command_start(host, step, command)
logger.command_end(host, step, exit_code, classification)
logger.command_error(host, step, exit_code, stderr)
```

### PythonTools responsibilities:

call the logger at the correct times

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
RunUpdates typically writes logs to:

```Code
logs/
  runupdates-2026-04-19.log
```

Each run produces:

* a timestamped log file
* deterministic ordering
* one entry per command per host

Parallel execution (future) will preserve ordering per host.

## 🔮 10. Future Enhancements

* JSON log output (optional)
* structured event IDs
* parallel execution log grouping
* log streaming for UI integrations

PythonTools extraction into standalone library