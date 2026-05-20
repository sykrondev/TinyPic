@echo off
setlocal
title TinyPic Build

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found.
    pause & exit /b 1
)

pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Dependency install failed.
    pause & exit /b 1
)

if exist dist\TinyPic.exe del /f /q dist\TinyPic.exe
if exist build rmdir /s /q build

pyinstaller tinypic.spec --noconfirm
if errorlevel 1 (
    echo [ERROR] Build failed.
    pause & exit /b 1
)

echo Output: dist\TinyPic.exe
pause
endlocal
