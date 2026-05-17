# RunUpdates Roadmap

## Current Phase
**Status:** Under Construction  
RunUpdates is in active development, focused on building a deterministic, YAML‑driven update orchestration engine for Linux hosts. The priority is establishing a stable execution pipeline, consistent inventory model, and reliable SSH session handling.

---

## Near‑Term Goals (Pre‑Release)

### Core Functionality
- Finalize the `hosts.yml` schema for distro blocks  
- Add support for shared package blocks (e.g., `debian-family`)  
- Implement dry‑run mode for safe validation  
- Expand structured logging (session lifecycle, command execution, exit‑code mapping)  
- Improve error handling and deterministic failure states  

### Inventory & Execution
- Normalize inventory traversal logic  
- Add validation for host entries (addresses, ports, enabled flags)  
- Improve Debug mode output for multi‑host runs  
- Add support for non‑standard SSH ports at the distro or host level  

### Documentation
- Add README examples for openSUSE, Debian-family, and RedHat-family  
- Add schema documentation for `hosts.yml`  
- Add troubleshooting section for SSH, permissions, and exit codes  

---

## Mid‑Term Goals (Architecture & Features)

### Inventory Model Evolution
- Introduce full family hierarchy:  
  `linux → family → distro → hosts`  
- Add migration path for existing flat inventories  
- Add schema versioning for future compatibility  

### Repository & Key Management
- Add support for importing vendor GPG keys (including Linktech Engineering key)  
- Add repo definitions to `hosts.yml`  
- Add lifecycle ordering: import keys → add repos → refresh → update  

### Execution Enhancements
- Add dry‑run diff output (planned vs actual operations)  
- Add per‑host execution summaries (JSON)  
- Add pre‑ and post‑update “list updates” capture for package counts  
- Add parallel execution mode with concurrency limits  

### Testing & Validation
- Add nightly validation harness  
- Add multi‑host test matrix (Debian, Ubuntu, openSUSE, RedHat-family)  
- Add mock SSH backend for local testing  

---

## Long‑Term Goals (v1.0 and Beyond)

### Release Milestones
- Publish RunUpdates v0.9 (feature‑complete beta)  
- Publish RunUpdates v1.0 (stable release)  

### Architecture & Refactoring
- Export PythonTools into its own standalone repository once the API surface stabilizes  
- Update RunUpdates to import PythonTools as an external dependency  

### Integration & Ecosystem
- Establish PythonTools as a shared library for future Linktech Engineering projects  
- Ensure RunUpdates, BotScanner, and future tools can consume PythonTools consistently  
- Add optional web dashboard for update status visualization (read‑only)  
- Provide structured per‑host summary files (JSON) to enable external tools, dashboards, or monitoring systems to consume RunUpdates results without requiring direct integration  
- Evaluate optional read‑only diagnostics endpoints (no remote execution, no control surface)  

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
