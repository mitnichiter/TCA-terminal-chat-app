#!/bin/bash

# This script automates the installation of dependencies for PyTerminal-Chat.

echo "--- Starting PyTerminal-Chat Setup ---"

# --- Step 1: Update package lists ---
echo "[1/3] Updating system package lists (requires sudo)..."
sudo apt-get update

# --- Step 2: Install system dependency for desktop notifications ---
# plyer needs this backend on Debian/Ubuntu to show notifications.
echo "[2/3] Installing system dependency for notifications (libnotify-dev)..."
sudo apt-get install -y libnotify-dev

# --- Step 3: Install Python packages using pip ---
echo "[3/3] Installing required Python packages (plyer)..."
# We use pip3 to be sure we're installing for Python 3.
pip3 install plyer

echo ""
echo "--- Setup Complete! ---"
echo "You are all set. You can now run the server and client scripts."
echo "-> To start the server: python3 server.py"
echo "-> To start the client: python3 client.py"
