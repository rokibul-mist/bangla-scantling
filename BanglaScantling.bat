@echo off
title Bangladesh Inland Vessel Scantlings Suite
cd /d "%~dp0"

echo ======================================================================
echo    BANGLADESH INLAND VESSEL STATUTORY SCANTLINGS SUITE
echo    Department of Shipping (DOS) SRO 308/Law-2001 ^& ISO 1976
echo ======================================================================
echo.
echo Launching Native Desktop Application (Edge App Mode)...
echo.

python run_app.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Application exited with error code %ERRORLEVEL%.
    pause
)
