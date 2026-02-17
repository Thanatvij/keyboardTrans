"""
Unit tests for text conversion logic.

Tests English to Thai and Thai to English conversion,
including edge cases and error handling.
"""

import pytest

from keyboardtrans.core.converter import TextConverter
from keyboardtrans.core.layout import KeyboardLayout
from keyboardtrans.exceptions import InvalidInputError


class TestTextConverter:
    """Tests for TextConverter class."""

    def test_en_to_th_basic_conversion(self):
        """Test basic English to Thai conversion."""
        layout = KeyboardLayout("test", {"a": "ก", "b": "ข"})
        converter = TextConverter(layout)

        result = converter.en_to_th("ab")
        assert result == "กข"

    def test_th_to_en_basic_conversion(self):
        """Test basic Thai to English conversion."""
        layout = KeyboardLayout("test", {"a": "ก", "b": "ข"})
        converter = TextConverter(layout)

        result = converter.th_to_en("กข")
        assert result == "ab"

    def test_unmapped_characters_pass_through(self):
        """Test that unmapped characters pass through unchanged."""
        layout = KeyboardLayout("test", {"a": "ก", "b": "ข"})
        converter = TextConverter(layout)

        # 'a' -> 'ก', 'b' -> 'ข', 'x' passes through unchanged
        result = converter.en_to_th("axb")
        assert result == "กxข"

    def test_empty_string(self):
        """Test empty string handling."""
        layout = KeyboardLayout("test", {"a": "ก"})
        converter = TextConverter(layout)

        assert converter.en_to_th("") == ""
        assert converter.th_to_en("") == ""

    def test_uppercase_lowercase(self):
        """Test that uppercase and lowercase are treated separately."""
        layout = KeyboardLayout("test", {"a": "ก", "A": "ข"})
        converter = TextConverter(layout)

        assert converter.en_to_th("aA") == "กข"
        assert converter.th_to_en("กข") == "aA"

    def test_special_characters(self):
        """Test special character conversion."""
        layout = KeyboardLayout("test", {"!": "๑", "@": "๒"})
        converter = TextConverter(layout)

        assert converter.en_to_th("!@") == "๑๒"
        assert converter.th_to_en("๑๒") == "!@"

    def test_non_string_input_raises_error(self):
        """Test that non-string input raises InvalidInputError."""
        layout = KeyboardLayout("test", {"a": "ก"})
        converter = TextConverter(layout)

        with pytest.raises(InvalidInputError) as exc_info:
            converter.en_to_th(123)

        assert "en_to_th" in str(exc_info.value)
        assert exc_info.value.expected_type == str
        assert exc_info.value.actual_type == int

    def test_none_input_raises_error(self):
        """Test that None input raises error."""
        layout = KeyboardLayout("test", {"a": "ก"})
        converter = TextConverter(layout)

        with pytest.raises(InvalidInputError):
            converter.en_to_th(None)

        with pytest.raises(InvalidInputError):
            converter.th_to_en(None)

    def test_mixed_language_input(self):
        """Test mixed language input."""
        layout = KeyboardLayout("test", {"a": "ก", "b": "ข"})
        converter = TextConverter(layout)

        # Input has both mapped and unmapped characters
        result = converter.en_to_th("aXbY")
        # 'a' -> 'ก', 'b' -> 'ข', 'X' and 'Y' pass through
        assert result == "กXขY"

    def test_converter_repr(self):
        """Test string representation."""
        layout = KeyboardLayout("test", {"a": "ก"})
        converter = TextConverter(layout)

        assert "TextConverter" in repr(converter)
        assert "test" in repr(converter)

    def test_deterministic_conversion(self):
        """Test that conversion is deterministic."""
        layout = KeyboardLayout("test", {"a": "ก", "b": "ข"})
        converter = TextConverter(layout)

        input_text = "ab"
        result1 = converter.en_to_th(input_text)
        result2 = converter.en_to_th(input_text)

        assert result1 == result2

    def test_round_trip(self):
        """Test round-trip conversion (EN -> TH -> EN)."""
        layout = KeyboardLayout("test", {"a": "ก", "b": "ข"})
        converter = TextConverter(layout)

        original = "ab"
        thai = converter.en_to_th(original)
        back = converter.th_to_en(thai)

        assert back == original

    def test_kedmanee_sample_conversion(self):
        """Test with actual Kedmanee layout sample."""
        from keyboardtrans.config.layouts import get_kedmanee_layout

        layout = KeyboardLayout("kedmanee", get_kedmanee_layout())
        converter = TextConverter(layout)

        # Test a simple conversion
        result = converter.en_to_th("hello")
        # Each character should be converted if mapped
        assert isinstance(result, str)

    def test_long_text_conversion(self):
        """Test conversion of long text."""
        layout = KeyboardLayout("test", {"a": "ก"})
        converter = TextConverter(layout)

        long_text = "a" * 1000
        result = converter.en_to_th(long_text)

        assert result == "ก" * 1000
        assert len(result) == 1000

    def test_unicode_characters(self):
        """Test handling of Unicode characters."""
        layout = KeyboardLayout("test", {"a": "ก"})
        converter = TextConverter(layout)

        # Test with emoji
        result = converter.en_to_th("a😀")
        assert result == "ก😀"

    def test_whitespace_handling(self):
        """Test whitespace handling."""
        layout = KeyboardLayout("test", {"a": "ก"})
        converter = TextConverter(layout)

        result = converter.en_to_th("a b  c")
        assert result == "ก b  c"
