import os
import json
import logging
import threading
import requests
import time
from pathlib import Path
from datetime import datetime
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from dotenv import load_dotenv

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

# Global state
job_status = {}  # In-memory job status tracking


class WhisperClient:
    """Simple client for Whisper transcription service"""
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.service_name = "Whisper"
    
    def health_check(self):
        """Check if service is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.json()
        except Exception as e:
            logger.error(f"Whisper service health check failed: {str(e)}")
            return {'status': 'unhealthy', 'error': str(e)}
    
    def start_transcription(self, filename):
        """Start transcription job"""
        try:
            response = requests.post(
                f"{self.base_url}/transcribe",
                json={'filename': filename},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to start Whisper job: {str(e)}")
            raise
    
    def get_job_status(self, job_id):
        """Get job status"""
        response = requests.get(
            f"{self.base_url}/job/{job_id}",
            timeout=10
        )
        return response.json()
    
    def wait_for_completion(self, job_id, poll_interval=5, callback=None):
        """Poll until job completes"""
        while True:
            status = self.get_job_status(job_id)
            
            # Call progress callback if provided
            if callback and status.get('progress'):
                callback(status['progress'])
            
            if status['status'] == 'completed':
                logger.info(f"Whisper job {job_id} completed")
                return status['result']
            elif status['status'] == 'error':
                error_msg = status.get('error', 'Unknown error')
                logger.error(f"Whisper job {job_id} failed: {error_msg}")
                raise Exception(f"Whisper service error: {error_msg}")
            
            time.sleep(poll_interval)


# Initialize Whisper client
whisper_client = WhisperClient(WHISPER_SERVICE_URL)


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
    whisper_health = whisper_client.health_check()
    
    return jsonify({
        'status': 'healthy',
        'backend': 'running',
        'whisper_service': whisper_health
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
    """Background task to process transcription with Whisper only"""
    start_time = datetime.now()
    
    try:
        logger.info(f"Starting transcription for {filename}")
        
        # Update status
        job_status[filename] = {
            'status': 'processing',
            'filename': filename,
            'progress': 0
        }
        
        # Progress callback
        def update_progress(progress):
            job_status[filename]['progress'] = progress
        
        # Start Whisper transcription
        logger.info(f"Starting Whisper job for {filename}")
        whisper_job = whisper_client.start_transcription(filename)
        whisper_job_id = whisper_job['job_id']
        
        # Wait for completion
        logger.info(f"Waiting for Whisper job {whisper_job_id}...")
        result = whisper_client.wait_for_completion(
            whisper_job_id,
            callback=update_progress
        )
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Get audio duration
        audio_path = os.path.join(AUDIO_DIR, filename)
        duration = get_audio_duration(audio_path)
        
        # Prepare transcript data (use Whisper output directly)
        transcript_data = {
            'segments': result['segments'],
            'language': result.get('language', 'unknown'),
            'processing_time': processing_time
        }
        
        if duration:
            transcript_data['duration'] = duration
        
        # Save transcript
        save_transcript(filename, transcript_data)
        
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
        
        # Check if Whisper service is available
        health = whisper_client.health_check()
        if health.get('status') != 'healthy':
            return jsonify({
                'error': 'Whisper service not available',
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
    logger.info(f"Whisper service: {WHISPER_SERVICE_URL}")
    
    # Check Whisper service health
    health = whisper_client.health_check()
    if health.get('status') == 'healthy':
        logger.info("✓ Whisper service is healthy!")
    else:
        logger.warning("⚠️  Whisper service is not available")
    
    # Start Flask app
    logger.info("Starting Flask server on port 5501...")
    app.run(host='0.0.0.0', port=5501, debug=False)
