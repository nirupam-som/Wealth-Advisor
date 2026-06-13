"""
AI Wealth Advisor – Main Entry Point
=====================================
Home page with hero section, key financial metrics, and feature overview.
"""

import streamlit as st

st.set_page_config(
    page_title="AI Wealth Advisor",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Imports after page config ──────────────────────────────────────────────────
import httpx
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from utils.styles import inject_css, GLOBAL_CSS, COLORS, api_url

inject_css()

if "welcomed" not in st.session_state:
    st.toast("Welcome to your AI Financial Copilot! 💰", icon="🚀")
    st.session_state.welcomed = True

# ── Sidebar branding ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center;padding:20px 0 10px;">
            <div style="font-size:2.8rem;margin-bottom:4px;">💰</div>
            <h2 style="margin:0;font-size:1.3rem;
                background:linear-gradient(135deg,#6C63FF,#00D4AA);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                background-clip:text;">AI Wealth Advisor</h2>
            <p style="color:#9999BB;font-size:0.8rem;margin-top:4px;">v1.0 · Premium</p>
        </div>
        <hr style="border:none;height:1px;
            background:linear-gradient(90deg,transparent,rgba(108,99,255,0.25),transparent);
            margin:8px 0 16px;">
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div style="position:fixed;bottom:20px;left:20px;right:20px;max-width:240px;">
            <p style="color:#9999BB;font-size:0.7rem;text-align:center;">
                Built with ❤️ using Streamlit + FastAPI
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Fetch live data (graceful fallback) ───────────────────────────────────────
balance = "₹1,24,850"
spending = "₹3,420"
savings_rate = "28%"
risk_score = "72"
backend_online = False

try:
    with httpx.Client(timeout=4) as client:
        resp = client.get(api_url("transactions/summary"))
        if resp.status_code == 200:
            data = resp.json()
            total_income = data.get("total_income", 0)
            total_expenses = data.get("total_expenses", 0)
            net = total_income - total_expenses
            rate = (net / total_income * 100) if total_income else 0
            balance = f"₹{net:,.0f}"
            spending = f"₹{total_expenses:,.0f}"
            savings_rate = f"{rate:.0f}%"
            backend_online = True
        # risk score
        resp2 = client.get(api_url("insights/risk-score"))
        if resp2.status_code == 200:
            risk_data = resp2.json()
            risk_score = str(risk_data.get("score", risk_score))
            backend_online = True
except Exception:
    pass

# ── Hero Section ──────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="text-align:center;padding:50px 0 30px;">
        <div class="fade-in">
            <div style="font-size:4rem;margin-bottom:8px;">💰</div>
            <h1 class="hero-title">AI Wealth Advisor</h1>
            <p class="hero-subtitle">Your AI-Powered Financial Copilot</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Status indicator ─────────────────────────────────────────────────────────
status_color = "#00D4AA" if backend_online else "#FF6B6B"
status_text = "Backend Connected" if backend_online else "Backend Offline – showing demo data"
st.markdown(
    f"""
    <div style="text-align:center;margin-bottom:32px;" class="fade-in fade-in-delay-1">
        <span class="pulse-dot" style="background:{status_color};"></span>
        <span style="color:{status_color};font-size:0.85rem;font-weight:600;">{status_text}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Key Metrics Row ──────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Total Balance", value=balance, delta="+4.2% this month")
with col2:
    st.metric(label="Monthly Spending", value=spending, delta="-12% vs last month", delta_color="inverse")
with col3:
    st.metric(label="Savings Rate", value=savings_rate, delta="+3pp")
with col4:
    st.metric(label="Risk Score", value=f"{risk_score}/100", delta="Moderate")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Feature Cards ────────────────────────────────────────────────────────────
st.markdown(
    "<h2 style='text-align:center;margin-bottom:8px;'>Everything You Need</h2>"
    "<p style='text-align:center;color:#9999BB;margin-bottom:32px;'>Powerful tools to master your finances</p>",
    unsafe_allow_html=True,
)

features = [
    {
        "icon": "📊",
        "title": "Smart Dashboard",
        "desc": "Visualize income, expenses, and trends with interactive charts powered by AI categorization.",
        "color": "#6C63FF",
    },
    {
        "icon": "📤",
        "title": "Easy Upload",
        "desc": "Import bank statements in CSV format. Transactions are auto-categorized instantly.",
        "color": "#00D4AA",
    },
    {
        "icon": "🎯",
        "title": "Goal Tracking",
        "desc": "Set savings goals, track progress, and get AI-powered recommendations to hit your targets.",
        "color": "#FFB347",
    },
    {
        "icon": "💡",
        "title": "AI Insights",
        "desc": "Get personalised spending analysis, savings tips, and risk assessment from advanced AI models.",
        "color": "#FF6B6B",
    },
    {
        "icon": "💬",
        "title": "Financial Chat",
        "desc": "Ask questions in plain English. Your AI advisor understands your complete financial picture.",
        "color": "#8B83FF",
    },
    {
        "icon": "🔒",
        "title": "Privacy First",
        "desc": "Your data stays local. No third-party access. Enterprise-grade encryption at rest.",
        "color": "#33DDBB",
    },
]

cols = st.columns(3)
for idx, feat in enumerate(features):
    with cols[idx % 3]:
        st.markdown(
            f"""
            <div class="glass-card fade-in fade-in-delay-{idx % 4 + 1}" style="margin-bottom:20px;min-height:210px;">
                <span class="feature-icon">{feat['icon']}</span>
                <h3 style="margin:0 0 8px;font-size:1.15rem;color:{feat['color']};">{feat['title']}</h3>
                <p style="color:#9999BB;font-size:0.92rem;line-height:1.55;margin:0;">{feat['desc']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Quick Start CTA ─────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="text-align:center;padding:20px 0 40px;" class="fade-in fade-in-delay-3">
        <h2 style="margin-bottom:8px;">Ready to take control?</h2>
        <p style="color:#9999BB;margin-bottom:24px;">Upload your first bank statement to get started.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
c1, c2, c3 = st.columns([1, 1, 1])
with c2:
    if st.button("🚀  Get Started — Upload Statement", use_container_width=True):
        st.switch_page("pages/2_📤_Upload.py")
