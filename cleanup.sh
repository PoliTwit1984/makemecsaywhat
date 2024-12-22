#!/bin/bash

echo "Cleaning up project files..."

# Remove generated audio files
echo "Removing audio files..."
rm -f *.mp3
rm -f *.wav

# Remove database
echo "Removing database..."
rm -f instance/*.db

# Remove Python cache files
echo "Removing Python cache..."
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Remove environment-specific files
echo "Removing environment files..."
rm -f .env

# Remove virtual environment (optional)
if [ "$1" == "--all" ]; then
    echo "Removing virtual environment..."
    rm -rf venv
fi

echo "Cleanup complete!"
echo "To start fresh, run:"
echo "1. ./setup.sh"
echo "2. python test_setup.py"
