import sqlite3


def init_db():
    conn = sqlite3.connect('poetry_contest.db')
    conn.execute('PRAGMA foreign_keys = ON')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS poets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        city TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS works (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        text TEXT,
        year INTEGER,
        poet_id INTEGER,
        FOREIGN KEY (poet_id) REFERENCES poets(id) ON DELETE CASCADE
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS performances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        poet_id INTEGER,
        theme TEXT,
        date TEXT,
        performance_order INTEGER,
        FOREIGN KEY (poet_id) REFERENCES poets(id) ON DELETE CASCADE
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS contests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        year INTEGER NOT NULL,
        theme TEXT,
        works_count INTEGER
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        year INTEGER NOT NULL,
        visitors INTEGER,
        participants INTEGER
    )''')

    conn.commit()
    conn.close()


def get_db_connection():
    conn = sqlite3.connect('poetry_contest.db')
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn