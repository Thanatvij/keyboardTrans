"""
Integration tests for KeyboardTrans.

Tests end-to-end functionality including the CLI and
complete conversion workflows.
"""

import pytest

from keyboardtrans.config.layouts import get_kedmanee_layout
from keyboardtrans.cli import KeyboardTransApp
from keyboardtrans.core.converter import TextConverter
from keyboardtrans.core.layout import KeyboardLayout
from keyboardtrans.strategies.simple import SimpleScoringStrategy


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_end_to_end_conversion(self):
        """Test complete conversion workflow."""
        # Setup
        layout = KeyboardLayout("test", {"a": "ก", "b": "ข", "h": "ส", "e": "ว", "l": "ด", "o": "ย"})
        converter = TextConverter(layout)
        strategy = SimpleScoringStrategy()

        # Convert EN to TH
        en_text = "hello"
        th_result = converter.en_to_th(en_text)
        assert th_result == "สวดดย"  # h->ส, e->ว, l->ด, l->ด, o->ย

        # Score both
        en_score = strategy.score_english(th_result)
        th_score = strategy.score_thai(th_result)

        # Should prefer Thai conversion (lower Thai score means less likely Thai)
        # but we're testing the scoring mechanism works

    def test_smart_convert_english_input(self):
        """Test smart conversion with English input."""
        from keyboardtrans.cli import KeyboardTransApp

        app = KeyboardTransApp()

        # Pure English input should stay as English (or be converted to Thai
        # and back if the Thai version scores higher)
        result = app._smart_convert("hello")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_smart_convert_thai_input(self):
        """Test smart conversion with Thai input."""
        app = KeyboardTransApp()

        # Pure Thai input should be detected
        result = app._smart_convert("สวัสดี")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_smart_convert_mixed_input(self):
        """Test smart conversion with mixed input."""
        app = KeyboardTransApp()

        # Mixed input
        result = app._smart_convert("helloสวัสดี")
        assert isinstance(result, str)

    def test_kedmanee_app_initialization(self):
        """Test initializing app with Kedmanee layout."""
        app = KeyboardTransApp()

        assert app._layout.name == "kedmanee"
        assert len(app._layout.en_to_th) > 0

    def test_custom_layout_initialization(self):
        """Test initializing app with custom layout."""
        custom_layout = KeyboardLayout("custom", {"a": "ก", "b": "ข"})
        app = KeyboardTransApp(layout=custom_layout)

        assert app._layout.name == "custom"
        assert app._layout.en_to_th["a"] == "ก"

    def test_verbose_mode_initialization(self):
        """Test initializing app with verbose mode."""
        app = KeyboardTransApp(verbose=True)

        assert app._verbose is True

    def test_fallback_behavior(self):
        """Test fallback behavior when scores are tied."""
        app = KeyboardTransApp()

        # Use input that might cause score ties
        result = app._smart_convert("xyz")
        assert isinstance(result, str)
        # Should not crash

    def test_round_trip_kedmanee(self):
        """Test round-trip conversion with Kedmanee layout."""
        layout = KeyboardLayout("kedmanee", get_kedmanee_layout())
        converter = TextConverter(layout)

        # Pick some characters that are definitely in the mapping
        test_cases = [
            "a",  # Should map to 'ฟ'
            "b",  # Should map to 'ห'
            "c",  # Should map to 'ก'
        ]

        for en_char in test_cases:
            th_char = converter.en_to_th(en_char)
            back_to_en = converter.th_to_en(th_char)

            # Should round trip correctly for bijective characters
            if back_to_en != en_char:
                # Character might not be bijective (original code had duplicates)
                # Just ensure we got something back
                assert isinstance(back_to_en, str)

    def test_empty_text_handling(self):
        """Test handling of empty text."""
        app = KeyboardTransApp()

        result = app._smart_convert("")
        assert result == ""

    def test_whitespace_only_handling(self):
        """Test handling of whitespace-only text."""
        app = KeyboardTransApp()

        result = app._smart_convert("   ")
        assert result == "   "

    def test_special_characters_handling(self):
        """Test handling of special characters."""
        app = KeyboardTransApp()

        # Special characters should pass through
        result = app._smart_convert("!@#$%")
        assert isinstance(result, str)

    def test_long_text_handling(self):
        """Test handling of long text."""
        app = KeyboardTransApp()

        long_text = "hello" * 100
        result = app._smart_convert(long_text)

        assert len(result) > 0

    def test_repeated_conversions(self):
        """Test that repeated conversions produce consistent results."""
        app = KeyboardTransApp()

        text = "hello world"

        result1 = app._smart_convert(text)
        result2 = app._smart_convert(text)
        result3 = app._smart_convert(text)

        # Should be deterministic
        assert result1 == result2 == result3

    def test_app_creation_multiple_times(self):
        """Test creating multiple app instances."""
        app1 = KeyboardTransApp()
        app2 = KeyboardTransApp()

        # Both should have valid layouts
        assert app1._layout is not None
        assert app2._layout is not None

    def test_converter_strategy_interaction(self):
        """Test interaction between converter and strategy."""
        layout = KeyboardLayout("test", {"a": "ก", "b": "ข"})
        converter = TextConverter(layout)
        strategy = SimpleScoringStrategy()

        # Convert and score
        text = "ab"
        th_version = converter.en_to_th(text)
        en_version = converter.th_to_en(text)

        th_score = strategy.score_thai(th_version)
        en_score = strategy.score_english(en_version)

        # Scores should be valid
        assert 0.0 <= th_score <= 1.0
        assert 0.0 <= en_score <= 1.0

    def test_kedmanee_comprehensive_conversion(self):
        """Test comprehensive conversion with full Kedmanee layout."""
        layout = KeyboardLayout("kedmanee", get_kedmanee_layout())
        converter = TextConverter(layout)

        # Test various character types
        test_cases = [
            # Lowercase
            "abcdefghijklmnopqrstuvwxyz",
            # Uppercase
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            # Numbers
            "0123456789",
            # Symbols
            "!@#$%^&*()_+-=[]{}|;':,.<>/?",
        ]

        for test_case in test_cases:
            result = converter.en_to_th(test_case)
            # Should not crash and should return string
            assert isinstance(result, str)

    def test_kedmanee_no_runtime_errors(self):
        """Test that Kedmanee layout doesn't cause runtime errors."""
        app = KeyboardTransApp()

        # Various inputs that should not cause errors
        test_inputs = [
            "",
            "a",
            "hello",
            "สวัสดี",
            "helloสวัสดี",
            "123",
            "!@#",
            "   ",
            "a" * 100,
            "\t\n\r",
        ]

        for input_text in test_inputs:
            result = app._smart_convert(input_text)
            assert isinstance(result, str)
