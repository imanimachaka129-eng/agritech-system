# simulator.py

import requests
import random
import time
from datetime import datetime
from database import get_db  # ← import moja kwa moja

FLASK_URL  = 'http://127.0.0.1:5000'
DEVICE_KEY = 'agrismart_device_2026'

HEADERS = {
    'Content-Type': 'application/json',
    'X-Device-Key': DEVICE_KEY
}

# ── Pata mashamba na sensorer zao kutoka database ────────
def pata_mashamba_na_sensorer():
    try:
        db = get_db()
        cursor = db.cursor()

        # Pata mashamba yote
        cursor.execute('SELECT id, jina FROM mashamba ORDER BY id')
        mashamba = cursor.fetchall()

        result = []
        for shamba in mashamba:
            # Pata aina za sensorer za shamba hilo
            cursor.execute('''
                SELECT DISTINCT aina, kipimo
                FROM sensorer
                WHERE shamba_id = ?
            ''', (shamba['id'],))
            sensorer = cursor.fetchall()

            result.append({
                'id': shamba['id'],
                'jina': shamba['jina'],
                'sensorer': [{'aina': s['aina'], 'kipimo': s['kipimo']} for s in sensorer]
            })

        db.close()
        return result

    except Exception as e:
        print(f"❌ Kosa la database: {e}")
        return []


# ── Thamani za random kwa kila aina ─────────────────────
def thamani_ya_aina(aina):
    aina = aina.lower()
    if 'unyevu' in aina or 'moisture' in aina:
        return round(random.uniform(20.0, 90.0), 1)
    elif 'joto' in aina or 'temp' in aina:
        return round(random.uniform(18.0, 38.0), 1)
    elif 'ph' in aina:
        return round(random.uniform(4.5, 8.5), 2)
    elif 'npk' in aina:
        return round(random.uniform(10.0, 60.0), 1)
    else:
        return round(random.uniform(10.0, 100.0), 1)


# ── Tuma data kwa shamba moja ────────────────────────────
def tuma_data(shamba):
    wakati = datetime.now().strftime('%H:%M:%S')

    if not shamba['sensorer']:
        print(f"\n[{wakati}] ⚠️  {shamba['jina']} — Haina sensorer!")
        return

    # Unda payload kutoka sensorer zilizopo
    sensorer_payload = []
    for s in shamba['sensorer']:
        sensorer_payload.append({
            'aina': s['aina'],
            'thamani': thamani_ya_aina(s['aina']),
            'kipimo': s['kipimo'] or '%'
        })

    payload = {
        'shamba_id': shamba['id'],
        'sensorer': sensorer_payload
    }

    try:
        response = requests.post(
            f'{FLASK_URL}/api/iot/data',
            json=payload,
            headers=HEADERS,
            timeout=5
        )
        data = response.json()

        print(f"\n[{wakati}] 📡 {shamba['jina']} (ID:{shamba['id']})")
        print(f"{'─'*45}")

        for s in data.get('data', []):
            hali_icon = {
                'nzuri': '✅',
                'tahadhari': '⚠️',
                'hatari': '🔴'
            }.get(s['hali'], '❓')
            print(f"  {hali_icon} {s['aina']:<15} {s['thamani']} {s['kipimo']:<8} [{s['hali']}]")

        print(f"{'─'*45}")

    except requests.exceptions.ConnectionError:
        print(f"\n[{wakati}] ❌ Imeshindwa kuunganika!")
    except Exception as e:
        print(f"\n[{wakati}] ❌ Kosa: {e}")


# ── Main loop ────────────────────────────────────────────
def main():
    print("=" * 45)
    print("  🌱 AgriSmart ESP32 Simulator")
    print("  Inasoma mashamba na sensorer")
    print("  kutoka database moja kwa moja!")
    print("  Ctrl+C kusimama")
    print("=" * 45)

    interval = 10

    while True:
        # Soma mashamba na sensorer kutoka database
        mashamba = pata_mashamba_na_sensorer()

        if not mashamba:
            print("\n❌ Hakuna mashamba — ongeza shamba kwanza!")
            time.sleep(5)
            continue

        print(f"\n🌾 Mashamba {len(mashamba)} yanahudumiwa...")

        for shamba in mashamba:
            tuma_data(shamba)
            time.sleep(1)

        print(f"\n⏳ Kusubiri sekunde {interval}...")
        time.sleep(interval)


if __name__ == '__main__':
    main()