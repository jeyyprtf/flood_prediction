from flask import Flask, request, jsonify
import psycopg2
from datetime import datetime

app = Flask(__name__)

# Konfigurasi database PostgreSQL
DATABASE_URL = "postgresql://postgres.dbzhmxekapnbldetiawn:Juanmadhy425@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"

def get_db_connection():
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

# Variabel global untuk melacak status hujan
is_raining = False
start_time = None

@app.route('/send-data', methods=['POST'])
def send_data():
    global is_raining, start_time

    try:
        # Ambil data dari request
        data = request.json
        if not data or 'status' not in data:
            return jsonify({"error": "Invalid JSON data"}), 400

        status = data.get('status')  # 0 = tidak hujan, 1 = hujan

        # Validasi status
        if status not in [0, 1]:
            return jsonify({"error": "Invalid status. Must be 0 or 1."}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        if status == 1:  # Hujan dimulai
            if not is_raining:
                is_raining = True
                start_time = datetime.now().strftime('%H:%M:%S')  # Simpan waktu mulai dalam format HH:MM:SS
                print(f"Rain started at {start_time}")  # Debugging
                return jsonify({"message": "Rain started"}), 200
            else:
                return jsonify({"message": "Already raining"}), 200

        elif status == 0:  # Hujan berhenti
            if is_raining:
                end_time = datetime.now().strftime('%H:%M:%S')  # Simpan waktu selesai dalam format HH:MM:SS
                print(f"Rain stopped at {end_time}")  # Debugging

                # Hitung durasi hujan
                start_datetime = datetime.strptime(start_time, '%H:%M:%S')
                end_datetime = datetime.strptime(end_time, '%H:%M:%S')

                duration = end_datetime - start_datetime
                print(f"Calculated duration: {duration}")  # Debugging

                # Simpan data ke tabel rain_events
                cursor.execute(
                    "INSERT INTO rain_events (date, start_time, end_time, duration) VALUES (%s, %s, %s, %s)",
                    (datetime.now().date(), start_time, end_time, duration)
                )
                conn.commit()

                is_raining = False
                return jsonify({"message": "Rain stopped", "duration": str(duration)}), 200
            else:
                return jsonify({"message": "Not raining"}), 200

    except Exception as e:
        print(f"Error: {e}")  # Debugging
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
