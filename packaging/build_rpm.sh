#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
PACKAGING_DIR="$ROOT_DIR/packaging"
OUTPUT_DIR="$PACKAGING_DIR/output"
RPMBUILD_DIR="$PACKAGING_DIR/rpmbuild"
STAGING_DIR="$PACKAGING_DIR/staging"

# Parse version from VERSION file
VERSION=$(grep -i version "$ROOT_DIR/VERSION" | cut -d '=' -f2 | tr -d ' "')

echo "=== Building RPM package ==="

# Clean rpmbuild tree
rm -rf "$RPMBUILD_DIR"
mkdir -p "$RPMBUILD_DIR"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}

# Copy spec file
cp "$PACKAGING_DIR/rpm/runupdates.spec" "$RPMBUILD_DIR/SPECS/"

# Ensure staging tree exists
if [[ ! -d "$STAGING_DIR/opt/RunUpdates" ]]; then
    echo "ERROR: Staging tree missing: $STAGING_DIR/opt/RunUpdates"
    exit 1
fi

echo "Using staging tree:"
tree "$STAGING_DIR/opt/RunUpdates" || true

# Copy full staging tree into SOURCES
# IMPORTANT: This preserves EXACTLY:
#   SOURCES/RunUpdates/opt/RunUpdates/...
mkdir -p "$RPMBUILD_DIR/SOURCES/RunUpdates"
cp -a "$STAGING_DIR/opt" "$RPMBUILD_DIR/SOURCES/RunUpdates/"

# Build RPM
rpmbuild -bb "$RPMBUILD_DIR/SPECS/runupdates.spec" \
    --define "version $VERSION" \
    --define "_topdir $RPMBUILD_DIR"

# Copy output RPM to packaging/output
mkdir -p "$OUTPUT_DIR"

RPM_FILE=$(find "$RPMBUILD_DIR/RPMS" -type f -name "*.rpm" | head -n 1)

if [[ -z "$RPM_FILE" ]]; then
    echo "ERROR: RPM build produced no output"
    exit 1
fi

echo "RPM built: $RPM_FILE"

cp "$RPM_FILE" "$OUTPUT_DIR/"

echo "=== RPM build complete ==="
echo "Output copied to: $OUTPUT_DIR"
