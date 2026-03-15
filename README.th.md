🇹🇭 ภาษาไทย | [🇬🇧 English](README.md)
# KeyboardTrans 🇹🇭⇌🔤

> แก้ข้อความที่พิมพ์ผิด keyboard layout ได้ทันที  
> ลืมเปลี่ยนภาษาก่อนพิมพ์? แค่รัน `kbt` ก็จบ

---

## ปัญหาที่แก้ได้

ใครๆ ก็เคยเจอ — พิมพ์ไปทั้งประโยคแล้วได้แบบนี้:

```
l;ylfu8iy[;yoouhgxHopy'w'[hk'
```

ทั้งที่ตั้งใจพิมพ์ว่า:

```
สวัสดีครับวันนี้เป็นยังไงบ้าง
```

KeyboardTrans แก้ได้ใน milliseconds ทำงานบนเครื่อง ไม่ต้องต่อ internet ไม่เสีย token

---

## ตัวอย่าง

```bash
$ kbt
พิมพ์: l;ylfu8iy[ แสฟีกำ gxHopy'w'[hk'
  → สวัสดีครับ claude เป็นยังไงบ้าง

พิมพ์: ;yoouhwx ทำำะรืเ dujF,'8iy[
  → วันนี้ไป meeting กี่โมงครับ

พิมพ์: Fxig0d9NgliH0c]h;8iy[
  → โปรเจกต์เสร็จแล้วครับ
```

---

## ความสามารถ

- ✅ แปลสองทิศทาง — ไทย→EN และ EN→ไทย
- ✅ รองรับภาษาผสม — ไทย+อังกฤษในประโยคเดียวกัน
- ✅똑똑รู้จักคำ EN จริง — `meeting`, `hello`, `ok` ไม่ถูกแปล
- ✅ ตัวเลขปลอดภัย — `500`, `2024` ผ่านไปเลย
- ✅ Copy clipboard อัตโนมัติ — ผลลัพธ์พร้อมวางทันที
- ✅ ทำงาน offline — ไม่มี API ไม่เสีย token
- ✅ ไฟล์เดียว ไม่มี dependencies

---

## ติดตั้ง

ต้องการแค่ Python 3.6+

```bash
git clone https://github.com/Thanatvij/keyboardTrans.git
cd keyboardTrans

sudo cp KeyboardTran.py /usr/local/bin/kbt
sudo chmod +x /usr/local/bin/kbt
```

อัปเดตหลังแก้ไขไฟล์:
```bash
sudo cp KeyboardTran.py /usr/local/bin/kbt
```

---

## วิธีใช้

**Interactive mode — แนะนำที่สุด**
```bash
kbt
```
พิมพ์ข้อความ กด Enter ผลลัพธ์ copy ไป clipboard อัตโนมัติ

**Clipboard mode**
```bash
# ก็อปข้อความที่ผิดก่อน
# จากนั้นกดลูกศรขึ้น ↑ เรียก command เก่า ไม่ต้องก็อป kbt ทับ
kbt --clip
# วางได้เลย ผลอยู่ใน clipboard แล้ว
```

**ใส่ตรงๆ**
```bash
kbt "ข้อความที่พิมพ์ผิด"
```

---

## ตัวอย่างจริง

| พิมพ์มา (ผิด) | ได้ผล (ถูก) |
|---|---|
| `l;ylfu8iy[` | `สวัสดีครับ` |
| `สวัสดีครับ` | `l;ylfu8iy[` |
| `;yoouhwx ทำำะรืเ dujF,'8iy[` | `วันนี้ไป meeting กี่โมงครับ` |
| `-v[86I,kdg]p ิพน` | `ขอบคุณมากเลย bro` |
| `Fxig0d9NgliH0c]h;8iy[` | `โปรเจกต์เสร็จแล้วครับ` |

---

## ผลการทดสอบ

```
ไทยล้วน        (10 cases) : 10/10 — 100% exact | 100% char accuracy
ผสมไทย+EN      (10 cases) : 10/10  — 100% exact | 100% char accuracy
รวม            (27 cases) : 27/27 — 100% exact | 100% char accuracy
:ตัวเลขผสม    (7 cases)  :  7/7  — 100% exact | 100% char accuracy
```

---

## สิ่งที่ควรรู้ก่อนใช้

- คำที่กำกวม เช่น `fine` — ไม่มีทางรู้ว่าหมายถึงคำอังกฤษ หรือ "ฟิน" ถ้าไม่มี context
- ชื่อเฉพาะ เช่น `Game`, `Bank` — อาจถูกแปลถ้าไม่อยู่ใน word list
- ยังไม่รองรับ layout Pattachote

---

## License

MIT License — Copyright (c) 2025 **ThanatV.**

ใช้ได้ฟรี แก้ไขได้ เผยแพร่ได้ แค่เก็บชื่อเจ้าของไว้

---

> สร้างโดย **ThanatV.** — สาขาวิชาเทคโนโลยีและนวัตกรรมดิจิทัล คณะวิทยาศาสตร์และเทคโนโลยี มหาวิทยาลัยธรรมศาสตร์  
> AI pair-programmed with **Claude Sonnet 4.6** by Anthropic