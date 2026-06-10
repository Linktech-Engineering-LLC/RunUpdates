# RunUpdates Packaging Overview

This directory contains all assets, specifications, and policies required to
package RunUpdates for distribution. It defines the official installation
model, directory layout, and constraints that all packaging formats must
follow (RPM, DEB, TGZ, ZIP).

This README is the entry point. For the full packaging manual, see:

- [`Packaging.md`](Packaging.md)

---

## 1. Installation Policy (Authoritative)

RunUpdates **must be installed into a directory that is writable by the user
running it**. This requirement is fundamental to the design of the tool.

### 1.1 Allowed installation roots

The installation root **must be user‑writable**. Valid examples include:

- `$HOME`
- Any directory owned by the user
- A directory created by root but explicitly `chown`ed to the user

Examples:

/home/leon/RunUpdates
/mnt/data/runupdates/RunUpdates
/srv/tools/RunUpdates

### 1.2 Forbidden installation roots

These locations are **not allowed** because they are root‑owned and not
writable by normal users:

- `/opt`
- `/usr/local`
- `/usr`
- `/var`
- Any system‑managed prefix

RunUpdates must not be installed into these directories unless the admin
explicitly changes ownership to the user.

### 1.3 Relocatable installation

RunUpdates is fully relocatable. The installation root is defined by the user
or by the packaging system. All internal paths are derived from:

`$INSTALL_DIR/RunUpdates`

No hardcoded absolute paths are permitted.

---

## 2. Directory Layout

All packaging formats must produce the following directory tree:

```code
RunUpdates
    bin/
    etc/
        hosts.yml              (template)
        schema/
            hosts.schema.yml   (the only schema file)
    var/
        log/
            summary/
        run/
```

### 2.1 `.env` generation

At install time, packaging scripts must generate:

```code
CONFIG_DIR=$INSTALL_DIR/RunUpdates/etc
SCHEMA_DIR=$INSTALL_DIR/RunUpdates/etc/schema
LOG_DIR=$INSTALL_DIR/RunUpdates/var/log
```

This file must not be included in source or freeze builds.

---

## 3. Packaging Formats

### 3.1 RPM

- Installs into a relocatable prefix.
- Must create the directory tree under `$INSTALL_DIR/RunUpdates`.
- Must copy `hosts.schema.yml` into `etc/schema/`.
- Must not install into `/opt` or `/usr/local` unless the admin chooses that
  prefix and ensures it is writable.

### 3.2 DEB

- Uses Debian `dh` conventions.
- Must respect relocatable installation.
- Must install the same directory structure as RPM.

### 3.3 TGZ

- A portable archive containing the full `RunUpdates/` directory tree.
- No system integration.
- No man pages.

### 3.4 ZIP

- Contains only the RPM and DEB artifacts.
- No binaries, no source, no documentation.

---

## 4. Freeze Build Requirements

All packaging formats depend on the PyInstaller freeze build. The freeze build
must:

- Place the binary in `RunUpdates/bin/runupdates`
- Exclude `etc/` and `schema/` from the freeze
- Clone PythonTools before building
- Produce a relocatable binary with no hardcoded paths

---

## 5. Directory Contents

```code
packaging/
    README.md        ← this file (start here)
    Packaging.md     ← full packaging manual
    rpm/
        runupdates.spec
    debian/
        control
        rules
        install
    scripts/
        build_tgz.sh
        build_zip.sh
```

---

## 6. Maintainer Notes

- All packaging work must conform to the installation policy above.
- No packaging format may introduce hardcoded paths.
- No packaging format may assume root‑owned installation directories.
- The schema directory contains **exactly one** schema file:
  `hosts.schema.yml`.

For detailed procedures, see `Packaging.md`.
