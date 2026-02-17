"""
Keyboard layout management and validation.

This module provides classes for defining and validating keyboard
layout mappings between English and Thai characters.
"""

from typing import Dict, Mapping, Set, Tuple
from types import MappingProxyType

from keyboardtrans.exceptions import LayoutIntegrityError


class KeyboardLayout:
    """
    Represents a keyboard layout with bidirectional EN ↔ TH mapping.

    The layout ensures bijective mapping (1:1 correspondence) between
    English keys and Thai characters. The layout is immutable after
    validation to prevent runtime corruption.

    Example:
        >>> en_to_th = {'a': 'ก', 'b': 'ข', 'c': 'ค'}
        >>> layout = KeyboardLayout("my_layout", en_to_th)
        >>> layout.en_to_th['a']  # 'ก'
        >>> layout.th_to_en['ก']  # 'a'
    """

    def __init__(self, name: str, en_to_th: Dict[str, str]):
        """
        Initialize a KeyboardLayout.

        Args:
            name: Human-readable name for this layout.
            en_to_th: Mapping from English characters to Thai characters.

        Raises:
            LayoutIntegrityError: If the mapping is not bijective.
        """
        self._name = name
        self._en_to_th = self._validate_and_freeze(en_to_th)
        self._th_to_en: Dict[str, str] | None = None

    @property
    def name(self) -> str:
        """Get the layout name."""
        return self._name

    @property
    def en_to_th(self) -> Mapping[str, str]:
        """
        Get the English to Thai mapping (immutable).

        Returns:
            Read-only mapping of English to Thai characters.
        """
        return self._en_to_th

    @property
    def th_to_en(self) -> Mapping[str, str]:
        """
        Get the Thai to English mapping (immutable).

        The reverse mapping is computed lazily on first access.

        Returns:
            Read-only mapping of Thai to English characters.
        """
        if self._th_to_en is None:
            self._th_to_en = self._compute_reverse_mapping()
        return self._th_to_en

    def _validate_and_freeze(self, mapping: Dict[str, str]) -> Mapping[str, str]:
        """
        Validate the mapping is bijective and return an immutable proxy.

        Args:
            mapping: The EN → TH mapping to validate.

        Returns:
            An immutable MappingProxyType of the validated mapping.

        Raises:
            LayoutIntegrityError: If duplicate values exist in the mapping.
        """
        # Check for duplicate values (non-bijective)
        duplicates = self._find_duplicates(mapping)

        if duplicates:
            dup_str = ", ".join(
                f"'{value}' <- {', '.join(repr(k) for k in sources)}"
                for value, sources in duplicates.items()
            )
            raise LayoutIntegrityError(
                f"Layout '{self._name}' has non-bijective mapping. "
                f"Duplicate values: {dup_str}",
                duplicates=duplicates,
            )

        # Return immutable proxy to prevent modification
        return MappingProxyType(mapping)

    def _find_duplicates(self, mapping: Dict[str, str]) -> Dict[str, Set[str]]:
        """
        Find all duplicate values in the mapping.

        Args:
            mapping: The mapping to check for duplicates.

        Returns:
            Dictionary mapping each duplicate value to the set of keys that map to it.
        """
        seen: Dict[str, Set[str]] = {}

        for key, value in mapping.items():
            if value not in seen:
                seen[value] = set()
            seen[value].add(key)

        # Return only values that have multiple keys
        return {k: v for k, v in seen.items() if len(v) > 1}

    def _compute_reverse_mapping(self) -> Mapping[str, str]:
        """
        Compute the reverse TH → EN mapping with validation.

        Returns:
            Immutable mapping from Thai to English characters.
        """
        # The reverse should be bijective since we validated the forward mapping
        reverse = {v: k for k, v in self._en_to_th.items()}
        return MappingProxyType(reverse)

    def __repr__(self) -> str:
        """Return string representation of the layout."""
        return f"KeyboardLayout(name='{self._name}', keys={len(self._en_to_th)})"


class LayoutRegistry:
    """
    Registry for managing multiple keyboard layouts.

    This class provides a centralized way to register and retrieve
    keyboard layouts by name.

    Example:
        >>> registry = LayoutRegistry()
        >>> registry.register(KeyboardLayout("kedmanee", kedmanee_map))
        >>> layout = registry.get("kedmanee")
        >>> all_layouts = registry.list()
    """

    def __init__(self):
        """Initialize an empty layout registry."""
        self._layouts: Dict[str, KeyboardLayout] = {}

    def register(self, layout: KeyboardLayout) -> None:
        """
        Register a keyboard layout.

        Args:
            layout: The KeyboardLayout instance to register.

        Raises:
            LayoutIntegrityError: If a layout with the same name exists.
        """
        if layout.name in self._layouts:
            raise LayoutIntegrityError(
                f"Layout '{layout.name}' is already registered. "
                f"Use replace=True to override."
            )
        self._layouts[layout.name] = layout

    def register_or_replace(self, layout: KeyboardLayout) -> None:
        """
        Register a keyboard layout, replacing any existing layout with the same name.

        Args:
            layout: The KeyboardLayout instance to register.
        """
        self._layouts[layout.name] = layout

    def get(self, name: str) -> KeyboardLayout:
        """
        Get a registered layout by name.

        Args:
            name: The name of the layout to retrieve.

        Returns:
            The requested KeyboardLayout instance.

        Raises:
            KeyError: If no layout with the given name is registered.
        """
        if name not in self._layouts:
            available = ", ".join(self._layouts.keys())
            raise KeyError(
                f"Layout '{name}' not found. Available layouts: {available}"
            )
        return self._layouts[name]

    def list(self) -> Tuple[str, ...]:
        """
        List all registered layout names.

        Returns:
            Tuple of layout names in registration order.
        """
        return tuple(self._layouts.keys())

    def __contains__(self, name: str) -> bool:
        """Check if a layout is registered."""
        return name in self._layouts

    def __repr__(self) -> str:
        """Return string representation of the registry."""
        return f"LayoutRegistry(layouts={len(self._layouts)}, names={self.list()})"
