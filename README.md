# Logo Designer

A Python application for designing logos with text and exporting them to PNG files.

## Features

- Create text-based logos with customizable fonts
- Choose from a variety of system fonts
- Apply 2D or 3D text effects
- Set text color (solid or gradient)
- Set background color (solid or gradient)
- Adjust canvas size
- Save logos as PNG files

## Installation

### Quick Start (Recommended)

1. Make sure you have Python installed (Python 3.6+)

2. Clone or download this repository and navigate to the directory

3. Run the setup script to install everything:
   ```
   ./setup.sh
   ```

4. Start the application:
   ```
   ./run_logo_designer.sh
   ```

### Manual Installation

1. Make sure you have Python installed (Python 3.6+)

2. Install pipenv if you don't have it:
   ```
   pip install --user pipenv
   ```

3. Install dependencies with pipenv:
   ```
   pipenv install
   ```

4. Run the application directly with pipenv:
   ```
   pipenv run python main.py
   ```

3. Run the setup script:
```bash
chmod +x setup.sh
./setup.sh
```

This will install Pipenv if needed and set up all dependencies.

Alternatively, you can set up manually:

1. Install Pipenv if you don't have it:
```bash
pip install pipenv
```

2. Install dependencies using Pipenv:
```bash
pipenv install
```

## Usage

### Using the provided script
```bash
# Make the run script executable
chmod +x run.sh

# Run the script
./run.sh
```

### Running directly with Pipenv
```bash
# Basic Logo Designer
pipenv run python main.py

# Advanced Logo Designer
pipenv run python advanced.py
```

## Creating Logos

1. Set your canvas size using the width and height controls
2. Enter your logo text
3. Choose a font and size
4. Apply styling (colors, 3D effect, etc.)
5. For the advanced version, add multiple text elements and apply effects
6. Click "Save Logo" to export your design

## Examples

Check the `examples/` directory for sample logo designs and ideas.

## Requirements

The following dependencies will be automatically installed by Pipenv:
- Python 3.6+
- Pillow (PIL Fork)
- NumPy

You also need:
- Tkinter (usually included with Python)

## License

This project is open source and available for personal and commercial use.
