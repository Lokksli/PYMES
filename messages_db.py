import sqlite3
import os

# messages DB helper: stores and retrieves chat messages
DB_PATH = os.path.join(os.path.dirname(__file__), 'messages.db')


def get_conn():
    # return a sqlite connection suitable for simple multi-threaded use
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    # create messages table if it does not exist
    conn = get_conn()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()


def add_message(username: str, message: str):
    # insert a single message row into the DB
    conn = get_conn()
    c = conn.cursor()
    c.execute('INSERT INTO messages (username, message) VALUES (?, ?)', (username, message))
    conn.commit()
    conn.close()


def get_recent_messages(limit: int = 100):
    # fetch recent messages (returns oldest-first)
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id, username, message, created_at FROM messages ORDER BY id DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()
    # rows come newest-first; reverse to show oldest first
    rows.reverse()
    return [
        {'id': r[0], 'username': r[1], 'message': r[2], 'created_at': r[3]} for r in rows
    ]
