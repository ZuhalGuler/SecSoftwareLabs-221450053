import http.server
import json
import sys

# Port ve Host ayarları
HOST = "localhost"
PORT = 8000

# Ödev gereksinimi: En az 8 güvenlik olayı 
# low, medium ve high severity tanımlı
SECURITY_EVENTS = [
    {"id": 1, "severity": "low", "type": "failed-login"},
    {"id": 2, "severity": "high", "type": "bruteforce"},
    {"id": 3, "severity": "medium", "type": "port-scan"},
    {"id": 4, "severity": "high", "type": "sql-injection"},
    {"id": 5, "severity": "low", "type": "suspicious-login"},
    {"id": 6, "severity": "medium", "type": "phishing"},
    {"id": 7, "severity": "high", "type": "malware"},
    {"id": 8, "severity": "low", "type": "failed-login"}
]


class SecurityEventHandler(http.server.BaseHTTPRequestHandler):
    """
    HTTP isteklerini karşılayan ve yönlendiren işleyici sınıfı.
    BaseHTTPRequestHandler sınıfından türetilmiştir.
    """

    def _send_json_response(self, status_code, data):
        """
        JSON formatında HTTP yanıtı ve başlıklarını gönderen yardımcı metot.
        Content-Type başlığı 'application/json; charset=utf-8' olarak ayarlanır.
        """
        response_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_GET(self):
        """
        Gelen HTTP GET isteklerini yönetir ve ilgili endpoint'e yönlendirir.
        """
        # URL yolunu normalize et 
        path = self.path.split("?")[0] 
        if path != "/" and path.endswith("/"):
            path = path[:-1]

        # 1. Endpoint: GET /api/events  Tüm olaylar
        if path == "/api/events":
            self._send_json_response(200, SECURITY_EVENTS)

        # 2. Endpoint: GET /api/events/high  Sadece severity == 'high' olanlar
        elif path == "/api/events/high":
            high_events = [e for e in SECURITY_EVENTS if e.get("severity") == "high"]
            self._send_json_response(200, high_events)

        # 3. Endpoint: GET /api/summary  Olayların dinamik istatistiksel özeti
        elif path == "/api/summary":
            # Değerler listeden dinamik olarak hesaplanır
            total = len(SECURITY_EVENTS)
            low_count = sum(1 for e in SECURITY_EVENTS if e.get("severity") == "low")
            medium_count = sum(1 for e in SECURITY_EVENTS if e.get("severity") == "medium")
            high_count = sum(1 for e in SECURITY_EVENTS if e.get("severity") == "high")

            summary_data = {
                "total": total,
                "low": low_count,
                "medium": medium_count,
                "high": high_count
            }
            self._send_json_response(200, summary_data)

        # Tanımsız endpointler için 404 döner
        else:
            self._send_json_response(404, {"error": "Endpoint not found"})

    def do_POST(self):
        """GET dışındaki istekler için de 404 / hata döner."""
        self._send_json_response(404, {"error": "Endpoint not found"})

    def do_PUT(self):
        self._send_json_response(404, {"error": "Endpoint not found"})

    def do_DELETE(self):
        self._send_json_response(404, {"error": "Endpoint not found"})

    def log_message(self, format, *args):
        """
        Gelen her isteği terminale formatlı şekilde loglar.
        """
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")


def run_server():
    """
    HTTP sunucusunu başlatır ve localhost:8000 adresinde dinlemeye alır.
    """
    server_address = (HOST, PORT)
    httpd = http.server.HTTPServer(server_address, SecurityEventHandler)
    print(f"Sunucu başlatıldı: http://{HOST}:{PORT}")
    print("Durdurmak için CTRL+C tuşlarına basabilirsiniz.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nSunucu kapatılıyor...")
    finally:
        httpd.server_close()
        print("Sunucu başarıyla kapatıldı.")


if __name__ == "__main__":
    run_server()
