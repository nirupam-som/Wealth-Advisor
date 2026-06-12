import streamlit as st
import httpx
import sys
import os
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, page_header, glass_card, api_url, PLOTLY_LAYOUT, COLORS

st.set_page_config(page_title="AI Insights | Wealth Advisor", page_icon="💡", layout="wide")
inject_css()

page_header("AI Insights", "Personalized financial analysis and recommendations.", "💡")

# Ensure user_id is set (default to 1 for demo)
user_id = 1

tab1, tab2, tab3 = st.tabs(["📊 Spending Insights", "💰 Savings Advice", "📈 Risk Analysis"])

with tab1:
    st.markdown("### Spending Analysis")
    with st.spinner("Analyzing your spending patterns..."):
        try:
            with httpx.Client(timeout=30) as client:
                resp = client.get(api_url("insights/spending"), params={"user_id": user_id})
                if resp.status_code == 200:
                    data = resp.json()
                    insights_text = data.get("content", "No insights available.")
                    
                    # Split into paragraphs and display in cards
                    paragraphs = [p.strip() for p in insights_text.split('\n\n') if p.strip()]
                    for i, p in enumerate(paragraphs):
                        glass_card(f"<div style='font-size:1.05rem;line-height:1.6;'>{p}</div>", extra_style="margin-bottom:16px;")
                else:
                    st.error("Failed to load spending insights. Please ensure you have uploaded a statement.")
        except httpx.RequestError:
            st.error("Backend server is unreachable.")

with tab2:
    st.markdown("### Savings Recommendations")
    with st.spinner("Generating personalized savings advice..."):
        try:
            with httpx.Client(timeout=30) as client:
                resp = client.get(api_url("insights/savings"), params={"user_id": user_id})
                if resp.status_code == 200:
                    data = resp.json()
                    advice_text = data.get("content", "No advice available.")
                    
                    paragraphs = [p.strip() for p in advice_text.split('\n\n') if p.strip()]
                    for i, p in enumerate(paragraphs):
                        glass_card(f"<div style='font-size:1.05rem;line-height:1.6;'>{p}</div>", extra_style="margin-bottom:16px;")
                else:
                    st.error("Failed to load savings advice.")
        except httpx.RequestError:
            st.error("Backend server is unreachable.")

with tab3:
    st.markdown("### Portfolio Risk Profile")
    with st.spinner("Calculating risk score..."):
        try:
            with httpx.Client(timeout=30) as client:
                resp = client.get(api_url("insights/risk-score"), params={"user_id": user_id})
                if resp.status_code == 200:
                    data = resp.json()
                    meta = data.get("metadata", {})
                    score = meta.get("risk_score", 0) * 10  # Scale 0-10 to 0-100 for gauge
                    explanation = data.get("content", "")
                    allocation = meta.get("asset_allocation", {})
                    
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        # Risk Gauge Chart
                        fig = go.Figure(go.Indicator(
                            mode = "gauge+number",
                            value = score,
                            domain = {'x': [0, 1], 'y': [0, 1]},
                            title = {'text': "Risk Score", 'font': {'size': 24, 'color': COLORS['text']}},
                            gauge = {
                                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': COLORS['text_muted']},
                                'bar': {'color': COLORS['primary']},
                                'bgcolor': "rgba(0,0,0,0)",
                                'borderwidth': 0,
                                'steps': [
                                    {'range': [0, 33], 'color': "rgba(0, 212, 170, 0.3)"},
                                    {'range': [33, 66], 'color': "rgba(255, 179, 71, 0.3)"},
                                    {'range': [66, 100], 'color': "rgba(255, 107, 107, 0.3)"}],
                            }
                        ))
                        fig.update_layout(**PLOTLY_LAYOUT, height=300)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        glass_card(
                            f"<h4 style='color:{COLORS['primary']};margin-top:0;'>Risk Assessment</h4>"
                            f"<p style='font-size:1.05rem;line-height:1.6;'>{explanation}</p>"
                        )
                        
                    if allocation:
                        st.markdown("#### Current Allocation")
                        labels = list(allocation.keys())
                        values = list(allocation.values())
                        fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4, marker=dict(colors=[COLORS['primary'], COLORS['accent'], COLORS['warning'], COLORS['danger']]))])
                        fig_pie.update_layout(**PLOTLY_LAYOUT, height=400)
                        st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.error("Failed to load risk analysis.")
        except httpx.RequestError:
            st.error("Backend server is unreachable.")
