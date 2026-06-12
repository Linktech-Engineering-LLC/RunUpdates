# Building RunUpdates from Source

This document describes how to build RunUpdates from the MIT-licensed source
code. The official binary distributions (RPM, DEB, TGZ, ZIP) include additional
proprietary components and freeze-time integrations that are not required for
source builds.

## 1. Prerequisites

You will need:

- Python 3.11+
- pip
- PyInstaller
- Git
- A Linux environment (recommended for binary parity)

Install PyInstaller:

    pip install pyinstaller

## 2. Clone the Repositories

RunUpdates depends on the internal PythonTools repository.

Clone both:

    git clone https://github.com/linktech-engineering-llc/PythonTools
    git clone https://github.com/linktech-engineeering-llc/RunUpdates

Your directory layout should look like:

    ~/dev/
      PythonTools/
      RunUpdates/

## 3. Install PythonTools Locally

RunUpdates imports PythonTools as a normal Python package.

From inside the PythonTools directory:

    pip install -e .

This makes PythonTools available to the RunUpdates build environment.

## 4. Freeze Rules

The RunUpdates build process uses PyInstaller with custom freeze rules:

- `etc/` and `schemata/` are excluded from the freeze
- PythonTools must be cloned before building
- The frozen build must create:
    - etc/
    - var/log/
    - var/log/summaries/
    - var/run/
- A `.env` file is NOT generated during the freeze
- RPM/DEB/TGZ/ZIP packaging scripts generate backend-specific env files

These rules are implemented in `build.py`.

## 5. Building the Frozen Binary

From inside the RunUpdates directory:

    python build.py

This produces a frozen binary tree under:

    dist/RunUpdates/

## 6. Running the Frozen Build

You must create an environment file before running the frozen binary.

Example:

    export RUNUPDATES_CONFIG=/path/to/etc
    export RUNUPDATES_SCHEMA=/path/to/etc/schemata
    export RUNUPDATES_LOG_DIR=/path/to/var/log

Vault settings must be provided by the user.

## 7. Packaging (Optional)

If you want to build your own RPM/DEB/TGZ/ZIP packages, see:

    packaging/rpm/runupdates.spec
    packaging/deb/
    packaging/tgz/
    packaging/zip/

These scripts replicate the official packaging layout but do not include
proprietary components used in the official binary distributions.

## 8. Support

For questions or contributions, contact:

    Linktech Engineering Support
    support@linktechengineering.net
