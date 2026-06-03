# RunUpdates Roadmap

## Current Phase

**Status:** Active Development
RunUpdates 1.0.0 provides a stable execution pipeline, a normalized inventory model, and a reliable SSH/local execution layer via PythonTools.
The next phase focuses on backend intelligence, structured output, and expanded validation.

## Near‑Term Goals (1.1.x Series)

### Backend Check Parsing

Implement backend‑specific parsing for update availability:

* **zypper**
  * total patch count
  * security patch count
  * repo health indicators

* **dnf**
  * advisories
  * update table parsing
  * security classifications

* **apt**
  * upgrade summary
  * security origins
  * held packages

Deliverables:
* Unified structured result for the check stage
* Improved exit‑code classification consistency across backends

### Core Functionality Enhancements

* Implement dry‑run mode (no remote execution, validation only)
* Improve error handling and deterministic failure states
* Expand structured logging (session lifecycle, command execution, exit‑code mapping)
* Add support for non‑standard SSH ports at the distro or host level

### Inventory & Validation

* Strengthen validation for host entries (addresses, ports, enabled flags)
* Add optional host tags (grouping, roles, metadata)
* Improve debug output for multi‑host runs

### Documentation

* Add schema documentation for hosts.yml
* Add troubleshooting section (SSH, permissions, exit codes)
* Add backend‑specific examples (openSUSE, Debian-family, RedHat-family)

## Mid‑Term Goals (1.2.x – 1.3.x)

### Inventory Model Evolution
* Add schema versioning
* Add migration path for older inventories
* Add richer host metadata (tags, roles, groups)

### Repository & Key Management
* Add support for importing vendor GPG keys
* Add repo definitions to hosts.yml
* Add lifecycle ordering:
  `import keys → add repos → refresh → update`

### Structured Output & Summaries

Enhance per‑host summaries to include:
* parsed check results
* advisory/security metadata
* repo health indicators
* update counts

Add optional fleet‑level summary for dashboards and monitoring systems.

### Execution Enhancements
* Add dry‑run diff output (planned vs actual operations)
* Add pre‑ and post‑update “list updates” capture
* Add parallel execution mode with concurrency limits
* Improve reboot classification across distros

### Testing & Validation
* Add nightly validation harness
* Add multi‑host test matrix (Debian, Ubuntu, openSUSE, RedHat-family)
* Add mock SSH backend for local testing

## Long‑Term Goals (1.x and Beyond)

### PythonTools Integration
* Continue stabilizing PythonTools as a standalone micro‑library
* Expand PythonTools session layer (timeouts, retries, diagnostics)
* Ensure consistent consumption across RunUpdates, BotScanner, TimerDeck, and future tools

### Architecture & Extensibility
* Add pluggable execution backends (local, SSH, containerized)
* Add rollback hooks for supported distros
* Add package‑level filtering (security updates only, kernel only, etc.)

### Ecosystem & Integration
* Optional web dashboard for update status visualization (read‑only)
* Optional diagnostics endpoints (read‑only)
* Structured summary files for external dashboards

### Future Research
* Evaluate support for Windows hosts (PowerShell remoting)
* Evaluate container‑based update execution for isolated testing
* Explore package‑level dependency graph visualization
* Investigate optional REST API for read‑only fleet status