% RUNUPDATES(1)
% Linktech Engineering
% June 2026

# NAME
**RunUpdates** — manage system patches and updates across multiple hosts

# SYNOPSIS
**RunUpdates** 

\[GLOBAL OPTIONS\]

 <command> 

\[ARGS\]



# DESCRIPTION
**RunUpdates** is a universal, distro‑agnostic update orchestration tool.  
It manages package updates across heterogeneous Linux environments using a
single inventory, a unified schema, and a consistent execution model.

RunUpdates does **not** rely on distro‑specific APIs.  
Instead, it uses **stdout‑based update detection**, allowing it to operate
uniformly across Debian, Ubuntu, RHEL, Rocky, Fedora, Arch, and others.

This man page describes the top‑level command.  
See the individual subcommand man pages for detailed usage.

# COMMANDS
The following subcommands are available:

**version**  
: Show version information.

**help**  
: Show help for a subcommand.

**inventory**  
: Inspect inventory families, distros, hosts, and metadata.

**update**  
: Apply updates to selected hosts.

**summary**  
: Display summary information from previous runs.

# GLOBAL OPTIONS

## Core Options
**-v**, **--verbose**  
: Enable verbose output.

**--dry-run**  
: Simulate actions without applying changes.

**-V**, **--version**  
: Show program version and exit.

## Logging Options
**--log-dir** *DIR*  
: Directory where logs are written.

**--log-max-mb** *MB*  
: Maximum size of a log file before rotation (default: 5 MB).

**--compress-archive**  
: Compress rotated logs (default: true).

**--delete-log**  
: Delete rotated logs instead of archiving (default: true).

**--archive-mode** *{tgz,zip}*  
: Archive format for rotated logs (default: zip).

**--backup-count** *N*  
: Number of rotated archives to retain (default: 7).

## Vault Options
**--vault-path** *FILE*  
: Path to an Ansible‑style vault file containing credentials.

**--vault-password-file** *FILE*  
: Path to a file containing the vault password.

## Config Options
**--config-dir** *DIR*  
: Override the configuration directory.

## Inventory Options
**-i**, **--inventory** *FILE*  
: Path to the inventory YAML file.

**--schema-dir** *DIR*  
: Override the schema directory.

# ENVIRONMENT
RunUpdates may read the following environment variables:

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

These variables are typically populated by the installed `.env` files:
`systemd.env`, `cron.env`, or `bash.env`.

# FILES
**/opt/RunUpdates/etc/**  
: Default configuration directory.

**/opt/RunUpdates/etc/schema/**  
: JSON schema definitions for inventory validation.

**/opt/RunUpdates/var/log/**  
: Default log directory.

**inventory.yml**  
: Host inventory file describing families, distros, and hosts.

# EXIT STATUS
**0**  
: Success.

**1**  
: General error.

**2**  
: Inventory or schema validation failure.

**3**  
: Update execution failure.

# EXAMPLES

Show version:

`RunUpdates version`

Display inventory information:

`RunUpdates inventory 

Run updates in dry‑run mode:

`RunUpdates update --dry-run`

Show summary of previous runs:

`RunUpdates summary`


# SEE ALSO
**runupdates-inventory(1)**,  
**runupdates-update(1)**,  
**runupdates-summary(1)**,  
**runupdates-config(5)**,  
**runupdates-inventory(5)**
