import re
from typing import List, Dict

def validate_family_id(family_id: str) -> bool:
    return bool(family_id and isinstance(family_id, str) and len(family_id) > 0)

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def sanitize_input(text: str) -> str:
    return text.strip() if text else ""

def parse_quantity(qty_str: str) -> float:
    match = re.search(r'([\d.]+)', qty_str)
    return float(match.group(1)) if match else 0.0

def format_quantity(qty: float, unit: str = "") -> str:
    if qty == int(qty):
        return f"{int(qty)} {unit}".strip()
    return f"{qty:.1f} {unit}".strip()
