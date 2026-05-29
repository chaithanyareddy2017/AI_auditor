import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import os
import tempfile
#import whisper
#from audiorecorder import audiorecorder
from groq import Groq
from dotenv import load_dotenv
from utils.database import init_db, save_session, get_sessions
from utils.resume import index_resume, query_resume
load_dotenv()
init_db()
 
# ── LOGIN ──────────────────────────────────────────────
if 'user' not in st.session_state:
    st.session_state.user = None
 
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'
 
if st.session_state.user is None:
    st.set_page_config(page_title="Interview Auditor", layout="centered")
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; background: #f0ede6 !important; }
    .stApp { background: #f0ede6 !important; }
    [data-testid="stToolbar"] { display: none; }
    .block-container { max-width: 400px !important; padding-top: 80px !important; margin: 0 auto !important; }
    .stTextInput label {
        font-family: 'Inter', sans-serif !important; font-size: 10px !important;
        font-weight: 700 !important; color: #888 !important; -webkit-text-fill-color: #888 !important;
        letter-spacing: 0.15em !important; text-transform: uppercase !important;
    }
    .stTextInput > div > div > input {
        border: 2px solid #111 !important; border-radius: 0 !important;
        font-size: 14px !important; padding: 10px 12px !important;
        background: #fff !important; color: #111 !important;
    }
    .stButton > button {
        background: #111 !important; color: #f0ede6 !important; border: none !important;
        border-radius: 0 !important; font-size: 13px !important; font-weight: 700 !important;
        letter-spacing: 0.08em !important; text-transform: uppercase !important;
        padding: 0.75rem 2rem !important; width: 100% !important;
    }
    </style>
    <div style="margin-bottom:24px;">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:20px;">
            <span style="font-size:20px;">⚡</span>
            <span style="font-family:'Bebas Neue',sans-serif;font-size:18px;letter-spacing:0.08em;color:#111;">INTERVIEW AUDITOR</span>
        </div>
        <div style="font-family:'Inter',sans-serif;font-size:28px;font-weight:800;color:#111;letter-spacing:-0.02em;margin-bottom:6px;">Sign In</div>
        <div style="height:3px;width:40px;background:#111;margin-bottom:20px;"></div>
    </div>
    """, unsafe_allow_html=True)
 
    name = st.text_input("Full Name", placeholder="Your name")
    email = st.text_input("Email", placeholder="your@email.com")
 
    if st.button("CONTINUE →"):
        if name.strip() == "" or email.strip() == "":
            st.error("Please enter both name and email.")
        else:
            st.session_state.user = {"name": name.strip(), "email": email.strip()}
            st.rerun()
    st.stop()
 
# ── MAIN APP CSS ───────────────────────────────────────
st.set_page_config(page_title="Interview Auditor", layout="wide")
 
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@300;400;500;600;700&family=Source+Serif+4:wght@600;700&display=swap');
html, body, [class*="css"] { font-family: 'Source Sans 3', sans-serif !important; background: #f5f5f5 !important; color: #1a1a1a !important; }
.stApp { background: #f5f5f5 !important; }
section[data-testid="stSidebar"] { display: none; }
[data-testid="stToolbar"] { display: none; }
.hero-banner { background: linear-gradient(135deg, #0056D2 0%, #003899 100%); padding: 40px 32px; color: #fff; }
.hero-inner { max-width: 860px; margin: 0 auto; }
.hero-eyebrow { font-size: 13px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: rgba(255,255,255,0.6); margin-bottom: 10px; }
.hero-title { font-family: 'Source Serif 4', serif; font-size: 34px; font-weight: 700; color: #fff; letter-spacing: -0.01em; margin-bottom: 8px; line-height: 1.2; }
.hero-sub { font-size: 16px; color: rgba(255,255,255,0.7); font-weight: 300; line-height: 1.6; max-width: 520px; }
.hero-stats { display: flex; gap: 32px; margin-top: 20px; }
.stat { display: flex; flex-direction: column; gap: 2px; }
.stat-num { font-size: 18px; font-weight: 700; color: #fff; }
.stat-label { font-size: 11px; color: rgba(255,255,255,0.5); text-transform: uppercase; letter-spacing: 0.08em; }
.body { max-width: 860px; margin: 0 auto; padding: 32px 24px; }
.card { background: #fff; border: 1px solid #e8e8e8; border-radius: 4px; padding: 24px; margin-bottom: 16px; }
.card-title { font-size: 18px; font-weight: 700; color: #1a1a1a; margin-bottom: 6px; display: flex; align-items: center; gap: 8px; }
.card-sub { font-size: 14px; color: #666; margin-bottom: 18px; font-weight: 400; }
.step-badge { display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px; background: #0056D2; color: #fff; border-radius: 50%; font-size: 11px; font-weight: 700; }
div[data-testid="stCheckbox"] { background: #f8f8f8 !important; border: 1px solid #e0e0e0 !important; border-radius: 4px !important; padding: 8px 14px !important; margin-bottom: 6px !important; margin-right: 6px !important; transition: all 0.15s !important; display: inline-flex !important; width: auto !important; }
div[data-testid="stCheckbox"]:hover { border-color: #0056D2 !important; background: #f0f5ff !important; }
div[data-testid="stCheckbox"]:has(input:checked) { background: #EEF4FF !important; border-color: #0056D2 !important; }
div[data-testid="stCheckbox"] label { font-family: 'Source Sans 3', sans-serif !important; font-size: 13px !important; font-weight: 500 !important; color: #444 !important; -webkit-text-fill-color: #444 !important; }
div[data-testid="stCheckbox"]:has(input:checked) label { color: #0056D2 !important; -webkit-text-fill-color: #0056D2 !important; font-weight: 600 !important; }
input[type="checkbox"] { accent-color: #0056D2 !important; }
div[data-testid="stRadio"] > div { display: flex !important; gap: 8px !important; flex-direction: row !important; }
div[data-testid="stRadio"] label { font-family: 'Source Sans 3', sans-serif !important; font-size: 13px !important; font-weight: 500 !important; color: #444 !important; -webkit-text-fill-color: #444 !important; background: #f8f8f8 !important; border: 1px solid #e0e0e0 !important; border-radius: 4px !important; padding: 8px 20px !important; }
div[data-testid="stRadio"]:has(input:checked) label { color: #0056D2 !important; -webkit-text-fill-color: #0056D2 !important; background: #EEF4FF !important; border-color: #0056D2 !important; font-weight: 600 !important; }
input[type="radio"] { accent-color: #0056D2 !important; }
.selected-wrap { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.sel-pill { font-size: 15px; font-weight: 600; color: #0056D2; background: #EEF4FF; border: 1px solid #c5d8ff; border-radius: 20px; padding: 4px 12px; }
.stButton > button { background: #0056D2 !important; color: #fff !important; border: none !important; border-radius: 4px !important; font-family: 'Source Sans 3', sans-serif !important; font-size: 14px !important; font-weight: 600 !important; padding: 0.75rem 2rem !important; width: 100% !important; }
.stButton > button:hover { background: #003899 !important; }
.q-card { background: #fff; border: 1px solid #e8e8e8; border-left: 3px solid #0056D2; border-radius: 4px; padding: 16px 20px; margin-bottom: 10px; display: flex; gap: 16px; align-items: flex-start; }
.q-num { font-size: 13px; font-weight: 700; color: #0056D2; letter-spacing: 0.1em; min-width: 24px; padding-top: 2px; text-transform: uppercase; }
.q-text { font-size: 14px; color: #1a1a1a; line-height: 1.65; font-weight: 400; }
.progress-bar { height: 3px; background: #e8e8e8; border-radius: 2px; margin-bottom: 24px; overflow: hidden; }
.progress-fill { height: 100%; background: #0056D2; border-radius: 2px; width: 25%; }
.footer-bar { display: flex; justify-content: space-between; align-items: center; padding: 16px 32px; border-top: 1px solid #e0e0e0; background: #fff; margin-top: 2rem; }
.footer-l { font-size: 15px; color: #888; }
.footer-links { display: flex; gap: 24px; }
.footer-link { font-size: 15px; color: #888; cursor: pointer; }
.footer-link:hover { color: #0056D2; }
</style>
""", unsafe_allow_html=True)
 
# ── TOPBAR ─────────────────────────────────────────────
user = st.session_state.user
initials = "".join([n[0].upper() for n in user['name'].split()[:2]])
 
col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1, 1, 1])
with col1:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;padding:12px 0;">
        <div style="width:32px;height:32px;background:#0056D2;border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;color:#fff;">AI</div>
        <div style="font-size:17px;font-weight:700;color:#1a1a1a;">Interview Auditor</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    if st.button("Dashboard", key="nav_dash"):
        st.session_state.page = 'dashboard'
        st.rerun()
with col3:
    if st.button("History", key="nav_hist"):
        st.session_state.page = 'history'
        st.rerun()
with col4:
    if st.button("Reports", key="nav_rep"):
        st.session_state.page = 'reports'
        st.rerun()
with col5:
    if st.button("Logout", key="nav_logout"):
        st.session_state.user = None
        st.session_state.page = 'dashboard'
        st.rerun()
with col6:
    st.markdown(f"""
    <div style="display:flex;justify-content:flex-end;padding:8px 0;">
        <div style="width:32px;height:32px;border-radius:50%;background:#0056D2;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#fff;">{initials}</div>
    </div>
    """, unsafe_allow_html=True)
 
st.markdown("<hr style='margin:0;border:none;border-top:1px solid #e0e0e0;'>", unsafe_allow_html=True)
 
# ── DASHBOARD PAGE ─────────────────────────────────────
if st.session_state.page == 'dashboard':
 
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-inner">
            <div class="hero-eyebrow">AI-Powered Interview Preparation</div>
            <div class="hero-title">Practice Interview</div>
            <div class="hero-sub">Select your skills, choose a difficulty level, and get sharp AI-generated interview questions tailored to you.</div>
            <div class="hero-stats">
                <div class="stat"><div class="stat-num">5</div><div class="stat-label">Questions</div></div>
                <div class="stat"><div class="stat-num">16</div><div class="stat-label">Skills</div></div>
                <div class="stat"><div class="stat-num">3</div><div class="stat-label">Levels</div></div>
            </div>
        </div>
    </div>
    <div class="body">
    <div class="progress-bar"><div class="progress-fill"></div></div>
    """, unsafe_allow_html=True)
 
    # Technical Skills
    st.markdown("""
    <div class="card">
        <div class="card-title"><span class="step-badge">1</span> Technical Skills</div>
        <div class="card-sub">Select the programming languages and technical concepts you want to be assessed on</div>
    </div>
    """, unsafe_allow_html=True)
 
    tech_skills = ["Python", "Java", "C++", "DSA", "System Design", "SQL", "REST APIs", "Git"]
    cols = st.columns(4)
    selected_tech = []
    for i, skill in enumerate(tech_skills):
        with cols[i % 4]:
            if st.checkbox(skill, key=f"tech_{skill}"):
                selected_tech.append(skill)
 
    # Domain Skills
    st.markdown("""
    <div class="card" style="margin-top:16px;">
        <div class="card-title"><span class="step-badge">2</span> Domain Skills</div>
        <div class="card-sub">Select the specialized domains relevant to your target role</div>
    </div>
    """, unsafe_allow_html=True)
 
    domain_skills = ["Machine Learning", "Deep Learning", "NLP", "Web Development",
                     "Data Science", "DevOps", "Computer Vision", "Cloud (AWS/GCP)"]
    cols2 = st.columns(4)
    selected_domain = []
    for i, skill in enumerate(domain_skills):
        with cols2[i % 4]:
            if st.checkbox(skill, key=f"domain_{skill}"):
                selected_domain.append(skill)
 
    # Difficulty
    st.markdown("""
    <div class="card" style="margin-top:16px;">
        <div class="card-title"><span class="step-badge">3</span> Difficulty Level</div>
        <div class="card-sub">Choose the complexity level of your interview questions</div>
    </div>
    """, unsafe_allow_html=True)
 
    difficulty = st.radio("", ["Beginner", "Intermediate", "Advanced"],
                          horizontal=True, label_visibility="collapsed")
 
    all_selected = selected_tech + selected_domain
    if all_selected:
        pills = "".join([f'<span class="sel-pill">{s}</span>' for s in all_selected])
        st.markdown(f"""
        <div class="card" style="margin-top:16px;">
            <div class="card-title">Selected Skills</div>
            <div class="selected-wrap">{pills}</div>
        </div>
        """, unsafe_allow_html=True)
        # Resume Upload
    st.markdown("""
    <div class="card" style="margin-top:16px;">
        <div class="card-title"><span class="step-badge">0</span> Upload Resume (Optional)</div>
        <div class="card-sub">Upload your resume to get personalized questions based on your experience</div>
    </div>
    """, unsafe_allow_html=True)

    resume_file = st.file_uploader("", type=["pdf"], label_visibility="collapsed")
    if resume_file is not None:
        if 'resume_indexed' not in st.session_state or st.session_state.get('resume_name') != resume_file.name:
            with st.spinner("Indexing your resume..."):
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                    f.write(resume_file.read())
                    temp_pdf = f.name
                try:
                    index_resume(temp_pdf, user['email'])
                    st.session_state.resume_indexed = True
                    st.session_state.resume_name = resume_file.name
                    os.unlink(temp_pdf)
                    st.success(f"✓ Resume indexed — {resume_file.name}")
                except Exception as e:
                    st.error(f"Resume error: {e}")
 
    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
 
    # Generate Questions
    if st.button("Generate Interview Questions"):
        if not all_selected:
            st.error("Please select at least one skill to continue.")
        else:
            with st.spinner("Generating your questions..."):
                client = Groq(api_key=os.getenv("GROQ_API_KEY"))
                skills_str = ", ".join(all_selected)
                resume_context = ""
            if st.session_state.get('resume_indexed'):
                resume_context = query_resume(user['email'], f"relevant experience and skills for {skills_str}")

            prompt = f"""You are an expert technical interviewer.
{"Use this resume context to personalize questions: " + resume_context if resume_context else ""}
Generate exactly 5 {difficulty} level interview questions for a candidate with skills in: {skills_str}.
Format strictly as:
Q1: [question]
Q2: [question]
Q3: [question]
Q4: [question]
Q5: [question]
No explanations. Just the questions."""
            response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7, max_tokens=800
                )
            questions_text = response.choices[0].message.content
            lines = [l.strip() for l in questions_text.strip().split('\n')
                         if l.strip() and l.strip().startswith('Q')]
            st.session_state.questions = lines
            st.session_state.questions_generated = True
 
            st.markdown("""
                <div class="card" style="margin-top:16px;">
                    <div class="card-title">Your Interview Questions</div>
                    <div class="card-sub">Review each question carefully before recording your answer</div>
                </div>
                """, unsafe_allow_html=True)
 
            for i, q in enumerate(lines[:5], 1):
                    clean_q = q[3:].strip() if len(q) > 3 and q[2] == ':' else q
                    st.markdown(f"""
                    <div class="q-card">
                        <div class="q-num">Q{i}</div>
                        <div class="q-text">{clean_q}</div>
                    </div>
                    """, unsafe_allow_html=True)
 
    # Audio Recording
    st.markdown("""
    <div class="card" style="margin-top:16px;">
        <div class="card-title"><span class="step-badge">4</span> Record Your Answer</div>
        <div class="card-sub">Click the microphone button to start recording, click stop when done</div>
    </div>
    """, unsafe_allow_html=True)
 
    #audio = audiorecorder(
    start_prompt="🎙 Start Recording",
    stop_prompt="⏹ Stop Recording",
    pause_prompt="",
    key="audio_recorder"
 )
 
    if len(audio) > 0:
        st.audio(audio.export().read(), format="audio/wav")
 
        with st.spinner("Transcribing your answer..."):
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                audio.export(f.name, format="wav")
                temp_path = f.name
            model = whisper.load_model("base")
            result = model.transcribe(temp_path)
            transcript = result["text"]
            os.unlink(temp_path)
 
        questions_context = ""
        if 'questions' in st.session_state:
            questions_context = "\n".join(st.session_state.questions)
 
        with st.spinner("Analyzing your answer..."):
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
 
            feedback_prompt = f"""You are an expert interview coach.
 
Interview Questions Asked:
{questions_context}
 
Candidate's Answer:
{transcript}
 
Analyze the answer and respond ONLY in this exact format:
 
SCORE: [number out of 100]
 
STRENGTHS:
- [point 1]
- [point 2]
- [point 3]
 
IMPROVEMENTS:
- [point 1]
- [point 2]
- [point 3]
 
STAR_REWRITE:
[Rewrite the answer in STAR format: Situation, Task, Action, Result]
 
VERDICT: [One sentence overall assessment]"""
 
            feedback_response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": feedback_prompt}],
                temperature=0.5, max_tokens=1000
            )
            feedback_text = feedback_response.choices[0].message.content
 
            # Parse score
            score = 0
            for line in feedback_text.split('\n'):
                if line.startswith('SCORE:'):
                    try:
                        score = int(''.join(filter(str.isdigit, line)))
                    except:
                          score = 0
                    break
 
            # Parse sections
            def extract_section(text, start_tag, end_tags):
                capturing = False
                result = []
                for line in text.split('\n'):
                    if line.strip().startswith(start_tag):
                        capturing = True
                        continue
                    if capturing:
                        if any(line.strip().startswith(t) for t in end_tags):
                            break
                        if line.strip():
                            result.append(line.strip())
                return result
 
            strengths = extract_section(feedback_text, 'STRENGTHS:', ['IMPROVEMENTS:', 'STAR_REWRITE:', 'VERDICT:'])
            improvements = extract_section(feedback_text, 'IMPROVEMENTS:', ['STAR_REWRITE:', 'VERDICT:'])
 
            verdict = ""
            for line in feedback_text.split('\n'):
                if line.startswith('VERDICT:'):
                    verdict = line.replace('VERDICT:', '').strip()
 
            star_lines = []
            capturing_star = False
            for line in feedback_text.split('\n'):
                if line.strip().startswith('STAR_REWRITE:'):
                    capturing_star = True
                    continue
                if capturing_star:
                    if line.strip().startswith('VERDICT:'):
                        break
                    if line.strip():
                        star_lines.append(line.strip())
            star_rewrite = ' '.join(star_lines)
 
            # Save session
            try:
                save_session(
                    user=st.session_state.user,
                    skills=all_selected,
                    difficulty=difficulty,
                    question=questions_context,
                    transcript=transcript,
                    score=score,
                    verdict=verdict,
                    strengths=strengths,
                    improvements=improvements,
                    star_rewrite=star_rewrite
                )
            except Exception as e:
                st.error(f"Save error: {e}")
 
            # Build results HTML
            strengths_html = ""
            for s in strengths:
                strengths_html += f"""
                <div style="display:flex;gap:10px;margin-bottom:12px;align-items:flex-start;">
                    <div style="width:18px;height:18px;border-radius:50%;background:#f0fdf4;border:1px solid #86efac;display:flex;align-items:center;justify-content:center;font-size:10px;color:#16a34a;flex-shrink:0;margin-top:1px;">✓</div>
                    <div style="font-size:15px;color:#1a1a1a;line-height:1.6;">{s.lstrip("-").strip()}</div>
                </div>"""
 
            improvements_html = ""
            for s in improvements:
                improvements_html += f"""
                <div style="display:flex;gap:10px;margin-bottom:12px;align-items:flex-start;">
                    <div style="width:18px;height:18px;border-radius:50%;background:#fffbeb;border:1px solid #fcd34d;display:flex;align-items:center;justify-content:center;font-size:10px;color:#d97706;flex-shrink:0;margin-top:1px;">→</div>
                    <div style="font-size:15px;color:#1a1a1a;line-height:1.6;">{s.lstrip("-").strip()}</div>
                </div>"""
 
            results_html = f"""
            <div style="background:#fff;border:1px solid #e8e8e8;border-radius:4px;margin-top:16px;overflow:hidden;">
                <div style="background:linear-gradient(135deg,#0056D2,#003899);padding:24px 28px;display:flex;align-items:center;gap:24px;">
                    <div style="width:72px;height:72px;border-radius:50%;background:rgba(255,255,255,0.15);border:2px solid rgba(255,255,255,0.4);display:flex;flex-direction:column;align-items:center;justify-content:center;">
                        <div style="font-size:24px;font-weight:800;color:#fff;">{score}</div>
                        <div style="font-size:13px;color:rgba(255,255,255,0.6);font-weight:500;">/ 100</div>
                    </div>
                    <div>
                        <div style="font-size:11px;font-weight:600;color:rgba(255,255,255,0.5);letter-spacing:0.12em;text-transform:uppercase;margin-bottom:4px;">Interview Score</div>
                        <div style="font-size:17px;color:#fff;font-weight:400;line-height:1.5;max-width:560px;font-style:italic;">{verdict}</div>
                    </div>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;border-top:1px solid #e8e8e8;">
                    <div style="padding:24px 28px;border-right:1px solid #e8e8e8;">
                        <div style="font-size:15px;font-weight:700;color:#16a34a;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:16px;">What Went Well</div>
                        {strengths_html}
                    </div>
                    <div style="padding:24px 28px;">
                        <div style="font-size:15px;font-weight:700;color:#d97706;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:16px;">What To Improve</div>
                        {improvements_html}
                    </div>
                </div>
                <div style="padding:24px 28px;border-top:1px solid #e8e8e8;background:#fafafa;">
                    <div style="font-size:15px;font-weight:700;color:#0056D2;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:16px;">⭐ How To Say It Better — STAR Format</div>
                    <div style="font-size:15px;color:#1a1a1a;line-height:1.9;">{star_rewrite}</div>
                </div>
                <div style="padding:24px 28px;border-top:1px solid #e8e8e8;">
                    <div style="font-size:15px;font-weight:700;color:#888;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:12px;">Your Transcript</div>
                    <div style="font-size:15px;color:#555;line-height:1.8;font-style:italic;">"{transcript}"</div>
                </div>
            </div>"""
 
            components.html(results_html, height=800, scrolling=True)
 
    st.markdown('</div>', unsafe_allow_html=True)
 
# ── HISTORY PAGE ───────────────────────────────────────
elif st.session_state.page == 'history':
    st.markdown("""
    <div style="max-width:860px;margin:0 auto;padding:32px 24px;">
        <div style="font-size:22px;font-weight:700;color:#1a1a1a;margin-bottom:8px;">Session History</div>
        <div style="font-size:14px;color:#888;margin-bottom:24px;">All your past interview sessions</div>
    </div>
    """, unsafe_allow_html=True)
 
    try:
        conn = sqlite3.connect(r"D:\auditor_2.0\app\data\auditor.db")
        c = conn.cursor()
        c.execute("SELECT * FROM sessions WHERE user_email = ? ORDER BY created_at DESC",
                  (user['email'],))
        rows = c.fetchall()
        conn.close()
 
        if not rows:
            st.info("No sessions yet. Go to Dashboard and complete an interview.")
        else:
            for row in rows:
                _, _, _, skills, difficulty, _, _, score, verdict, _, _, _, created_at = row
                score_color = "#16a34a" if score >= 80 else "#d97706" if score >= 60 else "#dc2626"
                st.markdown(f"""
                <div style="background:#fff;border:1px solid #e8e8e8;border-radius:4px;
                padding:20px 24px;margin-bottom:12px;display:flex;
                justify-content:space-between;align-items:center;
                max-width:860px;margin-left:auto;margin-right:auto;">
                    <div>
                        <div style="font-size:12px;color:#888;margin-bottom:4px;">{created_at}</div>
                        <div style="font-size:15px;font-weight:600;color:#1a1a1a;margin-bottom:4px;">{skills}</div>
                        <div style="font-size:13px;color:#666;">{difficulty} · {verdict[:80]}...</div>
                    </div>
                    <div style="font-size:28px;font-weight:800;color:{score_color};min-width:60px;text-align:right;">{score}<span style="font-size:13px;color:#888;font-weight:400;">/100</span></div>
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading history: {e}")
 
# ── REPORTS PAGE ───────────────────────────────────────
elif st.session_state.page == 'reports':
    st.markdown("""
    <div style="max-width:860px;margin:0 auto;padding:32px 24px;">
        <div style="font-size:22px;font-weight:700;color:#1a1a1a;margin-bottom:8px;">Reports</div>
        <div style="font-size:14px;color:#888;margin-bottom:24px;">Your performance analytics</div>
    </div>
    """, unsafe_allow_html=True)

    try:
        conn = sqlite3.connect(r"D:\auditor_2.0\app\data\auditor.db")
        c = conn.cursor()
        c.execute("SELECT score, skills, difficulty, created_at FROM sessions WHERE user_email = ? ORDER BY created_at DESC", (user['email'],))
        rows = c.fetchall()
        conn.close()

        if not rows:
            st.info("No sessions yet. Complete an interview first.")
        else:
            scores = [r[0] for r in rows]
            avg_score = round(sum(scores) / len(scores))
            best_score = max(scores)
            total_sessions = len(scores)
            avg_color = "#16a34a" if avg_score >= 80 else "#d97706" if avg_score >= 60 else "#dc2626"

            # Stats cards
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div style="background:#fff;border:1px solid #e8e8e8;border-radius:4px;padding:20px 24px;">
                    <div style="font-size:11px;font-weight:600;color:#888;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px;">Total Sessions</div>
                    <div style="font-size:32px;font-weight:800;color:#1a1a1a;">{total_sessions}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div style="background:#fff;border:1px solid #e8e8e8;border-radius:4px;padding:20px 24px;">
                    <div style="font-size:11px;font-weight:600;color:#888;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px;">Average Score</div>
                    <div style="font-size:32px;font-weight:800;color:{avg_color};">{avg_score}</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div style="background:#fff;border:1px solid #e8e8e8;border-radius:4px;padding:20px 24px;">
                    <div style="font-size:11px;font-weight:600;color:#888;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px;">Best Score</div>
                    <div style="font-size:32px;font-weight:800;color:#16a34a;">{best_score}</div>
                </div>
                """, unsafe_allow_html=True)

            # Score trend
            st.markdown("""
            <div style="background:#fff;border:1px solid #e8e8e8;border-radius:4px;padding:20px 24px;margin-top:16px;">
                <div style="font-size:15px;font-weight:700;color:#1a1a1a;margin-bottom:16px;">Score Trend</div>
            </div>
            """, unsafe_allow_html=True)

            for r in rows[:10]:
                score_val = r[0]
                date_val = r[3][:10]
                skill_val = r[1][:30]
                bar_color = "#16a34a" if score_val >= 80 else "#d97706" if score_val >= 60 else "#dc2626"
                st.markdown(f"""
                <div style="background:#fff;border-left:1px solid #e8e8e8;border-right:1px solid #e8e8e8;
                border-bottom:1px solid #e8e8e8;padding:12px 24px;
                display:flex;align-items:center;gap:12px;">
                    <div style="font-size:13px;color:#888;min-width:100px;">{date_val}</div>
                    <div style="font-size:15px;color:#444;min-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{skill_val}</div>
                    <div style="flex:1;background:#f0f0f0;border-radius:2px;height:8px;">
                        <div style="width:{score_val}%;background:{bar_color};height:8px;border-radius:2px;"></div>
                    </div>
                    <div style="font-size:15px;font-weight:700;color:{bar_color};min-width:36px;text-align:right;">{score_val}</div>
                </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error loading reports: {e}")
     
# ── FOOTER ─────────────────────────────────────────────
st.markdown("""
<div class="footer-bar">
    <div class="footer-l">© 2026 Interview Auditor · Built by Chaithanya Reddy</div>
    <div class="footer-links">
        <span class="footer-link">About</span>
        <span class="footer-link">Privacy</span>
        <span class="footer-link">Help</span>
        <span class="footer-link">Contact</span>
    </div>
</div>
""", unsafe_allow_html=True)