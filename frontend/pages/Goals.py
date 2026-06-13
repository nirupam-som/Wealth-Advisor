"""
🎯 Goals – Goal-Based Financial Planning
==========================================
Create, track, edit, and delete savings goals with visual
progress cards and priority badges.
"""

import streamlit as st
import httpx
import sys, os
from datetime import date, datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.styles import inject_css, page_header, glass_card, api_url, COLORS

page_header(
    "Goal Planner",
    "Set savings targets, track your progress, and crush your financial goals",
    "🎯",
)

# ── Priority helpers ─────────────────────────────────────────────────────────
PRIORITY_CONFIG = {
    "high":   {"color": COLORS["danger"],  "badge": "badge-danger",  "icon": "🔴"},
    "medium": {"color": COLORS["warning"], "badge": "badge-warning", "icon": "🟡"},
    "low":    {"color": COLORS["accent"],  "badge": "badge-accent",  "icon": "🟢"},
}

# ── Create New Goal Form ────────────────────────────────────────────────────
with st.expander("➕  Create New Goal", expanded=False):
    with st.form("new_goal_form", clear_on_submit=True):
        st.markdown("##### Define your new savings goal")
        g_col1, g_col2 = st.columns(2)
        with g_col1:
            goal_name = st.text_input("Goal Name", placeholder="e.g. Emergency Fund")
            target_amount = st.number_input("Target Amount (₹)", min_value=1.0, value=5000.0, step=100.0)
        with g_col2:
            deadline = st.date_input("Target Date", value=date(2027, 1, 1), min_value=date.today())
            priority = st.selectbox("Priority", ["high", "medium", "low"], index=1)

        submitted = st.form_submit_button("🎯  Create Goal", use_container_width=True, type="primary")

        if submitted:
            if not goal_name.strip():
                st.warning("Please enter a goal name.")
            else:
                payload = {
                    "name": goal_name.strip(),
                    "target_amount": target_amount,
                    "deadline": deadline.isoformat(),
                    "priority": priority,
                }
                try:
                    with httpx.Client(timeout=10) as client:
                        resp = client.post(api_url("goals/"), json=payload)
                    if resp.status_code in (200, 201):
                        st.success(f"✅ Goal **{goal_name}** created successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed to create goal (HTTP {resp.status_code}): {resp.text}")
                except httpx.ConnectError:
                    st.error("❌ Backend not available. Start the server on `localhost:8000`.")
                except Exception as e:
                    st.error(f"Error: {e}")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Fetch existing goals ────────────────────────────────────────────────────
goals = []
try:
    with httpx.Client(timeout=5) as client:
        resp = client.get(api_url("goals/"))
        if resp.status_code == 200:
            data = resp.json()
            goals = data if isinstance(data, list) else data.get("goals", [])
except httpx.ConnectError:
    st.warning("⚠️ Cannot reach the backend. Goals will appear here once the server is running.")
except Exception as e:
    st.error(f"Error loading goals: {e}")

# ── Display Goals ────────────────────────────────────────────────────────────
if not goals:
    st.markdown(
        """
        <div class="glass-card" style="text-align:center;padding:60px 40px;">
            <div style="font-size:4rem;margin-bottom:16px;">🎯</div>
            <h2 style="margin-bottom:8px;">No Goals Yet</h2>
            <p style="color:#9999BB;max-width:420px;margin:0 auto;">
                Create your first savings goal above to start tracking your progress toward financial freedom.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

st.markdown(f"#### Your Goals ({len(goals)})")

# Render goals in 2-column grid
cols = st.columns(2)
for idx, goal in enumerate(goals):
    goal_id = goal.get("id", idx)
    name = goal.get("name", "Unnamed Goal")
    target = goal.get("target_amount", 0)
    current = goal.get("current_amount", 0)
    priority = goal.get("priority", "medium").lower()
    deadline_str = goal.get("deadline", "")
    pcfg = PRIORITY_CONFIG.get(priority, PRIORITY_CONFIG["medium"])

    # Progress calculation
    progress = min((current / target * 100) if target > 0 else 0, 100)
    progress_frac = progress / 100.0

    # Days remaining
    days_remaining = "—"
    if deadline_str:
        try:
            dl = datetime.fromisoformat(deadline_str.replace("Z", "+00:00")).date() if "T" in deadline_str else date.fromisoformat(deadline_str)
            diff = (dl - date.today()).days
            days_remaining = f"{diff} days" if diff > 0 else ("Today!" if diff == 0 else "Overdue")
        except Exception:
            pass

    # Gradient based on progress
    if progress >= 80:
        bar_gradient = f"linear-gradient(90deg, {COLORS['accent']}, #66E5CC)"
    elif progress >= 40:
        bar_gradient = f"linear-gradient(90deg, {COLORS['primary']}, {COLORS['accent']})"
    else:
        bar_gradient = f"linear-gradient(90deg, {COLORS['warning']}, {COLORS['primary']})"

    with cols[idx % 2]:
        st.markdown(
            f"""
            <div class="glass-card" style="margin-bottom:20px;min-height:200px;">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px;">
                    <div>
                        <h3 style="margin:0;font-size:1.15rem;">{name}</h3>
                        <p style="margin:4px 0 0;color:#9999BB;font-size:0.82rem;">⏰ {days_remaining} remaining</p>
                    </div>
                    <span class="badge {pcfg['badge']}">{pcfg['icon']} {priority}</span>
                </div>

                <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
                    <span style="color:#9999BB;font-size:0.82rem;">Progress</span>
                    <span style="font-weight:700;font-size:0.9rem;color:{COLORS['text']};">{progress:.1f}%</span>
                </div>

                <!-- Progress bar -->
                <div style="background:rgba(108,99,255,0.12);border-radius:10px;height:12px;overflow:hidden;margin-bottom:16px;">
                    <div style="width:{progress}%;height:100%;background:{bar_gradient};border-radius:10px;
                        transition:width 0.6s cubic-bezier(0.4,0,0.2,1);"></div>
                </div>

                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <span style="color:#9999BB;font-size:0.78rem;">Current</span>
                        <p style="margin:0;font-weight:700;color:{COLORS['accent']};">₹{current:,.2f}</p>
                    </div>
                    <div style="text-align:right;">
                        <span style="color:#9999BB;font-size:0.78rem;">Target</span>
                        <p style="margin:0;font-weight:700;color:{COLORS['text']};">₹{target:,.2f}</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Action buttons row
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button(f"✏️ Edit", key=f"edit_{goal_id}"):
                st.session_state[f"editing_{goal_id}"] = True
        with btn_col2:
            if st.button(f"🗑️ Delete", key=f"del_{goal_id}"):
                try:
                    with httpx.Client(timeout=5) as client:
                        resp = client.delete(api_url(f"goals/{goal_id}"))
                    if resp.status_code in (200, 204):
                        st.success(f"Deleted **{name}**")
                        st.rerun()
                    else:
                        st.error(f"Delete failed: {resp.text}")
                except httpx.ConnectError:
                    st.error("Backend not available.")
                except Exception as e:
                    st.error(f"Error: {e}")

        # Inline edit form
        if st.session_state.get(f"editing_{goal_id}", False):
            with st.form(f"edit_form_{goal_id}"):
                st.markdown(f"##### Edit: {name}")
                e1, e2 = st.columns(2)
                with e1:
                    new_name = st.text_input("Name", value=name, key=f"ename_{goal_id}")
                    new_target = st.number_input("Target (₹)", value=float(target), min_value=1.0, step=100.0, key=f"etarget_{goal_id}")
                with e2:
                    new_current = st.number_input("Current (₹)", value=float(current), min_value=0.0, step=50.0, key=f"ecurrent_{goal_id}")
                    new_priority = st.selectbox("Priority", ["high", "medium", "low"],
                                                index=["high", "medium", "low"].index(priority), key=f"eprio_{goal_id}")
                save = st.form_submit_button("💾  Save Changes", use_container_width=True)
                if save:
                    update_payload = {
                        "name": new_name.strip(),
                        "target_amount": new_target,
                        "current_amount": new_current,
                        "priority": new_priority,
                    }
                    try:
                        with httpx.Client(timeout=10) as client:
                            resp = client.put(api_url(f"goals/{goal_id}"), json=update_payload)
                        if resp.status_code == 200:
                            st.success("Updated!")
                            st.session_state[f"editing_{goal_id}"] = False
                            st.rerun()
                        else:
                            st.error(f"Update failed: {resp.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
