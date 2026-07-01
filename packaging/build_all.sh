#!/bin/bash
set -e

# Resolve repo root (works locally and in GitHub Actions)
ROOT_DIR="$(git rev-parse --show-toplevel)"
DIST_DIR="$ROOT_DIR/dist/RunUpdates"
SPEC_FILE="$ROOT_DIR/RunUpdates/RunUpdates.spec"

echo "=== Freezing RunUpdates ==="

# Clean old builds
rm -rf "$ROOT_DIR/build" "$ROOT_DIR/dist"

# Run PyInstaller (assumes venv already active in CI)
#pyinstaller --onefile RunUpdates/__main__.py --name RunUpdates
python3 scripts/build.py --include-toml .

# Verify frozen binary
# Locate the frozen binary (onefile)
FROZEN_BIN=$(find "$ROOT_DIR/release" -maxdepth 1 -type f -name "RunUpdates" | head -n 1)

if [[ -z "$FROZEN_BIN" ]]; then
    echo "ERROR: PyInstaller did not produce a RunUpdates binary"
    exit 1
fi

echo "Frozen binary: $FROZEN_BIN"

echo "=== Preparing staging tree ==="
rm -rf packaging/staging
mkdir -p packaging/staging/opt/RunUpdates/bin
mkdir -p packaging/staging/opt/RunUpdates/etc
mkdir -p packaging/staging/opt/RunUpdates/var
mkdir -p packaging/staging/opt/RunUpdates/etc/schemata

# Copy frozen binary and support dirs
cp "$FROZEN_BIN" packaging/staging/opt/RunUpdates/bin/
cp -a RunUpdates/etc packaging/staging/opt/RunUpdates/ 2>/dev/null || true
cp -a RunUpdates/var packaging/staging/opt/RunUpdates/ 2>/dev/null || true
cp -a RunUpdates/schema/* packaging/staging/opt/RunUpdates/etc/schemata/

# Ensure rpmbuild directory structure exists
mkdir -p packaging/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SRPMS}

# Copy staging tree into SOURCES
cp -a packaging/staging "$ROOT_DIR/packaging/rpmbuild/SOURCES/"

echo "=== Freeze complete ==="
echo

echo "=== Building DEB package ==="
"$ROOT_DIR/packaging/build_deb.sh"
echo

echo "=== Building RPM package ==="
"$ROOT_DIR/packaging/build_rpm.sh"
echo

echo "=== Building portable TGZ/ZIP ==="
"$ROOT_DIR/packaging/build_tgz_zip.sh"

echo "=== All builds complete ==="
