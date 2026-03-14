# PROJECT_CONTEXT.md

## 🤖 Instructions for AI Assistant (Claude Code)

**Read these files before doing ANYTHING:**
1. `CLAUDE_zz_nutz.md` — dev guidelines and short codes
2. `PROJECT_CONTEXT.md` — this file (architecture + known bugs)
3. `README.md` — features and usage

**Hard rules — never break these:**
- ❌ Do NOT create a `keyboardtrans/` package structure — this project is intentionally single-file
- ❌ Do NOT modify `EN_TO_TH` dict without explicit permission — layout has been verified against real macOS keyboard
- ❌ Do NOT revert `'N': '์'` back to `'V': '์'` — macOS Thai Kedmanee uses `N`, not `V`
- ❌ Do NOT add external dependencies — zero dependencies is a core requirement
- ✅ Files you may edit: `KeyboardTran.py`, `accuracy_test.py`, `RoundTripTest.py`
- ✅ After every change, run: `python3 accuracy_test.py` and `python3 RoundTripTest.py`
- ✅ Always report pass/fail count before asking what to do next

**Short codes (from CLAUDE_zz_nutz.md):**
- `nnn` — analyze and create implementation plan
- `gogogo` — execute latest plan step by step
- `lll` — show project status

---

## Executive Summary

KeyboardTrans is a personal productivity tool that fixes text typed on the wrong Thai-English keyboard layout (Kedmanee). It handles:
- Pure Thai typed as EN keystrokes → convert back to Thai
- Pure EN garbage → convert to Thai
- Mixed Thai+EN in the same sentence → convert Thai parts, preserve real EN words

**Design philosophy:** Single Python file, zero dependencies, offline, runs in milliseconds.

---

## Project Structure

```
keyboardTrans/
├── KeyboardTran.py       # Main tool — single file, no dependencies
├── accuracy_test.py      # 20 real-world test cases (95% exact match)
├── RoundTripTest.py      # Roundtrip validation for all chars in layout
├── README.md             # English documentation
├── README_th.md          # Thai documentation
├── PROJECT_CONTEXT.md    # This file
└── CLAUDE_zz_nutz.md     # AI dev guidelines
```

---

## Architecture

### Single-file design
Everything lives in `KeyboardTran.py`. No packages, no imports beyond stdlib.

```
KeyboardTran.py
├── EN_TO_TH              # Kedmanee layout dict (EN key → Thai char)
├── TH_TO_EN              # Reverse map (first-seen-wins, fixes collision bug)
├── REAL_EN               # Set of real English words that should NOT be converted
├── en_to_th(text)        # Convert EN keystrokes → Thai chars
├── th_to_en(text)        # Convert Thai chars → EN keystrokes (ASCII pass-through)
├── fix(text)             # Main entry point — auto-detect direction + convert
├── _fix_ascii_segment()  # EN→TH mode: process token by token
├── _fix_token()          # Decide: convert this token or keep it?
├── get_clipboard()       # Read macOS clipboard (pbpaste)
├── copy_to_clipboard()   # Write macOS clipboard (pbcopy)
└── main()                # CLI: interactive / --clip / argument mode
```

### Conversion Logic

```python
fix(text):
    has_thai = bool(re.search(r'[\u0E00-\u0E7F]', text))

    if has_thai:
        # TH→EN mode — split into segments
        # Thai segment  → th_to_en()
        # ASCII segment → _fix_ascii_segment()
    else:
        # EN→TH mode — token by token
        _fix_ascii_segment(text)

_fix_token(token):
    1. token.lower() in REAL_EN      → keep  (meeting, hello, ok, etc.)
    2. re.match(r'^\d+$', token)     → keep  (pure numbers: 500, 2024)
    3. mappable_chars / len > 0.3    → en_to_th()
    4. otherwise                     → keep
```

### Key Bug Fixes (DO NOT REVERT)

**1. Collision fix**
Layout has both `','` → `'ม'` and `'}'` → `','`, causing last-write-wins collision where `'ม'` → `'}'` instead of `'ม'` → `','`.
Fixed with first-seen-wins:
```python
TH_TO_EN = {}
for k, v in EN_TO_TH.items():
    if v not in TH_TO_EN:
        TH_TO_EN[v] = k
```

**2. ASCII pass-through**
`th_to_en()` skips ASCII characters (`ord(c) < 128`) so commas, spaces, digits, and real EN words pass through unchanged.

**3. macOS N=์ fix**
macOS Thai Kedmanee layout uses `N` = `์`, not `V` = `์` as in the generic TIS spec.
Verified directly against user's keyboard. Do not change.

---

## Layout Details

Thai Kedmanee (TIS 820-2531) — macOS version

| Key | Thai | Note |
|-----|------|------|
| `N` | `์`  | macOS specific (generic spec uses `V`) |
| `V` | `ฒ`  | macOS specific (generic spec uses `N`) |

---

## Test Results

```
accuracy_test.py:
  Pure Thai    (10 cases) :  9/10  — 90%  exact match | 94%  char accuracy
  Mixed TH+EN  (10 cases) : 10/10  — 100% exact match | 100% char accuracy
  Overall      (20 cases) : 19/20  — 95%  exact match | 97%  char accuracy

RoundTripTest.py:
  EN→TH→EN roundtrip : 83/91 — 91% pass
  8 failures = symbol collisions (/, -, ., %) — expected, not bugs
  Real sentences     :  7/7  — 100% roundtrip
```

---

## Usage

```bash
# Interactive mode (recommended)
kbt

# Clipboard mode — copy garbled text first, then press ↑ to recall command
kbt --clip

# Direct input
kbt "garbled text here"

# Update kbt after editing KeyboardTran.py
sudo cp KeyboardTran.py /usr/local/bin/kbt
```

---

## Known Limitations

- **Ambiguous words** like `fine` — no way to know if user meant English "fine" or Thai "ฟิน" without context
- **Proper nouns** (`Game`, `Bank`) — may get converted if not in REAL_EN list
- **Code blocks** — no detection; Thai chars inside code will get converted
- **Pattachote layout** — not supported (roadmap)

---

## Roadmap

- [ ] Pattachote layout support
- [ ] Makefile for auto-update kbt
- [ ] Expand REAL_EN word list
- [ ] More accuracy test cases