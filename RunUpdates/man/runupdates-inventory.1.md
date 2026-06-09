% RUNUPDATES-INVENTORY(1)
% Linktech Engineering
% June 2026

# NAME
**RunUpdates inventory** — inspect inventory families, distros, hosts, and metadata

# SYNOPSIS
**RunUpdates inventory** 

\[GLOBAL OPTIONS\]

 

\[INVENTORY OPTIONS\]

 

\[FILTERS\]



# DESCRIPTION
The **inventory** subcommand inspects and displays information from the
RunUpdates inventory file. When invoked without additional listing flags,
it outputs the **fully resolved inventory**, including families, distros,
hosts, variables, commands, and metadata.

This makes:

`RunUpdates inventory`

the primary operator command for viewing the complete inventory.

# OPTIONS

## Output Options
**--json**  
: Output results in JSON format. When writing to a TTY, JSON is pretty‑printed.

**--color**  
: Force colorized output. Color is automatically enabled when writing to a TTY.

## Listing Options
**--list-families**  
: List all defined families.

**--list-distros**  
: List all distros under each family.

**--list-hosts**  
: List all hosts defined in the inventory.

**--list-inventory**  
: Output the fully resolved inventory (this is the default behavior).

**--show-metadata**  
: Display metadata fields for families, distros, and hosts.

## Filtering Options
**--family FAMILY**  
: Restrict output to a specific family.

**--distro DISTRO**  
: Restrict output to a specific distro.

**--host HOST**  
: Restrict output to a specific host.

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
**--log-dir DIR**  
: Directory where logs are written.

**--log-max-mb MB**  
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
  If omitted, RunUpdates loads:

**$RUNUPDATES_CONFIG/hosts.yml**

**--schema-dir DIR**  
: Override the schema directory.

# ENVIRONMENT
**RUNUPDATES_CONFIG**  
: Path to the configuration directory.

**RUNUPDATES_SCHEMA**  
: Path to the schema directory.

**RUNUPDATES_VAULT_PATH**  
: Path to the vault file.

**RUNUPDATES_VAULT_PASSWORD_FILE**  
: Path to the vault password file.

# FILES
**inventory.yml**  
: Primary inventory file describing families, distros, and hosts.

**schema/inventory.schema.json**  
: JSON schema used to validate the inventory.

# EXIT STATUS
**0**  
: Success.

**1**  
: General error.

**2**  
: Inventory or schema validation failure.

# EXAMPLES

Show the full resolved inventory (default behavior):

`RunUpdates inventory`

List all families:

`RunUpdates inventory --list-families`

List all distros:

`RunUpdates inventory --list-distros`

List all hosts:

`RunUpdates inventory --list-hosts`

Filter by family:

`RunUpdates inventory --family linux`

Filter by host:

`RunUpdates inventory --host Suse-Roll-01`

Development‑tree usage (when not installed):

`RunUpdates inventory --inventory ../etc/hosts.yml`

# SEE ALSO
**RunUpdates(1)**,  
**runupdates-update(1)**,  
**runupdates-summary(1)**,  
**runupdates-config(5)**,  
**runupdates-inventory(5)**
