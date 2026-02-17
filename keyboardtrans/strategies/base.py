"""
Base classes for scoring strategies.

This module defines the abstract interface that all scoring
strategies must implement, enabling the Strategy pattern.
"""

from abc import ABC, abstractmethod


class ScoringStrategy(ABC):
    """
    Abstract base class for text scoring strategies.

    All scoring strategies must inherit from this class and
    implement the required methods.

    A scoring strategy evaluates text and returns a score
    indicating the likelihood that the text belongs to a
    particular language. Scores should be in the range [0, 1].

    Example:
        >>> class MyStrategy(ScoringStrategy):
        ...     def score_english(self, text: str) -> float:
        ...         # Implementation here
        ...         pass
        ...     def score_thai(self, text: str) -> float:
        ...         # Implementation here
        ...         pass
    """

    @abstractmethod
    def score_english(self, text: str) -> float:
        """
        Score text as English.

        Args:
            text: The text to score.

        Returns:
            A score in [0, 1] representing likelihood of English.
        """
        pass

    @abstractmethod
    def score_thai(self, text: str) -> float:
        """
        Score text as Thai.

        Args:
            text: The text to score.

        Returns:
            A score in [0, 1] representing likelihood of Thai.
        """
        pass


# Alias for backwards compatibility
BaseScoringStrategy = ScoringStrategy
