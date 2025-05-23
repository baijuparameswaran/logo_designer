#!/bin/bash
# Launch Logo Designer using pipenv environment

# Change to script directory
cd "$(dirname "$0")"

# Check if pipenv is installed
if ! command -v pipenv &> /dev/null; then
    echo "Pipenv not found. Installing pipenv..."
    pip install --user pipenv
    
    # Add the user binary directory to PATH if needed
    if ! command -v pipenv &> /dev/null; then
        echo "Please add pipenv to your PATH and try again."
        echo "You can typically do this by adding the following to your .bashrc or .profile:"
        echo "export PATH=\"\$PATH:\$HOME/.local/bin\""
        exit 1
    fi
fi

# Install dependencies if needed
echo "Setting up environment..."
pipenv install

# Run the app with pipenv
echo "Starting Logo Designer..."
pipenv run python main.py
