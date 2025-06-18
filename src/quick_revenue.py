"""
Quick Revenue Generator - Get to $1000 MRR Fast
Focus on what makes money, ignore everything else
"""

import streamlit as st
import requests
import os
from datetime import datetime
import json

# Simple configuration
SCRAPERAPI_KEY = os.getenv('SCRAPERAPI_KEY', '')

class QuickRevenueScraper:
    """Minimal viable scraper - just get it working"""
    
    def __init__(self):
        self.use_scraperapi = bool(SCRAPERAPI_KEY)
    
    def scrape(self, url, selector=None):
        """Dead simple scraping"""
        try:
            if self.use_scraperapi:
                # Use ScraperAPI for reliability
                api_url = f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={url}"
                response = requests.get(api_url, timeout=30)
            else:
                # Direct request as fallback
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                # Super basic extraction
                text = response.text
                
                # Look for common price patterns
                import re
                price_patterns = [
                    r'\$[\d,]+\.?\d*',  # $123.45
                    r'[\d,]+\.?\d*\s*USD',  # 123.45 USD
                    r'Price:\s*[\d,]+\.?\d*',  # Price: 123.45
                ]
                
                for pattern in price_patterns:
                    match = re.search(pattern, text)
                    if match:
                        return {
                            'price': match.group(),
                            'available': 'out of stock' not in text.lower(),
                            'raw_html': text[:1000]  # First 1000 chars
                        }
                
                return {'error': 'No price found', 'raw_html': text[:1000]}
            else:
                return {'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            return {'error': str(e)}


def main():
    """Revenue-focused UI"""
    st.set_page_config(
        page_title="ScrapeMaster Pro - Price Monitoring",
        page_icon="💰",
        layout="wide"
    )
    
    st.title("💰 ScrapeMaster Pro")
    st.subheader("Enterprise Price Monitoring That Pays For Itself")
    
    # Sidebar for client management
    with st.sidebar:
        st.header("💼 Quick Actions")
        
        if st.button("📞 Book Demo Call"):
            st.success("Calendly link: calendly.com/scrapemaster/demo")
        
        if st.button("💳 Send Invoice"):
            st.info("Stripe invoice link: invoice.stripe.com/...")
        
        st.markdown("---")
        st.metric("MRR", "$0", help="Update this manually for now")
        st.metric("Active Clients", "0")
        st.metric("Targets Monitored", "0")
    
    # Main revenue-generating features
    tab1, tab2, tab3 = st.tabs(["🎯 Monitor Prices", "📊 Client Dashboard", "💰 Billing"])
    
    with tab1:
        st.header("Add New Price Monitor")
        
        col1, col2 = st.columns(2)
        
        with col1:
            client_name = st.text_input("Client Name", placeholder="Amazon Seller LLC")
            target_url = st.text_input("URL to Monitor", placeholder="https://amazon.com/dp/B08...")
            check_frequency = st.selectbox("Check Frequency", ["Every Hour", "Every 6 Hours", "Daily"])
        
        with col2:
            client_email = st.text_input("Alert Email", placeholder="client@example.com")
            price_threshold = st.number_input("Alert if price drops below", min_value=0.0, value=100.0)
            
        if st.button("🚀 Start Monitoring", type="primary"):
            # Quick test scrape
            scraper = QuickRevenueScraper()
            with st.spinner("Testing URL..."):
                result = scraper.scrape(target_url)
            
            if 'error' not in result:
                st.success(f"✅ Successfully monitoring! Found price: {result.get('price', 'N/A')}")
                
                # Save to simple JSON database for now
                monitor_data = {
                    'client': client_name,
                    'email': client_email,
                    'url': target_url,
                    'frequency': check_frequency,
                    'threshold': price_threshold,
                    'last_result': result,
                    'created': datetime.now().isoformat()
                }
                
                # Append to monitors.json
                monitors = []
                if os.path.exists('monitors.json'):
                    with open('monitors.json', 'r') as f:
                        monitors = json.load(f)
                
                monitors.append(monitor_data)
                
                with open('monitors.json', 'w') as f:
                    json.dump(monitors, f, indent=2)
                
            else:
                st.error(f"❌ Scraping failed: {result['error']}")
                st.info("💡 Tip: Sign up for ScraperAPI to monitor any website reliably")
    
    with tab2:
        st.header("Client Dashboard")
        
        # Load monitors
        if os.path.exists('monitors.json'):
            with open('monitors.json', 'r') as f:
                monitors = json.load(f)
            
            for monitor in monitors:
                with st.expander(f"📦 {monitor['client']} - {monitor['url'][:50]}..."):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Email:** {monitor['email']}")
                        st.write(f"**Frequency:** {monitor['frequency']}")
                    
                    with col2:
                        st.write(f"**Threshold:** ${monitor['threshold']}")
                        st.write(f"**Last Price:** {monitor.get('last_result', {}).get('price', 'N/A')}")
                    
                    with col3:
                        if st.button("🔄 Check Now", key=f"check_{monitor['url']}"):
                            scraper = QuickRevenueScraper()
                            result = scraper.scrape(monitor['url'])
                            
                            if 'error' not in result:
                                st.success(f"Current price: {result.get('price', 'N/A')}")
                            else:
                                st.error(f"Check failed: {result['error']}")
        else:
            st.info("No monitors yet. Add your first client above!")
    
    with tab3:
        st.header("💰 Revenue Tracking")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Quick Invoice")
            invoice_client = st.text_input("Client", key="invoice_client")
            invoice_amount = st.number_input("Amount", min_value=0.0, value=199.0)
            
            if st.button("Generate Stripe Link"):
                # In production, use Stripe API
                st.code(f"https://buy.stripe.com/test_xxx?amount={invoice_amount}&client={invoice_client}")
        
        with col2:
            st.subheader("Pricing Calculator")
            num_urls = st.number_input("URLs to monitor", min_value=1, value=5)
            
            # Value-based pricing
            if num_urls <= 5:
                price = 199
            elif num_urls <= 15:
                price = 399
            else:
                price = 599
            
            st.metric("Recommended Price", f"${price}/month")
            st.caption("ROI: Client saves 10x this in prevented losses")
    
    # Footer with CTA
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; padding: 20px;'>
            <h3>Ready to scale?</h3>
            <p>Current special: $199/mo (normally $399)</p>
            <p>📧 Email: sales@scrapemaster.pro | 📞 Book a demo: calendly.com/scrapemaster</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main() 