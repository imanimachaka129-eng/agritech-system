from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_db

sensor_bp = Blueprint('sensor', __name__)

def login_required():
    if 'mtumiaji_id' not in session:
        flash('Ingia kwanza!', 'hatari')
        return redirect(url_for('auth.login'))
    return None

@sensor_bp.route('/sensorer')
def sensorer():
    check = login_required()
    if check: return check

    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT s.*, m.jina as jina_shamba
        FROM sensorer s
        JOIN mashamba m ON s.shamba_id = m.id
        ORDER BY s.wakati DESC
    ''')
    sensorer_zote = cursor.fetchall()
    db.close()
    return render_template('sensorer.html', sensorer=sensorer_zote)


@sensor_bp.route('/sensorer/ongeza', methods=['GET', 'POST'])
def ongeza_sensor():
    check = login_required()
    if check: return check

    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        shamba_id = request.form['shamba_id']
        aina      = request.form['aina']
        thamani   = request.form['thamani']
        kipimo    = request.form['kipimo']
        hali      = request.form['hali']

        if not all([shamba_id, aina, thamani, kipimo, hali]):
            flash('Tafadhali jaza sehemu zote!', 'hatari')
            return redirect(url_for('sensor.ongeza_sensor'))

        cursor.execute('''
            INSERT INTO sensorer (shamba_id, aina, thamani, kipimo, hali)
            VALUES (?, ?, ?, ?, ?)
        ''', (int(shamba_id), aina, float(thamani), kipimo, hali))
        db.commit()
        db.close()

        flash('Sensor imeongezwa! ✅', 'habari')
        return redirect(url_for('sensor.sensorer'))

    cursor.execute('SELECT id, jina FROM mashamba ORDER BY jina')
    mashamba = cursor.fetchall()
    db.close()
    return render_template('ongeza_sensor.html', mashamba=mashamba)


@sensor_bp.route('/sensorer/hariri/<int:id>', methods=['GET', 'POST'])
def hariri_sensor(id):
    check = login_required()
    if check: return check

    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        shamba_id = request.form['shamba_id']
        aina      = request.form['aina']
        thamani   = request.form['thamani']
        kipimo    = request.form['kipimo']
        hali      = request.form['hali']

        if not all([shamba_id, aina, thamani, kipimo, hali]):
            flash('Tafadhali jaza sehemu zote!', 'hatari')
            return redirect(url_for('sensor.hariri_sensor', id=id))

        cursor.execute('''
            UPDATE sensorer
            SET shamba_id=?, aina=?, thamani=?, kipimo=?, hali=?
            WHERE id=?
        ''', (int(shamba_id), aina, float(thamani), kipimo, hali, id))
        db.commit()
        db.close()

        flash('Sensor imeboreshwa! ✅', 'habari')
        return redirect(url_for('sensor.sensorer'))

    cursor.execute('SELECT * FROM sensorer WHERE id = ?', (id,))
    sensor = cursor.fetchone()

    cursor.execute('SELECT id, jina FROM mashamba ORDER BY jina')
    mashamba = cursor.fetchall()
    db.close()

    if not sensor:
        flash('Sensor haipatikani!', 'hatari')
        return redirect(url_for('sensor.sensorer'))

    return render_template('hariri_sensor.html', sensor=sensor, mashamba=mashamba)


@sensor_bp.route('/sensorer/futa/<int:id>', methods=['POST'])
def futa_sensor(id):
    check = login_required()
    if check: return check

    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT aina FROM sensorer WHERE id = ?', (id,))
    sensor = cursor.fetchone()

    if not sensor:
        flash('Sensor haipatikani!', 'hatari')
        db.close()
        return redirect(url_for('sensor.sensorer'))

    cursor.execute('DELETE FROM sensorer WHERE id = ?', (id,))
    db.commit()
    db.close()

    flash(f'Sensor ya {sensor["aina"]} imefutwa!', 'onyo')
    return redirect(url_for('sensor.sensorer'))