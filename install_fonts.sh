#!/bin/bash
# Script to install required fonts for Logo Designer

echo "======================================="
echo "Logo Designer - Font Installer"
echo "======================================="

# Create user fonts directory if it doesn't exist
USER_FONTS_DIR="$HOME/.fonts"
mkdir -p "$USER_FONTS_DIR"

# Function to download and install a font to user directory
download_font() {
    font_url="$1"
    font_name="$2"
    output_file="$USER_FONTS_DIR/$font_name"
    
    echo "Downloading $font_name..."
    if command -v curl >/dev/null; then
        curl -L "$font_url" -o "$output_file"
    elif command -v wget >/dev/null; then
        wget "$font_url" -O "$output_file"
    else
        echo "Error: Neither curl nor wget is installed. Cannot download fonts."
        return 1
    fi
    
    if [ -f "$output_file" ]; then
        echo "Successfully downloaded $font_name"
        return 0
    else
        echo "Failed to download $font_name"
        return 1
    fi
}

# Detect the operating system
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Detected Linux system"
    
    # Try system-wide installation first
    SYSTEM_INSTALL=false
    
    # Check for package manager
    if command -v apt-get >/dev/null; then
        echo "Attempting to install fonts using apt..."
        if sudo apt-get update && sudo apt-get install -y fonts-dejavu fonts-liberation fontconfig; then
            SYSTEM_INSTALL=true
        else
            echo "System-wide installation failed. Will try user installation."
        fi
    elif command -v dnf >/dev/null; then
        echo "Attempting to install fonts using dnf..."
        if sudo dnf install -y dejavu-sans-fonts liberation-fonts; then
            SYSTEM_INSTALL=true
        else
            echo "System-wide installation failed. Will try user installation."
        fi
    elif command -v pacman >/dev/null; then
        echo "Attempting to install fonts using pacman..."
        if sudo pacman -S --noconfirm ttf-dejavu ttf-liberation; then
            SYSTEM_INSTALL=true
        else
            echo "System-wide installation failed. Will try user installation."
        fi
    else
        echo "No supported package manager found. Will install fonts to user directory."
    fi
    
    # If system install failed, download fonts directly
    if [ "$SYSTEM_INSTALL" = false ]; then
        echo "Installing fonts to user directory: $USER_FONTS_DIR"
        
        # Download DejaVu Sans
        download_font "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf" "DejaVuSans.ttf"
        
        # Download Liberation Sans
        download_font "https://github.com/liberationfonts/liberation-fonts/raw/main/liberation-fonts-ttf-2.1.5/LiberationSans-Regular.ttf" "LiberationSans-Regular.ttf"
    fi
    
    # Update font cache
    echo "Updating font cache..."
    if command -v fc-cache >/dev/null; then
        fc-cache -f -v
    else
        echo "Warning: fc-cache not found. You may need to manually refresh your font cache."
    fi
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS"
    
    # Check for homebrew
    if command -v brew >/dev/null; then
        echo "Installing fonts using Homebrew..."
        brew tap homebrew/cask-fonts
        if brew install --cask font-dejavu-sans font-liberation; then
            echo "Successfully installed fonts via Homebrew"
        else
            echo "Homebrew installation failed. Installing to user directory."
            download_font "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf" "DejaVuSans.ttf"
            download_font "https://github.com/liberationfonts/liberation-fonts/raw/main/liberation-fonts-ttf-2.1.5/LiberationSans-Regular.ttf" "LiberationSans-Regular.ttf"
        fi
    else
        echo "Homebrew not found. Installing fonts to user directory."
        download_font "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf" "DejaVuSans.ttf"
        download_font "https://github.com/liberationfonts/liberation-fonts/raw/main/liberation-fonts-ttf-2.1.5/LiberationSans-Regular.ttf" "LiberationSans-Regular.ttf"
    fi
    
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "Detected Windows"
    echo "Installing fonts to user directory..."
    
    # On Windows, fonts should be in a different location
    USER_FONTS_DIR="$APPDATA/Microsoft/Windows/Fonts"
    mkdir -p "$USER_FONTS_DIR"
    
    download_font "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf" "DejaVuSans.ttf"
    download_font "https://github.com/liberationfonts/liberation-fonts/raw/main/liberation-fonts-ttf-2.1.5/LiberationSans-Regular.ttf" "LiberationSans-Regular.ttf"
    
    echo "Note: On Windows, you may need to manually install the downloaded fonts."
    echo "Right-click the font files in $USER_FONTS_DIR and select 'Install'."
fi

echo ""
echo "Font installation completed. You may need to restart your application."
echo "======================================="
