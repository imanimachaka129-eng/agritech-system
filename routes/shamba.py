from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_db

shamba_bp = Blueprint('shamba', __name__)

def login_required():
    if 'mtumiaji_id' not in session:
        flash('Ingia kwanza!', 'hatari')
        return redirect(url_for('auth.login'))
    return None

@shamba_bp.route('/mashamba')
def mashamba():
    check = login_required()
    if check: return check

    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT m.*, COUNT(s.id) as idadi_sensorer
        FROM mashamba m
        LEFT JOIN sensorer s ON m.id = s.shamba_id
        GROUP BY m.id
        ORDER BY m.created_at DESC
    ''')
    mashamba_yote = cursor.fetchall()
    db.close()
    return render_template('mashamba.html', mashamba=mashamba_yote)


@shamba_bp.route('/mashamba/ongeza', methods=['GET', 'POST'])
def ongeza_shamba():
    check = login_required()
    if check: return check

    if request.method == 'POST':
        jina         = request.form['jina'].strip()
        eneo         = request.form['eneo'].strip()
        ukubwa_hekta = request.form['ukubwa_hekta']
        aina_mazao   = request.form['aina_mazao'].strip()
        tarehe       = request.form['tarehe_ilianzishwa']

        if not all([jina, eneo, ukubwa_hekta, aina_mazao, tarehe]):
            flash('Tafadhali jaza sehemu zote!', 'hatari')
            return redirect(url_for('shamba.ongeza_shamba'))

        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO mashamba (jina, eneo, ukubwa_hekta, aina_mazao, tarehe_ilianzishwa)
            VALUES (?, ?, ?, ?, ?)
        ''', (jina, eneo, float(ukubwa_hekta), aina_mazao, tarehe))
        db.commit()
        db.close()

        flash(f'Shamba "{jina}" limeongezwa! ✅', 'habari')
        return redirect(url_for('shamba.mashamba'))

    return render_template('ongeza_shamba.html')


@shamba_bp.route('/mashamba/hariri/<int:id>', methods=['GET', 'POST'])
def hariri_shamba(id):
    check = login_required()
    if check: return check

    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        jina         = request.form['jina'].strip()
        eneo         = request.form['eneo'].strip()
        ukubwa_hekta = request.form['ukubwa_hekta']
        aina_mazao   = request.form['aina_mazao'].strip()
        tarehe       = request.form['tarehe_ilianzishwa']

        if not all([jina, eneo, ukubwa_hekta, aina_mazao, tarehe]):
            flash('Tafadhali jaza sehemu zote!', 'hatari')
            return redirect(url_for('shamba.hariri_shamba', id=id))

        cursor.execute('''
            UPDATE mashamba
            SET jina=?, eneo=?, ukubwa_hekta=?, aina_mazao=?, tarehe_ilianzishwa=?
            WHERE id=?
        ''', (jina, eneo, float(ukubwa_hekta), aina_mazao, tarehe, id))
        db.commit()
        db.close()

        flash(f'Shamba "{jina}" limeboreshwa! ✅', 'habari')
        return redirect(url_for('shamba.mashamba'))

    cursor.execute('SELECT * FROM mashamba WHERE id = ?', (id,))
    shamba = cursor.fetchone()
    db.close()

    if not shamba:
        flash('Shamba halipatikani!', 'hatari')
        return redirect(url_for('shamba.mashamba'))

    return render_template('hariri_shamba.html', shamba=shamba)


@shamba_bp.route('/mashamba/futa/<int:id>', methods=['POST'])
def futa_shamba(id):
    check = login_required()
    if check: return check

    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT jina FROM mashamba WHERE id = ?', (id,))
    shamba = cursor.fetchone()

    if not shamba:
        flash('Shamba halipatikani!', 'hatari')
        db.close()
        return redirect(url_for('shamba.mashamba'))

    cursor.execute('DELETE FROM sensorer WHERE shamba_id = ?', (id,))
    cursor.execute('DELETE FROM mashamba WHERE id = ?', (id,))
    db.commit()
    db.close()

    flash(f'Shamba "{shamba["jina"]}" limefutwa!', 'onyo')
    return redirect(url_for('shamba.mashamba'))