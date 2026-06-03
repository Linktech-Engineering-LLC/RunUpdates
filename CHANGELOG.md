# Changelog
All notable changes to **RunUpdates** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

* Path‑resolution model (resolve_paths) with CLI → ENV → dev‑mode → installed‑mode priority
* Documentation refinements (README, Architecture, Installation)
* Improved error messages for malformed inventories
* Clarified secrets model and environment variable behavior

### Planned

* Backend‑specific parsing for check output (zypper, dnf, apt)
* Structured JSON results for check
* Pre‑ and post‑update “list updates” capture
* Schema versioning
* Repo and GPG key management
* Parallel execution mode
* Expanded distro support (APT, DNF families)
* Nightly validation harness
* Structured error reporting

## [1.0.0] – 2026‑XX‑XX

### Added

* Deterministic lifecycle:
  `refresh → check → update? → clean → reboot?`
* New RunUpdatesInventoryLoader with:
  * YAML loading
  * schema validation
  * inheritance merging
  * vault merging
  * normalized host flattening
  * `raw_yaml` exposure for list operations
* Per‑host JSON summaries
* Final summary generation
* New orchestrator host‑selection model (CLI filtering only)
* Separation of raw vs normalized inventory
* PythonTools extracted into standalone micro‑library
* SSH + sudo execution via PythonTools
* Structured logging for all lifecycle stages

### Changed

* Removed InventoryProcessor (fully replaced by loader)
* Removed inventory flattening from orchestrator
* Removed self.proc and all references to it
* Clean now always runs, regardless of update status
* Updated secrets injection to explicit passing (no globals)
* Updated logging framework to use resolved paths
* Simplified orchestrator responsibilities (no inheritance logic, no flattening)

### Fixed

* Debug output corrected for multi‑host runs
* Normalized inventory consistently passed to orchestrator
* Improved validation for host entries (addresses, ports, enabled flags)

## [0.1.0] – 2026‑XX‑XX (Unreleased / Development Only)

### Added

* Initial project structure
* Early YAML‑driven inventory model
* Basic update execution pipeline
* SSH session handling and exit‑code mapping
* Initial logging framework
* Early documentation (README, Roadmap, Changelog)