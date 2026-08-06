#!/usr/bin/env bash
set -e


# --- Configuration ---
PACKAGE_NAME="sefia"
VERSION="2.4.0.1"
ARCHITECTURE="all"
BUILD_DIR="${PACKAGE_NAME}_${VERSION}_${ARCHITECTURE}"


echo "🔨 Starting Debian package creation for ${PACKAGE_NAME}..."


# 1. Clean up any previous build directories
if [ -d "$BUILD_DIR" ]; then
    rm -rf "$BUILD_DIR"
fi


# 2. Recreate standard Debian directory hierarchy
# /usr/bin -> execution wrapper
# /usr/share/sefia-code -> Python script and assets
# /usr/share/pixmaps -> Application icon
# /usr/share/applications -> Desktop launcher shortcut
mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/usr/bin"
mkdir -p "$BUILD_DIR/usr/share/${PACKAGE_NAME}"
mkdir -p "$BUILD_DIR/usr/share/pixmaps"
mkdir -p "$BUILD_DIR/usr/share/applications"


# 3. Verify and copy application assets
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found in the current directory!" >&2
    exit 1
fi


if [ ! -f "sefia-ai.png" ]; then
    echo "⚠️ Warning: sefia-ai.png not found! Creating a placeholder layout..."
    # Fallback placeholder if icon doesn't exist
    touch "$BUILD_DIR/usr/share/pixmaps/sefia-ai.png"
else
    cp sefia-ai.png "$BUILD_DIR/usr/share/pixmaps/sefia-ai.png"
fi


# Copy the core scripts and runtime assets into the package
for asset in main.py sefiachat.py sefiahost.py sefiapod.py sefiaterm.py sefiatoken.py requirements.tx telemetry.py README.md; do
    if [ -f "$asset" ]; then
        cp "$asset" "$BUILD_DIR/usr/share/${PACKAGE_NAME}/"
        chmod 644 "$BUILD_DIR/usr/share/${PACKAGE_NAME}/$asset"
    fi
done


# 4. Create the system execution wrapper script
# This allows users to simply type 'sefia-code' in any terminal to launch it.
cat << 'EOF' > "$BUILD_DIR/usr/bin/${PACKAGE_NAME}"
#!/usr/bin/env bash
# Wrapper to execute Sefia Code from its system destination
python3 /usr/share/sefia/main.py "$@"
EOF
chmod 755 "$BUILD_DIR/usr/bin/${PACKAGE_NAME}"


# 5. Create the GUI Desktop Launcher Entry
cat << EOF > "$BUILD_DIR/usr/share/applications/${PACKAGE_NAME}.desktop"
[Desktop Entry]
Version=2.0
Type=Application
Name=Sefia
Comment=AI-Powered Assistant.
Exec=${PACKAGE_NAME}
Icon=sefia-ai.png
Terminal=true
Categories=AI;ChatBot;Terminal
EOF
chmod 644 "$BUILD_DIR/usr/share/applications/${PACKAGE_NAME}.desktop"


# 6. Create the mandatory Debian metadata Control file
# Added python3-pip and python3-ollama to dependencies (adjust if needed)
cat << EOF > "$BUILD_DIR/DEBIAN/control"
Package: ${PACKAGE_NAME}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: ${ARCHITECTURE}
Depends: python3, python3-pip
Maintainer: Camden Carr <aiventures84@gmail.com.com>
Description: Sefia-AI - a simple CLI client for Ollama models.
EOF


# 7. Compile the package using dpkg-deb
echo "📦 Packing files into .deb archive..."
dpkg-deb --build "$BUILD_DIR"


# Cleanup build workspace safely
rm -rf "$BUILD_DIR"


echo "✅ Success! Created: ${PACKAGE_NAME}_${VERSION}_${ARCHITECTURE}.deb"
