# Quick Reference Guide

## 🚀 Common Commands

### Setup (First Time)

```bash
# 1. Add your HF token to .env
nano .env  # Add: HF_TOKEN=hf_your_token_here

# 2. Run automated setup
./setup.sh

# OR do it manually:
docker-compose build
python3 download_models.py  # Optional but recommended
```

### Start/Stop Services

```bash
# Start (foreground, see logs)
docker-compose up

# Start (background)
docker-compose up -d

# Stop
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Restart specific service
docker-compose restart backend
docker-compose restart frontend
```

### View Logs

```bash
# All logs
docker-compose logs

# Follow logs (live)
docker-compose logs -f

# Backend only
docker-compose logs backend
docker-compose logs -f backend

# Frontend only
docker-compose logs frontend
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100
```

### Check Status

```bash
# Check running containers
docker-compose ps

# Check backend health
curl http://localhost:5501/api/health

# List audio files
curl http://localhost:5501/api/audio-files

# Check transcription status
curl http://localhost:5501/api/status/mentlist.mp3
```

### Rebuild Containers

```bash
# Rebuild after code changes
docker-compose build

# Rebuild without cache
docker-compose build --no-cache

# Rebuild and start
docker-compose up --build
```

### Clean Up

```bash
# Remove stopped containers
docker-compose down

# Remove containers and volumes
docker-compose down -v

# Remove all Docker data (careful!)
docker system prune -a
```

## 📁 File Locations

```bash
# Audio files (input)
./Audio/

# Generated transcripts (output)
./transcripts/

# ML models (host machine)
./models/whisper/
./models/pyannote/

# Backend code
./backend/

# Frontend code
./frontend/src/

# Configuration
./.env
./docker-compose.yml
```

## 🔧 Configuration

### Environment Variables (.env)

```env
# Required
HF_TOKEN=hf_your_token_here

# Optional (defaults shown)
MODEL_MODE=local
WHISPER_MODEL_PATH=/models/whisper
PYANNOTE_MODEL_PATH=/models/pyannote
AUDIO_DIR=/audio
TRANSCRIPT_DIR=/transcripts
```

### Change Ports

Edit `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "YOUR_PORT:5501"  # Change YOUR_PORT
  frontend:
    ports:
      - "YOUR_PORT:3501"  # Change YOUR_PORT
```

Then rebuild: `docker-compose up --build`

## 🌐 URLs

```bash
# Frontend UI
http://localhost:3501

# Backend API
http://localhost:5501

# API Endpoints
http://localhost:5501/api/health
http://localhost:5501/api/audio-files
http://localhost:5501/api/audio/<filename>
http://localhost:5501/api/transcript/<filename>
http://localhost:5501/api/status/<filename>
```

## 🎯 Typical Workflow

```bash
# 1. Start services
docker-compose up -d

# 2. Check backend is ready
curl http://localhost:5501/api/health
# Should show: "models_loaded": true

# 3. Open UI
open http://localhost:3501

# 4. In UI:
#    - Click "Transcribe" on audio file
#    - Wait 20-35 minutes
#    - Click "View & Play" when complete

# 5. Stop services
docker-compose down
```

## 🐛 Troubleshooting

### Models Not Loading

```bash
# Check logs
docker-compose logs backend | grep -i model

# Verify HF_TOKEN
cat .env | grep HF_TOKEN

# Download models manually
python3 download_models.py

# Restart backend
docker-compose restart backend
```

### Port Already in Use

```bash
# Find what's using the port
lsof -i :5501
lsof -i :3501

# Kill the process
kill -9 <PID>

# Or change ports in docker-compose.yml
```

### Backend Not Responding

```bash
# Check if container is running
docker-compose ps

# Check logs for errors
docker-compose logs backend

# Restart backend
docker-compose restart backend

# Full restart
docker-compose down && docker-compose up
```

### Transcription Stuck

```bash
# Check status
curl http://localhost:5501/api/status/your_file.mp3

# Check backend logs
docker-compose logs -f backend

# If truly stuck, restart backend
docker-compose restart backend
```

### Frontend Won't Load

```bash
# Check logs
docker-compose logs frontend

# Verify backend is running
curl http://localhost:5501/api/health

# Clear browser cache
# Or try incognito/private mode

# Rebuild frontend
docker-compose build frontend
docker-compose up frontend
```

## 📊 Performance Tips

### Speed Up Processing

```bash
# Current (CPU): 30-min audio → 20-35 min processing
# With GPU: 30-min audio → 3-5 min processing

# To use GPU in future:
# 1. Get GPU server
# 2. Same docker-compose setup
# 3. Models automatically use GPU if available
```

### Reduce Memory Usage

```bash
# Process shorter files first
# Close other applications
# Use Whisper Medium instead of Large (edit backend code)
```

## 🔄 Update Code

```bash
# After editing backend code
docker-compose restart backend

# After editing frontend code
docker-compose restart frontend

# After major changes
docker-compose down
docker-compose build
docker-compose up
```

## 📦 Backup & Restore

### Backup Transcripts

```bash
# Copy transcripts directory
cp -r transcripts transcripts_backup_$(date +%Y%m%d)

# Or create archive
tar -czf transcripts_backup.tar.gz transcripts/
```

### Backup Configuration

```bash
# Save your .env file
cp .env .env.backup
```

### Restore

```bash
# Copy back transcripts
cp -r transcripts_backup/* transcripts/

# Restore .env
cp .env.backup .env
```

## 🎓 Advanced

### Run Backend Outside Docker (Development)

```bash
cd backend
pip install -r requirements.txt
export HF_TOKEN=your_token
export AUDIO_DIR=../Audio
export TRANSCRIPT_DIR=../transcripts
python app.py
```

### Run Frontend Outside Docker (Development)

```bash
cd frontend
npm install
PORT=3501 npm start
```

### Test API Directly

```bash
# Test transcription
curl -X POST http://localhost:5501/api/transcribe/test.mp3

# Get transcript
curl http://localhost:5501/api/transcript/test.mp3 | jq .

# Download audio
curl http://localhost:5501/api/audio/test.mp3 > downloaded.mp3
```

## 💡 Tips

1. **First run?** Use a short audio file (2-3 min) to test the pipeline
2. **Processing time:** Be patient, 20-35 min for 30-min audio is normal on CPU
3. **Model updates:** Just download new version to models/ directory
4. **Multiple files:** Process one at a time (or implement queue)
5. **Logs:** Always check logs when something goes wrong

---

**Need more help?** Check:
- `README.md` - Full documentation
- `SETUP_GUIDE.md` - Detailed setup
- `IMPLEMENTATION_SUMMARY.md` - Architecture overview

