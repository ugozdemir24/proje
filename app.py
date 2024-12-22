from gevent import monkey
monkey.patch_all()

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import pymysql
import os
from pymysql.err import OperationalError
from werkzeug.security import generate_password_hash

app = Flask(__name__)
CORS(app)

app.template_folder = "templates"
socketio = SocketIO(app, async_mode='gevent')

valid_tables = {
    'kullanici': ['kullanici_id', 'kullanici_adi', 'email', 'sifre_hash', 'kayit_tarihi', 'son_giris_tarihi'],
    'mesaj': ['mesaj_id', 'gonderen_id', 'alici_id', 'icerik', 'gonderim_tarihi', 'teslim_durumu'],
    'arama': ['arama_id', 'baslatan_id', 'katilimci_id', 'baslangic_zamani', 'bitis_zamani', 'arama_durumu'],
    'mesaj_arama_kaydi': ['kayit_id', 'kullanici_id', 'mesaj_id', 'arama_id', 'kayit_tarihi']
}

@app.route('/')
def home():
    return render_template('giris.html')

@app.route('/kayit')
def kayit():
    return render_template('kayit.html')

def get_db_connection():
    try:
        connection = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'bil18a'),
            database=os.getenv('DB_NAME', 'msg18'),
            cursorclass=pymysql.cursors.DictCursor,
            charset='utf8mb4'
        )
        print("Veritabanı bağlantısı başarılı!")
        return connection
    except OperationalError as e:
        print(f"Veritabanına bağlanılamadı: {e}")
        return None

@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        kullanici_adi = data.get('kullanici_adi')
        email = data.get('email')
        sifre = data.get('sifre')

        hashed_sifre = generate_password_hash(sifre)

        sql = "INSERT INTO kullanici (kullanici_adi, email, sifre_hash) VALUES (%s, %s, %s)"
        connection = get_db_connection()
        if connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (kullanici_adi, email, hashed_sifre))
                connection.commit()
            return jsonify({'message': 'Kayıt başarılı!'}), 200
        else:
            return jsonify({'error': 'Veritabanı bağlantısı başarısız'}), 500
    except Exception as e:
        return jsonify({'error': f'Kayıt sırasında bir hata oluştu: {str(e)}'}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    sifre = data.get('sifre')

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                sql = "SELECT sifre_hash FROM kullanici WHERE email = %s"
                cursor.execute(sql, (email,))
                user = cursor.fetchone()

                if user and user['sifre_hash'] == sifre:  # Şifre doğrulama için burada hash kontrolü yapılabilir
                    return jsonify({"message": "Login başarılı!"}), 200
                else:
                    return jsonify({"error": "Email veya şifre hatalı!"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@socketio.on('connect')
def handle_connect():
    print("Bir kullanıcı bağlandı.")
    emit('response', {'message': 'Bağlantı başarılı!'})

@socketio.on('send_message')
def handle_message(data):
    gonderen_id = data['gonderen_id']
    alici_id = data['alici_id']
    icerik = data['icerik']

    sql = "INSERT INTO mesaj (gonderen_id, alici_id, icerik, gonderim_tarihi) VALUES (%s, %s, %s, NOW())"
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (gonderen_id, alici_id, icerik))
                connection.commit()

        emit('receive_message', {'gonderen_id': gonderen_id, 'alici_id': alici_id, 'icerik': icerik}, broadcast=True)
    except pymysql.Error as e:
        print(f"Veritabanı hatası: {e}")

@app.route('/mesajlar/<int:kullanici_id>', methods=['GET'])
def get_messages(kullanici_id):
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM mesaj WHERE gonderen_id = %s OR alici_id = %s ORDER BY gonderim_tarihi DESC"
                cursor.execute(sql, (kullanici_id, kullanici_id))
                messages = cursor.fetchall()
                return jsonify(messages), 200
    except pymysql.Error as e:
        return jsonify({'error': str(e)}), 400

@app.route('/tablo/<string:table_name>', methods=['GET'])
def get_table_data(table_name):
    if table_name not in valid_tables:
        return jsonify({'error': 'Geçersiz tablo adı'}), 400

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {table_name}")
                data = cursor.fetchall()
                return jsonify(data), 200
    except pymysql.Error as e:
        return jsonify({'error': str(e)}), 400

@app.route('/tablo/<string:table_name>/<int:id>', methods=['GET'])
def get_data_by_id(table_name, id):
    if table_name not in valid_tables:
        return jsonify({'error': 'Geçersiz tablo adı'}), 400

    id_column = valid_tables[table_name][0]
    sql = f"SELECT * FROM {table_name} WHERE {id_column} = %s"

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (id,))
                result = cursor.fetchone()
                if result:
                    return jsonify(result), 200
                else:
                    return jsonify({'error': 'Veri bulunamadı'}), 404
    except pymysql.Error as e:
        return jsonify({'error': str(e)}), 400

@app.route('/tablo/<string:table_name>/<int:id>', methods=['PUT'])
def update_data(table_name, id):
    if table_name not in valid_tables:
        return jsonify({'error': 'Geçersiz tablo adı'}), 400

    data = request.json
    set_clause = ', '.join([f"{key} = %s" for key in data])
    values = tuple(data[key] for key in data)

    id_column = valid_tables[table_name][0]
    sql = f"UPDATE {table_name} SET {set_clause} WHERE {id_column} = %s"

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (*values, id))
                connection.commit()
                return jsonify({'message': f'{table_name} tablosunda veri başarıyla güncellendi!'}), 200
    except pymysql.Error as e:
        return jsonify({'error': str(e)}), 400

@app.route('/tablo/<string:table_name>/<int:id>', methods=['DELETE'])
def delete_data(table_name, id):
    if table_name not in valid_tables:
        return jsonify({'error': 'Geçersiz tablo adı'}), 400

    id_column = valid_tables[table_name][0]
    sql = f"DELETE FROM {table_name} WHERE {id_column} = %s"

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (id,))
                connection.commit()
                return jsonify({'message': f'{table_name} tablosundan veri başarıyla silindi!'}), 200
    except pymysql.Error as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5005)




