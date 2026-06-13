import streamlit as st
import httpx
import sys
import os
import re
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.styles import inject_css, page_header, glass_card, api_url, PLOTLY_LAYOUT, COLORS

st.set_page_config(page_title="AI Insights | Wealth Advisor", page_icon="💡", layout="wide")
inject_css()

page_header("AI Insights", "Personalized financial analysis and recommendations.", "💡")

# Ensure user_id is set (default to 1 for demo)
user_id = 1


def render_insight_cards(text: str):
    """Parse LLM markdown output into nicely formatted glass cards.

    Splits on bullet points (lines starting with - or * or numbered lists)
    and renders each as a separate glass card with proper markdown.
    """
    if not text or text.strip() == "":
        st.info("No insights available.")
        return

    # Split into individual insight bullets/paragraphs
    lines = text.strip().split("\n")
    cards = []
    current_card = []

    for line in lines:
        stripped = line.strip()
        # Detect new bullet/insight start
        if re.match(r"^[-*•]\s+|^\d+[\.\)]\s+", stripped):
            if current_card:
                cards.append("\n".join(current_card))
            current_card = [stripped]
        elif stripped == "":
            if current_card:
                cards.append("\n".join(current_card))
                current_card = []
        else:
            current_card.append(stripped)

    if current_card:
        cards.append("\n".join(current_card))

    # Render each card
    for card_text in cards:
        # Clean up bullet prefix for display
        clean = re.sub(r"^[-*•]\s+", "", card_text.strip())
        clean = re.sub(r"^\d+[\.\)]\s+", "", clean)

        if clean:
            with st.container():
                st.markdown(
                    f"""<div class="glass-card" style="margin-bottom:16px;">
                        <div style="font-size:1.05rem;line-height:1.7;">
                        </div>
                    </div>""",
                    unsafe_allow_html=True,
                )
                # Use st.markdown for proper markdown rendering
                st.markdown(clean)


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

                    # Use st.markdown directly so markdown formatting works
                    st.markdown(insights_text)
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

                    # Use st.markdown directly so markdown formatting works
                    st.markdown(advice_text)
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
                    risk_level = meta.get("risk_level", "N/A")
                    score = meta.get("risk_score", 0) * 10  # Scale 0-10 to 0-100 for gauge
                    explanation = data.get("content", "")
                    allocation = meta.get("asset_allocation", {})

                    # Show empty state if no portfolio
                    if risk_level == "N/A" and score == 0:
                        st.markdown(
                            """
                            <div class="glass-card" style="text-align:center;padding:60px 40px;">
                                <div style="font-size:4rem;margin-bottom:16px;">📈</div>
                                <h2 style="margin-bottom:8px;">No Portfolio Data</h2>
                                <p style="color:#9999BB;max-width:480px;margin:0 auto 24px;">
                                    Add portfolio holdings to get your personalized risk assessment,
                                    asset allocation analysis, and AI-powered recommendations.
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    else:
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            # Risk Gauge Chart
                            fig = go.Figure(go.Indicator(
                                mode="gauge+number",
                                value=score,
                                domain={'x': [0, 1], 'y': [0, 1]},
                                title={'text': "Risk Score", 'font': {'size': 24, 'color': COLORS['text']}},
                                gauge={
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
                            # Risk level badge
                            level_colors = {
                                "Conservative": COLORS["accent"],
                                "Moderate": COLORS["warning"],
                                "Aggressive": COLORS["danger"],
                                "Very Aggressive": COLORS["danger"],
                            }
                            level_color = level_colors.get(risk_level, COLORS["primary"])

                            glass_card(
                                f"<h4 style='color:{COLORS['primary']};margin-top:0;'>Risk Assessment</h4>"
                                f"<div style='margin-bottom:12px;'>"
                                f"<span class='badge' style='background:rgba({','.join(str(int(level_color.lstrip('#')[i:i+2], 16)) for i in (0,2,4))},0.18);"
                                f"color:{level_color};font-size:0.9rem;padding:6px 18px;'>"
                                f"{risk_level}</span></div>"
                                f"<p style='font-size:1.05rem;line-height:1.6;'>{explanation}</p>"
                            )

                        if allocation:
                            st.markdown("#### Current Allocation")
                            labels = list(allocation.keys())
                            values = list(allocation.values())
                            fig_pie = go.Figure(data=[go.Pie(
                                labels=labels, values=values, hole=.4,
                                marker=dict(colors=[COLORS['primary'], COLORS['accent'], COLORS['warning'], COLORS['danger']])
                            )])
                            fig_pie.update_layout(**PLOTLY_LAYOUT, height=400)
                            st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.error("Failed to load risk analysis.")
        except httpx.RequestError:
            st.error("Backend server is unreachable.")
