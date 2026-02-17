"""
KeyboardTrans - Thai-English Keyboard Transliterator

A modular, testable library for converting between Thai and English
keystrokes based on keyboard layout mappings.
"""

__version__ = "0.1.0"
__author__ = "Thanatv"

from keyboardtrans.exceptions import (
    LayoutIntegrityError,
    ConversionError,
    InvalidInputError,
)
from keyboardtrans.core.layout import KeyboardLayout, LayoutRegistry
from keyboardtrans.core.converter import TextConverter
from keyboardtrans.core.scoring import VocabularyScoringStrategy
from keyboardtrans.strategies.base import ScoringStrategy, BaseScoringStrategy
from keyboardtrans.strategies.simple import SimpleScoringStrategy
from keyboardtrans.strategies.weighted import WeightedScoringStrategy

__all__ = [
    # Version
    "__version__",
    # Exceptions
    "LayoutIntegrityError",
    "ConversionError",
    "InvalidInputError",
    # Core classes
    "KeyboardLayout",
    "LayoutRegistry",
    "TextConverter",
    # Scoring
    "ScoringStrategy",
    "VocabularyScoringStrategy",
    "BaseScoringStrategy",
    "SimpleScoringStrategy",
    "WeightedScoringStrategy",
]
