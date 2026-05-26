from flask import Blueprint, render_template, redirect, url_for, flash, session
from database import get_db

dashboard_bp = Blueprint('dashboard', __name__)

def login_required():
    if 'mtumiaji_id' not in session:
        flash('Ingia kwanza!', 'hatari')
        return redirect(url_for('auth.login'))
    return None

@dashboard_bp.route('/dashboard')
def dashboard():
    check = login_required()
    if check: return check

    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT COUNT(*) as jumla FROM mashamba')
    jumla_mashamba = cursor.fetchone()['jumla']

    cursor.execute('SELECT COUNT(*) as jumla FROM sensorer')
    jumla_sensorer = cursor.fetchone()['jumla']

    cursor.execute("SELECT COUNT(*) as jumla FROM sensorer WHERE hali = 'hatari'")
    jumla_hatari = cursor.fetchone()['jumla']

    cursor.execute("SELECT COUNT(*) as jumla FROM sensorer WHERE hali = 'tahadhari'")
    jumla_tahadhari = cursor.fetchone()['jumla']

    cursor.execute('''
        SELECT s.*, m.jina as jina_shamba
        FROM sensorer s
        JOIN mashamba m ON s.shamba_id = m.id
        ORDER BY s.wakati DESC
        LIMIT 5
    ''')
    sensorer_karibuni = cursor.fetchall()

    cursor.execute('''
        SELECT hali, COUNT(*) as idadi
        FROM sensorer
        GROUP BY hali
    ''')
    hali_data = cursor.fetchall()

    cursor.execute('''
        SELECT aina, COUNT(*) as idadi
        FROM sensorer
        GROUP BY aina
    ''')
    aina_data = cursor.fetchall()

    cursor.execute('''
        SELECT m.jina,
               COUNT(s.id) as idadi_sensorer,
               SUM(CASE WHEN s.hali = 'hatari' THEN 1 ELSE 0 END) as hatari,
               SUM(CASE WHEN s.hali = 'tahadhari' THEN 1 ELSE 0 END) as tahadhari
        FROM mashamba m
        LEFT JOIN sensorer s ON m.id = s.shamba_id
        GROUP BY m.id
        ORDER BY m.created_at DESC
    ''')
    mashamba_hali = cursor.fetchall()

    db.close()

    return render_template('dashboard.html',
        jumla_mashamba=jumla_mashamba,
        jumla_sensorer=jumla_sensorer,
        jumla_hatari=jumla_hatari,
        jumla_tahadhari=jumla_tahadhari,
        sensorer_karibuni=sensorer_karibuni,
        hali_data=[dict(r) for r in hali_data],
        aina_data=[dict(r) for r in aina_data],
        mashamba_hali=mashamba_hali,
    )