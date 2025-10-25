# Quick Setup Guide

Follow these steps to get your transcription service running:

## Prerequisites Check

- [ ] Docker installed: `docker --version`
- [ ] Docker Compose installed: `docker-compose --version`
- [ ] Python 3.10+ installed: `python3 --version`
- [ ] Hugging Face account created: [https://huggingface.co/join](https://huggingface.co/join)

## Step-by-Step Setup

### 1. Get Your Hugging Face Token

1. Go to [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Click "New token"
3. Give it a name (e.g., "transcription-service")
4. Select "Read" permissions
5. Copy the token (starts with `hf_`)

### 2. Accept Pyannote Model License

1. Visit [https://huggingface.co/pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
2. Click "Agree and access repository"
3. This is required for Pyannote to work

### 3. Configure Environment

```bash
# Navigate to project directory
cd /Users/nareshjoshi/Documents/TetherWorkspace/TranscriptionService

# Copy environment template
cp .env.example .env

# Edit .env file
nano .env
# or
open .env
```

Update the `HF_TOKEN` line:
```env
HF_TOKEN=hf_your_actual_token_here
```

Save and close the file.

### 4. Download Models (Optional but Recommended)

This step downloads models to your local machine (~4GB). It's optional but recommended for faster container startup.

```bash
# Install Python dependencies
pip3 install openai-whisper pyannote.audio torch torchaudio

# Set environment variable for this session
export HF_TOKEN=hf_your_actual_token_here

# Run download script
python3 download_models.py
```

**Expected output:**
```
ML Model Download Script
[1/2] Downloading Whisper Large v3 model...
✓ Whisper model downloaded successfully!
[2/2] Downloading Pyannote speaker diarization model...
✓ Pyannote model downloaded successfully!
✓ All models downloaded successfully!
```

**Note**: If you skip this step, models will be downloaded when the Docker container first starts (slower but automatic).

### 5. Verify Audio Files

Make sure you have audio files in the `Audio/` directory:

```bash
ls Audio/
# Should show: mentlist.mp3 (or your audio files)
```

Supported formats: `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`

### 6. Build Docker Containers

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

### 7. Start the Services

```bash
# Start all services
docker-compose up
```

**What to expect:**
- Backend will start on port 5501
- Frontend will start on port 3501
- First startup: 2-3 minutes for model loading
- You'll see logs from both services

**Look for these messages:**
```
backend_1   | Models initialized successfully!
backend_1   | Running on http://0.0.0.0:5501
frontend_1  | webpack compiled successfully
frontend_1  | On Your Network:  http://0.0.0.0:3501
```

### 8. Access the Application

Open your browser:
```
http://localhost:3501
```

You should see the Transcription Service UI with your audio files listed!

## Verification Checklist

- [ ] Backend health check: `curl http://localhost:5501/api/health`
  - Should return: `{"status": "healthy", "models_loaded": true}`

- [ ] Frontend accessible: Open `http://localhost:3501`
  - Should show "Transcription Service" title

- [ ] Audio files visible: Check if `mentlist.mp3` appears in the list

- [ ] Can click "Transcribe" button without errors

## Common Issues

### Issue: "HF_TOKEN not set" error

**Solution:**
```bash
# Make sure .env file has your token
cat .env | grep HF_TOKEN
# Should show: HF_TOKEN=hf_xxx...

# If empty, edit it:
nano .env
# Add: HF_TOKEN=hf_your_token_here
# Save and restart: docker-compose restart backend
```

### Issue: "Models not loaded" in health check

**Solution:**
1. Check you accepted the Pyannote license
2. Verify HF_TOKEN is valid
3. Check backend logs: `docker-compose logs backend`
4. Try pre-downloading models with `python3 download_models.py`

### Issue: Port already in use

**Solution:**
```bash
# Check what's using the port
lsof -i :5501
lsof -i :3501

# Kill the process or change ports in docker-compose.yml
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

1. **Test with a short file first** (5 min audio) to verify the pipeline works
2. **Monitor processing**: Processing takes ~20-35 min for 30-min audio on CPU
3. **Check transcripts**: They'll appear in `transcripts/` directory as JSON files
4. **Play & view**: Click "View & Play" to see synchronized playback

## Stopping the Services

```bash
# Stop containers (Ctrl+C if running in foreground)
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Running in Background

```bash
# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

**Need help?** Check the main README.md or the Troubleshooting section!

