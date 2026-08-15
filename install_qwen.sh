#!/bin/bash

set -e  # bricht bei Fehlern ab

echo "🔧 Installing Ollama..."
if ! command -v ollama &> /dev/null
then
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "Ollama already installed"
fi

echo "Checking Ollama version..."
ollama --version

echo "Pulling model qwen2.5-coder..."
ollama pull qwen2.5-coder

echo "Setup finished!"