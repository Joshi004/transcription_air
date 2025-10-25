#!/bin/bash

echo "=========================================="
echo "  Starting Transcription Services"
echo "=========================================="
echo ""

# Get project root
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_ROOT"

# Load environment
if [ -f .env ]; then
    source .env
fi

echo "Starting services in background..."
echo ""

# Start Whisper service
echo "[1/2] Starting Whisper Service (Port 8501)..."
cd whisper-service
export AUDIO_DIR="$PROJECT_ROOT/Audio"
export MODELS_DIR="$PROJECT_ROOT/models/whisper"
nohup python3 app.py > ../logs/whisper-service.log 2>&1 &
WHISPER_PID=$!
echo "      PID: $WHISPER_PID"
sleep 2

# Start Docker services
echo "[2/2] Starting Docker services (Backend + Frontend)..."
cd "$PROJECT_ROOT"
docker-compose up -d

echo ""
echo "=========================================="
echo "  All Services Started!"
echo "=========================================="
echo ""
echo "Service URLs:"
echo "  Frontend:  http://localhost:3501"
echo "  Backend:   http://localhost:5501"
echo "  Whisper:   http://localhost:8501"
echo ""
echo "Process IDs:"
echo "  Whisper:   $WHISPER_PID"
echo ""
echo "Logs:"
echo "  Whisper:   tail -f logs/whisper-service.log"
echo "  Backend:   docker-compose logs -f backend"
echo "  Frontend:  docker-compose logs -f frontend"
echo ""
echo "To stop all services:"
echo "  ./stop-all-services.sh"
echo ""
echo "=========================================="

