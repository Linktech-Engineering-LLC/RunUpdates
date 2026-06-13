#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
PACKAGING_DIR="$ROOT_DIR/packaging"
OUTPUT_DIR="$PACKAGING_DIR/output"
RPMBUILD_DIR="$PACKAGING_DIR/rpmbuild"

# Parse version from VERSION file
VERSION=$(grep -i version "$ROOT_DIR/VERSION" | cut -d '=' -f2 | tr -d ' "')

echo "=== Building RPM package ==="

# Clean rpmbuild tree
rm -rf "$RPMBUILD_DIR"
mkdir -p "$RPMBUILD_DIR"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}

# Copy spec file
cp "$PACKAGING_DIR/rpm/runupdates.spec" "$RPMBUILD_DIR/SPECS/"

# Copy frozen output (the entire tree)
mkdir -p "$RPMBUILD_DIR/SOURCES/RunUpdates"
cp -r "$ROOT_DIR/dist/RunUpdates/"* "$RPMBUILD_DIR/SOURCES/RunUpdates/"

# Build RPM
rpmbuild -bb "$RPMBUILD_DIR/SPECS/runupdates.spec" \
    --define "version $VERSION" \
    --define "_topdir $RPMBUILD_DIR"

# Copy output RPM to packaging/output
mkdir -p "$OUTPUT_DIR"
cp "$RPMBUILD_DIR/RPMS/x86_64/"*.rpm "$OUTPUT_DIR/"

echo "=== RPM build complete ==="
