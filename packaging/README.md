# RunUpdates Packaging Overview

This directory contains all assets, specifications, and policies required to
package RunUpdates for distribution. It defines the official installation
model, directory layout, and constraints that all packaging formats must
follow (RPM, DEB, TGZ, ZIP).

This README is the entry point. For the full packaging manual, see:

- [`Packaging.md`](Packaging.md)

---

## 1. Installation Policy (Authoritative)

RunUpdates supports **two installation models**, depending on the packaging format:

| Format | Install Location | Requires Root | Notes |
| --- | --- | --- | --- |
| ``.tgz`` / ``.zip`` | ``$HOME/RunUpdates`` | No | Portable, user‑local installs |
| ``.deb`` / ``.rpm`` | ``/opt/RunUpdates`` | Yes | System‑level installs |

This distinction is required because:

* **DEB cannot install into** ``$HOME``
* **RPM installs into system paths by default**
* **TGZ/ZIP are user‑local and relocatable**

### 1.1 User‑Local Installation (TGZ/ZIP)

TGZ and ZIP archives must install into a directory **writable by the user**.

Valid examples:

```Code
$HOME/RunUpdates
/mnt/data/runupdates/RunUpdates
/srv/tools/RunUpdates
```

### 1.2 System Installation (DEB/RPM)

DEB and RPM packages install into:

```Code
/opt/RunUpdates
```

This location is:

* root‑owned
* standard for third‑party tools
* required by DEB packaging rules
* compatible with RPM packaging conventions

After installation, the admin must make the directory writable:

```Code
sudo chown -R <user>:<group> /opt/RunUpdates
```

### 1.3 Relocatable Installation

Only **TGZ/ZIP** are fully relocatable.

DEB and RPM are **not** relocatable into ``$HOME``, but may be relocated by an admin into another system directory if ownership is corrected.

---

## 2. Directory Layout

All packaging formats must produce the following directory tree:

```Code
RunUpdates/
    bin/
    lib/
    etc/
        hosts.yml              (not packaged)
        schemata/
            hosts.schema.yml   (the only schema file)
    var/
        logs/
        logs/summaries/
        run/
```

### 2.1 ``.env`` generation

At install time, packaging scripts must generate:

```Code
CONFIG_DIR=$INSTALL_DIR/RunUpdates/etc
SCHEMA_DIR=$INSTALL_DIR/RunUpdates/etc/schemata
LOG_DIR=$INSTALL_DIR/RunUpdates/var/logs
```

This file must **not** be included in freeze builds.

---

## 3. Packaging Formats

### 3.1 RPM

* Installs into /opt/RunUpdates
* Requires root
*  Must create the directory tree under /opt/RunUpdates
* Must copy hosts.schema.yml into etc/schemata/
* Must not package hosts.yml
* RPM output is renamed to:

```Code
RunUpdates_<version>.x86_64.rpm
```

### 3.2 DEB

Installs into /opt/RunUpdates

* Requires root
* Must create the same directory structure as RPM
* Must not package hosts.yml
* DEB output is named:

```Code
RunUpdates_<version>.deb
```

### 3.3 TGZ

Portable archive containing the full RunUpdates/ directory tree

* Extracts into $HOME/RunUpdates by default
* No system integration

### 3.4 ZIP

* Same as TGZ, but ZIP format
* Extracts into $HOME/RunUpdates

---

## 4. Freeze Build Requirements

All packaging formats depend on the PyInstaller freeze build. The freeze build must:

* Place the binary in RunUpdates/bin/RunUpdates
* Exclude etc/ and schemata/ from the freeze
* Clone PythonTools before building
* Produce a relocatable binary tree with no hardcoded paths

The freeze output is **not compressed**.
Compression happens only in TGZ/ZIP packaging.

---

## 5. Directory Contents

```Code
packaging/
    README.md        ← this file (start here)
    Packaging.md     ← full packaging manual
    rpm/
        runupdates.spec
    deb/
        control
        postinst
        prerm
    scripts/
        build_tgz.sh
        build_zip.sh
        build_deb.sh
        build_rpm.sh
        build_all.sh
```

---

## 6. Maintainer Notes

* TGZ/ZIP installs are user‑local and relocatable.
* DEB/RPM installs are system‑level and require root.
* After DEB/RPM installation, ``/opt/RunUpdates`` must be made writable.
* No packaging format may include secrets.
* No packaging format may include operator inventory.
* The schema directory contains exactly one schema file:
  ``hosts.schema.yml``.

For detailed procedures, see [Packaging](Packaging.md)