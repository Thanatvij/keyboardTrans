"""
Unit tests for scoring strategies.

Tests vocabulary-based and simple scoring strategies
for language detection.
"""

import pytest

from keyboardtrans.strategies.simple import SimpleScoringStrategy
from keyboardtrans.strategies.base import BaseScoringStrategy


class TestSimpleScoringStrategy:
    """Tests for SimpleScoringStrategy class."""

    def test_inherits_from_base(self):
        """Test that SimpleScoringStrategy inherits from BaseScoringStrategy."""
        strategy = SimpleScoringStrategy()

        assert isinstance(strategy, BaseScoringStrategy)

    def test_score_english_high_confidence(self):
        """Test scoring high-confidence English text."""
        strategy = SimpleScoringStrategy()

        score = strategy.score_english("hello world")
        assert score > 0.5  # Should be high because "hello" is in vocabulary

    def test_score_english_no_match(self):
        """Test scoring English text with no vocabulary matches."""
        strategy = SimpleScoringStrategy()

        score = strategy.score_english("asdfghjkl")
        # Should still return a score (for unmatched words), but lower
        assert 0.0 < score < 0.6

    def test_score_english_empty_string(self):
        """Test scoring empty string returns 0."""
        strategy = SimpleScoringStrategy()

        score = strategy.score_english("")
        assert score == 0.0

    def test_score_thai_high_confidence(self):
        """Test scoring high-confidence Thai text."""
        strategy = SimpleScoringStrategy()

        score = strategy.score_thai("สวัสดีครับ")
        assert score >= 0.5  # Should be high because "สวัสดี" is in vocabulary

    def test_score_thai_no_match(self):
        """Test scoring Thai text with no vocabulary matches."""
        strategy = SimpleScoringStrategy()

        # Create some random Thai characters
        score = strategy.score_thai("กขค")
        # Should still return a score (for unmatched words), but lower
        assert 0.0 < score < 0.6

    def test_score_thai_empty_string(self):
        """Test scoring empty string returns 0."""
        strategy = SimpleScoringStrategy()

        score = strategy.score_thai("")
        assert score == 0.0

    def test_scores_are_normalized(self):
        """Test that scores are normalized between 0 and 1."""
        strategy = SimpleScoringStrategy()

        # Test various inputs
        en_score1 = strategy.score_english("hello what why how")
        en_score2 = strategy.score_english("the and is a to")
        th_score1 = strategy.score_thai("สวัสดีครับค่ะ")
        th_score2 = strategy.score_thai("ทำอะไรคุณ")

        # All scores should be in valid range
        assert 0.0 <= en_score1 <= 1.0
        assert 0.0 <= en_score2 <= 1.0
        assert 0.0 <= th_score1 <= 1.0
        assert 0.0 <= th_score2 <= 1.0

    def test_non_string_input_raises_error(self):
        """Test that non-string input raises TypeError."""
        strategy = SimpleScoringStrategy()

        with pytest.raises(TypeError):
            strategy.score_english(123)

        with pytest.raises(TypeError):
            strategy.score_thai(123)

    def test_case_insensitive_english_scoring(self):
        """Test that English scoring is case-insensitive."""
        strategy = SimpleScoringStrategy()

        score1 = strategy.score_english("Hello")
        score2 = strategy.score_english("hello")
        score3 = strategy.score_english("HELLO")

        # Should be the same (all convert to lowercase)
        assert score1 == score2 == score3

    def test_mixed_language_scoring(self):
        """Test scoring mixed language text."""
        strategy = SimpleScoringStrategy()

        # English text with Thai characters
        en_score = strategy.score_english("hello สวัสดี")
        # Thai text with English characters
        th_score = strategy.score_thai("สวัสดี hello")

        # Both should return some score
        assert en_score >= 0.0
        assert th_score >= 0.0

    def test_punctuation_handling(self):
        """Test that punctuation is handled correctly."""
        strategy = SimpleScoringStrategy()

        score = strategy.score_english("hello, world! how are you?")
        # Punctuation should be ignored, words should be counted
        assert score > 0.5

    def test_vocabulary_contains_expected_words(self):
        """Test that vocabulary contains expected words."""
        strategy = SimpleScoringStrategy()

        # Check English vocabulary
        assert "hello" in strategy.EN_WORDS
        assert "what" in strategy.EN_WORDS
        assert "thanat" in strategy.EN_WORDS

        # Check Thai vocabulary
        assert "สวัสดี" in strategy.TH_WORDS
        assert "ครับ" in strategy.TH_WORDS
        assert "ธนัช" in strategy.TH_WORDS

    def test_multiple_words_increase_score(self):
        """Test that more vocabulary matches increase score."""
        strategy = SimpleScoringStrategy()

        score1 = strategy.score_english("hello")
        score2 = strategy.score_english("hello what")

        # More matches should increase score (or stay same if all matched)
        assert score2 >= score1

    def test_score_deterministic(self):
        """Test that scoring is deterministic."""
        strategy = SimpleScoringStrategy()

        text = "hello world"
        score1 = strategy.score_english(text)
        score2 = strategy.score_english(text)

        assert score1 == score2

    def test_english_word_extraction(self):
        """Test that English words are extracted correctly."""
        strategy = SimpleScoringStrategy()

        # The regex should extract only a-z A-Z sequences
        score = strategy.score_english("hello123world")
        # Should count "hello" and "world" separately
        assert score > 0.0

    def test_thai_word_extraction(self):
        """Test that Thai words are extracted correctly."""
        strategy = SimpleScoringStrategy()

        # The regex should extract Thai characters
        score = strategy.score_thai("สวัสดี123ครับ")
        # Should count "สวัสดี" and "ครับ" separately
        assert score > 0.0

    def test_whitespace_only(self):
        """Test that whitespace-only text returns 0 score."""
        strategy = SimpleScoringStrategy()

        assert strategy.score_english("   ") == 0.0
        assert strategy.score_thai("   ") == 0.0

    def test_numbers_only(self):
        """Test that numbers-only text returns 0 score."""
        strategy = SimpleScoringStrategy()

        # Numbers don't count as words
        assert strategy.score_english("123 456") == 0.0

    def test_single_word(self):
        """Test scoring single word."""
        strategy = SimpleScoringStrategy()

        # Matched word
        score_matched = strategy.score_english("hello")
        # Unmatched word
        score_unmatched = strategy.score_english("asdfg")

        # Matched should score higher
        assert score_matched > score_unmatched

    def test_special_characters_only(self):
        """Test that special characters return 0 score."""
        strategy = SimpleScoringStrategy()

        assert strategy.score_english("!@#$%^&*()") == 0.0
