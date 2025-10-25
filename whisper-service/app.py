#!/usr/bin/env python3
"""
Whisper Service - Independent transcription service
Runs natively on host machine (not in Docker)
Port: 8501
"""

import os
import uuid
import json
import logging
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
import whisper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
AUDIO_DIR = os.getenv('AUDIO_DIR', os.path.abspath('../Audio'))
MODELS_DIR = os.getenv('MODELS_DIR', os.path.abspath('../models/whisper'))

# Global state
whisper_model = None
jobs = {}  # In-memory job tracking


def load_model():
    """Load Whisper model on startup"""
    global whisper_model
    
    logger.info("Loading Whisper Large v3 model...")
    logger.info(f"Model directory: {MODELS_DIR}")
    
    try:
        # Set cache directory
        os.environ['XDG_CACHE_HOME'] = os.path.dirname(MODELS_DIR)
        
        whisper_model = whisper.load_model(
            "large-v3",
            download_root=MODELS_DIR
        )
        logger.info("✓ Whisper model loaded successfully!")
        return True
    except Exception as e:
        logger.error(f"Failed to load Whisper model: {str(e)}")
        raise


def transcribe_audio_background(job_id, audio_path):
    """Background task for transcription"""
    try:
        logger.info(f"Starting transcription for job {job_id}")
        
        jobs[job_id]['status'] = 'processing'
        jobs[job_id]['progress'] = 0
        jobs[job_id]['started_at'] = datetime.now().isoformat()
        
        # Transcribe with Whisper
        logger.info(f"Running Whisper on {audio_path}")
        result = whisper_model.transcribe(
            audio_path,
            language=None,  # Auto-detect
            task="transcribe",
            verbose=False
        )
        
        jobs[job_id]['progress'] = 100
        jobs[job_id]['status'] = 'completed'
        jobs[job_id]['completed_at'] = datetime.now().isoformat()
        jobs[job_id]['result'] = {
            'text': result['text'],
            'segments': result['segments'],
            'language': result['language']
        }
        
        logger.info(f"Job {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Error in job {job_id}: {str(e)}")
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['error'] = str(e)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'service': 'whisper',
        'status': 'healthy',
        'model_loaded': whisper_model is not None,
        'model_version': 'large-v3',
        'port': 8501
    })


@app.route('/transcribe', methods=['POST'])
def transcribe():
    """Start transcription job"""
    try:
        data = request.json
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': 'filename is required'}), 400
        
        # Build audio path
        audio_path = os.path.join(AUDIO_DIR, filename)
        
        if not os.path.exists(audio_path):
            return jsonify({'error': f'Audio file not found: {filename}'}), 404
        
        # Create job
        job_id = str(uuid.uuid4())
        jobs[job_id] = {
            'job_id': job_id,
            'filename': filename,
            'audio_path': audio_path,
            'status': 'queued',
            'progress': 0,
            'created_at': datetime.now().isoformat()
        }
        
        # Start background thread
        thread = threading.Thread(
            target=transcribe_audio_background,
            args=(job_id, audio_path),
            daemon=True
        )
        thread.start()
        
        logger.info(f"Started transcription job {job_id} for {filename}")
        
        return jsonify({
            'job_id': job_id,
            'status': 'queued',
            'message': 'Transcription started'
        }), 202
        
    except Exception as e:
        logger.error(f"Error starting transcription: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/job/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get job status"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    
    # Return job info (without full result if not completed)
    response = {
        'job_id': job_id,
        'filename': job.get('filename'),
        'status': job['status'],
        'progress': job.get('progress', 0),
        'created_at': job.get('created_at')
    }
    
    if job['status'] == 'completed':
        response['result'] = job['result']
        response['completed_at'] = job.get('completed_at')
    elif job['status'] == 'error':
        response['error'] = job.get('error')
    
    return jsonify(response)


@app.route('/jobs', methods=['GET'])
def list_jobs():
    """List all jobs"""
    return jsonify({
        'jobs': list(jobs.values()),
        'total': len(jobs)
    })


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("Starting Whisper Service")
    logger.info("=" * 60)
    logger.info(f"Audio directory: {AUDIO_DIR}")
    logger.info(f"Models directory: {MODELS_DIR}")
    
    # Load model
    load_model()
    
    logger.info("Starting Flask server on port 8501...")
    app.run(host='0.0.0.0', port=8501, debug=False)

