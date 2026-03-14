#!/usr/bin/env python3
"""
roundtrip_test.py — ทดสอบว่า layout ถูกต้องครบทุกตัวอักษร
Thai → EN → Thai ต้องได้เหมือนเดิม
"""

import sys
sys.path.insert(0, "/Users/thanatv./Desktop/Thanatv/Python/keyboardTrans")
from KeyboardTran import EN_TO_TH, TH_TO_EN, en_to_th, th_to_en

print("=" * 55)
print("  Roundtrip Test: Thai → EN → Thai")
print("=" * 55)

# ทดสอบทุก Thai char ใน layout
passed = 0
failed = 0

for en_key, th_char in sorted(EN_TO_TH.items()):
    # Thai → EN → Thai
    en_result = th_to_en(th_char)
    back = en_to_th(en_result)

    if back == th_char:
        passed += 1
    else:
        failed += 1
        print(f"❌ '{en_key}' → '{th_char}' → '{en_result}' → '{back}'")

print(f"\nEN→TH→EN roundtrip: {passed}/{passed+failed} passed")

# ทดสอบประโยคจริง
print("\n" + "=" * 55)
print("  Real Sentence Roundtrip")
print("=" * 55)

sentences = [
    "สวัสดีครับ",
    "วันนี้อากาศดีมาก",
    "ขอบคุณมากนะครับ",
    "โปรเจกต์เสร็จแล้วครับ",
    "ไปประชุมตอนบ่ายสามโมง",
    "วันศุกร์นะ",
    "แวะมาหาได้นะครับ",
]

for s in sentences:
    en = th_to_en(s)
    back = en_to_th(en)
    ok = "✅" if back == s else "❌"
    print(f"{ok} '{s}' → '{en}' → '{back}'")