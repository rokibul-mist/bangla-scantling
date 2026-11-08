@echo off
title Bangladesh Inland Vessel Scantlings Suite
cd /d "%~dp0"

echo ======================================================================
echo    BANGLADESH INLAND VESSEL STATUTORY COMPLIANCE ^& SCANTLINGS APP
echo    Department of Shipping (DOS) SRO 308/Law-2001 ^& ISO 1976
echo ======================================================================
echo.
echo Launching Native Desktop Application (Edge App Mode)...
echo.

python run_app.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Application encountered an issue or Python is not found in PATH.
    echo Please make sure Python 3 is installed and added to PATH.
    echo.
    pause
)
