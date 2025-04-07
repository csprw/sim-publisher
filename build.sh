#!/usr/bin/env bash

# Stop on any error
set -e

echo "Installing/Upgrading PyInstaller..."
pip install --upgrade pyinstaller

echo "Creating single-file executable with PyInstaller..."
pyinstaller --onefile server.py

echo "Moving config.yaml into the dist/ folder..."
cp config.yaml dist/

echo "Removing .spec file..."
rm -f server.spec

echo "Removing build/ folder..."
rm -rf build/

echo "Done! Your executable and config.yaml can be found in the dist/ directory."
