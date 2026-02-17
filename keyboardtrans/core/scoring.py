"""
Vocabulary-based scoring strategies.

This module provides scoring strategies based on word vocabularies
for determining the likelihood that text is English or Thai.
"""

import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Set

from keyboardtrans.strategies.base import BaseScoringStrategy


class VocabularyScoringStrategy(BaseScoringStrategy):
    """
    Scores text based on vocabulary word matching.

    This strategy checks text against predefined vocabularies and
    returns normalized scores in the range [0, 1].

    Example:
        >>> strategy = VocabularyScoringStrategy(
        ...     en_vocab_path="config/vocab/en_words.json",
        ...     th_vocab_path="config/vocab/th_words.json"
        ... )
        >>> strategy.score_english("hello world")  # Returns high score
        >>> strategy.score_thai("สวัสดีครับ")         # Returns high score
    """

    def __init__(self, en_vocab_path: str | Path, th_vocab_path: str | Path):
        """
        Initialize VocabularyScoringStrategy.

        Args:
            en_vocab_path: Path to English vocabulary JSON file.
            th_vocab_path: Path to Thai vocabulary JSON file.
        """
        self._en_vocab: Set[str] = self._load_vocab(en_vocab_path)
        self._th_vocab: Set[str] = self._load_vocab(th_vocab_path)

        # Regex patterns for word extraction
        self._en_word_pattern = re.compile(r"[a-zA-Z]+")
        self._th_word_pattern = re.compile(r"[ก-๙]+")

    def score_english(self, text: str) -> float:
        """
        Score text as English based on vocabulary matching.

        The score is calculated as:
        score = (matched_words * 2 + unmatched_words) / total_words

        This gives higher weight to vocabulary matches while still
        counting any English words.

        Args:
            text: The text to score.

        Returns:
            A score in [0, 1] representing likelihood of English.
            Returns 0.0 for empty or non-English text.
        """
        if not isinstance(text, str):
            raise TypeError(f"Expected str, got {type(text).__name__}")

        # Extract English words
        words = self._en_word_pattern.findall(text.lower())

        if not words:
            return 0.0

        # Count matched vs unmatched
        matched = sum(1 for w in words if w in self._en_vocab)
        unmatched = len(words) - matched

        # Score: matched words count double, unmatched count single
        # Normalize by total words (weighted)
        total = (matched * 2) + unmatched
        return total / (len(words) * 2)

    def score_thai(self, text: str) -> float:
        """
        Score text as Thai based on vocabulary matching.

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

        # Extract Thai words
        words = self._th_word_pattern.findall(text)

        if not words:
            return 0.0

        # Count matched vs unmatched
        matched = sum(1 for w in words if w in self._th_vocab)
        unmatched = len(words) - matched

        # Score: matched words count double, unmatched count single
        total = (matched * 2) + unmatched
        return total / (len(words) * 2)

    def _load_vocab(self, path: str | Path) -> Set[str]:
        """
        Load vocabulary from a JSON file.

        Args:
            path: Path to the vocabulary JSON file.

        Returns:
            Set of vocabulary words (lowercased for English).

        Raises:
            FileNotFoundError: If the vocabulary file doesn't exist.
            ValueError: If the file is not valid JSON.
        """
        import json

        path = Path(path)

        if not path.exists():
            # Return empty set if file doesn't exist (graceful fallback)
            return set()

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Support both list and dict formats
            if isinstance(data, list):
                return set(str(w).lower() for w in data)
            elif isinstance(data, dict):
                return set(str(k).lower() for k in data.keys())
            else:
                raise ValueError(
                    f"Invalid vocabulary format in {path}: expected list or dict"
                )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {path}: {e}") from e
