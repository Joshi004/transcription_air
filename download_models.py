#!/usr/bin/env python3
"""
Script to download ML models to the host machine before running containers.
This ensures models are available when containers start.
"""

import os
import sys
from pathlib import Path

print("=" * 60)
print("ML Model Download Script")
print("=" * 60)

# Create models directory
models_dir = Path("./models")
whisper_dir = models_dir / "whisper"
pyannote_dir = models_dir / "pyannote"

whisper_dir.mkdir(parents=True, exist_ok=True)
pyannote_dir.mkdir(parents=True, exist_ok=True)

print(f"\nModels will be downloaded to: {models_dir.absolute()}")

# Download Whisper
print("\n[1/2] Downloading Whisper Large v3 model...")
print("This may take several minutes (~3GB download)...")

try:
    import whisper
    
    # Set download directory
    os.environ['XDG_CACHE_HOME'] = str(models_dir.absolute())
    
    print("Loading Whisper model (will download if not present)...")
    model = whisper.load_model("large-v3", download_root=str(whisper_dir.absolute()))
    print("✓ Whisper model downloaded successfully!")
    
except ImportError:
    print("✗ Error: 'whisper' package not installed.")
    print("  Install it with: pip install openai-whisper")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error downloading Whisper model: {str(e)}")
    sys.exit(1)

# Download Pyannote
print("\n[2/2] Downloading Pyannote speaker diarization model...")
print("This requires a Hugging Face token.")

hf_token = os.getenv('HF_TOKEN')
if not hf_token:
    print("\n⚠ HF_TOKEN environment variable not set!")
    print("  Get your token from: https://huggingface.co/settings/tokens")
    print("  Then run: export HF_TOKEN=your_token_here")
    
    # Ask user if they want to enter token now
    user_input = input("\nEnter your Hugging Face token now (or press Enter to skip): ").strip()
    if user_input:
        hf_token = user_input
    else:
        print("\n⚠ Skipping Pyannote download. You'll need to set HF_TOKEN before running the service.")
        print("\nYou can download Pyannote later by running this script again with HF_TOKEN set.")
        sys.exit(0)

try:
    from pyannote.audio import Pipeline
    
    # Set Hugging Face cache directory
    os.environ['HF_HOME'] = str(pyannote_dir.absolute())
    
    print("Loading Pyannote pipeline (will download if not present)...")
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=hf_token
    )
    print("✓ Pyannote model downloaded successfully!")
    
except ImportError:
    print("✗ Error: 'pyannote.audio' package not installed.")
    print("  Install it with: pip install pyannote.audio")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error downloading Pyannote model: {str(e)}")
    print("\nMake sure your HF_TOKEN is valid and you have accepted the model license at:")
    print("  https://huggingface.co/pyannote/speaker-diarization-3.1")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ All models downloaded successfully!")
print("=" * 60)
print("\nModels are stored in:")
print(f"  - Whisper: {whisper_dir.absolute()}")
print(f"  - Pyannote: {pyannote_dir.absolute()}")
print("\nYou can now run: docker-compose up")
print("=" * 60)

