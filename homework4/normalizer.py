

import urllib.parse


def normalize(value):
    """
    Gelen URL veya metin değerini güvenlik analizi öncesinde standartlaştırır.
    - None veya string olmayan girdilerde çökmez (boş string döndürür).
    - Encoding bypass girişimlerini (örn. çift encode %2527) yakalamak için
      birden fazla tur URL decode (urllib.parse.unquote) uygular.
    - Tüm karakterleri küçük harfe çevirir.
    - Baş/son boşlukları temizler ve ardışık çoklu boşlukları tek boşluğa indirir.
    """
    if value is None or not isinstance(value, str):
        return ""

    decoded = value
    # Çift veya çoklu URL encoding bypass girişimlerini çözmek için 3 tura kadar decode et
    for _ in range(3):
        unquoted = urllib.parse.unquote(decoded)
        if unquoted == decoded:
            break
        decoded = unquoted

    # Küçük harfe çevir ve çoklu boşlukları tek boşluğa indir (strip + split/join)
    normalized = " ".join(decoded.lower().strip().split())
    return normalized
