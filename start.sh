#!/bin/bash
# Start script for Railway deployment

# Export PORT if not set
export PORT=${PORT:-8501}

# Start Streamlit with the landing page (for marketing)
# Change to src/quick_revenue.py when ready to onboard customers
streamlit run src/landing_page.py \
  --server.port=$PORT \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --browser.serverAddress=0.0.0.0 \
  --browser.gatherUsageStats=false 