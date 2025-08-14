@echo off
title PyTerminal-Chat Windows Setup

echo.
echo --- Starting PyTerminal-Chat Setup for Windows ---
echo.
echo This script will install the Python packages needed to run the client.
echo.

:: =================================================================
echo [1/1] Installing required Python packages...
echo    - plyer (for desktop notifications)
echo    - windows-curses (for the terminal interface on Windows)
echo.
:: =================================================================

:: Using "py -m pip" is the recommended and most reliable way to run pip on Windows
:: as it avoids issues with multiple Python versions or incorrect PATH setups.
py -m pip install plyer windows-curses

:: Check the exit code of the previous command. 0 means success.
if %errorlevel% neq 0 (
    echo.
    echo *******************************************************************
    echo * ERROR: An error occurred during installation.                     *
    echo * Please make sure you have Python installed and have added it to   *
    echo * your system PATH during the Python installation.                  *
    echo * You can download Python from python.org                           *
    echo *******************************************************************
    echo.
) else (
    echo.
    echo --- Setup Complete! ---
    echo You are all set and ready to chat.
    echo.
    echo -> To start the server:   py server.py
    echo -> To start the client:   py client.py
    echo.
)

echo This window will close after you press any key.
pause
