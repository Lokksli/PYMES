import sqlite3
import os

# messages DB helper: stores and retrieves chat messages
DB_PATH = os.path.join(os.path.dirname(__file__), 'badwords.db')

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

def add_word(word: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute('INSERT INTO words (word) VALUES(?)', (word,))
    conn.commit()
    conn.close()

def get_all_words():
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT word FROM words')
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

def get_a_word_by_id(id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT word FROM words WHERE id = ?', (id,))
    word = c.fetchone()
    conn.close()
    return word
   
