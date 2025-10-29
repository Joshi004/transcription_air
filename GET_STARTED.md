# 🚀 Getting Started

## What You Have Now

✅ **Whisper Service** - Independent transcription service (Port 8501)  
✅ **Backend** - Lightweight API orchestrator (Port 5501, Docker)  
✅ **Frontend** - React UI (Port 3501, Docker)  

All services are **independent** - you can start/stop each one separately!

---

## 🎯 First Time Setup (4 Steps)

### Step 1: Verify Models Are Downloaded

```bash
cd /Users/nareshjoshi/Documents/TetherWorkspace/TranscriptionService

# Check Whisper
ls -lh models/whisper/large-v3.pt
# Should show: ~3GB file
```

✅ **If model is present, skip to Step 2**

❌ **If model is missing:**
```bash
# Download model by starting Whisper service
# It will download automatically on first run
cd whisper-service
python3 app.py
```

---

### Step 2: Install Python Dependencies (For Whisper Service)

```bash
# Install Whisper dependencies
pip3 install -r whisper-service/requirements.txt

# This installs:
# - Whisper + dependencies (~5 min)
# - PyTorch and other ML libraries
```

---

### Step 3: Start All Services

```bash
# One command starts everything!
./start-all-services.sh
```

**What happens:**
```
[1/2] Starting Whisper Service...
      Loading model (2-3 minutes)...
      ✓ Listening on port 8501

[2/2] Starting Docker services...
      Backend starting...
      Frontend starting...
      ✓ All services ready!
```

**Total startup time: ~3-4 minutes** (first time, then faster)

---

### Step 4: Access the Application

Open your browser:

```
http://localhost:3501
```

You should see:
- 🎙️ Transcription Service
- List of audio files
- "Transcribe" button on each file

---

## 🧪 Quick Test

### 1. Verify Services Are Healthy

```bash
# Test Whisper
curl http://localhost:8501/health
# Expected: {"service": "whisper", "status": "healthy", "model_loaded": true}

# Test Backend
curl http://localhost:5501/api/health
# Expected: {"status": "healthy", "backend": "running"}
```

### 2. List Audio Files

```bash
curl http://localhost:5501/api/audio-files | jq
```

Should show your audio files.

### 3. Start First Transcription

**Option A: Via UI (Recommended)**
1. Open http://localhost:3501
2. Click "Transcribe" on mentlist.mp3
3. Wait ~15-25 minutes (shows progress)
4. Click "View & Play" when complete

**Option B: Via API**
```bash
# Start transcription
curl -X POST http://localhost:5501/api/transcribe/mentlist.mp3

# Monitor progress
watch -n 2 'curl -s localhost:5501/api/status/mentlist.mp3 | jq'

# When complete, get transcript
curl http://localhost:5501/api/transcript/mentlist.mp3 | jq
```

---

## ⏱️ What to Expect

### First Transcription Timeline

```
Minute 0:00 - Click "Transcribe"
Minute 0:01 - Backend starts Whisper job
              Whisper job: started

Minute 0-20 - Whisper processing (transcribing audio)
              Progress updates every 5 seconds

Minute 20:00 - Whisper completes
Minute 20:01 - Backend saves transcript
Minute 20:02 - UI shows "View & Play" button

Total: ~15-25 minutes for 30-min audio
```

---

## 🎯 Success Indicators

You'll know it's working when:

1. ✅ All health checks return "healthy"
2. ✅ Frontend shows your audio files
3. ✅ "Transcribe" button is clickable
4. ✅ Progress updates appear after clicking
5. ✅ Transcript appears after processing
6. ✅ Audio plays with synchronized text

---

## 🔄 Daily Workflow

### Option 1: Keep Services Running

```bash
# Start once in the morning
./start-all-services.sh

# Use throughout the day
# Services stay loaded (faster subsequent transcriptions)

# Stop at night
./stop-all-services.sh
```

### Option 2: Start/Stop as Needed

```bash
# Before transcribing
./start-all-services.sh

# After transcription completes
./stop-all-services.sh

# Next transcription
./start-all-services.sh
```

---

## 💡 Pro Tips

### 1. Test with Short File First

Before processing 30-min audio:
```bash
# Use a 2-3 minute audio clip
# Completes in ~2-3 minutes
# Verifies everything works!
```

### 2. Monitor Logs During First Run

```bash
# Terminal 1: Whisper logs
tail -f logs/whisper-service.log

# Terminal 2: Backend logs
docker-compose logs -f backend
```

### 3. Check Progress via API

```bash
# Real-time progress
watch -n 2 'curl -s localhost:5501/api/status/mentlist.mp3 | \
  jq "{status, progress}"'
```

### 4. Save PIDs for Easy Management

```bash
# After starting services
echo "Whisper PID: $(lsof -ti:8501)" > .service-pids

# Later, to stop
cat .service-pids | cut -d: -f2 | xargs kill
```

---

## 📞 Need Help?

### Check Documentation

- **GET_STARTED.md** (this file) - Initial setup
- **ARCHITECTURE.md** - How it works
- **README.md** - Complete reference
- **QUICK_REFERENCE.md** - Command cheatsheet

### Check Logs

```bash
tail -f logs/whisper-service.log
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Check Service Health

```bash
curl localhost:8501/health | jq
curl localhost:5501/api/health | jq
```

---

## ✨ Ready to Start!

Run this now:

```bash
./start-all-services.sh
```

Wait 3-4 minutes, then open http://localhost:3501

**Enjoy your transcription system!** 🎙️

---

## 🔧 Managing Services

### Check What's Running

```bash
# List all services
ps aux | grep "python3 app.py"

# Check ports
lsof -i :8501  # Whisper
lsof -i :5501  # Backend
lsof -i :3501  # Frontend
```

### Stop Individual Services

```bash
# Stop only Whisper (if you need RAM)
lsof -ti:8501 | xargs kill
# Backend, Frontend keep running

# Stop Docker only
docker-compose down
# Whisper keeps running
```

### Stop Everything

```bash
./stop-all-services.sh
```

---

## 📋 Typical Usage Session

```bash
# Morning: Start services
./start-all-services.sh
# ☕ Get coffee while Whisper model loads (3 min)

# Use the UI
open http://localhost:3501
# Transcribe audio files

# Check logs if needed
tail -f logs/whisper-service.log

# Afternoon: Need RAM for other work?
lsof -ti:8501 | xargs kill  # Stop Whisper
# Docker keeps running (uses minimal RAM)

# Evening: Stop everything
./stop-all-services.sh
```

---

## 🌟 Cool Things You Can Do Now

### 1. Run Only What You Need

```bash
# Just transcription
cd whisper-service && ./start.sh
docker-compose up
```

### 2. Test Different Models

```bash
# Run Whisper Medium (faster) instead of Large
cd whisper-service
# Edit app.py: whisper.load_model("medium")
python3 app.py

# Compare results!
```

### 3. Monitor Resource Usage

```bash
# Watch Whisper memory
watch -n 1 'ps aux | grep whisper-service | grep -v grep'

# Activity Monitor: Filter by "python3"
```

---

## 🐛 Troubleshooting

### Services Won't Start

```bash
# Check Python version
python3 --version  # Should be 3.10+

# Check dependencies
pip3 list | grep whisper

# Install if missing
pip3 install -r whisper-service/requirements.txt
```

### Backend Can't Connect to Whisper

```bash
# Test from host
curl localhost:8501/health  # Should work

# Test from Docker
docker exec transcription-backend \
  curl http://host.docker.internal:8501/health

# If Docker fails, check docker-compose.yml has:
# extra_hosts:
#   - "host.docker.internal:host-gateway"
```

### Transcription Fails

```bash
# Check Whisper jobs
curl localhost:8501/jobs

# Check logs
tail -50 logs/whisper-service.log
docker-compose logs backend
```

---

## 📖 Next Steps

1. **Read ARCHITECTURE.md** - Understand the design
2. **Test with short file** - 2-3 min audio first
3. **Process your 30-min file** - Will take 15-25 min
4. **Plan GPU deployment** - When you want 10x speed

---

## 🎉 You're All Set!

Your transcription service is now:

✅ **Production-ready** - Stable, no crashes  
✅ **Microservices-based** - Independent Whisper service  
✅ **Flexible** - Start/stop services individually  
✅ **Scalable** - Easy to move to GPU  
✅ **Well-documented** - Clear guides  

**Start using it:**
```bash
./start-all-services.sh
open http://localhost:3501
```

Happy transcribing! 🎙️
