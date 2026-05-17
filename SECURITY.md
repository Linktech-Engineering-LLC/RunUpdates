# Security Policy

## Supported Versions

RunUpdates is actively maintained and security‑patched on a best‑effort basis.
The following versions currently receive security updates:

| Version | Supported |
|---------|-----------|
| 1.x     | ✔ Supported |
| 0.x     | ✘ Not supported |
| Older   | ✘ Not supported |

Only the latest minor release within the 1.x series receives fixes.

---

## Reporting a Vulnerability

If you discover a security vulnerability in RunUpdates, please report it privately.

**Contact:**
security@linktechengineering.net  
or  
ldmcclatchey@linktechengineering.net

Please include:

- A clear description of the issue  
- Steps to reproduce (if applicable)  
- Any relevant logs or environment details  
- Your assessment of potential impact  

You will receive an acknowledgment within **72 hours**, and updates will be provided as the issue is investigated.

If the vulnerability is confirmed:

- A fix will be developed as quickly as possible  
- A security advisory will be published (if warranted)  
- Credit will be given to the reporter unless anonymity is requested  

Please do **not** disclose the vulnerability publicly until a fix has been released.

---

# Security Expectations

RunUpdates is designed with deterministic, operator‑grade behavior and a minimal attack surface.
The following principles guide its security posture.

---

## Execution Model

- No remote code execution beyond package manager commands  
- No dynamic imports or runtime code generation  
- No unvalidated input passed to system commands  
- No shell expansion unless explicitly required and wrapped safely  
- No YAML‑driven execution paths that alter program flow  

All execution paths are explicit, documented, and deterministic.

---

## Authentication & Secrets

- SSH authentication uses keyfiles when available  
- Password authentication is used only as a fallback  
- Sudo passwords are never logged  
- Secrets are injected at runtime and never stored in logs or artifacts  
- Vault‑style secrets (if used) must be stored outside the repository  

RunUpdates never writes sensitive data to disk.

---

## Logging

RunUpdates uses a structured, deterministic logging model.

- Logs contain **no sensitive data**  
- Commands are logged, but passwords and secrets are redacted  
- Session creation logs include only non‑sensitive metadata  
- Failures are logged with exit codes and stderr  
- Per‑host summaries contain only operational results  

Operator logs and machine‑readable summaries are intentionally separate.

---

## Inventory & YAML

- Inventory files are validated before execution  
- Unknown fields are rejected  
- No implicit defaults are assumed  
- Exit‑code interpretation is declarative and controlled  
- No arbitrary YAML‑driven execution paths  

Inventories must use placeholder values in examples.

---

## Local Execution

- Local privileged operations use `sudo_run`  
- Commands are wrapped safely when shell operators are present  
- No elevation occurs without explicit user configuration  
- Local mode follows the same logging and redaction rules as SSH mode  

---

## File System & Output

- Per‑host summaries contain no secrets  
- Log files contain no credentials  
- Temporary files (if any) are cleaned up deterministically  
- No sensitive data is written to cache directories  

RunUpdates produces audit‑friendly output suitable for long‑term retention.

---

## Responsible Disclosure

We strongly encourage responsible disclosure.
If you believe you have found a vulnerability that could impact users, please contact us privately so we can address it promptly and safely.

---

Thank you.  
Your efforts help keep RunUpdates secure, deterministic, and reliable for everyone.
