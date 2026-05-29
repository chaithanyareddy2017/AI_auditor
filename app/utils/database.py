import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "auditor.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT,
            user_email TEXT,
            skills TEXT,
            difficulty TEXT,
            question TEXT,
            transcript TEXT,
            score INTEGER,
            verdict TEXT,
            strengths TEXT,
            improvements TEXT,
            star_rewrite TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_session(user, skills, difficulty, question, transcript, score, verdict, strengths, improvements, star_rewrite):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO sessions (
            user_name, user_email, skills, difficulty, question,
            transcript, score, verdict, strengths, improvements,
            star_rewrite, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user['name'],
        user['email'],
        ", ".join(skills),
        difficulty,
        question,
        transcript,
        score,
        verdict,
        "\n".join(strengths),
        "\n".join(improvements),
        star_rewrite,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

def get_sessions(user_email):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT * FROM sessions 
        WHERE user_email = ? 
        ORDER BY created_at DESC
    ''', (user_email,))
    rows = c.fetchall()
    conn.close()
    return rows