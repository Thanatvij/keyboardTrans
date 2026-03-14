#!/usr/bin/env python3
"""
accuracy_test.py — ทดสอบความแม่นยำของ KeyboardTran.py
รัน: python3 accuracy_test.py
"""

import sys
sys.path.insert(0, "/Users/thanatv./Desktop/Thanatv/Python/keyboardTrans/KeyboardTran.py")

from KeyboardTran import fix

# ============================================================
# Dataset: (input ที่พิมพ์ผิด, expected output)
# ============================================================

# --- Pure Thai (พิมพ์ผิด layout ทั้งหมด) ---
PURE_THAI = [
    ("l;ylfu8iy[;yoouhgxHopy'w'[hk'",   "สวัสดีครับวันนี้เป็นยังไงบ้าง"),
    ("z,wxdbo-hk;dy[grnjvog,njv;ko",     "ผมไปกินข้าวกับเพื่อนเมื่อวาน"),
    (";yoouhvkdkLfu,kdg]p",              "วันนี้อากาศดีมากเลย"),
    ("-v[86I,kdot8iy[",                  "ขอบคุณมากนะครับ"),
    ("wxxit=6,9vo[jkplk,F,'",           "ไปประชุมตอนบ่ายสามโมง"),
    ("Fxig0d9NgliH0c]h;8iy[",           "โปรเจกต์เสร็จแล้วครับ"),
    ("]n,gx]ujpo4kKkvudc]h;",           "ลืมเปลี่ยนภาษาอีกแล้ว"),
    ("dbo-hk;py'8iy[",                  "กินข้าวยังครับ"),
    (";yoouhme'kogsonjvp,kd",            "วันนี้ทำงานเหนื่อยมาก"),
    ("c;t,kskwfhot8iy[",  "แวะมาหาได้นะครับ"),
]

# --- Mixed Thai+EN (ผสม) ---
MIXED = [
    (";yoouhwx ทำำะรืเ dujF,'8iy[",         "วันนี้ไป meeting กี่โมงครับ"),
    ("กำยสนั gliH0c]h;ot iv พำอรำไ fh;p",   "deploy เสร็จแล้วนะ รอ review ด้วย"),
    ("]n, ยีห้ แนกำ wxg]p กำฟกสรืำ ri6j'ouh", "ลืม push code ไปเลย deadline พรุ่งนี้"),
    ("wxdbo สีืแ้ fh;pdyo,yhp",              "ไปกิน lunch ด้วยกันมั้ย"),
    ("ผนนท แฟสส 9vo[jkplv'F,'ot8iy[",       "zoom call ตอนบ่ายสองโมงนะครับ"),
    ("ิีเ ouhcdhpkd,kdg]p ้ำสย fh;p",       "bug นี้แก้ยากมากเลย help ด้วย"),
    ("นา 8iy[gfuJp; แ้ำแา .sh",             "ok ครับเดี๋ยว check ให้"),
    ("ยพน่ำแะ ouh กำฟกสรืำ ;yoL6diNot",     "project นี้ deadline วันศุกร์นะ"),
    ("-v[86I,kdg]p ิพน",                    "ขอบคุณมากเลย bro"),
    (";yoouh ไนพา ดพนท ้นทำ 8iy[",          "วันนี้ work from home ครับ"),
]


# ============================================================
# Scoring
# ============================================================

def exact_match(pred: str, expected: str) -> bool:
    return pred.strip() == expected.strip()

def char_accuracy(pred: str, expected: str) -> float:
    """% ตัวอักษรที่ถูกต้อง"""
    correct = sum(p == e for p, e in zip(pred, expected))
    return correct / max(len(expected), 1)

def run_tests(dataset, label):
    print(f"\n{'='*60}")
    print(f"  {label} ({len(dataset)} cases)")
    print(f"{'='*60}")

    exact = 0
    char_acc_total = 0.0

    for i, (inp, expected) in enumerate(dataset, 1):
        pred = fix(inp)
        em = exact_match(pred, expected)
        ca = char_accuracy(pred, expected)

        if em:
            exact += 1
            status = "✅"
        else:
            status = "❌"

        print(f"\n{status} Case {i}")
        print(f"   Input:    {inp}")
        print(f"   Expected: {expected}")
        print(f"   Got:      {pred}")
        if not em:
            print(f"   Char acc: {ca:.0%}")

        char_acc_total += ca

    total = len(dataset)
    print(f"\n{'─'*60}")
    print(f"  Exact Match : {exact}/{total} ({exact/total:.0%})")
    print(f"  Avg Char Acc: {char_acc_total/total:.0%}")
    return exact, total, char_acc_total / total


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    e1, t1, c1 = run_tests(PURE_THAI, "Pure Thai (พิมพ์ผิด layout ทั้งหมด)")
    e2, t2, c2 = run_tests(MIXED,     "Mixed Thai+EN (ผสม)")

    total_exact = e1 + e2
    total_cases = t1 + t2
    avg_char = (c1 * t1 + c2 * t2) / total_cases

    print(f"\n{'='*60}")
    print(f"  OVERALL RESULTS")
    print(f"{'='*60}")
    print(f"  Exact Match : {total_exact}/{total_cases} ({total_exact/total_cases:.0%})")
    print(f"  Avg Char Acc: {avg_char:.0%}")
    print(f"{'='*60}\n")