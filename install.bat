@echo off
SETLOCAL ENABLEEXTENSIONS

:: Check for Python and install if not present
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Attempting to install Python...
    :: Specify the version and installer of Python here
    set PYTHON_INSTALLER_URL=https://www.python.org/ftp/python/3.9.1/python-3.9.1-amd64.exe
    set PYTHON_INSTALLER=python-installer.exe

    :: Download Python installer
    echo Downloading Python installer...
    powershell -Command "(New-Object Net.WebClient).DownloadFile('%PYTHON_INSTALLER_URL%', '%PYTHON_INSTALLER%')"

    :: Install Python silently, add to PATH, and do not display the GUI
    echo Installing Python, please wait...
    .\%PYTHON_INSTALLER% /quiet InstallAllUsers=1 PrependPath=1

    :: Clean up installer
    del .\%PYTHON_INSTALLER%

    echo Python installed.
) else (
    echo Python is already installed.
)

:: Wait for Python path to update
timeout /t 5 /nobreak >nul

:: Locate pip
for /f "delims=" %%i in ('where pip') do set PIP_PATH=%%i
if not defined PIP_PATH (
    echo pip is not found. Attempting to use Python -m pip instead.
    set PIP_PATH=python -m pip
)

echo Installing required Python packages...
%PIP_PATH% install PyQt5 requests Pillow

echo Installation complete. You can now run your Python program.
:End
pause
ENDLOCAL
