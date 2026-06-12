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
pyinstaller --onefile RunUpdates/__main__.py --name RunUpdates

# Verify frozen binary
# Locate the frozen binary (onefile)
FROZEN_BIN=$(find "$ROOT_DIR/dist" -maxdepth 1 -type f -name "RunUpdates" | head -n 1)

if [[ -z "$FROZEN_BIN" ]]; then
    echo "ERROR: PyInstaller did not produce a RunUpdates binary"
    exit 1
fi

echo "Frozen binary: $FROZEN_BIN"

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
