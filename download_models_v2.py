#!/usr/bin/env python3
"""
Alternative model download script with better error handling
"""

import os
import sys
from pathlib import Path

print("=" * 60)
print("ML Model Download Script (v2 - Enhanced)")
print("=" * 60)

# Create models directory
models_dir = Path("./models")
whisper_dir = models_dir / "whisper"
pyannote_dir = models_dir / "pyannote"

whisper_dir.mkdir(parents=True, exist_ok=True)
pyannote_dir.mkdir(parents=True, exist_ok=True)

print(f"\nModels will be downloaded to: {models_dir.absolute()}")

# Get HF token
hf_token = os.getenv('HF_TOKEN')
if not hf_token:
    print("\n⚠ HF_TOKEN environment variable not set!")
    hf_token = input("Enter your Hugging Face token: ").strip()
    if not hf_token:
        print("❌ No token provided. Exiting.")
        sys.exit(1)

print(f"\n✓ Using HF_TOKEN: {hf_token[:10]}...")

# Download Whisper
print("\n[1/2] Downloading Whisper Large v3 model...")
print("This may take several minutes (~3GB download)...")

try:
    import whisper
    
    # Set download directory
    os.environ['XDG_CACHE_HOME'] = str(models_dir.absolute())
    
    print("Loading Whisper model...")
    model = whisper.load_model("large-v3", download_root=str(whisper_dir.absolute()))
    print("✓ Whisper model downloaded successfully!")
    
except ImportError:
    print("✗ Error: 'whisper' package not installed.")
    print("  Install it with: pip3 install openai-whisper")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error downloading Whisper model: {str(e)}")
    sys.exit(1)

# Download Pyannote with better error handling
print("\n[2/2] Downloading Pyannote speaker diarization model...")
print("⚠  IMPORTANT: You must accept model licenses at:")
print("  1. https://huggingface.co/pyannote/speaker-diarization-3.1")
print("  2. https://huggingface.co/pyannote/segmentation-3.0")
print("")

try:
    from pyannote.audio import Pipeline
    
    # Set Hugging Face cache directory
    os.environ['HF_HOME'] = str(pyannote_dir.absolute())
    
    print("Attempting to download Pyannote pipeline...")
    print("(This will fail if you haven't accepted licenses)")
    
    # Try to load the pipeline
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=hf_token
    )
    print("✓ Pyannote model downloaded successfully!")
    
except ImportError:
    print("✗ Error: 'pyannote.audio' package not installed.")
    print("  Install it with: pip3 install pyannote.audio")
    sys.exit(1)
except Exception as e:
    error_msg = str(e)
    print(f"✗ Error downloading Pyannote model: {error_msg}")
    print("")
    print("=" * 60)
    print("TROUBLESHOOTING STEPS:")
    print("=" * 60)
    print("")
    print("1. Make sure you've accepted ALL model licenses:")
    print("   https://huggingface.co/pyannote/speaker-diarization-3.1")
    print("   https://huggingface.co/pyannote/segmentation-3.0")
    print("")
    print("2. Wait 2-3 minutes after accepting licenses")
    print("")
    print("3. Verify your token is valid:")
    print("   https://huggingface.co/settings/tokens")
    print("")
    print("4. Check if model is gated:")
    if "gated" in error_msg.lower() or "private" in error_msg.lower():
        print("   ⚠  Model is GATED - you MUST accept licenses!")
    print("")
    sys.exit(1)

print("")
print("=" * 60)
print("✓ All models downloaded successfully!")
print("=" * 60)
print("")
print("Models are stored in:")
print(f"  - Whisper: {whisper_dir.absolute()}")
print(f"  - Pyannote: {pyannote_dir.absolute()}")
print("")
print("You can now run: docker-compose up")
print("=" * 60)

