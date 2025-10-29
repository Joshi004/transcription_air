# 🏗️ Transcription Service - Microservices Architecture

## Overview

This transcription service uses a **microservices architecture** with an **independent Whisper service** for flexibility and scalability.

---

## Architecture Diagram

```
Your MacBook Pro (24GB RAM):

┌────────────────────────────────────────────────────────────────┐
│                                                                  │
│  📝 Whisper Service (Native Python - Port 8501)                 │
│     ├─ Whisper Large v3 model                                   │
│     ├─ Transcription with timestamps                            │
│     └─ Can be stopped/restarted independently                   │
│            ↕ REST API                                            │
│            │                                                     │
│  ┌─────────┴──────────────────────────────────────┐            │
│  │          Docker Containers                     │            │
│  │  ┌──────────────────────────────────────────┐ │            │
│  │  │  🔧 Backend (Port 5501)                  │ │            │
│  │  │     ├─ Flask API (no ML code!)           │ │            │
│  │  │     ├─ Orchestrates Whisper service      │ │            │
│  │  │     ├─ Manages files & transcripts       │ │            │
│  │  │     └─ Job management                    │ │            │
│  │  └──────────────────────────────────────────┘ │            │
│  │            ↕ REST API                          │            │
│  │  ┌──────────────────────────────────────────┐ │            │
│  │  │  🎨 Frontend (Port 3501)                 │ │            │
│  │  │     └─ React + Material UI               │ │            │
│  │  └──────────────────────────────────────────┘ │            │
│  └───────────────────────────────────────────────┘            │
│                                                                  │
│  📂 Shared Directories (accessible by all):                     │
│     ├─ Audio/          (input files - read by all)             │
│     └─ transcripts/    (output files - written by Backend)     │
│                                                                  │
└────────────────────────────────────────────────────────────────┘
```

---

## Service Ports

| Service | Port | Runs In | Purpose |
|---------|------|---------|---------|
| **Whisper** | 8501 | Native Mac | Transcription with timestamps |
| **Backend** | 5501 | Docker | API orchestration, file mgmt |
| **Frontend** | 3501 | Docker | User interface |

---

## Key Benefits

### 1. Independent Service

✅ **Stop Whisper** without affecting Docker containers:
```bash
lsof -ti:8501 | xargs kill
# Backend keeps running (uses minimal RAM)
```

✅ **Restart Whisper** independently:
```bash
cd whisper-service && python3 app.py
```

✅ **Update model** without touching other services

### 2. Flexible Deployment

Run Whisper locally or remotely:

```env
# Local
WHISPER_SERVICE_URL=http://localhost:8501

# Remote GPU server
WHISPER_SERVICE_URL=https://gpu-server.com:8501
```

### 3. Resource Management

- **Whisper**: Memory-intensive (6-8GB when processing)
- **Backend**: Lightweight (~100MB)
- **Frontend**: Lightweight (~150MB)

Kill Whisper when you need RAM for other tasks!

### 4. Development & Testing

Test different model versions independently:

```bash
# Test Whisper Medium (faster, less accurate)
cd whisper-service
# Edit app.py: whisper.load_model("medium")
python3 app.py  # Port 8501

# No other changes needed!
```

---

## Startup Sequence

### Quick Start (All Services)

```bash
# One command starts everything!
./start-all-services.sh

# Services start in this order:
# 1. Whisper Service (2-3 min to load model)
# 2. Docker containers (10 seconds)
```

### Manual Start (More Control)

```bash
# Terminal 1: Whisper
cd whisper-service
./start.sh

# Terminal 2: Docker
docker-compose up

# Keep terminals open to see logs!
```

---

## Communication Flow

### Complete Transcription Process

```
1. User clicks "Transcribe" on mentlist.mp3
   Frontend → Backend: POST /api/transcribe/mentlist.mp3

2. Backend starts Whisper job:
   
   Backend → Whisper: POST http://localhost:8501/transcribe
   Whisper → Backend: {"job_id": "whisper-abc-123"} (30ms response)

3. Backend polls Whisper service (every 5 seconds):
   
   Backend → Whisper: GET /job/whisper-abc-123
   Response: {"status": "processing", "progress": 40}

4. Whisper completes (~15-20 min):
   Backend → Whisper: GET /job/whisper-abc-123
   Response: {"status": "completed", "result": {segments: [...]}}

5. Backend saves transcript:
   ./transcripts/mentlist.json

6. Frontend polls Backend (every 5 seconds):
   Frontend → Backend: GET /api/status/mentlist.mp3
   Response: {"status": "completed"}

7. Frontend fetches transcript:
   Frontend → Backend: GET /api/transcript/mentlist.mp3
   Response: {full transcript with timestamps}

8. User sees synchronized playback!
```

---

## Shared Directory Access

### How Each Service Accesses Files

```
Audio Directory (./Audio/):
├── Whisper Service:  /Users/.../TranscriptionService/Audio/mentlist.mp3 (direct)
├── Backend (Docker):  /audio/mentlist.mp3 (mounted volume)
└── Frontend:         Via Backend API streaming endpoint

Transcripts Directory (./transcripts/):
├── Backend (Docker):  /transcripts/mentlist.json (writes, mounted volume)
└── Frontend:         Via Backend API JSON endpoint

Models Directory (./models/):
└── Whisper Service:  /Users/.../TranscriptionService/models/whisper/
```

**Key Points:**
- Whisper service READS audio files
- Backend WRITES transcripts (with Whisper results)
- All share the same physical files via different paths

---

## Configuration

### Environment Variables (.env)

```env
# Whisper Service URL (change for remote deployment)
WHISPER_SERVICE_URL=http://host.docker.internal:8501

# Docker paths
AUDIO_DIR=/audio
TRANSCRIPT_DIR=/transcripts
```

### Switching Deployments

```bash
# All local (current)
WHISPER_SERVICE_URL=http://host.docker.internal:8501

# Whisper on GPU server
WHISPER_SERVICE_URL=https://gpu-server.com:8501

# No code changes needed - just update .env and restart!
```

---

## Advantages of Microservices Architecture

| Aspect | Monolithic | Microservices |
|--------|------------|---------------|
| **Services** | 1 combined service | Independent services |
| **Ports** | Single port | 8501 (Whisper) + 5501 (Backend) + 3501 (Frontend) |
| **Start/Stop** | All or nothing | Individual control |
| **Memory** | 8-10GB always | 6-8GB (Whisper) + 250MB (Backend+Frontend) |
| **Testing** | Must load everything | Test each separately |
| **Deployment** | Must be together | Can split across servers |
| **Updates** | Restart everything | Update one, keep others running |
| **Debugging** | Mixed logs | Separate logs per service |
| **Resource Management** | Kill all or nothing | Kill heavy service, keep light ones |

---

## Service Management

### Check Service Status

```bash
# Check all services
curl http://localhost:8501/health  # Whisper
curl http://localhost:5501/api/health  # Backend

# One-liner
curl -s localhost:8501/health | jq '.status' && \
curl -s localhost:5501/api/health | jq '.status'
```

### Stop Individual Services

```bash
# Stop only Whisper
lsof -ti:8501 | xargs kill

# Stop Docker (Backend + Frontend)
docker-compose down
```

### Restart Individual Services

```bash
# Restart Whisper
lsof -ti:8501 | xargs kill
cd whisper-service && ./start.sh
```

### View Logs

```bash
# Whisper logs
tail -f logs/whisper-service.log

# Backend logs
docker-compose logs -f backend

# Frontend logs
docker-compose logs -f frontend
```

---

## Development Workflow

### Typical Development Session

```bash
# Morning: Start all services
./start-all-services.sh

# Work on frontend
# Changes auto-reload in Docker

# Work on backend
# Edit backend/app.py → docker-compose restart backend

# Work on Whisper service
# Edit whisper-service/app.py → kill and restart Whisper

# Evening: Stop everything
./stop-all-services.sh
```

### Testing Different Model Versions

```bash
# Test Whisper Medium (faster, less accurate)
cd whisper-service
# Edit app.py: whisper.load_model("medium")
lsof -ti:8501 | xargs kill
python3 app.py

# No other changes needed!
```

---

## Deployment Scenarios

### Scenario 1: All Local (Current)

```
Your Mac:
├── Whisper Service (Native, Port 8501)
└── Docker (Backend + Frontend)

Start: ./start-all-services.sh
Stop: ./stop-all-services.sh
```

### Scenario 2: Whisper on GPU, Backend Local

```
Your Mac:
└── Docker (Backend + Frontend)

GPU Server:
└── Whisper Service (Port 8501) - 10x faster!

.env:
WHISPER_SERVICE_URL=https://gpu-server.com:8501
```

### Scenario 3: Full Remote

```
Your Mac:
└── Browser only

Cloud Servers:
├── Whisper Service (GPU)
├── Backend (Docker)
└── Frontend (Docker)
```

---

## Performance & Resource Usage

### Memory Consumption

| Service | Idle | Processing |
|---------|------|------------|
| Whisper Service | ~4GB | ~6-8GB |
| Backend | ~50MB | ~100MB |
| Frontend | ~100MB | ~150MB |
| **Total (all running)** | ~4.2GB | ~6-8GB |

### Processing Time (30-min audio)

| Setup | Whisper | Total |
|-------|---------|-------|
| **Mac CPU** | 15-20 min | ~15-20 min |
| **GPU Server** | 2-3 min | ~2-3 min |

---

## Troubleshooting

### Whisper Service Won't Start

```bash
# Check logs
tail -f logs/whisper-service.log

# Common issues:
# 1. Model not downloaded
ls -lh models/whisper/large-v3.pt  # Should be ~3GB

# 2. Port already in use
lsof -i :8501  # Check what's using the port

# 3. Python dependencies missing
pip3 install -r whisper-service/requirements.txt
```

### Backend Can't Reach Whisper Service

```bash
# From within backend container
docker exec -it transcription-backend bash
curl http://host.docker.internal:8501/health

# If fails, check:
# 1. Whisper service is running
ps aux | grep "python3 app.py"

# 2. Docker has host access (extra_hosts in docker-compose.yml)
```

---

## Monitoring

### Check All Services

```bash
# Quick health check script
#!/bin/bash
echo "Whisper:  $(curl -s localhost:8501/health | jq -r '.status')"
echo "Backend:  $(curl -s localhost:5501/api/health | jq -r '.status')"
echo "Frontend: $(curl -s localhost:3501 -o /dev/null -w '%{http_code}' 2>/dev/null)"
```

### Monitor Processing

```bash
# Watch job progress in real-time
watch -n 1 'curl -s localhost:5501/api/status/mentlist.mp3 | jq'

# Watch Whisper jobs
watch -n 2 'curl -s localhost:8501/jobs | jq ".total"'
```

---

## Migration Path to Remote

### Phase 1: All Local (Now)

```
Start: ./start-all-services.sh
.env:  WHISPER_SERVICE_URL=http://host.docker.internal:8501
```

### Phase 2: Whisper on GPU

```
Deploy Whisper to GPU server
.env:  WHISPER_SERVICE_URL=https://gpu-server.com:8501

Result: 10x faster transcription!
```

### Phase 3: Full Cloud

```
Deploy all to cloud
Stop local services, access via web

Result: No local resources needed!
```

**No code changes in any phase!**

---

## Summary

This microservices architecture gives you:

✅ **Independent Control** - Start/stop Whisper service separately  
✅ **Flexible Deployment** - Mix local and remote services  
✅ **Better Resource Management** - Kill Whisper when not needed  
✅ **Easy Testing** - Test models independently  
✅ **Scalable** - Add more Whisper instances if needed  
✅ **Portable** - Same code works local and remote  

Perfect for your use case: develop locally, deploy to GPU when ready!
