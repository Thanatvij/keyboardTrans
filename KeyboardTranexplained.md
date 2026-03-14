# KeyboardTran.py — อธิบายการทำงาน

## มันทำอะไร?

แก้ข้อความที่พิมพ์ผิด keyboard layout **Kedmanee** โดยไม่ต้องต่อ internet ไม่เสีย token

```
input:  l;ylfu8iy[ แสฟีกำ gxHopy'w'[hk'
output: สวัสดีครับ claude เป็นยังไงบ้าง
```

---

## วิธีใช้

```bash
cd keyboardTrans

# แนะนำ — พิมพ์ได้เรื่อยๆ ผลก็อปกลับ clipboard อัตโนมัติ
python3 KeyboardTran.py

# ก็อปข้อความผิดไว้ก่อน → กดลูกศรขึ้นเรียก command เก่า → Enter
python3 KeyboardTran.py --clip
```

---

## Logic หลัก — `fix(text)`

```
มี Thai chars ในข้อความ?
│
├── YES → TH→EN mode
│         แยกเป็น segments ด้วย Thai/non-Thai
│         Thai segment → th_to_en()
│         ASCII segment → ดู token by token
│                         real EN word? → keep
│                         อื่นๆ → en_to_th()
│
└── NO  → EN→TH mode (token by token)
          real EN word? → keep
          pure number?  → keep
          อื่นๆ         → en_to_th()
```

**ตัวอย่าง:**
```
"สวัสดี hello"
 ^^^^^^^       → Thai segment → th_to_en() → "lhkjfu"
         ^^^^^  → ASCII, "hello" in REAL_EN → keep

output: "lhkjfu hello"
```

---

## ส่วนที่ 1 — Layout Map

```python
EN_TO_TH = {
    'a': 'ฟ',  # กด a ได้ ฟ
    's': 'ห',  # กด s ได้ ห
    'd': 'ก',  # กด d ได้ ก
    ...
}
```

เป็น dict ของ Kedmanee layout ทั้งหมด 94 คู่ ครอบคลุมทุก key รวม Shift

---

## ส่วนที่ 2 — Reverse Map (TH → EN)

```python
TH_TO_EN = {}
for k, v in EN_TO_TH.items():
    if v not in TH_TO_EN:   # first-seen-wins
        TH_TO_EN[v] = k
```

**ทำไมต้อง first-seen-wins?**

layout มี collision:
- `','` → `'ม'`  (กด comma ได้ ม)
- `'}'` → `','`  (กด } ได้ comma)

ถ้าใช้ `{v: k for k, v in ...}` แบบปกติ
`ม` จะ reverse เป็น `}` ผิด!

first-seen-wins ทำให้ `ม` → `','` ถูกต้อง ✅

---

## ส่วนที่ 3 — REAL_EN (คำอังกฤษที่ไม่แปล)

```python
REAL_EN = {"meeting", "hello", "ok", "claude", "python", ...}
```

ถ้าไม่มี list นี้ `"meeting"` จะถูกแปลเป็น Thai มั่วๆ

**ตัวอย่างที่แก้ได้:**
```
"ผมไป meeting วันนี้"
         ^^^^^^^  → in REAL_EN → keep as "meeting"
output: ",;,wx; meeting ;'ou0"
```

---

## ส่วนที่ 4 — th_to_en()

```python
def th_to_en(text: str) -> str:
    result = []
    for c in text:
        if ord(c) < 128:   # ASCII (space, comma, numbers) → ผ่านไปเลย
            result.append(c)
        else:               # Thai → แปลด้วย reverse map
            result.append(TH_TO_EN.get(c, c))
    return "".join(result)
```

**ทำไมต้อง check `ord(c) < 128`?**

ถ้าไม่ check comma `,` ใน Thai text จะถูกแปลเป็น `}` ผิด
เพราะ `,` อยู่ใน TH_TO_EN map ด้วย

---

## ส่วนที่ 5 — _fix_token()

```python
def _fix_token(token: str) -> str:
    if token.lower() in REAL_EN:          # real EN → keep
        return token
    if re.match(r"^\d+$", token):         # 123 → keep (pure digits)
        return token                       # แต่ "9kpsjk" ไม่ใช่ pure digit → แปล
    mappable = sum(1 for c in token if c in _MAPPABLE)
    if mappable / len(token) > 0.3:       # >30% chars อยู่ใน layout → แปล
        return en_to_th(token)
    return token                           # อื่นๆ → keep
```

**ทำไม 30% threshold?**

บาง token มี special chars ปน เช่น `9kpsjk`
- `9` อยู่ใน layout (9 → ต)
- `k`, `p`, `s`, `j` อยู่ใน layout
- ratio = 6/6 = 100% → แปล ✅

---

## ข้อจำกัด

| กรณี | ผลลัพธ์ |
|------|---------|
| `fine` (EN จริง หรือ ฟิน?) | ❌ เดาไม่ได้ ไม่มี context |
| `pls msg tmr` (EN ย่อ) | ✅ อยู่ใน REAL_EN แล้ว |
| ชื่อคน เช่น `Game`, `Bank` | ⚠️ ต้องเพิ่มใน REAL_EN เอง |
| Code block | ⚠️ Thai string ใน code จะถูกแปล |
| ประโยคยาวมาก ambiguous | ❌ ต้องการ LLM |

**80-90% ของ use case ทั่วไปทำได้ถูกต้องครับ**
