"""
Input validation and sanitization utilities.
"""

import re


def sanitize_string(input_str, max_length=255):
    if not input_str or not isinstance(input_str, str):
        return None

    sanitized = re.sub(r'[<>"\'\\;]', "", input_str.strip())

    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized if sanitized else None


def validate_csv_content(content):
    if not content or not isinstance(content, str):
        return False

    dangerous_patterns = [
        r"<script",
        r"javascript:",
        r"onload=",
        r"onerror=",
        r"vbscript:",
        r"data:",
        r"<!ENTITY",
        r"<!DOCTYPE",
        r"<?xml",
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return False

    lines = content.split("\n")
    for line in lines:
        if len(line) > 10000:
            return False

    return True
