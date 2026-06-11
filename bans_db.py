import sqlite3
import os
import time

DB_PATH = os.path.join(os.path.dirname(__file__), 'bans.db')

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        banned_until INTEGER NOT NULL
    )''')
    conn.commit()
    conn.close()

def ban_user(username: str, seconds: int):
    """Ban a user for `seconds` seconds from now. Overwrites existing ban."""
    until = int(time.time()) + int(seconds)
    conn = get_conn()
    c = conn.cursor()
    # upsert style: remove existing then insert
    c.execute('DELETE FROM bans WHERE username = ?', (username,))
    c.execute('INSERT INTO bans (username, banned_until) VALUES (?, ?)', (username, until))
    conn.commit()
    conn.close()

def is_banned(username: str):
    """Return (bool, seconds_left)."""
    now = int(time.time())
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT banned_until FROM bans WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()
    if not row:
        return False, 0
    until = int(row[0])
    if until <= now:
        # ban expired; cleanup
        conn = get_conn()
        c = conn.cursor()
        c.execute('DELETE FROM bans WHERE username = ?', (username,))
        conn.commit()
        conn.close()
        return False, 0
    return True, until - now
