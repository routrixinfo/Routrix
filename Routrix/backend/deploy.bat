@echo off
REM ROUTRIX Backend Deployment Script (Windows)
REM Usage: deploy.bat [development|production]

setlocal enabledelayedexpansion

set ENVIRONMENT=%1
if "!ENVIRONMENT!"=="" set ENVIRONMENT=development

echo.
echo ============================================
echo 🚀 ROUTRIX Backend Deployment
echo Environment: !ENVIRONMENT!
echo ============================================
echo.

REM Check if .env exists
if not exist .env (
    echo ❌ Error: .env file not found!
    echo 📝 Please create .env from .env.example
    exit /b 1
)

REM Create virtual environment if not exists
if not exist venv (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo ✨ Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
if "!ENVIRONMENT!"=="production" (
    pip install -r ..\requirements-prod.txt
) else (
    pip install -r ..\requirements.txt
)

REM Create necessary directories
echo 📁 Creating directories...
if not exist database mkdir database
if not exist uploads mkdir uploads
if not exist banners mkdir banners
if not exist pod_images mkdir pod_images
if not exist media mkdir media
if not exist pdf mkdir pdf
if not exist logs mkdir logs

REM Run application
if "!ENVIRONMENT!"=="production" (
    echo 🔒 Starting in PRODUCTION mode...
    gunicorn -w 4 -b 0.0.0.0:8000 main:app
) else (
    echo 🔨 Starting in DEVELOPMENT mode...
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
)
