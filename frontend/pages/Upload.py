"""
📤 Upload – Import Bank Statements
====================================
CSV upload with preview, processing, categorization results,
and previously uploaded file listing.
"""

import streamlit as st
import pandas as pd
import httpx
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.styles import inject_css, page_header, glass_card, api_url, COLORS

page_header(
    "Upload Statement",
    "Import your bank statements in CSV format for AI-powered analysis",
    "📤",
)

# ── Sample download section ──────────────────────────────────────────────────
sample_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_statement.csv")
if os.path.exists(sample_path):
    with open(sample_path, "rb") as f:
        sample_bytes = f.read()
    st.download_button(
        label="📥  Download Sample CSV",
        data=sample_bytes,
        file_name="sample_statement.csv",
        mime="text/csv",
    )
else:
    st.markdown(
        """
        <div class="glass-card" style="padding:16px 24px;">
            <p style="margin:0;color:#9999BB;font-size:0.9rem;">
                💡 <strong>Tip:</strong> Your CSV should have columns like
                <code>date</code>, <code>description</code>, <code>amount</code>,
                and optionally <code>category</code>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── File Uploader ────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Choose a bank statement (CSV or PDF)",
    type=["csv", "pdf"],
    help="Upload a CSV or PDF file containing your bank transactions. Expected columns: date, description, amount.",
)

if uploaded_file is not None:
    # ── Preview ──────────────────────────────────────────────────────────────
    try:
        is_pdf = uploaded_file.name.lower().endswith(".pdf")
        if is_pdf:
            import pdfplumber
            df_list = []
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages[:2]: # Check first 2 pages for preview
                    table = page.extract_table()
                    if table and len(table) > 1:
                        headers = [str(h).replace('\n', ' ') if h else '' for h in table[0]]
                        df_list.append(pd.DataFrame(table[1:], columns=headers))
            if df_list:
                df_preview = pd.concat(df_list, ignore_index=True)
            else:
                df_preview = pd.DataFrame(columns=["date", "description", "amount", "type"])
        else:
            df_preview = pd.read_csv(uploaded_file)
            
        uploaded_file.seek(0)  # Reset for later upload

        st.markdown("#### 📋 File Preview")
        st.markdown(
            f"""
            <div class="glass-card" style="padding:16px 24px;margin-bottom:16px;">
                <div style="display:flex;gap:32px;flex-wrap:wrap;">
                    <div><span style="color:#9999BB;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em;">File Name</span>
                         <p style="margin:2px 0 0;font-weight:600;">{uploaded_file.name}</p></div>
                    <div><span style="color:#9999BB;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em;">Rows</span>
                         <p style="margin:2px 0 0;font-weight:600;">{len(df_preview):,}</p></div>
                    <div><span style="color:#9999BB;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em;">Columns</span>
                         <p style="margin:2px 0 0;font-weight:600;">{len(df_preview.columns)}</p></div>
                    <div><span style="color:#9999BB;font-size:0.8rem;text-transform:uppercase;letter-spacing:0.05em;">Size</span>
                         <p style="margin:2px 0 0;font-weight:600;">{uploaded_file.size / 1024:.1f} KB</p></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Show first 10 rows
        display_df = df_preview.head(10).copy()
        display_df.columns = [c.title() for c in display_df.columns]
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        if len(df_preview) > 10:
            st.caption(f"Showing first 10 of {len(df_preview):,} rows")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Process button ───────────────────────────────────────────────────
        if st.button("🚀  Process Statement", use_container_width=True, type="primary"):
            with st.spinner("Uploading and categorizing transactions…"):
                try:
                    uploaded_file.seek(0)
                    mime_type = "application/pdf" if uploaded_file.name.lower().endswith(".pdf") else "text/csv"
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), mime_type)}
                    with httpx.Client(timeout=30) as client:
                        resp = client.post(api_url("upload/statement"), files=files)

                    if resp.status_code in (200, 201):
                        result = resp.json()
                        tx_count = result.get("transactions_imported", result.get("count", len(df_preview)))
                        categories = result.get("categories", {})

                        # Success banner
                        st.markdown(
                            f"""
                            <div class="glass-card" style="border-color:rgba(0,212,170,0.4);margin-top:16px;">
                                <div style="display:flex;align-items:center;gap:16px;">
                                    <div style="font-size:2.5rem;">✅</div>
                                    <div>
                                        <h3 style="margin:0;color:#00D4AA;">Upload Successful!</h3>
                                        <p style="margin:4px 0 0;color:#9999BB;">
                                            <strong>{tx_count}</strong> transactions imported and categorized.
                                        </p>
                                    </div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        # Categorization results
                        if categories:
                            st.markdown("#### 🏷️ Categorization Results")
                            cat_cols = st.columns(min(len(categories), 4))
                            color_map = {
                                0: COLORS["primary"],
                                1: COLORS["accent"],
                                2: COLORS["warning"],
                                3: COLORS["danger"],
                            }
                            for idx, (cat, count) in enumerate(categories.items()):
                                col_color = color_map.get(idx % 4, COLORS["primary"])
                                with cat_cols[idx % len(cat_cols)]:
                                    st.markdown(
                                        f"""
                                        <div class="glass-card" style="text-align:center;padding:18px 12px;">
                                            <p style="margin:0;font-size:0.78rem;color:#9999BB;text-transform:uppercase;
                                               letter-spacing:0.05em;">{cat}</p>
                                            <p style="margin:6px 0 0;font-size:1.6rem;font-weight:800;color:{col_color};">{count}</p>
                                        </div>
                                        """,
                                        unsafe_allow_html=True,
                                    )

                        st.balloons()
                    else:
                        st.error(f"Upload failed (HTTP {resp.status_code}): {resp.text}")

                except httpx.ConnectError:
                    st.error("❌ Cannot connect to the backend API. Please make sure the server is running on `localhost:8000`.")
                except Exception as e:
                    st.error(f"❌ Upload error: {e}")

    except Exception as e:
        st.error(f"Could not read the file for preview: {e}")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Previously Uploaded Files ────────────────────────────────────────────────
st.markdown("#### 📁 Previously Uploaded Files")

try:
    with httpx.Client(timeout=5) as client:
        resp = client.get(api_url("upload/files"))
        if resp.status_code == 200:
            files_data = resp.json()
            file_list = files_data if isinstance(files_data, list) else files_data.get("files", [])

            if file_list:
                for idx, f in enumerate(file_list):
                    fname = f.get("filename", f.get("name", f"File {idx + 1}"))
                    fdate = f.get("uploaded_at", f.get("date", "—"))
                    fcount = f.get("transaction_count", f.get("count", "—"))
                    st.markdown(
                        f"""
                        <div class="glass-card" style="padding:14px 20px;margin-bottom:10px;
                            display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
                            <div style="display:flex;align-items:center;gap:12px;">
                                <div style="font-size:1.4rem;">📄</div>
                                <div>
                                    <p style="margin:0;font-weight:600;font-size:0.95rem;">{fname}</p>
                                    <p style="margin:2px 0 0;color:#9999BB;font-size:0.8rem;">Uploaded: {fdate}</p>
                                </div>
                            </div>
                            <span class="badge badge-accent">{fcount} transactions</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    """
                    <div class="glass-card" style="text-align:center;padding:40px;">
                        <p style="color:#9999BB;margin:0;">No files uploaded yet. Use the uploader above to get started.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("Could not fetch previously uploaded files.")

except httpx.ConnectError:
    st.markdown(
        """
        <div class="glass-card" style="text-align:center;padding:30px;">
            <p style="color:#9999BB;margin:0;">📡 Backend not available — upload history will appear here once the server is running.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
except Exception:
    st.markdown(
        """
        <div class="glass-card" style="text-align:center;padding:30px;">
            <p style="color:#9999BB;margin:0;">Could not load file history.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
