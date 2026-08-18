import re

# Enhanced malicious signatures for SQL Injection (SQLi)
SQLI_PATTERNS = [
    # Quotes, SQL comments, and hashes
    r"(\%27)|(\')|(\-\-)|(\#)|(\%23)",
    # Common SQL keywords followed by space or URL-encoded space (%20)
    r"(?i)(SELECT|UNION|INSERT|UPDATE|DROP|DELETE|ALTER|CAST|DECLARE)(\s+|\%20)+",
    # Boolean-based tautology checks (e.g., OR 1=1, '1'='1', or URL encoded)
    r"(?i)(OR|AND)(\s+|\%20)+[^\n]*((\%3D)|(=))",
    r"(\%3D)|(=)[^\n]*((\%27)|(\')|(\-\-)|(\%3B))",
]

# Enhanced malicious signatures for Cross-Site Scripting (XSS)
XSS_PATTERNS = [
    # Standard script tags and variations
    r"(?i)<script[^>]*>[\s\S]*?</script>",
    # Javascript URI schemes (including encoded variants like java%0ascript:)
    r"(?i)javascript\s*:",
    r"(?i)java\%0ascript\s*:",
    # Common DOM event handler injections (onload, onerror, onclick, etc.)
    r"(?i)(onerror|onload|onclick|onmouseover|onfocus|onunload)\s*=",
    # Malicious image tags with embedded javascript
    r"(?i)<img[^>]+src[^>]*=\s*['\"]?javascript:",
    # Encoded HTML brackets (< or >)
    r"(\%3C)|(\%3E)",
]


def detect_sql_injection(text: str) -> bool:
    """
    Inspects input strings for SQL Injection attack signatures.
    Returns True if a match is found, False otherwise.
    """
    if not text:
        return False
    for pattern in SQLI_PATTERNS:
        if re.search(pattern, text):
            return True
    return False


def detect_xss(text: str) -> bool:
    """
    Inspects input strings for Cross-Site Scripting (XSS) attack signatures.
    Returns True if a match is found, False otherwise.
    """
    if not text:
        return False
    for pattern in XSS_PATTERNS:
        if re.search(pattern, text):
            return True
    return False
