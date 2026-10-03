# HW 2 – JSON, Regex, CSV ve Veri Doğrulama (Python)

## 1. Ödevin Amacı
Bu ödevin amacı; JSONL (JSON Lines) formatındaki log kayıtlarını satır satır okumak, hatalı/bozuk satırlara karşı dayanıklı hata yönetimi (`try/except`) geliştirmek, Düzenli İfadeler (Regex) ile IPv4 adres geçerliliğini doğrulamak ve filtrelenen başarısız olayları CSV formatında dışa aktarmaktır.

## 2. Kullanılan Veri Seti
- **Dosya Yolu:** `datasets/events.jsonl`
- **Format:** Her satırda bir JSON nesnesi yer alır.
- **Alanlar:** `timestamp`, `event_id`, `source`, `src_ip`, `user`, `status`
- **Örnek Kayıt:**
  ```json
  {"timestamp": "2026-09-21T09:00:00", "event_id": 1, "source": "auth", "src_ip": "10.10.1.12", "user": "ali", "status": "FAILED"}
  ```

## 3. Programın Ne Yaptığı
1. `events.jsonl` dosyasını satır satır okur ve gereksiz boşlukları/boş satırları atlar.
2. Her satırı `json.loads()` ile parse eder. `THIS IS NOT JSON` gibi bozuk satırlar `json.JSONDecodeError` ile yakalanıp `"Geçersiz JSON satırı atlandı."` uyarısı verilerek atlanır.
3. Başarıyla ayrıştırılan geçerli JSON kayıtlarının toplam sayısını (`Total events`) hesaplar.
4. Yalnızca `status == "FAILED"` durumundaki olayları filtreler.
5. `src_ip` alanını IPv4 kuralına (0-255 aralığında 4 oktet) göre derlenmiş regex deseniyle `re.fullmatch` kullanarak kontrol eder; `"MERHABA"` gibi geçersiz veya eksik IP'ye sahip kayıtları eler.
6. Doğrulanan başarısız olayları `failed_events.csv` dosyasına `csv.DictWriter` ile yazar (`timestamp, event_id, src_ip, user, status`).
7. İstatistiksel sonuçları ve oluşturulan dosya bilgisini terminale yazdırır.

## 4. Programın Çalıştırılması
`homework2` klasörü içerisindeyken komut satırından aşağıdaki komut çalıştırılır:

```bash
python week03_regex_json.py
```

## 5. Gerçek Çıktı Örneği
```text
Total events: 35
Failed events: 16
CSV oluşturuldu: failed_events.csv
```
*(Not: Veri setinde bozuk JSON satırı olduğunda çıktı öncesinde `Geçersiz JSON satırı atlandı.` mesajı basılmaktadır.)*
