% RUNUPDATES-UPDATE(1)
% Linktech Engineering
% June 2026

# NAME
**RunUpdates update** — apply system updates to selected hosts

# SYNOPSIS
**RunUpdates update** 

\[GLOBAL OPTIONS\]

 

\[INVENTORY OPTIONS\]

 

\[TARGET SELECTION\]

 

\[EXECUTION OPTIONS\]



# DESCRIPTION
The **update** subcommand executes the full update lifecycle on one or more
hosts defined in the inventory. The lifecycle is determined by the distro
family and may include:

- refresh (optional)
- check
- update
- clean
- reboot (conditional)

RunUpdates uses **stdout‑based update detection**, allowing it to operate
uniformly across Debian, Ubuntu, RHEL, Rocky, Fedora, openSUSE, and others.

Update execution is logged, validated, and summarized for later inspection.

# OPTIONS

## Output Options
**--json**  
: Output results in JSON format. When writing to a TTY, JSON is pretty‑printed.

**--color**  
: Force colorized output. Color is automatically enabled when writing to a TTY.

## Target Selection
These options restrict which hosts receive updates:

**--family {linux}**  
: Restrict updates to the specified family.

**--distro DISTRO**  
: Restrict updates to the specified distro.

**-H**, **--host** *HOST*  
: Restrict updates to a specific host.

If no filters are provided, **all enabled hosts** in the inventory are updated.

## Execution Options
**--force**  
: Force update execution even if pre‑update checks fail.

**--mode {sequential,parallel,distro-parallel}**  
: Select orchestrator execution mode:  
  - **sequential** — update hosts one at a time  
  - **parallel** — update all hosts concurrently  
  - **distro-parallel** — update hosts in parallel per‑distro group

# GLOBAL OPTIONS
The following global options are accepted by all RunUpdates subcommands:

### Core Options
**-v**, **--verbose**  
: Enable verbose output.

**--dry-run**  
: Simulate actions without applying changes.

**-V**, **--version**  
: Show program version and exit.

### Logging Options
**--log-dir** *DIR*  
: Directory where logs are written.

**--log-max-mb** *MB*  
: Maximum size of a log file before rotation.

**--compress-archive**  
: Compress rotated logs.

**--delete-log**  
: Delete rotated logs instead of archiving.

**--archive-mode {tgz,zip}**  
: Archive format for rotated logs.

**--backup-count N**  
: Number of rotated archives to retain.

### Vault Options
**--vault-path FILE**  
: Path to an Ansible‑style vault file containing credentials.

**--vault-password-file FILE**  
: Path to a file containing the vault password.

### Config Options
**--config-dir DIR**  
: Override the configuration directory.

### Inventory Options
**-i**, **--inventory FILE**  
: Path to the inventory YAML file.

**--schema-dir DIR**  
: Override the schema directory.

# ENVIRONMENT
The following environment variables may influence update behavior:

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

# FILES
**inventory.yml**  
: Primary inventory file describing families, distros, and hosts.

**schema/inventory.schema.json**  
: JSON schema used to validate the inventory.

**schema/family.schema.json**  
: Schema for family‑level definitions.

**schema/distro.schema.json**  
: Schema for distro‑level definitions.

# EXIT STATUS
**0**  
: All updates completed successfully.

**1**  
: General error.

**2**  
: Inventory or schema validation failure.

**3**  
: One or more hosts encountered update errors.

**4**  
: One or more hosts require reboot.

# EXAMPLES

Update all enabled hosts:

`RunUpdates update`

Update only Debian hosts:

`RunUpdates update --distro debian`

Update a specific host:

`RunUpdates update --host ub25-desk-01`

Run updates in parallel:

`RunUpdates update --mode parallel`

Force updates even if checks fail:

`RunUpdates update --force`

Simulate updates without applying changes:

`RunUpdates update --dry-run`

Verbose update run:

`RunUpdates update --verbose`

# SEE ALSO
**RunUpdates(1)**,  
**runupdates-inventory(1)**,  
**runupdates-summary(1)**,  
**runupdates-config(5)**,  
**runupdates-inventory(5)**
