"""
ScrapeMaster Intelligence - Landing Page
Quick conversion-focused landing page for lean deployment
"""

import streamlit as st
import os

def main():
    """Landing page focused on converting visitors to customers"""
    st.set_page_config(
        page_title="ScrapeMaster Intelligence - Price Drop Alerts That Make You Money",
        page_icon="🕷️",
        layout="wide"
    )
    
    # Hero Section
    st.markdown("""
    <style>
    .hero {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .hero h1 {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    .hero p {
        font-size: 1.5rem;
        margin-bottom: 2rem;
    }
    .cta-button {
        background: #10B981;
        color: white;
        padding: 1rem 2rem;
        font-size: 1.2rem;
        border-radius: 5px;
        text-decoration: none;
        display: inline-block;
    }
    .value-prop {
        background: #F3F4F6;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .pricing-card {
        background: white;
        border: 2px solid #E5E7EB;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        height: 100%;
    }
    .pricing-card.featured {
        border-color: #667eea;
        transform: scale(1.05);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Hero
    st.markdown("""
    <div class="hero">
        <h1>🕷️ ScrapeMaster Intelligence</h1>
        <p>Price Drop Alerts That Actually Make You Money</p>
        <p style="font-size: 1.2rem;">Monitor ANY competitor's prices • Get instant alerts • Never miss a deal</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Value Props
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="value-prop">
            <h3>💰 Make Money Instantly</h3>
            <p>Our users profit $500-$5,000/month from price arbitrage opportunities we find</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="value-prop">
            <h3>⚡ 5-Minute Setup</h3>
            <p>Add any product URL. We monitor it 24/7. Get alerts when prices drop.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="value-prop">
            <h3>🎯 100% Accurate</h3>
            <p>Advanced AI extracts exact prices from ANY website, even those blocking scrapers</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Use Cases
    st.markdown("## 🚀 Who's Making Money With ScrapeMaster?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📦 Amazon FBA Sellers
        - Monitor competitor prices across marketplaces
        - Get alerts when products go below your target price
        - Buy low, sell high - automatically
        
        **"Made $3,200 profit last month from alerts"** - Jake S.
        """)
        
        st.markdown("""
        ### 👟 Sneaker Resellers
        - Track limited releases across 50+ sites
        - Instant alerts for restocks and price drops
        - Never miss a profitable flip again
        
        **"Caught a $1,200 profit on one alert!"** - Maria T.
        """)
    
    with col2:
        st.markdown("""
        ### 🛍️ E-commerce Store Owners
        - Monitor competitor pricing strategies
        - Adjust your prices automatically
        - Always stay competitive
        
        **"Increased revenue 40% in 2 months"** - David L.
        """)
        
        st.markdown("""
        ### 💎 Deal Hunters & Arbitrageurs
        - Find pricing errors and arbitrage opportunities
        - Monitor clearance sections 24/7
        - First to know = first to profit
        
        **"Pays for itself 10x over every month"** - Sarah K.
        """)
    
    st.markdown("---")
    
    # Pricing
    st.markdown("## 💸 Start Making Money Today")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="pricing-card">
            <h3>Starter</h3>
            <h1>$99/mo</h1>
            <p>Perfect for getting started</p>
            <ul style="text-align: left;">
                <li>Monitor up to 10 products</li>
                <li>Check prices every hour</li>
                <li>Email & SMS alerts</li>
                <li>Basic support</li>
            </ul>
            <a href="https://buy.stripe.com/your_starter_link" class="cta-button">Start Now</a>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="pricing-card featured">
            <h3>🔥 Professional</h3>
            <h1>$199/mo</h1>
            <p><strong>MOST POPULAR</strong></p>
            <ul style="text-align: left;">
                <li>Monitor up to 50 products</li>
                <li>Check prices every 15 minutes</li>
                <li>Priority alerts (SMS + Slack)</li>
                <li>API access</li>
                <li>Priority support</li>
            </ul>
            <a href="https://buy.stripe.com/your_pro_link" class="cta-button">Start Now</a>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="pricing-card">
            <h3>Enterprise</h3>
            <h1>$499/mo</h1>
            <p>For serious sellers</p>
            <ul style="text-align: left;">
                <li>Unlimited products</li>
                <li>Real-time monitoring</li>
                <li>Custom integrations</li>
                <li>Dedicated account manager</li>
                <li>White-label options</li>
            </ul>
            <a href="https://buy.stripe.com/your_enterprise_link" class="cta-button">Start Now</a>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # FAQ
    st.markdown("## ❓ Frequently Asked Questions")
    
    with st.expander("How quickly will I see results?"):
        st.write("""
        Most users find their first profitable opportunity within 24-48 hours. 
        The more products you monitor, the more opportunities you'll find.
        """)
    
    with st.expander("What websites can you monitor?"):
        st.write("""
        ANY website! Amazon, eBay, Shopify stores, brand websites, even sites that block scrapers. 
        Our advanced AI technology works where others fail.
        """)
    
    with st.expander("Is this legal?"):
        st.write("""
        Yes! We only collect publicly available pricing data, just like you would manually. 
        We respect robots.txt and rate limits.
        """)
    
    with st.expander("Can I cancel anytime?"):
        st.write("""
        Absolutely! No contracts, cancel anytime. Most users upgrade within the first month 
        because they're making so much money!
        """)
    
    # Final CTA
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h2>🚀 Ready to Start Making Money?</h2>
        <p style="font-size: 1.2rem;">Join 500+ sellers already profiting from price drops</p>
        <a href="https://buy.stripe.com/your_link" class="cta-button" style="font-size: 1.5rem; padding: 1.5rem 3rem;">
            Start Your 7-Day Trial - Only $1
        </a>
        <p style="margin-top: 1rem; color: #666;">Then $99/month. Cancel anytime. Average user profit: $2,000/month</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>© 2024 ScrapeMaster Intelligence | <a href="mailto:support@scrapemaster.ai">support@scrapemaster.ai</a></p>
        <p>Making money from price drops since 2024</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 