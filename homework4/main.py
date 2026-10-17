# main.py - Mini WAF and Web Attack Detector Entry Point

import json
import os
import sys
from detector import detect_attack, evaluate_request


def load_requests(file_path):
    """JSON dosyasından HTTP istek listesini okur."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


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


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(base_dir, "test_requests.json")

    requests_data = load_requests(input_file)

    stats = {
        "total": 0,
        "allowed": 0,
        "blocked": 0,
        "sqli": 0,
        "xss": 0,
        "traversal": 0,
    }

    for item in requests_data:
        src_ip = item.get("src_ip", "UNKNOWN")
        url = item.get("url", "")

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

        print_request_result(src_ip, url, attack_label, severity, action)

    print_statistics(stats)


if __name__ == "__main__":
    main()
