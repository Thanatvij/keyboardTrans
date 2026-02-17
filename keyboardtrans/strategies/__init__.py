"""
Scoring strategies for language detection.

This module provides extensible strategies for determining
whether text is likely English or Thai.
"""

from keyboardtrans.strategies.base import BaseScoringStrategy, ScoringStrategy
from keyboardtrans.strategies.simple import SimpleScoringStrategy
from keyboardtrans.strategies.weighted import WeightedScoringStrategy

__all__ = [
    "BaseScoringStrategy",
    "ScoringStrategy",
    "SimpleScoringStrategy",
    "WeightedScoringStrategy",
]
