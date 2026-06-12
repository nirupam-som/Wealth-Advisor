"""
Shared CSS styles and theme configuration for AI Wealth Advisor.
Provides consistent, premium dark-theme styling across all pages.
"""

# ── Color Palette ──────────────────────────────────────────────────────────────
COLORS = {
    "primary": "#6C63FF",
    "primary_light": "#8B83FF",
    "primary_dark": "#4B44CC",
    "accent": "#00D4AA",
    "accent_light": "#33DDBB",
    "warning": "#FFB347",
    "danger": "#FF6B6B",
    "background": "#0a0e27",
    "card": "#1a1a3e",
    "card_hover": "#242455",
    "text": "#E8E8FF",
    "text_muted": "#9999BB",
    "border": "rgba(108, 99, 255, 0.25)",
    "glass": "rgba(26, 26, 62, 0.65)",
    "glass_border": "rgba(108, 99, 255, 0.18)",
    "gradient_start": "#0a0e27",
    "gradient_end": "#1a1a3e",
    "success": "#00D4AA",
}

# ── Plotly Theme Config ────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color=COLORS["text"]),
    margin=dict(l=40, r=40, t=50, b=40),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(108,99,255,0.2)",
        borderwidth=1,
        font=dict(size=12),
    ),
)

PLOTLY_COLORS = [
    "#6C63FF", "#00D4AA", "#FFB347", "#FF6B6B",
    "#8B83FF", "#33DDBB", "#FFC977", "#FF9999",
    "#A89CFF", "#66E5CC", "#FFD9A0", "#FFBDBD",
]

# ── CSS Stylesheet ─────────────────────────────────────────────────────────────
GLOBAL_CSS = """
<style>
/* ── Google Fonts ───────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Root & Global Reset ────────────────────────────────────────── */
:root {
    --primary: #6C63FF;
    --primary-light: #8B83FF;
    --accent: #00D4AA;
    --warning: #FFB347;
    --danger: #FF6B6B;
    --bg: #0a0e27;
    --card: #1a1a3e;
    --text: #E8E8FF;
    --text-muted: #9999BB;
    --glass: rgba(26, 26, 62, 0.65);
    --glass-border: rgba(108, 99, 255, 0.18);
}

html, body, [data-testid="stAppViewContainer"], .main, [data-testid="stApp"] {
    background: linear-gradient(145deg, var(--bg) 0%, #111136 50%, var(--card) 100%) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── Sidebar ────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1233 0%, #161845 50%, #1c1e55 100%) !important;
    border-right: 1px solid var(--glass-border) !important;
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown li,
[data-testid="stSidebar"] .stMarkdown span,
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: var(--text) !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
    color: var(--text-muted) !important;
    font-weight: 500;
    transition: all 0.3s ease;
    border-radius: 8px;
    padding: 4px 8px;
}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
    color: var(--primary-light) !important;
    background: rgba(108, 99, 255, 0.08);
}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-selected="true"] {
    color: var(--primary) !important;
    background: rgba(108, 99, 255, 0.12);
}

/* ── Headers ────────────────────────────────────────────────────── */
h1, h2, h3 {
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
}
h1 {
    font-weight: 800 !important;
    letter-spacing: -0.03em;
}

/* ── Glassmorphism Card ─────────────────────────────────────────── */
.glass-card {
    background: var(--glass);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 24px;
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}
.glass-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--primary), var(--accent));
    border-radius: 16px 16px 0 0;
}
.glass-card:hover {
    border-color: rgba(108, 99, 255, 0.35);
    transform: translateY(-3px);
    box-shadow: 0 12px 40px rgba(108, 99, 255, 0.12);
}

/* ── Metric Cards ───────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--glass);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--glass-border);
    border-radius: 14px;
    padding: 20px 24px;
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}
[data-testid="stMetric"]:hover {
    border-color: rgba(108, 99, 255, 0.35);
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(108, 99, 255, 0.1);
}
[data-testid="stMetric"] label {
    color: var(--text-muted) !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    font-size: 0.75rem !important;
    letter-spacing: 0.08em;
}
[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-weight: 800 !important;
    font-size: 1.8rem !important;
    background: linear-gradient(135deg, var(--primary), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
[data-testid="stMetric"] [data-testid="stMetricDelta"] {
    font-weight: 600 !important;
}

/* ── Buttons ────────────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, var(--primary) 0%, #5a52e0 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 28px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    letter-spacing: 0.02em;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 15px rgba(108, 99, 255, 0.3);
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(108, 99, 255, 0.45) !important;
    background: linear-gradient(135deg, #7b73ff 0%, #6C63FF 100%) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Dataframes & Tables ────────────────────────────────────────── */
[data-testid="stDataFrame"], .stDataFrame {
    border-radius: 12px !important;
    overflow: hidden;
    border: 1px solid var(--glass-border) !important;
}

/* ── Tabs ───────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: transparent;
    border-bottom: 1px solid var(--glass-border);
    padding-bottom: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    border-radius: 10px 10px 0 0 !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    border: 1px solid transparent !important;
    border-bottom: none !important;
    transition: all 0.3s ease;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--primary-light) !important;
    background: rgba(108, 99, 255, 0.06) !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: var(--primary) !important;
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    border-bottom: 2px solid var(--primary) !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    background-color: var(--primary) !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 20px;
}

/* ── Inputs ─────────────────────────────────────────────────────── */
.stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox select,
[data-baseweb="input"] input, [data-baseweb="select"] {
    background: var(--glass) !important;
    color: var(--text) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.3s ease;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(108, 99, 255, 0.15) !important;
}

/* ── File Uploader ──────────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: var(--glass) !important;
    border: 2px dashed var(--glass-border) !important;
    border-radius: 16px !important;
    padding: 20px !important;
    transition: all 0.3s ease;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--primary) !important;
    background: rgba(108, 99, 255, 0.05) !important;
}

/* ── Chat Messages ──────────────────────────────────────────────── */
[data-testid="stChatMessage"] {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 14px !important;
    padding: 16px 20px !important;
    margin-bottom: 12px;
    backdrop-filter: blur(12px);
    transition: all 0.3s ease;
}
[data-testid="stChatMessage"]:hover {
    border-color: rgba(108, 99, 255, 0.3) !important;
}

/* ── Chat Input ─────────────────────────────────────────────────── */
[data-testid="stChatInput"] textarea {
    background: var(--glass) !important;
    color: var(--text) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── Progress Bars ──────────────────────────────────────────────── */
.stProgress > div > div {
    background: linear-gradient(90deg, var(--primary), var(--accent)) !important;
    border-radius: 10px;
}
.stProgress > div {
    background: rgba(108, 99, 255, 0.12) !important;
    border-radius: 10px;
}

/* ── Expanders ──────────────────────────────────────────────────── */
.streamlit-expanderHeader {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-weight: 600 !important;
}

/* ── Alert / Info boxes ─────────────────────────────────────────── */
[data-testid="stAlert"] {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
}

/* ── Spinner ────────────────────────────────────────────────────── */
.stSpinner > div {
    border-top-color: var(--primary) !important;
}

/* ── Scrollbar ──────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(108, 99, 255, 0.3);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(108, 99, 255, 0.5); }

/* ── Custom utility classes ─────────────────────────────────────── */
.gradient-text {
    background: linear-gradient(135deg, #6C63FF, #00D4AA);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-title {
    font-size: 3.5rem;
    font-weight: 900;
    line-height: 1.1;
    margin-bottom: 0.5rem;
    background: linear-gradient(135deg, #FFFFFF 0%, #6C63FF 50%, #00D4AA 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shimmer 3s ease-in-out infinite alternate;
}
@keyframes shimmer {
    0%   { background-position: 0% 50%; }
    100% { background-position: 100% 50%; }
}
.hero-subtitle {
    font-size: 1.35rem;
    color: var(--text-muted);
    font-weight: 400;
    margin-top: 0;
}
.badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.badge-primary  { background: rgba(108,99,255,0.18); color: #8B83FF; }
.badge-accent   { background: rgba(0,212,170,0.18); color: #00D4AA; }
.badge-warning  { background: rgba(255,179,71,0.18); color: #FFB347; }
.badge-danger   { background: rgba(255,107,107,0.18); color: #FF6B6B; }

.feature-icon {
    font-size: 2.5rem;
    margin-bottom: 12px;
    display: block;
}

.divider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--glass-border), transparent);
    margin: 32px 0;
}

/* ── Fade-in animation ──────────────────────────────────────────── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
.fade-in {
    animation: fadeInUp 0.6s ease-out forwards;
}
.fade-in-delay-1 { animation-delay: 0.1s; }
.fade-in-delay-2 { animation-delay: 0.2s; }
.fade-in-delay-3 { animation-delay: 0.3s; }
.fade-in-delay-4 { animation-delay: 0.4s; }

/* ── Pulse glow for live indicators ─────────────────────────────── */
@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(0,212,170,0.4); }
    50%      { box-shadow: 0 0 0 8px rgba(0,212,170,0); }
}
.pulse-dot {
    width: 10px; height: 10px;
    background: var(--accent);
    border-radius: 50%;
    display: inline-block;
    animation: pulse 2s infinite;
    margin-right: 6px;
    vertical-align: middle;
}
</style>
"""


def inject_css():
    """Inject the global CSS into the current Streamlit page."""
    import streamlit as st
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def page_header(title: str, description: str = "", icon: str = ""):
    """Render a consistent page header with icon, title and description."""
    import streamlit as st
    inject_css()
    header_html = f"""
    <div style="margin-bottom:28px;">
        <h1 style="margin-bottom:4px;">{icon} {title}</h1>
        <p style="color:var(--text-muted);font-size:1.05rem;margin-top:0;">{description}</p>
        <div class="divider"></div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)


def glass_card(content_html: str, extra_style: str = ""):
    """Wrap arbitrary HTML in a glassmorphism card."""
    import streamlit as st
    st.markdown(
        f'<div class="glass-card" style="{extra_style}">{content_html}</div>',
        unsafe_allow_html=True,
    )


def api_url(path: str) -> str:
    """Return the full backend API URL for a given path."""
    base = "http://localhost:8000"
    path = path.lstrip("/")
    return f"{base}/{path}"
