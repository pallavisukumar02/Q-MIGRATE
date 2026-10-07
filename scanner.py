import re

PATTERNS = {
    "RSA": (r"\bRSA\b|rsa\.|RSA2?\d*", "Public-key"),
    "ECC/ECDSA": (r"\bECDSA\b|\bECC\b|ec\.|EllipticCurve", "Public-key"),
    "ECDH": (r"\bECDH\b", "Key exchange"),
    "DH": (r"\bDiffie[- ]Hellman\b|\bDH\b", "Key exchange"),
    "DSA": (r"\bDSA\b", "Digital signature"),
    "AES": (r"\bAES[-_ ]?(128|192|256)?\b|AES\.new", "Symmetric"),
    "SHA-256": (r"\bSHA[-_ ]?256\b|sha256", "Hash"),
    "SHA-1": (r"\bSHA[-_ ]?1\b|sha1", "Hash"),
    "TLS": (r"\bTLS\s?1\.[23]\b|ssl\.|TLS", "Protocol"),
}

def scan_text(text, filename):
    rows = []
    for alg, (pattern, category) in PATTERNS.items():
        matches = list(re.finditer(pattern, text, re.I))
        for i, m in enumerate(matches[:5], 1):
            line = text[:m.start()].count("\n") + 1
            rows.append({
                "asset": f"{alg} @ {filename}:{line}",
                "algorithm": alg,
                "file": filename,
                "category": category,
                "line": line
            })
    return rows
