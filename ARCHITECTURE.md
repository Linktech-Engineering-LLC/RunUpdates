# RunUpdates Architecture

RunUpdates is a deterministic, YAML‑driven update orchestrator for Linux hosts.
Its architecture emphasizes clarity, reproducibility, and operator‑grade behavior.

This document describes the internal structure of RunUpdates, the execution pipeline, and the responsibilities of each component.

## 1. Design Principles

RunUpdates is built around:
* **Deterministic execution** — no hidden behavior, no implicit defaults
* **Explicit configuration** — all behavior originates from hosts.yml
* **Minimal dependencies** — PythonTools + standard libraries
* **Structured logging** — predictable, machine‑readable output
* **Separation of concerns** — each module has a single responsibility
* **Audit‑friendly operation** — logs and summaries reflect exactly what happened

## 2. High‑Level Architecture

RunUpdates is composed of five primary layers, executed in this order:

Code
```
Inventory → Orchestrator → Selector → Connector → Executor
```

Each layer transforms structured input into structured output, with no side effects outside its scope.

### 2.1 Inventory Loader (inventory/loader.py)

The **RunUpdatesInventoryLoader** is responsible for:
* loading hosts.yml
* schema validation
* inheritance merging
* vault merging
* normalization into flattened host entries

It produces two representations:
* raw_yaml — used for list operations
* normalized — used for orchestration

**Note**: The schema structure and validation flow are stable, but the schema files themselves will continue to expand as distro models and check‑parsing features mature.

#### Key Behaviors

* address is always normalized to a list
* vault secrets override inventory fields
* family/distro/host inheritance is deterministic
* validation is strict and fail‑fast

The loader fully replaces the old InventoryProcessor.

### 2.2 Orchestrator ([operations/orchestrator.py])

The orchestrator coordinates the entire run:
1. Receive normalized inventory
2. Select hosts
3. Create sessions
4. Execute lifecycle
5. Collect per‑host results
6. Write final summary
7. Return aggregated status

#### Final Summary (Implemented)

The orchestrator writes:

Code
```
summary.json
```

containing:
* run start/end
* duration
* total hosts
* completed
* failed
* skipped
* repo_broken
* reboot_required
* per‑host status map

**Orchestrator Does NOT:**
* flatten inventory
* merge inheritance
* run commands directly

It is a clean, minimal coordinator.

### 2.3 Selector (operations/selector.py)

Responsible for:
* filtering normalized hosts based on CLI arguments
* validating that selected hosts exist
* returning a list of host execution targets

The selector operates **only** on normalized data.

It does **not**:
* merge inheritance
* perform vault operations
* modify host definitions

### 2.4 Connector (operations/connector.py)

Responsible for establishing execution sessions.

RunUpdates uses PythonTools for all execution primitives.

#### Local Execution
Uses:

Code
```
PythonTools.sudo_run
```
There is **no LocalSession class**.

#### Remote Execution
Uses:

Code
```
PythonTools.SSHSession
```
SSHSession is fully provided by PythonTools.

#### Unified Interface

Both local and remote execution expose:

```python
session.run(command) → (exit_code, stdout, stderr)
```

The executor does not know or care whether the session is local or remote.

#### Connector Responsibilities

* choose local vs remote session
* initialize the session
* log connection lifecycle
* return a ready‑to‑use session object

### 2.5 Executor (operations/executor.py)

Responsible for running the deterministic lifecycle:

Code
```
refresh → check → update? → clean → reboot detection
```

The executor:
* runs distro‑defined commands
* interprets exit codes
* detects reboot requirements
* logs each stage
* records lifecycle events
* writes per‑host summaries

#### Per‑Host Summary (Implemented)

After all stages complete, the executor writes:

Code
```
<hostname>.json
```

containing:
* lifecycle status
* update status
* repo health
* exit codes
* stdout/stderr
* timestamps
* reboot requirement
* lifecycle events

This is not “planned” — it is fully implemented.

## 3. Execution Pipeline

Each host follows the same deterministic sequence:
1. refresh
2. check
3. exit‑code interpretation
  * backend‑specific parsing (future)
4. update (only if needed)
5. clean
6. reboot detection
7. per‑host summary

### Not Yet Implemented (Future)

* pre‑update list
* post‑update list
* update count diffing

These remain roadmap items.

## 4. Inventory Model

The inventory supports a hierarchical model:

```yaml
linux:
  opensuse:
    hosts:
      sample-node:
        address: ["192.0.2.10"]
        port: 2222
```

The loader merges:
* family defaults
* distro defaults
* host overrides
* vault secrets

…into normalized host entries.

### Current Behavior

* openSUSE Leap and Tumbleweed share the opensuse distro
* splitting them requires only inventory changes, not code changes

### Future Enhancements

* schema versioning
* repo definitions
* GPG key imports
* host grouping and tags

## 5. PythonTools Integration

RunUpdates uses PythonTools as its execution substrate:
* [sudo_run] for privileged local execution
* [local_command] for non‑privileged local execution
  * local_command is available in PythonTools but is not used by RunUpdates today.
* [SSHSession] for remote execution
* structured logging injection
* secrets injection
* consistent return structures

PythonTools is a standalone micro‑library shared across:
* RunUpdates
* BotScanner
* TimerDeck
* future tools

RunUpdates relies on PythonTools for all execution‑layer behavior.

## 6. Future Enhancements

Planned architectural improvements:
* backend‑specific check parsing
* pre/post list operations
* concurrency limits for parallel execution
* rollback hooks
* package‑level filtering
* pluggable execution backends
* optional diagnostics endpoints
* optional web dashboard (read‑only)

## 7. Summary

RunUpdates is designed to be:
* predictable
* auditable
* maintainable
* extensible
* operator‑grade

The architecture ensures that each component has a clear responsibility and that the entire execution pipeline remains deterministic and transparent.
