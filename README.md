# RunUpdates

RunUpdates is a deterministic, operator‑grade update orchestration tool designed for controlled, auditable, and reproducible system updates across heterogeneous Linux environments. It provides a consistent execution model, structured logging, vault‑backed secrets, and a predictable CLI workflow.

## Features

- Deterministic update execution with explicit operator control  
- Structured logging with lifecycle, audit, and trace channels  
- Vault‑backed credential resolution  
- Inventory‑driven host targeting  
- Reproducible orchestration model  
- Preview mode for safe dry‑runs  
- Maintenance utilities (e.g., update_modified.py)

## Logging

RunUpdates uses a layered logging system with:

- File logs in `RunUpdates/var/log/RunUpdates.log`  
- Console output for operator visibility  
- Custom levels: `AUDIT`, `LIFECYCLE`, `TRACE`  
- Rotating log files with retention controls  

Maintenance scripts log to:

<Project Root>/Logs/<script>.log

## Directory Structure

RunUpdates/
├── RunUpdates/
│   ├── logging/
│   ├── parser/
│   ├── var/log/
│   ├── main.py
│   └── ...
└── README.md

Code

## Requirements

- Python 3.11+
- Linux environment (tested on SUSE, Ubuntu, Rocky)
- Vault password file or direct CLI password

## Usage

```bash
python -m RunUpdates --inventory hosts.yml --vault-password-file .vaultpass
```

Preview mode:

```bash
python -m RunUpdates --preview
```

License
MIT License