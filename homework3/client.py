import csv
import json
import os
import socket
import sys
import urllib.error
import urllib.request

# Varsayılan sunucu adresi ve varsayılan endpoint
DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_ENDPOINT = "/api/events"


def fetch_and_process_events(endpoint_or_url=DEFAULT_ENDPOINT):
    """
    Sunucudan güvenlik olaylarını çeker, analiz eder, high severity olanları
    CSV dosyasına kaydeder ve sonuçları terminale yazdırır.
    """
    # URL oluşturma: Parametre doğrudan tam URL değilse base_url ile birleştir
    if endpoint_or_url.startswith("http://") or endpoint_or_url.startswith("https://"):
        target_url = endpoint_or_url
    else:
        # Başında / yoksa ekle
        path = endpoint_or_url if endpoint_or_url.startswith("/") else f"/{endpoint_or_url}"
        target_url = f"{DEFAULT_BASE_URL}{path}"

    try:
        # 1. HTTP GET İsteği: timeout=5 ile sunucu yanıt vermezse kilitlenmeyi önler
        req = urllib.request.Request(target_url, headers={"User-Agent": "SecurityEventClient/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            status_code = response.getcode()
            response_body = response.read().decode("utf-8")

        # 2. JSON Ayrıştırma: Metin tabanlı JSON verisini Python listesine/sözlüğüne çevirir
        try:
            data = json.loads(response_body)
        except json.JSONDecodeError:
            print("JSON ayrıştırma hatası: Sunucudan dönen yanıt geçerli bir JSON formatında değil.")
            return

        print("API bağlantısı başarılı.")

        # Eğer endpoint /api/events gibi bir liste döndürdüyse analiz et
        if isinstance(data, list):
            total_events = len(data)
            low_count = sum(1 for e in data if isinstance(e, dict) and e.get("severity") == "low")
            medium_count = sum(1 for e in data if isinstance(e, dict) and e.get("severity") == "medium")
            high_count = sum(1 for e in data if isinstance(e, dict) and e.get("severity") == "high")

            print(f"Toplam olay: {total_events}")
            print("Severity dağılımı:")
            print(f"LOW    : {low_count}")
            print(f"MEDIUM : {medium_count}")
            print(f"HIGH   : {high_count}")
            print("HIGH SEVERITY EVENTS")

            # High severity olayları filtrele
            high_events = [e for e in data if isinstance(e, dict) and e.get("severity") == "high"]
            for event in high_events:
                print(f"ID: {event.get('id')}")
                print(f"Type: {event.get('type')}")

            # 3. CSV Kaydı: high_events.csv dosyasını client.py'nin bulunduğu klasöre kaydet
            script_dir = os.path.dirname(os.path.abspath(__file__))
            csv_path = os.path.join(script_dir, "high_events.csv")

            with open(csv_path, mode="w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["id", "severity", "type"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for event in high_events:
                    writer.writerow({
                        "id": event.get("id"),
                        "severity": event.get("severity"),
                        "type": event.get("type")
                    })
        elif isinstance(data, dict):
            # Sözlük tipinde bir yanıt geldiyse (örn: /api/summary veya hata mesajı)
            print("Alınan Yanıt:")
            print(json.dumps(data, indent=2, ensure_ascii=False))

    # Hata Yönetimi
    except urllib.error.HTTPError as e:
        # HTTP 404, 500 vb. durum kodları sunucu tarafından döndüğünde yakalanır
        print(f"HTTP hatası: {e.code}")
    except (urllib.error.URLError, ConnectionRefusedError, socket.timeout, TimeoutError):
        # Sunucu kapalıyken veya ağ/zaman aşımı problemleri olduğunda yakalanır
        print("API sunucusuna bağlanılamadı.")
    except Exception as e:
        # Diğer beklenmeyen hatalar için programın çökmesini engeller
        print(f"Beklenmeyen bir hata oluştu: {e}")


if __name__ == "__main__":
    # Komut satırı argümanı kontrolü (varsayılan: /api/events)
    # Örnek kullanım: python client.py /api/abc
    endpoint = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ENDPOINT
    fetch_and_process_events(endpoint)
