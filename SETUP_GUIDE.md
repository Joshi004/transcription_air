# Quick Setup Guide

Follow these steps to get your transcription service running:

## Prerequisites Check

- [ ] Docker installed: `docker --version`
- [ ] Docker Compose installed: `docker-compose --version`
- [ ] Python 3.10+ installed: `python3 --version`

## Step-by-Step Setup

### 1. Navigate to Project Directory

```bash
# Navigate to project directory
cd /Users/nareshjoshi/Documents/TetherWorkspace/TranscriptionService
```

### 2. Install Whisper Service Dependencies

Install Python dependencies needed for the Whisper service:

```bash
# Install Python dependencies for Whisper service
pip3 install -r whisper-service/requirements.txt
```

**Expected output:**
```
Successfully installed openai-whisper torch torchaudio ...
```

The Whisper model (~3GB) will be downloaded automatically on first run.

### 3. Verify Audio Files

Make sure you have audio files in the `Audio/` directory:

```bash
ls Audio/
# Should show: mentlist.mp3 (or your audio files)
```

Supported formats: `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`

### 4. Build Docker Containers

```bash
# Build both frontend and backend containers
docker-compose build
```

**Expected output:**
```
Building backend...
Building frontend...
Successfully built...
Successfully tagged...
```

This may take 5-10 minutes on first build.

### 5. Start All Services

```bash
# Start Whisper service, backend, and frontend
./start-all-services.sh
```

**What to expect:**
- Whisper service will start on port 8501 (2-3 minutes to load model)
- Backend will start on port 5501
- Frontend will start on port 3501
- Total startup time: ~3-4 minutes

**Look for these messages:**
```
[1/2] Starting Whisper Service (Port 8501)...
      PID: 12345
[2/2] Starting Docker services (Backend + Frontend)...
✓ All Services Started!
```

### 6. Access the Application

Open your browser:
```
http://localhost:3501
```

You should see the Transcription Service UI with your audio files listed!

## Verification Checklist

- [ ] Whisper health check: `curl http://localhost:8501/health`
  - Should return: `{"service": "whisper", "status": "healthy", "model_loaded": true}`

- [ ] Backend health check: `curl http://localhost:5501/api/health`
  - Should return: `{"status": "healthy", "backend": "running"}`

- [ ] Frontend accessible: Open `http://localhost:3501`
  - Should show "Transcription Service" title

- [ ] Audio files visible: Check if `mentlist.mp3` appears in the list

- [ ] Can click "Transcribe" button without errors

## Common Issues

### Issue: Whisper service won't start

**Solution:**
```bash
# Check logs
tail -f logs/whisper-service.log

# Verify Python dependencies
pip3 install -r whisper-service/requirements.txt

# Check if port is in use
lsof -i :8501
```

### Issue: "Models not loaded" in health check

**Solution:**
1. Check Whisper service logs: `tail -f logs/whisper-service.log`
2. Verify model directory exists: `ls -l models/whisper/`
3. Ensure sufficient disk space (~3GB) and RAM (~6-8GB)
4. Restart Whisper service: `cd whisper-service && ./start.sh`

### Issue: Port already in use

**Solution:**
```bash
# Check what's using the ports
lsof -i :8501  # Whisper
lsof -i :5501  # Backend
lsof -i :3501  # Frontend

# Kill the process if needed
lsof -ti:8501 | xargs kill
```

### Issue: Docker build fails

**Solution:**
```bash
# Clean up Docker
docker-compose down -v
docker system prune -a

# Rebuild
docker-compose build --no-cache
docker-compose up
```

## Next Steps

Once everything is running:

1. **Test with a short file first** (2-3 min audio) to verify the pipeline works
2. **Monitor processing**: Processing takes ~15-25 min for 30-min audio on CPU
3. **Check transcripts**: They'll appear in `transcripts/` directory as JSON files
4. **Play & view**: Click "View & Play" to see synchronized playback

## Stopping the Services

```bash
# Stop all services (Whisper + Docker)
./stop-all-services.sh
```

## Viewing Logs

```bash
# Whisper logs
tail -f logs/whisper-service.log

# Backend logs
docker-compose logs -f backend

# Frontend logs
docker-compose logs -f frontend
```

---

**Need help?** Check the main README.md or the Troubleshooting section!

