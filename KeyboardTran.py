import re

# ===== Explicit Mapping (US -> Thai Kedmanee) =====

en_to_th = {
    '`':'_', '1':'ๅ','2':'/','3':'-','4':'ภ','5':'ถ','6':'ุ','7':'ึ','8':'ค','9':'ต','0':'จ','-':'ข','=':'ช',
    '~':'%','!':'+','@':'๑','#':'๒','$':'๓','%':'๔','^':'ู','&':'฿','*':'๕','(':'๖',')':'๗','_':'๘','+':'๙',

    'q':'ๆ','w':'ไ','e':'ำ','r':'พ','t':'ะ','y':'ั','u':'ี','i':'ร','o':'น','p':'ย','[':'บ',']':'ล','\\':'ฃ',
    'Q':'๐','W':'"','E':'ฎ','R':'ฑ','T':'ธ','Y':'ํ','U':'๊','I':'ณ','O':'ฯ','P':'ญ','{':'ฐ','}':',',

    'a':'ฟ','s':'ห','d':'ก','f':'ด','g':'เ','h':'้','j':'่','k':'า','l':'ส',';':'ว',"'":'ง',
    'A':'ฤ','S':'ฆ','D':'ฏ','F':'โ','G':'ฌ','H':'็','J':'๋','K':'ษ','L':'ศ',':':'ซ','"':'ฺ',

    'z':'ผ','x':'ป','c':'แ','v':'อ','b':'ิ','n':'ื','m':'ท',',':'ม','.':'ใ','/':'ฝ',
    'Z':'ฉ','X':'ฮ','C':'ฺ','V':'์','B':'?','N':'ฒ','M':'ฬ','<':'ฦ','>':'ฦ','?':'ฦ'
}

# reverse mapping
th_to_en = {v: k for k, v in en_to_th.items()}


def convert_en_to_th(text):
    return "".join(en_to_th.get(c, c) for c in text)

def convert_th_to_en(text):
    return "".join(th_to_en.get(c, c) for c in text)


# ===== Simple scoring =====

EN_WORDS = {"hello","what","why","how","are","you","doing","thanat"}
TH_WORDS = {"สวัสดี","ครับ","ค่ะ","ทำ","อะไร","คุณ","ธนัช"}

def score_english(text):
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return sum(2 if w in EN_WORDS else 1 for w in words)

def score_thai(text):
    words = re.findall(r"[ก-๙]+", text)
    return sum(2 if w in TH_WORDS else 1 for w in words)


def smart_convert(text):
    th_version = convert_en_to_th(text)
    en_version = convert_th_to_en(text)

    score_th = score_thai(th_version)
    score_en = score_english(en_version)

    if score_th > score_en:
        return th_version
    elif score_en > score_th:
        return en_version
    else:
        # fallback ใช้ฝั่งที่มีตัวอักษรเยอะกว่า
        return th_version


# ===== Run =====
while True:
    text = input("พิมพ์ข้อความที่มั่ว: ")
    if text.lower() == "exit":
        break

    print("แก้ไขแล้ว:", smart_convert(text))
    print()