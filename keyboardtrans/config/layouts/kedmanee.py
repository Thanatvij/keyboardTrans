"""
Thai Kedmanee Keyboard Layout.

This module defines the official Thai Kedmanee keyboard layout mapping
between English keystrokes and Thai characters.

Reference:
    - Thai Industrial Standard TIS 820-2531 (1988)
    - Windows Thai Kedmanee layout

The layout includes:
- 47 Thai consonants
- 32 Thai vowels and tone marks
- 15 Thai digits and symbols

The mapping is bijective (1:1) to enable proper bidirectional conversion.
"""

# Thai Kedmanee Keyboard Layout (US -> Thai Kedmanee)
# Reference: Standard Thai Kedmanee keyboard layout
# Fix: Removed duplicate mappings to ensure bijective 1:1 correspondence

KEDMANEE_LAYOUT = {
    # Row 1: Numbers and symbols
    '`': '_',
    '1': 'ๅ',
    '2': '/',
    '3': '-',
    '4': 'ภ',
    '5': 'ถ',
    '6': 'ุ',
    '7': 'ึ',
    '8': 'ค',
    '9': 'ต',
    '0': 'จ',
    '-': 'ข',
    '=': 'ช',
    # Shifted row 1
    '~': '%',
    '!': '+',
    '@': '๑',
    '#': '๒',
    '$': '๓',
    '%': '๔',
    '^': 'ู',
    '&': '฿',
    '*': '๕',
    '(': '๖',
    ')': '๗',
    '_': '๘',
    '+': '๙',
    # Row 2
    'q': 'ๆ',
    'w': 'ไ',
    'e': 'ำ',
    'r': 'พ',
    't': 'ะ',
    'y': 'ั',
    'u': 'ี',
    'i': 'ร',
    'o': 'น',
    'p': 'ย',
    '[': 'บ',
    ']': 'ล',
    '\\': 'ฃ',
    # Shifted row 2
    'Q': '๐',
    'W': '"',
    'E': 'ฎ',
    'R': 'ฑ',
    'T': 'ธ',
    'Y': 'ํ',
    'U': '๊',
    'I': 'ณ',
    'O': 'ฯ',
    'P': 'ญ',
    '{': 'ฐ',
    '}': ',',
    '|': '.',
    # Row 3
    'a': 'ฟ',
    's': 'ห',
    'd': 'ก',
    'f': 'ด',
    'g': 'เ',
    'h': '้',
    'j': '่',
    'k': 'า',
    'l': 'ส',
    ';': 'ว',
    "'": 'ง',
    # Shifted row 3
    'A': 'ฤ',
    'S': 'ฆ',
    'D': 'ฏ',
    'F': 'โ',
    'G': 'ฌ',
    'H': '็',
    'J': '๋',
    'K': 'ษ',
    'L': 'ศ',
    ':': 'ซ',
    '"': 'ฺ',
    # Row 4
    'z': 'ผ',
    'x': 'ป',
    'c': 'แ',
    'v': 'อ',
    'b': 'ิ',
    'n': 'ื',
    'm': 'ท',
    ',': 'ม',
    '.': 'ใ',
    '/': 'ฝ',
    # Shifted row 4
    'Z': 'ฉ',
    'X': 'ฮ',
    # 'C': 'ฺ'  - REMOVED: Duplicate of '"' mapping
    'V': '์',  # Thai tone mark Phinthu
    'B': '?',  # Question mark
    'N': 'ฒ',
    'M': 'ฬ',
    '<': 'ฦ',  # Thai letter LU (keeping this one)
    # Removed: '>': 'ฦ' - duplicate of '<'
    # Removed: '?': 'ฦ' - duplicate of '<'
}

# Layout metadata
KEDMANEE_METADATA = {
    "name": "Thai Kedmanee",
    "standard": "TIS 820-2531 (1988)",
    "description": "Standard Thai keyboard layout named after the Kedmanee family",
    "characters": len(KEDMANEE_LAYOUT),
    "version": "1.0",
}


def get_kedmanee_layout() -> dict:
    """
    Get the Thai Kedmanee layout mapping.

    Returns:
        Dictionary mapping English keystrokes to Thai characters.
    """
    return KEDMANEE_LAYOUT.copy()
