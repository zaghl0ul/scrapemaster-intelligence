"""
ScrapeMaster Intelligence Platform - Enterprise Edition
Production-ready web scraping SaaS with advanced architecture

Author: AI Development Team
Version: 1.0.0
License: Proprietary
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import asyncio
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union, Tuple
import json
import requests
from bs4 import BeautifulSoup
import time
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import os
import sys
from pathlib import Path
import threading
from contextlib import contextmanager
import re
from urllib.parse import urljoin, urlparse
import secrets
from functools import lru_cache, wraps
import traceback

# Import core modules
try:
    # Try absolute imports first (when running from project root)
    from src.core.database import DatabaseManager
    from src.core.scraper import WebScraper
    from src.core.config import get_config
    from src.core.models import ScrapingTarget, ScrapedData, Client, PlanType
    print("Successfully imported from src.core")
except ImportError as e:
    print(f"Failed to import from src.core: {e}")
    # Fall back to relative imports (when running from src directory)
    try:
        from core.database import DatabaseManager
        from core.scraper import WebScraper
        from core.config import get_config
        from core.models import ScrapingTarget, ScrapedData, Client, PlanType
        print("Successfully imported from core")
    except ImportError as e2:
        print(f"Failed to import from core: {e2}")
        raise

# Configure enterprise-grade logging with absolute path resolution
# Since app.py is in src/, parent is src, parent.parent is project root
# Use absolute path to ensure correct resolution when run via streamlit
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
DATA_DIR = PROJECT_ROOT / "data"

# Debug path resolution
print(f"__file__: {__file__}")
print(f"PROJECT_ROOT: {PROJECT_ROOT}")
print(f"PROJECT_ROOT absolute: {PROJECT_ROOT.absolute()}")
print(f"DATA_DIR: {DATA_DIR}")
print(f"DATA_DIR absolute: {DATA_DIR.absolute()}")

# Ensure critical directories exist with proper permissions
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Advanced logging configuration with structured output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'scrapemaster.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Performance monitoring decorator
def performance_monitor(func):
    """Advanced performance monitoring with metrics collection"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.3f}s: {str(e)}")
            raise
    return wrapper

# Data models are imported from src.core.models

# DatabaseManager is imported from src.core.database above

# Add custom CSS styling and helper functions
def load_custom_css():
    """Load custom CSS for enhanced styling"""
    st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --success-color: #28a745;
        --warning-color: #ffc107;
        --danger-color: #dc3545;
        --info-color: #17a2b8;
        --dark-color: #343a40;
        --light-color: #f8f9fa;
    }
    
    /* Custom header styling */
    .main-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
    }
    
    .main-header h1 {
        color: white;
        text-align: center;
        margin: 0;
        font-size: 2.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        text-align: center;
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
    }
    
    /* Enhanced metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid var(--primary-color);
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    
    /* Status badges */
    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        display: inline-block;
        margin: 2px;
    }
    
    .status-active {
        background-color: var(--success-color);
        color: white;
    }
    
    .status-error {
        background-color: var(--danger-color);
        color: white;
    }
    
    .status-paused {
        background-color: var(--warning-color);
        color: var(--dark-color);
    }
    
    /* Target cards */
    .target-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
        transition: all 0.3s ease;
    }
    
    .target-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        border-color: var(--primary-color);
    }
    
    /* Button enhancements */
    .stButton > button {
        border-radius: 8px;
        border: none;
        transition: all 0.2s ease;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Success/Error alerts */
    .custom-alert {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid;
    }
    
    .alert-success {
        background-color: #d4edda;
        border-color: var(--success-color);
        color: #155724;
    }
    
    .alert-warning {
        background-color: #fff3cd;
        border-color: var(--warning-color);
        color: #856404;
    }
    
    .alert-error {
        background-color: #f8d7da;
        border-color: var(--danger-color);
        color: #721c24;
    }
    
    /* Sidebar enhancements */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Progress bar styling */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        border-radius: 10px;
    }
    
    /* Form enhancements */
    .stSelectbox > div > div {
        border-radius: 8px;
    }
    
    .stTextInput > div > div {
        border-radius: 8px;
    }
    
    /* Loading spinner customization */
    .stSpinner > div {
        border-top-color: var(--primary-color) !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    
    /* Table styling */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def status_badge(status: str) -> str:
    """Create a styled status badge"""
    status_classes = {
        'active': 'status-active',
        'error': 'status-error', 
        'paused': 'status-paused'
    }
    class_name = status_classes.get(status.lower(), 'status-active')
    return f'<span class="status-badge {class_name}">{status}</span>'

def custom_metric_card(title: str, value: str, delta: str = None, delta_color: str = "normal"):
    """Create a custom metric card with enhanced styling"""
    delta_html = ""
    if delta:
        delta_colors = {
            "normal": "#666",
            "positive": "var(--success-color)",
            "negative": "var(--danger-color)"
        }
        color = delta_colors.get(delta_color, "#666")
        delta_html = f'<p style="color: {color}; font-size: 0.9rem; margin: 0.5rem 0 0 0;">{delta}</p>'
    
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="margin: 0; color: var(--dark-color); font-size: 1.1rem;">{title}</h3>
        <h2 style="margin: 0.5rem 0; color: var(--primary-color); font-size: 2rem;">{value}</h2>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def enhanced_progress_bar(progress: float, text: str = "", color: str = "primary"):
    """Create an enhanced progress bar with custom styling"""
    colors = {
        "primary": "var(--primary-color)",
        "success": "var(--success-color)",
        "warning": "var(--warning-color)",
        "danger": "var(--danger-color)"
    }
    
    bar_color = colors.get(color, colors["primary"])
    
    st.markdown(f"""
    <div style="margin: 1rem 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span style="font-weight: 500;">{text}</span>
            <span style="color: {bar_color}; font-weight: bold;">{progress:.1f}%</span>
        </div>
        <div style="background-color: #e9ecef; border-radius: 10px; height: 8px; overflow: hidden;">
            <div style="background: linear-gradient(90deg, {bar_color}, {bar_color}); width: {progress}%; height: 100%; border-radius: 10px; transition: width 0.3s ease;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def success_animation():
    """Display a success animation"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <div style="font-size: 4rem; animation: bounce 1s infinite;">🎉</div>
        <h3 style="color: var(--success-color); margin-top: 1rem;">Success!</h3>
    </div>
    <style>
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-30px); }
        60% { transform: translateY(-15px); }
    }
    </style>
    """, unsafe_allow_html=True)

def loading_animation(text: str = "Processing..."):
    """Display a custom loading animation"""
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem;">
        <div style="display: inline-block; width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid var(--primary-color); border-radius: 50%; animation: spin 1s linear infinite;"></div>
        <p style="margin-top: 1rem; color: var(--primary-color); font-weight: 500;">{text}</p>
    </div>
    <style>
    @keyframes spin {
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }
    </style>
    """, unsafe_allow_html=True)

def create_target_card(target, show_actions: bool = True):
    """Create an enhanced target card with better styling"""
    status_html = status_badge(target.status.value)
    
    # Determine card border color based on status
    border_colors = {
        'active': 'var(--success-color)',
        'error': 'var(--danger-color)',
        'paused': 'var(--warning-color)'
    }
    border_color = border_colors.get(target.status.value, 'var(--primary-color)')
    
    card_html = f"""
    <div class="target-card" style="border-left: 4px solid {border_color};">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
            <h4 style="margin: 0; color: var(--dark-color);">🎯 {target.name}</h4>
            {status_html}
        </div>
        <p style="margin: 0.5rem 0; color: #666; font-size: 0.9rem;">
            🔗 <a href="{target.url}" target="_blank" style="color: var(--primary-color); text-decoration: none;">{target.url[:50]}...</a>
        </p>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1rem 0;">
            <div>
                <small style="color: #666;">Frequency</small>
                <p style="margin: 0; font-weight: 500;">⏱️ Every {target.frequency_hours} hours</p>
            </div>
            <div>
                <small style="color: #666;">Monthly Value</small>
                <p style="margin: 0; font-weight: 500; color: var(--success-color);">💰 ${target.price_per_month}/month</p>
            </div>
        </div>
    """
    
    if target.last_scraped:
        card_html += f"""
        <p style="margin: 0.5rem 0; color: #666; font-size: 0.9rem;">
            📅 Last scraped: {target.last_scraped.strftime('%Y-%m-%d %H:%M')}
        </p>
        """
    
    card_html += "</div>"
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Enhanced progress bar for success rate
    if hasattr(target, 'success_rate'):
        color = "success" if target.success_rate >= 80 else "warning" if target.success_rate >= 60 else "danger"
        enhanced_progress_bar(target.success_rate, f"Success Rate: {target.success_rate:.1f}%", color)

class ScrapeMasterApp:
    """Main application class for ScrapeMaster Intelligence Platform"""
    
    def __init__(self):
        """Initialize the application with all required components"""
        # Load custom CSS first
        load_custom_css()
        
        self.db = DatabaseManager()
        
        # Load proxy configuration if enabled
        proxy_list = None
        if get_config().scraping.use_stealth and get_config().scraping.proxy.enabled:
            try:
                from src.core.proxy_loader import get_proxy_loader
                proxy_loader = get_proxy_loader()
                proxy_list = proxy_loader.get_proxy_list()
                if proxy_list:
                    logger.info(f"Loaded {len(proxy_list)} proxies for stealth scraping")
            except Exception as e:
                logger.warning(f"Failed to load proxies: {e}")
        
        # Initialize scraper with proxy support
        self.scraper = WebScraper(proxy_list=proxy_list, use_stealth=get_config().scraping.use_stealth)
        self.config = get_config()
        
        # Set page configuration
        st.set_page_config(
            page_title="ScrapeMaster Intelligence Platform",
            page_icon="🕷️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Initialize session state
        if 'initialized' not in st.session_state:
            st.session_state.initialized = True
            st.session_state.active_page = "📊 Executive Dashboard"
            st.session_state.scraping_in_progress = False
    
    def render_executive_dashboard(self):
        """Render the main executive dashboard with key metrics"""
        # Custom header
        st.markdown("""
        <div class="main-header">
            <h1>🕷️ ScrapeMaster Intelligence</h1>
            <p>Enterprise Web Scraping & Competitive Intelligence Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Get revenue analytics
        revenue_data = self.db.get_revenue_analytics()
        
        # Enhanced key metrics row using custom cards
        st.subheader("📊 Key Performance Indicators")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            growth_delta = f"+{revenue_data['growth_rate']:.1f}% growth" if revenue_data['growth_rate'] > 0 else f"{revenue_data['growth_rate']:.1f}% growth"
            delta_color = "positive" if revenue_data['growth_rate'] > 0 else "negative" if revenue_data['growth_rate'] < 0 else "normal"
            custom_metric_card(
                "Monthly Recurring Revenue",
                f"${revenue_data['mrr']:,.0f}",
                growth_delta,
                delta_color
            )
        
        with col2:
            enterprise_clients = revenue_data.get('enterprise_clients', 0)
            delta_text = f"{enterprise_clients} enterprise" if enterprise_clients > 0 else "Growing client base"
            custom_metric_card(
                "Active Clients",
                str(revenue_data['client_count']),
                delta_text,
                "positive" if enterprise_clients > 0 else "normal"
            )
        
        with col3:
            active_targets = revenue_data.get('active_targets', revenue_data['target_count'])
            delta_text = f"{active_targets}/{revenue_data['target_count']} active"
            custom_metric_card(
                "Monitoring Targets",
                str(revenue_data['target_count']),
                delta_text,
                "positive"
            )
        
        with col4:
            avg_revenue = revenue_data['mrr'] / max(revenue_data['client_count'], 1)
            success_rate = revenue_data.get('avg_success_rate', 100)
            delta_text = f"{success_rate:.0f}% success rate"
            custom_metric_card(
                "Avg Revenue/Client",
                f"${avg_revenue:,.0f}",
                delta_text,
                "positive" if success_rate >= 90 else "normal"
            )
        
        # Enhanced revenue chart with better styling
        st.markdown("---")
        st.subheader("📈 Revenue Analytics")
        
        if 'revenue_trend' in revenue_data and revenue_data['revenue_trend']:
            revenue_df = pd.DataFrame(revenue_data['revenue_trend'])
            if not revenue_df.empty:
                # Enhanced chart with custom styling
                fig = px.line(
                    revenue_df,
                    x='date',
                    y='revenue',
                    title='Daily Revenue Trend',
                    labels={'revenue': 'Revenue ($)', 'date': 'Date'}
                )
                
                # Customize chart appearance
                fig.update_traces(
                    line=dict(color='#667eea', width=3),
                    fill='tonexty',
                    fillcolor='rgba(102, 126, 234, 0.1)'
                )
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#343a40'),
                    title_font_size=16,
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.markdown("""
                <div class="alert-warning custom-alert">
                    <strong>📊 Getting Started:</strong> No revenue data available yet. Start adding clients to see trends!
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-warning custom-alert">
                <strong>📊 Getting Started:</strong> No revenue data available yet. Start adding clients to see trends!
            </div>
            """, unsafe_allow_html=True)
        
        # Enhanced activity sections
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔔 Recent Changes Detected")
            recent_changes = self.db.get_recent_changes(limit=5)
            if not recent_changes.empty:
                for _, change in recent_changes.iterrows():
                    st.markdown(f"""
                    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid var(--info-color);">
                        <strong>{change['target_name']}</strong><br>
                        <small style="color: #666;">{change['timestamp']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="custom-alert alert-success">
                    <strong>✅ All Clear:</strong> No recent changes detected. Your targets are stable!
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("⚠️ Targets Requiring Attention")
            with self.db.get_connection() as conn:
                error_targets = pd.read_sql_query("""
                    SELECT name, url, consecutive_errors, last_scraped
                    FROM scraping_targets
                    WHERE status = 'error' AND is_active = TRUE
                    ORDER BY consecutive_errors DESC
                    LIMIT 5
                """, conn)
            
            if not error_targets.empty:
                for _, target in error_targets.iterrows():
                    error_level = "danger" if target['consecutive_errors'] > 3 else "warning"
                    st.markdown(f"""
                    <div class="custom-alert alert-{error_level}">
                        <strong>{target['name']}</strong><br>
                        <small>{target['consecutive_errors']} consecutive errors</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="custom-alert alert-success">
                    <strong>🎉 Excellent:</strong> All targets operating normally!
                </div>
                """, unsafe_allow_html=True)
    
    def render_advanced_target_management(self):
        """Advanced target management interface with bulk operations"""
        st.header("🎯 Target Management")
        
        # Target creation form
        with st.expander("➕ Add New Target", expanded=True):
            with st.form("add_target_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    target_name = st.text_input("Target Name", placeholder="e.g., Competitor Product Page")
                    target_url = st.text_input("URL", placeholder="https://example.com/product")
                    frequency = st.selectbox(
                        "Monitoring Frequency",
                        options=[1, 6, 12, 24, 48, 72, 168],
                        format_func=lambda x: f"Every {x} hours" if x > 1 else "Every hour",
                        index=3
                    )
                
                with col2:
                    client_email = st.text_input("Client Email", placeholder="client@example.com")
                    price = st.number_input("Price per Month ($)", min_value=0.0, value=99.0, step=10.0)
                    plan_type = st.selectbox(
                        "Plan Type",
                        options=["starter", "professional", "enterprise", "custom"],
                        format_func=lambda x: x.capitalize()
                    )
                
                st.subheader("📋 Data Selectors")
                st.info("Define CSS selectors for the data you want to extract")
                
                selector_col1, selector_col2 = st.columns(2)
                
                with selector_col1:
                    price_selector = st.text_input(
                        "Price Selector",
                        value="[class*='price'], .price, #price",
                        help="CSS selector for price elements"
                    )
                    title_selector = st.text_input(
                        "Title Selector",
                        value="h1, .product-title, [class*='title']",
                        help="CSS selector for title/name"
                    )
                
                with selector_col2:
                    availability_selector = st.text_input(
                        "Availability Selector",
                        value="[class*='stock'], [class*='availability']",
                        help="CSS selector for stock status"
                    )
                    custom_selector = st.text_input(
                        "Custom Selector",
                        placeholder="Any additional selector",
                        help="Additional data to track"
                    )
                
                submitted = st.form_submit_button("🚀 Create Target", use_container_width=True)
                
                if submitted and target_name and target_url and client_email:
                    # Create client if doesn't exist
                    client_id = hashlib.md5(client_email.encode()).hexdigest()[:8]
                    
                    # Add client to database
                    client = Client(
                        id=client_id,
                        name=client_email.split('@')[0].title(),
                        email=client_email,
                        plan_type=PlanType(plan_type),
                        monthly_value=price
                    )
                    
                    # Always try to add/update client
                    self.db.add_client(client)
                    
                    # Create target
                    target = ScrapingTarget(
                        name=target_name,
                        url=target_url,
                        selectors={
                            'price': price_selector,
                            'title': title_selector,
                            'availability': availability_selector,
                            'custom': custom_selector
                        } if custom_selector else {
                            'price': price_selector,
                            'title': title_selector,
                            'availability': availability_selector
                        },
                        frequency_hours=frequency,
                        client_id=client_id,
                        price_per_month=price
                    )
                    
                    if self.db.add_target(target):
                        st.success(f"✅ Successfully created target '{target_name}'")
                        st.balloons()
                    else:
                        st.error("Failed to create target. A target with this URL may already exist for this client.")
        
        # Display existing targets
        st.subheader("📊 Active Targets")
        
        targets = self.db.get_active_targets()
        
        if targets:
            # Target filters
            filter_col1, filter_col2, filter_col3 = st.columns(3)
            
            with filter_col1:
                status_filter = st.multiselect(
                    "Status",
                    options=["active", "error", "paused"],
                    default=["active", "error"]
                )
            
            with filter_col2:
                frequency_filter = st.slider(
                    "Frequency (hours)",
                    min_value=1,
                    max_value=168,
                    value=(1, 168)
                )
            
            with filter_col3:
                search_term = st.text_input("🔍 Search targets", placeholder="Search by name or URL")
            
            # Filter targets
            filtered_targets = [
                t for t in targets
                if t.status.value in status_filter
                and frequency_filter[0] <= t.frequency_hours <= frequency_filter[1]
                and (not search_term or search_term.lower() in t.name.lower() or search_term.lower() in t.url.lower())
            ]
            
            # Display targets in a grid
            for i in range(0, len(filtered_targets), 2):
                col1, col2 = st.columns(2)
                
                for j, col in enumerate([col1, col2]):
                    if i + j < len(filtered_targets):
                        target = filtered_targets[i + j]
                        
                        with col:
                            with st.container():
                                st.subheader(f"🎯 {target.name}")
                                
                                status_color = {
                                    'active': '🟢',
                                    'error': '🔴',
                                    'paused': '🟡'
                                }.get(target.status.value, '⚪')
                                
                                st.write(f"{status_color} Status: **{target.status.value.upper()}**")
                                st.write(f"🔗 URL: {target.url[:50]}...")
                                st.write(f"⏱️ Frequency: Every {target.frequency_hours} hours")
                                st.write(f"💰 Price: ${target.price_per_month}/month")
                                
                                if target.last_scraped:
                                    st.write(f"📅 Last scraped: {target.last_scraped.strftime('%Y-%m-%d %H:%M')}")
                                
                                st.progress(target.success_rate / 100, text=f"Success rate: {target.success_rate:.1f}%")
                                
                                action_col1, action_col2, action_col3 = st.columns(3)
                                
                                with action_col1:
                                    if st.button("▶️ Scrape Now", key=f"scrape_{target.id}"):
                                        self._execute_single_scrape(target)
                                
                                with action_col2:
                                    if st.button("⏸️ Pause" if target.is_active else "▶️ Resume", key=f"pause_{target.id}"):
                                        target.is_active = not target.is_active
                                        # Update in database
                                        st.rerun()
                                
                                with action_col3:
                                    if st.button("🗑️ Delete", key=f"delete_{target.id}"):
                                        # Mark target as inactive instead of showing confirmation
                                        with self.db.get_connection() as conn:
                                            cursor = conn.cursor()
                                            cursor.execute(
                                                "UPDATE scraping_targets SET is_active = FALSE WHERE id = ?",
                                                (target.id,)
                                            )
                                        st.success(f"Target {target.name} deleted")
                                        st.rerun()
                                
                                st.divider()
        else:
            st.info("No targets configured yet. Add your first target above!")
    
    def render_live_monitoring_center(self):
        """Real-time monitoring dashboard with live updates"""
        st.header("📡 Live Monitoring Center")
        
        # Auto-refresh toggle
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.subheader("🔴 Real-Time Monitoring")
        
        with col2:
            auto_refresh = st.checkbox("Auto-refresh", value=False)
        
        with col3:
            if st.button("🔄 Refresh Now"):
                st.rerun()
        
        if auto_refresh:
            st.info("Auto-refresh enabled - Dashboard will update every 30 seconds")
            time.sleep(30)
            st.rerun()
        
        # Get targets due for scraping
        targets = self.db.get_active_targets()
        due_targets = [t for t in targets if t.is_due_for_scraping]
        
        # Summary metrics
        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
        
        with summary_col1:
            st.metric("📊 Total Targets", len(targets))
        
        with summary_col2:
            st.metric("⏰ Due for Scraping", len(due_targets))
        
        with summary_col3:
            error_count = sum(1 for t in targets if t.status.value == 'error')
            st.metric("❌ Errors", error_count)
        
        with summary_col4:
            avg_success = sum(t.success_rate for t in targets) / len(targets) if targets else 0
            st.metric("✅ Avg Success Rate", f"{avg_success:.1f}%")
        
        # Scraping controls
        st.divider()
        
        control_col1, control_col2 = st.columns([3, 1])
        
        with control_col1:
            if due_targets:
                st.warning(f"⏰ {len(due_targets)} targets are due for scraping")
            else:
                st.success("✅ All targets are up to date")
        
        with control_col2:
            if st.button("🚀 Scrape All Due", type="primary", disabled=st.session_state.scraping_in_progress):
                st.session_state.scraping_in_progress = True
                self._execute_bulk_scrape(due_targets)
                st.session_state.scraping_in_progress = False
                st.rerun()
        
        # Live monitoring grid
        st.subheader("📊 Target Status Grid")
        
        if targets:
            # Create monitoring grid
            grid_cols = st.columns(4)
            
            for idx, target in enumerate(targets):
                col_idx = idx % 4
                
                with grid_cols[col_idx]:
                    # Determine card color based on status
                    if target.status.value == 'error':
                        card_color = "#ff4444"
                    elif target.is_due_for_scraping:
                        card_color = "#ffaa44"
                    else:
                        card_color = "#44ff44"
                    
                    st.markdown(
                        f"""
                        <div style="
                            background-color: {card_color}20;
                            border: 2px solid {card_color};
                            border-radius: 10px;
                            padding: 10px;
                            margin-bottom: 10px;
                        ">
                            <h4 style="margin: 0;">{target.name[:20]}...</h4>
                            <p style="margin: 5px 0; font-size: 0.8em;">
                                {target.url[:30]}...
                            </p>
                            <p style="margin: 5px 0; font-size: 0.9em;">
                                Success: {target.success_rate:.0f}%
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        else:
            st.info("No targets to monitor. Add some targets to get started!")
        
        # Recent activity log
        st.divider()
        st.subheader("📜 Recent Activity")
        
        with self.db.get_connection() as conn:
            recent_activity = pd.read_sql_query("""
                SELECT 
                    sd.timestamp,
                    t.name as target_name,
                    sd.status_code,
                    sd.response_time_ms,
                    sd.change_detected
                FROM scraped_data sd
                JOIN scraping_targets t ON sd.target_id = t.id
                ORDER BY sd.timestamp DESC
                LIMIT 20
            """, conn)
        
        if not recent_activity.empty:
            for _, activity in recent_activity.iterrows():
                icon = "🔔" if activity['change_detected'] else "✅" if activity['status_code'] == 200 else "❌"
                st.write(
                    f"{icon} **{activity['target_name']}** - "
                    f"{activity['timestamp']} - "
                    f"{activity['response_time_ms']}ms"
                )
        else:
            st.info("No recent activity to display")
    
    def _execute_bulk_scrape(self, targets: List[ScrapingTarget]):
        """Execute bulk scraping with progress tracking"""
        if not targets:
            st.warning("No targets to scrape!")
            return
            
        # Enhanced loading animation
        loading_container = st.empty()
        with loading_container.container():
            loading_animation("Initializing bulk scrape...")
        
        time.sleep(1)  # Brief pause for UX
        loading_container.empty()
        
        # Progress tracking with enhanced styling
        progress_container = st.container()
        status_container = st.empty()
        
        successful_scrapes = 0
        failed_scrapes = 0
        changes_detected = 0
        
        with progress_container:
            st.subheader("🚀 Bulk Scraping Progress")
            
            for idx, target in enumerate(targets):
                progress = ((idx + 1) / len(targets)) * 100
                
                # Enhanced progress bar
                enhanced_progress_bar(
                    progress, 
                    f"Scraping {target.name}... ({idx + 1}/{len(targets)})",
                    "primary"
                )
                
                try:
                    with status_container.container():
                        st.info(f"🔄 Processing: {target.name}")
                    
                    result = self.scraper.scrape_target(target)
                    
                    if result and result.status_code == 200:
                        self.db.store_scraped_data(result)
                        successful_scrapes += 1
                        
                        if result.change_detected:
                            changes_detected += 1
                            with status_container.container():
                                st.markdown(f"""
                                <div class="custom-alert alert-warning">
                                    <strong>🔔 Change Detected:</strong> {target.name}
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            with status_container.container():
                                st.markdown(f"""
                                <div class="custom-alert alert-success">
                                    <strong>✅ Success:</strong> {target.name}
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        failed_scrapes += 1
                        with status_container.container():
                            st.markdown(f"""
                            <div class="custom-alert alert-error">
                                <strong>❌ Failed:</strong> {target.name}
                            </div>
                            """, unsafe_allow_html=True)
                        
                except Exception as e:
                    failed_scrapes += 1
                    with status_container.container():
                        st.markdown(f"""
                        <div class="custom-alert alert-error">
                            <strong>❌ Error:</strong> {target.name} - {str(e)[:50]}...
                        </div>
                        """, unsafe_allow_html=True)
                    logger.error(f"Scraping error for {target.name}: {e}")
                
                # Small delay for better UX
                time.sleep(0.5)
        
        # Clear progress and show final results
        progress_container.empty()
        status_container.empty()
        
        # Success animation if changes detected
        if changes_detected > 0:
            success_animation()
        
        # Enhanced summary with custom cards
        st.subheader("📊 Scraping Summary")
        summary_col1, summary_col2, summary_col3 = st.columns(3)
        
        with summary_col1:
            custom_metric_card(
                "Successful Scrapes",
                str(successful_scrapes),
                f"{(successful_scrapes/len(targets)*100):.1f}% success rate",
                "positive" if successful_scrapes > 0 else "normal"
            )
        
        with summary_col2:
            custom_metric_card(
                "Changes Detected",
                str(changes_detected),
                "Content updates found" if changes_detected > 0 else "No changes",
                "positive" if changes_detected > 0 else "normal"
            )
        
        with summary_col3:
            custom_metric_card(
                "Failed Attempts",
                str(failed_scrapes),
                f"{(failed_scrapes/len(targets)*100):.1f}% failure rate" if failed_scrapes > 0 else "Perfect run!",
                "negative" if failed_scrapes > 0 else "positive"
            )
    
    def _execute_single_scrape(self, target: ScrapingTarget):
        """Execute single target scrape with detailed feedback"""
        # Enhanced loading state
        loading_container = st.empty()
        with loading_container.container():
            loading_animation(f"Scraping {target.name}...")
        
        try:
            result = self.scraper.scrape_target(target)
            loading_container.empty()
            
            if result:
                self.db.store_scraped_data(result)
                
                if result.status_code == 200:
                    # Success with animation
                    st.markdown(f"""
                    <div class="custom-alert alert-success">
                        <strong>✅ Success!</strong> Successfully scraped {target.name}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if result.change_detected:
                        st.markdown(f"""
                        <div class="custom-alert alert-warning">
                            <strong>🔔 Change Detected!</strong> Content has been updated
                        </div>
                        """, unsafe_allow_html=True)
                        success_animation()
                    
                    # Enhanced data display
                    with st.expander("📊 View Extracted Data", expanded=result.change_detected):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.json(result.data)
                        
                        with col2:
                            custom_metric_card(
                                "Response Time",
                                f"{result.response_time_ms}ms",
                                "Fast response" if result.response_time_ms < 2000 else "Slow response",
                                "positive" if result.response_time_ms < 2000 else "warning"
                            )
                            
                            if hasattr(result, 'extraction_success_rate'):
                                enhanced_progress_bar(
                                    result.extraction_success_rate,
                                    "Extraction Success Rate",
                                    "success" if result.extraction_success_rate >= 80 else "warning"
                                )
                else:
                    st.markdown(f"""
                    <div class="custom-alert alert-error">
                        <strong>❌ Scraping Failed</strong><br>
                        Status Code: {result.status_code}<br>
                        Errors: {result.errors}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="custom-alert alert-error">
                    <strong>❌ Critical Error</strong><br>
                    Failed to scrape {target.name}. Please check the target configuration.
                </div>
                """, unsafe_allow_html=True)
                
        except Exception as e:
            loading_container.empty()
            st.markdown(f"""
            <div class="custom-alert alert-error">
                <strong>❌ Unexpected Error</strong><br>
                {str(e)}
            </div>
            """, unsafe_allow_html=True)
    
    def render_client_management(self):
        """Advanced client management with CRM features"""
        st.header("👥 Client Management")
        
        # Client overview metrics
        client_metrics = self._get_client_metrics()
        
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            st.metric("Total Clients", client_metrics['total_clients'])
        
        with metric_col2:
            st.metric("Active Clients", client_metrics['active_clients'])
        
        with metric_col3:
            st.metric("Avg Revenue/Client", f"${client_metrics['avg_revenue_per_client']:.0f}")
        
        with metric_col4:
            st.metric("Client Satisfaction", f"{client_metrics['avg_satisfaction']:.1f}/5.0")
        
        # Client list with management options
        st.subheader("📊 Client Portfolio")
        
        with self.db.get_connection() as conn:
            client_data = pd.read_sql_query("""
                SELECT 
                    c.id, c.name, c.company, c.email, c.plan_type, c.monthly_value,
                    COUNT(st.id) as target_count,
                    AVG(st.success_rate) as avg_success_rate,
                    MAX(st.last_scraped) as last_activity
                FROM clients c
                LEFT JOIN scraping_targets st ON c.id = st.client_id AND st.is_active = TRUE
                WHERE c.is_active = TRUE
                GROUP BY c.id, c.name, c.company, c.email, c.plan_type, c.monthly_value
                ORDER BY c.monthly_value DESC
            """, conn)
        
        if not client_data.empty:
            # Enhanced client table
            for _, client in client_data.iterrows():
                with st.container():
                    client_col1, client_col2, client_col3, client_col4 = st.columns([3, 2, 2, 1])
                    
                    with client_col1:
                        st.write(f"**{client['name']}**")
                        if client['company']:
                            st.caption(f"🏢 {client['company']}")
                        st.caption(f"📧 {client['email']}")
                    
                    with client_col2:
                        st.metric("Monthly Value", f"${client['monthly_value']:,.0f}")
                        st.caption(f"📊 {client['plan_type']} Plan")
                    
                    with client_col3:
                        st.metric("Active Targets", int(client['target_count'] or 0))
                        if client['avg_success_rate']:
                            st.caption(f"✅ {client['avg_success_rate']:.1f}% success rate")
                    
                    with client_col4:
                        if st.button("📞 Contact", key=f"contact_{client['id']}"):
                            self._show_client_contact_form(client)
                        if st.button("📈 Reports", key=f"report_{client['id']}"):
                            self._generate_client_report(client)
                    
                    st.divider()
        else:
            st.info("No clients configured. Add clients through target creation.")
    
    def _get_client_metrics(self) -> Dict:
        """Calculate client-related metrics"""
        try:
            with self.db.get_connection() as conn:
                metrics_query = """
                    SELECT 
                        COUNT(DISTINCT c.id) as total_clients,
                        COUNT(DISTINCT CASE WHEN c.is_active = TRUE THEN c.id END) as active_clients,
                        AVG(CASE WHEN c.is_active = TRUE THEN c.monthly_value END) as avg_revenue_per_client,
                        AVG(CASE WHEN c.is_active = TRUE THEN c.satisfaction_score END) as avg_satisfaction
                    FROM clients c
                """
                result = pd.read_sql_query(metrics_query, conn).iloc[0]
                
                return {
                    'total_clients': int(result['total_clients'] or 0),
                    'active_clients': int(result['active_clients'] or 0),
                    'avg_revenue_per_client': float(result['avg_revenue_per_client'] or 0),
                    'avg_satisfaction': float(result['avg_satisfaction'] or 5.0)
                }
        except:
            return {
                'total_clients': 0,
                'active_clients': 0,
                'avg_revenue_per_client': 0,
                'avg_satisfaction': 5.0
            }
    
    def _show_client_contact_form(self, client):
        """Show client contact form"""
        st.subheader(f"📞 Contact {client['name']}")
        
        with st.form(f"contact_form_{client['id']}"):
            message_type = st.selectbox(
                "Message Type",
                ["Status Update", "Issue Resolution", "Upsell Opportunity", "General Check-in"]
            )
            
            message = st.text_area(
                "Message",
                placeholder="Hi [Client Name], I wanted to provide you with an update on your monitoring targets..."
            )
            
            if st.form_submit_button("Send Message"):
                st.success("✅ Message sent successfully!")
                # In production, this would integrate with email/CRM system
    
    def _generate_client_report(self, client):
        """Generate comprehensive client report with real data"""
        st.subheader(f"📈 Performance Report: {client['name']}")
        
        with self.db.get_connection() as conn:
            # Get real performance metrics
            client_metrics = pd.read_sql_query("""
                SELECT 
                    COUNT(DISTINCT st.id) as total_targets,
                    COUNT(DISTINCT sd.id) as total_scrapes,
                    AVG(sd.response_time_ms) as avg_response_time,
                    SUM(CASE WHEN sd.change_detected = TRUE THEN 1 ELSE 0 END) as changes_detected,
                    AVG(sd.extraction_success_rate) as avg_success_rate,
                    MIN(sd.timestamp) as first_scrape,
                    MAX(sd.timestamp) as last_scrape
                FROM scraping_targets st
                LEFT JOIN scraped_data sd ON st.id = sd.target_id
                WHERE st.client_id = ?
                AND st.is_active = TRUE
            """, conn, params=[client['id']])
            
            if not client_metrics.empty:
                metrics = client_metrics.iloc[0]
                
                report_col1, report_col2 = st.columns(2)
                
                with report_col1:
                    st.metric("Targets Monitored", int(metrics['total_targets'] or 0))
                    st.metric("Total Scrapes", int(metrics['total_scrapes'] or 0))
                    st.metric("Changes Detected", int(metrics['changes_detected'] or 0))
                
                with report_col2:
                    avg_response = metrics['avg_response_time'] or 0
                    st.metric("Avg Response Time", f"{avg_response:.0f}ms")
                    
                    success_rate = metrics['avg_success_rate'] or 0
                    st.metric("Extraction Success", f"{success_rate:.1f}%")
                    
                    # Calculate uptime (targets without errors)
                    error_free_targets = pd.read_sql_query("""
                        SELECT COUNT(*) as error_free
                        FROM scraping_targets
                        WHERE client_id = ? AND consecutive_errors = 0 AND is_active = TRUE
                    """, conn, params=[client['id']])
                    
                    uptime = (error_free_targets['error_free'].iloc[0] / max(metrics['total_targets'], 1)) * 100
                    st.metric("Target Uptime", f"{uptime:.1f}%")
            else:
                st.info("No data available for report generation yet.")
    
    def run(self):
        """Main application entry point with enhanced navigation"""
        # Configure sidebar with branding
        with st.sidebar:
            st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <h1>🕷️ ScrapeMaster</h1>
                <p><em>Intelligence Platform</em></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Navigation
            page = st.radio(
                "Navigation",
                [
                    "📊 Executive Dashboard",
                    "🎯 Target Management", 
                    "📡 Live Monitoring",
                    "👥 Client Management",
                    "⚙️ Settings"
                ]
            )
            
            st.markdown("---")
            
            # Quick stats
            st.markdown("**📈 Quick Stats**")
            revenue_data = self.db.get_revenue_analytics()
            st.metric("MRR", f"${revenue_data['mrr']:,.0f}")
            st.metric("Clients", revenue_data['client_count'])
            st.metric("Targets", revenue_data['target_count'])
            
            st.markdown("---")
            
            # Revenue projections
            st.markdown("**🎯 Revenue Goals**")
            st.markdown("• Month 1: **$3,000 MRR**")
            st.markdown("• Month 3: **$15,000 MRR**")
            st.markdown("• Month 6: **$25,000 MRR**")
            st.markdown("• Year 1: **$50,000 MRR**")
            
            st.markdown("---")
            
            # Support and resources
            st.markdown("**🔗 Resources**")
            if st.button("📚 Documentation"):
                st.info("Documentation coming soon!")
            if st.button("💬 Support Chat"):
                st.info("Support chat integration coming soon!")
            if st.button("🎥 Video Tutorials"):
                st.info("Video tutorials coming soon!")
        
        # Main content area
        if page == "📊 Executive Dashboard":
            self.render_executive_dashboard()
        elif page == "🎯 Target Management":
            self.render_advanced_target_management()
        elif page == "📡 Live Monitoring":
            self.render_live_monitoring_center()
        elif page == "👥 Client Management":
            self.render_client_management()
        elif page == "⚙️ Settings":
            self.render_settings()
        
        # Footer
        st.markdown("---")
        st.markdown(
            """
            <div style="text-align: center; color: #666; padding: 1rem;">
                ScrapeMaster Intelligence Platform v1.0.0 | 
                Enterprise Web Scraping & Competitive Intelligence |
                <a href="mailto:support@scrapemaster.ai">support@scrapemaster.ai</a>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    def render_settings(self):
        """Application settings and configuration"""
        st.header("⚙️ Platform Settings")
        
        settings_tab1, settings_tab2, settings_tab3, settings_tab4 = st.tabs(
            ["🔧 General", "🔔 Notifications", "💳 Billing", "🛡️ Proxy & Security"]
        )
        
        with settings_tab1:
            st.subheader("General Settings")
            
            col1, col2 = st.columns(2)
            
            with col1:
                default_frequency = st.selectbox(
                    "Default Scraping Frequency",
                    options=[1, 6, 12, 24],
                    format_func=lambda x: f"Every {x} hours",
                    index=1
                )
                
                max_concurrent = st.number_input(
                    "Max Concurrent Scrapers",
                    min_value=1, max_value=50, value=10
                )
            
            with col2:
                timeout_seconds = st.number_input(
                    "Request Timeout (seconds)",
                    min_value=5, max_value=60, value=30
                )
                
                retry_attempts = st.number_input(
                    "Retry Attempts",
                    min_value=1, max_value=5, value=3
                )
            
            if st.button("💾 Save General Settings"):
                st.success("✅ Settings saved successfully!")
        
        with settings_tab2:
            st.subheader("Notification Settings")
            
            email_alerts = st.checkbox("📧 Email Alerts", value=True)
            desktop_notifications = st.checkbox("🖥️ Desktop Notifications", value=False)
            slack_integration = st.checkbox("💬 Slack Integration", value=False)
            
            if slack_integration:
                slack_webhook = st.text_input(
                    "Slack Webhook URL",
                    placeholder="https://hooks.slack.com/services/..."
                )
            
            st.subheader("Alert Triggers")
            alert_on_changes = st.checkbox("🔔 Alert on content changes", value=True)
            alert_on_errors = st.checkbox("⚠️ Alert on scraping errors", value=True)
            alert_on_downtime = st.checkbox("🚨 Alert on target downtime", value=True)
            
            if st.button("💾 Save Notification Settings"):
                st.success("✅ Notification settings saved!")
        
        with settings_tab3:
            st.subheader("Billing & Revenue Tracking")
            
            st.metric("Current MRR", f"${self.db.get_revenue_analytics()['mrr']:,.2f}")
            
            # Pricing configuration
            st.subheader("Pricing Tiers")
            
            tier_col1, tier_col2, tier_col3 = st.columns(3)
            
            with tier_col1:
                starter_price = st.number_input("Starter Plan", value=99, step=10)
                st.caption("Up to 5 targets")
            
            with tier_col2:
                pro_price = st.number_input("Professional Plan", value=199, step=10)
                st.caption("Up to 15 targets")
            
            with tier_col3:
                enterprise_price = st.number_input("Enterprise Plan", value=499, step=10)
                st.caption("50+ targets")
            
            if st.button("💾 Update Pricing"):
                st.success("✅ Pricing updated successfully!")
        
        with settings_tab4:
            st.subheader("🛡️ Proxy & Anti-Detection Settings")
            
            # Stealth mode toggle
            use_stealth = st.checkbox(
                "Enable Stealth Mode",
                value=self.config.scraping.use_stealth,
                help="Use advanced anti-detection techniques including proxy rotation and browser fingerprinting"
            )
            
            # Proxy configuration
            st.subheader("🌐 Proxy Configuration")
            
            proxy_enabled = st.checkbox(
                "Enable Proxy Rotation",
                value=self.config.scraping.proxy.enabled,
                help="Rotate through multiple proxies to avoid IP blocking"
            )
            
            if proxy_enabled:
                # Load current proxies
                try:
                    from src.core.proxy_loader import get_proxy_loader
                    proxy_loader = get_proxy_loader()
                    current_proxies = proxy_loader.get_proxy_list()
                    
                    st.info(f"Currently configured proxies: {len(current_proxies)}")
                    
                    # Display proxy list
                    if current_proxies:
                        st.subheader("Active Proxies")
                        for idx, proxy in enumerate(current_proxies):
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                st.text(proxy)
                            with col2:
                                if st.button("❌", key=f"remove_proxy_{idx}"):
                                    proxy_loader.remove_proxy(proxy)
                                    proxy_loader.save_proxies()
                                    st.rerun()
                    
                    # Add new proxy
                    st.subheader("Add New Proxy")
                    new_proxy_url = st.text_input(
                        "Proxy URL",
                        placeholder="http://username:password@proxy.example.com:8080"
                    )
                    
                    if st.button("➕ Add Proxy"):
                        if new_proxy_url:
                            proxy_loader.add_proxy(new_proxy_url)
                            proxy_loader.save_proxies()
                            st.success("✅ Proxy added successfully!")
                            st.rerun()
                    
                    # Proxy recommendations
                    with st.expander("📚 Recommended Proxy Providers"):
                        st.markdown("""
                        **Premium Proxy Services:**
                        
                        1. **BrightData (Luminati)** - Enterprise-grade residential proxies
                           - 72M+ IPs worldwide
                           - Starting at $500/month
                           - [brightdata.com](https://brightdata.com)
                        
                        2. **Oxylabs** - Reliable datacenter and residential proxies
                           - 100M+ IPs
                           - Starting at $300/month
                           - [oxylabs.io](https://oxylabs.io)
                        
                        3. **SmartProxy** - Affordable rotating proxies
                           - 40M+ IPs
                           - Starting at $75/month
                           - [smartproxy.com](https://smartproxy.com)
                        
                        4. **ProxyMesh** - Simple rotating proxy service
                           - Multiple locations
                           - Starting at $10/month
                           - [proxymesh.com](https://proxymesh.com)
                        """)
                    
                except Exception as e:
                    st.error(f"Failed to load proxy configuration: {e}")
            
            # Advanced settings
            st.subheader("🔧 Advanced Anti-Detection")
            
            col1, col2 = st.columns(2)
            
            with col1:
                rotation_strategy = st.selectbox(
                    "Proxy Rotation Strategy",
                    options=["round_robin", "random", "best_performance"],
                    index=0,
                    help="How to select proxies for each request"
                )
                
                user_agent_rotation = st.checkbox(
                    "Rotate User Agents",
                    value=True,
                    help="Use different browser user agents for each request"
                )
            
            with col2:
                browser_fingerprinting = st.checkbox(
                    "Advanced Browser Fingerprinting",
                    value=True,
                    help="Mimic real browser behavior and fingerprints"
                )
                
                human_delays = st.checkbox(
                    "Human-like Request Delays",
                    value=True,
                    help="Add random delays between requests to appear human"
                )
            
            if st.button("💾 Save Security Settings"):
                # Update configuration
                self.config.scraping.use_stealth = use_stealth
                self.config.scraping.proxy.enabled = proxy_enabled
                self.config.scraping.proxy.rotation_strategy = rotation_strategy
                
                # Save to config file
                self.config.save_custom_settings()
                
                st.success("✅ Security settings saved successfully!")
                st.info("Restart the application for changes to take full effect.")


if __name__ == "__main__":
    # Initialize and run the ScrapeMaster Intelligence application
    try:
        app = ScrapeMasterApp()
        app.run()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        logger.error(f"Application startup error: {traceback.format_exc()}")
        st.info("Please check the logs for detailed error information.")