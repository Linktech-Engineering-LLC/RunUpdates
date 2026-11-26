 # Build Environment — RunUpdates

**Part of:** RunUpdates
**Document:** Build Environment Reference
**Author:** Leon McClatchey, Linktech Engineering LLC
**License:** MIT
**Requires:** Python 3.12+, Build Toolchain
**Last Updated:** 2026-11-26

## Table of Contents

1. [Overview](#1-overview)
2. [Build Philosophy](#2-build-philosophy)
3. [Required Toolchain](#3-required-toolchain)
4. [Python Dependencies](#4-python-dependencies)
5. [Tool Verification](#5-tool-verification)
6. [Build Process](#6-build-process)
7. [Artifact Generation](#7-artifact-generation)
8. [Packaging Outputs](#8-packaging-outputs)
9. [Notes](#9-notes)

---

## 1. Overview

This document describes the supported build environment,
required development tools, and packaging workflow for
RunUpdates.

The project is built using a standardized toolchain and
automated packaging process. The build environment is
defined by the available toolchain rather than a specific
operating system, container image, or CI implementation.

---

## 2. Build Philosophy

RunUpdates separates build tooling from project
dependencies.

Build tooling is expected to be available in the build
environment, while project-specific dependencies are
installed during the build process.

---

## 3. Required Toolchain

### Build Tools
* Python 3.12 or later
* pip
* PyInstaller

### Development Tools
* pytest
* mypy
* ruff
* shellcheck
* yamllint

### Packaging and Release Tools
* jq
* pandoc

Additional tools may be required by individual packaging scripts
depending on the target artifact format being generated.

---

## 4. Python Dependencies

Project dependencies are defined in `requirements.txt`.

Some builds additionally install PythonTools as a shared
project dependency used by RunUpdates and other Linktech
Engineering projects.

Install project dependencies using:

```bash
python3 -m pip install -r requirements.txt
```

---

## 5. Tool Verification

Verify that the required development tools are available:

```bash
python3 --version
pip --version
pytest --version
mypy --version
ruff --version
shellcheck --version
yamllint --version
pyinstaller --version
jq --version
pandoc --version
```

---

## 6. Build Process

The RunUpdates build process is designed to produce
reproducible artifacts across all supported platforms.

A typical build performs the following operations:

1. Verify availability of the required build toolchain.
2. Check out the source repository.
3. Capture build metadata, including timestamp and source commit identifier.
4. Install project dependencies from `requirements.txt`.
5. Install and verify PythonTools dependencies.
6. Execute the packaging workflow.
7. Collect generated artifacts.
8. Generate release metadata.
9. Publish artifacts to the nightly release.
10. Deploy the generated dashboard.

All release artifacts are generated from the current
repository state at build time.

---

## 7. Artifact Generation

After packaging completes, generated artifacts are
collected and staged for publication.

Each build generates a metadata file describing the
resulting packages. Metadata may include:

* Build date and time
* Source commit hash
* Python version
* PyInstaller version
* Generated artifact list
* Artifact size information
* Checksums
* CRC values

The metadata file is used by dashboards and release
automation to present build information and verify
artifact integrity.

---

## 8. Packaging Outputs

Packaging scripts are located under:

`packaging/`

Generated packages are written to:

`packaging/output/`

Release metadata is generated in:

`artifacts/`

Depending on the target platforms enabled during the
build, the following package formats may be produced:

* RPM
* DEB
* TGZ
* ZIP

Package naming follows the conventions defined by the
packaging scripts and may include version, architecture,
and platform identifiers.

Output artifacts are collected automatically and
published as part of the release generation process.

---

## 9. Notes

The documented toolchain represents the reference build
environment used during development and continuous
integration testing.

Alternative build environments may function correctly;
however, identical results are only expected when the
documented toolchain and dependency requirements are
satisfied.

Project-specific dependencies are intentionally
separated from build tooling to simplify maintenance,
standardize workflows, and support reproducible builds.
