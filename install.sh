#!/bin/bash

# Configuration setup
APP_NAME="sefia-code"
VERSION="alpha0.1.8"
TAR_URL="https://github.com/camdencarr84-jpg/Sefia-AI/archive/refs/tags/alpha0.1.8.tar.gz"
INSTALL_DIR="$HOME/.local/share/sefia"
BIN_DIR="$HOME/.local/bin"

# Terminal colors
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
RESET="\033[0m"

echo -e "${GREEN}Starting installer for Sefia AI ($VERSION)...${RESET}"

# Make sure Ollama is installed locally
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}[WARNING] Ollama is not detected in your PATH.${RESET}"
    echo -e "Make sure Ollama is installed and running so Sefia can access your local models."

fi

# Ensure directory structure exists
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

# Download the source archive from GitHub
echo "Downloading source code..."
TEMP_TAR=$(mktemp)
if ! curl -sL "$TAR_URL" -o "$TEMP_TAR"; then
    echo -e "${RED}[ERROR] Failed to download source archive.${RESET}"
    exit 1
fi

echo "Extracting files..."
tar -xzf "$TEMP_TAR" -C "$INSTALL_DIR" --strip-components 1
rm "$TEMP_TAR"

# Set up isolated virtual environment for dependencies
echo "Setting up isolated Python environment..."
cd "$INSTALL_DIR" || exit 1
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install ollama requests

# Generate launcher wrapper script
echo "Creating terminal execution wrapper..."
LAUNCHER="$BIN_DIR/$APP_NAME"

cat << EOF > "$LAUNCHER"
#!/bin/bash
# Move to Sefia folder so context/model text files read and write locally
cd "$INSTALL_DIR"
source venv/bin/activate
python3 main.py "\$@"
EOF

chmod +x "$LAUNCHER"

# Automatic PATH verification and injection
echo "Checking your terminal environment PATH..."
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    # Figure out if user runs zsh or bash
    SHELL_RC=""
    if [[ "$SHELL" == */zsh ]]; then
        SHELL_RC="$HOME/.zshrc"
    elif [[ "$SHELL" == */bash ]]; then
        SHELL_RC="$HOME/.bash_profile"
        [ ! -f "$SHELL_RC" ] && SHELL_RC="$HOME/.bashrc"
    fi

    if [ -n "$SHELL_RC" ] && [ -f "$SHELL_RC" ]; then
        echo "Adding $BIN_DIR to PATH inside $SHELL_RC..."
        echo -e "\n# Sefia AI Path Customization\nexport PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$SHELL_RC"
        PATH_ADDED=true
    else
        PATH_ADDED=false
    fi
else
    PATH_ADDED=true
fi

echo -e "\n${GREEN}Installation Complete${RESET}"
echo -e "Sefia AI has been successfully installed to: $INSTALL_DIR"
    echo -e "\n[SUCCESS] The command '$APP_NAME' has been added to your PATH."
    echo -e "Restart your terminal or run this command to update your window:"
    echo -e "  ${YELLOW}source $SHELL_RC${RESET}"
    echo -e "Then run: ${GREEN}$APP_NAME${RESET}"
else
    echo -e "\n[MANUAL STEP REQUIRED] Could not automatically update your shell config."
    echo -e "Please add this line to your terminal profile manually to enable global execution:"
    echo -e "  export PATH=\"\$HOME/.local/bin:\$PATH\""
fi
