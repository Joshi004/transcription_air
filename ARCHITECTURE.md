# 🏗️ Transcription Service - Microservices Architecture

## Overview

This transcription service uses a **microservices architecture** with **independent model services** for maximum flexibility and scalability.

---

## Architecture Diagram

```
Your MacBook Pro (24GB RAM):

┌────────────────────────────────────────────────────────────────┐
│                                                                  │
│  📝 Whisper Service (Native Python - Port 8501)                 │
│     ├─ Whisper Large v3 model                                   │
│     ├─ Transcription only                                       │
│     └─ Can be stopped/restarted independently                   │
│            ↕ REST API                                            │
│                                                                  │
│  👥 Pyannote Service (Native Python - Port 8502)                │
│     ├─ Pyannote 3.1 model                                       │
│     ├─ Speaker diarization only                                 │
│     └─ Can be stopped/restarted independently                   │
│            ↕ REST API                                            │
│            │                                                     │
│  ┌─────────┴──────────────────────────────────────┐            │
│  │          Docker Containers                     │            │
│  │  ┌──────────────────────────────────────────┐ │            │
│  │  │  🔧 Backend (Port 5501)                  │ │            │
│  │  │     ├─ Flask API (no ML code!)           │ │            │
│  │  │     ├─ Orchestrates both model services  │ │            │
│  │  │     ├─ Aligns results                    │ │            │
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
| **Whisper** | 8501 | Native Mac | Transcription only |
| **Pyannote** | 8502 | Native Mac | Speaker diarization only |
| **Backend** | 5501 | Docker | API orchestration, file mgmt |
| **Frontend** | 3501 | Docker | User interface |

---

## Key Benefits

### 1. Independent Services

✅ **Stop Whisper** without affecting Pyannote:
```bash
lsof -ti:8501 | xargs kill
# Pyannote keeps running on port 8502
```

✅ **Restart Pyannote** without affecting Whisper:
```bash
cd pyannote-service && python3 app.py
# Whisper keeps running on port 8501
```

✅ **Update one model** without touching the other

### 2. Flexible Deployment

Run different models in different locations:

```env
# Both local
WHISPER_SERVICE_URL=http://localhost:8501
PYANNOTE_SERVICE_URL=http://localhost:8502

# Whisper local, Pyannote remote
WHISPER_SERVICE_URL=http://localhost:8501
PYANNOTE_SERVICE_URL=https://gpu-server.com:8502

# Both remote
WHISPER_SERVICE_URL=https://gpu1.example.com:8501
PYANNOTE_SERVICE_URL=https://gpu2.example.com:8502
```

### 3. Resource Management

- **Whisper**: Memory-intensive (6-8GB when processing)
- **Pyannote**: Lighter (2-3GB when processing)

Kill Pyannote when you need RAM for other tasks, keep Whisper running!

### 4. Development & Testing

Test different model versions independently:

```bash
# Terminal 1: Whisper Large v3
cd whisper-service && python3 app.py

# Terminal 2: Whisper Medium (lighter)
cd whisper-service-medium && python3 app.py  # Port 8503

# Terminal 3: Test both
curl http://localhost:8501/health  # Large
curl http://localhost:8503/health  # Medium
```

---

## Startup Sequence

### Quick Start (All Services)

```bash
# One command starts everything!
./start-all-services.sh

# Services start in this order:
# 1. Whisper Service (2-3 min to load model)
# 2. Pyannote Service (1-2 min to load model)
# 3. Docker containers (10 seconds)
```

### Manual Start (More Control)

```bash
# Terminal 1: Whisper
cd whisper-service
./start.sh

# Terminal 2: Pyannote
cd pyannote-service
./start.sh

# Terminal 3: Docker
docker-compose up

# Keep terminals open to see logs!
```

### Selective Start (Only What You Need)

```bash
# Example: Test Whisper only
cd whisper-service && python3 app.py
# Backend will fail to reach Pyannote, but Whisper works

# Example: Skip Pyannote (for transcription-only testing)
cd whisper-service && python3 app.py
docker-compose up
# Update backend to skip diarization when Pyannote unavailable
```

---

## Communication Flow

### Complete Transcription Process

```
1. User clicks "Transcribe" on mentlist.mp3
   Frontend → Backend: POST /api/transcribe/mentlist.mp3

2. Backend orchestrates both services:
   
   2a. Start Whisper job
       Backend → Whisper: POST http://localhost:8501/transcribe
       Whisper → Backend: {"job_id": "whisper-abc-123"} (30ms response)
   
   2b. Start Pyannote job (parallel!)
       Backend → Pyannote: POST http://localhost:8502/diarize
       Pyannote → Backend: {"job_id": "pyannote-xyz-789"} (30ms response)

3. Backend polls both services (every 5 seconds):
   
   Backend → Whisper: GET /job/whisper-abc-123
   Response: {"status": "processing", "progress": 40}
   
   Backend → Pyannote: GET /job/pyannote-xyz-789
   Response: {"status": "processing", "progress": 60}
   
   Overall progress: (40% * 0.7) + (60% * 0.3) = 46%

4. Whisper completes first (~15-20 min):
   Backend → Whisper: GET /job/whisper-abc-123
   Response: {"status": "completed", "result": {segments: [...]}}

5. Pyannote completes (~5-10 min):
   Backend → Pyannote: GET /job/pyannote-xyz-789
   Response: {"status": "completed", "result": {speakers: [...]}}

6. Backend aligns results:
   - Matches Whisper segments with Pyannote speakers
   - Creates final transcript with speaker labels

7. Backend saves transcript:
   ./transcripts/mentlist.json

8. Frontend polls Backend (every 5 seconds):
   Frontend → Backend: GET /api/status/mentlist.mp3
   Response: {"status": "completed"}

9. Frontend fetches transcript:
   Frontend → Backend: GET /api/transcript/mentlist.mp3
   Response: {full transcript with speakers}

10. User sees synchronized playback!
```

---

## Shared Directory Access

### How Each Service Accesses Files

```
Audio Directory (./Audio/):
├── Whisper Service:  /Users/.../TranscriptionService/Audio/mentlist.mp3 (direct)
├── Pyannote Service: /Users/.../TranscriptionService/Audio/mentlist.mp3 (direct)
├── Backend (Docker):  /audio/mentlist.mp3 (mounted volume)
└── Frontend:         Via Backend API streaming endpoint

Transcripts Directory (./transcripts/):
├── Backend (Docker):  /transcripts/mentlist.json (writes, mounted volume)
├── Frontend:         Via Backend API JSON endpoint
└── Model Services:   Don't write transcripts (Backend does alignment + save)

Models Directory (./models/):
├── Whisper Service:  /Users/.../TranscriptionService/models/whisper/
└── Pyannote Service: /Users/.../TranscriptionService/models/pyannote/
```

**Key Points:**
- Model services READ audio files
- Backend WRITES transcripts (after aligning results from both services)
- All share the same physical files via different paths

---

## Configuration

### Environment Variables (.env)

```env
# Model Service URLs (change these for remote deployment)
WHISPER_SERVICE_URL=http://host.docker.internal:8501
PYANNOTE_SERVICE_URL=http://host.docker.internal:8502

# Hugging Face Token (required for Pyannote)
HF_TOKEN=hf_your_token_here

# Docker paths
AUDIO_DIR=/audio
TRANSCRIPT_DIR=/transcripts
```

### Switching Deployments

```bash
# All local (current)
WHISPER_SERVICE_URL=http://host.docker.internal:8501
PYANNOTE_SERVICE_URL=http://host.docker.internal:8502

# Whisper on GPU, Pyannote local
WHISPER_SERVICE_URL=https://gpu-server.com:8501
PYANNOTE_SERVICE_URL=http://host.docker.internal:8502

# Both on GPU (different servers!)
WHISPER_SERVICE_URL=https://gpu1.example.com:8501
PYANNOTE_SERVICE_URL=https://gpu2.example.com:8502

# Load balanced Whisper, single Pyannote
WHISPER_SERVICE_URL=https://whisper-lb.example.com  # Load balancer
PYANNOTE_SERVICE_URL=https://gpu-server.com:8502
```

**No code changes needed - just update .env and restart!**

---

## Advantages vs Monolithic

| Aspect | Old (Monolithic) | New (Microservices) |
|--------|------------------|---------------------|
| **Services** | 1 combined service | 2 independent services |
| **Ports** | 8501 | 8501 (Whisper) + 8502 (Pyannote) |
| **Start/Stop** | All or nothing | Individual control |
| **Memory** | 10-12GB always | 6-8GB (Whisper) + 2-3GB (Pyannote) |
| **Testing** | Must load both | Test each separately |
| **Deployment** | Must be together | Can split across servers |
| **Updates** | Restart both models | Update one, keep other running |
| **Debugging** | Mixed logs | Separate logs per service |
| **Resource Management** | Kill all or nothing | Kill heavy service, keep light one |

---

## Service Management

### Check Service Status

```bash
# Check all services
curl http://localhost:8501/health  # Whisper
curl http://localhost:8502/health  # Pyannote
curl http://localhost:5501/api/health  # Backend

# One-liner
curl -s localhost:8501/health | jq '.status' && \
curl -s localhost:8502/health | jq '.status' && \
curl -s localhost:5501/api/health | jq '.status'
```

### Stop Individual Services

```bash
# Stop only Whisper
lsof -ti:8501 | xargs kill

# Stop only Pyannote
lsof -ti:8502 | xargs kill

# Stop Docker (Backend + Frontend)
docker-compose down
```

### Restart Individual Services

```bash
# Restart Whisper
lsof -ti:8501 | xargs kill
cd whisper-service && ./start.sh

# Restart Pyannote
lsof -ti:8502 | xargs kill
cd pyannote-service && ./start.sh
```

### View Logs

```bash
# Whisper logs
tail -f logs/whisper-service.log

# Pyannote logs
tail -f logs/pyannote-service.log

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

# Work on model logic
# Edit whisper-service/app.py → kill and restart just Whisper

# Evening: Stop everything
./stop-all-services.sh
```

### Testing New Model Versions

```bash
# Test Whisper Medium (faster, less accurate)
# Create whisper-service-medium/ on port 8503
# Update .env: WHISPER_SERVICE_URL=http://localhost:8503
# No other changes needed!
```

---

## Deployment Scenarios

### Scenario 1: All Local (Current)

```
Your Mac:
├── Whisper Service (Native, Port 8501)
├── Pyannote Service (Native, Port 8502)
└── Docker (Backend + Frontend)

Start: ./start-all-services.sh
Stop: ./stop-all-services.sh
```

### Scenario 2: Whisper on GPU, Pyannote Local

```
Your Mac:
├── Pyannote Service (Native, Port 8502) - CPU is fine
└── Docker (Backend + Frontend)

GPU Server:
└── Whisper Service (Port 8501) - 10x faster!

.env:
WHISPER_SERVICE_URL=https://gpu-server.com:8501
PYANNOTE_SERVICE_URL=http://host.docker.internal:8502
```

### Scenario 3: Both Remote

```
Your Mac:
└── Docker (Backend + Frontend only)

GPU Server 1:
└── Whisper Service (Port 8501)

GPU Server 2:
└── Pyannote Service (Port 8502)

.env:
WHISPER_SERVICE_URL=https://gpu1.example.com:8501
PYANNOTE_SERVICE_URL=https://gpu2.example.com:8502
```

---

## Performance & Resource Usage

### Memory Consumption

| Service | Idle | Processing |
|---------|------|------------|
| Whisper Service | ~4GB | ~6-8GB |
| Pyannote Service | ~2GB | ~2-3GB |
| Backend | ~50MB | ~100MB |
| Frontend | ~100MB | ~150MB |
| **Total (all running)** | ~6.2GB | ~8-11GB |

### Processing Time (30-min audio)

| Setup | Whisper | Pyannote | Total |
|-------|---------|----------|-------|
| **Both on Mac CPU** | 15-20 min | 5-8 min | ~20-25 min |
| **Whisper on GPU, Pyannote CPU** | 2-3 min | 5-8 min | ~7-10 min |
| **Both on GPU** | 2-3 min | 1-2 min | ~3-5 min |

**Note:** Services run in parallel, so total ≈ max(Whisper, Pyannote), not sum!

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

### Pyannote Service Won't Start

```bash
# Check logs
tail -f logs/pyannote-service.log

# Common issues:
# 1. HF_TOKEN not set
echo $HF_TOKEN  # Should show your token

# 2. License not accepted
# Visit: https://huggingface.co/pyannote/speaker-diarization-3.1

# 3. Models incomplete
du -sh models/pyannote/  # Should be ~500MB
```

### Backend Can't Reach Services

```bash
# From within backend container
docker exec -it transcription-backend bash
curl http://host.docker.internal:8501/health
curl http://host.docker.internal:8502/health

# If fails, check:
# 1. Services are running
ps aux | grep "python3 app.py"

# 2. Firewall not blocking
# 3. Docker has host access (extra_hosts in docker-compose.yml)
```

---

## Monitoring

### Check All Services

```bash
# Quick health check script
#!/bin/bash
echo "Whisper:  $(curl -s localhost:8501/health | jq -r '.status')"
echo "Pyannote: $(curl -s localhost:8502/health | jq -r '.status')"
echo "Backend:  $(curl -s localhost:5501/api/health | jq -r '.status')"
echo "Frontend: $(curl -s localhost:3501 -o /dev/null -w '%{http_code}' 2>/dev/null)"
```

### Monitor Processing

```bash
# Watch job progress in real-time
watch -n 1 'curl -s localhost:5501/api/status/mentlist.mp3 | jq'

# Watch both model services
watch -n 2 'echo "=== Whisper Jobs ===" && \
            curl -s localhost:8501/jobs | jq ".total" && \
            echo "=== Pyannote Jobs ===" && \
            curl -s localhost:8502/jobs | jq ".total"'
```

---

## Migration Path to Remote

### Phase 1: All Local (Now)

```
Start: ./start-all-services.sh
.env:  WHISPER_SERVICE_URL=http://host.docker.internal:8501
       PYANNOTE_SERVICE_URL=http://host.docker.internal:8502
```

### Phase 2: Test Remote Whisper

```
Deploy Whisper to GPU server
.env:  WHISPER_SERVICE_URL=https://gpu-server.com:8501
       PYANNOTE_SERVICE_URL=http://host.docker.internal:8502

Result: 3x faster transcription!
```

### Phase 3: Full Remote

```
Deploy both to cloud
.env:  WHISPER_SERVICE_URL=https://whisper.example.com
       PYANNOTE_SERVICE_URL=https://pyannote.example.com

Stop local services, keep only Docker
```

**No code changes in any phase!**

---

## Summary

This microservices architecture gives you:

✅ **Independent Control** - Start/stop each model service separately  
✅ **Flexible Deployment** - Mix local and remote services  
✅ **Better Resource Management** - Kill services when not needed  
✅ **Easy Testing** - Test models independently  
✅ **Scalable** - Add more instances of any service  
✅ **Portable** - Same code works local and remote  

Perfect for your use case: develop locally, deploy to GPU when ready!

