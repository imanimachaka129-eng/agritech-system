import sqlite3
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, 'agrismart.db')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS watumiaji (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jina TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            token TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mashamba (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jina TEXT NOT NULL,
            eneo TEXT NOT NULL,
            ukubwa_hekta REAL NOT NULL,
            aina_mazao TEXT NOT NULL,
            tarehe_ilianzishwa TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensorer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shamba_id INTEGER NOT NULL,
            aina TEXT NOT NULL,
            thamani REAL NOT NULL,
            kipimo TEXT,
            hali TEXT DEFAULT 'nzuri',
            wakati TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (shamba_id) REFERENCES mashamba(id)
        )
    ''')

    cursor.execute("SELECT COUNT(*) FROM mashamba")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO mashamba (jina, eneo, ukubwa_hekta, aina_mazao, tarehe_ilianzishwa)
            VALUES (?, ?, ?, ?, ?)
        ''', [
            ('Shamba A', 'Mbeya Vijijini', 5.50, 'Mahindi', '2024-01-15'),
            ('Shamba B', 'Mbeya Mjini',   3.25, 'Mpunga',  '2024-03-01'),
            ('Shamba C', 'Uyole',          8.00, 'Viazi',   '2023-11-20'),
        ])
        cursor.executemany('''
            INSERT INTO sensorer (shamba_id, aina, thamani, kipimo, hali)
            VALUES (?, ?, ?, ?, ?)
        ''', [
            (1, 'unyevu', 68.0, '%',  'nzuri'),
            (1, 'joto',   24.5, '°C', 'nzuri'),
            (1, 'pH',      6.8, 'pH', 'nzuri'),
            (2, 'unyevu', 42.0, '%',  'tahadhari'),
            (2, 'joto',   31.0, '°C', 'tahadhari'),
            (3, 'unyevu', 18.0, '%',  'hatari'),
            (3, 'pH',      5.2, 'pH', 'tahadhari'),
        ])

    conn.commit()
    conn.close()