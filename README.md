# 🎙️ Audio Transcription Service

A full-stack application for transcribing audio files using **Whisper Large v3**.

## Features

- 📝 **Accurate Transcription**: Using OpenAI's Whisper Large v3 model
- ⏱️ **Timestamped Segments**: Word-level timestamps for precise alignment
- 🎵 **Audio Playback**: Play audio files directly in the browser
- 🔄 **Synchronized View**: Transcript highlights in sync with audio playback
- 🎯 **Click-to-Seek**: Click any transcript segment to jump to that point in audio
- 🐳 **Dockerized**: Complete containerization with Docker Compose
- 💾 **Host-Mounted Models**: Models stored on host machine, shared across containers

## Architecture

```
Frontend (React + Material UI) → Backend (Flask API) → Whisper Service
    Port 3501                         Port 5501          Port 8501
```

### Tech Stack

**Backend:**
- Flask (REST API)
- Whisper Large v3 (Transcription)
- Threading (Async processing)

**Frontend:**
- React 18
- Material UI 5
- Axios (API calls)

**Infrastructure:**
- Docker & Docker Compose
- Volume mounts for Audio, Transcripts, and Models

## Prerequisites

1. **Docker** and **Docker Compose** installed
2. **Python 3.10+** (for Whisper service)
3. **~3GB free disk space** for Whisper model

## Setup Instructions

### Step 1: Clone and Navigate

```bash
cd /Users/nareshjoshi/Documents/TetherWorkspace/TranscriptionService
```

### Step 2: Configure Environment Variables (Optional)

If you have a `.env` file, it will be loaded automatically. No specific configuration is required for basic operation.

### Step 3: Install Whisper Service Dependencies

```bash
# Install Python dependencies for Whisper service
pip3 install -r whisper-service/requirements.txt
```

The Whisper model (~3GB) will be downloaded automatically on first run.

### Step 4: Place Audio Files

Put your audio files in the `Audio/` directory:

```bash
# Your audio file is already there
ls Audio/
# mentlist.mp3
```

Supported formats: `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`

### Step 5: Start All Services

```bash
# Start Whisper service, backend, and frontend
./start-all-services.sh
```

**First launch may take 2-3 minutes** as the Whisper model is loaded into memory.

### Step 6: Access the Application

Open your browser and navigate to:
```
http://localhost:3501
```

The backend API is available at:
```
http://localhost:5501
```

## Usage

### 1. View Audio Files

The home page displays all audio files from the `Audio/` directory with their:
- Filename
- Duration
- File size
- Status (Not Processed, Processing, Completed, Error)

### 2. Start Transcription

Click the **"Transcribe"** button on any audio file. 

⏱️ **Processing Time**: For a 30-minute audio file, expect:
- **~15-25 minutes** on CPU (MacBook Pro)
- **~3-5 minutes** on GPU server

The UI will poll for updates every 5 seconds and show progress.

### 3. View Transcript

Once processing is complete:
- Click **"View & Play"** to open the synchronized player
- Audio player at the top
- Transcript segments below with timestamps
- Active segment highlights automatically as audio plays
- Click any segment to jump to that timestamp

### 4. Transcript Format

Transcripts are saved as JSON in `transcripts/` directory:

```json
{
  "filename": "mentlist.mp3",
  "duration": 1800.5,
  "language": "en",
  "status": "completed",
  "segments": [
    {
      "start": 0.0,
      "end": 2.5,
      "text": "Hello, how are you?"
    }
  ]
}
```

## API Endpoints

### Backend REST API

```bash
# Health check
GET /api/health

# List all audio files
GET /api/audio-files

# Stream audio file
GET /api/audio/<filename>

# Get transcript
GET /api/transcript/<filename>

# Trigger transcription
POST /api/transcribe/<filename>

# Check processing status
GET /api/status/<filename>
```

### Example API Calls

```bash
# Check if backend is ready
curl http://localhost:5501/api/health

# List audio files
curl http://localhost:5501/api/audio-files

# Start transcription
curl -X POST http://localhost:5501/api/transcribe/mentlist.mp3

# Check status
curl http://localhost:5501/api/status/mentlist.mp3

# Get transcript
curl http://localhost:5501/api/transcript/mentlist.mp3
```

## Project Structure

```
TranscriptionService/
├── Audio/                    # Your audio files (existing)
│   └── mentlist.mp3
├── backend/                  # Flask API
│   ├── app.py               # Main Flask application
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile
├── frontend/                 # React UI
│   ├── src/
│   │   ├── components/
│   │   │   ├── AudioList.js
│   │   │   └── AudioPlayer.js
│   │   ├── services/
│   │   │   └── api.js
│   │   └── App.js
│   ├── package.json
│   └── Dockerfile
├── models/                   # ML models (host machine)
│   └── whisper/             # Whisper models cache
├── transcripts/              # Generated transcripts
├── whisper-service/          # Whisper transcription service
│   ├── app.py               # Whisper Flask server
│   └── requirements.txt     # Python dependencies
├── docker-compose.yml        # Container orchestration
└── README.md                 # This file
```

## Configuration

### Custom Ports

Default ports are `3501` (frontend) and `5501` (backend). To change:

**docker-compose.yml:**
```yaml
services:
  backend:
    ports:
      - "YOUR_PORT:5501"
  frontend:
    ports:
      - "YOUR_PORT:3501"
```

### Toggle Local/Remote Models

In `.env`, change:
```env
MODEL_MODE=local   # Use models from host machine
# MODEL_MODE=remote  # Use remote API (future feature)
```

## Troubleshooting

### Whisper Service Won't Start

**Problem**: Whisper service crashes on startup or fails to load model.

**Solutions**:
1. Ensure Python dependencies are installed: `pip3 install -r whisper-service/requirements.txt`
2. Check Whisper service logs: `tail -f logs/whisper-service.log`
3. Verify model directory exists: `ls -l models/whisper/`
4. Ensure sufficient disk space (~3GB) and RAM (~6-8GB)

### Cannot Connect to Backend

**Problem**: Frontend shows "Unable to connect to backend."

**Solutions**:
1. Ensure backend is running: `docker ps`
2. Check backend logs: `docker-compose logs backend`
3. Verify port 5501 is not in use: `lsof -i :5501`
4. Restart services: `docker-compose restart`

### Transcription Takes Too Long

**Expected**: 15-25 minutes for 30-minute audio on CPU is normal.

**To speed up**:
- Move to GPU server with NVIDIA GPU (10x faster)
- Use smaller Whisper models (Medium or Small instead of Large v3)
- Edit `whisper-service/app.py` to change model: `whisper.load_model("medium")`

### Audio File Not Showing

**Solutions**:
1. Ensure file is in `Audio/` directory
2. Check supported formats: `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`
3. Refresh the browser
4. Check backend logs for errors

### Docker Build Fails

**Solutions**:
1. Ensure Docker daemon is running
2. Check internet connectivity (needed for package downloads)
3. Clean up Docker: `docker-compose down -v`
4. Rebuild: `docker-compose build --no-cache`

## Performance Notes

### CPU vs GPU Processing

**Your Current Setup (MacBook Pro 24GB RAM, CPU):**
- 30-min audio → 15-25 min processing
- Memory usage: ~6-8GB during processing
- Fan will run loud during processing

**With NVIDIA GPU Server:**
- 30-min audio → 3-5 min processing
- 10x faster transcription

## Future Enhancements

- [ ] File upload via UI
- [ ] Export transcripts (SRT, VTT, TXT formats)
- [ ] Progress bar during processing
- [ ] Batch processing queue
- [ ] Remote API integration
- [ ] Real-time streaming transcription
- [ ] Multiple language models
- [ ] Speaker diarization integration

## License

This project uses:
- **Whisper** (MIT License)

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review Docker logs: `docker-compose logs`
3. Verify all setup steps completed

---

**Built with ❤️ using Whisper Large v3**

