"""
Custom exceptions for KeyboardTrans.

All exceptions provide clear, actionable error messages.
"""


class KeyboardTransError(Exception):
    """Base exception for all KeyboardTrans errors."""


class LayoutIntegrityError(KeyboardTransError):
    """
    Raised when a keyboard layout mapping is not bijective.

    A bijective mapping ensures that each key maps to exactly one
    character and vice versa. Duplicate mappings prevent proper
    reverse conversion.

    Example:
        >>> en_to_th = {'a': 'ก', 'b': 'ก'}  # Duplicate value
        >>> # LayoutIntegrityError: Duplicate value 'ก' mapped from: a, b
    """

    def __init__(self, message: str, duplicates: dict | None = None):
        """
        Initialize LayoutIntegrityError.

        Args:
            message: Error message describing the issue.
            duplicates: Dictionary mapping duplicate values to source keys.
        """
        super().__init__(message)
        self.duplicates = duplicates or {}


class ConversionError(KeyboardTransError):
    """
    Raised when text conversion fails.

    This error is raised for unexpected conversion failures
    that cannot be attributed to invalid input type.
    """


class InvalidInputError(KeyboardTransError):
    """
    Raised when input is not a valid string.

    All conversion functions expect string input. This error
    provides a clear message about the expected type.

    Example:
        >>> converter.en_to_th(123)  # Invalid input
        >>> # InvalidInputError: Expected str, got int
    """

    def __init__(self, message: str, expected_type: type, actual_type: type):
        """
        Initialize InvalidInputError.

        Args:
            message: Error message describing the issue.
            expected_type: The expected input type.
            actual_type: The actual input type received.
        """
        super().__init__(message)
        self.expected_type = expected_type
        self.actual_type = actual_type
