"""
Unit tests for keyboard layout management.

Tests layout validation, bijection checking, and reverse mapping.
"""

import pytest

from keyboardtrans.config.layouts import get_kedmanee_layout
from keyboardtrans.core.layout import KeyboardLayout, LayoutRegistry
from keyboardtrans.exceptions import LayoutIntegrityError


class TestKeyboardLayout:
    """Tests for KeyboardLayout class."""

    def test_valid_layout_creation(self):
        """Test creating a valid keyboard layout."""
        en_to_th = {"a": "ก", "b": "ข", "c": "ค"}
        layout = KeyboardLayout("test", en_to_th)

        assert layout.name == "test"
        assert len(layout.en_to_th) == 3
        assert layout.en_to_th["a"] == "ก"

    def test_kedmanee_layout_bijective(self):
        """Test that the Kedmanee layout is bijective."""
        layout = KeyboardLayout("kedmanee", get_kedmanee_layout())

        # Check no duplicate values
        values = list(layout.en_to_th.values())
        assert len(values) == len(set(values)), "Layout has duplicate values"

        # Check reverse mapping is complete
        assert len(layout.th_to_en) == len(layout.en_to_th)

    def test_duplicate_values_raise_error(self):
        """Test that duplicate values raise LayoutIntegrityError."""
        en_to_th = {"a": "ก", "b": "ก"}  # Duplicate value

        with pytest.raises(LayoutIntegrityError) as exc_info:
            KeyboardLayout("test", en_to_th)

        assert "non-bijective" in str(exc_info.value)
        assert exc_info.value.duplicates == {"ก": {"a", "b"}}

    def test_immutable_mapping(self):
        """Test that the layout mapping is immutable."""
        layout = KeyboardLayout("test", {"a": "ก"})

        # Try to modify the mapping (should raise TypeError)
        with pytest.raises(TypeError):
            layout.en_to_th["b"] = "ข"

    def test_lazy_reverse_mapping(self):
        """Test that reverse mapping is computed lazily."""
        layout = KeyboardLayout("test", {"a": "ก"})

        # Access th_to_en property
        assert layout.th_to_en["ก"] == "a"

    def test_reverse_mapping_accuracy(self):
        """Test that reverse mapping is accurate."""
        en_to_th = {"a": "ก", "b": "ข", "c": "ค"}
        layout = KeyboardLayout("test", en_to_th)

        for en_char, th_char in en_to_th.items():
            assert layout.th_to_en[th_char] == en_char

    def test_empty_layout(self):
        """Test creating an empty layout."""
        layout = KeyboardLayout("empty", {})

        assert len(layout.en_to_th) == 0
        assert len(layout.th_to_en) == 0

    def test_repr(self):
        """Test string representation."""
        layout = KeyboardLayout("test", {"a": "ก", "b": "ข"})

        assert "KeyboardLayout" in repr(layout)
        assert "test" in repr(layout)
        assert "keys=2" in repr(layout)


class TestLayoutRegistry:
    """Tests for LayoutRegistry class."""

    def test_register_and_retrieve(self):
        """Test registering and retrieving a layout."""
        registry = LayoutRegistry()
        layout = KeyboardLayout("test", {"a": "ก"})

        registry.register(layout)
        retrieved = registry.get("test")

        assert retrieved is layout
        assert retrieved.name == "test"

    def test_duplicate_registration_raises_error(self):
        """Test that registering a duplicate name raises an error."""
        registry = LayoutRegistry()
        layout1 = KeyboardLayout("test", {"a": "ก"})
        layout2 = KeyboardLayout("test", {"b": "ข"})

        registry.register(layout1)

        with pytest.raises(LayoutIntegrityError) as exc_info:
            registry.register(layout2)

        assert "already registered" in str(exc_info.value)

    def test_register_or_replace(self):
        """Test register_or_replace replaces existing layout."""
        registry = LayoutRegistry()
        layout1 = KeyboardLayout("test", {"a": "ก"})
        layout2 = KeyboardLayout("test", {"b": "ข"})

        registry.register(layout1)
        registry.register_or_replace(layout2)

        retrieved = registry.get("test")
        assert retrieved is layout2
        assert retrieved.en_to_th["b"] == "ข"

    def test_get_nonexistent_raises_keyerror(self):
        """Test that getting nonexistent layout raises KeyError."""
        registry = LayoutRegistry()

        with pytest.raises(KeyError) as exc_info:
            registry.get("nonexistent")

        assert "nonexistent" in str(exc_info.value)

    def test_list_layouts(self):
        """Test listing all registered layouts."""
        registry = LayoutRegistry()
        registry.register(KeyboardLayout("layout1", {"a": "ก"}))
        registry.register(KeyboardLayout("layout2", {"b": "ข"}))

        layouts = registry.list()

        assert len(layouts) == 2
        assert "layout1" in layouts
        assert "layout2" in layouts

    def test_contains(self):
        """Test the 'in' operator."""
        registry = LayoutRegistry()
        layout = KeyboardLayout("test", {"a": "ก"})

        assert "test" not in registry

        registry.register(layout)
        assert "test" in registry

    def test_registry_repr(self):
        """Test string representation of registry."""
        registry = LayoutRegistry()
        registry.register(KeyboardLayout("layout1", {"a": "ก"}))

        repr_str = repr(registry)
        assert "LayoutRegistry" in repr_str
        assert "layouts=1" in repr_str
        assert "layout1" in repr_str

    def test_kedmanee_layout_has_correct_size(self):
        """Test that Kedmanee layout has expected number of keys."""
        kedmanee_map = get_kedmanee_layout()

        # Kedmanee should have all mapped keys
        assert len(kedmanee_map) > 80  # Approximate expected size

        # Verify all keys are single characters
        for key in kedmanee_map.keys():
            assert isinstance(key, str)
            assert len(key) == 1

        # Verify all values are single characters
        for value in kedmanee_map.values():
            assert isinstance(value, str)
            assert len(value) == 1

    def test_kedmanee_comma_mapping_consistency(self):
        """
        Test that Kedmanee layout comma mapping is bidirectional and consistent.

        Verifies the cycle: } → , → ม → , → }
        This ensures no collision in the bidirectional mapping.
        """
        layout = KeyboardLayout("kedmanee", get_kedmanee_layout())

        # Forward mapping (EN → TH)
        assert layout.en_to_th["}"] == ",", "Right brace should map to comma"
        assert layout.en_to_th[","] == "ม", "Comma should map to Thai letter ม"

        # Reverse mapping (TH → EN)
        assert layout.th_to_en["ม"] == ",", "Thai letter ม should map back to comma"
        assert layout.th_to_en[","] == "}", "Comma should map back to right brace"

        # Verify bidirectional consistency
        # EN → TH → EN cycle
        assert layout.th_to_en[layout.en_to_th["}"]] == "}"
        assert layout.th_to_en[layout.en_to_th[","]] == ","

        # TH → EN → TH cycle
        assert layout.en_to_th[layout.th_to_en["ม"]] == "ม"
        assert layout.en_to_th[layout.th_to_en[","]] == ","
