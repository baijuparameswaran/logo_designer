#!/bin/bash
# Setup script for Logo Designer

# Display welcome message
echo "====================================="
echo "Logo Designer - Setup Script"
echo "====================================="

# Change to script directory
cd "$(dirname "$0")"

# Check if pipenv is installed
if ! command -v pipenv &> /dev/null; then
    echo "Pipenv is not installed. Installing pipenv..."
    pip install --user pipenv
    
    # Add the user binary directory to PATH if needed
    if ! command -v pipenv &> /dev/null; then
        echo "Please add pipenv to your PATH and try again."
        echo "You can typically do this by adding the following to your .bashrc or .profile:"
        echo "export PATH=\"\$PATH:\$HOME/.local/bin\""
        exit 1
    fi
fi

# Install dependencies
echo "Installing dependencies with pipenv..."
pipenv install

# Install fonts if needed
echo "Checking fonts..."
if [ -x "$(command -v fc-list)" ]; then
    if ! fc-list | grep -i "dejavu\|liberation" > /dev/null; then
        echo "Would you like to install recommended fonts? (y/n)"
        read -r install_fonts
        if [[ $install_fonts =~ ^[Yy]$ ]]; then
            ./install_fonts.sh
        fi
    else
        echo "Required fonts already installed."
    fi
else
    echo "Font utilities not found. You may need to install fonts manually."
fi

# Make scripts executable
chmod +x main.py run_logo_designer.sh install_fonts.sh

echo ""
echo "Setup complete! Run './run_logo_designer.sh' to start the Logo Designer."
echo "====================================="
