#!/bin/bash

# Set the name of the virtual environment directory
VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"

# Check if the virtual environment already exists
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  python3 -m venv $VENV_DIR

  echo "Activating virtual environment..."
  source $VENV_DIR/bin/activate

  if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing dependencies from $REQUIREMENTS_FILE..."
    pip install --upgrade pip
    pip install -r $REQUIREMENTS_FILE
  else
    echo "Error: $REQUIREMENTS_FILE not found."
    exit 1
  fi
else
  echo "Virtual environment already exists. Activating..."
  source $VENV_DIR/bin/activate
fi
