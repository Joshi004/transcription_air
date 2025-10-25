#!/bin/bash

echo "=========================================="
echo "  Starting Whisper Service (Port 8501)"
echo "=========================================="
echo ""

# Get the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Set environment variables
export AUDIO_DIR="$PROJECT_ROOT/Audio"
export MODELS_DIR="$PROJECT_ROOT/models/whisper"

echo "Audio directory: $AUDIO_DIR"
echo "Models directory: $MODELS_DIR"
echo ""

# Check if HF_TOKEN is set (not required for Whisper, but good practice)
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo "Loading .env file..."
    source "$PROJECT_ROOT/.env"
fi

# Check Python dependencies
echo "Checking Python dependencies..."
python3 -c "import whisper; import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  Dependencies not installed!"
    echo "Install with: pip3 install -r requirements.txt"
    echo ""
    exit 1
fi

echo "✓ Dependencies installed"
echo ""
echo "Starting Whisper service..."
echo "Access at: http://localhost:8501"
echo "Health check: http://localhost:8501/health"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the service
cd "$SCRIPT_DIR"
python3 app.py

