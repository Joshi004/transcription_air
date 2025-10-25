import os
import json
import logging
import threading
from pathlib import Path
from datetime import datetime
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from dotenv import load_dotenv

from model_services_client import TranscriptionOrchestrator

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
WHISPER_SERVICE_URL = os.getenv('WHISPER_SERVICE_URL', 'http://host.docker.internal:8501')
PYANNOTE_SERVICE_URL = os.getenv('PYANNOTE_SERVICE_URL', 'http://host.docker.internal:8502')

# Global state
orchestrator = None
job_status = {}  # In-memory job status tracking


def initialize_orchestrator():
    """Initialize the orchestrator that coordinates model services"""
    global orchestrator
    
    logger.info("Initializing Transcription Orchestrator...")
    logger.info(f"Whisper Service: {WHISPER_SERVICE_URL}")
    logger.info(f"Pyannote Service: {PYANNOTE_SERVICE_URL}")
    
    orchestrator = TranscriptionOrchestrator(
        whisper_url=WHISPER_SERVICE_URL,
        pyannote_url=PYANNOTE_SERVICE_URL
    )
    
    # Check if services are available
    health = orchestrator.check_services_health()
    if health['all_healthy']:
        logger.info("✓ All model services are healthy!")
    else:
        logger.warning("⚠️  Some model services are not available:")
        logger.warning(f"  Whisper: {health['whisper'].get('status')}")
        logger.warning(f"  Pyannote: {health['pyannote'].get('status')}")


def get_audio_duration(audio_path):
    """Get duration of audio file in seconds"""
    try:
        import subprocess
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', audio_path],
            capture_output=True,
            text=True
        )
        return float(result.stdout.strip())
    except Exception as e:
        logger.warning(f"Could not get duration: {str(e)}")
        return None


def get_transcript_path(filename):
    """Get path to transcript file for given audio filename"""
    base_name = Path(filename).stem
    return os.path.join(TRANSCRIPT_DIR, f"{base_name}.json")


def load_transcript(filename):
    """Load transcript for given audio filename"""
    transcript_path = get_transcript_path(filename)
    if os.path.exists(transcript_path):
        with open(transcript_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def save_transcript(filename, transcript_data):
    """Save transcript to JSON file"""
    base_name = Path(filename).stem
    transcript_path = os.path.join(TRANSCRIPT_DIR, f"{base_name}.json")
    
    # Ensure directory exists
    os.makedirs(TRANSCRIPT_DIR, exist_ok=True)
    
    # Add metadata
    full_transcript = {
        'filename': filename,
        'created_at': datetime.now().isoformat(),
        'status': 'completed',
        **transcript_data
    }
    
    # Save as JSON
    with open(transcript_path, 'w', encoding='utf-8') as f:
        json.dump(full_transcript, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Transcript saved to {transcript_path}")


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    services_health = orchestrator.check_services_health() if orchestrator else {}
    
    return jsonify({
        'status': 'healthy',
        'backend': 'running',
        'model_services': services_health
    })


@app.route('/api/audio-files', methods=['GET'])
def list_audio_files():
    """List all audio files with their status"""
    try:
        audio_files = []
        
        if not os.path.exists(AUDIO_DIR):
            return jsonify({'error': 'Audio directory not found'}), 404
        
        for filename in os.listdir(AUDIO_DIR):
            if filename.endswith(('.mp3', '.wav', '.m4a', '.flac', '.ogg')):
                audio_path = os.path.join(AUDIO_DIR, filename)
                
                # Get file info
                file_size = os.path.getsize(audio_path)
                duration = get_audio_duration(audio_path)
                
                # Check transcript status
                transcript = load_transcript(filename)
                if transcript:
                    status = 'completed'
                elif filename in job_status:
                    status = job_status[filename].get('status', 'unknown')
                else:
                    status = 'not_processed'
                
                audio_files.append({
                    'filename': filename,
                    'size': file_size,
                    'duration': duration,
                    'status': status,
                    'has_transcript': transcript is not None
                })
        
        # Sort by filename
        audio_files.sort(key=lambda x: x['filename'])
        
        return jsonify({'audio_files': audio_files})
    
    except Exception as e:
        logger.error(f"Error listing audio files: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/audio/<filename>', methods=['GET'])
def stream_audio(filename):
    """Stream audio file"""
    try:
        audio_path = os.path.join(AUDIO_DIR, filename)
        
        if not os.path.exists(audio_path):
            return jsonify({'error': 'Audio file not found'}), 404
        
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
        return jsonify({'error': str(e)}), 500


@app.route('/api/transcript/<filename>', methods=['GET'])
def get_transcript(filename):
    """Get transcript for audio file"""
    try:
        transcript = load_transcript(filename)
        
        if transcript:
            return jsonify(transcript)
        else:
            return jsonify({'error': 'Transcript not found'}), 404
    
    except Exception as e:
        logger.error(f"Error getting transcript: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/status/<filename>', methods=['GET'])
def get_status(filename):
    """Get processing status for audio file"""
    try:
        # Check if there's an active job
        if filename in job_status:
            return jsonify(job_status[filename])
        
        # Check if transcript exists
        transcript = load_transcript(filename)
        if transcript:
            return jsonify({
                'status': 'completed',
                'filename': filename
            })
        
        return jsonify({
            'status': 'not_processed',
            'filename': filename
        })
    
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return jsonify({'error': str(e)}), 500


def process_transcription_background(filename):
    """Background task to orchestrate transcription"""
    start_time = datetime.now()
    
    try:
        logger.info(f"Starting orchestrated processing for {filename}")
        
        # Update status
        job_status[filename] = {
            'status': 'processing',
            'filename': filename,
            'progress': 0,
            'whisper_progress': 0,
            'pyannote_progress': 0
        }
        
        # Progress callback to track both services
        def update_progress(service, progress):
            if service == 'whisper':
                job_status[filename]['whisper_progress'] = progress
            elif service == 'pyannote':
                job_status[filename]['pyannote_progress'] = progress
            
            # Overall progress: 70% Whisper, 30% Pyannote
            overall = (job_status[filename]['whisper_progress'] * 0.7 + 
                      job_status[filename]['pyannote_progress'] * 0.3)
            job_status[filename]['progress'] = int(overall)
        
        # Process with orchestrator
        result = orchestrator.process_audio(filename, progress_callback=update_progress)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Add metadata
        result['processing_time'] = processing_time
        result['filename'] = filename
        
        # Get audio duration
        audio_path = os.path.join(AUDIO_DIR, filename)
        duration = get_audio_duration(audio_path)
        if duration:
            result['duration'] = duration
        
        # Save transcript
        save_transcript(filename, result)
        
        # Update status
        job_status[filename] = {
            'status': 'completed',
            'filename': filename,
            'progress': 100,
            'processing_time': processing_time
        }
        
        logger.info(f"Processing completed for {filename} in {processing_time:.1f} seconds")
        
    except Exception as e:
        logger.error(f"Error processing {filename}: {str(e)}")
        job_status[filename] = {
            'status': 'error',
            'filename': filename,
            'error': str(e)
        }


@app.route('/api/transcribe/<filename>', methods=['POST'])
def transcribe_audio(filename):
    """Trigger transcription for audio file"""
    try:
        audio_path = os.path.join(AUDIO_DIR, filename)
        
        if not os.path.exists(audio_path):
            return jsonify({'error': 'Audio file not found'}), 404
        
        # Check if already processing
        if filename in job_status and job_status[filename]['status'] == 'processing':
            return jsonify({'error': 'Already processing this file'}), 409
        
        # Check if model services are available
        health = orchestrator.check_services_health()
        if not health['all_healthy']:
            return jsonify({
                'error': 'Model services not available',
                'details': health
            }), 503
        
        # Start background thread
        thread = threading.Thread(
            target=process_transcription_background,
            args=(filename,),
            daemon=True
        )
        thread.start()
        
        return jsonify({
            'status': 'started',
            'filename': filename,
            'message': 'Transcription started in background'
        })
    
    except Exception as e:
        logger.error(f"Error starting transcription: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Starting Transcription Service Backend")
    logger.info("=" * 60)
    logger.info(f"Audio directory: {AUDIO_DIR}")
    logger.info(f"Transcript directory: {TRANSCRIPT_DIR}")
    
    # Initialize orchestrator
    initialize_orchestrator()
    
    # Start Flask app
    logger.info("Starting Flask server on port 5501...")
    app.run(host='0.0.0.0', port=5501, debug=False)

