#!/bin/bash

echo "=========================================="
echo "  Stopping Transcription Services"
echo "=========================================="
echo ""

# Stop Docker services
echo "[1/2] Stopping Docker services..."
docker-compose down

# Stop Whisper service
echo "[2/2] Stopping Whisper Service (Port 8501)..."
lsof -ti:8501 | xargs kill -9 2>/dev/null && echo "      ✓ Whisper stopped" || echo "      (not running)"

echo ""
echo "=========================================="
echo "  All Services Stopped"
echo "=========================================="

