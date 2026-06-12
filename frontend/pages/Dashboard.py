"""
📊 Dashboard – Financial Overview
===================================
Displays income/expense metrics, spending breakdown charts,
monthly trend lines, and recent transactions table.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import httpx
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.styles import inject_css, page_header, glass_card, api_url, PLOTLY_LAYOUT, PLOTLY_COLORS, COLORS

page_header("Dashboard", "Your complete financial overview at a glance", "📊")

# ── Fetch summary data ────────────────────────────────────────────────────────
summary = None
transactions = []

try:
    with httpx.Client(timeout=5) as client:
        with st.spinner("Loading financial data…"):
            resp = client.get(api_url("transactions/summary"))
            if resp.status_code == 200:
                summary = resp.json()
            resp_tx = client.get(api_url("transactions/"))
            if resp_tx.status_code == 200:
                transactions = resp_tx.json()
                if isinstance(transactions, dict):
                    transactions = transactions.get("transactions", [])
except httpx.ConnectError:
    st.warning("⚠️ Cannot reach the backend API at `localhost:8000`. Please start the backend server.")
except Exception as e:
    st.error(f"Error fetching data: {e}")

# ── No data state ─────────────────────────────────────────────────────────────
if summary is None and not transactions:
    st.markdown(
        """
        <div class="glass-card" style="text-align:center;padding:60px 40px;">
            <div style="font-size:4rem;margin-bottom:16px;">📭</div>
            <h2 style="margin-bottom:8px;">No Financial Data Yet</h2>
            <p style="color:#9999BB;max-width:480px;margin:0 auto 24px;">
                Upload your first bank statement to see your dashboard come alive with
                beautiful charts, insights, and trends.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("📤  Go to Upload Page", use_container_width=False):
        st.switch_page("pages/2_📤_Upload.py")
    st.stop()

# ── Extract metrics ──────────────────────────────────────────────────────────
total_income = summary.get("total_income", 0) if summary else 0
total_expenses = summary.get("total_expense", 0) if summary else 0
net_savings = total_income - total_expenses
savings_rate = (net_savings / total_income * 100) if total_income else 0

# ── Top Metric Row ───────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("💰 Total Income", f"${total_income:,.2f}")
with m2:
    st.metric("💸 Total Expenses", f"${total_expenses:,.2f}")
with m3:
    delta_color = "normal" if net_savings >= 0 else "inverse"
    st.metric("📈 Net Savings", f"${net_savings:,.2f}", delta_color=delta_color)
with m4:
    st.metric("🏦 Savings Rate", f"{savings_rate:.1f}%")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Prepare transaction dataframe ────────────────────────────────────────────
if transactions:
    df = pd.DataFrame(transactions)

    # Normalize column names to lowercase
    df.columns = [c.lower() for c in df.columns]

    # Ensure expected columns exist
    if "amount" in df.columns:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.sort_values("date", ascending=False)
    if "category" not in df.columns:
        df["category"] = "Uncategorized"

    # ── Charts row ───────────────────────────────────────────────────────────
    chart_left, chart_right = st.columns(2)

    # -- Spending by Category (Donut) --
    with chart_left:
        st.markdown("#### Spending by Category")
        expenses_df = df[df["transaction_type"] == "debit"].copy() if "transaction_type" in df.columns else df.copy()
        if not expenses_df.empty:
            expenses_df["abs_amount"] = expenses_df["amount"].abs()
            cat_spend = expenses_df.groupby("category")["abs_amount"].sum().reset_index()
            cat_spend.columns = ["Category", "Amount"]
            cat_spend = cat_spend.sort_values("Amount", ascending=False)

            fig_donut = px.pie(
                cat_spend,
                names="Category",
                values="Amount",
                hole=0.55,
                color_discrete_sequence=PLOTLY_COLORS,
            )
            fig_donut.update_layout(
                **PLOTLY_LAYOUT,
                showlegend=True,
                height=380,
            )
            fig_donut.update_layout(
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.05,
                    font=dict(size=11),
                    bgcolor="rgba(0,0,0,0)",
                ),
            )
            fig_donut.update_traces(
                textposition="inside",
                textinfo="percent+label",
                textfont_size=11,
                marker=dict(line=dict(color="#0a0e27", width=2)),
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("No expense transactions to chart.")

    # -- Monthly Spending Trend (Line) --
    with chart_right:
        st.markdown("#### Monthly Spending Trend")
        if "date" in df.columns and "amount" in df.columns:
            trend_df = df.copy()
            trend_df["month"] = trend_df["date"].dt.to_period("M").astype(str)
            expenses_trend = trend_df[trend_df["transaction_type"] == "debit"].copy() if "transaction_type" in trend_df.columns else pd.DataFrame()
            if not expenses_trend.empty:
                expenses_trend["abs_amount"] = expenses_trend["amount"].abs()
                monthly = expenses_trend.groupby("month")["abs_amount"].sum().reset_index()
                monthly.columns = ["Month", "Spending"]
                monthly = monthly.sort_values("Month")

                fig_line = go.Figure()
                fig_line.add_trace(
                    go.Scatter(
                        x=monthly["Month"],
                        y=monthly["Spending"],
                        mode="lines+markers",
                        line=dict(color=COLORS["primary"], width=3, shape="spline"),
                        marker=dict(size=8, color=COLORS["accent"], line=dict(width=2, color=COLORS["primary"])),
                        fill="tozeroy",
                        fillcolor="rgba(108,99,255,0.08)",
                        name="Spending",
                    )
                )
                fig_line.update_layout(
                    **PLOTLY_LAYOUT,
                    height=380,
                    xaxis_title="Month",
                    yaxis_title="Spending ($)",
                    xaxis=dict(gridcolor="rgba(108,99,255,0.08)"),
                    yaxis=dict(gridcolor="rgba(108,99,255,0.08)"),
                )
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.info("Not enough data for trend chart.")
        else:
            st.info("Date column not found in transactions.")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # -- Income vs Expenses Bar --
    if "date" in df.columns and "amount" in df.columns:
        st.markdown("#### Income vs Expenses")
        df_temp = df.copy()
        df_temp["month"] = df_temp["date"].dt.to_period("M").astype(str)
        income_m = df_temp[df_temp["transaction_type"] == "credit"].groupby("month")["amount"].sum().reset_index()
        income_m.columns = ["Month", "Income"]
        expense_m = df_temp[df_temp["transaction_type"] == "debit"].copy()
        expense_m["amount"] = expense_m["amount"].abs()
        expense_m = expense_m.groupby("month")["amount"].sum().reset_index()
        expense_m.columns = ["Month", "Expenses"]
        merged = pd.merge(income_m, expense_m, on="Month", how="outer").fillna(0).sort_values("Month")

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=merged["Month"], y=merged["Income"], name="Income", marker_color=COLORS["accent"]))
        fig_bar.add_trace(go.Bar(x=merged["Month"], y=merged["Expenses"], name="Expenses", marker_color=COLORS["danger"]))
        fig_bar.update_layout(
            **PLOTLY_LAYOUT,
            barmode="group",
            height=360,
            xaxis_title="Month",
            yaxis_title="Amount ($)",
            xaxis=dict(gridcolor="rgba(108,99,255,0.08)"),
            yaxis=dict(gridcolor="rgba(108,99,255,0.08)"),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Recent Transactions Table ────────────────────────────────────────────
    st.markdown("#### Recent Transactions")
    display_cols = [c for c in ["date", "description", "category", "amount"] if c in df.columns]
    display_df = df[display_cols].head(25).copy()
    if "date" in display_df.columns:
        display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
    if "amount" in display_df.columns:
        display_df["amount"] = display_df["amount"].apply(lambda x: f"${x:,.2f}")
    display_df.columns = [c.title() for c in display_df.columns]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=min(len(display_df) * 38 + 40, 600),
    )
else:
    st.info("Transaction list is empty. Upload a statement to see data here.")
