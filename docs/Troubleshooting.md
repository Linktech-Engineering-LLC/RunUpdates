# Troubleshooting RunUpdates

This guide provides practical, operator‑grade troubleshooting steps for diagnosing and resolving issues encountered while running RunUpdates. It complements the Execution Flow, Error Classification, and Security documents by focusing on real‑world failure modes and actionable fixes.

## 1. Inventory Issues

### 1.1 Invalid YAML

**Symptoms:**
* RunUpdates exits immediately
* Error indicates YAML parsing failure

**Fix:**
* Validate YAML structure
* Ensure indentation is consistent
* Confirm lists use - and not inline commas

### 1.2 Unknown or misspelled fields

**Symptoms:**
* Validation error: "Unknown field"

**Fix:**
* Compare against the documented schema
* Remove unsupported keys

### 1.3 Address not a list

**Symptoms:**
* Validation error: [address must be a list]

**Fix:**

address:
  - 192.0.2.10

### 1.4 Missing required fields

**Symptoms:**
Validation error referencing missing [address], [port], or [user]

**Fix:**
* Add required fields to the host entry

## 2. SSH Connection Failures

### 2.1 Authentication failure

**Symptoms:**
* [fatal] classification
* Summary shows: [SSH connection failed]

Fix:
* Ensure SSH key exists and permissions are correct
* Verify username in inventory
* Test manually:

```ssh user@host -p <port>```

### 2.2 Host unreachable

**Symptoms:**
* Timeout
* Connection refused

**Fix:**
* Verify network connectivity
* Confirm firewall rules
* Ensure correct port in inventory

### 2.3 Wrong SSH key or agent not loaded

**Fix:**

```bash
ssh-add -l
ssh-add ~/.ssh/id_rsa
```

## 3. Local Execution Problems

### 3.1 sudo password incorrect or missing

**Symptoms:**
* [fatal] classification
* stderr indicates sudo failure

**Fix:**
* Ensure sudo password is provided via vault
* Confirm user has sudo privileges

### 3.2 sudo requires TTY

**Symptoms:**
* stderr: [sudo: no tty present]

**Fix:**
* Update /etc/sudoers:

[Defaults:<user> !requiretty]

## 4. Vault and Secrets Issues

### 4.1 Vault path not found

**Symptoms:**
* Fatal error loading vault

**Fix:**
* Verify [RUNUPDATES_VAULT_PATH]
* Confirm file permissions

### 4.2 Missing vault password file

**Fix:**
* Set [RUNUPDATES_VAULT_PASSWORD_FILE]
* Ensure file contains only the password

### 4.3 Secrets not merging into inventory

**Fix:**
* Confirm vault keys match inventory fields
* Check for indentation errors in vault YAML

## 5. Package Manager Failures

### 5.1 zypper errors

**Symptoms:**
* Exit codes 4, 100, or vendor‑change warnings

**Fix:**
* Refresh repos manually:
  `sudo zypper refresh`
* Check for broken repos in /etc/zypp/repos.d/

### 5.2 apt errors

**Symptoms:**
* [Hash Sum mismatch]
* [Could not get lock]

**Fix:**

```bash
sudo rm /var/lib/apt/lists/lock
sudo rm /var/lib/dpkg/lock*
sudo dpkg --configure -a
```

### 5.3 dnf errors

**Symptoms:**
* Metadata cache issues

**Fix:**

```bash
sudo dnf clean all
sudo dnf makecache
```

## 6. Reboot Detection Issues

### 6.1 False positives

**Symptoms:**
* Summary shows [reboot_required: true] unexpectedly

**Fix:**
* Check distro‑specific indicators:
    * Debian/Ubuntu: [/var/run/reboot-required]
    * openSUSE: [zypper needs-rebooting]
    * RedHat: [needs-restarting -r]

### 6.2 False negatives

**Fix:**
* Ensure required tools are installed ([zypper-needs-rebooting], [yum-utils])

## 7. repo_broken Classification

**Symptoms:**
* Summary shows: [repo_broken: true]
* zypper or apt reports unreachable or invalid repositories

**Fix:**
* Disable failing repos
* Update mirror URLs
* Validate GPG keys

## 8. Summary.json Interpretation

### 8.1 Host marked failed but commands succeeded

**Cause:**
*A non‑zero exit code was classified as error

**Fix:**
* Check per‑host summary for the exact command
* Review stderr for actionable errors

### 8.2 Missing summary files

**Fix:**
* Ensure log directory is writable
* Confirm RunUpdates was not terminated early

## 9. Common Misconfigurations

* Using scalar instead of list for [address]
* Wrong SSH port
* Missing vault password file
* Incorrect sudo password
* Unsupported distro name
* Host defined under wrong family
* YAML indentation errors

## 10. Debugging Techniques

### 10.1 Increase verbosity

Run with:

`--debug`

### 10.2 Test commands manually

```bash
ssh user@host
sudo zypper refresh
sudo apt update
sudo dnf check-update
```

### 10.3 Validate inventory

`runupdates --list`

### 10.4 Inspect logs

Check:

`/var/log/runupdates/`

## 11. When to File an Issue

Please open an issue if:
* a classification seems incorrect
* a supported distro behaves unexpectedly
* logs indicate an unhandled exception
* summaries contain inconsistent data
* inventory validation rejects valid configurations

Include:
* sanitized inventory snippet
* sanitized logs
* distro version
* RunUpdates version

This guide will expand as new edge cases and operator feedback emerge.