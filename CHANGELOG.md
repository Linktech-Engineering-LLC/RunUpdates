# Changelog
All notable changes to **RunUpdates** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]
### Added
- Initial project structure and documentation
- YAML-driven inventory model (`hosts.yml`)
- Core execution pipeline for update orchestration
- SSH session handling and exit-code mapping
- Distro-specific update commands (openSUSE, Debian-family, RedHat-family)
- Debug mode for verbose execution tracing
- Logging framework for session lifecycle and command execution

### Planned
- Per-host summary generation (JSON)
- Pre- and post-update “list updates” capture for package counts
- Reboot-required detection per distro
- Schema versioning for inventory files
- Dry-run mode for validation without execution
- Inventory traversal improvements (family → distro → hosts)
- Repo and GPG key management
- Nightly validation harness
- Structured error reporting

---

## [0.1.0] – 2026-XX-XX
### Added
- First public alpha release of RunUpdates
- Basic update execution for supported distros
- Initial documentation set (README, Roadmap, Changelog)
