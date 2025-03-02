from flask import Flask, request, jsonify
import psycopg2
from datetime import datetime

app = Flask(__name__)

# Konfigurasi database PostgreSQL
DATABASE_URL = "postgresql://postgres.dbzhmxekapnbldetiawn:Juanmadhy425@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("Database connection successful")  # Debugging
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

# Variabel global untuk melacak status hujan
is_raining = False
start_time = None

@app.route('/get-data', methods=['GET'])
def get_data():
    conn = None  # Pastikan conn terdefinisi di luar blok try-except

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Ambil data dari tabel rain_events
        cursor.execute("SELECT date, start_time, end_time, duration FROM rain_events ORDER BY date DESC")
        rows = cursor.fetchall()

        # Format data untuk response
        data_list = []
        for row in rows:
                data_list.append({
                    "date": str(row[0]),
                    "start_time": str(row[1]),
                    "end_time": str(row[2]),
                    "duration": str(row[3])
                })

        return jsonify(data_list), 200

    except Exception as e:
        print(f"Error: {e}")  # Debugging
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/send-data', methods=['POST'])
def send_data():
    global is_raining, start_time

    conn = None  # Pastikan conn terdefinisi di luar blok try-except

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
                start_time = datetime.now().strftime('%H:%M:%S')  # Simpan waktu mulai (HH:MM:SS)
                print(f"Rain started at {start_time}")  # Debugging
                return jsonify({"message": "Rain started"}), 200
            else:
                return jsonify({"message": "Already raining"}), 200

        elif status == 0:  # Hujan berhenti
            if is_raining:
                end_time = datetime.now().strftime('%H:%M:%S')  # Simpan waktu selesai (HH:MM:SS)
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
    # Validasi koneksi database saat startup
    try:
        startup_conn = get_db_connection()
        startup_conn.close()
        print("Startup DB connection check successful.")
    except Exception as e:
        print("Failed to connect to DB at startup. Exiting...")
        exit(1)

    # Jalankan Flask
    app.run(debug=True, port=1024, host='0.0.0.0')
