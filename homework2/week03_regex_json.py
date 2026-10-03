import csv
import json
import re
from pathlib import Path

# Veri seti ve çıktı dosyası yollarının belirlenmesi
# datasets/ klasörü ana repo dizininde olduğu için parents[1] kullanılır
DATA = Path(__file__).parents[1] / "datasets" / "events.jsonl"
OUT = Path(__file__).parent / "failed_events.csv"

# IPv4 Oktet Deseni: Her bir oktetin 0-255 arasında olmasını sağlar
# 250-255 | 200-249 | 100-199 | 10-99 | 0-9
OCTET = r"(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)"
# 4 oktet ve aralarında nokta (.) olacak şekilde Regex derlenmesi
IP_RE = re.compile(rf"{OCTET}(?:\.{OCTET}){{3}}")

# CSV dosyasına yazılacak sütun başlıkları
FIELDS = ["timestamp", "event_id", "src_ip", "user", "status"]


def main():
    total_events = 0
    failed_events = []

    # events.jsonl dosyasının satır satır okunması
    with DATA.open(mode="r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Boş satırları atla
            if not line:
                continue

            # 1. JSON Parse ve Bozuk Satır Kontrolü (try/except)
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                # Bozuk veya geçersiz JSON satırlarında program çökmez, atlar
                print("Geçersiz JSON satırı atlandı.")
                continue

            # JSON nesnesinin sözlük (dict) formatında olduğunu doğrula
            if not isinstance(event, dict):
                continue

            # Başarıyla parse edilen geçerli olay sayısını artır
            total_events += 1

            # 2. Yalnızca status == "FAILED" olan olayları filtrele
            if event.get("status") != "FAILED":
                continue

            # 3. src_ip alanını Regex ile doğrula (0-255 aralığı ve fullmatch kontrolü)
            src_ip = event.get("src_ip")
            if not isinstance(src_ip, str) or not IP_RE.fullmatch(src_ip):
                # "MERHABA" gibi geçersiz IP'ye sahip kayıtlar elenir
                continue

            # 4. CSV için istenen alanları seç ve listeye ekle
            row = {field: event.get(field, "") for field in FIELDS}
            failed_events.append(row)

    # 5. Başarısız olayları CSV dosyasına yaz (newline="" parametresi ile)
    with OUT.open(mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(failed_events)

    # 6. İstatistik ve bilgilendirme çıktıları
    print(f"Total events: {total_events}")
    print(f"Failed events: {len(failed_events)}")
    print(f"CSV oluşturuldu: {OUT.name}")


if __name__ == "__main__":
    main()
