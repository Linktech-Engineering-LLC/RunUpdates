#!/usr/bin/env bash
set -euo pipefail

# ------------------------------------------------------------
# Defaults
# ------------------------------------------------------------
PREFIX="/opt/RunUpdates"
INSTALL_SYSTEMD=false
INSTALL_CRON=false

# ------------------------------------------------------------
# Parse arguments
# ------------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        --prefix)
            PREFIX="$2"
            shift 2
            ;;
        --systemd)
            INSTALL_SYSTEMD=true
            shift
            ;;
        --cron)
            INSTALL_CRON=true
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done

echo "Installing RunUpdates to: $PREFIX"

# ------------------------------------------------------------
# Validate frozen binary exists
# ------------------------------------------------------------
if [[ ! -f "release/RunUpdates" ]]; then
    echo "ERROR: Frozen RunUpdates binary not found in release/RunUpdates"
    echo "This installer expects the binary to be produced by GitHub Actions."
    exit 1
fi

# ------------------------------------------------------------
# Create directory structure
# ------------------------------------------------------------
mkdir -p "$PREFIX/bin"
mkdir -p "$PREFIX/etc/schema"
mkdir -p "$PREFIX/var/log"
mkdir -p "$PREFIX/var/run"

# ------------------------------------------------------------
# Copy frozen binary
# ------------------------------------------------------------
cp release/RunUpdates "$PREFIX/bin/"
chmod +x "$PREFIX/bin/RunUpdates"

# ------------------------------------------------------------
# Copy templates
# ------------------------------------------------------------
cp -r RunUpdates/schema/* "$PREFIX/etc/schema/"
cp RunUpdates/etc/hosts.template.yml "$PREFIX/etc/"

# ------------------------------------------------------------
# Generate .env files from skeletons
# ------------------------------------------------------------
generate_env() {
    local skel="$1"
    local out="$2"

    sed \
        -e "s|RUNUPDATES_CONFIG=|RUNUPDATES_CONFIG=$PREFIX/etc|" \
        -e "s|RUNUPDATES_SCHEMA=|RUNUPDATES_SCHEMA=$PREFIX/etc/schema|" \
        -e "s|RUNUPDATES_LOG_DIR=|RUNUPDATES_LOG_DIR=$PREFIX/var/log|" \
        "$skel" > "$out"
}

generate_env "packaging/systemd.env.skel" "$PREFIX/etc/systemd.env"
generate_env "packaging/cron.env.skel" "$PREFIX/etc/cron.env"

# ------------------------------------------------------------
# bash.env gets user guidance comments
# ------------------------------------------------------------
sed \
    -e "s|export RUNUPDATES_CONFIG=|export RUNUPDATES_CONFIG=$PREFIX/etc|" \
    -e "s|export RUNUPDATES_SCHEMA=|export RUNUPDATES_SCHEMA=$PREFIX/etc/schema|" \
    -e "s|export RUNUPDATES_LOG_DIR=|export RUNUPDATES_LOG_DIR=$PREFIX/var/log|" \
    packaging/bash.env.skel > "$PREFIX/etc/bash.env"

cat >> "$PREFIX/etc/bash.env" <<EOF

# ------------------------------------------------------------
# VAULT SETTINGS (USER MUST FILL THESE IN)
# ------------------------------------------------------------
# export RUNUPDATES_VAULT_PATH=/path/to/ansible/vault.yml
# export RUNUPDATES_VAULT_PASSWORD_FILE=/path/to/password/file
EOF

echo "Generated systemd.env, cron.env, and bash.env."

# ------------------------------------------------------------
# Install systemd user service/timer (optional)
# ------------------------------------------------------------
if [[ "$INSTALL_SYSTEMD" == true ]]; then
    echo "Installing systemd user service..."

    mkdir -p "$HOME/.config/systemd/user"

    cp packaging/runupdates.service "$HOME/.config/systemd/user/"
    cp packaging/runupdates.timer "$HOME/.config/systemd/user/"

    systemctl --user daemon-reload
    systemctl --user enable runupdates.timer

    echo "Systemd user service installed and timer enabled."
fi

# ------------------------------------------------------------
# Install cron entry (optional)
# ------------------------------------------------------------
if [[ "$INSTALL_CRON" == true ]]; then
    echo "Installing cron entry..."

    # Append cron job if not already present
    (crontab -l 2>/dev/null | grep -v "RunUpdates summary" ; \
     echo "* * * * * . $PREFIX/etc/cron.env && $PREFIX/bin/RunUpdates summary") \
     | crontab -

    echo "Cron entry installed."
fi

echo "RunUpdates installation complete."
