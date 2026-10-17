# main.py - Mini WAF and Web Attack Detector Entry Point

import csv
import json
import os
import sys
from detector import detect_attack, evaluate_request


def load_requests(file_path):
    """
    JSON dosyasından HTTP istek listesini güvenli bir şekilde okur.
    Dosya bulunamaması, geçersiz JSON formatı veya kök verinin liste olmaması
    durumlarında programı çökertmeden uyarı verir ve None döndürür.
    """
    if not os.path.exists(file_path):
        print(f"[ERROR] Dosya bulunamadı: {file_path}")
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Geçersiz JSON formatı ({file_path}): {e}")
        return None
    except OSError as e:
        print(f"[ERROR] Dosya okuma hatası ({file_path}): {e}")
        return None

    if not isinstance(data, list):
        print(f"[ERROR] Beklenmeyen JSON kök veri tipi: Liste bekleniyordu, {type(data).__name__} bulundu.")
        return None

    return data


def validate_and_extract_request(item, index):
    """
    Tek bir istek kaydını doğrular.
    - Kayıt bir dict değilse geçersiz sayılır.
    - 'url' alanı eksikse, None ise, string değilse veya boşluklardan ibaretse geçersiz sayılır.
    - 'src_ip' eksik veya geçersiz tip ise varsayılan 'UNKNOWN' atanır.
    - 'method' eksik veya geçersiz tip ise varsayılan 'GET' atanır.
    Geçerliyse (True, src_ip, method, url), geçersizse (False, None, None, None) döndürür.
    """
    if not isinstance(item, dict):
        print(f"[WARNING] Kayıt #{index} atlandı: Sözlük (dict) bekleniyordu, '{type(item).__name__}' bulundu.")
        return False, None, None, None

    if "url" not in item:
        print(f"[WARNING] Kayıt #{index} atlandı: 'url' alanı eksik -> {item}")
        return False, None, None, None

    raw_url = item["url"]
    if raw_url is None or not isinstance(raw_url, str):
        print(f"[WARNING] Kayıt #{index} atlandı: 'url' alanı string olmalı, '{type(raw_url).__name__}' bulundu -> {item}")
        return False, None, None, None

    if not raw_url.strip():
        print(f"[WARNING] Kayıt #{index} atlandı: 'url' alanı boş -> {item}")
        return False, None, None, None

    raw_ip = item.get("src_ip")
    if raw_ip is None or not isinstance(raw_ip, str) or not raw_ip.strip():
        src_ip = "UNKNOWN"
    else:
        src_ip = raw_ip.strip()

    raw_method = item.get("method")
    if raw_method is None or not isinstance(raw_method, str) or not raw_method.strip():
        method = "GET"
    else:
        method = raw_method.strip().upper()

    return True, src_ip, method, raw_url


def save_alerts_to_csv(alerts, output_path):
    """
    Sadece saldırı tespit edilen (BLOCK) istekleri alerts.csv dosyasına yazar.
    csv modülü sayesinde virgül veya tırnak içeren URL'ler güvenli biçimde kaçışlanır.
    """
    fieldnames = ["src_ip", "method", "url", "attack", "severity", "action"]
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for alert in alerts:
                writer.writerow(alert)
    except OSError as e:
        print(f"[ERROR] CSV dosyası yazılamadı ({output_path}): {e}")


def print_request_result(src_ip, url, attack_label, severity, action):
    """Tek bir HTTP isteğinin analiz sonucunu istenen formatta ekrana yazdırır."""
    print(f"IP : {src_ip}")
    print(f"URL : {url}")
    print(f"Attack : {attack_label}")
    print(f"Severity : {severity}")
    print(f"Action : {action}")
    print("-" * 45)


def print_statistics(stats):
    """Analiz sonunda özet istatistikleri ekrana yazdırır."""
    print("\n=== WAF ANALYSIS SUMMARY ===")
    print(f"Total Requests   : {stats['total']}")
    print(f"Allowed          : {stats['allowed']}")
    print(f"Blocked          : {stats['blocked']}")
    print(f"SQL Injection    : {stats['sqli']}")
    print(f"XSS              : {stats['xss']}")
    print(f"Path Traversal   : {stats['traversal']}")
    print(f"Invalid/Skipped  : {stats['invalid']}")


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) > 1:
        arg_path = sys.argv[1]
        input_file = arg_path if os.path.isabs(arg_path) else os.path.abspath(arg_path)
        if not os.path.exists(input_file):
            alt_path = os.path.join(base_dir, arg_path)
            if os.path.exists(alt_path):
                input_file = alt_path
    else:
        input_file = os.path.join(base_dir, "test_requests.json")

    alerts_file = os.path.join(base_dir, "alerts.csv")

    requests_data = load_requests(input_file)
    if requests_data is None:
        return

    stats = {
        "total": 0,
        "allowed": 0,
        "blocked": 0,
        "sqli": 0,
        "xss": 0,
        "traversal": 0,
        "invalid": 0,
    }
    alerts = []

    for idx, item in enumerate(requests_data, start=1):
        is_valid, src_ip, method, url = validate_and_extract_request(item, idx)
        if not is_valid:
            stats["invalid"] += 1
            continue

        attack_type = detect_attack(url)
        attack_label, severity, action = evaluate_request(attack_type)

        stats["total"] += 1
        if action == "ALLOW":
            stats["allowed"] += 1
        else:
            stats["blocked"] += 1
            if attack_type == "SQL_INJECTION":
                stats["sqli"] += 1
            elif attack_type == "XSS":
                stats["xss"] += 1
            elif attack_type == "PATH_TRAVERSAL":
                stats["traversal"] += 1

            alerts.append({
                "src_ip": src_ip,
                "method": method,
                "url": url,
                "attack": attack_label,
                "severity": severity,
                "action": action,
            })

        print_request_result(src_ip, url, attack_label, severity, action)

    # Sadece varsayılan test_requests.json çalıştırıldığında veya geçerli kayıt analiz edildiğinde CSV güncelle
    if os.path.basename(input_file) == "test_requests.json":
        save_alerts_to_csv(alerts, alerts_file)

    print_statistics(stats)


if __name__ == "__main__":
    main()
