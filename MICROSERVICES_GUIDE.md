# 🚀 Microservices Setup & Usage Guide

## Quick Start

```bash
# 1. Make sure models are downloaded
ls -lh models/whisper/large-v3.pt    # Should be ~3GB
du -sh models/pyannote/               # Should be ~31MB+

# 2. Install Python dependencies for model services
pip3 install -r whisper-service/requirements.txt
pip3 install -r pyannote-service/requirements.txt

# 3. Ensure HF_TOKEN is in .env
cat .env | grep HF_TOKEN

# 4. Start all services
./start-all-services.sh

# 5. Open browser
open http://localhost:3501
```

---

## Service Architecture

### What Runs Where

```
Native on Mac (No Docker):
├── Whisper Service   → Port 8501  (2-3 min startup)
└── Pyannote Service  → Port 8502  (1-2 min startup)

Docker Containers:
├── Backend   → Port 5501  (10 sec startup)
└── Frontend  → Port 3501  (10 sec startup)
```

### Why This Design?

**Model Services (Native):**
- ✅ Full access to your 24GB RAM
- ✅ No Docker memory limits
- ✅ Better performance (no virtualization)
- ✅ Easy debugging

**Backend/Frontend (Docker):**
- ✅ Isolated environment
- ✅ Easy to deploy
- ✅ Consistent across machines

---

## Starting Services

### Option 1: All at Once (Easiest)

```bash
./start-all-services.sh
```

Wait ~5 minutes for model services to load, then:
- Whisper: http://localhost:8501/health
- Pyannote: http://localhost:8502/health
- Backend: http://localhost:5501/api/health
- Frontend: http://localhost:3501

### Option 2: Manual (More Control)

**Terminal 1: Start Whisper**
```bash
cd whisper-service
./start.sh

# You'll see:
# Loading Whisper Large v3...
# ✓ Whisper model loaded successfully!
# Starting Flask server on port 8501...
```

**Terminal 2: Start Pyannote**
```bash
cd pyannote-service
./start.sh

# You'll see:
# Loading Pyannote speaker diarization pipeline...
# ✓ Pyannote pipeline loaded successfully!
# Starting Flask server on port 8502...
```

**Terminal 3: Start Docker**
```bash
docker-compose up

# You'll see:
# backend_1   | ✓ All model services are healthy!
# frontend_1  | webpack compiled successfully
```

### Option 3: Selective Start

**Only need transcription (no speakers)?**
```bash
# Start only Whisper
cd whisper-service && ./start.sh

# Backend will work for transcription
# (will skip diarization if Pyannote unavailable)
```

**Only need speaker diarization?**
```bash
# Start only Pyannote
cd pyannote-service && ./start.sh
```

---

## Stopping Services

### Stop Everything

```bash
./stop-all-services.sh
```

### Stop Individual Services

```bash
# Stop Whisper only
lsof -ti:8501 | xargs kill

# Stop Pyannote only
lsof -ti:8502 | xargs kill

# Stop Docker only
docker-compose down
```

---

## Usage Workflow

### 1. Verify Services are Running

```bash
# Check Whisper
curl http://localhost:8501/health
# Expected: {"service": "whisper", "status": "healthy", "model_loaded": true}

# Check Pyannote
curl http://localhost:8502/health
# Expected: {"service": "pyannote", "status": "healthy", "model_loaded": true}

# Check Backend
curl http://localhost:5501/api/health
# Expected: {"status": "healthy", "model_services": {"all_healthy": true}}
```

### 2. List Audio Files

```bash
curl http://localhost:5501/api/audio-files
```

Or open: http://localhost:3501

### 3. Start Transcription

**Via UI:**
- Open http://localhost:3501
- Click "Transcribe" button on any file

**Via API:**
```bash
curl -X POST http://localhost:5501/api/transcribe/mentlist.mp3
```

### 4. Monitor Progress

**Via UI:**
- Progress updates automatically every 5 seconds

**Via API:**
```bash
# Check status
curl http://localhost:5501/api/status/mentlist.mp3

# Watch progress
watch -n 2 'curl -s localhost:5501/api/status/mentlist.mp3 | jq'
```

### 5. View Results

Once status is "completed":

**Via UI:**
- Click "View & Play"
- See synchronized audio + transcript

**Via API:**
```bash
curl http://localhost:5501/api/transcript/mentlist.mp3 | jq
```

---

## Testing Individual Services

### Test Whisper Service Directly

```bash
# Start a transcription job
curl -X POST http://localhost:8501/transcribe \
  -H "Content-Type: application/json" \
  -d '{"filename": "mentlist.mp3"}'

# Returns: {"job_id": "abc-123", "status": "queued"}

# Check progress
curl http://localhost:8501/job/abc-123

# Wait for completion, then get result
curl http://localhost:8501/job/abc-123 | jq '.result'
```

### Test Pyannote Service Directly

```bash
# Start a diarization job
curl -X POST http://localhost:8502/diarize \
  -H "Content-Type: application/json" \
  -d '{"filename": "mentlist.mp3"}'

# Returns: {"job_id": "xyz-789", "status": "queued"}

# Check progress
curl http://localhost:8502/job/xyz-789

# Get result with speaker segments
curl http://localhost:8502/job/xyz-789 | jq '.result.speakers'
```

---

## Troubleshooting

### Issue: "Model services not available"

**Check if services are running:**
```bash
ps aux | grep "python3 app.py"

# Should see:
# whisper-service/app.py
# pyannote-service/app.py
```

**Start missing service:**
```bash
cd whisper-service && ./start.sh  # In new terminal
cd pyannote-service && ./start.sh  # In new terminal
```

### Issue: Services crash on startup

**Whisper crashes:**
```bash
# Check logs
tail -50 logs/whisper-service.log

# Common: Model not found
ls models/whisper/large-v3.pt

# Download if missing
python3 download_models.py
```

**Pyannote crashes:**
```bash
# Check logs
tail -50 logs/pyannote-service.log

# Common: HF_TOKEN issues
echo $HF_TOKEN

# Or license not accepted
# Visit: https://huggingface.co/pyannote/speaker-diarization-3.1
```

### Issue: Backend shows "Service unhealthy"

**Backend can't reach services:**
```bash
# Test from host
curl localhost:8501/health  # Should work
curl localhost:8502/health  # Should work

# Test from Docker
docker exec -it transcription-backend curl http://host.docker.internal:8501/health

# If Docker test fails, check extra_hosts in docker-compose.yml
```

### Issue: Transcription gets stuck

```bash
# Check which service is stuck
curl localhost:8501/jobs  # Whisper jobs
curl localhost:8502/jobs  # Pyannote jobs

# Check logs
tail -f logs/whisper-service.log
tail -f logs/pyannote-service.log

# Restart stuck service
lsof -ti:8501 | xargs kill  # Kill Whisper
cd whisper-service && ./start.sh  # Restart
```

---

## Advanced Usage

### Running Multiple Whisper Instances

```bash
# Start Whisper Large on 8501
cd whisper-service && PORT=8501 python3 app.py &

# Start Whisper Medium on 8503 (faster, less accurate)
cd whisper-service-medium && PORT=8503 python3 app.py &

# Backend can route to either based on file size
```

### Load Balancing

```bash
# Run multiple instances
cd whisper-service && PORT=8501 python3 app.py &
cd whisper-service && PORT=8503 python3 app.py &
cd whisper-service && PORT=8505 python3 app.py &

# Backend round-robins between them
WHISPER_SERVICE_URLS=http://localhost:8501,http://localhost:8503,http://localhost:8505
```

### Development Mode (Hot Reload)

```bash
# Use Flask's debug mode for auto-reload
cd whisper-service
FLASK_DEBUG=1 python3 app.py

# Now changes to app.py auto-reload!
```

---

## Performance Comparison

### Old Monolithic Architecture

```
Docker startup: 2-3 min (loading models)
Docker memory: 10-12GB constant
Crashes: Frequent (exit 137 - OOM)
Flexibility: None (all or nothing)
```

### New Microservices Architecture

```
Service startup: 
  - Whisper: 2-3 min (one-time)
  - Pyannote: 1-2 min (one-time)
  - Docker: 10 seconds

Memory usage:
  - Can kill services when not needed
  - Whisper: 6-8GB (only during processing)
  - Pyannote: 2-3GB (only during processing)

Crashes: None!
Flexibility: Total - run/stop/update each service independently
```

---

## FAQ

**Q: Do I need to run both services?**  
A: Yes, for full transcription with speakers. But you can run just Whisper for transcription-only.

**Q: Can I update Whisper without affecting Pyannote?**  
A: Yes! Just restart Whisper service. Pyannote keeps running.

**Q: What if one service crashes?**  
A: Just restart that service. Others keep running.

**Q: How do I switch to GPU server?**  
A: Update .env with remote URL, restart Docker. Done!

**Q: Can I run Whisper locally and Pyannote remotely?**  
A: Yes! Just set different URLs in .env.

**Q: Do services communicate with each other?**  
A: No! Backend orchestrates them. Services are completely independent.

---

## Next Steps

1. ✅ **Test locally** - Run all services on your Mac
2. ✅ **Verify transcription** - Process a short file first
3. ✅ **Monitor resource usage** - Use Activity Monitor
4. 📋 **Plan remote deployment** - When ready for GPU

---

**Your transcription service is now fully microservices-based!** 🎉

Each model runs independently, giving you maximum flexibility and control.

