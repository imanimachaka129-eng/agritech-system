from flask import Blueprint, jsonify, request
from database import get_db
from werkzeug.security import check_password_hash, generate_password_hash
import functools
import secrets

api_bp = Blueprint('api', __name__, url_prefix='/api')

def token_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-API-Token')
        if not token:
            return jsonify({'status': 'error', 'ujumbe': 'Token inahitajika!'}), 401
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM watumiaji WHERE token = ?', (token,))
        mtumiaji = cursor.fetchone()
        db.close()
        if not mtumiaji:
            return jsonify({'status': 'error', 'ujumbe': 'Token si sahihi!'}), 403
        return f(mtumiaji, *args, **kwargs)
    return decorated


@api_bp.route('/auth/register', methods=['POST'])
def api_register():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'ujumbe': 'Data inahitajika (JSON)'}), 400

    jina     = data.get('jina', '').strip()
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not all([jina, email, password]):
        return jsonify({'status': 'error', 'ujumbe': 'Jaza jina, email, na password'}), 400

    if len(password) < 6:
        return jsonify({'status': 'error', 'ujumbe': 'Password iwe na herufi 6+'}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id FROM watumiaji WHERE email = ?', (email,))
    if cursor.fetchone():
        db.close()
        return jsonify({'status': 'error', 'ujumbe': 'Email tayari imesajiliwa'}), 409

    token  = secrets.token_hex(32)
    hashed = generate_password_hash(password)
    cursor.execute('''
        INSERT INTO watumiaji (jina, email, password, token)
        VALUES (?, ?, ?, ?)
    ''', (jina, email, hashed, token))
    db.commit()
    db.close()

    return jsonify({
        'status': 'ok',
        'ujumbe': 'Umesajiliwa!',
        'token': token,
        'jina': jina
    }), 201


@api_bp.route('/auth/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'ujumbe': 'Data inahitajika (JSON)'}), 400

    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not all([email, password]):
        return jsonify({'status': 'error', 'ujumbe': 'Jaza email na password'}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM watumiaji WHERE email = ?', (email,))
    mtumiaji = cursor.fetchone()
    db.close()

    if not mtumiaji or not check_password_hash(mtumiaji['password'], password):
        return jsonify({'status': 'error', 'ujumbe': 'Email au password si sahihi'}), 401

    return jsonify({
        'status': 'ok',
        'ujumbe': f'Karibu, {mtumiaji["jina"]}!',
        'token': mtumiaji['token'],
        'jina': mtumiaji['jina'],
        'id': mtumiaji['id']
    }), 200


@api_bp.route('/mashamba', methods=['GET'])
@token_required
def api_mashamba(mtumiaji):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT m.*, COUNT(s.id) as idadi_sensorer
        FROM mashamba m
        LEFT JOIN sensorer s ON m.id = s.shamba_id
        GROUP BY m.id
        ORDER BY m.created_at DESC
    ''')
    mashamba = [dict(r) for r in cursor.fetchall()]
    db.close()
    return jsonify({'status': 'ok', 'data': mashamba}), 200


@api_bp.route('/mashamba/<int:id>', methods=['GET'])
@token_required
def api_shamba_moja(mtumiaji, id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM mashamba WHERE id = ?', (id,))
    shamba = cursor.fetchone()
    db.close()
    if not shamba:
        return jsonify({'status': 'error', 'ujumbe': 'Shamba halipatikani'}), 404
    return jsonify({'status': 'ok', 'data': dict(shamba)}), 200


@api_bp.route('/mashamba', methods=['POST'])
@token_required
def api_ongeza_shamba(mtumiaji):
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'ujumbe': 'Data inahitajika (JSON)'}), 400

    jina         = data.get('jina', '').strip()
    eneo         = data.get('eneo', '').strip()
    ukubwa_hekta = data.get('ukubwa_hekta')
    aina_mazao   = data.get('aina_mazao', '').strip()
    tarehe       = data.get('tarehe_ilianzishwa', '').strip()

    if not all([jina, eneo, ukubwa_hekta, aina_mazao, tarehe]):
        return jsonify({'status': 'error', 'ujumbe': 'Jaza sehemu zote'}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO mashamba (jina, eneo, ukubwa_hekta, aina_mazao, tarehe_ilianzishwa)
        VALUES (?, ?, ?, ?, ?)
    ''', (jina, eneo, float(ukubwa_hekta), aina_mazao, tarehe))
    db.commit()
    new_id = cursor.lastrowid
    db.close()

    return jsonify({'status': 'ok', 'ujumbe': f'Shamba "{jina}" limeongezwa!', 'id': new_id}), 201


@api_bp.route('/mashamba/<int:id>', methods=['PUT'])
@token_required
def api_hariri_shamba(mtumiaji, id):
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'ujumbe': 'Data inahitajika (JSON)'}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM mashamba WHERE id = ?', (id,))
    shamba = cursor.fetchone()
    if not shamba:
        db.close()
        return jsonify({'status': 'error', 'ujumbe': 'Shamba halipatikani'}), 404

    jina         = data.get('jina', shamba['jina'])
    eneo         = data.get('eneo', shamba['eneo'])
    ukubwa_hekta = data.get('ukubwa_hekta', shamba['ukubwa_hekta'])
    aina_mazao   = data.get('aina_mazao', shamba['aina_mazao'])
    tarehe       = data.get('tarehe_ilianzishwa', shamba['tarehe_ilianzishwa'])

    cursor.execute('''
        UPDATE mashamba
        SET jina=?, eneo=?, ukubwa_hekta=?, aina_mazao=?, tarehe_ilianzishwa=?
        WHERE id=?
    ''', (jina, eneo, float(ukubwa_hekta), aina_mazao, tarehe, id))
    db.commit()
    db.close()
    return jsonify({'status': 'ok', 'ujumbe': f'Shamba "{jina}" limeboreshwa!'}), 200


@api_bp.route('/mashamba/<int:id>', methods=['DELETE'])
@token_required
def api_futa_shamba(mtumiaji, id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT jina FROM mashamba WHERE id = ?', (id,))
    shamba = cursor.fetchone()
    if not shamba:
        db.close()
        return jsonify({'status': 'error', 'ujumbe': 'Shamba halipatikani'}), 404

    cursor.execute('DELETE FROM sensorer WHERE shamba_id = ?', (id,))
    cursor.execute('DELETE FROM mashamba WHERE id = ?', (id,))
    db.commit()
    db.close()
    return jsonify({'status': 'ok', 'ujumbe': 'Shamba limefutwa!'}), 200


@api_bp.route('/sensorer', methods=['GET'])
@token_required
def api_sensorer(mtumiaji):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT s.*, m.jina as jina_shamba
        FROM sensorer s
        JOIN mashamba m ON s.shamba_id = m.id
        ORDER BY s.wakati DESC
    ''')
    sensorer = [dict(r) for r in cursor.fetchall()]
    db.close()
    return jsonify({'status': 'ok', 'data': sensorer}), 200


@api_bp.route('/sensorer/<int:id>', methods=['GET'])
@token_required
def api_sensor_moja(mtumiaji, id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT s.*, m.jina as jina_shamba
        FROM sensorer s
        JOIN mashamba m ON s.shamba_id = m.id
        WHERE s.id = ?
    ''', (id,))
    sensor = cursor.fetchone()
    db.close()
    if not sensor:
        return jsonify({'status': 'error', 'ujumbe': 'Sensor haipatikani'}), 404
    return jsonify({'status': 'ok', 'data': dict(sensor)}), 200


@api_bp.route('/sensorer', methods=['POST'])
@token_required
def api_ongeza_sensor(mtumiaji):
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'ujumbe': 'Data inahitajika (JSON)'}), 400

    shamba_id = data.get('shamba_id')
    aina      = data.get('aina', '').strip()
    thamani   = data.get('thamani')
    kipimo    = data.get('kipimo', '').strip()
    hali      = data.get('hali', 'nzuri')

    if not all([shamba_id, aina, thamani, kipimo]):
        return jsonify({'status': 'error', 'ujumbe': 'Jaza sehemu zote'}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO sensorer (shamba_id, aina, thamani, kipimo, hali)
        VALUES (?, ?, ?, ?, ?)
    ''', (int(shamba_id), aina, float(thamani), kipimo, hali))
    db.commit()
    new_id = cursor.lastrowid
    db.close()
    return jsonify({'status': 'ok', 'ujumbe': 'Sensor imeongezwa!', 'id': new_id}), 201


@api_bp.route('/sensorer/<int:id>', methods=['PUT'])
@token_required
def api_hariri_sensor(mtumiaji, id):
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'ujumbe': 'Data inahitajika (JSON)'}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM sensorer WHERE id = ?', (id,))
    sensor = cursor.fetchone()
    if not sensor:
        db.close()
        return jsonify({'status': 'error', 'ujumbe': 'Sensor haipatikani'}), 404

    shamba_id = data.get('shamba_id', sensor['shamba_id'])
    aina      = data.get('aina', sensor['aina'])
    thamani   = data.get('thamani', sensor['thamani'])
    kipimo    = data.get('kipimo', sensor['kipimo'])
    hali      = data.get('hali', sensor['hali'])

    cursor.execute('''
        UPDATE sensorer
        SET shamba_id=?, aina=?, thamani=?, kipimo=?, hali=?
        WHERE id=?
    ''', (int(shamba_id), aina, float(thamani), kipimo, hali, id))
    db.commit()
    db.close()
    return jsonify({'status': 'ok', 'ujumbe': 'Sensor imeboreshwa!'}), 200


@api_bp.route('/sensorer/<int:id>', methods=['DELETE'])
@token_required
def api_futa_sensor(mtumiaji, id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT aina FROM sensorer WHERE id = ?', (id,))
    sensor = cursor.fetchone()
    if not sensor:
        db.close()
        return jsonify({'status': 'error', 'ujumbe': 'Sensor haipatikani'}), 404

    cursor.execute('DELETE FROM sensorer WHERE id = ?', (id,))
    db.commit()
    db.close()
    return jsonify({'status': 'ok', 'ujumbe': 'Sensor imefutwa!'}), 200


@api_bp.route('/dashboard', methods=['GET'])
@token_required
def api_dashboard(mtumiaji):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT COUNT(*) as jumla FROM mashamba')
    jumla_mashamba = cursor.fetchone()['jumla']

    cursor.execute('SELECT COUNT(*) as jumla FROM sensorer')
    jumla_sensorer = cursor.fetchone()['jumla']

    cursor.execute("SELECT COUNT(*) as jumla FROM sensorer WHERE hali='hatari'")
    jumla_hatari = cursor.fetchone()['jumla']

    cursor.execute("SELECT COUNT(*) as jumla FROM sensorer WHERE hali='tahadhari'")
    jumla_tahadhari = cursor.fetchone()['jumla']

    db.close()
    return jsonify({
        'status': 'ok',
        'data': {
            'jumla_mashamba': jumla_mashamba,
            'jumla_sensorer': jumla_sensorer,
            'jumla_hatari': jumla_hatari,
            'jumla_tahadhari': jumla_tahadhari,
        }
    }), 200


# ════════════════════════════════════════════════════════
# IOT ENDPOINT — ESP32 inatuma data hapa
# ════════════════════════════════════════════════════════

# POST /api/iot/data
@api_bp.route('/iot/data', methods=['POST'])
def iot_data():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'ujumbe': 'Data inahitajika (JSON)'}), 400

    # Angalia API key ya device
    api_key = request.headers.get('X-Device-Key')
    if api_key != 'agrismart_device_2026':
        return jsonify({'status': 'error', 'ujumbe': 'Device key si sahihi!'}), 403

    shamba_id = data.get('shamba_id')
    sensorer  = data.get('sensorer', [])

    if not shamba_id or not sensorer:
        return jsonify({'status': 'error', 'ujumbe': 'shamba_id na sensorer zinahitajika'}), 400

    db = get_db()
    cursor = db.cursor()

    # Angalia shamba lipo
    cursor.execute('SELECT id FROM mashamba WHERE id = ?', (shamba_id,))
    if not cursor.fetchone():
        db.close()
        return jsonify({'status': 'error', 'ujumbe': 'Shamba halipatikani'}), 404

    # Hifadhi kila sensor
    zilizohifadhiwa = []
    for s in sensorer:
        aina    = s.get('aina', '').strip()
        thamani = s.get('thamani')
        kipimo  = s.get('kipimo', '').strip()

        # Amua hali kulingana na thamani
        hali = 'nzuri'
        if aina == 'unyevu':
            if thamani < 30:
                hali = 'hatari'
            elif thamani < 50:
                hali = 'tahadhari'
        elif aina == 'joto':
            if thamani > 35:
                hali = 'hatari'
            elif thamani > 30:
                hali = 'tahadhari'
        elif aina == 'pH':
            if thamani < 5.5 or thamani > 7.5:
                hali = 'hatari'
            elif thamani < 6.0 or thamani > 7.0:
                hali = 'tahadhari'

        cursor.execute('''
            INSERT INTO sensorer (shamba_id, aina, thamani, kipimo, hali)
            VALUES (?, ?, ?, ?, ?)
        ''', (int(shamba_id), aina, float(thamani), kipimo, hali))

        zilizohifadhiwa.append({
            'aina': aina,
            'thamani': thamani,
            'kipimo': kipimo,
            'hali': hali
        })

    db.commit()
    db.close()

    return jsonify({
        'status': 'ok',
        'ujumbe': f'Sensorer {len(zilizohifadhiwa)} zimehifadhiwa!',
        'data': zilizohifadhiwa
    }), 201