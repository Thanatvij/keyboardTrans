# KeyboardTrans 🇹🇭⇌🔤

> **Fix Thai-English keyboard layout mistakes instantly.**  
> Typed in the wrong language? Just run `kbt` and it's fixed.

---

## The Problem

Thai developers and users constantly switch between Thai and English keyboard layouts.  
One moment of forgetting to switch leads to gibberish like:

```
l;ylfu8iy[;yoouhgxHopy'w'[hk'
```

When you actually meant:

```
สวัสดีครับวันนี้เป็นยังไงบ้าง
```

**KeyboardTrans fixes this in milliseconds — locally, offline, with zero API calls.**

---

## Demo

```bash
$ kbt
  KeyboardTrans — แก้ข้อความพิมพ์ผิด layout
──────────────────────────────────────────────
พิมพ์: l;ylfu8iy[ แสฟีกำ gxHopy'w'[hk'
  → สวัสดีครับ claude เป็นยังไงบ้าง
  📋 คัดลอกผลลัพธ์ไปยัง clipboard แล้ว

พิมพ์: ;yoouhwx ทำำะรืเ dujF,'8iy[
  → วันนี้ไป meeting กี่โมงครับ

พิมพ์: Fxig0d9NgliH0c]h;8iy[
  → โปรเจกต์เสร็จแล้วครับ
```

---

## Features

- ✅ **Bidirectional** — Thai→EN and EN→Thai
- ✅ **Mixed input** — Handles Thai + English in the same sentence
- ✅ **Smart detection** — Preserves real English words (`meeting`, `hello`, `ok`) automatically
- ✅ **Number safe** — Pure numbers (`500`, `2024`) pass through unchanged
- ✅ **Auto clipboard** — Result is copied to clipboard automatically (macOS)
- ✅ **Offline** — No internet, no API, no tokens consumed
- ✅ **Fast** — Runs in milliseconds, single Python file, zero dependencies
- ✅ **macOS optimized** — Matches actual macOS Thai Kedmanee layout (`N` = `์`)

---

## Installation

**Requirements:** Python 3.6+ (no external dependencies)

```bash
# Clone the repo
git clone https://github.com/Thanatvij/keyboardTrans.git
cd keyboardTrans

# Install as global command (recommended)
sudo cp KeyboardTran.py /usr/local/bin/kbt
sudo chmod +x /usr/local/bin/kbt

# Done! Run from anywhere
kbt
```

**Update after editing:**
```bash
sudo cp KeyboardTran.py /usr/local/bin/kbt
```

---

## Usage

### Interactive Mode (Recommended)
```bash
kbt
```
Type your mixed-up text, press Enter. Result is printed and auto-copied to clipboard.

### Clipboard Mode
```bash
# 1. Copy your garbled text first
# 2. Press ↑ to recall last command (no need to re-copy!)
kbt --clip
# 3. Paste — result is already in clipboard
```

### Direct Input
```bash
kbt "l;ylfu8iy[;yoouhgxHopy'w'[hk'"
# → สวัสดีครับวันนี้เป็นยังไงบ้าง
```

---

## How It Works

KeyboardTrans uses the **Thai Kedmanee keyboard layout** (TIS 820-2531) for deterministic character-by-character mapping.

### Detection Logic

```
Input text
    │
    ├─ Contains Thai characters (U+0E00–U+0E7F)?
    │       │
    │      YES → TH→EN Mode (segment-aware)
    │              ├─ Thai segment   → th_to_en()
    │              └─ ASCII segment  → keep if real EN word
    │                                  else → en_to_th()
    │
    └─    NO  → EN→TH Mode (token-by-token)
                   ├─ Real EN word   → keep  ("meeting", "hello", "ok" ...)
                   ├─ Pure number    → keep  (500, 2024)
                   └─ Other token   → en_to_th()
```

### Real-World Examples

| Input (garbled) | Output (fixed) | Mode |
|---|---|---|
| `l;ylfu8iy[` | `สวัสดีครับ` | EN→TH |
| `สวัสดีครับ` | `l;ylfu8iy[` | TH→EN |
| `;yoouhwx ทำำะรืเ dujF,'8iy[` | `วันนี้ไป meeting กี่โมงครับ` | Mixed |
| `-v[86I,kdg]p ิพน` | `ขอบคุณมากเลย bro` | Mixed |
| `Fxig0d9NgliH0c]h;8iy[` | `โปรเจกต์เสร็จแล้วครับ` | EN→TH |

### Key Technical Details

**Collision fix:** Layout maps both `,` → `ม` and `}` → `,`, causing reverse-mapping collision.  
Fixed with **first-seen-wins**:
```python
TH_TO_EN = {}
for k, v in EN_TO_TH.items():
    if v not in TH_TO_EN:
        TH_TO_EN[v] = k
```

**ASCII pass-through:** `th_to_en()` skips ASCII characters (`ord(c) < 128`) so commas, spaces, and numbers survive intact.

**macOS layout fix:** macOS Thai Kedmanee uses `N` = `์` (differs from generic TIS spec).

---

## Accuracy

Tested on 20 real-world Thai-English mixed sentences:

```
Pure Thai input    (10 cases) :  9/10  — 90%  exact match | 94%  char accuracy
Mixed Thai+EN      (10 cases) : 10/10  — 100% exact match | 100% char accuracy
─────────────────────────────────────────────────────────────────────────────
Overall            (20 cases) : 19/20  — 95%  exact match | 97%  char accuracy

Roundtrip test     (91 chars) : 83/91  — 91%  pass
  └─ 8 failures = symbol collisions (/, -, ., %) — expected behavior
  └─ Real sentences: 7/7 — 100% roundtrip
```

Run tests yourself:
```bash
python3 accuracy_test.py
python3 RoundTripTest.py
```

---

## Project Files

```
keyboardTrans/
├── KeyboardTran.py       # Main tool — everything in one file, no dependencies
├── accuracy_test.py      # 20 real-world test cases with scoring
├── RoundTripTest.py      # Roundtrip validation for all layout characters
├── README.md             # This file
├── README_th.md          # Thai documentation  
└── PROJECT_CONTEXT.md    # Technical context for AI-assisted development
```

---

## Known Limitations

| Case | Behavior | Reason |
|---|---|---|
| `fine` | Kept as-is | Ambiguous: English word or ฟิน? No context available |
| Proper nouns (`Game`, `Bank`) | May convert | Not in real-EN word list |
| Code blocks | Thai parts get converted | No code-block detection |
| Pattachote layout | Not supported | Kedmanee only (for now) |

---

## Roadmap

- [ ] Pattachote layout support
- [ ] Auto-update script (Makefile)
- [ ] Browser extension
- [ ] Expand real-EN word list

---

## License

MIT License — Copyright (c) 2025 **ThanatV.**

Free to use, copy, modify, and distribute. Just keep the copyright notice.

---

> **Built by [ThanatV.](https://github.com/Thanatvij)** — Digital Technology & Innovation, Thammasat University  
> **AI pair-programmed with [Claude Sonnet 4.6](https://www.anthropic.com/claude) by Anthropic**