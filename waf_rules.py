import re

# Common malicious signatures for SQL Injection and XSS
SQLI_PATTERNS = [
    r"(\%27)|(\')|(\-\-)|(\#)|(\%23)",  # Quotes, comments
    r"(?i)(SELECT|UNION|INSERT|UPDATE|DROP|DELETE|ALTER|CAST|DECLARE)\s+",  # SQL keywords
    r"(\%3D)|(=)[^\n]*((\%27)|(\')|(\-\-)|(\%3B))",  # Tautologies like 1=1
]

XSS_PATTERNS = [
    r"(?i)<script[^>]*>[\s\S]*?</script>",  # Script tags
    r"(?i)javascript\s*:",  # Javascript URIs
    r"(?i)onerror\s*=",  # Event handler injections
    r"(?i)<img[^>]+src[^>]*=\s*['\"]?javascript:",
]


def detect_sql_injection(text: str) -> bool:
    for pattern in SQLI_PATTERNS:
        if re.search(pattern, text):
            return True
    return False


def detect_xss(text: str) -> bool:
    for pattern in XSS_PATTERNS:
        if re.search(pattern, text):
            return True
    return False
