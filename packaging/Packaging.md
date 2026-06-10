# RunUpdates Packaging Guide

This document describes how to package RunUpdates for distribution, including:

* source tarballs (`.tar.gz` / `.zip`)
* frozen binary tarballs (`.tar.gz` / `.zip`)
* RPM packaging
* directory layout
* freeze rules
* environment expectations
* GitHub Actions workflows

RunUpdates supports both **source‑based** and **binary‑based** distribution
models. This guide covers all packaging paths.

For installation and configuration instructions, see **QuickStart.md**.  
For internal architecture, see **ARCHITECTURE.md**.

---

## 1. Packaging Overview

RunUpdates produces three types of distributable artifacts:

1. **Source Distribution**  
   A clean, versioned archive of the source tree.

2. **Frozen Distribution**  
   A PyInstaller‑based self‑contained binary tree.

3. **RPM Package**  
   For openSUSE, SLES, Fedora, and RHEL systems.

Each artifact serves a different operational environment:

| Artifact | Use Case |
|---------|----------|
| `.tar.gz` / `.zip` (source) | Developers, packagers, offline builds |
| `.tar.gz` / `.zip` (frozen) | Operators, air‑gapped systems, CI/CD |
| `.rpm` / `.deb` | Enterprise deployments, managed systems |

---

## 2. Directory Layout (Source, Frozen, RPM)

All packaging formats follow the same runtime layout:

**The installation root must be user‑writable.**  

The default installation root is:

$HOME/RunUpdates


Example:

/home/johndoe/RunUpdates


### Runtime Layout

$INSTALL_DIR/RunUpdates/        ← installation root
    bin/                        ← frozen executable
    lib/                        ← Python runtime + dependencies (frozen builds)
    etc/                        ← configuration directory
        hosts.yml               ← operator inventory (not packaged)
        schema/
            hosts.schema.yml    ← the only schema file
    var/
        logs/                   ← rotating logs
        logs/summaries/         ← per-host + per-run summaries
        run/                    ← PID file

### Key Rules

* `$INSTALL_DIR` **must be writable by the user.**
* `etc/` is created automatically in all packaged builds.
*  `schema/hosts.schema.yml` is always included.
* `hosts.yml` is never packaged.
* `var/logs`, `var/log/summaries`, and `var/run` must be writable.
* No system paths (`/opt`, `/usr/local`, `/usr`) may be used unless the admin explicitly overrides and ensures write permissions.

---

## 3. Source Distribution Packaging

Source distributions are provided as:

```code
runupdates-<version>.tar.gz
runupdates-<version>.zip
```

## 3.1 Included in Source Tarball

```code
RunUpdates/ (source)
schemata/
templates/
docs/
build.py
requirements.txt
setup.cfg / pyproject.toml (if present)
```

## 3.2 Excluded from Source Tarball

```code
etc/
var/
vault files
logs
summaries
__pycache__
```

## 3.3 Creating a Source Tarball

From the repository root:

```bash
git archive --format=tar.gz --prefix=runupdates-<version>/ -o runupdates-<version>.tar.gz HEAD
```

ZIP variant:

```bash
git archive --format=zip --prefix=runupdates-<version>/ -o runupdates-<version>.zip HEAD
```

## 4. Frozen Distribution Packaging

Frozen builds are created using PyInstaller and packaged as:

```code
runupdates-frozen-<version>-linux-x86_64.tar.gz
runupdates-frozen-<version>-linux-x86_64.zip
```

## 4.1 Freeze Rules

The frozen build must:

* include the RunUpdates source
* include PythonTools
* include all dependencies
* create required runtime directories:

```code
etc/
etc/schemata/
var/logs/
var/log/summaries/
var/run/
```

exclude:

```code
etc/hosts.yml
vault files
vault password files
logs
summaries
```

## 4.2 Creating a Frozen Tarball

After running PyInstaller:

```bash
tar -czf runupdates-frozen-<version>-linux-x86_64.tar.gz runupdates/
```

ZIP variant:
```bash
zip -r runupdates-frozen-<version>-linux-x86_64.zip runupdates/
```

## 4.3 Required Operator Steps After Extraction

Operators must:

1. Create /$HOME/RunUpdates/etc (if not present)
2. Copy hosts.yml
3. Ensure schema files exist in /$HOME/RunUpdates/etc/schemata/
4. Provide vault files via environment variables

## 5. RPM Packaging

The RPM package follows the same directory layout as frozen builds, but must
respect the **relocatable installation root.**

## 5.1 RPM Install Paths

Default prefix:

```Code
%{_buildroot}/home/%{username}/RunUpdates
```

Or admin‑selected prefix:

```Code
--prefix /srv/tools
```

## 5.2 RPM Scriptlets

%post

* create writable directories
* set permissions
* ensure correct ownership

%preun / %postun

* stop running instance if PID exists
* clean up temporary files

## 5.3 SELinux / AppArmor

If packaging for RHEL/Fedora/SLES:

* allow execution from `$INSTALL_DIR/RunUpdates/bin`
* allow writes to `$INSTALL_DIR/RunUpdates/var/logs`
* allow writes to `$INSTALL_DIR/RunUpdates/var/run`

## 6. Release Asset Naming Conventions

Recommended naming:

```code
runupdates-<version>.tar.gz
runupdates-<version>.zip
runupdates-frozen-<version>-linux-x86_64.tar.gz
runupdates-frozen-<version>-linux-x86_64.zip
runupdates-<version>-1.x86_64.rpm
runupdates-<version>-checksums.txt
```

## 7. Checksum Generation

Generate SHA256 checksums for all release assets:

```bash
sha256sum runupdates-* > runupdates-<version>-checksums.txt
```

## 8. GitHub Actions Release Workflow

A typical release workflow:

1. Checkout repository
2. Build source tarball
3. Build frozen binary
4. Build RPM and DEB
5. Generate checksums
6. Upload all artifacts to GitHub Release

### 8.1 Required Steps

1. install PythonTools
2. install requirements
3. run PyInstaller
4. create tarballs and zip archives
5. build RPM and DEB packages
6. generate checksums
7. upload artifacts

## 9. Packaging Constraints

### 9.1 Never Package Secrets

The following must never appear in any package:

* vault.yml
* vault password file
* operator inventory
* operator logs
* operator summaries

### 9.2 Never Package Host‑Specific Data

Packages must not include:

* hostnames
* IP addresses
* SSH keys
* credentials

### 9.3 Never Package Writable Files

Writable files must be created at install time, not build time.

## 10. Testing a Packaged Build

After installing a frozen or RPM build:

### 10.1 Create config directory

```bash
mkdir -p $HOME/RunUpdates/etc
```

### 10.2 Add inventory

```bash
cp hosts.yml $HOME/RunUpdates/etc/hosts.yml
```

### 10.3 Ensure schemata exists

```bash
ls $HOME/RunUpdates/etc/schemata
```

### 10.4 Provide vault files

```bash
export RUNUPDATES_VAULT_PATH=/secure/vault.yml
export RUNUPDATES_VAULT_PASSWORD_FILE=/secure/passfile
```

### 10.5 Run

```bash
/$HOME/RunUpdates/bin/RunUpdates update
```

## 11. Future Packaging Enhancements

Planned improvements:

* DEB packaging
* systemd service unit
* systemd timer for scheduled updates
* logrotate integration
* packaging tests in CI
* reproducible build metadata
* optional container image

## 12. Summary

This packaging guide ensures that RunUpdates builds are:

* deterministic
* reproducible
* operator‑grade
* secure
* free of secrets
* consistent across distros

Source tarballs, frozen tarballs, ZIP archives, and RPM packages all follow the same directory layout and runtime expectations, making RunUpdates predictable and easy to deploy in production.

