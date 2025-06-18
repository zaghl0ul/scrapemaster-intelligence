#!/bin/bash
# Railway startup script for ScrapeMaster

# Set default PORT if not provided
export PORT=${PORT:-8501}

# Start Streamlit with proper configuration
exec streamlit run src/landing_page.py \
  --server.port=$PORT \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false \
  --browser.gatherUsageStats=false \
  --server.fileWatcherType=none 