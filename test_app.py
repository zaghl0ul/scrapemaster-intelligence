import streamlit as st

st.set_page_config(page_title="Test App", page_icon="🧪")

st.title("🧪 ScrapeMaster Test")
st.write("Testing if Streamlit is working properly...")

# Test database creation
try:
    import sqlite3
    from pathlib import Path
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Test database connection
    db_path = data_dir / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY)")
    conn.close()
    
    st.success("✅ Database connection successful!")
    st.write(f"Database path: {db_path.absolute()}")
except Exception as e:
    st.error(f"❌ Database error: {str(e)}")

# Test imports
try:
    from src.core.config import get_config
    st.success("✅ Config module imported successfully!")
except Exception as e:
    st.error(f"❌ Config import error: {str(e)}")

try:
    from src.core.models import ScrapingTarget
    st.success("✅ Models module imported successfully!")
except Exception as e:
    st.error(f"❌ Models import error: {str(e)}")

try:
    from src.core.database import DatabaseManager
    st.success("✅ Database module imported successfully!")
except Exception as e:
    st.error(f"❌ Database import error: {str(e)}")

try:
    from src.core.scraper import WebScraper
    st.success("✅ Scraper module imported successfully!")
except Exception as e:
    st.error(f"❌ Scraper import error: {str(e)}")

st.info("If all tests pass, the main app should work!") 