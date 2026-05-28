# RunUpdates — Error Classification Model

This document describes how RunUpdates interprets exit codes, classifies errors, and records them in logs and summaries.  
The goal is to provide deterministic, operator‑grade behavior across all supported distributions.

RunUpdates uses a simple, explicit classification model:

* **success**
* **warning**
* **error**
* **fatal**

These classifications appear in:

* operator logs  
* per‑host summaries  
* aggregated results  

They never contain sensitive data.

---

# 1. Purpose of Error Classification

Error classification provides:

* consistent interpretation across distros  
* predictable operator behavior  
* stable automation hooks  
* clear reporting in summaries  
* deterministic logging  

RunUpdates does **not** rely on distro‑specific semantics alone.  
Instead, it maps exit codes into a unified model.

---

# 2. Classification Levels

## 2.1 success
Indicates that the command completed without errors.

Examples:

* <zypper lu> returned 0  
* <apt upgrade -y> returned 0  
* <dnf upgrade -y> returned 0  

Recorded as:

<classification: success>


---

## 2.2 warning
Indicates a non‑fatal issue that did not prevent execution.

Examples:

* package manager returned a non‑zero code but still produced usable output  
* a list command returned partial results  
* a reboot is required (not an error, but noteworthy)  

Recorded as:

<classification: warning>


Warnings do **not** stop execution.

---

## 2.3 error
Indicates a failure that affected the command but did not stop the host’s overall execution flow.

Examples:

* update command failed  
* list command failed  
* SSH command returned a non‑zero exit code  
* stderr contained actionable errors  

Recorded as:

<classification: error>


Execution continues to:

* post‑update list  
* reboot detection  
* summary generation  

---

## 2.4 fatal
Indicates a failure that prevents further execution for the host.

Examples:

* SSH session could not be created  
* authentication failed  
* inventory entry was invalid  
* command could not be executed at all  
* PythonTools raised an unrecoverable exception  

Recorded as:

`"classification": "fatal"`


A fatal classification ends processing for that host.
Other hosts are unaffected.

---

# 3. How Exit Codes Are Interpreted

RunUpdates uses a deterministic mapping:

| Exit Code | Classification | Meaning |
|-----------|----------------|---------|
| [0]       | success        | Command completed normally |
| [1–99]    | error          | Command failed but execution may continue |
| [100–199] | warning        | Non‑fatal issues (distro‑specific) |
| [200+]    | fatal          | Unrecoverable failure |

This mapping is intentionally simple and distro‑agnostic.

### Notes

- Some distros use special codes (e.g., `zypper` reboot codes).  
  These are mapped into **warning** or **success** depending on context.
- PythonTools may override classification if stderr indicates a fatal condition.

---

# 4. PythonTools Integration

PythonTools provides:

- exit code capture  
- stderr/stdout capture  
- exception handling  
- SSH error detection  
- redaction of sensitive data  

RunUpdates then applies its classification model on top of this.

### PythonTools fatal conditions include:

- SSH connection failure  
- authentication failure  
- command execution failure (no exit code)  
- unexpected exceptions  

These are always mapped to:

<classification: fatal>

---

# 5. How Classification Affects Execution Flow

## 5.1 success
Execution continues normally.

## 5.2 warning
Execution continues, but the summary records the issue.

## 5.3 error
Execution continues, but the host is marked as having failed operations.

## 5.4 fatal
Execution stops for that host immediately.
Other hosts continue unaffected.

---

# 6. Logging Behavior

Each command produces a log entry:

code

```
[2025-05-01 14:03:22] COMMAND: zypper lu
[2025-05-01 14:03:23] EXIT: 4
[2025-05-01 14:03:23] CLASSIFICATION: warning
```


Logs contain:

* timestamp  
* command  
* exit code  
* classification  
* stderr (redacted if needed)  

Logs never contain:

* passwords  
* SSH keys  
* vault secrets  
* sensitive inventory data  

---

# 7. Summary Behavior

Each host summary includes:

code

'''
"exit_code": 4,
"classification": "warning",
"errors": ["Reboot required"],
"reboot_required": true
'''

Summaries are machine‑readable and safe for long‑term retention.

---

# 8. Examples

## 8.1 Successful update

code

```
exit_code: 0
classification: success
reboot_required: false
```

## 8.2 Update succeeded but reboot required

code

```
exit_code: 103
classification: warning
reboot_required: true
```

## 8.3 Update failed

code

```
exit_code: 1
classification: error
reboot_required: false
```

## 8.4 SSH failure

code

```
exit_code: null
classification: fatal
error: "SSH connection failed"
```

---

# 9. Summary

RunUpdates uses a deterministic, distro‑agnostic error classification model that ensures:

* predictable operator behavior  
* consistent logging  
* clear summaries  
* stable automation hooks  
* safe, audit‑friendly output  

This document defines the authoritative classification rules for all RunUpdates operations.
