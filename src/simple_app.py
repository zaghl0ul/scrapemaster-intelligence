"""
Simple ScrapeMaster Landing Page - Minimal version for Railway
"""
import streamlit as st

def main():
    st.set_page_config(
        page_title="ScrapeMaster Intelligence - Price Monitoring Service",
        page_icon="🕷️",
        layout="wide"
    )
    
    # Header
    st.title("🕷️ ScrapeMaster Intelligence")
    st.subheader("Price Drop Alerts That Make You Money")
    
    # Main content
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 💰 Make Money
        Our users profit $500-$5,000/month from price arbitrage
        """)
    
    with col2:
        st.markdown("""
        ### ⚡ Quick Setup
        Add any URL. We monitor 24/7. Get instant alerts.
        """)
    
    with col3:
        st.markdown("""
        ### 🎯 100% Accurate
        Advanced scraping works on any website
        """)
    
    st.markdown("---")
    
    # Pricing
    st.header("💸 Simple Pricing")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### Starter
        **$99/month**
        - 10 products
        - Hourly checks
        - Email alerts
        """)
        st.button("Get Started", key="starter")
    
    with col2:
        st.markdown("""
        ### Professional 🔥
        **$199/month**
        - 50 products
        - 15-min checks
        - SMS + Slack alerts
        - API access
        """)
        st.button("Get Started", key="pro")
    
    with col3:
        st.markdown("""
        ### Enterprise
        **$499/month**
        - Unlimited products
        - Real-time monitoring
        - Custom integrations
        """)
        st.button("Get Started", key="enterprise")
    
    st.markdown("---")
    
    # Contact
    st.markdown("""
    ### 📧 Ready to start?
    Contact us at **support@scrapemaster.ai** or sign up above!
    
    *Average user makes $2,000+/month from our alerts*
    """)

if __name__ == "__main__":
    main() 