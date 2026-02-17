"""
Pytest configuration and shared fixtures.

This module provides shared test fixtures for the test suite.
"""

import pytest

from keyboardtrans.config.layouts import get_kedmanee_layout
from keyboardtrans.core.converter import TextConverter
from keyboardtrans.core.layout import KeyboardLayout
from keyboardtrans.strategies.simple import SimpleScoringStrategy


@pytest.fixture
def simple_layout():
    """Create a simple test layout."""
    return {
        "a": "ก",
        "b": "ข",
        "c": "ค",
        "h": "ส",
        "e": "ว",
        "l": "ด",
        "o": "ย",
    }


@pytest.fixture
def keyboard_layout(simple_layout):
    """Create a KeyboardLayout instance for testing."""
    return KeyboardLayout("test", simple_layout)


@pytest.fixture
def text_converter(keyboard_layout):
    """Create a TextConverter instance for testing."""
    return TextConverter(keyboard_layout)


@pytest.fixture
def scoring_strategy():
    """Create a SimpleScoringStrategy instance for testing."""
    return SimpleScoringStrategy()


@pytest.fixture
def kedmanee_layout():
    """Create the Kedmanee layout for testing."""
    return KeyboardLayout("kedmanee", get_kedmanee_layout())
