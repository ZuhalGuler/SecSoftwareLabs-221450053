# signatures.py - Attack Signatures and Severity Definitions

# SQL Injection saldırı imzaları (normalize edilmiş küçük harf formatında)
SQLI_PATTERNS = [
    "or 1=1",
    "union select",
    "' or '1'='1",   # Eklenen özel imza 1: Tırnaklı boolean-based SQLi
    "drop table",    # Eklenen özel imza 2: Tablo silme komutu
    "--",            # Eklenen özel imza 3: SQL yorum satırı ile sorgu kesme
]

# Cross-Site Scripting (XSS) saldırı imzaları (normalize edilmiş küçük harf formatında)
XSS_PATTERNS = [
    "<script",
    "javascript:",
    "onerror=",      # Eklenen özel imza 1: Event handler tabanlı XSS
    "<img",          # Eklenen özel imza 2: Zararlı görsel etiketi enjeksiyonu
    "onload=",       # Eklenen özel imza 3: Yükleme olayı tabanlı XSS
]
