#!/bin/bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
STAGING_DIR="$ROOT_DIR/packaging/staging"
OUT_DIR="$ROOT_DIR/packaging/output"
VERSION="$(cat "$ROOT_DIR/VERSION")"

mkdir -p "$OUT_DIR"

SYSTEM_DIR="$STAGING_DIR/opt/RunUpdates"
PORTABLE_DIR="$STAGING_DIR/RunUpdates"

# Clean previous portable tree
rm -rf "$PORTABLE_DIR"
mkdir -p "$PORTABLE_DIR"

# Copy *contents* of system tree into portable tree
cp -a "$SYSTEM_DIR/"* "$PORTABLE_DIR/"

echo "=== Creating TGZ archive ==="
tar -czf "$OUT_DIR/RunUpdates-$VERSION.tgz" \
    -C "$STAGING_DIR" RunUpdates

echo "=== Creating ZIP archive ==="
(
    cd "$STAGING_DIR"
    zip -r "$OUT_DIR/RunUpdates-$VERSION.zip" RunUpdates
)

echo "=== TGZ and ZIP archives created ==="
