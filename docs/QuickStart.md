# RunUpdates — Quick Start

RunUpdates is a deterministic, YAML‑driven update orchestrator for Linux hosts.  
This guide provides the minimum steps required to install, configure, and run RunUpdates from source.

---

## 1. Requirements

RunUpdates requires:

* Python 3.10+
* A Python virtual environment (venv)
* PythonTools installed in the same venv
* RunUpdates installed in the same venv
* SSH access to remote hosts (password or key‑based)
* A valid `hosts.yml` inventory
* A valid Vault file and Vault password file (required)

RunUpdates is **source‑only** in this version. Frozen binaries and RPM packaging are documented separately.

---

## 2. Installation (Source)

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install PythonTools into the venv:

```bash
pip install git+https://github.com/Linktech-Engineering-LLC/PythonTools.git
```

Clone and install RunUpdates into the same venv:

```bash
git clone https://github.com/Linktech-Engineering-LLC/RunUpdates.git
cd RunUpdates
pip install -e .
pip install -r requirements.txt
```

RunUpdates is now installed as a package and ready to execute.

## 3. Configuration Directory Setup

RunUpdates expects a configuration directory containing:

```Code
etc/
  hosts.yml
  schemata/   (symlink to source schemata/)
```

The cloned repository does not include an etc/ directory.
You must create it manually:

```bash
mkdir -p etc
```

Populate hosts.yml
Copy or create a hosts.yml from your templates:

```bash
cp templates/hosts.yml.example etc/hosts.yml
Symlink schemata into etc/
bash
ln -s ../schemata etc/schemata
```

This ensures the loader can find schema definitions without duplicating files.

Validate your inventory

```bash
python -m RunUpdates inventory
```

List specific scopes:

```bash
python -m RunUpdates inventory --family linux
python -m RunUpdates inventory --distro opensuse
python -m RunUpdates inventory --host leap-node
```

## 4. Vault Setup (Required)

RunUpdates requires a Vault file for credentials.

If neither CLI options nor environment variables are provided, RunUpdates will exit with an error.

### Vault file (``vault.yml``)

* Must not be placed in the RunUpdates repository
* Must not be placed in ``etc/``
* Must reside in a secure directory with **0700** permissions
* The file itself must be **0600**

Example:

```bash
mkdir -m 700 ~/runupdates-vault
cp vault.yml ~/runupdates-vault/
chmod 600 ~/runupdates-vault/vault.yml
```

### Vault password file

* Must be stored separately from the vault
* Must be **0600**

Example:

```bash
echo "mypassword" > ~/.vault_pass
chmod 600 ~/.vault_pass
```

### Providing vault paths

RunUpdates accepts vault paths via **CLI** or **environment variables**.

#### Option 1 — CLI flags

```bash
python -m RunUpdates update \
  --vault-path ~/runupdates-vault/vault.yml \
  --vault-password-file ~/.vault_pass
```

#### Option 2 — Environment variables

```bash
export RUNUPDATES_VAULT_PATH=~/runupdates-vault/vault.yml
export RUNUPDATES_VAULT_PASSWORD_FILE=~/.vault_pass
```

Then simply run:

```bash
python -m RunUpdates update
```

RunUpdates will not run unless both the vault path and password file are provided.

## 5. Running RunUpdates

RunUpdates uses subcommands:

* ``inventory`` — inspect inventory
* ``update`` — run updates
* ``summary`` — show run summaries
* ``version`` — show version
* ``help`` — show help for subcommands

Run updates on all hosts:

```bash
python -m RunUpdates update
```

Run updates on a specific host:

```bash
python -m RunUpdates update --host leap-node
```

Run updates on a distro:

```bash
python -m RunUpdates update --distro opensuse
```

Run updates on a family:

```bash
python -m RunUpdates update --family linux
```

## 6. Runtime Directories

RunUpdates uses the following default runtime paths:

### Logs

```Code
var/logs/
```

Contains:

* rotating logs
* compressed archives
* operator‑level logs

### Summaries

```Code
var/log/summaries/
```

Contains:

* per‑host summaries
* per‑run summaries

### PID file

```Code
var/run/runupdates.pid
```

Independent of ``--log-dir``.

## 7. What Happens During a Run

Each host executes the same deterministic lifecycle:

```Code
refresh → check → update? → clean → reboot detection
```

* RunUpdates logs:
* lifecycle events
* stdout/stderr
* exit codes
* timestamps
* update decisions
* repo health
* reboot requirements

## 8. Exit Codes

The exit codes listed below apply **only to the RunUpdates orchestrator itself** — the Python program that coordinates all hosts.

RunUpdates returns:

* **0** — all hosts completed successfully  
* **1** — one or more hosts failed  
* **2** — inventory or schema validation error  
* **3** — connection failure  
* **4** — internal error  

### Note on Package‑Manager Exit Codes

These exit codes do **not** represent the exit codes returned by package managers such as APT, DNF, YUM, Zypper, or Pacman.

Package‑manager exit codes are:

- **distro‑specific**
- **command‑specific**
- **version‑specific**
- **host‑overrideable**

RunUpdates does **not** hardcode these values.  
Instead, each distro defines its own exit‑code rules in the inventory under:

```yaml
exit_codes:
  check:
    up_to_date: [...]
    patches_available: [...]
    reboot_required: [...]
    error: ["*"]
```

Hosts may override these rules.
RunUpdates interprets package‑manager exit codes using the merged host configuration via ``classify_exit_code()``.

## 9. Updating Inventory or Schema

After modifying:

* ``etc/hosts.yml``
* ``schemata/*.yml``

Validate again:

```bash
python -m RunUpdates inventory
```

RunUpdates is strict and fail‑fast — invalid inventory stops execution immediately.

## 10. Next Steps

* Review [ARCHITECTURE](ARCHITECTURE.md) for internal design
* See [Packaging](docs/Packaging.md) for packaging and release instructions
* Use ``--family``, ``--distro``, and ``--host`` to target specific groups

RunUpdates is designed to be predictable, auditable, and operator‑grade.
This Quick Start covers everything needed to run it from source.