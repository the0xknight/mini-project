import math
import re
from urllib.parse import urlparse
import tldextract

def calculate_shannon_entropy(text: str) -> float:
    """Calculates the Shannon information entropy of an input string."""
    if not text:
        return 0.0
    length = len(text)
    counts = {}
    for char in text:
        counts[char] = counts.get(char, 0) + 1
    entropy = 0.0
    for count in counts.values():
        p = count / length
        entropy -= p * math.log2(p)
    return float(round(entropy, 4))

def extract_features_from_url(url: str) -> dict:
    """
    Extracts 16 client-side reproducible features from a raw URL.
    Returns a dictionary of float values.
    """
    raw_url = str(url).strip()
    if not raw_url.startswith(('http://', 'https://')):
        url_to_parse = 'http://' + raw_url
    else:
        url_to_parse = raw_url

    parsed = urlparse(url_to_parse)
    ext = tldextract.extract(url_to_parse)

    hostname = (parsed.netloc or '').lower()
    path = parsed.path or ''
    query = parsed.query or ''

    # 1. Length metrics
    url_len = float(len(raw_url))
    host_len = float(len(hostname))
    path_len = float(len(path))

    # 2. Character counts
    count_dot = float(raw_url.count('.'))
    count_hyphen = float(hostname.count('-'))
    count_at = float(raw_url.count('@'))
    count_question = float(raw_url.count('?'))
    count_equal = float(raw_url.count('='))
    count_slash = float(raw_url.count('/'))
    count_percent = float(raw_url.count('%'))

    # 3. Structural & Domain metrics
    host_clean = hostname.split(':')[0]
    is_ip = 1.0 if re.match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', host_clean) else 0.0

    subdomain = ext.subdomain
    subdomain_depth = float(subdomain.count('.') + 1) if subdomain else 0.0

    suspicious_keywords = ['login', 'verify', 'update', 'banking', 'secure', 'signin', 'account', 'admin']
    has_keyword = 1.0 if any(kw in (path + query).lower() for kw in suspicious_keywords) else 0.0

    is_https = 1.0 if parsed.scheme == 'https' else 0.0

    # 4. Information-Theoretic Metrics
    hostname_entropy = calculate_shannon_entropy(hostname)
    url_entropy = calculate_shannon_entropy(raw_url)

    return {
        'url_len': url_len,
        'host_len': host_len,
        'path_len': path_len,
        'count_dot': count_dot,
        'count_hyphen': count_hyphen,
        'count_at': count_at,
        'count_question': count_question,
        'count_equal': count_equal,
        'count_slash': count_slash,
        'count_percent': count_percent,
        'is_ip': is_ip,
        'subdomain_depth': subdomain_depth,
        'has_keyword': has_keyword,
        'is_https': is_https,
        'hostname_entropy': hostname_entropy,
        'url_entropy': url_entropy
    }