# detector.py - Attack Detection Engine

from normalizer import normalize
from signatures import SQLI_PATTERNS, XSS_PATTERNS, TRAVERSAL_PATTERNS, SEVERITY_MAP


def detect_sqli(normalized_url):
    """Normalize edilmiş URL içinde SQL Injection imzalarını arar."""
    if not normalized_url or not isinstance(normalized_url, str):
        return False
    for pattern in SQLI_PATTERNS:
        if pattern in normalized_url:
            return True
    return False


def detect_xss(normalized_url):
    """Normalize edilmiş URL içinde Cross-Site Scripting (XSS) imzalarını arar."""
    if not normalized_url or not isinstance(normalized_url, str):
        return False
    for pattern in XSS_PATTERNS:
        if pattern in normalized_url:
            return True
    return False


def detect_traversal(normalized_url):
    """Normalize edilmiş URL içinde Path Traversal imzalarını arar."""
    if not normalized_url or not isinstance(normalized_url, str):
        return False
    for pattern in TRAVERSAL_PATTERNS:
        if pattern in normalized_url:
            return True
    return False


def detect_attack(url):
    """
    URL'yi normalize edip sırasıyla SQLi, XSS ve Path Traversal kontrolü yapar.
    Saldırı tespit edilirse "SQL_INJECTION", "XSS" veya "PATH_TRAVERSAL" döndürür.
    Saldırı yoksa None döndürür.
    """
    normalized_url = normalize(url)
    if not normalized_url:
        return None

    if detect_sqli(normalized_url):
        return "SQL_INJECTION"
    if detect_xss(normalized_url):
        return "XSS"
    if detect_traversal(normalized_url):
        return "PATH_TRAVERSAL"

    return None


def evaluate_request(attack_type):
    """
    Tespit edilen saldırı türüne göre (attack_label, severity, action) üçlüsünü döndürür.
    Saldırı yoksa ("NONE", "NONE", "ALLOW"), varsa (attack_type, severity, "BLOCK") döner.
    """
    if attack_type is None:
        return "NONE", "NONE", "ALLOW"

    severity = SEVERITY_MAP.get(attack_type, "LOW")
    return attack_type, severity, "BLOCK"
