@echo off
REM ========================================
REM  Install Required Python Packages
REM ========================================

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║      📦 INSTALLING REQUIRED PACKAGES 📦                 ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed!
    echo.
    echo Please install Python first.
    echo Run: check_python.bat for instructions
    echo.
    pause
    exit /b 1
)

echo ✅ Python found!
python --version
echo.

echo ════════════════════════════════════════════════════════════
echo 📥 Installing packages (this may take 1-2 minutes)...
echo ════════════════════════════════════════════════════════════
echo.

echo Installing: flask
pip install flask
if errorlevel 1 goto :error

echo.
echo Installing: flask-sqlalchemy
pip install flask-sqlalchemy
if errorlevel 1 goto :error

echo.
echo Installing: pillow (image processing)
pip install pillow
if errorlevel 1 goto :error

echo.
echo Installing: geopy (GPS calculations)
pip install geopy
if errorlevel 1 goto :error

echo.
echo Installing: pyopenssl (HTTPS certificates)
pip install pyopenssl
if errorlevel 1 goto :error

echo.
echo ════════════════════════════════════════════════════════════
echo ✅ ALL PACKAGES INSTALLED SUCCESSFULLY!
echo ════════════════════════════════════════════════════════════
echo.
echo Installed packages:
pip list | findstr /i "flask pillow geopy pyopenssl sqlalchemy"
echo.
echo ════════════════════════════════════════════════════════════
echo 🎉 SYSTEM READY TO RUN ATTENDANCE APP!
echo ════════════════════════════════════════════════════════════
echo.
echo Next steps:
echo   1. Configure: python setup_wizard.py
echo   2. Start app: start_app.bat
echo.
pause
exit /b 0

:error
echo.
echo ════════════════════════════════════════════════════════════
echo ❌ INSTALLATION FAILED!
echo ════════════════════════════════════════════════════════════
echo.
echo Possible solutions:
echo   1. Run Command Prompt as Administrator
echo   2. Check internet connection
echo   3. Try: python -m pip install [package_name]
echo   4. Disable antivirus temporarily
echo.
echo If problem persists, try:
echo   pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org flask flask-sqlalchemy pillow geopy pyopenssl
echo.
pause
exit /b 1

