# Changelog
All notable changes to **RunUpdates** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]
### Added
* Initial project structure and documentation
* YAML-driven inventory model (`hosts.yml`)
* Core execution pipeline for update orchestration
* SSH session handling and exit-code mapping
* Distro-specific update commands (openSUSE, Debian-family, RedHat-family)
* Debug mode for verbose execution tracing
* Logging framework for session lifecycle and command execution
* New RunUpdatesInventoryLoader with:
    * YAML loading
    * schema validation
    * inheritance merging
    * normalized host flattening
    * raw_yaml exposure for list operations
* New deterministic lifecycle:
  `refresh → check → update? → clean → reboot?`
* New path‑resolution model (resolve_paths)
* New logging initialization flow (paths + project name passed explicitly)
* New orchestrator host‑selection model (CLI filtering only)
* New separation of raw vs normalized inventory
* PythonTools extracted into a standalone micro‑library
* Updated README, Roadmap, and Architecture documentation

### Changed
* Removed InventoryProcessor (replaced by loader)
* Removed inventory flattening from orchestrator
* Removed self.proc and all references to it
* Updated orchestrator logging (Selected X hosts for processing)
* Clean now always runs, regardless of update status
* Simplified orchestrator responsibilities (no inheritance logic, no flattening)
* Updated secrets injection to explicit passing (no globals)
* Updated logging framework to use resolved paths

### Planned
* Backend‑specific parsing for check output:
    * zypper: patch + security counts
    * dnf: update table + advisories
    * apt: upgrade summary + security origins
* Structured JSON result for check operation
* Per‑host JSON summaries
* Pre‑ and post‑update “list updates” capture
* Schema versioning for inventory files
* Repo and GPG key management
* Parallel execution mode
* Nightly validation harness
* Structured error reporting
* Expanded distro support (APT, DNF families)

---

## [0.2.0] – 2026-XX-XX
### Added
- Backend-specific `check` operation parsing for openSUSE (zypper)
  - Extracts total patch count
  - Extracts security patch count
  - Provides internal structured results for orchestrator use
- New deterministic lifecycle:
  refresh → check → update? → clean → reboot?
- New `RunUpdatesInventoryLoader` with:
  - YAML loading
  - schema validation
  - inheritance merging
  - normalized host flattening
  - `raw_yaml` exposure for list operations
- Improved validation for host entries (addresses, ports, enabled flags)
- Updated documentation (README, Roadmap, Architecture)

### Changed
- Removed `InventoryProcessor` (fully replaced by loader)
- Removed inventory flattening from orchestrator
- Updated orchestrator logging (“Selected X hosts for processing”)
- Clean now always runs, regardless of update status
- Updated secrets handling to explicit passing (no global state)
- Updated logging initialization to use resolved paths
- Simplified orchestrator responsibilities (no inheritance logic, no flattening)
- Improved error messages for malformed inventories

### Fixed
- Incorrect references to `self.proc` removed
- Normalized inventory now consistently passed to orchestrator
- Debug output corrected for multi-host runs

### Planned (for v0.3.0+)
- Structured JSON results for `check` operation (public-facing)
- Per-host JSON summaries
- Pre- and post-update “list updates” capture
- Expanded backend support (APT, DNF families)
- Schema versioning for inventory files
- Repo and GPG key management
- Parallel execution mode

---

## [0.1.0] – 2026-XX-XX
### Added
- First public alpha release of RunUpdates
- Initial YAML-driven inventory model (`hosts.yml`)
- Basic update execution for supported distros (openSUSE, Debian-family, RedHat-family)
- SSH session handling and basic exit-code mapping
- Early orchestrator pipeline (refresh → check → update → clean → reboot)
- Initial logging framework (session lifecycle + command execution)
- Initial documentation set (README, Roadmap, Changelog)
