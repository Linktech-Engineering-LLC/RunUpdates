# RunUpdates Troubleshooting Guide

**Part of:** RunUpdates
**Document:** Troubleshooting Guide
**Author:** Leon McClatchey, Linktech Engineering LLC
**License:** MIT
**Requires:** RunUpdates
**Last Updated:** 2026-11-27

---

## Table of Contents

1. [Overview](#1-overview)
2. [Purpose](#2-purpose)
3. [Inventory Issues](#3-inventory-issues)
   1. [Invalid YAML](#31-invalid-yaml)
   2. [Unknown Fields](#32-unknown-fields)
   3. [Address Validation Failures](#33-address-validation-failures)
   4. [Lifecycle Validation Failures](#34-lifecycle-validation-failures)
4. [Connection Issues](#4-connection-issues)
   1. [Authentication Failures](#41-authentication-failures)
   2. [Host Unreachable](#42-host-unreachable)
   3. [SSH Key Problems](#43-ssh-key-problems)
5. [Local Execution Issues](#5-local-execution-issues)
   1. [Sudo Authentication Failures](#51-sudo-authentication-failures)
   2. [Sudo TTY Requirements](#52-sudo-tty-requirements)
6. [Vault Issues](#6-vault-issues)
   1. [Vault Not Found](#61-vault-not-found)
   2. [Vault Password File Missing](#62-vault-password-file-missing)
   3. [Secret Merge Problems](#63-secret-merge-problems)
7. [Package Manager Issues](#7-package-manager-issues)
   1. [zypper Issues](#71-zypper-issues)
   2. [apt Issues](#72-apt-issues)
   3. [dnf Issues](#73-dnf-issues)
8. [Reboot Detection Issues](#8-reboot-detection-issues)
9. [Classification Issues](#9-classification-issues)
10. [Summary Issues](#10-summary-issues)
11. [Common Misconfigurations](#11-common-misconfigurations)
12. [Diagnostic Techniques](#12-diagnostic-techniques)
13. [Filing an Issue](#13-filing-an-issue)
14. [Summary](#14-summary)
15. [Notes](#15-notes)

---

## 1. Overview

This guide provides practical troubleshooting procedures for diagnosing and resolving issues encountered while using RunUpdates.

The focus of this document is operational troubleshooting and recovery.

Detailed information regarding execution flow, classification behavior, logging, inventory structure, and schema validation is documented elsewhere.

---

## 2. Purpose

The purpose of this document is to:

* Help operators identify common failures.
* Provide corrective actions.
* Document known failure modes.
* Explain expected system behavior.
* Improve troubleshooting efficiency.

After identifying the symptom, locate the matching section and follow the recommended corrective action.

---

## 3. Inventory Issues

Inventory validation failures occur before execution begins.

Inventory issues are generally reported immediately and prevent host processing.

### 3.1 Invalid YAML

#### Symptoms

* RunUpdates exits immediately.
* YAML parser errors are displayed.
* Inventory validation cannot begin.

#### Fix

* Verify indentation is consistent.
* Verify list formatting is correct.
* Verify keys use valid YAML syntax.
* Validate the YAML file with an external validator.

Example:

```yaml
hosts:
  host01:
    enabled: true
    address:
      - 192.0.2.10
```

---

### 3.2 Unknown Fields

#### Symptoms

* Validation reports unknown fields.
* Inventory validation fails.
* Host normalization does not complete.

#### Fix

* Remove unsupported fields.
* Compare the inventory against `Schema_Reference.md`.
* Verify field names are spelled correctly.

Only documented schema fields are accepted.

---

### 3.3 Address Validation Failures

#### Symptoms

* Validation reports that address formatting is invalid.
* Host validation fails.

#### Fix

The address field must always be a list.

Invalid:

```yaml
address: 192.0.2.10
```

Valid:

```yaml
address:
  - 192.0.2.10
```

Addresses are always represented as a list even when only a single address exists.

---

### 3.4 Lifecycle Validation Failures

#### Symptoms

* Validation reports unknown lifecycle steps.
* Execution planning fails.

#### Fix

Verify that lifecycle entries correspond to defined commands.

Example:

```yaml
lifecycle:
  - check
  - update
  - clean
  - reboot
```

Each lifecycle entry should have a corresponding command definition.

---

## 4. Connection Issues

Connection issues occur after inventory validation but before command execution.

### 4.1 Authentication Failures

#### Symptoms

* Connection attempts fail.
* Host summaries show connection failure.
* Authentication errors appear in logs.

#### Fix

* Verify SSH key permissions.
* Verify vault credentials.
* Verify username definitions.
* Test connectivity manually.

Example:

```bash
ssh user@host -p 2222
```

Correct authentication failures before rerunning RunUpdates.

---

### 4.2 Host Unreachable

#### Symptoms

* Connection timeouts.
* Connection refused errors.
* Network unreachable messages.

#### Fix

* Verify network connectivity.
* Verify routing.
* Verify firewall rules.
* Verify host availability.

If multiple addresses are defined, verify all configured addresses.

---

### 4.3 SSH Key Problems

#### Symptoms

* Key authentication fails.
* Password fallback is unexpectedly used.

#### Fix

Inspect currently loaded keys:

```bash
ssh-add -l
```

Load the intended key:

```bash
ssh-add ~/.ssh/id_rsa
```

Verify file permissions and ownership.

---

## 5. Local Execution Issues

Local execution problems generally affect hosts identified as local systems.

### 5.1 Sudo Authentication Failures

#### Symptoms

* Privileged commands fail.
* Sudo authentication errors appear.
* Lifecycle execution fails.

#### Fix

* Verify password information in the vault.
* Verify sudo access manually.
* Verify account privileges.

Example:

```bash
sudo id
```

Successful execution confirms sudo permissions.

---

### 5.2 Sudo TTY Requirements

#### Symptoms

* Sudo reports TTY requirements.
* Local execution fails despite valid credentials.

#### Fix

Review sudo configuration.

A configuration such as:

```text
Defaults:<user> !requiretty
```

may be required depending on the operating system and environment.

---

## 6. Vault Issues

Vault failures occur before host execution begins.

### 6.1 Vault Not Found

#### Symptoms

* Vault loading fails.
* Execution terminates before processing hosts.

#### Fix

* Verify vault file paths.
* Verify environment variables.
* Verify file permissions.

Confirm both path and readability.

---

### 6.2 Vault Password File Missing

#### Symptoms

* Vault cannot be decrypted.
* Startup validation fails.

#### Fix

* Verify vault password file location.
* Verify environment variables.
* Verify file permissions.

The password file must exist before execution begins.

---

### 6.3 Secret Merge Problems

#### Symptoms

* Credentials appear missing.
* Authentication fails despite inventory correctness.

#### Fix

* Verify vault structure.
* Verify host names match inventory definitions.
* Verify YAML formatting.
* Verify expected keys exist in the vault.

Inventory and vault definitions must align correctly.

---

## 7. Package Manager Issues

Package manager behavior varies by distribution.

### 7.1 zypper Issues

#### Symptoms

* Refresh failures.
* Repository errors.
* Vendor-change warnings.
* Dependency resolution failures.

#### Fix

Refresh repositories manually:

```bash
sudo zypper refresh
```

Inspect repository definitions:

```bash
ls /etc/zypp/repos.d
```

Correct repository issues before rerunning updates.

---

### 7.2 apt Issues

#### Symptoms

* Package lock errors.
* Hash mismatches.
* Dependency configuration issues.

#### Fix

Repair package state:

```bash
sudo dpkg --configure -a
```

Update package metadata:

```bash
sudo apt update
```

Verify package manager health before rerunning RunUpdates.

---

### 7.3 dnf Issues

#### Symptoms

* Metadata cache problems.
* Repository synchronization issues.

#### Fix

Clean the cache:

```bash
sudo dnf clean all
```

Rebuild metadata:

```bash
sudo dnf makecache
```

Verify repositories are accessible.

---

## 8. Reboot Detection Issues

Reboot detection depends upon distribution-specific mechanisms.

### False Positives

#### Symptoms

* Reboot required appears unexpectedly.

#### Fix

Verify the underlying reboot indicator.

Examples include:

* `/var/run/reboot-required`
* `zypper needs-rebooting`
* `needs-restarting -r`

Confirm the actual state directly on the host.

### False Negatives

#### Symptoms

* Reboot appears unnecessary despite updates.

#### Fix

Verify required supporting packages are installed.

Verify reboot commands execute successfully when run manually.

---

## 9. Classification Issues

RunUpdates separates execution from classification.

#### Symptoms

* Classifications appear incorrect.
* Hosts report unexpected states.
* Summary output does not match expectations.

#### Fix

Verify:

* Command execution results.
* Exit codes.
* Command classifications.
* Inventory-defined exit-code mappings.

Classification behavior is defined by inventory configuration and documented in `Error_Classification.md`.

---

## 10. Summary Issues

Summary generation occurs after host processing completes.

### 10.1 Failed Host with Successful Commands

#### Cause

Classification may determine overall failure despite command success.

#### Fix

Review:

* Host summary files.
* Exit-code classifications.
* Repository-health status.
* Error output.

Classifications determine final host status.

---

### 10.2 Missing Summary Files

#### Symptoms

* Host summaries are not generated.
* Fleet summaries are incomplete.

#### Fix

* Verify write permissions.
* Verify summary directory configuration.
* Verify execution was not interrupted.

Summary generation requires successful file access.

---

## 11. Common Misconfigurations

Common issues include:

* Address defined as a scalar instead of a list.
* Invalid lifecycle definitions.
* Missing vault password file.
* Incorrect credentials.
* Invalid command definitions.
* Typographical errors in exit-code mappings.
* YAML indentation mistakes.
* Incorrect host placement beneath distros.

Most configuration issues are detected during validation.

---

## 12. Diagnostic Techniques

RunUpdates provides several troubleshooting approaches.

### 12.1 Enable Debug Output

Run with:

```bash
runupdates --debug
```

Debug output provides additional diagnostic information.

### 12.2 Test Commands Manually

Examples:

```bash
ssh user@host
```

```bash
sudo zypper refresh
```

```bash
sudo apt update
```

```bash
sudo dnf check-update
```

Manual verification often isolates environmental issues quickly.

### 12.3 Validate Inventory

Run:

```bash
runupdates inventory
```

Validation should succeed before attempting updates.

### 12.4 Review Logs

Inspect:

```text
var/logs/
```

Review:

* Lifecycle events.
* Errors.
* Classifications.
* Connection attempts.

Logs are often the fastest path to identifying failures.

---

## 13. Filing an Issue

Consider filing an issue when:

* Classification results appear incorrect.
* Inventory validation rejects valid data.
* Supported distributions behave unexpectedly.
* Summaries contain inconsistent information.
* Unhandled exceptions occur.

Include:

* Sanitized inventory examples.
* Sanitized logs.
* Distribution and version information.
* RunUpdates version information.
* Reproduction steps.

Complete issue reports significantly reduce troubleshooting time.

---

## 14. Summary

RunUpdates uses deterministic validation, execution, classification, and reporting.

Most issues can be isolated by reviewing:

* Inventory validation output.
* Execution logs.
* Host summaries.
* Fleet summaries.
* Classification results.

The troubleshooting process should begin with the earliest reported error, as later failures are often secondary effects of the original problem.

## 15. Notes

This document provides operational guidance for diagnosing and resolving RunUpdates issues.

For related information, see:

* [Build.md](Build.md)
* [Design.md](Design.md)
* [Directory_Structure.md](Directory_Structure.md)
* [Error_Classification.md](Error_Classification.md)
* [Execution_Flow.md](Execution_Flow.md)
* [Inventory.md](Inventory.md)
* [Logging.md](Logging.md)
* [Operation.md](Operation.md)
* [PythonTools.md](PythonTools.md)
* [QuickStart.md](QuickStart.md)
* [Schema_Reference.md](Schema_Reference.md)

Troubleshooting guidance documented here is intended to supplement operational procedures, classification rules, inventory validation, and execution diagnostics.

When troubleshooting an issue, operators should begin by identifying the earliest reported error and then review associated logs, summaries, and classifications before examining later symptoms.