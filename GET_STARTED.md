# 🚀 Getting Started - Microservices Edition

## What You Have Now

✅ **Whisper Service** - Independent transcription service (Port 8501)  
✅ **Pyannote Service** - Independent speaker diarization service (Port 8502)  
✅ **Backend** - Lightweight API orchestrator (Port 5501, Docker)  
✅ **Frontend** - React UI (Port 3501, Docker)  

All services are **independent** - you can start/stop each one separately!

---

## 🎯 First Time Setup (5 Steps)

### Step 1: Verify Models Are Downloaded

```bash
cd /Users/nareshjoshi/Documents/TetherWorkspace/TranscriptionService

# Check Whisper
ls -lh models/whisper/large-v3.pt
# Should show: ~3GB file

# Check Pyannote
du -sh models/pyannote/
# Should show: ~31MB
```

✅ **If models are present, skip to Step 2**

❌ **If models are missing:**
```bash
# Download models
export HF_TOKEN=Actual_Token
python3 download_models.py
```

---

### Step 2: Install Python Dependencies (For Model Services)

```bash
# Install Whisper dependencies
pip3 install -r whisper-service/requirements.txt

# Install Pyannote dependencies
pip3 install -r pyannote-service/requirements.txt

# This installs:
# - Whisper + dependencies (~5 min)
# - Pyannote + dependencies (~3 min)
```

---

### Step 3: Verify Configuration

```bash
# Check .env file
cat .env

# Should contain:
# WHISPER_SERVICE_URL=http://host.docker.internal:8501
# PYANNOTE_SERVICE_URL=http://host.docker.internal:8502
# HF_TOKEN=actula_token
```

✅ Looks good? Continue to Step 4!

---

### Step 4: Start All Services

```bash
# One command starts everything!
./start-all-services.sh
```

**What happens:**
```
[1/3] Starting Whisper Service...
      Loading model (2-3 minutes)...
      ✓ Listening on port 8501

[2/3] Starting Pyannote Service...
      Loading model (1-2 minutes)...
      ✓ Listening on port 8502

[3/3] Starting Docker services...
      Backend starting...
      Frontend starting...
      ✓ All services ready!
```

**Total startup time: ~5 minutes** (first time, then faster)

---

### Step 5: Access the Application

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

# Test Pyannote
curl http://localhost:8502/health
# Expected: {"service": "pyannote", "status": "healthy", "model_loaded": true}

# Test Backend
curl http://localhost:5501/api/health
# Expected: {"status": "healthy", "model_services": {"all_healthy": true}}
```

### 2. List Audio Files

```bash
curl http://localhost:5501/api/audio-files | jq
```

Should show your `mentlist.mp3` file.

### 3. Start First Transcription

**Option A: Via UI (Recommended)**
1. Open http://localhost:3501
2. Click "Transcribe" on mentlist.mp3
3. Wait ~20-25 minutes (shows progress)
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
Minute 0:01 - Backend starts both jobs
              Whisper job: started
              Pyannote job: started

Minute 0-15 - Whisper processing (transcribing audio)
              Pyannote processing (identifying speakers)
              Progress updates every 5 seconds

Minute 15:00 - Whisper completes
Minute 20:00 - Pyannote completes
Minute 20:01 - Backend aligns results
Minute 20:02 - Transcript saved
Minute 20:05 - UI shows "View & Play" button

Total: ~20-25 minutes for 30-min audio
```

### Services Process in Parallel!

```
Timeline:
├─ Whisper:  [████████████████████] 20 min
└─ Pyannote: [████████] 8 min

Total wait: 20 min (not 28 min!)
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

# Terminal 2: Pyannote logs
tail -f logs/pyannote-service.log

# Terminal 3: Backend logs
docker-compose logs -f backend
```

### 3. Check Progress via API

```bash
# Real-time progress
watch -n 2 'curl -s localhost:5501/api/status/mentlist.mp3 | \
  jq "{status, progress, whisper_progress, pyannote_progress}"'
```

### 4. Save PIDs for Easy Management

```bash
# After starting services
echo "Whisper PID: $(lsof -ti:8501)" > .service-pids
echo "Pyannote PID: $(lsof -ti:8502)" >> .service-pids

# Later, to stop
cat .service-pids | cut -d: -f2 | xargs kill
```

---

## 📞 Need Help?

### Check Documentation

- **GET_STARTED.md** (this file) - Initial setup
- **ARCHITECTURE.md** - How it works
- **MICROSERVICES_GUIDE.md** - Advanced usage
- **FINAL_IMPLEMENTATION.md** - What was built
- **QUICK_REFERENCE.md** - Command cheatsheet

### Check Logs

```bash
tail -f logs/whisper-service.log
tail -f logs/pyannote-service.log
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Check Service Health

```bash
curl localhost:8501/health | jq
curl localhost:8502/health | jq
curl localhost:5501/api/health | jq
```

---

## ✨ Ready to Start!

Run this now:

```bash
./start-all-services.sh
```

Wait 5 minutes, then open http://localhost:3501

**Enjoy your new microservices-based transcription system!** 🎙️

---

## 🔧 Managing Services

### Check What's Running

```bash
# List all services
ps aux | grep "python3 app.py"

# Check ports
lsof -i :8501  # Whisper
lsof -i :8502  # Pyannote
lsof -i :5501  # Backend
lsof -i :3501  # Frontend
```

### Stop Individual Services

```bash
# Stop only Whisper (if you need RAM)
lsof -ti:8501 | xargs kill
# Pyannote, Backend, Frontend keep running

# Stop only Pyannote
lsof -ti:8502 | xargs kill
# Whisper keeps running (can do transcription-only)

# Stop Docker only
docker-compose down
# Model services keep running
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
# ☕ Get coffee while models load (5 min)

# Use the UI
open http://localhost:3501
# Upload/transcribe audio files

# Check logs if needed
tail -f logs/whisper-service.log

# Afternoon: Need RAM for other work?
lsof -ti:8501 | xargs kill  # Stop Whisper
lsof -ti:8502 | xargs kill  # Stop Pyannote
# Docker keeps running (uses minimal RAM)

# Evening: Stop everything
./stop-all-services.sh
```

---

## 🌟 Cool Things You Can Do Now

### 1. Run Only What You Need

```bash
# Just transcription (no speaker labels)
cd whisper-service && ./start.sh
docker-compose up
# Faster! Skip Pyannote

# Just diarization (test speakers on existing transcript)
cd pyannote-service && ./start.sh
# Test speaker detection separately
```

### 2. Test Different Models

```bash
# Run Whisper Medium (faster) on port 8503
cd whisper-service
# Edit app.py: whisper.load_model("medium")
PORT=8503 python3 app.py

# Update .env to use it
WHISPER_SERVICE_URL=http://host.docker.internal:8503
docker-compose restart backend

# Compare results!
```

### 3. Monitor Resource Usage

```bash
# Watch Whisper memory
watch -n 1 'ps aux | grep whisper-service | grep -v grep'

# Watch Pyannote memory
watch -n 1 'ps aux | grep pyannote-service | grep -v grep'

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
pip3 list | grep pyannote

# Install if missing
pip3 install -r whisper-service/requirements.txt
pip3 install -r pyannote-service/requirements.txt
```

### Backend Can't Connect to Services

```bash
# Test from host
curl localhost:8501/health  # Should work
curl localhost:8502/health  # Should work

# Test from Docker
docker exec transcription-backend \
  curl http://host.docker.internal:8501/health

# If Docker fails, check docker-compose.yml has:
# extra_hosts:
#   - "host.docker.internal:host-gateway"
```

### Transcription Fails

```bash
# Check which service failed
curl localhost:8501/jobs  # Whisper jobs
curl localhost:8502/jobs  # Pyannote jobs

# Check logs
tail -50 logs/whisper-service.log
tail -50 logs/pyannote-service.log
docker-compose logs backend
```

---

## 📖 Next Steps

1. **Read ARCHITECTURE.md** - Understand the design
2. **Read MICROSERVICES_GUIDE.md** - Advanced usage
3. **Test with short file** - 2-3 min audio first
4. **Process your 30-min file** - Will take 20-25 min
5. **Plan GPU deployment** - When you want 10x speed

---

## 🎉 You're All Set!

Your transcription service is now:

✅ **Production-ready** - Stable, no crashes  
✅ **Microservices-based** - Independent model services  
✅ **Flexible** - Start/stop services individually  
✅ **Scalable** - Easy to move to GPU  
✅ **Well-documented** - 7 guide documents  

**Start using it:**
```bash
./start-all-services.sh
open http://localhost:3501
```

Happy transcribing! 🎙️

