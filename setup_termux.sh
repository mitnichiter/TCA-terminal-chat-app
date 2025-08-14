#!/bin/bash

# This script sets up the environment for PyTerminal-Chat on Termux.
# Bish bish bish bish let's get this done!

echo "--- Starting PyTerminal-Chat Setup for Termux ---"
echo ""
echo "############################################################"
echo "# IMPORTANT MANUAL STEP:"
echo "# This script requires the 'Termux:API' app."
echo "# Please install it from the Google Play Store or F-Droid"
echo "# BEFORE you continue."
echo "############################################################"
echo ""
read -p "Have you installed the Termux:API app? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Setup cancelled. Please install the app and run this script again."
    exit 1
fi

# --- Step 1: Update Termux packages ---
echo "[1/2] Updating Termux package lists..."
pkg update -y

# --- Step 2: Install required packages ---
# 'python' is needed to run the client.
# 'termux-api' is needed for the 'termux-notification' command.
echo "[2/2] Installing Python and the Termux API..."
pkg install -y python termux-api

echo ""
echo "--- Termux Setup Complete! ---"
echo "You are all set. Your phone is ready to chat!"
echo "-> On your PC, start the server: python3 server.py"
echo "-> On Termux, start this client: python client_termux.py"
