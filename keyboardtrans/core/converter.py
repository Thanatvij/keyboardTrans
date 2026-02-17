"""
Text conversion logic for keyboard transliteration.

This module provides deterministic, type-safe text conversion
between English keystrokes and Thai characters.
"""

from typing import TYPE_CHECKING

from keyboardtrans.exceptions import InvalidInputError

if TYPE_CHECKING:
    from keyboardtrans.core.layout import KeyboardLayout


class TextConverter:
    """
    Converts text between English keystrokes and Thai characters.

    This class uses a KeyboardLayout to perform deterministic,
    O(n) complexity conversions. All unmapped characters are
    passed through unchanged.

    Example:
        >>> layout = KeyboardLayout("test", {'a': 'ก', 'b': 'ข'})
        >>> converter = TextConverter(layout)
        >>> converter.en_to_th("ab")  # 'กข'
        >>> converter.th_to_en("กข")  # 'ab'
        >>> converter.en_to_th("x")   # 'x' (unmapped)
    """

    def __init__(self, layout: "KeyboardLayout"):
        """
        Initialize a TextConverter.

        Args:
            layout: The KeyboardLayout to use for conversions.
        """
        self._layout = layout

    def en_to_th(self, text: str) -> str:
        """
        Convert English keystrokes to Thai characters.

        Unmapped characters (those not in the layout) are passed
        through unchanged.

        Args:
            text: The English text to convert.

        Returns:
            The converted Thai text.

        Raises:
            InvalidInputError: If input is not a string.
        """
        if not isinstance(text, str):
            raise InvalidInputError(
                f"en_to_th() expects str input, got {type(text).__name__}",
                expected_type=str,
                actual_type=type(text),
            )

        # Empty string optimization
        if not text:
            return text

        # O(n) conversion - single pass through characters
        return "".join(self._layout.en_to_th.get(c, c) for c in text)

    def th_to_en(self, text: str) -> str:
        """
        Convert Thai characters to English keystrokes.

        Unmapped characters are passed through unchanged.
        ASCII characters are passed through unchanged even if they
        appear in the reverse mapping (e.g., comma ','). This prevents
        incorrect conversion of mixed Thai+ASCII text.

        Args:
            text: The Thai text to convert.

        Returns:
            The converted English keystrokes.

        Raises:
            InvalidInputError: If input is not a string.
        """
        if not isinstance(text, str):
            raise InvalidInputError(
                f"th_to_en() expects str input, got {type(text).__name__}",
                expected_type=str,
                actual_type=type(text),
            )

        # Empty string optimization
        if not text:
            return text

        # O(n) conversion - single pass through characters
        # Only convert Thai characters (Unicode range U+0E01-U+0E5B)
        # ASCII characters pass through unchanged
        def convert_char(c: str) -> str:
            # Thai Unicode range: U+0E01 to U+0E5B
            is_thai = 0x0E01 <= ord(c) <= 0x0E5B
            if is_thai:
                return self._layout.th_to_en.get(c, c)
            return c

        return "".join(convert_char(c) for c in text)

    def __repr__(self) -> str:
        """Return string representation of the converter."""
        return f"TextConverter(layout='{self._layout.name}')"
