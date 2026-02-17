# PROJECT_CONTEXT.md

## Executive Summary

KeyboardTrans is a Python library that performs bidirectional conversion between English keystrokes and Thai characters based on keyboard layout mappings. The system addresses mixed-language keyboard input issues by providing a deterministic conversion mechanism with language detection scoring to intelligently determine the intended output language.

The library is designed with zero external dependencies (Python stdlib only), comprehensive test coverage (84 tests), and an extensible architecture using Strategy pattern for scoring algorithms.

## Technical Architecture

### Module Structure

```
keyboardtrans/
├── exceptions.py          # Exception hierarchy
├── cli.py                 # Interactive REPL (KeyboardTransApp)
├── core/
│   ├── layout.py          # KeyboardLayout, LayoutRegistry
│   ├── converter.py       # TextConverter (ASCII pass-through in th_to_en)
│   └── scoring.py        # VocabularyScoringStrategy
├── strategies/
│   ├── base.py           # ScoringStrategy (ABC)
│   ├── simple.py         # SimpleScoringStrategy (V1, built-in vocab)
│   └── weighted.py      # WeightedScoringStrategy (V3.1, multi-factor scoring)
└── config/
    ├── layouts/
    │   └── kedmanee.py   # Thai Kedmanee layout (TIS 820-2531)
    └── vocab/
        ├── en_words.json  # English vocabulary
        └── th_words.json  # Thai vocabulary
```

### Core Components

#### 1. KeyboardLayout ([`core/layout.py`](keyboardtrans/core/layout.py))
Represents a keyboard layout with bidirectional EN ↔ TH mapping.

- **Initialization**: Takes a name and EN→TH dictionary
- **Validation**: Enforces bijective (1:1) mapping via `_validate_and_freeze()`
- **Immutability**: Returns `MappingProxyType` to prevent runtime modification
- **Lazy evaluation**: `th_to_en` computed on first access via `_compute_reverse_mapping()`
- **Error handling**: Raises `LayoutIntegrityError` with duplicate information if validation fails

Key methods:
- `en_to_th` (property): Immutable EN→TH mapping
- `th_to_en` (property): Immutable TH→EN mapping (computed lazily)
- `_find_duplicates()`: Identifies non-bijective mappings
- `_validate_and_freeze()`: Validates and returns immutable proxy

#### 2. LayoutRegistry ([`core/layout.py`](keyboardtrans/core/layout.py))
Centralized registry for managing multiple layouts.

- `register(layout)`: Register a layout (raises error if name exists)
- `register_or_replace(layout)`: Register or replace existing layout
- `get(name)`: Retrieve layout by name (raises KeyError if not found)
- `list()`: Return tuple of registered names
- `__contains__`: Check if layout is registered

#### 3. TextConverter ([`core/converter.py`](keyboardtrans/core/converter.py))
Performs bidirectional text conversion.

- **Complexity**: O(n) single-pass character iteration
- **Algorithm**: Dictionary lookup with fallback for unmapped characters
- **Unmapped handling**: Passes through unchanged
- **Type checking**: Raises `InvalidInputError` for non-string input
- **Optimization**: Early return for empty strings
- **V3.1 enhancement**: `th_to_en()` passes ASCII characters through unchanged (prevents incorrect conversion of mixed Thai+ASCII text)

Key methods:
- `en_to_th(text: str) -> str`: Convert English to Thai
- `th_to_en(text: str) -> str`: Convert Thai to English (ASCII pass-through added in V3.1)

Conversion formula:
```python
# en_to_th
result = "".join(layout.get(char, char) for char in text)

# th_to_en (V3.1)
def convert_char(c):
    is_thai = 0x0E01 <= ord(c) <= 0x0E5B
    if is_thai:
        return layout.get(c, c)
    return c
result = "".join(convert_char(c) for c in text)
```

#### 4. Scoring Strategies

##### Base Strategy ([`strategies/base.py`](keyboardtrans/strategies/base.py))
Abstract base class defining the scoring interface:
- `score_english(text: str) -> float`: Score in [0, 1]
- `score_thai(text: str) -> float`: Score in [0, 1]

##### SimpleScoringStrategy ([`strategies/simple.py`](keyboardtrans/strategies/simple.py)) - **Scoring V1**
Built-in vocabulary scoring without file dependencies:
- `EN_WORDS`: Set of ~20 common English words
- `TH_WORDS`: Set of ~16 common Thai words
- Uses regex `[a-zA-Z]+` for English word extraction
- Uses regex `[ก-๙]+` for Thai word extraction
- Case-insensitive for English

##### WeightedScoringStrategy ([`strategies/weighted.py`](keyboardtrans/strategies/weighted.py)) - **Scoring V3.1**
Enhanced multi-factor scoring with improvement-based decision logic:
- `EN_WORDS`: Set of 90 common English words
- `TH_WORDS`: Set of 90 common Thai words
- `IMPROVEMENT_THRESHOLD = 0.08`: Reduced from 0.1 to make flips easier

**Weighted Scoring Formula (V3.1):**
```
final_score = 0.35 * dictionary_score
           + 0.20 * script_ratio_score
           + 0.25 * validity_score
           + 0.10 * boundary_score
           - 0.10 * garbage_score
```

**Scoring Components:**
1. **Dictionary Score (35%)**: Vocabulary matching
2. **Script Ratio Score (20%)**: ASCII/Thai Unicode ratio detection
3. **Validity Score (25%)**: Valid word pattern recognition
4. **Boundary Score (10%)**: Space ratio analysis (new in V3.1)
5. **Garbage Penalty (-10%)**: Spam/repetition and symbol density penalties

**V3.1 Enhancements:**
- **Vowelless Penalty**: Detects ASCII text without vowels as "garbage English" to prevent scoring high for keyboard garbage
  - Words >3 chars with vowel_ratio < 0.2 are marked as garbage
  - Words <=3 chars with no vowels are marked as garbage
  - Applied in `score_english()` to reduce script_score
- **Layout Noise Score**: Detects symbol clustering and vowelless words
- **Auto Correct Method**: Added `auto_correct(text)` for easy one-call correction using pythainlp

**Decision Logic (V3.1):**
- Layout inversion detection with 0.08 improvement threshold (reduced from 0.1)
- Strong flip: best_flip > original_best + 0.08
- Smart rescue: original_best < 0.45 and best_flip > original_best + 0.12
- ASCII garbage penalty: vowelless penalty > 0.6 reduces original EN score by 50%

**Helper Methods:**
- `_dictionary_score()`: Vocabulary matching score
- `_ascii_ratio()`: ASCII character ratio
- `_thai_ratio()`: Thai Unicode ratio
- `_token_validity()`: Word pattern validity
- `_boundary_score()`: Space ratio analysis (new in V3.1)
- `_garbage_penalty()`: Repetition and symbol density
- `_vowelless_penalty()`: Detects ASCII without vowels as garbage English (new in V3.1)
- `_layout_noise_score()`: Detects symbol clustering (new in V3.1)

**Additional Methods:**
- `auto_correct(text: str) -> Tuple[str, str]`: One-call correction using pythainlp (new in V3.1)
- `get_language_decision(original, th_version, en_version) -> Tuple[str, str]`:
  Makes final language decision with improvement-based logic
  Returns (chosen_text, decision_reason)
  Decision reasons (V3.1):
  - "keep_original": Original kept (no significant improvement)
  - "flipped_to_thai_strong": Flipped to TH (strong improvement)
  - "flipped_to_english_strong": Flipped to EN (strong improvement)
  - "flipped_to_thai_rescue": Flipped to TH (rescue low-confidence original)
  - "flipped_to_english_rescue": Flipped to EN (rescue low-confidence original)

##### VocabularyScoringStrategy ([`core/scoring.py`](keyboardtrans/core/scoring.py))
External vocabulary scoring from JSON files:
- Loads from configurable JSON paths
- Supports both list and dict JSON formats
- Graceful fallback to empty set if file missing
- Raises `ValueError` for malformed JSON

#### 5. KeyboardTransApp ([`cli.py`](keyboardtrans/cli.py))
Interactive CLI application.

- **Default layout**: Kedmanee (via `get_kedmanee_layout()`)
- **V3.1 Enhancement**: Uses segment-aware conversion, not WeightedScoringStrategy
  - Detects Thai characters in input → TH→EN mode
  - Detects ASCII text → EN→TH mode (token-by-token with smart handling)
  - EN→TH mode preserves: real English words (e.g., "meeting", "hello", "world") and pure digits (e.g., "500")
  - EN→TH mode converts: mixed input like "9kpsjk" to Thai
  - No pythainlp dependency in CLI (uses TextConverter directly)
- **Verbose mode**: Optional debug output showing conversion mode

Key methods:
- `_smart_convert(text: str) -> str`:
  1. Detect Thai characters in input (Thai Unicode range check)
  2. If Thai found → run TH→EN conversion (TextConverter.th_to_en)
  3. If no Thai → run EN→TH conversion with token-by-token processing
  4. Return converted text
- `_detect_and_convert(text: str) -> Tuple[str, str]`:
  1. Check for Thai characters using Unicode range (U+0E01-U+0E5B)
  2. Determine conversion mode (TH→EN or EN→TH)
  3. Run appropriate conversion

## Data Flow Diagram

### Conversion Flow (TextConverter)
```
Input Text
    │
    ▼
Type Validation (str check)
    │
    ▼
Empty Check (early return)
    │
    ▼
Character Iteration (O(n))
    │
    ├──┬──► Mapped char → Use layout mapping
    │   └──► Unmapped char → Pass through
    │
    ▼
Result String
```

### Smart Conversion Flow (KeyboardTransApp - V3.1 Segment-Aware)
```
Input Text
    │
    ▼
Thai Unicode Check (U+0E01-U+0E5B)
    │
    ├────────────────┬────────────────┐
    ▼                ▼                ▼
Thai Found     No Thai         Token Check
    │                │                │
    ▼                ▼                ▼
TH→EN Mode     EN→TH Mode    Real EN Word
    │                │                │
    ▼                ▼                ▼
Apply          Apply           Skip
th_to_en()    en_to_th()      (keep as is)
    │                │                │
    └────────────────┴────────────────┘
                    │
                    ▼
            Return Converted Text
```
```
Input Text
    │
    ├──────────────────────┐
    ▼                      ▼
EN→TH Version         TH→EN Version
    │                      │
    ▼                      ▼
Score Thai           Score English
    │                      │
    └──────────┬───────────┘
               ▼
        Calculate Improvement Scores
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
Check Original         Compare Flipped
Language Dominance      vs Original Scores
    │                     │
    │               ┌────┴────┐
    │               ▼         ▼
    │        Original < 0.6?
    │               │
    │       ┌───────┴───────┐
    │       ▼               ▼
    │    Flip Condition    Keep Original
    │       │               Met
    │       │               │
    │   ┌───┴───┐         │
    │   ▼       ▼         │
    │  Flip    Keep      │
    │  to TH   Original  │
    │   or     (Good)    │
    │   to EN             │
    │       │               │
    └───────┴───────────────┘
               ▼
        Return Best Result
```

### Layout Validation Flow
```
EN→TH Dictionary
    │
    ▼
Check for Duplicate Values
    │
    ├──┬──► Duplicates found → Raise LayoutIntegrityError
    │   └──► No duplicates
    │       │
    │       ▼
    │   Wrap in MappingProxyType (immutable)
    │       │
    │       ▼
    │   Return Validated Layout
```

### Weighted Scoring Flow (V3.1)
```
Input Text
    │
    ├──────────────────────────────────────────┐
    ▼                                   ▼
Dictionary Score (35%)          Script Ratio Score (20%)
    │                                   │
    ▼                                   ▼
Word Extraction & Matching       ASCII/Thai Ratio Detection
    │                                   │
    └──────────┬────────────────────────┘
               │
    ┌──────────┼──────────┬──────────┐
    ▼          ▼          ▼          ▼
Validity    Boundary   Garbage   Vowelless
Score (25%) Score (10%) Penalty (-10%) Penalty (V3.1)
    │          │          │          │
    ▼          ▼          ▼          ▼
Word        Space      Symbol     Check for
Pattern     Ratio      Density    vowels
Validity     Analysis   Analysis
    │          │          │          │
    └──────────┴──────────┴──────────┘
                  │
                  ▼
          ┌───────┴──────────────┐
          ▼                      ▼
  Combine: 0.35*Dict + 0.20*Script + 0.25*Validity + 0.10*Boundary - 0.10*Garbage
          │
          ▼
   Apply Vowelless Penalty to English score (if applicable)
          │
          ▼
         Clamp to [0, 1]
          │
          ▼
        Final Score
```

## Scoring Formula

### Scoring V1 Formula (SimpleScoringStrategy, VocabularyScoringStrategy)
```
For each extracted word w:
  if w in vocabulary: weight = 2
  else: weight = 1

matched = count(weight == 2)
unmatched = count(weight == 1)
total = (matched * 2) + unmatched
score = total / (num_words * 2)
```

### Scoring V3.1 Formula (WeightedScoringStrategy)
```
final_score = 0.35 * dictionary_score
           + 0.20 * script_ratio_score
           + 0.25 * validity_score
           + 0.10 * boundary_score
           - 0.10 * garbage_score
```

Where:
- `dictionary_score` = (matched * 2 + unmatched) / (num_words * 2)`
- `script_ratio_score` = ASCII ratio for English, Thai Unicode ratio for Thai
- `validity_score` = Valid words / total words (vowels, length)
- `boundary_score` = Space ratio analysis (0.08-0.25 for EN, <=0.15 for TH)
- `garbage_score` = Min(1.0, (repetition_penalty + symbol_density_penalty))
- `vowelless_penalty` (V3.1): Ratio of ASCII tokens without vowels (words >3 chars with vowel_ratio < 0.2 or words <=3 chars with no vowels)
  - Applied to English score: script_score = script_score * (1.0 - vowelless_penalty)

### Range: [0, 1]

**Scoring V1:**
- **0.0**: No words extracted (empty or non-matching characters)
- **0.5**: No words match (all unmatched)
- **1.0**: All words match vocabulary

**Scoring V2:**
- **0.0**: Empty string, or all components return 0
- **0.5 - 1.0**: Depends on weighted combination of all factors
- **1.0**: All components at maximum (high vocab match, correct script, valid tokens, no garbage)

### English Word Extraction
Regex: `[a-zA-Z]+`
- Case-insensitive (lowercased before matching)
- Ignores numbers, punctuation, whitespace

### Thai Word Extraction
Regex: `[ก-๙]+`
- Thai consonants, vowels, tone marks, digits
- Case-sensitive (Thai has no case)

## Deterministic Guarantees

### 1. Layout Immutability
- Mappings wrapped in `MappingProxyType` at initialization
- No modification possible after creation
- Prevents runtime state corruption

### 2. Conversion Determinism
- Pure functional conversion (no side effects)
- Same input always produces same output
- No randomness or external state dependence
- Verified by test: `test_deterministic_conversion`

### 3. Scoring V1 Determinism (SimpleScoringStrategy, VocabularyScoringStrategy)
- Vocabulary sets are constant after initialization
- Regex extraction is deterministic
- Same text produces identical scores
- Verified by test: `test_score_deterministic`

### 4. Scoring V3.1 Determinism (WeightedScoringStrategy)
- All scoring components use deterministic algorithms
- Vocabulary sets are constant after initialization
- Regex extraction is deterministic
- Script ratio calculation is deterministic (character count)
- Token validity check uses deterministic rules
- Boundary score uses deterministic rules (space ratio)
- Garbage penalty uses deterministic rules (character repetition, symbol density)
- Vowelless penalty uses deterministic rules (vowel counting, word length)
- Layout noise score uses deterministic rules (symbol clustering, vowelless words)
- Same text produces identical scores
- Clamping to [0, 1] range is deterministic
- Decision logic is deterministic (threshold comparisons: 0.08 improvement, 0.45 rescue, 0.6 vowelless)
- Verified by test: `test_score_deterministic` (WeightedScoringStrategy)

### 5. Lazy Evaluation Consistency
- `th_to_en` computed once on first access
- Cached internally, returns same instance
- No re-computation or variation

### 6. Decision Logic Determinism (V3.1)
- Improvement threshold is constant (0.08)
- Rescue threshold is constant (0.12)
- Minimum confidence threshold is constant (0.45)
- Vowelless penalty threshold is constant (0.6)
- Decision logic is deterministic based on threshold comparisons
- No hard script locks - improvement-based and rescue-based comparison only

## Design Constraints

### Bijective Mapping Requirement
- Each English key must map to exactly one Thai character
- Each Thai character must map to exactly one English key
- Enforced at initialization time
- Purpose: Enable correct round-trip conversion (EN→TH→EN)

### Character-Level Mapping
- Conversion operates on individual characters only
- No context-aware transformations
- No n-gram or positional considerations
- Simplicity over linguistic accuracy

### Zero Dependencies
- Uses only Python standard library
- No third-party packages required
- `json`, `re`, `pathlib`, `abc`, `typing` only
- Trade-off: Limited functionality vs. dependency management

### Type Safety
- Full type hints throughout codebase
- `mypy` configuration in [`pyproject.toml`](pyproject.toml)
- Runtime type checking in conversion methods
- Raises `InvalidInputError` for type violations

### Python Version Support
- Minimum: Python 3.8
- Tested up to: Python 3.12
- Compatibility maintained via stdlib-only approach

## Coding Standards Observed

### Code Organization
- One class per file (typically)
- Clear separation of concerns (core, strategies, config)
- Explicit `__all__` exports
- Module-level docstrings

### Naming Conventions
- Classes: `PascalCase` (e.g., `KeyboardLayout`)
- Functions/methods: `snake_case` (e.g., `en_to_th`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `EN_WORDS`, `CONFIDENCE_THRESHOLD`)
- Private methods: `_leading_underscore` (e.g., `_validate_and_freeze`)

### Documentation
- Comprehensive docstrings (Google style)
- Type hints in signatures
- Examples in docstrings
- Inline comments for complex logic

### Error Handling
- Custom exception hierarchy
- Descriptive error messages
- Type information in exceptions
- Graceful fallbacks (e.g., missing vocab files)

### Code Style
- Line length: 100 characters ([`pyproject.toml`](pyproject.toml))
- Import organization: stdlib, third-party, local
- `black` formatter configured
- `ruff` linter configured

## Dependency Philosophy

### Standard Library Only
Intentional decision to use zero external dependencies for core functionality:

**Rationale:**
- Simplified deployment and distribution
- Reduced dependency conflicts
- Faster installation (no large packages)
- Easier to audit and maintain
- Works in constrained environments

**Stdlib modules used:**
- `json`: Vocabulary file parsing
- `re`: Word extraction patterns
- `pathlib`: File path handling
- `abc`: Abstract base classes
- `typing`: Type hints
- `types.MappingProxyType`: Immutability

**Dev dependencies only:**
- `pytest`: Testing framework
- `pytest-cov`: Coverage reporting
- `mypy`: Type checking
- `black`: Code formatting
- `ruff`: Linting

## Testing Philosophy

### Test Organization
- [`tests/test_layout.py`](tests/test_layout.py): Layout validation and registry
- [`tests/test_converter.py`](tests/test_converter.py): Conversion logic
- [`tests/test_scoring.py`](tests/test_scoring.py): Scoring strategies (V1)
- [`tests/test_weighted_v2_regression.py`](tests/test_weighted_v2_regression.py): Scoring strategies (V2.1 regression)
- [`tests/test_integration.py`](tests/test_integration.py): End-to-end workflows
- [`tests/conftest.py`](tests/conftest.py): Shared fixtures

### Coverage Strategy
- Unit tests for individual methods
- Integration tests for component interaction
- Edge case handling (empty strings, non-string input, etc.)
- Determinism verification
- Round-trip conversion testing

### Fixtures ([`conftest.py`](tests/conftest.py))
- `simple_layout`: Minimal test layout (7 keys)
- `keyboard_layout`: KeyboardLayout instance
- `text_converter`: TextConverter instance
- `scoring_strategy`: SimpleScoringStrategy instance

### Test Categories
1. **Happy path**: Normal operation
2. **Edge cases**: Empty strings, single characters
3. **Error cases**: Invalid input, type violations
4. **Determinism**: Repeated calls produce same result
5. **Properties**: Round-trip conversion, immutability

## Roadmap Alignment

### Current State (v0.1.0 - V3.1)
- ✅ Kedmanee layout support
- ✅ Simple scoring strategy (V1)
- ✅ Weighted scoring strategy (V3.1) - **COMPLETED**
- ✅ IMPROVEMENT_THRESHOLD reduced from 0.1 to 0.08 - **COMPLETED**
- ✅ Vowelless penalty for English garbage detection - **COMPLETED**
- ✅ Boundary score (space ratio analysis) - **COMPLETED**
- ✅ Layout noise score (symbol clustering) - **COMPLETED**
- ✅ Auto correct method with pythainlp integration - **COMPLETED**
- ✅ CLI uses segment-aware conversion (not WeightedScoringStrategy) - **COMPLETED**
- ✅ converter.py th_to_en() passes ASCII through unchanged - **COMPLETED**
- ✅ Comprehensive test suite (17 layout tests)
- ✅ Zero-dependency core (CLI uses no pythainlp)

### Planned Features ([`README.md`](README.md))
- ⬜ Pattachote layout support
- ⬜ ML-based scoring strategy (future, not current)
- ⬜ N-gram language model scoring (future)
- ⬜ Beam search for ambiguous conversions (future)
- ⬜ Web API
- ⬜ GUI application

### Extension Points Identified
1. **New layouts**: Create layout file in `config/layouts/`
2. **Custom scoring**: Inherit from `BaseScoringStrategy`
3. **Scoring V2 components**: Each factor can be extended independently
4. **ML integration**: Implement strategy with model inference (future)

## Known Trade-offs

### Greedy Conversion vs. Context-Aware
- **Current**: Character-by-character greedy conversion
- **Trade-off**: Cannot handle homophones or context-dependent mappings
- **Impact**: May produce incorrect conversions for ambiguous inputs
- **Mitigation**: Language detection scoring for post-conversion selection (V1), Multi-factor scoring (V2)

### Vocabulary-Based Scoring vs. N-Grams
- **Scoring V1**: Word vocabulary matching only
- **Scoring V2**: Multi-factor scoring (dict + script + validity - garbage)
- **Trade-off**: No contextual language modeling
- **Impact**: Lower accuracy on short or mixed text (V1), Improved accuracy (V2)
- **Mitigation**: Larger vocabularies, script ratio detection, future N-gram support

### Single Layout vs. Multi-Layout
- **Current**: CLI uses single layout (Kedmanee)
- **Trade-off**: Cannot detect layout from input
- **Impact**: Wrong layout produces incorrect output
- **Mitigation**: Explicit layout selection, future auto-detection

### Bidirectional vs. Unidirectional
- **Current**: Both EN→TH and TH→EN
- **Trade-off**: Bijective requirement limits layout support
- **Impact**: Cannot support layouts with duplicate mappings
- **Mitigation**: Layout validation at initialization

### Zero Dependencies vs. Rich Features
- **Current**: Stdlib-only core
- **Trade-off**: Limited ML/NLP capabilities
- **Impact**: Scoring relies on simple vocabulary matching (V1), Enhanced multi-factor (V2)
- **Mitigation**: Optional ML-based strategies in future

### Hard Rules vs. Pure Scoring
- **Scoring V2**: Uses hard rules for clear-cut decisions
- **Trade-off**: May override scoring results even when marginally incorrect
- **Impact**: ASCII/Thai ratio thresholds force specific outcomes
- **Mitigation**: Thresholds set conservatively (0.9), confidence threshold (0.15)

## Non-Goals (What Does NOT Do)

### Intentionally Out of Scope
1. **Contextual translation**: No sentence or paragraph-level analysis
2. **Grammar checking**: No linguistic validation
3. **Automatic layout detection**: User must select layout explicitly
4. **Smart correction**: No typo fixing or spell-checking
5. **Unicode normalization**: Does not normalize characters (uses input as-is)
6. **Fuzzy matching**: Exact character mapping only (no similarity scoring)
7. **Learning from user input**: No adaptive scoring or feedback loops
8. **Real-time input processing**: Designed for batch/text input, not keystroke hooks
9. **Cross-platform keyboard hooks**: No OS-level keyboard interception
10. **Multi-layout auto-switching**: Single active layout per session
11. **Machine learning**: Not used in V1 or V2 - pure deterministic scoring
12. **Neural networks**: Not used - pure deterministic algorithms

### Linguistic Non-Goals
1. **Morphological analysis**: No word stemming or lemmatization
2. **Syntactic parsing**: No sentence structure analysis
3. **Semantic understanding**: No meaning-based conversion
4. **Tone mark validation**: Does not verify Thai tone mark correctness
5. **Vowel checking**: Does not validate Thai vowel combinations

## Key Design Decisions Rationale

### 1. Bijective Validation
**Decision**: Enforce 1:1 mapping at layout initialization
**Rationale**: Prevents runtime conversion errors, ensures round-trip consistency
**Impact**: Rejects layouts with duplicate values (original Kedmanee had duplicates)

### 2. Immutable Mappings
**Decision**: Use `MappingProxyType` for layout dictionaries
**Rationale**: Prevents accidental modification, ensures thread-safety
**Impact**: Any modification attempt raises TypeError

### 3. Lazy Reverse Mapping
**Decision**: Compute `th_to_en` on first access
**Rationale**: Save computation time if never used
**Impact**: First `th_to_en` access incurs one-time cost

### 4. Strategy Pattern for Scoring
**Decision**: Abstract scoring via `BaseScoringStrategy`
**Rationale**: Extensible design, easy to add ML or N-gram strategies
**Impact**: New scoring methods don't require core changes

### 5. Pass-Through for Unmapped Chars
**Decision**: Return unchanged for characters not in layout
**Rationale**: Graceful handling of mixed input, no data loss
**Impact**: Symbols, numbers, and foreign characters preserved

### 6. Character-Level Conversion
**Decision**: Convert one character at a time
**Rationale**: Simplicity, O(n) complexity, deterministic
**Impact**: Cannot handle multi-character mappings (e.g., combined characters)

### 7. Vocabulary Scoring Formula (V1)
**Decision**: `score = (matched*2 + unmatched) / (total*2)`
**Rationale**: Vocabulary matches count double, unmatched count single
**Impact**: Favors known words, reduces false positives

### 8. Weighted Multi-Factor Scoring (V2)
**Decision**: `final_score = 0.4*dict + 0.3*script + 0.2*validity - 0.1*garbage`
**Rationale**: Multiple factors provide more balanced scoring than vocabulary alone
**Impact**: Improved accuracy, addresses V1 limitations:
  - Script ratio provides clear language signal
  - Token validity filters gibberish
  - Garbage penalty penalizes spam and symbols
  - All factors are deterministic and stdlib-only

### 9. Hard Rules for Decision Making (V2)
**Decision**: Apply hard rules before score comparison
- ASCII ratio > 0.9 → force English
- Thai ratio > 0.9 → force Thai
- Confidence diff < 0.15 → return original (ambiguous)
**Rationale**: Prevents 0.500 vs 0.500 ambiguity, reduces incorrect conversions
**Impact**: Some loss of precision for guaranteed correctness in ambiguous cases

### 10. Expanded Vocabulary (V2)
**Decision**: Expand from ~20 EN words / ~16 TH words (V1) to ~200 EN words / ~210 TH words (V2)
**Rationale**: Better vocabulary coverage improves dictionary score accuracy
**Impact**: Reduces "low dictionary coverage" issues from V1
