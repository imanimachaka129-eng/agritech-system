import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db

auth_bp = Blueprint('auth', __name__)

# ── Email Validation ─────────────────────────────────────
def email_sahihi(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def domain_sahihi(email):
    domains_halisi = [
        'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com',
        'icloud.com', 'live.com', 'msn.com', 'me.com',
        'protonmail.com', 'mail.com', 'ymail.com',
        'go.tz', 'ac.tz', 'co.tz', 'or.tz', 'ne.tz'
    ]
    domain = email.split('@')[1].lower()
    return domain in domains_halisi


# ── Register ─────────────────────────────────────────────
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        jina     = request.form['jina'].strip()
        email    = request.form['email'].strip().lower()
        password = request.form['password']
        confirm  = request.form['confirm']

        # Validate — fields zote
        if not all([jina, email, password, confirm]):
            flash('Jaza sehemu zote!', 'hatari')
            return redirect(url_for('auth.register'))

        # Validate — email muundo
        if not email_sahihi(email):
            flash('Muundo wa email si sahihi! mf. jina@gmail.com', 'hatari')
            return redirect(url_for('auth.register'))

        # Validate — email domain
        if not domain_sahihi(email):
            flash('Tumia email halisi! mf. Gmail, Yahoo, Outlook', 'hatari')
            return redirect(url_for('auth.register'))

        # Validate — nywila
        if password != confirm:
            flash('Nywila hazifanani!', 'hatari')
            return redirect(url_for('auth.register'))

        if len(password) < 6:
            flash('Nywila iwe na herufi 6 au zaidi!', 'hatari')
            return redirect(url_for('auth.register'))

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id FROM watumiaji WHERE email = ?', (email,))
        existing = cursor.fetchone()

        if existing:
            flash('Email hii tayari imesajiliwa!', 'hatari')
            db.close()
            return redirect(url_for('auth.register'))

        hashed = generate_password_hash(password)
        cursor.execute('''
            INSERT INTO watumiaji (jina, email, password)
            VALUES (?, ?, ?)
        ''', (jina, email, hashed))
        db.commit()
        db.close()

        flash('Umesajiliwa! Ingia sasa. ✅', 'habari')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


# ── Login ─────────────────────────────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email'].strip().lower()
        password = request.form['password']

        if not all([email, password]):
            flash('Jaza email na nywila!', 'hatari')
            return redirect(url_for('auth.login'))

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM watumiaji WHERE email = ?', (email,))
        mtumiaji = cursor.fetchone()
        db.close()

        if not mtumiaji or not check_password_hash(mtumiaji['password'], password):
            flash('Email au nywila si sahihi!', 'hatari')
            return redirect(url_for('auth.login'))

        session['mtumiaji_id']   = mtumiaji['id']
        session['mtumiaji_jina'] = mtumiaji['jina']

        flash(f'Karibu, {mtumiaji["jina"]}! 👋', 'habari')
        return redirect(url_for('dashboard.dashboard'))

    return render_template('login.html')


# ── Logout ───────────────────────────────────────────────
@auth_bp.route('/logout')
def logout():
    jina = session.get('mtumiaji_jina', '')
    session.clear()
    flash(f'Umefanya logout. Kwa heri, {jina}!', 'onyo')
    return redirect(url_for('auth.login'))