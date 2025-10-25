@echo off
REM BizBooks Management Script for Windows
REM Quick commands to manage your BizBooks system

IF "%1"=="start" GOTO START
IF "%1"=="stop" GOTO STOP
IF "%1"=="restart" GOTO RESTART
IF "%1"=="status" GOTO STATUS
IF "%1"=="urls" GOTO URLS
GOTO HELP

:START
echo.
echo ========================================
echo   Starting BizBooks...
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.9+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation!
    pause
    exit /b 1
)

REM Check if cloudflared is installed
cloudflared --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo ERROR: Cloudflare Tunnel (cloudflared) is not installed!
    echo.
    echo Download from: https://github.com/cloudflare/cloudflared/releases
    echo Install and make sure it's in your PATH
    pause
    exit /b 1
)

REM Install dependencies if needed
IF NOT EXIST "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
    echo Installing dependencies...
    call venv\Scripts\activate.bat
    pip install flask flask-sqlalchemy geopy pillow qrcode
) ELSE (
    call venv\Scripts\activate.bat
)

REM Start Flask app
echo Starting Flask app...
cd modular_app
start /B python app.py > app.log 2>&1
timeout /t 3 /nobreak >nul

REM Start Cloudflare tunnel
echo Starting Cloudflare tunnel...
start /B cloudflared tunnel run bizbooks-attendance > tunnel.log 2>&1

echo.
echo ========================================
echo   BizBooks Started Successfully!
echo ========================================
echo.
echo Your URLs:
echo   https://attendance.bizbooks.co.in/
echo   https://attendance.bizbooks.co.in/admin/login
echo.
echo Press any key to continue...
pause >nul
GOTO END

:STOP
echo.
echo ========================================
echo   Stopping BizBooks...
echo ========================================
echo.

REM Stop Flask app (port 5001)
FOR /F "tokens=5" %%P IN ('netstat -ano ^| findstr :5001') DO (
    taskkill /PID %%P /F >nul 2>&1
)
echo Flask app stopped

REM Stop Cloudflare tunnel
taskkill /F /IM cloudflared.exe >nul 2>&1
echo Cloudflare tunnel stopped

echo.
echo BizBooks stopped successfully!
echo.
pause
GOTO END

:RESTART
echo.
echo ========================================
echo   Restarting BizBooks...
echo ========================================
echo.
CALL :STOP
timeout /t 2 /nobreak >nul
CALL :START
GOTO END

:STATUS
echo.
echo ========================================
echo   BizBooks Status
echo ========================================
echo.

REM Check Flask app
netstat -ano | findstr :5001 >nul 2>&1
IF ERRORLEVEL 1 (
    echo Flask app: NOT RUNNING
) ELSE (
    echo Flask app: RUNNING (port 5001)
)

REM Check Cloudflare tunnel
tasklist | findstr cloudflared.exe >nul 2>&1
IF ERRORLEVEL 1 (
    echo Cloudflare tunnel: NOT RUNNING
) ELSE (
    echo Cloudflare tunnel: RUNNING
    echo.
    echo URLs:
    echo   https://attendance.bizbooks.co.in/
    echo   https://attendance.bizbooks.co.in/admin/login
)

echo.
echo Press any key to continue...
pause >nul
GOTO END

:URLS
echo.
echo ========================================
echo   BizBooks URLs
echo ========================================
echo.
echo Employee Attendance:
echo   https://attendance.bizbooks.co.in/
echo.
echo Admin Dashboard:
echo   https://attendance.bizbooks.co.in/admin/login
echo   Username: admin
echo   Password: admin123
echo.
echo Inventory:
echo   https://attendance.bizbooks.co.in/admin/inventory
echo.
echo ========================================
echo.
pause
GOTO END

:HELP
echo.
echo ========================================
echo   BizBooks Management Commands
echo ========================================
echo.
echo   manage_bizbooks.bat start      - Start all services
echo   manage_bizbooks.bat stop       - Stop all services
echo   manage_bizbooks.bat restart    - Restart all services
echo   manage_bizbooks.bat status     - Check service status
echo   manage_bizbooks.bat urls       - Show all URLs
echo.
echo Example: manage_bizbooks.bat start
echo.
echo ========================================
pause
GOTO END

:END

