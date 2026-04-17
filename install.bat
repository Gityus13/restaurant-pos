@echo off
title POS System Installer
echo ========================================
echo    Restaurant POS System Installer
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

:: Get Python version
for /f "tokens=2" %%I in ('python --version 2^>^&1') do set PYTHON_VERSION=%%I
echo [OK] Python %PYTHON_VERSION% found

:: Create virtual environment
echo Creating virtual environment...
python -m venv pos-venv

:: Activate and install
call pos-venv\Scripts\activate.bat
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

:: Create data directory
mkdir data 2>nul

echo.
echo ========================================
echo    Installation Complete!
echo ========================================
echo.
echo To start the POS system:
echo   pos-venv\Scripts\activate
echo   python app.py
echo.
echo Or double-click run.bat
echo.
echo Default login PIN: 0000 (Admin)
pause