"""
Command-line interface for KeyboardTrans.

Smart segment-aware conversion:
- Input มี Thai → แปลทั้งประโยค TH→EN (char-by-char, EN chars ที่ไม่ map ก็ผ่านไปเอง)
- Input ไม่มี Thai → ดู token-by-token ว่าแต่ละคำควรแปลหรือปล่อยไว้

ฉลาดกว่าเว็บ reference ตรงที่:
1. รู้จัก "real English words" → ไม่แปลคำพวก meeting, hello, OK
2. รองรับ mixed input เช่น "มึง meeting เมื่อวาน" → "yje meeting mewxwfh"
3. Special chars / numbers ใน layout → แปลได้ถูกต้อง
4. EN garbage (;][, ฯลฯ) ที่ map ได้ → แปลเป็น Thai
"""

import re
import sys

from keyboardtrans.config.layouts import get_kedmanee_layout
from keyboardtrans.core.converter import TextConverter
from keyboardtrans.core.layout import KeyboardLayout

_THAI_RE = re.compile(r"[\u0E00-\u0E7F]")


# Real English words ที่ไม่ควรแปลเป็น Thai
# (subset ที่ใช้บ่อย — ไม่ต้องครบ เน้น false-positive ที่พบบ่อย)
_REAL_EN_WORDS = {
    "a","i","ok","hi","no","go","do","up","in","on","at","by","to","or",
    "the","and","for","but","not","you","are","was","has","had","can",
    "will","did","get","got","let","put","set","use","see","say","was",
    "he","she","we","it","me","my","his","her","its","our","them","they",
    "who","why","how","what","when","where","which","all","any","few","world",
    "more","some","such","into","than","then","very","just","also","back",
    "well","even","much","too","both","each","here","there","after",
    "before","between","through","during","without","within","about",
    "above","below","over","under","again","same","own","off","out",
    # คำที่มักปนใน Thai context
    "meeting","hello","bye","yes","no","ok","lol","omg","wtf","bro","sis",
    "love","like","follow","post","share","link","id","name","call","line",
    "chat","work","home","school","food","shop","sale","free","new","hot",
    "live","online","app","web","site","page","group","team","game","play",
}


class KeyboardTransApp:
    def __init__(self, layout: KeyboardLayout | None = None, verbose: bool = False):
        if layout is None:
            self._layout = KeyboardLayout("kedmanee", get_kedmanee_layout())
        else:
            self._layout = layout

        self._converter = TextConverter(self._layout)
        # Build reverse lookup: which ASCII chars have a Thai mapping
        self._mappable_chars: set = set(self._layout.en_to_th.keys())
        self._verbose = verbose

    # ------------------------------------------------------------------
    # PUBLIC
    # ------------------------------------------------------------------

    def _smart_convert(self, text: str) -> str:
        if not text.strip():
            return text

        has_thai = bool(_THAI_RE.search(text))

        if has_thai:
            # มี Thai character → แปลทั้งก้อน TH→EN
            # converter.th_to_en จะ pass-through ตัวที่ไม่ map (space, EN จริงๆ ฯลฯ)
            result = self._converter.th_to_en(text)
            if self._verbose:
                print(f"[DEBUG] Mode: TH→EN (found Thai chars)")
            return result
        else:
            # ไม่มี Thai → ตัดเป็น token แล้วตัดสินใจทีละ token
            return self._convert_en_input(text)

    # ------------------------------------------------------------------
    # INTERNAL
    # ------------------------------------------------------------------

    def _convert_en_input(self, text: str) -> str:
        """
        แปล EN input โดย:
        - token ที่เป็น real English word → ปล่อยไว้
        - token ที่เป็น numbers → ปล่อยไว้
        - อื่นๆ → en_to_th
        """
        # tokenize: แยก word / number / space / symbol runs
        # เก็บ delimiter ด้วยเพื่อ reconstruct
        tokens = re.split(r'(\s+)', text)
        parts = []

        for tok in tokens:
            if not tok:
                continue
            if re.match(r'^\s+$', tok):
                parts.append(tok)
                continue

            converted = self._convert_token(tok)
            parts.append(converted)

        result = "".join(parts)
        if self._verbose:
            print(f"[DEBUG] Mode: EN→TH (token-by-token)")
        return result

    def _convert_token(self, token: str) -> str:
        """
        ตัดสินใจแปลหรือไม่แปล token นี้:
        1. Real English word → keep
        2. Pure number → keep
        3. มี mappable chars → แปล en_to_th
        4. อื่นๆ → keep
        """
        # Real EN word (case-insensitive)
        if token.lower() in _REAL_EN_WORDS:
            if self._verbose:
                print(f"[DEBUG] KEEP (real EN): '{token}'")
            return token

        # Pure number
        if re.match(r'^\d+$', token):
            if self._verbose:
                print(f"[DEBUG] KEEP (number): '{token}'")
            return token

        # ตรวจว่ามี mappable chars หรือเปล่า
        # ถ้า >50% ของ chars อยู่ใน layout → แปล
        mappable = sum(1 for c in token if c in self._mappable_chars)
        ratio = mappable / len(token) if token else 0

        if ratio > 0.3:
            converted = self._converter.en_to_th(token)
            if self._verbose:
                print(f"[DEBUG] EN→TH ({ratio:.0%} mappable): '{token}' → '{converted}'")
            return converted

        if self._verbose:
            print(f"[DEBUG] KEEP (low mappable {ratio:.0%}): '{token}'")
        return token

    # ------------------------------------------------------------------
    # RUN
    # ------------------------------------------------------------------

    def run(self) -> None:
        print("\n" + "=" * 55)
        print("  KeyboardTrans — Smart Thai⇌EN Converter")
        print("=" * 55)
        print(f"  Layout : {self._layout.name}")
        print("  มี Thai → แปล TH→EN  |  ASCII → แปล EN→TH อัจฉริยะ")
        print("  'exit' หรือ Ctrl+C เพื่อออก")
        print("-" * 55 + "\n")

        while True:
            try:
                text = input("พิมพ์: ")

                if text.lower() in ("exit", "quit", "q"):
                    print("\nBye! 👋\n")
                    break

                result = self._smart_convert(text)
                print(f"  → {result}\n")

            except KeyboardInterrupt:
                print("\nBye! 👋\n")
                sys.exit(0)
            except EOFError:
                sys.exit(0)
            except Exception as e:
                print(f"\n[Error] {e}\n")
                if self._verbose:
                    import traceback
                    traceback.print_exc()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Thai-English Keyboard Transliterator")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show debug info")
    parser.add_argument("--layout", type=str, default="kedmanee")
    args = parser.parse_args()

    app = KeyboardTransApp(verbose=args.verbose)
    app.run()


if __name__ == "__main__":
    main()