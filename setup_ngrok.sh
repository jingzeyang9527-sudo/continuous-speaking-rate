#!/bin/bash
# Quick setup script for ngrok

echo "=== DSAL ngrok Setup ==="
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "ngrok is not installed."
    echo ""
    echo "Please install ngrok:"
    echo "1. Visit https://ngrok.com/download"
    echo "2. Download for Linux"
    echo "3. Extract and move to /usr/local/bin/ngrok"
    echo ""
    echo "Or use snap:"
    echo "  sudo snap install ngrok"
    exit 1
fi

echo "✅ ngrok is installed"
echo ""

# Check if authtoken is configured
if [ ! -f ~/.ngrok2/ngrok.yml ] && [ ! -f ~/.config/ngrok/ngrok.yml ]; then
    echo "⚠️  ngrok authtoken not configured"
    echo ""
    echo "To configure:"
    echo "1. Sign up at https://ngrok.com/ (free)"
    echo "2. Get your authtoken from the dashboard"
    echo "3. Run: ngrok config add-authtoken YOUR_TOKEN"
    echo ""
    read -p "Do you want to configure it now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your ngrok authtoken: " token
        ngrok config add-authtoken "$token"
        echo "✅ Authtoken configured"
    fi
else
    echo "✅ ngrok authtoken is configured"
fi

echo ""
echo "=== Usage ==="
echo ""
echo "Terminal 1 - Start Streamlit:"
echo "  cd /data/jingzeyang/dsal_toolkit"
echo "  source .venv/bin/activate"
echo "  streamlit run app/main.py --server.port 8501"
echo ""
echo "Terminal 2 - Start ngrok:"
echo "  ngrok http 8501"
echo ""
echo "Then share the ngrok URL (e.g., https://abc123.ngrok-free.app) with others!"
echo ""
