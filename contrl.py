from flask import Flask, jsonify
import pymysql
from pymysql.err import OperationalError

app = Flask(__name__)



# MySQL Veritabanı Bağlantı Ayarları
def get_db_connection():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='ab',  # Kullanıcı adı
            password='sifre',  # Şifre
            database='msg18',  # Veritabanı adı
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except OperationalError as e:
        return None  # Hata durumunda None döndür


@app.route('/test-connection', methods=['GET'])
def test_connection():
    connection = get_db_connection()

    if connection is None:
        return jsonify({'error': 'Veritabanına bağlanılamadı.'}), 500
    else:
        connection.close()  # Bağlantıyı kapat
        return jsonify({'message': 'Veritabanı bağlantısı başarılı!'}), 200


if __name__ == '__main__':
    app.run(debug=True)




