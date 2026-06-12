#!/bin/bash
set -e

# Resolve repo root (works locally and in GitHub Actions)
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DIST_DIR="$ROOT_DIR/dist/RunUpdates"
SPEC_FILE="$ROOT_DIR/RunUpdates/RunUpdates.spec"

echo "=== Freezing RunUpdates ==="

# Clean old builds
rm -rf "$ROOT_DIR/build" "$ROOT_DIR/dist"

# Run PyInstaller (assumes venv already active in CI)
pyinstaller "$SPEC_FILE"

# Verify output directory
if [ ! -d "$DIST_DIR" ]; then
    echo "ERROR: PyInstaller did not produce $DIST_DIR"
    exit 1
fi

# Verify frozen binary
FROZEN_BIN="$DIST_DIR/RunUpdates"
if [ ! -f "$FROZEN_BIN" ]; then
    echo "ERROR: Frozen binary missing: $FROZEN_BIN"
    exit 1
fi
if [ ! -x "$FROZEN_BIN" ]; then
    echo "ERROR: Frozen binary exists but is not executable"
    exit 1
fi

# Verify lib directory
if [ ! -d "$DIST_DIR/lib" ]; then
    echo "ERROR: PyInstaller lib directory missing"
    exit 1
fi

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
