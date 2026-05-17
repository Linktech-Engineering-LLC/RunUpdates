# RunUpdates — Inventory Schema Reference (`hosts.yml`)

This document defines the formal schema for the RunUpdates inventory file.
The schema is considered **stable**. Any changes require:

- discussion in an issue
- a schema version bump
- migration notes
- README updates

RunUpdates uses a deterministic, explicit configuration model.  
There are **no implicit defaults** and no hidden behavior.

---

# 1. Top‑Level Structure

The inventory is a hierarchical YAML document:

linux:
<family>:
<distro>:
hosts:
- <host entry>


Hierarchy:

linux → family → distro → hosts


Each level is explicit and required.

---

# 2. Families

A **family** groups related distributions.

Examples:

- `debian-family`
- `redhat-family`
- `opensuse-family` (future)
- `arch-family` (future)

Families contain one or more **distro blocks**.

Family names must:

- be lowercase
- use hyphens, not underscores
- be unique within `linux`

---

# 3. Distro Blocks

A distro block defines:

- the distro name
- the hosts belonging to that distro
- optional package blocks (future)
- optional repo/key definitions (future)

Example:

```yaml
linux:
  debian-family:
    ubuntu:
      hosts:
        - address: nnn.nnn.nnn.nnn
          port: nn
          user: placeholder
          enabled: true
```

## 3.1 Required Fields

| Field | Type | Description |
| --- | --- | --- |
| ``hosts`` | list | List of host entries |

## 3.2 Optional Fields (Future)

| Field | Type | Description |
| --- | --- | --- |
| ``packages`` | map | Shared package lists for the distro |
| ``repos`` | list | Repository definitions |
| ``keys`` | list | GPG key import definitions |

# 4. Host Entries
Each host entry represents a single machine.

## 4.1 Required Fields

| Field | Type | Description |
| --- | --- | --- |
| ``address`` | string | IP or hostname (placeholder only in examples) |
| ``port`` | integer | SSH port |
| ``user`` | string | SSH username |
| ``enabled`` | boolean | Whether this host participates in execution |

## 4.2 Optional Fields

| Field | Type | Description |
| --- | --- | --- |
| ``tags`` | list | Future: grouping and selection |
| ``comment`` | string | Human‑readable notes |

## 4.3 Field Rules

* address must not be empty
* port must be a valid integer (1–65535)
* user must be a non‑empty string
* enabled must be explicitly true or false
* no defaults are assumed
* no fields are auto‑generated

## 4.4 Example Host Entry

```yaml
- address: nnn.nnn.nnn.nnn
  port: 22
  user: placeholder
  enabled: true
- address: nnn.nnn.nnn.nnn
  port: 22
  user: placeholder
  enabled: true
```

# 5. Reserved Future Fields

To avoid namespace collisions, the following keys are reserved:

* schema_version
* repos
* keys
* packages
* tags
* groups
* metadata

These may be introduced in future versions.

# 6. Validation Rules

RunUpdates performs strict validation:

## 6.1 Structural Validation

* linux must exist
* each family must contain at least one distro
* each distro must contain a hosts list
* each host must contain all required fields

## 6.2 Type Validation

* strings must be strings
* integers must be integers
* booleans must be booleans
* lists must be lists

## 6.3 Semantic Validation

* enabled must be explicitly set
* no duplicate host entries
* no empty family or distro names
* no unknown top‑level keys

## 6.4 Security Validation

RunUpdates rejects inventories containing:

* real passwords
* embedded private keys
* inline secrets
* environment variables containing secrets

# 7. Example Inventory (Safe Placeholders)

```yaml
linux:
  debian-family:
    ubuntu:
      hosts:
        - address: nnn.nnn.nnn.nnn
          port: 22
          user: placeholder
          enabled: true

  redhat-family:
    rocky:
      hosts:
        - address: nnn.nnn.nnn.nnn
          port: 2222
          user: placeholder
          enabled: false
```
This example demonstrates structure only — no real values.

# 8. Schema Versioning (Future)

A future version of RunUpdates will introduce:

```yaml
schema_version: 1
```

Rules:

* version increments on breaking changes
* RunUpdates will refuse to run mismatched versions
* migration notes will accompany each bump

9. Summary

The RunUpdates inventory schema is:

* explicit
* deterministic
* stable
* operator‑grade
* free of implicit defaults

This document serves as the authoritative reference for hosts.yml.