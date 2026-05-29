import os
import psycopg2
from psycopg2.extras import RealDictCursor

# URL ya database
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://agrismart_db_n3cb_user:8roqXRECruaogQmtSuYX3ZdE7iGnOPoM@dpg-d8cjinugvqtc7387ejqg-a/agrismart_db_n3cb'
)

def get_db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS watumiaji (
            id SERIAL PRIMARY KEY,
            jina TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            token TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mashamba (
            id SERIAL PRIMARY KEY,
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
            id SERIAL PRIMARY KEY,
            shamba_id INTEGER NOT NULL,
            aina TEXT NOT NULL,
            thamani REAL NOT NULL,
            kipimo TEXT,
            hali TEXT DEFAULT 'nzuri',
            wakati TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (shamba_id) REFERENCES mashamba(id)
        )
    ''')

    # Data za mfano
    cursor.execute("SELECT COUNT(*) FROM mashamba")
    count = cursor.fetchone()['count']

    if count == 0:
        cursor.execute('''
            INSERT INTO mashamba (jina, eneo, ukubwa_hekta, aina_mazao, tarehe_ilianzishwa)
            VALUES
            ('Shamba A', 'Mbeya Vijijini', 5.50, 'Mahindi', '2024-01-15'),
            ('Shamba B', 'Mbeya Mjini', 3.25, 'Mpunga', '2024-03-01'),
            ('Shamba C', 'Uyole', 8.00, 'Viazi', '2023-11-20')
        ''')

        cursor.execute('''
            INSERT INTO sensorer (shamba_id, aina, thamani, kipimo, hali)
            VALUES
            (1, 'unyevu', 68.0, '%', 'nzuri'),
            (1, 'joto', 24.5, '°C', 'nzuri'),
            (1, 'pH', 6.8, 'pH', 'nzuri'),
            (2, 'unyevu', 42.0, '%', 'tahadhari'),
            (2, 'joto', 31.0, '°C', 'tahadhari'),
            (3, 'unyevu', 18.0, '%', 'hatari'),
            (3, 'pH', 5.2, 'pH', 'tahadhari')
        ''')

    conn.commit()
    conn.close()