# BUILD.md

## Build Environment

RunUpdates is developed and tested using a controlled build environment.
The project does not require a specific operating system, virtual
environment layout, container image, or CI platform; however, the
following tools must be available and accessible from the command line.

### Required Toolchain

- Python 3.12 or later
- pip
- PyInstaller
- pytest
- mypy
- ruff
- shellcheck
- yamllint
- jq
- pandoc

Additional tools may be required by individual packaging scripts
depending on the target artifact format being generated.

## Python Dependencies

Project dependencies are defined in `requirements.txt`.

Install project dependencies using:

```bash
python3 -m pip install -r requirements.txt
```

## Verification

Verify that the required development tools are available:

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

## Packaging

Packaging scripts are located under:

`\packaging/`

Generated packages are written to:

`packaging/output/`

Supported package formats may include:

* RPM
* DEB
* TGZ
* ZIP


depending on the target platform and packaging configuration.

## Support Statement

The project is continuously built and validated using an automated build pipeline. Alternative build environments may function correctly; however, only environments that satisfy the documented tool and dependency requirements are expected to produce identical results.
