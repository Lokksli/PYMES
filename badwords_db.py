import sqlite3
import os

# badwords DB helper: stores words and a flag whether each entry is a regex
DB_PATH = os.path.join(os.path.dirname(__file__), 'badwords.db')


def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    conn = get_conn()
    c = conn.cursor()
    # create table with an is_regex column (0/1)
    c.execute('''CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT NOT NULL,
        is_regex INTEGER DEFAULT 0
    )''')
    conn.commit()

    # ensure column exists for older DBs (sqlite pragma check)
    c.execute("PRAGMA table_info(words)")
    cols = [r[1] for r in c.fetchall()]
    if 'is_regex' not in cols:
        # add missing column
        try:
            c.execute('ALTER TABLE words ADD COLUMN is_regex INTEGER DEFAULT 0')
            conn.commit()
        except Exception:
            pass

    conn.close()


def add_word(word: str, is_regex: bool = False):
    conn = get_conn()
    c = conn.cursor()
    c.execute('INSERT INTO words (word, is_regex) VALUES(?, ?)', (word, 1 if is_regex else 0))
    conn.commit()
    conn.close()


def get_all_words():
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id, word, is_regex FROM words ORDER BY id DESC')
    rows = c.fetchall()
    conn.close()
    # return list of dicts
    return [{'id': r[0], 'word': r[1], 'is_regex': bool(r[2])} for r in rows]


def delete_word(id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('DELETE FROM words WHERE id = ?', (id,))
    conn.commit()
    conn.close()


def get_a_word_by_id(id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id, word, is_regex FROM words WHERE id = ?', (id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    return {'id': row[0], 'word': row[1], 'is_regex': bool(row[2])}
   
