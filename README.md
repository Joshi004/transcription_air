# 🎙️ Audio Transcription Service

A full-stack application for transcribing audio files with speaker diarization using **Whisper Large v3** and **Pyannote 3.0**.

## Features

- 📝 **Accurate Transcription**: Using OpenAI's Whisper Large v3 model
- 👥 **Speaker Diarization**: Identifies and labels different speakers using Pyannote 3.0
- ⏱️ **Timestamped Segments**: Word-level timestamps for precise alignment
- 🎵 **Audio Playback**: Play audio files directly in the browser
- 🔄 **Synchronized View**: Transcript highlights in sync with audio playback
- 🎯 **Click-to-Seek**: Click any transcript segment to jump to that point in audio
- 🐳 **Dockerized**: Complete containerization with Docker Compose
- 💾 **Host-Mounted Models**: Models stored on host machine, shared across containers

## Architecture

```
Frontend (React + Material UI) → Backend (Flask API) → ML Models (Whisper + Pyannote)
    Port 3501                         Port 5501              Host Machine
```

### Tech Stack

**Backend:**
- Flask (REST API)
- Whisper Large v3 (Transcription)
- Pyannote 3.0 (Speaker Diarization)
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
2. **Hugging Face Account** - Get your token from [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
3. **Accept Pyannote License** - Visit [https://huggingface.co/pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1) and accept the model license
4. **Python 3.10+** (for model download script)
5. **~4GB free disk space** for models

## Setup Instructions

### Step 1: Clone and Navigate

```bash
cd /Users/nareshjoshi/Documents/TetherWorkspace/TranscriptionService
```

### Step 2: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit the .env file and add your Hugging Face token
nano .env
```

Update the `HF_TOKEN` value:
```env
HF_TOKEN=hf_your_token_here
```

### Step 3: Download ML Models (One-Time Setup)

**Option A: Using the download script (Recommended)**

```bash
# Install Python dependencies (if not already installed)
pip install openai-whisper pyannote.audio torch

# Set your Hugging Face token
export HF_TOKEN=hf_your_token_here

# Run the download script
python download_models.py
```

This will download:
- Whisper Large v3 (~3GB) to `./models/whisper/`
- Pyannote 3.1 (~500MB) to `./models/pyannote/`

**Option B: Let Docker download on first run**

Skip this step, and models will be downloaded automatically when the backend container starts (slower first launch).

### Step 4: Place Audio Files

Put your audio files in the `Audio/` directory:

```bash
# Your audio file is already there
ls Audio/
# mentlist.mp3
```

Supported formats: `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`

### Step 5: Build and Run with Docker Compose

```bash
# Build the containers
docker-compose build

# Start the services
docker-compose up
```

**First launch may take 2-3 minutes** as models are loaded into memory.

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
- Whisper: 15-25 minutes
- Pyannote: 5-10 minutes
- **Total: ~20-35 minutes** on CPU

The UI will poll for updates every 5 seconds and show progress.

### 3. View Transcript

Once processing is complete:
- Click **"View & Play"** to open the synchronized player
- Audio player at the top
- Transcript segments below with speaker labels
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
      "speaker": "SPEAKER_00",
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
│   ├── model_manager.py     # Model loading logic
│   ├── transcription_processor.py  # Transcription pipeline
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
│   ├── whisper/             # Whisper models cache
│   └── pyannote/            # Pyannote models cache
├── transcripts/              # Generated transcripts
├── docker-compose.yml        # Container orchestration
├── download_models.py        # Model download script
├── .env                      # Environment variables
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

### Models Not Loading

**Problem**: Backend shows "Models not loaded" or crashes on startup.

**Solutions**:
1. Ensure `HF_TOKEN` is set correctly in `.env`
2. Accept the Pyannote license at [https://huggingface.co/pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
3. Run `python download_models.py` to pre-download models
4. Check Docker logs: `docker-compose logs backend`

### Cannot Connect to Backend

**Problem**: Frontend shows "Unable to connect to backend."

**Solutions**:
1. Ensure backend is running: `docker ps`
2. Check backend logs: `docker-compose logs backend`
3. Verify port 5501 is not in use: `lsof -i :5501`
4. Restart services: `docker-compose restart`

### Transcription Takes Too Long

**Expected**: 20-35 minutes for 30-minute audio on CPU is normal.

**To speed up** (future):
- Move to GPU server with NVIDIA GPU
- Use smaller models (Whisper Medium instead of Large)
- Set `MODEL_MODE=remote` and use cloud-based inference

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
- 30-min audio → 20-35 min processing
- Memory usage: ~12-15GB peak
- Fan will run loud during processing

**With NVIDIA GPU Server (Future):**
- 30-min audio → 3-5 min processing
- 10x faster transcription
- 5x faster diarization

## Future Enhancements

- [ ] File upload via UI
- [ ] Speaker name editing (rename SPEAKER_00 to "John")
- [ ] Export transcripts (SRT, VTT, TXT formats)
- [ ] Progress bar during processing
- [ ] Batch processing queue
- [ ] Remote API integration
- [ ] Real-time streaming transcription
- [ ] Multiple language models

## License

This project uses:
- **Whisper** (MIT License)
- **Pyannote** (MIT License, requires Hugging Face license acceptance)

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review Docker logs: `docker-compose logs`
3. Verify all setup steps completed

---

**Built with ❤️ using Whisper Large v3 + Pyannote 3.0**

