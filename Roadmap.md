# RunUpdates Roadmap

## Current Phase
**Status**: Active Development
RunUpdates now has a stable execution pipeline, a normalized inventory model, and a reliable SSH/local session layer via PythonTools.
The current focus is expanding backend support, improving observability, and preparing for structured output in the next release.
---

## Near‑Term Goals (Pre‑Release)

### Check Operation Enhancements

* Add backend‑specific parsing for update availability:
  * **zypper**: extract total + security patch counts
  * **dnf**: detect update table + advisories
  * **apt**: parse upgrade summary + security origins
* Return a unified structured result to the orchestrator
* Improve exit‑code classification consistency across backends

### Core Functionality
- Finalize the `hosts.yml` schema for distro blocks  
- Add support for shared package blocks (e.g., `debian-family`)  
- Implement dry‑run mode for safe validation  
- Expand structured logging (session lifecycle, command execution, exit‑code mapping)  
- Improve error handling and deterministic failure states  

### Inventory & Execution
* Finalize normalized inventory structure
* Improve validation for host entries (addresses, ports, enabled flags)
* Improve debug output for multi‑host runs
* Add support for non‑standard SSH ports at the distro or host level
* Add optional tags for host grouping (planned)

### Documentation
* Update README with corrected lifecycle
* Add schema documentation for hosts.yml
* Add troubleshooting section for SSH, permissions, and exit codes
* Add backend‑specific examples (openSUSE, Debian-family, RedHat-family)

---

## Mid‑Term Goals (Architecture & Features)

### Inventory Model Evolution
* Add schema versioning for future compatibility
* Add migration path for older inventories
* Add richer host metadata (tags, roles, groups)

### Repository & Key Management
- Add support for importing vendor GPG keys (including Linktech Engineering key)  
- Add repo definitions to `hosts.yml`  
- Add lifecycle ordering: import keys → add repos → refresh → update  

### Structured Output & Summaries
* Add per‑host JSON summaries
* Include:
  * refresh/check/update/clean/reboot results
  * exit codes + classifications
  * timestamps
  * update counts (once parsing is implemented)
* Add optional machine‑readable fleet summary

### Execution Enhancements
* Add dry‑run diff output (planned vs actual operations)
* Add pre‑ and post‑update “list updates” capture
* Add parallel execution mode with concurrency limits
* Improve reboot classification across distros

### Testing & Validation
* Add nightly validation harness
* Add multi‑host test matrix (Debian, Ubuntu, openSUSE, RedHat-family)
* Add mock SSH backend for local testing

---

## Long‑Term Goals (v1.0 and Beyond)

### Release Milestones
- Publish RunUpdates v0.9 (feature‑complete beta)  
- Publish RunUpdates v1.0 (stable release)  

### PythonTools Integration
* Continue stabilizing PythonTools as a standalone micro‑library
* Ensure RunUpdates, BotScanner, TimerDeck, and future tools consume PythonTools consistently
* Expand PythonTools session layer (timeouts, retries, diagnostics)

### Architecture & Refactoring
- Export PythonTools into its own standalone repository once the API surface stabilizes  
- Update RunUpdates to import PythonTools as an external dependency  

### Integration & Ecosystem
* Add optional web dashboard for update status visualization (read‑only)
* Provide structured per‑host summary files for dashboards and monitoring systems
* Evaluate optional read‑only diagnostics endpoints (no remote execution)

### Advanced Features
- Add rollback hooks for supported distros  
- Add package‑level filtering (security updates only, kernel only, etc.)  
- Add host grouping and tag‑based execution  
- Add pluggable execution backends (local, SSH, containerized)  

---

## Future Research
- Evaluate support for Windows hosts (PowerShell remoting)  
- Evaluate container‑based update execution for isolated testing  
- Explore package‑level dependency graph visualization  
- Investigate optional REST API for read‑only fleet status
