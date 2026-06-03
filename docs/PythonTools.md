# PythonTools — Shared Execution Layer

PythonTools is a standalone, reusable execution library that provides deterministic,
cross‑platform command execution for multiple Linktech Engineering tools. It is not
an internal component of RunUpdates; instead, RunUpdates depends on PythonTools as
its execution layer.

PythonTools provides:

* a unified execution model
* local privileged execution ([sudo_run])
* non‑privileged local execution ([local_command])
* remote execution via [SSHSession]
* injected logging
* injected secrets
* reusable helpers (in progress)

PythonTools is intentionally project‑agnostic. It does not know anything about:

* YAML
* inventory structure
* distro models
* exit‑code interpretation
* orchestration logic

RunUpdates, BotScanner, and future tools inject everything PythonTools needs.

## 🧱 1. Purpose

PythonTools exists to provide a **deterministic, minimal, operator‑grade execution layer** that can be shared across multiple tools without duplication.

Its goals:
* predictable execution
* consistent return structures
* clean separation of concerns
* safe logging and secret handling
* portability across projects

## 🧩 2. Design Principles

### Deterministic

Execution results are predictable, structured, and stable.

### Minimal

No unnecessary dependencies, no magic behavior, no hidden state.

### Project‑agnostic

PythonTools never imports downstream tools or knows anything about their configuration.

### Injectable

Logging and secrets are provided externally.

### Extractable

The module is maintained as an independent micro‑library.

## 🔌 3. Logging Integration

PythonTools does **not** initialize logging.
It receives a logger from the downstream tool:

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

### _NullLogger Fallback

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
Downstream tools inject them:

```python
from PythonTools.secrets import set_secrets
set_secrets(secrets_dict)
```

Typical secrets:

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

### A. Local Execution — [local_command]

Runs a command without privilege escalation.

```python
result = local_command("ls -la")
```

Used for:
* non‑privileged operations
* environment checks
* local diagnostics

### B. Local Privileged Execution — [sudo_run]

Runs a command with sudo using the injected password.

```python
result = sudo_run("zypper refresh")
```

Characteristics:
* password is passed securely
* password is never logged
* stdout/stderr/exit_code are captured
* deterministic return structure

### C. Remote Execution — [SSHSession]

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

**Authentication Model**

* keyfile → primary
* password → fallback

**Responsibilities**

* connection lifecycle
* command execution
* stdout/stderr capture
* exit‑code retrieval
* error normalization
* logging hooks

SSHSession converts transport‑level failures (timeouts, handshake errors, DNS failures) into deterministic PythonTools exceptions so downstream tools can classify them consistently.

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

PythonTools truncates stdout to a fixed length to prevent log bloat.
Truncation length is fixed in code and not user‑configurable.

This allows downstream tools to remain distro‑agnostic and inventory‑agnostic.

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

These will be added as they stabilize.

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

PythonTools is upstream; downstream tools must not fork or modify it.

## 🔮 9. Distribution & Versioning

PythonTools is maintained as a standalone micro‑library inside its own repository.
It is not published to PyPI or any external package index.

### 📦 Local Installation

After cloning the repository:

```bash
pip install -e .
```

This installs PythonTools into the active virtual environment in editable mode, allowing downstream tools (RunUpdates, BotScanner, etc.) to import it normally:

```python
import PythonTools
```

### 📁 Repository Layout
Code
PythonTools/
  python_tools/
    logging.py
    secrets.py
    sessions.py
    commands.py
    helpers/

### 🔢 Versioning

PythonTools uses a simple internal version number stored in the repository.
Downstream tools should treat PythonTools as an upstream dependency but must not fork or modify it.

### 🔗 Integration with RunUpdates

RunUpdates treats PythonTools as a black‑box dependency. It imports only the public interfaces ([local_command], [sudo_run], [SSHSession], and the logger/secrets injectors) and never references internal folders such as [core], [net], or [utils].
During development, RunUpdates should keep PythonTools installed in editable mode ([pip install -e .]) so updates propagate automatically.
Once PythonTools stabilizes, RunUpdates can pin a version in its pyproject.toml to ensure compatibility.
