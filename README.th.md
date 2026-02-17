# KeyboardTrans

ตัวแปลงคีย์บอร์ดไทย-อังกฤษ - ไลบรารี Python แบบโมดูลาร์และทดสอบได้สำหรับแปลงระหว่างแป้นพิมพ์ไทยและอังกฤษตามรูปแบบเค้าโครงแป้นพิมพ์

## คุณสมบัติ (Features)

- **สถาปัตยกรรมแบบโมดูล**: การแยกความรับผิดชอบอย่างชัดเจน ประกอบด้วยการจัดการเค้าโครง, ตรรกะการแปลง, และกลยุทธ์การให้คะแนน
- **การตรวจสอบแบบ Bijective**: รับประกันความถูกต้องของการแม็ป EN ↔ TH แบบ 1:1 ในการเริ่มต้น
- **พฤติกรรมแบบ Deterministic**: ข้อมูลนำเข้าเดิมจะให้ผลลัพธ์เดิมเสมอ
- **Type Safety**: มี type hints ทั้งหมด
- **ขยายได้**: รูปแบบ strategy สำหรับกลยุทธ์การให้คะแนนแบบกำหนดเอง
- **ทดสอบอย่างครบถ้วน**: ชุดทดสอบ pytest ที่ครอบคลุม (84 ข้อทดสอบ)
- **ไม่มีการพึ่งพาภายนอก**: ใช้ไลบรารีมาตรฐานของ Python เท่านั้น

### การให้คะแนน V3.1 (Scoring V3.1)

ไลบรารีใช้ **WeightedScoringStrategy** (Scoring V3.1) ที่มีการให้คะแนนแบบหลายปัจจัยที่ปรับปรุงแล้ว:

**สูตรการให้คะแนนแบบถ่วงน้ำหนัก:**
```
final_score = 0.35 * dictionary_score
           + 0.20 * script_ratio_score
           + 0.25 * validity_score
           + 0.10 * boundary_score
           - 0.10 * garbage_score
```

**ประเภทการให้คะแนน:**
- **Dictionary Score** (35%): การจับคู่กับคำศัพท์
- **Script Ratio Score** (20%): การตรวจจับอัตราส่วนของ ASCII สำหรับอังกฤษ, อัตราส่วน Unicode ไทยสำหรับภาษาไทย
- **Validity Score** (25%): การรับรู้รูปแบบคำที่ถูกต้อง
- **Boundary Score** (10%): การวิเคราะห์อัตราส่วนของเว้นวรรค
- **Garbage Penalty** (-10%): การหักคะแนนจาก spam/การทำซ้ำและความหนาแน่นของสัญลักษณ์
- **Vowelless Penalty** (V3.1): ตรวจจับ ASCII โดยไม่มี vowel เป็น "garbage English"

**ตรรกะการตัดสินใจ (V3.1):**
- การตรวจจับการกลับ layout แบบใช้การปรับปรุง (threshold 0.08, ลดลงจาก 0.1)
- การกู้คืนสำหรับข้อความที่มีความมั่นใจต่ำ (threshold 0.12)
- การหักคะแนนของ vowelless ลดคะแนน English สำหรับข้อความ garbage (threshold 0.6)
- ไม่มีกฎล็อคภาษาคงที่
- ไม่มีการบล็อกการแปลงจาก threshold ของความมั่นใจ

**ความครอบคลุมของคำศัพท์:**
- อังกฤษ: 90 คำทั่วไป
- ไทย: 90 คำทั่วไป

**การปรับปรุงใน V3.1:**
- ✓ ลด IMPROVEMENT_THRESHOLD จาก 0.1 เป็น 0.08 (flip ง่ายขึ้น)
- ✓ เพิ่ม vowelless penalty เพื่อตรวจจับ keyboard garbage
- ✓ เพิ่ม boundary score สำหรับการวิเคราะห์อัตราส่วนของเว้นวรรค
- ✓ เพิ่ม layout noise score สำหรับการตรวจจับการรวมกันของสัญลักษณ์
- ✓ เพิ่มเมธอด auto_correct() ด้วยการเชื่อมต่อ pythainlp
- ✓ CLI ใช้ segment-aware conversion (ไม่ใช้ WeightedScoringStrategy)
- ✓ converter.py th_to_en() ส่งผ่าน ASCII โดยไม่เปลี่ยนแปลง (แก้ไขปัญหา comma)
- ✓ ไม่มี pythainlp dependency ใน CLI (ใช้ TextConverter โดยตรง)
- ✓ ไม่มี Machine Learning - การให้คะแนนแบบ deterministic ล้วน

## การติดตั้ง (Installation)

```bash
# จาก source
cd keyboardTrans
pip install -e .

# สำหรับการพัฒนา
pip install -e ".[dev]"
```

## เริ่มต้นอย่างรวดเร็ว (Quick Start)

### Python API

```python
from keyboardtrans.config.layouts import get_kedmanee_layout
from keyboardtrans.core.layout import KeyboardLayout
from keyboardtrans.core.converter import TextConverter

# สร้าง layout และ converter
layout = KeyboardLayout("kedmanee", get_kedmanee_layout())
converter = TextConverter(layout)

# แปลงข้อความ
thai_text = converter.en_to_th("hello")
english_keystrokes = converter.th_to_en("สวัสดี")

print(thai_text)  # แปลงแป้นพิมพ์อังกฤษเป็นตัวอักษรไทย
```

### บรรทัดคำสั่ง (Command Line)

```bash
# เรียกใช้ CLI แบบโต้ตอบ (ด้วย segment-aware conversion)
python -m keyboardtrans.cli

# หรือใช้คำสั่งที่ติดตั้งแล้ว
keyboardtrans

# เปิดใช้ verbose mode เพื่อดูโหมดการแปลง
python -m keyboardtrans.cli --verbose
```

## สถาปัตยกรรม (Architecture)

```
keyboardtrans/
├── __init__.py           # การส่งออกแพ็กเกจ
├── cli.py                # อินเทอร์เฟซบรรทัดคำสั่ง
├── exceptions.py         # ข้อยกเว้นแบบกำหนดเอง
├── core/
│   ├── layout.py         # การจัดการและตรวจสอบ layout
│   ├── converter.py      # ตรรกะการแปลงข้อความ
│   └── scoring.py         # การให้คะแนนตามคำศัพท์
├── strategies/
│   ├── base.py           # อินเทอร์เฟซ strategy แบบนามธรรม
│   ├── simple.py         # การให้คะแนนแบบง่ายพร้อมคำศัพท์ในตัว (V1)
│   └── weighted.py      # การให้คะแนนแบบถ่วงน้ำหนักพร้อมหลายปัจจัย (V2.1)
└── config/
    ├── layouts/
    │   └── kedmanee.py   # คำนิยาม layout Kedmanee
    └── vocab/
        ├── en_words.json  # คำศัพท์ภาษาอังกฤษ
        └── th_words.json  # คำศัพท์ภาษาไทย
```

## การใช้งาน (Usage)

### การแปลงแบบอัจฉริยะพร้อมการตรวจจับภาษา (Scoring V2.1)

```python
from keyboardtrans.cli import KeyboardTransApp

# สร้าง app ด้วย Kedmanee layout
app = KeyboardTransApp()

# Smart convert ใช้ segment-aware conversion (Thai check → TH→EN, else EN→TH with token handling)
# EN→TH mode เก็บคำ EN จริงและตัวเลขเท่านั้น แปลง input ผสมเช่น "9kpsjk" เป็นไทย
result = app._smart_convert("hello")
print(result)  # คืนค่าข้อความที่แก้ไขแล้ว
```

### การใช้ WeightedScoringStrategy V2.1 โดยตรง

```python
from keyboardtrans.strategies.weighted import WeightedScoringStrategy
from keyboardtrans.core.converter import TextConverter
from keyboardtrans.core.layout import KeyboardLayout

# สร้าง layout และ converter
layout = KeyboardLayout("kedmanee", get_kedmanee_layout())
converter = TextConverter(layout)

# ใช้ WeightedScoringStrategy
strategy = WeightedScoringStrategy()
th_score = strategy.score_thai("สวัสดีครับ")
en_score = strategy.score_english("hello world")

# รับการตัดสินใจภาษาพร้อมตรรกะแบบใช้การปรับปรุง
original = "สวัสดี"
th_version = converter.en_to_th(original)
en_version = converter.th_to_en(original)
result, reason = strategy.get_language_decision(original, th_version, en_version)

print(f"Result: {result}")
print(f"Reason: {reason}")  # เช่น "keep_original_no_improvement", "flipped_to_english_improves_confidence"
```

### กลยุทธ์การให้คะแนนแบบกำหนดเอง

```python
from keyboardtrans.strategies.base import BaseScoringStrategy

class MyScoringStrategy(BaseScoringStrategy):
    def score_english(self, text: str) -> float:
        # ตรรกะการให้คะแนนแบบกำหนดเอง
        pass

    def score_thai(self, text: str) -> float:
        # ตรรกะการให้คะแนนแบบกำหนดเอง
        pass

# ใช้กลยุทธ์แบบกำหนดเอง
from keyboardtrans.cli import KeyboardTransApp
app = KeyboardTransApp()
app._strategy = MyScoringStrategy()
```

### หลาย Layout

```python
from keyboardtrans.core.layout import KeyboardLayout, LayoutRegistry

# สร้าง registry
registry = LayoutRegistry()

# ลงทะเบียน layouts
kedmanee = KeyboardLayout("kedmanee", get_kedmanee_layout())
registry.register(kedmanee)

# ดึง layout
layout = registry.get("kedmanee")
```

## การพัฒนา (Development)

### การรันทดสอบ

```bash
# รันทดสอบทั้งหมด
pytest

# รันพร้อม coverage
pytest --cov=keyboardtrans

# รันไฟล์ทดสอบเฉพาะ
pytest tests/test_layout.py

# รันทดสอบเฉพาะ
pytest tests/test_converter.py::TestTextConverter::test_en_to_th_basic_conversion
```

### คุณภาพโค้ด

```bash
# จัดรูปแบบโค้ด
black .

# ตรวจสอบโค้ด
ruff check .

# ตรวจสอบ type
mypy keyboardtrans
```

## รูปแบบแป้นพิมพ์ (Keyboard Layouts)

### ไทย Kedmanee

ไลบรารีนี้รวมรูปแบบแป้นพิมพ์ไทย Kedmanee (TIS 820-2531) การแม็ปได้รับการตรวจสอบเพื่อให้แน่ใจว่ามีความสัมพันธ์แบบ 1:1 (bijective) เพื่อให้สามารถแปลงได้ทั้งสองทิศทาง

### การเพิ่ม Layout ใหม่

1. สร้างไฟล์ layout ใหม่ใน `config/layouts/`
2. กำหนดพจนานุกรมการแม็ป EN → TH
3. ลงทะเบียน layout โดยใช้ `KeyboardLayout`

## อ้างอิง API (API Reference)

### `KeyboardLayout`

แทนรูปแบบแป้นพิมพ์ด้วยการแม็ปแบบสองทิศทาง EN ↔ TH

**Methods:**
- `__init__(name: str, en_to_th: Dict[str, str])`: เริ่มต้น layout
- `property en_to_th`: รับการแม็ป EN → TH (ไม่เปลี่ยนแปลง)
- `property th_to_en`: รับการแม็ป TH → EN (ไม่เปลี่ยนแปลง, คำนวณเมื่อต้องการ)

### `TextConverter`

แปลงข้อความระหว่างแป้นพิมพ์อังกฤษและตัวอักษรไทย

**Methods:**
- `__init__(layout: KeyboardLayout)`: เริ่มต้น converter
- `en_to_th(text: str) -> str`: แปลงภาษาอังกฤษเป็นไทย
- `th_to_en(text: str) -> str`: แปลงภาษาไทยเป็นอังกฤษ

### `WeightedScoringStrategy` (Scoring V2.1)

กลยุทธ์การให้คะแนนแบบถ่วงน้ำหนักที่ปรับปรุงแล้วพร้อมการวิเคราะห์หลายปัจจัยและตรรกะการตัดสินใจแบบใช้การปรับปรุง

**Methods:**
- `score_english(text: str) -> float`: ให้คะแนนเป็นภาษาอังกฤษ [0, 1]
- `score_thai(text: str) -> float`: ให้คะแนนเป็นภาษาไทย [0, 1]
- `get_language_decision(original, th_version, en_version) -> Tuple[str, str]`: ทำการตัดสินใจสุดท้ายพร้อมตรรกะแบบใช้การปรับปรุง

**Constants:**
- `IMPROVEMENT_THRESHOLD = 0.1`: การปรับปรุงขั้นต่ำที่ต้องการเพื่อกลับ (การตรวจจับการกลับ layout)
- การรักษาความมั่นใจขั้นต่ำ: ข้อความต้นฉบับที่มีคะแนน >= 0.6 จะถูกเก็บไว้เสมอ

### `SimpleScoringStrategy` (Scoring V1)

กลยุทธ์การให้คะแนนแบบง่ายพร้อมคำศัพท์ในตัว (คงไว้เพื่อความเข้ากันได้กับระบบเดิม)

**Methods:**
- `score_english(text: str) -> float`: ให้คะแนนเป็นภาษาอังกฤษ [0, 1]
- `score_thai(text: str) -> float`: ให้คะแนนเป็นภาษาไทย [0, 1]

## การมีส่วนร่วม (Contributing)

1. Fork repository
2. สร้าง feature branch (`git checkout -b feat/amazing-feature`)
3. ทำการเปลี่ยนแปลง
4. เพิ่มการทดสอบสำหรับฟังก์ชันใหม่
5. ตรวจสอบให้แน่ใจว่าทดสอบทั้งหมดผ่าน (`pytest`)
6. Commit การเปลี่ยนแปลง
7. พุชไปยัง branch (`git push origin feat/amazing-feature`)
8. เปิด Pull Request

## สัญญาอนุญาต (License)

MIT License - ดูรายละเอียดในไฟล์ LICENSE

## แผนงาน (Roadmap)

- [x] การให้คะแนนแบบถ่วงน้ำหนักหลายปัจจัย (V3.1) - **เสร็จสิ้น**
- [x] Vowelless penalty สำหรับการตรวจจับ garbage - **เสร็จสิ้น**
- [x] Boundary score สำหรับการวิเคราะห์อัตราส่วนของเว้นวรรค - **เสร็จสิ้น**
- [x] ลด IMPROVEMENT_THRESHOLD เป็น 0.08 - **เสร็จสิ้น**
- [x] CLI segment-aware conversion (ไม่ใช้ WeightedScoringStrategy) - **เสร็จสิ้น**
- [x] converter.py ส่งผ่าน ASCII ใน th_to_en - **เสร็จสิ้น**
- [ ] รองรับ layout Pattachote
- [ ] กลยุทธ์การให้คะแนนแบบ N-gram language model
- [ ] Beam search สำหรับการแปลงที่ไม่ชัดเจน
- [ ] Web API
- [ ] แอปพลิเคชัน GUI

## ขอบคุณ (Acknowledgments)

- มาตรฐานอุตสาหกรรมไทย TIS 820-2531 สำหรับข้อกำหนด layout Kedmanee
- แรงบันดาลใจเดิมจากความต้องการที่จะแก้ไขปัญหาการป้อนข้อมูลภาษาผสมบนแป้นพิมพ์
