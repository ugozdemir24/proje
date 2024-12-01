import requests
import json

# API URL
base_url = 'http://localhost:5002/tablo'  # API URL'si

# Verileri eklemek için tablo adı ve veriler
data_dict = {
    'kullanici': {
        'kullanici_id': 232212,
        'kullanici_adi': 'john_doe',
        'email': 'addd.doe@example.com',
        'sifre_hash': 'hashed_password_123',
        'kayit_tarihi': '2024-11-30 10:00:00',
        'son_giris_tarihi': '2024-11-30 10:30:00'
    },
    'mesaj': {
        'mesaj_id': 1011,
        'gonderen_id': 1,
        'alici_id': 2,
        'icerik': 'Merhaba, nasılsın?'
    },
    'arama': {
        'arama_id': 110219,
        'baslatan_id': 1,
        'katilimci_id': 2,
        'baslangic_zamani': '2024-11-30 12:00:00',
        'bitis_zamani': '2024-11-30 13:00:00',
        'arama_durumu': 'Reddedildi'
    },
    'mesaj_arama_kaydi': {
        'kayit_id': 2313,
        'kullanici_id': 1,
        'mesaj_id': 122,
        'arama_id': 1,
        'kayit_tarihi': '2024-11-30 10:45:00'
    }
}

# Headers
headers = {
    'Content-Type': 'application/json'
}

# Veri gönderme fonksiyonu
def send_data_to_table(table_name, data):
    url = f'{base_url}/{table_name}'
    response = requests.post(url, data=json.dumps(data), headers=headers)

    # Yanıtı kontrol et
    if response.status_code == 201:
        print(f'{table_name} tablosuna veri başarıyla eklendi:', response.json())
    else:
        print(f'Hata oluştu {table_name} tablosunda:', response.status_code, response.json())

# Veri silme fonksiyonu
def delete_data_from_table(table_name, record_id):
    url = f'{base_url}/{table_name}/{record_id}'
    response = requests.delete(url)

    # Yanıtı kontrol et
    if response.status_code == 200:
        print(f'{table_name} tablosundaki {record_id} id\'li veri başarıyla silindi.')
    else:
        print(f'Hata oluştu {table_name} tablosunda veri silinirken:', response.status_code, response.json())

# Veri güncelleme fonksiyonu
def update_data_in_table(arama, 15, 10):
    url = f'{base_url}/{table_name}/{record_id}'
    response = requests.put(url, data=json.dumps(updated_data), headers=headers)

    # Yanıtı kontrol et
    if response.status_code == 200:
        print(f'{arama} tablosundaki {15} id\'li veri başarıyla güncellendi:', response.json())
    else:
        print(f'Hata oluştu {table_name} tablosunda veri güncellenirken:', response.status_code, response.json())

# Veri görüntüleme fonksiyonu
def get_data_from_table(table_name, record_id=None):
    if record_id:
        url = f'{base_url}/{table_name}/{record_id}'
    else:
        url = f'{base_url}/{table_name}'

    response = requests.get(url)

    # Yanıtı kontrol et
    if response.status_code == 200:
        print(f'{table_name} tablosundaki veriler başarıyla getirildi:', response.json())
    else:
        print(f'Hata oluştu {table_name} tablosundaki veriler getirilirken:', response.status_code, response.json())

# Test işlemleri
if __name__ == "__main__":
    # 1. Veri ekleme
    print("Veri ekleniyor...")
    for table_name, data in data_dict.items():
        send_data_to_table(table_name, data)

    # 2. Veri görüntüleme
    print("\nVeriler görüntüleniyor...")
    get_data_from_table('kullanici')
    get_data_from_table('mesaj')
    get_data_from_table('arama')
    get_data_from_table('mesaj_arama_kaydi')

    # 3. Veri güncelleme
    print("\nVeri güncelleniyor...")
    update_data_in_table('kullanici', 2312, {
        'kullanici_adi': 'john_doe_updated',
        'email': 'john.doe_updated@example.com'
    })

    # 4. Veri silme
    print("\nVeri siliniyor...")
    delete_data_from_table('kullanici', 2312)

    # 5. Son olarak, tekrar veri görüntüleme
    print("\nGüncel veriler görüntüleniyor...")
    get_data_from_table('kullanici')
    get_data_from_table('mesaj')
    get_data_from_table('arama')
    get_data_from_table('mesaj_arama_kaydi')
