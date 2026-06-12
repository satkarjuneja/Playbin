#!/usr/bin/env bash
# remember to run this from the dist directory itself

set -e
VERSION="2.0.0"
BIN_NAME="playbin"
TARGET="/usr/local/bin/$BIN_NAME"
echo "Installing $BIN_NAME v$VERSION..."


# ---------- Check binary exists ----------
if [ ! -f "./$BIN_NAME" ]; then
    echo "Error: $BIN_NAME binary not found in current directory. remember to run this from the dist directory itself"
    exit 1
fi

# ---------- Check mpv ----------
if ! command -v mpv >/dev/null 2>&1; then
    echo "Warning: mpv is not installed."
    echo "Install it using: sudo dnf install mpv"
fi

# ---------- Check parec ----------
if ! command -v parec >/dev/null 2>&1; then
    echo "Warning: parec is not installed."
    echo "Install it using: sudo dnf install pulseaudio-utils"
fi

# ---------- yt-dlp is bundled ----------
echo "Note: yt-dlp is bundled"

# ---------- Copy binary ----------
echo "Copying to $TARGET..."
sudo cp "./$BIN_NAME" "$TARGET"

# ---------- Set permissions ----------
sudo chmod 755 "$TARGET"
# ---------- Verify install ----------

if command -v $BIN_NAME >/dev/null 2>&1; then
    echo "Installation successful."
    echo "installed playbin ${VERSION} by Satkar Juneja"
    echo "Run using: $BIN_NAME"
else
    echo "Installation failed: binary not in PATH"
    exit 1
fi