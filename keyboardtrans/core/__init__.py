"""
Core components for KeyboardTrans.

This module contains the fundamental building blocks for text conversion:
- Layout management and validation
- Text conversion logic
- Scoring strategies for language detection
"""

from keyboardtrans.core.layout import KeyboardLayout, LayoutRegistry
from keyboardtrans.core.converter import TextConverter
from keyboardtrans.core.scoring import VocabularyScoringStrategy

__all__ = [
    "KeyboardLayout",
    "LayoutRegistry",
    "TextConverter",
    "VocabularyScoringStrategy",
]
