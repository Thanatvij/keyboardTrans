#!/usr/bin/env python3
"""
KeyboardTran.py — แก้ข้อความที่พิมพ์ผิด keyboard layout (Kedmanee)

วิธีใช้:
  python3 KeyboardTran.py              → interactive mode (แนะนำ)
  python3 KeyboardTran.py "ข้อความ"   → แปลทันที
  python3 KeyboardTran.py --clip       → อ่านจาก clipboard
"""

import re
import sys

# ============================================================
# Kedmanee Layout Map
# EN key → Thai character (ตาม TIS 820-2531)
# ============================================================

EN_TO_TH = {
    '`':'_','1':'ๅ','2':'/','3':'-','4':'ภ','5':'ถ',
    '6':'ุ','7':'ึ','8':'ค','9':'ต','0':'จ','-':'ข','=':'ช',
    '~':'%','!':'+','@':'๑','#':'๒','$':'๓','%':'๔','^':'ู',
    '&':'฿','*':'๕','(':'๖',')':'๗','_':'๘','+':'๙',
    'q':'ๆ','w':'ไ','e':'ำ','r':'พ','t':'ะ','y':'ั','u':'ี',
    'i':'ร','o':'น','p':'ย','[':'บ',']':'ล','\\':'ฃ',
    'Q':'๐','W':'"','E':'ฎ','R':'ฑ','T':'ธ','Y':'ํ','U':'๊',
    'I':'ณ','O':'ฯ','P':'ญ','{':'ฐ','}':',','|':'.',
    'a':'ฟ','s':'ห','d':'ก','f':'ด','g':'เ','h':'้','j':'่',
    'k':'า','l':'ส',';':'ว',"'":'ง',
    'A':'ฤ','S':'ฆ','D':'ฏ','F':'โ','G':'ฌ','H':'็','J':'๋',
    'K':'ษ','L':'ศ',':':'ซ','"':'ฺ',
    'z':'ผ','x':'ป','c':'แ','v':'อ','b':'ิ','n':'ื','m':'ท',
    ',':'ม','.':'ใ','/':'ฝ',
    'Z':'ฉ','X':'ฮ','V':'ฒ','B':'?','N':'์','M':'ฬ','<':'ฦ',
}

# สร้าง reverse map: Thai → EN key
# ใช้ first-seen-wins เพื่อแก้ collision bug
# (เช่น ',' map เป็น 'ม' แต่ '}' ก็ map เป็น ',' ด้วย)
TH_TO_EN = {}
for k, v in EN_TO_TH.items():
    if v not in TH_TO_EN:
        TH_TO_EN[v] = k

# คำอังกฤษที่ไม่ควรแปล (real English words)
REAL_EN = {
    "a","i","ok","hi","no","go","do","up","in","on","at","by","to","or",
    "the","and","for","but","not","you","are","was","has","had","can",
    "will","did","get","got","let","put","set","use","see","say","he",
    "she","we","it","me","my","his","her","its","our","them","they",
    "who","why","how","what","when","where","which","all","any","few",
    "more","some","into","than","then","very","just","also","back",
    "well","even","much","too","both","each","here","there","after",
    "before","about","over","under","same","own","off","out","world",
    "meeting","hello","bye","yes","lol","omg","wtf","bro","sis",
    "love","like","follow","post","share","link","id","name","call",
    "chat","work","home","school","food","shop","free","new","hot",
    "live","online","app","web","site","page","group","team","game",
    "project","zoom","email","phone","number","pls","msg","tmr","thx",
    "tbh","ngl","imo","fyi","asap","etc","vs","ft","america","israel",
    "deploy","server","config","crash","code","push","fix","bug",
    "test","run","build","error","log","git","dev","claude","python",
}

_THAI_RE = re.compile(r"[\u0E00-\u0E7F]")  # Thai Unicode range
_MAPPABLE = set(EN_TO_TH.keys())            # EN chars ที่มี Thai mapping


# ============================================================
# Core conversion functions
# ============================================================

def en_to_th(text: str) -> str:
    """แปล EN keystrokes → Thai chars ทีละตัว"""
    return "".join(EN_TO_TH.get(c, c) for c in text)


def th_to_en(text: str) -> str:
    """แปล Thai chars → EN keystrokes ทีละตัว
    ASCII chars (space, comma, numbers) ผ่านไปเลยไม่แปล
    """
    result = []
    for c in text:
        if ord(c) < 128:  # ASCII → pass through
            result.append(c)
        else:             # Thai → lookup reverse map
            result.append(TH_TO_EN.get(c, c))
    return "".join(result)


def fix(text: str) -> str:
    """
    แก้ข้อความที่พิมพ์ผิด layout อัจฉริยะ

    Logic:
    1. มี Thai chars → TH→EN mode
       - Thai segments → th_to_en()
       - ASCII segments → ถ้าเป็น real EN word ปล่อยไว้ ไม่งั้น en_to_th()
    2. ไม่มี Thai → EN→TH mode (token by token)
       - real EN word → keep
       - pure number → keep
       - อื่นๆ → en_to_th()
    """
    if not text.strip():
        return text

    has_thai = bool(_THAI_RE.search(text))

    if has_thai:
        # แยก Thai segments และ non-Thai segments
        parts = re.split(r"([\u0E00-\u0E7F]+)", text)
        result = []
        for part in parts:
            if not part:
                continue
            if _THAI_RE.search(part):
                # Thai segment → th_to_en
                result.append(th_to_en(part))
            else:
                # ASCII segment → token by token
                result.append(_fix_ascii_segment(part))
        return "".join(result)
    else:
        # ไม่มี Thai → EN→TH token by token
        return _fix_ascii_segment(text)


def _fix_ascii_segment(text: str) -> str:
    """แยก token ด้วย space แล้วตัดสินใจแปลหรือไม่แต่ละ token"""
    tokens = re.split(r"(\s+)", text)
    return "".join(_fix_token(tok) for tok in tokens if tok)


def _fix_token(token: str) -> str:
    """
    ตัดสินใจแปล token นี้หรือไม่:
    - whitespace → ผ่านไปเลย
    - real EN word → keep
    - pure number (123) → keep
    - mappable chars > 30% → en_to_th()
    - อื่นๆ → keep
    """
    if re.match(r"^\s+$", token):
        return token
    if token.lower() in REAL_EN:
        return token
    if re.match(r"^\d+$", token):
        return token
    mappable = sum(1 for c in token if c in _MAPPABLE)
    if len(token) > 0 and mappable / len(token) > 0.3:
        return en_to_th(token)
    return token


# ============================================================
# Clipboard helpers (macOS)
# ============================================================

def get_clipboard() -> str:
    try:
        import subprocess
        result = subprocess.run(["pbpaste"], capture_output=True, text=True)
        return result.stdout
    except Exception:
        print("❌ ไม่สามารถอ่าน clipboard (รองรับเฉพาะ macOS)")
        sys.exit(1)


def copy_to_clipboard(text: str):
    try:
        import subprocess
        subprocess.run(["pbcopy"], input=text.encode(), check=True)
        print("📋 คัดลอกผลลัพธ์ไปยัง clipboard แล้ว")
    except Exception:
        pass


# ============================================================
# Main
# ============================================================

def main():
    # ไม่มี argument → interactive mode
    # พิมพ์ข้อความได้เลย ไม่ต้องก็อป command ทับ clipboard
    if len(sys.argv) < 2:
        print("=" * 50)
        print("  KeyboardTrans — แก้ข้อความพิมพ์ผิด layout")
        print("=" * 50)
        print("พิมพ์แล้วกด Enter | Ctrl+C เพื่อออก\n")
        while True:
            try:
                text = input("พิมพ์: ").strip()
                if not text:
                    continue
                result = fix(text)
                print(f"  → {result}\n")
                copy_to_clipboard(result)
            except KeyboardInterrupt:
                print("\nBye!")
                break
        return

    # --clip → อ่านจาก clipboard โดยไม่ต้องก็อป command ทับ
    # วิธีใช้: ก็อปข้อความก่อน แล้วกดลูกศรขึ้นเรียก command เก่า
    if sys.argv[1] == "--clip":
        text = get_clipboard()
        print(f"📋 Input: {text.strip()}")
        result = fix(text)
        print(f"✅ {result}")
        copy_to_clipboard(result)
        return

    # มี argument → แปลทันที
    text = " ".join(sys.argv[1:])
    result = fix(text)
    print(f"✅ {result}")
    copy_to_clipboard(result)


if __name__ == "__main__":
    main()