bash#!/bin/bash
# Start Ollama in the background
ollama serve &

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to start..."
sleep 5

# Start the RunPod worker
echo "🚀 Starting RunPod handler..."
python -u handler.py