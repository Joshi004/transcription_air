import os
import json
import logging
import threading
from pathlib import Path
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from mutagen import File as MutagenFile

from model_manager import ModelManager
from transcription_processor import TranscriptionProcessor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=['http://localhost:3501'])

# Configuration
AUDIO_DIR = os.getenv('AUDIO_DIR', '/audio')
TRANSCRIPT_DIR = os.getenv('TRANSCRIPT_DIR', '/transcripts')

# Global state
model_manager = None
transcription_processor = None
job_status = {}  # In-memory job status tracking
processing_lock = threading.Lock()


def initialize_models():
    """Initialize ML models on startup."""
    global model_manager, transcription_processor
    
    logger.info("Initializing models...")
    try:
        model_manager = ModelManager()
        model_manager.load_models()
        transcription_processor = TranscriptionProcessor(model_manager)
        logger.info("Models initialized successfully!")
    except Exception as e:
        logger.error(f"Failed to initialize models: {str(e)}")
        raise


def get_audio_duration(audio_path):
    """Get duration of audio file in seconds."""
    try:
        audio = MutagenFile(audio_path)
        if audio is not None and audio.info is not None:
            return audio.info.length
        return None
    except Exception as e:
        logger.warning(f"Could not get duration for {audio_path}: {str(e)}")
        return None


def get_transcript_path(filename):
    """Get path to transcript file for given audio filename."""
    base_name = Path(filename).stem
    return os.path.join(TRANSCRIPT_DIR, f"{base_name}.json")


def load_transcript(filename):
    """Load transcript for given audio filename."""
    transcript_path = get_transcript_path(filename)
    if os.path.exists(transcript_path):
        with open(transcript_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "models_loaded": model_manager.is_ready() if model_manager else False,
        "model_mode": os.getenv('MODEL_MODE', 'local')
    })


@app.route('/api/audio-files', methods=['GET'])
def list_audio_files():
    """List all audio files with their status."""
    try:
        audio_files = []
        
        # Get all audio files
        if not os.path.exists(AUDIO_DIR):
            return jsonify({"error": "Audio directory not found"}), 404
        
        for filename in os.listdir(AUDIO_DIR):
            if filename.endswith(('.mp3', '.wav', '.m4a', '.flac', '.ogg')):
                audio_path = os.path.join(AUDIO_DIR, filename)
                
                # Get file info
                file_size = os.path.getsize(audio_path)
                duration = get_audio_duration(audio_path)
                
                # Check transcript status
                transcript = load_transcript(filename)
                if transcript:
                    status = transcript.get('status', 'completed')
                elif filename in job_status:
                    status = job_status[filename].get('status', 'unknown')
                else:
                    status = 'not_processed'
                
                audio_files.append({
                    "filename": filename,
                    "size": file_size,
                    "duration": duration,
                    "status": status,
                    "has_transcript": transcript is not None
                })
        
        # Sort by filename
        audio_files.sort(key=lambda x: x['filename'])
        
        return jsonify({"audio_files": audio_files})
    
    except Exception as e:
        logger.error(f"Error listing audio files: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/audio/<filename>', methods=['GET'])
def stream_audio(filename):
    """Stream audio file."""
    try:
        audio_path = os.path.join(AUDIO_DIR, filename)
        
        if not os.path.exists(audio_path):
            return jsonify({"error": "Audio file not found"}), 404
        
        # Determine MIME type
        ext = Path(filename).suffix.lower()
        mime_types = {
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.m4a': 'audio/mp4',
            '.flac': 'audio/flac',
            '.ogg': 'audio/ogg'
        }
        mime_type = mime_types.get(ext, 'audio/mpeg')
        
        return send_file(audio_path, mimetype=mime_type)
    
    except Exception as e:
        logger.error(f"Error streaming audio: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/transcript/<filename>', methods=['GET'])
def get_transcript(filename):
    """Get transcript for audio file."""
    try:
        transcript = load_transcript(filename)
        
        if transcript:
            return jsonify(transcript)
        else:
            return jsonify({"error": "Transcript not found"}), 404
    
    except Exception as e:
        logger.error(f"Error getting transcript: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/status/<filename>', methods=['GET'])
def get_status(filename):
    """Get processing status for audio file."""
    try:
        # Check if there's an active job
        if filename in job_status:
            return jsonify(job_status[filename])
        
        # Check if transcript exists
        transcript = load_transcript(filename)
        if transcript:
            return jsonify({
                "status": "completed",
                "filename": filename
            })
        
        return jsonify({
            "status": "not_processed",
            "filename": filename
        })
    
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return jsonify({"error": str(e)}), 500


def process_transcription_background(filename):
    """Background task to process transcription."""
    try:
        logger.info(f"Starting background processing for {filename}")
        
        # Update status
        job_status[filename] = {
            "status": "processing",
            "filename": filename,
            "progress": 0
        }
        
        # Process the audio
        result = transcription_processor.process_audio(filename)
        
        # Update status to completed
        job_status[filename] = {
            "status": "completed",
            "filename": filename,
            "result": result
        }
        
        logger.info(f"Background processing completed for {filename}")
    
    except Exception as e:
        logger.error(f"Error in background processing: {str(e)}")
        job_status[filename] = {
            "status": "error",
            "filename": filename,
            "error": str(e)
        }


@app.route('/api/transcribe/<filename>', methods=['POST'])
def transcribe_audio(filename):
    """Trigger transcription for audio file."""
    try:
        audio_path = os.path.join(AUDIO_DIR, filename)
        
        if not os.path.exists(audio_path):
            return jsonify({"error": "Audio file not found"}), 404
        
        # Check if already processing
        if filename in job_status and job_status[filename]['status'] == 'processing':
            return jsonify({"error": "Already processing this file"}), 409
        
        # Check if models are loaded
        if not model_manager or not model_manager.is_ready():
            return jsonify({"error": "Models not loaded yet"}), 503
        
        # Start background thread
        thread = threading.Thread(
            target=process_transcription_background,
            args=(filename,),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            "status": "started",
            "filename": filename,
            "message": "Transcription started in background"
        })
    
    except Exception as e:
        logger.error(f"Error starting transcription: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Initialize models before starting server
    logger.info("Starting Transcription Service Backend...")
    initialize_models()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5501, debug=False)

