# HomeWork 3 – Mini Security Event API

## 1. Ödevin Amacı
Bu ödevin amacı; Python'ın sadece standart kütüphanesini (`http.server`, `urllib`, `json`, `csv`, `socket`) kullanarak bir RESTful HTTP API sunucusu (`server.py`) ve bu API ile iletişim kuran bir istemci (`client.py`) geliştirmektir. Proje kapsamında istemci-sunucu mimarisi, HTTP durum kodları, JSON formatında veri alışverişi, veri filtreleme/hesaplama, CSV dışa aktarımı ve dayanıklı hata yönetimi (exception handling) pratik edilmiştir.

---

## 2. Kurulum ve Çalıştırma

Harici hiçbir üçüncü taraf paket (dependency) gerekmemektedir.

### Adım 1: Sunucunun Başlatılması (1. Terminal)
`homework3` klasöründe sunucuyu başlatmak için:
```bash
python server.py
```
*Sunucu `http://localhost:8000` üzerinde dinlemeye başlar.*

### Adım 2: İstemcinin Çalıştırılması (2. Terminal)
İkinci bir terminal açarak `homework3` klasörü içerisinden istemciyi çalıştırın:
```bash
# Varsayılan olarak /api/events endpoint'ine istek atar
python client.py

# İsteğe bağlı olarak farklı endpoint'leri test etmek için:
python client.py /api/abc
```

---

## 3. Kullanılan Endpointler

| HTTP Metodu | Endpoint Yolu | Açıklama | Başarılı Durum Kodu |
|---|---|---|---|
| `GET` | `/api/events` | Sistemdeki tüm güvenlik olaylarını JSON listesi olarak döner. | `200 OK` |
| `GET` | `/api/events/high` | Sadece `severity == "high"` olan güvenlik olaylarını döner. | `200 OK` |
| `GET` | `/api/summary` | Toplam olay ve önem seviyelerine (low, medium, high) göre sayıları dinamik hesaplayıp döner. | `200 OK` |
| `GET` / Diğer | `/*` (Tanımsız yollar) | Tanımlı olmayan yollar için `{"error": "Endpoint not found"}` yanıtı döner. | `404 Not Found` |

---

## 4. Gerçek Test Çıktıları ve Hata Senaryoları

### Test 1: Normal Akış (Sunucu Açık, Standart Çalışma)
Sunucu aktifken `python client.py` çalıştırıldığında alınan terminal çıktısı:

```text
API bağlantısı başarılı.
Toplam olay: 8
Severity dağılımı:
LOW    : 3
MEDIUM : 2
HIGH   : 3
HIGH SEVERITY EVENTS
ID: 2
Type: bruteforce
ID: 4
Type: sql-injection
ID: 7
Type: malware
```

Oluşturulan `high_events.csv` dosyasının içeriği:
```csv
id,severity,type
2,high,bruteforce
4,high,sql-injection
7,high,malware
```

Ayrıca `curl` test yanıtları:
- `curl http://localhost:8000/api/summary`
```json
{
  "total": 8,
  "low": 3,
  "medium": 2,
  "high": 3
}
```

---

### Test 2: Yanlış Endpoint Testi (404 Not Found)
Sunucu açıkken tanımlanmamış bir adrese istek atıldığında:

```bash
python client.py /api/abc
```
**Çıktı:**
```text
HTTP hatası: 404
```

`curl` ile doğrulama:
```bash
curl -i http://localhost:8000/api/abc
```
**Çıktı:**
```text
HTTP/1.0 404 Not Found
Content-Type: application/json; charset=utf-8

{
  "error": "Endpoint not found"
}
```

---

### Test 3: Sunucu Kapalı Senaryosu (Bağlantı Hatası)
Sunucu durdurulduktan sonra `python client.py` çalıştırıldığında programın traceback vermeden kontrollü sonlanması:

```bash
python client.py
```
**Çıktı:**
```text
API sunucusuna bağlanılamadı.
```

---

## 5. Kavramlar ve Kod ile İlişkisi

- **Client (İstemci):** Sunucuya istek gönderip yanıt bekleyen yazılımdır (`client.py`, `urllib.request` ile istek yapar).
- **Server (Sunucu):** Belirli bir portu dinleyerek gelen isteklere uygun yanıtı üreten yapıdır (`server.py`, `http.server.HTTPServer` ile 8000 portunu dinler).
- **Endpoint:** Sunucu üzerinde belirli bir veriye veya fonksiyona erişim sağlayan URL yoludur (örn: `/api/events`, `/api/summary`).
- **Status Code (Durum Kodu):** Sunucunun isteğin sonucunu bildirdiği 3 basamaklı koddur (`200 OK` başarıyı, `404 Not Found` kaynağın bulunamadığını ifade eder).
- **JSON (JavaScript Object Notation):** İstemci ve sunucu arasında veri taşımak için kullanılan hafif, metin tabanlı veri formatıdır (`json.dumps` ile üretilir, `json.loads` ile çözümlenir).
- **Timeout (Zaman Aşımı):** Sunucu yanıt vermediğinde istemcinin sonsuza kadar kilitlenip beklemesini önleyen süredir (`urllib.request.urlopen(..., timeout=5)`).
- **Hata Yönetimi (Error Handling):** Ağ kesintileri, geçersiz JSON veya 404 gibi beklenmeyen durumlarda programın çökmesini önleyip kullanıcıya anlaşılır mesaj sunma mekanizmasıdır (`try/except` blokları).
