import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')

def init_db():
    # create users table if it does not exist
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, name TEXT NOT NULL)''')
    conn.commit()
    conn.close()

def add_user(name):
    # add a username 
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO users (name) VALUES (?)', (name,))
    conn.commit()
    conn.close()

def get_users():
    # return all users 
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, name FROM users')
    users = c.fetchall()
    conn.close()
    users.reverse()
    # return list of dicts with id and name keys
    return [{'id': u[0], 'name': u[1]} for u in users]