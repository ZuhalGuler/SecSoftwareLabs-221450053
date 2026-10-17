# HomeWork 4 – Mini WAF ve Web Attack Detector

## 1. Projenin Amacı
Bu projenin amacı; gelen HTTP isteklerini analiz ederek yaygın web saldırılarını (**SQL Injection**, **Cross-Site Scripting - XSS** ve **Path Traversal**) tespit eden, saldırının kritiklik seviyesini (**Severity**) belirleyen ve isteğe izin verilip verilmeyeceğine (**ALLOW / BLOCK**) karar veren basit bir **Web Application Firewall (WAF)** simülasyonu geliştirmektir.

Uygulama yalnızca Python 3 standart kütüphanelerini (`json`, `csv`, `urllib.parse`, `sys`, `os`) kullanır, URL encoding / çift encoding ile gizlenmiş saldırıları normalize ederek yakalar, hatalı/eksik veri tiplerine karşı çökmeden çalışır ve tespit edilen saldırıları `alerts.csv` dosyasına kaydeder.

---

## 2. Dosya Yapısı

`homework4/` klasörü içerisindeki dosyalar ve görevleri:

| Dosya Adı | Görevi |
|---|---|
| `main.py` | Uygulamanın giriş noktasıdır. JSON dosyasından HTTP isteklerini okur, hatalı kayıtları filtreler, her isteği analiz motoruna gönderir, sonuçları ekrana basar, saldırıları `alerts.csv` dosyasına yazar ve özet istatistikleri gösterir. |
| `normalizer.py` | `normalize(value)` fonksiyonunu içerir. Gelen URL'yi çok turlu URL decode (`urllib.parse.unquote`) işleminden geçirir, küçük harfe çevirir ve fazla boşlukları tek boşluğa indirir. |
| `signatures.py` | `SQLI_PATTERNS`, `XSS_PATTERNS`, `TRAVERSAL_PATTERNS` imza listelerini ve saldırı türlerine karşılık gelen `SEVERITY_MAP` önem derecesi sözlüğünü barındırır. |
| `detector.py` | `detect_sqli()`, `detect_xss()`, `detect_traversal()`, `detect_attack()` ve `evaluate_request()` fonksiyonları ile normalize edilmiş URL üzerinde imza kontrolü ve aksiyon (`ALLOW`/`BLOCK`) kararı verir. |
| `test_requests.json` | Normal istekler, açık/encode edilmiş SQLi, XSS, Path Traversal ve False Positive senaryolarını içeren 16 adet test isteği. |
| `test_invalid_requests.json` | Eksik `url`, eksik `src_ip`, boş URL ve geçersiz veri tiplerini (`int`, `None`, `list`, `str`) test etmek için kullanılan hatalı veri dosyası. |
| `test_broken.json` | Bozuk JSON söz문 (syntax) yapısına karşı programın çökmediğini doğrulayan test dosyası. |
| `alerts.csv` | Program çalıştığında sadece saldırı tespit edilen (`BLOCK`) isteklerin kaydedildiği CSV çıktı dosyası. |
| `README.md` | Proje dokümantasyonu, mimari açıklama, test senaryoları ve False Positive analizi. |

---

## 3. Çalıştırma

Harici hiçbir kütüphane kurulumu gerekmez. `homework4` dizini içerisinde aşağıdaki komutlarla çalıştırılabilir:

```bash
# Varsayılan test_requests.json ile çalıştırma
python main.py

# Hatalı veri yönetimi testi
python main.py test_invalid_requests.json

# Bozuk JSON formatı testi
python main.py test_broken.json
```

---

## 4. Detection (Tespit) Mantığı

Mini WAF motoru her HTTP isteğini aşağıdaki 6 aşamalı boru hattından (pipeline) geçirir:

```text
HTTP Request → URL Decode → Normalization → Signature Engine → Attack Detection → Severity → ALLOW / BLOCK
```

1. **HTTP Request:** JSON dosyasından `src_ip`, `method` ve `url` bilgileri okunur ve veri doğrulamasından (`validate_and_extract_request`) geçirilir.
2. **URL Decode:** Saldırganların filtreleri aşmak için kullandığı `%27` (`'`), `%20` (boşluk), `%3D` (`=`) veya çift encode edilmiş `%2527` gibi karakterler `urllib.parse.unquote` ile 3 tura kadar çözülür.
3. **Normalization:** Decode edilen URL tamamen küçük harfe (`lower()`) çevrilir, baş/son boşlukları silinir (`strip()`) ve ardışık çoklu boşluklar tek boşluğa (`" ".join(split())`) indirgenir. Böylece `"OR   1=1"` ile `"or 1=1"` aynı standart biçime dönüşür.
4. **Signature Engine:** Standartlaştırılmış URL, `signatures.py` içindeki küçük harfli saldırı imzalarıyla karşılaştırılır.
5. **Attack Detection:** Sırasıyla SQL Injection (`detect_sqli`), XSS (`detect_xss`) ve Path Traversal (`detect_traversal`) kontrolleri yapılır. Eşleşme varsa ilgili saldırı türü (`SQL_INJECTION`, `XSS`, `PATH_TRAVERSAL`), yoksa `None` döner.
6. **Severity & Action:** Saldırı türüne göre kritiklik seviyesi belirlenir (`HIGH` veya `MEDIUM`) ve saldırı varsa `BLOCK`, temiz ise `ALLOW` kararı üretilir. `BLOCK` edilen istekler `alerts.csv` dosyasına yazılır.

---

## 5. Kullanılan Signature'lar (İmzalar)

Tüm imzalar, normalizasyon aşamasından sonra tam eşleşebilmesi için küçük harfle tanımlanmıştır:

### SQL Injection (`SQLI_PATTERNS`)
- `"or 1=1"` *(Temel örnek)*
- `"union select"` *(Temel örnek)*
- `"' or '1'='1"` *(Kendim ekledim — Tırnaklı karakter/string tabanlı boolean SQLi)*
- `"drop table"` *(Kendim ekledim — Veritabanı tablosunu silmeye yönelik yıkıcı SQL komutu)*
- `"--"` *(Kendim ekledim — SQL sorgusunun geri kalanını yorum satırı yaparak devre dışı bırakma)*

### Cross-Site Scripting (`XSS_PATTERNS`)
- `"<script"` *(Temel örnek)*
- `"javascript:"` *(Temel örnek)*
- `"onerror="` *(Kendim ekledim — Hata olayı üzerinden JS çalıştıran event handler)*
- `"<img"` *(Kendim ekledim — Zararlı görsel etiketi enjeksiyonu)*
- `"onload="` *(Kendim ekledim — Sayfa/eleman yüklenirken otomatik tetiklenen event handler)*

### Path Traversal (`TRAVERSAL_PATTERNS`)
- `"../"` *(Temel örnek — Unix/Linux üst dizin geçişi)*
- `"..\\"` *(Temel örnek — Windows üst dizin geçişi)*
- `"/etc/passwd"` *(Kendim ekledim — Linux sistemlerde kullanıcı hesap bilgilerini barındıran kritik dosya)*
- `"%2e%2e"` *(Kendim ekledim — Nokta karakterlerinin URL-encode edilmiş hali)*
- `"..%2f"` *(Kendim ekledim — Slash karakterinin URL-encode edilmiş hibrit hali)*

---

## 6. Severity (Önem Derecesi) Seçimlerinin Gerekçesi

| Saldırı Türü | Severity | Gerekçe |
|---|---|---|
| **SQL_INJECTION** | `HIGH` | Doğrudan veritabanını hedef alır. Başarılı olması durumunda kimlik doğrulama aşılabilir (authentication bypass), tüm veritabanı sızdırılabilir, veriler değiştirilebilir veya silinebilir (`DROP TABLE`). |
| **XSS** | `HIGH` | Kurban kullanıcıların tarayıcısında zararlı JavaScript kodu çalıştırır. Oturum çerezlerinin (`document.cookie`) çalınmasına, hesap ele geçirilmesine (Account Takeover) ve kullanıcı adına yetkisiz işlem yapılmasına yol açar. |
| **PATH_TRAVERSAL** | `MEDIUM` | Sunucu dosya sistemindeki yetkisiz dosyaların okunmasına neden olur. Bilgi ifşası (Information Disclosure) açısından tehlikeli olsa da doğrudan veritabanı silme veya tam oturum çalma yerine genellikle okuma yetkisiyle sınırlı kaldığı için `MEDIUM` olarak sınıflandırılmıştır. |

---

## 7. Test Senaryoları ve Gerçek Program Çıktıları

### Senaryo 1: Normal İstek → ALLOW
Masum bir kullanıcı isteğinde hiçbir imza eşleşmez ve istek onaylanır:
```text
IP : 10.10.1.10
URL : /index.html
Attack : NONE
Severity : NONE
Action : ALLOW
```

### Senaryo 2: Açık SQL Injection → BLOCK / SQL_INJECTION
`or 1=1` ve `--` imzaları yakalanarak istek engellenir:
```text
IP : 10.10.1.20
URL : /products?id=1' OR 1=1--
Attack : SQL_INJECTION
Severity : HIGH
Action : BLOCK
```

### Senaryo 3: URL-Encoded ve Double-Encoded SQL Injection → BLOCK / SQL_INJECTION
`/products?id=1%27%20OR%201%3D1--` isteği decode edildiğinde `/products?id=1' or 1=1--` haline gelir ve açık SQLi isteğiyle **birebir aynı sonucu** verir. Ayrıca çift encode edilmiş (`%2527`) saldırı da başarıyla yakalanır:
```text
IP : 10.10.1.21
URL : /products?id=1%27%20OR%201%3D1--
Attack : SQL_INJECTION
Severity : HIGH
Action : BLOCK
---------------------------------------------
IP : 10.10.1.24
URL : /auth?user=admin%2527%2520or%2520%25271%2527%253D%25271
Attack : SQL_INJECTION
Severity : HIGH
Action : BLOCK
```

### Senaryo 4: XSS Saldırısı → BLOCK / XSS
`<script`, `<img` / `onerror=` ve `javascript:` vektörleri tespit edilerek engellenir:
```text
IP : 10.10.1.30
URL : /comment?text=<script>alert('XSS')</script>
Attack : XSS
Severity : HIGH
Action : BLOCK
```

### Senaryo 5: Path Traversal Saldırısı → BLOCK / PATH_TRAVERSAL
Hem Unix (`../` ve `/etc/passwd`), hem Windows (`..\`), hem de URL-encoded (`%2e%2e%2f`) dizin geçişleri yakalanır:
```text
IP : 10.10.1.35
URL : /download?file=../../../../etc/passwd
Attack : PATH_TRAVERSAL
Severity : MEDIUM
Action : BLOCK
```

### Senaryo 6: False-Positive Testi
Eğitim amaçlı yapılan masum bir arama sorgusu, içerdiği anahtar kelimeler nedeniyle imza motoruna takılır:
```text
IP : 10.10.1.99
URL : /search?q=SQL UNION SELECT tutorial
Attack : SQL_INJECTION
Severity : HIGH
Action : BLOCK
```

### Senaryo 7: Hatalı Veri ve Bozuk JSON Testi (`test_invalid_requests.json` & `test_broken.json`)
`python main.py test_invalid_requests.json` çalıştırıldığında program çökmez, eksik `src_ip` için `UNKNOWN` kullanır ve geçersiz kayıtları raporlayıp atlar:
```text
[WARNING] Kayıt #1 atlandı: 'url' alanı eksik -> {'src_ip': '10.10.1.40'}
IP : UNKNOWN
URL : /index.html
Attack : NONE
Severity : NONE
Action : ALLOW
---------------------------------------------
[WARNING] Kayıt #3 atlandı: 'url' alanı boş -> {'src_ip': '10.10.1.42', 'method': 'GET', 'url': ''}
[WARNING] Kayıt #4 atlandı: 'url' alanı boş -> {'src_ip': '10.10.1.43', 'method': 'GET', 'url': '   '}
[WARNING] Kayıt #5 atlandı: 'url' alanı string olmalı, 'int' bulundu -> {'src_ip': '10.10.1.44', 'method': 'POST', 'url': 12345}
[WARNING] Kayıt #6 atlandı: 'url' alanı string olmalı, 'NoneType' bulundu -> {'src_ip': '10.10.1.45', 'method': 'GET', 'url': None}
[WARNING] Kayıt #7 atlandı: 'url' alanı string olmalı, 'list' bulundu -> {'src_ip': '10.10.1.46', 'method': 'GET', 'url': ['/admin', '/login']}
[WARNING] Kayıt #8 atlandı: Sözlük (dict) bekleniyordu, 'str' bulundu.
[WARNING] Kayıt #9 atlandı: Sözlük (dict) bekleniyordu, 'int' bulundu.
[WARNING] Kayıt #10 atlandı: Sözlük (dict) bekleniyordu, 'NoneType' bulundu.
IP : UNKNOWN
URL : /products?id=1' OR 1=1--
Attack : SQL_INJECTION
Severity : HIGH
Action : BLOCK
---------------------------------------------

=== WAF ANALYSIS SUMMARY ===
Total Requests   : 2
Allowed          : 1
Blocked          : 1
SQL Injection    : 1
XSS              : 0
Path Traversal   : 0
Invalid/Skipped  : 9
```

Bozuk JSON (`python main.py test_broken.json`) çalıştırıldığında alınan çıktı:
```text
[ERROR] Geçersiz JSON formatı (C:\Users\ZUHAL\Desktop\homework4\homework4\test_broken.json): Expecting property name enclosed in double quotes: line 7 column 3 (char 80)
```

---

## 8. False Positive Analizi

Basit alt-dize (substring) eşleşmesine dayalı WAF sistemlerinde masum kullanıcı istekleri bazen saldırı olarak işaretlenebilir. Bu durum **False Positive (Yanlış Pozitif)** olarak adlandırılır.

### 1. Hangi request false positive oluşturdu?
`10.10.1.99` IP adresinden gönderilen şu arama isteği false positive oluşturmuştur:
```text
/search?q=SQL UNION SELECT tutorial
```
Kullanıcı burada veritabanına saldırı yapmak yerine arama çubuğunda *"SQL UNION SELECT tutorial"* (SQL UNION SELECT dersi/rehberi) araması yapmaktadır.

### 2. Hangi signature yakaladı?
İstek normalize edildiğinde `/search?q=sql union select tutorial` biçimine dönüşmüş ve `SQLI_PATTERNS` listesinde yer alan **`"union select"`** imzası tarafından yakalanmıştır.

### 3. Kuralı tamamen kaldırmadan nasıl azaltılabilir?
`"union select"` kuralını tamamen silmek gerçek SQL Injection saldırılarının kaçmasına (False Negative) yol açar. Bunun yerine şu yöntemlerle false positive oranı düşürülebilir:
- **Daha Spesifik Regex / Bağlam Kontrolü:** Sadece `"union select"` aramak yerine, gerçek bir SQL sorgusu yapısını doğrulayan `union\s+select\s+.+\s+from\s+` düzenli ifadesi (regex) kullanılabilir.
- **SQL Sözdizimi Karakterleriyle Birliktelik Arama:** Tek başına `"union select"` kelimesi yerine, aynı parametrede tek tırnak (`'`), noktalı virgül (`;`), yorum karakteri (`--`, `/*`) gibi SQL kontrol karakterlerinin de bulunup bulunmadığı kontrol edilebilir.
- **Skor (Anomaly Scoring) Tabanlı Yaklaşım (OWASP CRS Mantığı):** Her imza eşleşmesine bir risk puanı verilir (örn. `"union select"` = +3 puan, `'` = +2 puan, `--` = +2 puan). Sadece toplam puan eşik değeri (örn. 5) aşıldığında istek `BLOCK` edilir.
- **Endpoint / Parametre Bazlı Politika (Whitelist / Context-Aware):** `/search` gibi serbest metin araması yapılan endpoint'lerde `q` parametresinin SQL sorgusuna parametrik (Prepared Statement) olarak bağlandığı biliniyorsa, bu parametre için esnek kurallar uygulanırken `/products?id=` gibi sayısal beklenen parametrelerde sıkı kurallar uygulanabilir.

---

## 9. Örnek Program Çıktısı ve İstatistik (`python main.py`)

```text
IP : 10.10.1.10
URL : /index.html
Attack : NONE
Severity : NONE
Action : ALLOW
---------------------------------------------
IP : 10.10.1.11
URL : /products?category=laptops&page=2
Attack : NONE
Severity : NONE
Action : ALLOW
---------------------------------------------
IP : 10.10.1.12
URL : /api/v1/login
Attack : NONE
Severity : NONE
Action : ALLOW
---------------------------------------------
IP : 10.10.1.13
URL : /about-us
Attack : NONE
Severity : NONE
Action : ALLOW
---------------------------------------------
IP : 10.10.1.20
URL : /products?id=1' OR 1=1--
Attack : SQL_INJECTION
Severity : HIGH
Action : BLOCK
---------------------------------------------
IP : 10.10.1.21
URL : /products?id=1%27%20OR%201%3D1--
Attack : SQL_INJECTION
Severity : HIGH
Action : BLOCK
---------------------------------------------
IP : 10.10.1.22
URL : /items?id=5 UNION SELECT username,password FROM users
Attack : SQL_INJECTION
Severity : HIGH
Action : BLOCK
---------------------------------------------
IP : 10.10.1.23
URL : /admin/delete?query=1; DROP TABLE members--
Attack : SQL_INJECTION
Severity : HIGH
Action : BLOCK
---------------------------------------------
IP : 10.10.1.24
URL : /auth?user=admin%2527%2520or%2520%25271%2527%253D%25271
Attack : SQL_INJECTION
Severity : HIGH
Action : BLOCK
---------------------------------------------
IP : 10.10.1.30
URL : /comment?text=<script>alert('XSS')</script>
Attack : XSS
Severity : HIGH
Action : BLOCK
---------------------------------------------
IP : 10.10.1.31
URL : /profile?avatar=<img src=x onerror=alert(1)>
Attack : XSS
Severity : HIGH
Action : BLOCK
---------------------------------------------
IP : 10.10.1.32
URL : /redirect?url=javascript:alert(document.cookie)
Attack : XSS
Severity : HIGH
Action : BLOCK
---------------------------------------------
IP : 10.10.1.35
URL : /download?file=../../../../etc/passwd
Attack : PATH_TRAVERSAL
Severity : MEDIUM
Action : BLOCK
---------------------------------------------
IP : 10.10.1.36
URL : /view?doc=..\..\windows\win.ini
Attack : PATH_TRAVERSAL
Severity : MEDIUM
Action : BLOCK
---------------------------------------------
IP : 10.10.1.37
URL : /static?path=%2e%2e%2f%2e%2e%2fconfig.json
Attack : PATH_TRAVERSAL
Severity : MEDIUM
Action : BLOCK
---------------------------------------------
IP : 10.10.1.99
URL : /search?q=SQL UNION SELECT tutorial
Attack : SQL_INJECTION
Severity : HIGH
Action : BLOCK
---------------------------------------------

=== WAF ANALYSIS SUMMARY ===
Total Requests   : 16
Allowed          : 4
Blocked          : 12
SQL Injection    : 6
XSS              : 3
Path Traversal   : 3
Invalid/Skipped  : 0
```

Üretilen `alerts.csv` dosyasının içeriği:
```csv
src_ip,method,url,attack,severity,action
10.10.1.20,GET,/products?id=1' OR 1=1--,SQL_INJECTION,HIGH,BLOCK
10.10.1.21,GET,/products?id=1%27%20OR%201%3D1--,SQL_INJECTION,HIGH,BLOCK
10.10.1.22,GET,"/items?id=5 UNION SELECT username,password FROM users",SQL_INJECTION,HIGH,BLOCK
10.10.1.23,POST,/admin/delete?query=1; DROP TABLE members--,SQL_INJECTION,HIGH,BLOCK
10.10.1.24,GET,/auth?user=admin%2527%2520or%2520%25271%2527%253D%25271,SQL_INJECTION,HIGH,BLOCK
10.10.1.30,GET,/comment?text=<script>alert('XSS')</script>,XSS,HIGH,BLOCK
10.10.1.31,GET,/profile?avatar=<img src=x onerror=alert(1)>,XSS,HIGH,BLOCK
10.10.1.32,GET,/redirect?url=javascript:alert(document.cookie),XSS,HIGH,BLOCK
10.10.1.35,GET,/download?file=../../../../etc/passwd,PATH_TRAVERSAL,MEDIUM,BLOCK
10.10.1.36,GET,/view?doc=..\..\windows\win.ini,PATH_TRAVERSAL,MEDIUM,BLOCK
10.10.1.37,GET,/static?path=%2e%2e%2f%2e%2e%2fconfig.json,PATH_TRAVERSAL,MEDIUM,BLOCK
10.10.1.99,GET,/search?q=SQL UNION SELECT tutorial,SQL_INJECTION,HIGH,BLOCK
```
