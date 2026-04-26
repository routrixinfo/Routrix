#!/bin/bash
# ROUTRIX Backend Deployment Script
# Usage: ./deploy.sh [development|production]

set -e  # Exit on error

ENVIRONMENT=${1:-development}
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "============================================"
echo "🚀 ROUTRIX Backend Deployment"
echo "Environment: $ENVIRONMENT"
echo "============================================"

# Navigate to project directory
cd $PROJECT_DIR

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "📝 Please create .env from .env.example"
    exit 1
fi

# Create virtual environment if not exists
if [ ! -d venv ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✨ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
if [ "$ENVIRONMENT" = "production" ]; then
    pip install -r ../requirements-prod.txt
else
    pip install -r ../requirements.txt
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p database uploads banners pod_images media pdf logs

# Database setup
if [ ! -f database/routrix.db ]; then
    echo "🗄️  Initializing database..."
    python3 -c "
import sqlite3
conn = sqlite3.connect('database/routrix.db')
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS trips (id INTEGER PRIMARY KEY)')
conn.commit()
conn.close()
print('✅ Database initialized')
"
fi

# Run application
if [ "$ENVIRONMENT" = "production" ]; then
    echo "🔒 Starting in PRODUCTION mode..."
    gunicorn -w 4 -b 0.0.0.0:8000 main:app
else
    echo "🔨 Starting in DEVELOPMENT mode..."
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
fi
