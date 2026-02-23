FROM python:3.11.1-slim

WORKDIR /app

# Install Ollama dependencies + curl
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Install Python dependencies
COPY builder/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src/ /app/

# Pull model at build time (bakes it into the image)
RUN ollama serve & sleep 5 && ollama pull qwen3:8b

# Startup script to launch Ollama then the worker
COPY builder/start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]