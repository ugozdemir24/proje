import requests

# API URL'sini belirleyin (Flask uygulamanızın çalıştığı yer)
API_URL = "http://localhost:5002/tablo/kullanici"

# Yeni kullanıcı verilerini hazırlayın
yeni_kullanici = {
    "kullanici_id": 134151,              # Benzersiz bir kullanıcı ID
    "kullanici_adi": "gece123",     # Kullanıcı adı
    "email": "gec343e@example.com",    # Kullanıcı e-posta adresi
    "sifre_hash": "hashedpassword", # Şifre (hashlenmiş hali)
    "kayit_tarihi": "2024-11-30",   # Kayıt tarihi (YYYY-MM-DD formatında)
    "son_giris_tarihi": None        # Son giriş tarihi (henüz giriş yapmadıysa None olabilir)
}

# API'ye POST isteği gönder
response = requests.post(API_URL, json=yeni_kullanici)

# API'den dönen yanıtı kontrol et
if response.status_code == 201:
    print("Yeni kullanıcı başarıyla eklendi:", response.json())
else:
    print("Kullanıcı eklenirken bir hata oluştu:", response.status_code, response.json())

