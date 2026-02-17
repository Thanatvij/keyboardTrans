"""
Simple scoring strategy with built-in vocabulary.

This module provides a basic scoring strategy that uses
hardcoded vocabulary for quick evaluation without external
file dependencies.
"""

import re
from typing import Set

from keyboardtrans.strategies.base import BaseScoringStrategy


class SimpleScoringStrategy(BaseScoringStrategy):
    """
    Simple scoring strategy using built-in vocabulary.

    This strategy uses a small, built-in vocabulary for quick
    evaluation. It's suitable for basic use cases or testing.

    Example:
        >>> strategy = SimpleScoringStrategy()
        >>> strategy.score_english("hello")  # Returns high score
        >>> strategy.score_thai("สวัสดี")   # Returns high score
    """

    # Built-in vocabulary
    EN_WORDS: Set[str] = {
        "hello",
        "what",
        "why",
        "how",
        "are",
        "you",
        "doing",
        "thanat",
        "the",
        "and",
        "is",
        "a",
        "to",
        "in",
        "that",
        "it",
        "for",
        "on",
        "with",
        "as",
        "this",
        "was",
        "at",
    }

    TH_WORDS: Set[str] = {
        "สวัสดี",
        "ครับ",
        "ค่ะ",
        "ทำ",
        "อะไร",
        "คุณ",
        "ธนัช",
        "ไม่",
        "มี",
        "หรือ",
        "ที่",
        "ของ",
        "เป็น",
        "แล้ว",
        "ได้",
        "ให้",
        "นะ",
    }

    def __init__(self):
        """Initialize SimpleScoringStrategy."""
        self._en_word_pattern = re.compile(r"[a-zA-Z]+")
        self._th_word_pattern = re.compile(r"[ก-๙]+")

    def score_english(self, text: str) -> float:
        """
        Score text as English using built-in vocabulary.

        The score is calculated as:
        score = (matched_words * 2 + unmatched_words) / total_words

        Args:
            text: The text to score.

        Returns:
            A score in [0, 1] representing likelihood of English.
            Returns 0.0 for empty or non-English text.
        """
        if not isinstance(text, str):
            raise TypeError(f"Expected str, got {type(text).__name__}")

        words = self._en_word_pattern.findall(text.lower())

        if not words:
            return 0.0

        matched = sum(1 for w in words if w in self.EN_WORDS)
        unmatched = len(words) - matched

        total = (matched * 2) + unmatched
        return total / (len(words) * 2)

    def score_thai(self, text: str) -> float:
        """
        Score text as Thai using built-in vocabulary.

        The score is calculated as:
        score = (matched_words * 2 + unmatched_words) / total_words

        Args:
            text: The text to score.

        Returns:
            A score in [0, 1] representing likelihood of Thai.
            Returns 0.0 for empty or non-Thai text.
        """
        if not isinstance(text, str):
            raise TypeError(f"Expected str, got {type(text).__name__}")

        words = self._th_word_pattern.findall(text)

        if not words:
            return 0.0

        matched = sum(1 for w in words if w in self.TH_WORDS)
        unmatched = len(words) - matched

        total = (matched * 2) + unmatched
        return total / (len(words) * 2)
