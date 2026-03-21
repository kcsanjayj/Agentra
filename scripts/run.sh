#!/bin/bash

# Multi-Agent Executor Launcher
# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${PURPLE}    🚀 MULTI-AGENT EXECUTOR${NC}"
echo -e "${CYAN}========================================${NC}"
echo
echo -e "${BLUE}Starting Multi-Agent Executor System...${NC}"
echo
echo -e "${YELLOW}[1]${NC} Starting Backend Server..."
echo -e "${YELLOW}[2]${NC} Checking Dependencies..."
echo -e "${YELLOW}[3]${NC} Launching Web Interface..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] Python 3 is not installed${NC}"
    echo "Please install Python 3.7+ first"
    exit 1
fi

# Check if required packages are installed
echo -e "${BLUE}Checking required packages...${NC}"
python3 -c "import fastapi, uvicorn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[INFO] Installing required packages...${NC}"
    pip3 install fastapi uvicorn websockets python-multipart
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR] Failed to install packages${NC}"
        exit 1
    fi
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo
echo -e "${GREEN}[SUCCESS] Starting server on http://localhost:8000${NC}"
echo -e "${BLUE}[INFO] Press Ctrl+C to stop the server${NC}"
echo -e "${BLUE}[INFO] Open your browser and navigate to: http://localhost:8000${NC}"
echo
echo -e "${CYAN}========================================${NC}"

# Start the FastAPI server
python3 server.py

# If server stops, wait for user input before closing
echo
echo -e "${YELLOW}Server stopped. Press any key to exit...${NC}"
read -n 1 -s
