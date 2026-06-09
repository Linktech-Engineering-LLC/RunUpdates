% RUNUPDATES-CONFIG(5)
% Linktech Engineering
% June 2026

# NAME
**RunUpdates configuration** — configuration directory layout, environment files, and schema definitions

# SYNOPSIS
RunUpdates uses a structured configuration directory containing environment
files, schema definitions, and runtime paths. This page documents the
layout and purpose of each file and directory.

# DESCRIPTION
RunUpdates loads its configuration from a directory specified by:

- the `--config-dir` command‑line option, or  
- the `RUNUPDATES_CONFIG` environment variable, or  
- the default installation path:

`/$INSTALL_DIR/RunUpdates/etc`

The configuration directory contains:

- `.env` files used by systemd, cron, and shell environments  
- JSON schema definitions for validating the inventory  
- runtime configuration files created during packaging  
- optional vault configuration for credentials  

This page describes the structure and purpose of each component.

# DIRECTORY LAYOUT

A typical installation layout looks like:

```
/$INSTALL_DIR/RunUpdates/
                    ├── etc/
                    │   ├── hosts.yml
                    │   ├── systemd.env
                    │   ├── cron.env
                    │   ├── bash.env
                    │   └── schema/
                    │       ├── inventory.schema.json
                    │       ├── family.schema.json
                    │       └── distro.schema.json
                    └── var/
                    └── log/
                    ├── runupdates.log
                    └── summaries/
```

# CONFIGURATION FILES

## hosts.yml
The primary inventory file describing:

- families  
- distros  
- hosts  
- variables  
- commands  
- exit codes  

This file is validated against the JSON schemas in `schema/`.

See **runupdates-inventory(5)** for full details.

## systemd.env
Environment file used by systemd units. Typically contains:

```
RUNUPDATES_CONFIG=$INSTALL_DIR/RunUpdates/etc
RUNUPDATES_SCHEMA=$INSTALL_DIR/RunUpdates/etc/schema
RUNUPDATES_LOG_DIR=$INSTALL_DIR/RunUpdates/var/log
```

## cron.env
Environment file used by cron jobs. Contains the same variables as
`systemd.env`, but formatted for cron execution.

## bash.env
Environment file for interactive shell usage. Operators may source this
file to ensure consistent paths when running RunUpdates manually.

# SCHEMA DIRECTORY

The `schema/` directory contains JSON schema definitions used to validate
the inventory structure.

## inventory.schema.json
Validates the top‑level inventory file (`hosts.yml`), including:

- family definitions  
- distro definitions  
- host definitions  
- variable inheritance rules  

## family.schema.json
Validates the structure of each family block.

## distro.schema.json
Validates the structure of each distro block.

# LOG DIRECTORY

RunUpdates writes logs and summary files to:

`/$INSTALL_DIR/RunUpdates/var/log`

This directory contains:

- `runupdates.log` — main log file  
- rotated logs (compressed or deleted depending on settings)  
- `summaries/` — JSON summary files from update runs  

The log directory may be overridden with:

--log-dir DIR
RUNUPDATES_LOG_DIR

# VAULT INTEGRATION

RunUpdates **requires** an Ansible‑style vault file for credentials.  
The vault is not optional; runs will fail if vault configuration is missing
or invalid.

Relevant options:


``--vault-path`` FILE
``--vault-password-file`` FILE

Relevant environment variables:

RUNUPDATES_VAULT_PATH
RUNUPDATES_VAULT_PASSWORD_FILE


The vault file contains encrypted credentials; the password file provides
the decryption key used at runtime.

# ENVIRONMENT VARIABLES

The following variables influence configuration loading:

**RUNUPDATES_CONFIG**  
: Path to the configuration directory.

**RUNUPDATES_SCHEMA**  
: Path to the schema directory.

**RUNUPDATES_LOG_DIR**  
: Path to the log directory.

**RUNUPDATES_VAULT_PATH**  
: Path to the vault file.

**RUNUPDATES_VAULT_PASSWORD_FILE**  
: Path to the vault password file.

# VAULT PERMISSION REQUIREMENTS

RunUpdates enforces strict security requirements on both the vault file and
the vault password file. These checks occur before any inventory loading or
update execution. If any requirement is not met, RunUpdates aborts with a
permission error.

## Required Permissions

### Vault file (e.g., vault.yml)
- Must exist
- Must be a regular file
- Must be owned by the current user
- Must have permissions **0600**
- The containing directory must have permissions **0700** or stricter

### Vault password file
- Must exist
- Must be a regular file
- Must be owned by the current user
- Must have permissions **0600**
- The containing directory must have permissions **0700** or stricter

These rules follow the same security model used by OpenSSH and GnuPG.

## Example of correct permissions

chmod 600 $INSTALL_DIR/RunUpdates/etc/vault.yml
chmod 600 $INSTALL_DIR/RunUpdates/etc/vault-password.txt
chmod 700 $INSTALL_DIR/RunUpdates/etc


## Example of incorrect permissions (RunUpdates will refuse to run)

```bash
-rw-r--r--  vault.yml        # world-readable
-rw-rw-r--  vault-password   # group-readable
drwxr-xr-x  etc/             # directory readable by others
```

## Failure Behavior

If permissions are incorrect, RunUpdates will:

1. Log a clear error message  
2. Raise a `VaultPermissionError`  
3. Abort execution before decrypting or loading anything  

Vault security is mandatory. RunUpdates will not operate without a valid,
secure vault configuration.

# SEE ALSO
**RunUpdates(1)**,  
**runupdates-inventory(1)**,  
**runupdates-update(1)**,  
**runupdates-summary(1)**,  
**runupdates-inventory(5)**
