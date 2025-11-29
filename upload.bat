@echo off
echo ========================================
echo Uploading to GitHub Repository
echo ========================================
echo.

REM Check if git is installed
where git >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Git is not installed!
    echo.
    echo Please install Git first:
    echo 1. Download from: https://git-scm.com/download/win
    echo 2. Or run: winget install Git.Git
    echo.
    echo Then run this script again.
    pause
    exit /b 1
)

echo Git found! Initializing repository...
echo.

REM Initialize git if not already initialized
if not exist .git (
    git init
    echo Repository initialized.
)

REM Add all files
git add bot.py requirements.txt README.md .gitignore start.bat UPLOAD_TO_GITHUB.md

REM Commit
git commit -m "Initial commit: Multi-language AI Discord bot with music and funny responses"

REM Add remote if not exists
git remote remove origin 2>nul
git remote add origin https://github.com/samir51525/tnx.git

REM Push to GitHub
echo.
echo Pushing to GitHub...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS! Code uploaded to GitHub!
    echo ========================================
    echo Repository: https://github.com/samir51525/tnx
) else (
    echo.
    echo ========================================
    echo ERROR: Push failed!
    echo ========================================
    echo.
    echo Possible reasons:
    echo 1. Not authenticated with GitHub
    echo 2. Repository doesn't exist or you don't have access
    echo 3. Need to set branch: git branch -M main
    echo.
    echo Try running these commands manually:
    echo   git branch -M main
    echo   git push -u origin main
)

pause

