#!/bin/bash
set -e

ROOT_DIR="$(git rev-parse --show-toplevel)"
STAGING_DIR="$ROOT_DIR/packaging/staging"
OUT_DIR="$ROOT_DIR/packaging/output"
VERSION="$(grep -i version $ROOT_DIR/VERSION | cut -d '=' -f2 | tr -d ' "')"

echo "=== Building DEB package ==="

# Locate frozen binary (onefile)
FROZEN_BIN=$(find "$ROOT_DIR/dist" -maxdepth 1 -type f -name "RunUpdates" | head -n 1)

if [[ -z "$FROZEN_BIN" ]]; then
    echo "ERROR: Frozen binary not found"
    exit 1
fi

# Clean staging
rm -rf "$STAGING_DIR"
mkdir -p "$STAGING_DIR/opt/RunUpdates/bin"
mkdir -p "$STAGING_DIR/opt/RunUpdates/etc"
mkdir -p "$STAGING_DIR/opt/RunUpdates/schemata"
mkdir -p "$STAGING_DIR/opt/RunUpdates/var/log"
mkdir -p "$STAGING_DIR/opt/RunUpdates/var/log/summaries"
mkdir -p "$STAGING_DIR/opt/RunUpdates/var/run"

# Copy DEBIAN metadata
cp -a packaging/DEBIAN "$STAGING_DIR/"

# Copy frozen binary
cp "$FROZEN_BIN" "$STAGING_DIR/opt/RunUpdates/bin/RunUpdates"

# Copy schemata
cp -a "$ROOT_DIR/RunUpdates/schema/"* "$STAGING_DIR/opt/RunUpdates/schemata/"

# Copy LICENSE
cp "$ROOT_DIR/LICENSE_BINARY.txt" "$STAGING_DIR/opt/RunUpdates/LICENSE"

# Generate env files
ENV_DIR="$STAGING_DIR/opt/RunUpdates/etc"
SKEL_SRC="$ROOT_DIR/RunUpdates/templates"

for f in bash cron systemd; do
    cp "$SKEL_SRC/$f.env.skel" "$ENV_DIR/$f.env.skel"

    sed \
      -e "s|@@CONFIG_DIR@@|/opt/RunUpdates/etc|g" \
      -e "s|@@SCHEMA_DIR@@|/opt/RunUpdates/schemata|g" \
      -e "s|@@LOG_DIR@@|/opt/RunUpdates/var/log|g" \
      "$ENV_DIR/$f.env.skel" > "$ENV_DIR/$f.env"
done

rm "$ENV_DIR"/*.env.skel

# Build DEB
mkdir -p "$OUT_DIR"
fakeroot dpkg-deb --build "$STAGING_DIR" "$OUT_DIR/RunUpdates_${VERSION}.deb"

echo "=== DEB build complete ==="
