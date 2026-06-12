#!/bin/bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
STAGING_DIR="$ROOT_DIR/packaging/staging"
OUT_DIR="$ROOT_DIR/packaging/output"
VERSION="$(cat "$ROOT_DIR/VERSION")"
DIST_DIR="$ROOT_DIR/dist/RunUpdates"

echo "=== Building RPM package ==="

# Clean staging
rm -rf "$STAGING_DIR"
mkdir -p "$STAGING_DIR/opt/RunUpdates"

# Copy frozen binary + lib
cp -a "$DIST_DIR/RunUpdates" "$STAGING_DIR/opt/RunUpdates/"
cp -a "$DIST_DIR/lib" "$STAGING_DIR/opt/RunUpdates/"

# Create etc, schemata, var/log
mkdir -p "$STAGING_DIR/opt/RunUpdates/etc"
mkdir -p "$STAGING_DIR/opt/RunUpdates/schemata"
mkdir -p "$STAGING_DIR/opt/RunUpdates/var/log"

# Copy schemata
cp -a "$ROOT_DIR/RunUpdates/schemata/"* "$STAGING_DIR/opt/RunUpdates/schemata/"

# Copy LICENSE
cp "$ROOT_DIR/LICENSE_BINARY.txt" "$STAGING_DIR/opt/RunUpdates/LICENSE"

# Generate env files
ENV_DIR="$STAGING_DIR/opt/RunUpdates/etc"
SKEL_SRC="$ROOT_DIR/RunUpdates/templates"

for f in bash cron systemd; do
    # Copy skeleton into staging
    cp "$SKEL_SRC/$f.env.skel" "$ENV_DIR/$f.env.skel"

    # Apply substitutions and write final .env file
    sed \
      -e "s|@@CONFIG_DIR@@|/opt/RunUpdates/etc|g" \
      -e "s|@@SCHEMA_DIR@@|/opt/RunUpdates/schemata|g" \
      -e "s|@@LOG_DIR@@|/opt/RunUpdates/var/log|g" \
      "$ENV_DIR/$f.env.skel" > "$ENV_DIR/$f.env"
done

# Remove skeletons from final package
rm "$ENV_DIR"/*.env.skel

# Build RPM
mkdir -p ~/rpmbuild/SOURCES
tar -czf ~/rpmbuild/SOURCES/runupdates-$VERSION.tar.gz -C "$STAGING_DIR" opt

rpmbuild -bb "$ROOT_DIR/packaging/runupdates.spec" \
  --define "_version $VERSION" \
  --define "_release 1"

# Normalize RPM filename
RPM_SRC=$(find ~/rpmbuild/RPMS -type f -name "runupdates-*.rpm" | head -n 1)
mv "$RPM_SRC" "$OUT_DIR/RunUpdates_${VERSION}.${ARCH}.rpm"

echo "=== RPM build complete ==="
