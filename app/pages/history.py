import streamlit as st
import sqlite3
from datetime import datetime

DB_PATH = r"D:\auditor_2.0\app\data\auditor.db"

st.set_page_config(page_title="History", layout="wide")

if 'user' not in st.session_state or st.session_state.user is None:
    st.error("Please login first.")
    st.stop()

user = st.session_state.user

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Source Sans 3', sans-serif !important; background: #f5f5f5 !important; }
.stApp { background: #f5f5f5 !important; }
[data-testid="stToolbar"] { display: none; }
</style>
""", unsafe_allow_html=True)

st.markdown(f"## Session History — {user['name']}")
st.markdown("---")

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("SELECT * FROM sessions WHERE user_email = ? ORDER BY created_at DESC", (user['email'],))
rows = c.fetchall()
conn.close()

if not rows:
    st.info("No sessions yet. Go to Dashboard and complete an interview.")
else:
    for row in rows:
        id, user_name, user_email, skills, difficulty, question, transcript, score, verdict, strengths, improvements, star_rewrite, created_at = row

        if score >= 80:
            score_color = "#16a34a"
        elif score >= 60:
            score_color = "#d97706"
        else:
            score_color = "#dc2626"

        st.markdown(f"""
        <div style="background:#fff;border:1px solid #e8e8e8;border-radius:4px;
        padding:20px 24px;margin-bottom:12px;display:flex;
        justify-content:space-between;align-items:center;">
            <div>
                <div style="font-size:12px;color:#888;margin-bottom:4px;">{created_at}</div>
                <div style="font-size:15px;font-weight:600;color:#1a1a1a;margin-bottom:4px;">{skills}</div>
                <div style="font-size:13px;color:#666;">{difficulty} · {verdict[:80]}...</div>
            </div>
            <div style="font-size:28px;font-weight:800;color:{score_color};">{score}</div>
        </div>
        """, unsafe_allow_html=True)