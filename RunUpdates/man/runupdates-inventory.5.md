% RUNUPDATES-INVENTORY(5)
% Linktech Engineering
% June 2026

# NAME
**RunUpdates inventory format** — specification for families, distros, hosts, variables, commands, and inheritance

# SYNOPSIS
The RunUpdates inventory is a YAML file describing families, distros, and
hosts. It defines update commands, variables, exit‑code rules, metadata,
and vault‑integrated credentials. This page documents the complete format.

# DESCRIPTION
The inventory file (`hosts.yml`) defines the update model for all managed
systems. It is validated against JSON schemas located in:

/$INSTALL_DIR/RunUpdates/etc/schema/

The inventory is hierarchical:

1. **Family** — top‑level grouping (e.g., `linux`)
2. **Distro** — distribution‑specific definitions (e.g., `debian`, `rocky`)
3. **Host** — individual machines

Each level may define:

- variables  
- commands  
- exit‑code rules  
- metadata  
- vault‑backed credentials  

Lower levels inherit from higher levels, with host‑level values taking
precedence.

# TOP‑LEVEL STRUCTURE

A minimal inventory looks like:

```yaml
families:
  linux:
    distros:
      debian:
        hosts:
          ub25-desk-01:
            hostname: ub25-desk-01.local
```

The required top‑level key is:

`families:`

Each family must contain:

`distros:`

Each distro must contain:

`hosts:`

## FAMILY DEFINITIONS
A family block defines:

```yaml
families:
  linux:
    metadata: {...}
    vars: {...}
    commands: {...}
    exit_codes: {...}
    distros: {...}
```

### Family Fields

**metadata**

Arbitrary operator‑defined metadata. Displayed with:

`RunUpdates inventory --show-metadata`

**vars**

Variables inherited by all distros and hosts under this family.

**commands**

Command definitions for:

* refresh
* check
* update
* clean
* reboot

Example:

```yaml
commands:
  check: "apt list --upgradable"
  update: "apt-get -y upgrade"
```

**exit_codes**

Defines which exit codes indicate success, failure, or reboot.

Example:

```yaml
exit_codes:
  reboot_required: [100]
```

## DISTRO DEFINITIONS

A distro block inherits from its family:

```yaml
distros:
  debian:
    metadata: {...}
    vars: {...}
    commands: {...}
    exit_codes: {...}
    hosts: {...}
```

Distro‑level fields override family‑level fields.

## HOST DEFINITIONS

A host block inherits from its distro and family:

```yaml
hosts:
  ub25-desk-01:
    hostname: ub25-desk-01.local
    metadata: {...}
    vars: {...}
    commands: {...}
    exit_codes: {...}
```

### Required Host Fields

**hostname**

The SSH or local execution target.

**enabled**

Optional. Defaults to true.

**vars**

Host‑specific variables override distro and family variables.

**commands** 

Host‑specific commands override distro and family commands.

**exit_codes**

Host‑specific exit‑code rules override distro and family rules.

## VARIABLE INHERITANCE

Variables merge downward:

`family.vars → distro.vars → host.vars`

Host values override distro values, which override family values.

Example:

```yaml
families:
  linux:
    vars:
      pkg_manager: apt
    distros:
      debian:
        vars:
          pkg_manager: apt-get
        hosts:
          ub25:
            vars:
              pkg_manager: nala
```

Result for host ub25:

`pkg_manager = "nala"`

## COMMAND INHERITANCE

Commands follow the same inheritance rules as variables.

Missing commands at the host level fall back to distro, then family.

## EXIT CODE INHERITANCE

Exit‑code rules merge downward. Host‑level definitions override distro and
family definitions.

## METADATA

Metadata is optional and never affects execution. It is displayed only when
requested:

`RunUpdates inventory --show-metadata`

Metadata is inherited and merged like variables.

## VAULT INTEGRATION

The inventory does **not** reference the vault and does not contain any
templated values such as `{{ vault.* }}`. Vault keys are never exposed in
the inventory and are not part of the schema.

RunUpdates loads the vault **before** loading the inventory and stores the
decrypted values in the runtime context. These values are used internally
by the update orchestrator but are never merged into the inventory.

Vault usage is **mandatory**, but vault data is completely external to the
inventory file.

## NORMALIZATION RULES

During inventory load, RunUpdates performs:

1. Schema validation
2. Vault decryption
3. Inheritance merging
4. Command normalization
5. Exit‑code normalization
6. Host enablement filtering
7. Final resolved inventory output

The resolved inventory is what appears when running:

`RunUpdates inventory`

## COMMON ERRORS

### Missing required keys

`InventoryError: Missing required key: families`

### Invalid schema

`InventorySchemaError: distros must be a mapping`

### Unknown host

`InventoryLookupError: Host 'foo' not found`

### Vault permission failure

`VaultPermissionError: vault.yml must have permissions 0600`

## EXAMPLE INVENTORY

```yaml
families:
  linux:
    vars:
      pkg_manager: apt
    commands:
      check: "apt list --upgradable"
      update: "apt-get -y upgrade"
    distros:
      debian:
        vars:
          pkg_manager: apt-get
        hosts:
          ub25-desk-01:
            hostname: ub25-desk-01.local
            vars:
              pkg_manager: nala
```

SEE ALSO
RunUpdates(1)  
runupdates-inventory(1)  
runupdates-update(1)  
runupdates-summary(1)  
runupdates-config(5)