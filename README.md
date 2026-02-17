# KeyboardTrans

Thai-English Keyboard Transliterator - A modular, testable Python library for converting between Thai and English keystrokes based on keyboard layout mappings.

## Features

- **Modular Architecture**: Clean separation of concerns with layout management, conversion logic, and scoring strategies
- **Bijective Validation**: Ensures 1:1 EN ↔ TH mapping integrity at initialization
- **Deterministic Behavior**: Same input always produces the same output
- **Type Safety**: Full type hints throughout
- **Extensible**: Strategy pattern for custom scoring algorithms
- **Well-Tested**: Comprehensive pytest test suite (84 tests)
- **Zero Dependencies**: Uses only Python standard library

### Scoring V3.1

The library uses **WeightedScoringStrategy** (Scoring V3.1) with enhanced multi-factor scoring:

**Weighted Scoring Formula:**
```
final_score = 0.35 * dictionary_score
           + 0.20 * script_ratio_score
           + 0.25 * validity_score
           + 0.10 * boundary_score
           - 0.10 * garbage_score
```

**Scoring Components:**
- **Dictionary Score** (35%): Vocabulary matching
- **Script Ratio Score** (20%): ASCII ratio detection for English, Thai Unicode ratio for Thai
- **Validity Score** (25%): Valid word pattern recognition
- **Boundary Score** (10%): Space ratio analysis
- **Garbage Penalty** (-10%): Spam/repetition and symbol density penalties
- **Vowelless Penalty** (V3.1): Detects ASCII without vowels as "garbage English"

**Decision Logic (V3.1):**
- Improvement-based layout inversion detection (0.08 threshold, reduced from 0.1)
- Smart rescue for low-confidence text (0.12 threshold)
- Vowelless penalty reduces English score for garbage text (0.6 threshold)
- No hard script locks
- No confidence threshold blocking conversions

**Vocabulary Coverage:**
- English: 90 common words
- Thai: 90 common words

**V3.1 Improvements:**
- ✓ Reduced IMPROVEMENT_THRESHOLD from 0.1 to 0.08 (easier flips)
- ✓ Added vowelless penalty to detect keyboard garbage
- ✓ Added boundary score for space ratio analysis
- ✓ Added layout noise score for symbol clustering
- ✓ Added auto_correct() method with pythainlp integration
- ✓ CLI uses segment-aware conversion (not WeightedScoringStrategy)
- ✓ converter.py th_to_en() passes ASCII through unchanged (fixes comma issue)
- ✓ No pythainlp dependency in CLI (uses TextConverter directly)
- ✓ No machine learning - pure deterministic scoring

## Installation

```bash
# From source
cd keyboardTrans
pip install -e .

# For development
pip install -e ".[dev]"
```

## Quick Start

### Python API

```python
from keyboardtrans.config.layouts import get_kedmanee_layout
from keyboardtrans.core.layout import KeyboardLayout
from keyboardtrans.core.converter import TextConverter

# Create layout and converter
layout = KeyboardLayout("kedmanee", get_kedmanee_layout())
converter = TextConverter(layout)

# Convert text
thai_text = converter.en_to_th("hello")
english_keystrokes = converter.th_to_en("สวัสดี")

print(thai_text)  # Converts English keystrokes to Thai characters
```

### Command Line

```bash
# Run interactive CLI (with segment-aware conversion)
python -m keyboardtrans.cli

# Or use the installed command
keyboardtrans

# Enable verbose mode to see conversion mode
python -m keyboardtrans.cli --verbose
```

## Architecture

```
keyboardtrans/
├── __init__.py           # Package exports
├── cli.py                # Command-line interface (segment-aware conversion)
├── exceptions.py         # Custom exceptions
├── core/
│   ├── layout.py         # Layout management and validation
│   ├── converter.py      # Text conversion logic (ASCII pass-through in th_to_en)
│   └── scoring.py         # Vocabulary-based scoring
├── strategies/
│   ├── base.py           # Abstract strategy interface
│   ├── simple.py         # Simple scoring with built-in vocab (V1)
│   └── weighted.py      # Weighted scoring with multi-factors (V3.1)
└── config/
    ├── layouts/
    │   └── kedmanee.py   # Kedmanee layout definition
    └── vocab/
        ├── en_words.json  # English vocabulary
        └── th_words.json  # Thai vocabulary
```

## Usage

### Smart Conversion with Language Detection (V3.1)

```python
from keyboardtrans.cli import KeyboardTransApp

# Create app with Kedmanee layout
app = KeyboardTransApp()

# Smart convert uses segment-aware conversion (Thai check → TH→EN, else EN→TH with token handling)
# EN→TH mode preserves real EN words and pure digits, converts mixed input like "9kpsjk"
result = app._smart_convert("hello")
print(result)  # Returns corrected text
```

### Using Scoring V3.1 Directly

```python
from keyboardtrans.strategies.weighted import WeightedScoringStrategy
from keyboardtrans.core.converter import TextConverter
from keyboardtrans.core.layout import KeyboardLayout

# Create layout and converter
layout = KeyboardLayout("kedmanee", get_kedmanee_layout())
converter = TextConverter(layout)

# Use WeightedScoringStrategy (V3.1)
strategy = WeightedScoringStrategy()
th_score = strategy.score_thai("สวัสดีครับ")
en_score = strategy.score_english("hello world")

# Get language decision with improvement-based logic (V3.1)
original = "สวัสดี"
result, reason = strategy.auto_correct(original)

print(f"Result: {result}")
print(f"Reason: {reason}")  # e.g., "keep_original", "flipped_to_thai_strong", "flipped_to_english_strong"
```

### Custom Scoring Strategy

```python
from keyboardtrans.strategies.base import BaseScoringStrategy

class MyScoringStrategy(BaseScoringStrategy):
    def score_english(self, text: str) -> float:
        # Your custom scoring logic
        pass

    def score_thai(self, text: str) -> float:
        # Your custom scoring logic
        pass

# Use custom strategy
from keyboardtrans.cli import KeyboardTransApp
app = KeyboardTransApp()
app._strategy = MyScoringStrategy()
```

### Multiple Layouts

```python
from keyboardtrans.core.layout import KeyboardLayout, LayoutRegistry

# Create registry
registry = LayoutRegistry()

# Register layouts
kedmanee = KeyboardLayout("kedmanee", get_kedmanee_layout())
registry.register(kedmanee)

# Retrieve layout
layout = registry.get("kedmanee")
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=keyboardtrans

# Run specific test file
pytest tests/test_layout.py

# Run specific test
pytest tests/test_converter.py::TestTextConverter::test_en_to_th_basic_conversion
```

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check .

# Type checking
mypy keyboardtrans
```

## Keyboard Layouts

### Thai Kedmanee

The library includes the Thai Kedmanee keyboard layout (TIS 820-2531). The mapping is validated for bijective (1:1) correspondence to enable proper bidirectional conversion.

### Adding New Layouts

1. Create a new layout file in `config/layouts/`
2. Define the EN → TH mapping dictionary
3. Register the layout using `KeyboardLayout`

## API Reference

### `KeyboardLayout`

Represents a keyboard layout with bidirectional EN ↔ TH mapping.

**Methods:**
- `__init__(name: str, en_to_th: Dict[str, str])`: Initialize layout
- `property en_to_th`: Get EN → TH mapping (immutable)
- `property th_to_en`: Get TH → EN mapping (immutable, computed lazily)

### `TextConverter`

Converts text between English keystrokes and Thai characters.

**Methods:**
- `__init__(layout: KeyboardLayout)`: Initialize converter
- `en_to_th(text: str) -> str`: Convert English to Thai
- `th_to_en(text: str) -> str`: Convert Thai to English

### `WeightedScoringStrategy` (Scoring V3.1)

Enhanced weighted scoring strategy with multi-factor analysis and improvement-based decision logic.

**Methods:**
- `score_english(text: str) -> float`: Score as English [0, 1]
- `score_thai(text: str) -> float`: Score as Thai [0, 1]
- `auto_correct(text: str) -> Tuple[str, str]`: One-call correction using pythainlp (V3.1)
- `get_language_decision(original, th_version, en_version) -> Tuple[str, str]`: Make final decision with improvement-based logic

**Constants:**
- `IMPROVEMENT_THRESHOLD = 0.08`: Minimum improvement required to flip (reduced from 0.1 in V2.1)
- Rescue threshold: 0.12 improvement for low-confidence original (score < 0.45)
- Vowelless penalty threshold: 0.6 reduces English score by 50% for garbage text

### `SimpleScoringStrategy` (Scoring V1)

Simple scoring strategy with built-in vocabulary (retained for backward compatibility).

**Methods:**
- `score_english(text: str) -> float`: Score as English [0, 1]
- `score_thai(text: str) -> float`: Score as Thai [0, 1]

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Commit your changes
7. Push to the branch (`git push origin feat/amazing-feature`)
8. Open a Pull Request

## License

MIT License - see LICENSE file for details.

## Roadmap

- [x] Weighted multi-factor scoring (V3.1) - **COMPLETED**
- [x] Vowelless penalty for garbage detection - **COMPLETED**
- [x] Boundary score for space ratio analysis - **COMPLETED**
- [x] Reduced IMPROVEMENT_THRESHOLD to 0.08 - **COMPLETED**
- [x] CLI segment-aware conversion (not WeightedScoringStrategy) - **COMPLETED**
- [x] converter.py ASCII pass-through in th_to_en - **COMPLETED**
- [ ] Pattachote layout support
- [ ] N-gram language model scoring
- [ ] Beam search for ambiguous conversions
- [ ] Web API
- [ ] GUI application

## Acknowledgments

- Thai Industrial Standard TIS 820-2531 for Kedmanee layout specification
- Original inspiration from the need to fix mixed-language keyboard input issues
