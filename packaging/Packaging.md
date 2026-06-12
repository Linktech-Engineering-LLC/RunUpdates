# RunUpdates Packaging Guide (Updated)

This document describes how RunUpdates is packaged for distribution, including:

* frozen binary builds
* DEB packaging
* RPM packaging
* TGZ/ZIP portable archives
* directory layout
* freeze rules
* GitHub Actions nightly workflow

RunUpdates uses a hybrid packaging model:

| Format | Install Location | Requires Root | Purpose |
| --- | --- | --- | --- |
| ``.tgz`` / ``.zip`` | ``$HOME/RunUpdates`` | No | Portable, user‑local installs |
| ``.deb`` / ``.rpm`` | ``/opt/RunUpdates`` | Yes | System‑level installs |

For installation instructions, see **QuickStart.md**.
For internal architecture, see **ARCHITECTURE.md**.

## 1. Packaging Overview

RunUpdates produces four distributable artifacts:

| Artifact | Purpose |
| --- | --- |
| ``.deb`` | Debian/Ubuntu installation |
| ``.rpm`` | RHEL/Fedora/openSUSE installation |
| ``.tgz`` | Portable Linux distribution |
| ``.zip`` | Portable Linux distribution |

All artifacts contain the same runtime layout and the same frozen binary.

### Final Artifact Naming

```Code
RunUpdates_<version>.deb
RunUpdates_<version>.x86_64.rpm
RunUpdates_<version>.tgz
RunUpdates_<version>.zip
```

No architecture suffix is used for DEB/TGZ/ZIP.
RPM retains ``.x86_64.rpm`` because the format requires it.

---

## 2. Runtime Directory Layout

All packaging formats produce the same runtime structure:

RunUpdates/
    bin/                    ← frozen executable
    lib/                    ← Python runtime + dependencies
    etc/                    ← configuration directory
        hosts.yml           ← operator inventory (not packaged)
        schemata/
            hosts.schema.yml
    var/
        logs/
        logs/summaries/
        run/

### Rules

* ``hosts.yml`` is never packaged.
* ``schemata/hosts.schema.yml`` is always included.
* ``var/logs``, ``var/logs/summaries``, and ``var/run`` must be writable.
* TGZ/ZIP installs are user‑local.
* DEB/RPM installs are system‑level.

---

## 3. Frozen Binary Build

RunUpdates uses **PyInstaller** to produce a self‑contained binary tree.

### Output

dist/RunUpdates/
    RunUpdates
    libpython…
    dependencies…

This output is **not compressed**.
Compression happens only during packaging (TGZ/ZIP/DEB/RPM).

### Freeze Rules

Include:

```Code
RunUpdates source
PythonTools
all Python dependencies
schemata/hosts.schema.yml
```

Exclude:

```Code
etc/hosts.yml
vault files
vault password files
logs
summaries
```

---

## 4. TGZ and ZIP Packaging (User‑Local Installs)

TGZ and ZIP packages are portable and do not require root.

### Install Location

```Code
$HOME/RunUpdates
```

### Naming

```Code
RunUpdates_<version>.tgz
RunUpdates_<version>.zip
```

### Creation

```Code
tar -czf RunUpdates_<version>.tgz RunUpdates/
zip -r RunUpdates_<version>.zip RunUpdates/
```

### Usage

```Code
mkdir -p $HOME/RunUpdates
tar -xzf RunUpdates_<version>.tgz -C $HOME
```

---

## 5. DEB Packaging (System Install)

DEB packages install into:

```Code
/opt/RunUpdates/
```

### Naming

```Code
RunUpdates_<version>.deb
```

### Requires

* root privileges
* system‑level installation

### Post‑Install Requirements

Because RunUpdates must be writable:

```Code
sudo chown -R <user>:<group> /opt/RunUpdates
```

### Build Process

* Create staging directory under packaging/deb
* Copy frozen binary tree
* Create DEBIAN/control
* Build package:

```Code
dpkg-deb --build <staging>
```

---

## 6. RPM Packaging (System Install)

RPM packages also install into:

```Code
/opt/RunUpdates
```

### Naming

RPMs are renamed after build:

```Code
RunUpdates_<version>.x86_64.rpm
```

### Requires

* root privileges
* system‑level installation

### Post‑Install Requirements

```Code
sudo chown -R <user>:<group> /opt/RunUpdates
```

### Build Process

* Create source tarball for rpmbuild
* rpmbuild unpacks into BUILD/
* %install copies files into /opt/RunUpdates
* rpmbuild produces:

```Code
runupdates-<version>-1.x86_64.rpm
```

Workflow renames it to:

```Code
RunUpdates_<version>.x86_64.rpm
```

---

## 7. GitHub Actions Nightly Workflow

The nightly workflow:

1. Freezes the binary
2. Builds DEB, RPM, TGZ, ZIP
3. Normalizes filenames
4. Uploads artifacts
5. Updates the nightly tag
6. Generates a dashboard
7. Publishes to gh-pages

Artifacts uploaded:

```Code
RunUpdates_<version>.deb
RunUpdates_<version>.x86_64.rpm
RunUpdates_<version>.tgz
RunUpdates_<version>.zip
```

---

## 8. Packaging Constraints

### Never package secrets

* vault.yml
* vault password files
* operator inventory
* logs
* summaries

### Never package host‑specific data

* hostnames
* IP addresses
* SSH keys
* credentials

### Never package writable files

Writable directories are created at install time.

## 9. Testing a Packaged Build

### TGZ/ZIP

```Code
mkdir -p $HOME/RunUpdates
tar -xzf RunUpdates_<version>.tgz -C $HOME
```

### DEB

```Code
sudo dpkg -i RunUpdates_<version>.deb
sudo chown -R $USER:$USER /opt/RunUpdates
```

### RPM

```Code
sudo rpm -ivh RunUpdates_<version>.x86_64.rpm
sudo chown -R $USER:$USER /opt/RunUpdates
```

### Run

```Code
/opt/RunUpdates/bin/RunUpdates update
```

or for TGZ/ZIP:

```Code
$HOME/RunUpdates/bin/RunUpdates update
```

---

## 10. Summary

RunUpdates packaging follows a hybrid model:

| Format | Install Location | Root Required |
| --- | --- | --- |
| TGZ/ZIP | ``$HOME/RunUpdates`` | No |
| DEB/RPM | ``/opt/RunUpdates`` | Yes |

All formats share:

* the same frozen binary
* the same directory layout
* the same schemata
* the same runtime expectations

This model ensures:

* portability for developers
* system‑level integration for operators
* consistent behavior across all distributions
