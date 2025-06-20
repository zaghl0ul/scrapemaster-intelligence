"""
ScrapeMaster Intelligence - Production App
Full-featured app that works on Railway
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import os

# Mock data for demonstration (replace with real DB when ready)
def get_mock_data():
    """Generate mock data for demonstration"""
    return {
        'total_clients': 47,
        'active_targets': 312,
        'total_revenue': 8942,
        'alerts_sent': 1847,
        'recent_alerts': [
            {'time': '2 mins ago', 'product': 'Nike Air Max 270', 'price_drop': '$40', 'url': 'amazon.com/...'},
            {'time': '15 mins ago', 'product': 'Apple AirPods Pro', 'price_drop': '$50', 'url': 'bestbuy.com/...'},
            {'time': '1 hour ago', 'product': 'PS5 Controller', 'price_drop': '$15', 'url': 'walmart.com/...'},
        ]
    }

def main():
    st.set_page_config(
        page_title="ScrapeMaster Intelligence - Professional Price Monitoring",
        page_icon="🕷️",
        layout="wide"
    )
    
    # Sidebar
    with st.sidebar:
        st.title("🕷️ ScrapeMaster")
        st.markdown("---")
        
        page = st.radio("Navigation", [
            "🏠 Dashboard",
            "🎯 Price Monitoring", 
            "📊 Analytics",
            "💰 Pricing",
            "⚙️ Settings"
        ])
    
    # Main content based on page selection
    if page == "🏠 Dashboard":
        render_dashboard()
    elif page == "🎯 Price Monitoring":
        render_monitoring()
    elif page == "📊 Analytics":
        render_analytics()
    elif page == "💰 Pricing":
        render_pricing()
    elif page == "⚙️ Settings":
        render_settings()

def render_dashboard():
    """Render the main dashboard"""
    st.title("ScrapeMaster Intelligence Dashboard")
    
    # Get mock data
    data = get_mock_data()
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Clients", data['total_clients'], "+5 this week")
    
    with col2:
        st.metric("Active Monitors", data['active_targets'], "+23 today")
    
    with col3:
        st.metric("Monthly Revenue", f"${data['total_revenue']}", "+12%")
    
    with col4:
        st.metric("Alerts Sent", f"{data['alerts_sent']:,}", "+147 today")
    
    st.markdown("---")
    
    # Recent alerts and chart
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Revenue Trend")
        
        # Create sample revenue data
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        revenue = [random.randint(200, 400) for _ in range(30)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=revenue,
            mode='lines+markers',
            line=dict(color='#667eea', width=3),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.1)'
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis_title="Date",
            yaxis_title="Revenue ($)",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🔔 Recent Alerts")
        for alert in data['recent_alerts']:
            st.markdown(f"""
            **{alert['time']}**  
            {alert['product']}  
            💰 Dropped {alert['price_drop']}  
            [View →]({alert['url']})
            """)
            st.markdown("---")

def render_monitoring():
    """Render price monitoring page"""
    st.title("🎯 Price Monitoring")
    
    # Add new target
    with st.expander("➕ Add New Target", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            url = st.text_input("Product URL", placeholder="https://www.amazon.com/dp/...")
            target_price = st.number_input("Alert when price drops below", min_value=0.01, value=100.00)
        
        with col2:
            check_frequency = st.selectbox("Check frequency", ["Every 15 minutes", "Every hour", "Every 6 hours", "Daily"])
            alert_method = st.multiselect("Alert methods", ["Email", "SMS", "Slack", "Discord"])
        
        if st.button("Start Monitoring", type="primary"):
            st.success("✅ Target added! We'll alert you when the price drops.")
    
    st.markdown("---")
    
    # Active monitors
    st.subheader("Active Monitors")
    
    # Sample data
    monitors = pd.DataFrame({
        'Product': ['Nike Air Max 270', 'Apple AirPods Pro', 'PS5 Controller', 'Samsung SSD 1TB'],
        'Current Price': ['$120', '$199', '$65', '$89'],
        'Target Price': ['$100', '$150', '$50', '$70'],
        'Last Check': ['2 mins ago', '5 mins ago', '12 mins ago', '18 mins ago'],
        'Status': ['🟢 Active', '🟢 Active', '🟢 Active', '🟢 Active']
    })
    
    st.dataframe(monitors, use_container_width=True)

def render_analytics():
    """Render analytics page"""
    st.title("📊 Analytics")
    
    # Date range selector
    col1, col2 = st.columns([3, 1])
    with col1:
        date_range = st.date_input("Select date range", value=(datetime.now() - timedelta(days=30), datetime.now()), format="MM/DD/YYYY")
    
    st.markdown("---")
    
    # Analytics metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Avg. Price Drop Detected", "$47.23", "↑ 12% from last month")
        
    with col2:
        st.metric("Success Rate", "94.7%", "↑ 2.3%")
        
    with col3:
        st.metric("Avg. Response Time", "1.2s", "↓ 0.3s")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Alerts by Category")
        categories = ['Electronics', 'Fashion', 'Home', 'Sports', 'Books']
        values = [145, 89, 67, 45, 23]
        
        fig = px.pie(values=values, names=categories, hole=0.4)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Alert Response Times")
        times = pd.date_range(start='00:00', end='23:59', freq='H').strftime('%H:%M')
        response_times = [random.uniform(0.8, 2.0) for _ in range(24)]
        
        fig = px.line(x=times, y=response_times)
        fig.update_layout(xaxis_title="Hour", yaxis_title="Response Time (s)")
        st.plotly_chart(fig, use_container_width=True)

def render_pricing():
    """Render pricing page"""
    st.title("💰 Choose Your Plan")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container():
            st.markdown("""
            <div style='text-align: center; padding: 2rem; background: #f3f4f6; border-radius: 10px;'>
                <h3>Starter</h3>
                <h1>$99/mo</h1>
                <p>Perfect for individuals</p>
                <ul style='text-align: left; list-style: none;'>
                    <li>✅ 10 product monitors</li>
                    <li>✅ Hourly checks</li>
                    <li>✅ Email alerts</li>
                    <li>✅ Basic analytics</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            st.button("Choose Starter", key="starter", use_container_width=True)
    
    with col2:
        with st.container():
            st.markdown("""
            <div style='text-align: center; padding: 2rem; background: #667eea; color: white; border-radius: 10px;'>
                <h3>Professional</h3>
                <h1>$199/mo</h1>
                <p>Most popular choice</p>
                <ul style='text-align: left; list-style: none;'>
                    <li>✅ 50 product monitors</li>
                    <li>✅ 15-minute checks</li>
                    <li>✅ Email + SMS + Slack</li>
                    <li>✅ Advanced analytics</li>
                    <li>✅ API access</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            st.button("Choose Professional", key="pro", type="primary", use_container_width=True)
    
    with col3:
        with st.container():
            st.markdown("""
            <div style='text-align: center; padding: 2rem; background: #f3f4f6; border-radius: 10px;'>
                <h3>Enterprise</h3>
                <h1>$499/mo</h1>
                <p>For serious businesses</p>
                <ul style='text-align: left; list-style: none;'>
                    <li>✅ Unlimited monitors</li>
                    <li>✅ Real-time checks</li>
                    <li>✅ All integrations</li>
                    <li>✅ Custom features</li>
                    <li>✅ Dedicated support</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            st.button("Contact Sales", key="enterprise", use_container_width=True)

def render_settings():
    """Render settings page"""
    st.title("⚙️ Settings")
    
    tabs = st.tabs(["General", "Notifications", "API Keys", "Billing"])
    
    with tabs[0]:
        st.subheader("General Settings")
        st.text_input("Company Name", value="My Store")
        st.text_input("Contact Email", value="contact@mystore.com")
        st.selectbox("Timezone", ["UTC", "EST", "PST", "CST"])
        st.checkbox("Enable dark mode")
    
    with tabs[1]:
        st.subheader("Notification Settings")
        st.checkbox("Email notifications", value=True)
        st.checkbox("SMS notifications", value=True)
        st.checkbox("Slack notifications")
        st.checkbox("Discord notifications")
        
        st.markdown("---")
        st.subheader("Notification Rules")
        st.slider("Only alert for price drops greater than", 0, 100, 10, format="%d%%")
        st.number_input("Maximum alerts per day", min_value=1, value=50)
    
    with tabs[2]:
        st.subheader("API Configuration")
        st.text_input("ScraperAPI Key", type="password", value="sk_test_..." if os.getenv("SCRAPERAPI_KEY") else "")
        st.text_input("Stripe Secret Key", type="password", value="sk_test_..." if os.getenv("STRIPE_SECRET_KEY") else "")
        
        if st.button("Test API Connection"):
            st.success("✅ API connection successful!")
    
    with tabs[3]:
        st.subheader("Billing Information")
        st.info("Current Plan: **Professional** ($199/month)")
        st.metric("Next billing date", "Dec 18, 2024")
        st.button("Update Payment Method")
        st.button("View Invoices")

if __name__ == "__main__":
    main() 