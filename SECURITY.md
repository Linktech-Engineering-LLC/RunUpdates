# Security Policy

## Supported Versions

RunUpdates is actively maintained and security‑patched on a best‑effort basis.
The following versions currently receive security updates:

| Version |	Supported |
|---------|------------|
| 1.x     | ✔ Supported |
| 0.x     | ✘ Not supported |
| Older   | ✘ Not supported |

## Reporting a Vulnerability

If you discover a security vulnerability in RunUpdates, please report it privately.

**Contact:**
security@linktechengineering.net
or
ldmcclatchey@linktechengineering.net

Please include:

* A clear description of the issue
* Steps to reproduce (if applicable)
* Any relevant logs or environment details
* Your assessment of potential impact

You will receive an acknowledgment within 72 hours, and updates will be provided as the issue is investigated.

If the vulnerability is confirmed:

* A fix will be developed as quickly as possible
* A security advisory will be published (if warranted)
* Credit will be given to the reporter unless anonymity is requested

Please do not disclose the vulnerability publicly until a fix has been released.

## Security Expectations

RunUpdates is designed with deterministic, operator‑grade behavior and a minimal attack surface.
The following principles guide its security posture:

## Execution Model

* No remote code execution beyond package manager commands
* No dynamic imports or runtime code generation
* No unvalidated input passed to system commands
* No shell expansion unless explicitly required and wrapped safely

## Authentication & Secrets

* SSH authentication uses keyfiles when available
* Password authentication is used only as a fallback
* Sudo passwords are never logged
* Secrets are injected at runtime and never stored in logs or artifacts

## Logging

* Logs contain no sensitive data
* Commands are logged, but passwords and secrets are redacted
* Failures are logged deterministically with exit codes and stderr

## Inventory & YAML

* Inventory files are validated before execution
* Exit‑code interpretation is declarative and controlled
* No arbitrary YAML‑driven execution paths

## Local Execution

* Local privileged operations use sudo_run
* Commands are wrapped safely when shell operators are present
* No elevation occurs without explicit user configuration

## Responsible Disclosure

We strongly encourage responsible disclosure.
If you believe you have found a vulnerability that could impact users, please contact us privately so we can address it promptly and safely.

Thank You
Your efforts help keep RunUpdates secure, deterministic, and reliable for everyone.