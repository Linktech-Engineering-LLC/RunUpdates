#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
PACKAGING_DIR="$ROOT_DIR/packaging"
OUTPUT_DIR="$PACKAGING_DIR/output"
RPMBUILD_DIR="$PACKAGING_DIR/rpmbuild"
STAGING_DIR="$PACKAGING_DIR/staging"

VERSION=$(grep -i version "$ROOT_DIR/VERSION" \
    | cut -d '=' -f2 \
    | tr -d ' "')

echo "=== Building RPM package ==="

#
# Clean RPM build tree
#
rm -rf "$RPMBUILD_DIR"
mkdir -p "$RPMBUILD_DIR"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}

#
# Verify staging tree exists
#
if [[ ! -d "$STAGING_DIR/opt/RunUpdates" ]]; then
    echo "ERROR: staging tree missing:"
    echo "  $STAGING_DIR/opt/RunUpdates"
    exit 1
fi

#
# Create RPM source tarball
#
echo "Creating source tarball..."

TMPDIR=$(mktemp -d)

TOPDIR="$TMPDIR/RunUpdates-$VERSION"

mkdir -p "$TOPDIR"

cp -a "$STAGING_DIR/opt" "$TOPDIR/"

TARBALL="$RPMBUILD_DIR/SOURCES/RunUpdates-$VERSION.tar.gz"

tar -czf "$TARBALL" \
    -C "$TMPDIR" \
    "RunUpdates-$VERSION"

rm -rf "$TMPDIR"

#
# Copy spec
#
cp "$PACKAGING_DIR/rpm/runupdates.spec" \
   "$RPMBUILD_DIR/SPECS/"

#
# Build RPM
#
echo "Running rpmbuild..."

rpmbuild -ba \
    "$RPMBUILD_DIR/SPECS/runupdates.spec" \
    --define "version $VERSION" \
    --define "_topdir $RPMBUILD_DIR"

#
# Locate output RPM
#
RPM_FILE=$(find "$RPMBUILD_DIR/RPMS" \
    -type f \
    -name "*.rpm" \
    | head -n 1)

if [[ -z "$RPM_FILE" ]]; then
    echo "ERROR: RPM build produced no output"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

cp "$RPM_FILE" "$OUTPUT_DIR/"

echo "RPM built: $RPM_FILE"
echo "Output copied to: $OUTPUT_DIR"
echo "=== RPM build complete ==="