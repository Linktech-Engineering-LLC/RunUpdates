# PythonTools — Shared Execution Layer for RunUpdates
PythonTools is the internal execution library used by RunUpdates to provide deterministic, cross‑platform command execution.
It abstracts local and remote execution, logging, secrets, and session management behind a clean, reusable interface.

PythonTools is currently embedded inside RunUpdates for rapid iteration, but it is architected to become a standalone Linktech Engineering micro‑library in the future.

## 🧱 1. Purpose

PythonTools provides:

* a unified execution model
* local privileged execution (sudo_run)
* non‑privileged local execution (local_command)
* remote execution via SSHSession
* injected logging
* injected secrets
* reusable helpers (in progress)

PythonTools is intentionally project‑agnostic.
It does not know anything about:

* YAML
* inventory structure
* distro models
* exit‑code interpretation
* RunUpdates orchestration logic

RunUpdates injects everything PythonTools needs.

## 🧩 2. Design Principles
PythonTools follows the same operator‑grade philosophy as the rest of the Linktech Engineering Tools Suite:

### Deterministic
Execution results are predictable and structured.

### Minimal
No unnecessary dependencies, no magic behavior.

### Project‑agnostic
No RunUpdates imports, no YAML parsing, no inventory logic.

### Injectable
Logging and secrets are provided externally.

### Extractable
The module can be moved into its own repo with minimal changes.

## 🔌 3. Logging Integration
PythonTools does **not** initialize logging.
It receives a logger from RunUpdates:

```python
from PythonTools.logging import set_logger
set_logger(runupdates_logger)
```

### Logging API
PythonTools uses a minimal, structured API:

```python
logger.debug(...)
logger.info(...)
logger.warning(...)
logger.error(...)

logger.command_start(host, step, command)
logger.command_end(host, step, exit_code, classification)
logger.command_error(host, step, exit_code, stderr)
```
`_NullLogger` **Fallback**
If no logger is injected:

* _NullLogger is used
* all methods are no‑ops
* no output is produced

This ensures PythonTools is safe in:

* unit tests
* standalone scripts
* early development environments

## 🔐 4. Secrets Injection
PythonTools does not load or validate secrets.
RunUpdates injects them:

```python
from PythonTools.secrets import set_secrets
set_secrets(secrets_dict)
```

Secrets typically include:

```yaml
username: "ssh username"
password: "optional ssh + sudo password"
keyfile: "/path/to/private/key"
```

PythonTools uses secrets only for:

* SSH authentication
* sudo password injection

PythonTools never logs secrets and never stores them beyond runtime.

## 🛠 5. Execution Primitives
PythonTools provides two local execution paths and one remote execution path.

### A. Local Execution — local_command
Runs a command without privilege escalation.

```python
result = local_command("ls -la")
```

Used for:

* non‑privileged operations
* environment checks
* local diagnostics

### B. Local Privileged Execution — sudo_run
Runs a command with sudo using the injected password.

```python
result = sudo_run("zypper refresh")
```

Characteristics:

* Password is passed securely
* password is never logged
* stdout/stderr/exit_code are captured
* deterministic return structure

### C. Remote Execution — SSHSession
PythonTools provides a full SSH session abstraction:

```python
session = SSHSession(
    address="192.168.0.67",
    port=2222,
    username="admin",
    keyfile="/path/to/key",
    password="fallback"
)

result = session.run("zypper up -y")
```

### Authentication Model

* keyfile → primary
* password → fallback

### Responsibilities

* connection lifecycle
* command execution
* stdout/stderr capture
* exit‑code retrieval
* error normalization
* logging hooks

## 📦 6. Return Structure
All execution functions return the same deterministic structure:

```python
{
  "stdout": "...",
  "stderr": "...",
  "exit_code": 0,
  "ok": True/False
}
```

This allows RunUpdates to remain distro‑agnostic and inventory‑agnostic.

## 🧰 7. Helpers (Current + Planned)

### Current

* _NullLogger
* logging injection
* secrets injection
* SSH session management
* local command wrappers

### Planned

* network helpers (host_exists, is_ip_address)
* OS helpers (is_linux, is_root)
* command helpers (shlex_split_safe)
* file helpers (read_text, write_text)

These will be moved from RunUpdates into PythonTools once stabilized.

## 🧭 8. Boundaries & Non‑Responsibilities

PythonTools must not:

* load YAML
* interpret exit codes
* understand distros
* manage inventory
* initialize logging
* store secrets
* define orchestration logic
* define update pipelines

These belong to RunUpdates.

## 🔮 9. Future Extraction Plan
PythonTools will eventually become a standalone repo:

```Code
PythonTools/
  python_tools/
    logging.py
    secrets.py
    sessions.py
    commands.py
    helpers/
```

Published as:

```Code
pip install python-tools-linktech
```

Used by:

* RunUpdates
* BotScanner
* future Linktech tools

Extraction will occur once:

* logging API is stable
* secrets model is stable
* helpers are consolidated
* session layer is finalized