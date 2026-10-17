# detector.py - Attack Detection Engine

from signatures import SQLI_PATTERNS


def detect_sqli(normalized_url):
    """Normalize edilmiş URL içinde SQL Injection imzalarını arar."""
    if not normalized_url or not isinstance(normalized_url, str):
        return False
    for pattern in SQLI_PATTERNS:
        if pattern in normalized_url:
            return True
    return False
