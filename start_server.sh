#!/bin/bash
# Start script for DSAL Streamlit server

cd "$(dirname "$0")"
source .venv/bin/activate

# Start Streamlit with public access
streamlit run app/main.py \
    --server.port 8502 \
    --server.address 0.0.0.0 \
    --server.headless true
