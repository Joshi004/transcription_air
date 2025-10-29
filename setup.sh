#!/bin/bash

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "========================================"
echo "  Transcription Service Setup Script"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ .env file not found${NC}"
    echo "Creating .env from template..."
    
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env file${NC}"
    else
        echo -e "${RED}✗ .env.example not found!${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${YELLOW}Please edit .env and add your HF_TOKEN:${NC}"
    echo "  1. Get token from: https://huggingface.co/settings/tokens"
    echo "  2. Edit .env file and set: HF_TOKEN=hf_your_token_here"
    echo "  3. Run this script again"
    echo ""
    exit 1
fi

# Load environment if exists
if [ -f .env ]; then
    source .env
fi

echo -e "${GREEN}✓ .env file configured${NC}"
echo ""

# Check if models directory exists
if [ ! -d "models" ]; then
    echo "Creating models directory..."
    mkdir -p models/whisper
    echo -e "${GREEN}✓ Models directory created${NC}"
else
    echo -e "${GREEN}✓ Models directory exists${NC}"
fi
echo ""

# Ask if user wants to download models
echo "Do you want to download Whisper model now? (~3GB, recommended)"
echo "If you skip, model will download when service starts (slower)."
read -p "Download models now? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Checking Python dependencies..."
    
    # Check if python3 is available
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}✗ Python 3 not found${NC}"
        echo "Please install Python 3.10+ and try again"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Python 3 found${NC}"
    echo ""
    
    # Ask if user wants to install dependencies
    echo "Installing Python dependencies (whisper, torch)..."
    echo "This may take a few minutes..."
    read -p "Install dependencies? (y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip3 install openai-whisper torch torchaudio
    fi
    
    echo ""
    echo "Downloading Whisper model..."
    export HF_TOKEN=$HF_TOKEN
    python3 -c "import whisper; whisper.load_model('large-v3', download_root='./models/whisper')"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Model download failed${NC}"
        echo "You can try again later or let Docker download them on first start"
    else
        echo -e "${GREEN}✓ Models downloaded successfully${NC}"
    fi
fi

echo ""
echo "========================================" 
echo "  Building Docker containers..."
echo "========================================"
echo ""

docker-compose build

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Docker build failed${NC}"
    echo "Please check Docker is running and try again"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Docker containers built successfully!${NC}"
echo ""
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
echo "To start the services, run:"
echo -e "  ${GREEN}docker-compose up${NC}"
echo ""
echo "Then open your browser to:"
echo -e "  ${GREEN}http://localhost:3501${NC}"
echo ""
echo "Backend API available at:"
echo -e "  ${GREEN}http://localhost:5501${NC}"
echo ""
echo "To run in background:"
echo -e "  ${GREEN}docker-compose up -d${NC}"
echo ""
echo "Happy transcribing! 🎙️"
echo ""

