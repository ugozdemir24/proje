from flask import Flask, request, jsonify
import pymysql
from pymysql.err import OperationalError
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# MySQL Veritabanı Bağlantı Ayarları
def get_db_connection():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='bil18a',
            database='msg18',
            cursorclass=pymysql.cursors.DictCursor,
            charset='utf8mb4'
        )
        print("Veritabanı bağlantısı başarılı!")
        return connection
    except OperationalError as e:
        print(f"Veritabanına bağlanılamadı: {e}")
        return None

# Tabloların tanımı
valid_tables = {
    'kullanici': ['kullanici_id', 'kullanici_adi', 'email', 'sifre_hash', 'kayit_tarihi', 'son_giris_tarihi'],
    'mesaj': ['mesaj_id', 'gonderen_id', 'alici_id', 'icerik', 'gonderim_tarihi', 'teslim_durumu'],
    'arama': ['arama_id', 'baslatan_id', 'katilimci_id', 'baslangic_zamani', 'bitis_zamani', 'arama_durumu'],
    'mesaj_arama_kaydi': ['kayit_id', 'kullanici_id', 'mesaj_id', 'arama_id', 'kayit_tarihi']  # Tabloyu buraya ekleyin
}

# Tabloya göre veriyi almak
@app.route('/tablo/<string:table_name>', methods=['GET'])
def get_table_data(table_name):
    if table_name not in valid_tables:
        return jsonify({'error': 'Geçersiz tablo adı'}), 400

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute(f"SELECT * FROM {table_name}")
                data = cursor.fetchall()
                return jsonify(data), 200
            except pymysql.Error as e:
                return jsonify({'error': str(e)}), 400

# ID'ye göre veriyi almak
@app.route('/tablo/<string:table_name>/<int:id>', methods=['GET'])
def get_data_by_id(table_name, id):
    table_columns = {
        'kullanici': 'kullanici_id',
        'mesaj': 'mesaj_id',
        'arama': 'arama_id',
        'mesaj_arama_kaydi': 'kayit_id'  # Buraya ekledik
    }

    if table_name not in table_columns:
        return jsonify({'error': 'Geçersiz tablo adı'}), 400

    id_column = table_columns[table_name]
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

# Veriyi güncelle
@app.route('/tablo/<string:table_name>/<int:id>', methods=['PUT'])
def update_data(table_name, id):
    table_columns = {
        'kullanici': 'kullanici_id',
        'mesaj': 'mesaj_id',
        'arama': 'arama_id',
        'mesaj_arama_kaydi': 'kayit_id'  # Buraya ekledik
    }

    if table_name not in table_columns:
        return jsonify({'error': 'Geçersiz tablo adı'}), 400

    data = request.json  # JSON formatında veri alıyoruz

    # Güncellenmesi gereken alanları oluşturuyoruz
    set_clause = ', '.join([f"{key} = %s" for key in data])
    values = tuple(data[key] for key in data)

    # Dinamik olarak WHERE koşulunu belirliyoruz
    id_column = table_columns[table_name]

    # SQL sorgusunu oluşturuyoruz
    sql = f"UPDATE {table_name} SET {set_clause} WHERE {id_column} = %s"

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (*values, id))
                connection.commit()
                return jsonify({'message': f'{table_name} tablosunda veri başarıyla güncellendi!'}), 200
    except pymysql.Error as e:
        return jsonify({'error': str(e)}), 400

# Veriyi sil
@app.route('/tablo/<string:table_name>/<int:id>', methods=['DELETE'])
def delete_data(table_name, id):
    table_columns = {
        'kullanici': 'kullanici_id',
        'mesaj': 'mesaj_id',
        'arama': 'arama_id',
        'mesaj_arama_kaydi': 'kayit_id'  # Buraya ekledik
    }

    if table_name not in table_columns:
        return jsonify({'error': 'Geçersiz tablo adı'}), 400

    id_column = table_columns[table_name]

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
    app.run(host="0.0.0.0", port=5002, debug=True)
