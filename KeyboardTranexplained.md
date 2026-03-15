---

## Test Results

```bash
python3 accuracy_test.py
```
```
Pure Thai    (10 cases) :  9/10  — 90%  exact match | 94%  char accuracy
Mixed TH+EN  (10 cases) : 10/10  — 100% exact match | 100% char accuracy
Overall      (20 cases) : 19/20  — 95%  exact match | 97%  char accuracy
```

```bash
python3 RoundTripTest.py
```
```
EN→TH→EN roundtrip : 83/91 — 91% pass
Real sentences     :  7/7  — 100%
```

---

## ไฟล์ทั้งหมด

```
KeyboardTran.py          — เครื่องมือหลัก
accuracy_test.py         — ทดสอบ 20 real-world cases
RoundTripTest.py         — ทดสอบ roundtrip ทุก char
KeyboardTranexplained.md — ไฟล์นี้
README.md                — English docs
README_th.md             — Thai docs
PROJECT_CONTEXT.md       — Technical context สำหรับ AI dev
```

---

> **สร้างโดย ThanatV.**  
> สาขาวิชาเทคโนโลยีและนวัตกรรมดิจิทัล (Digital Technology and Innovation)  
> คณะวิทยาศาสตร์และเทคโนโลยี (Faculty of Science and Technology)  
> มหาวิทยาลัยธรรมศาสตร์ (Thammasat University)  
>
> AI pair-programmed with **Claude Sonnet 4.6** by Anthropic