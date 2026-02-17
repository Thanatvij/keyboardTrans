import re
from typing import Set, Tuple

from keyboardtrans.strategies.base import BaseScoringStrategy
from pythainlp.util import eng_to_thai, thai_to_eng


class WeightedScoringStrategy(BaseScoringStrategy):
    """
    Weighted Scoring Strategy V3.1
    Key fix: ASCII-without-vowels is treated as "garbage EN", not real English.
    This prevents mewxwfh, mevtwi, etc. from scoring high as English.
    """

    IMPROVEMENT_THRESHOLD: float = 0.08  # ลดจาก 0.1 เพื่อให้ flip ง่ายขึ้นเล็กน้อย

    EN_WORDS: Set[str] = {
        "hello","what","why","how","are","you","doing","the","and","is","a",
        "to","in","that","it","for","on","with","as","this","was","at","by",
        "an","be","which","or","from","but","not","have","had","has","we",
        "they","he","she","i","his","her","their","our","my","me","him",
        "them","us","will","would","could","should","may","might","can",
        "need","must","do","did","does","go","went","come","came","get",
        "got","make","made","take","took","see","saw","know","knew",
        "think","thought","want","wanted","give","gave","find","found",
        "tell","told","ask","asked","work","worked","good","new","first",
        "last","long","great","little","own","other","old","right","big",
        "high","different","small","large","next","early","young",
        "important","few","public","bad","same","able","time","year",
        "people","way","day","man","woman","child","world","life",
    }

    TH_WORDS: Set[str] = {
        "สวัสดี","ครับ","ค่ะ","ทำ","อะไร","คุณ","ไม่","มี","หรือ",
        "ที่","ของ","เป็น","แล้ว","ได้","ให้","นะ","มา","ไป",
        "อยาก","ต้อง","จะ","เรา","เขา","หลาย","ทุก","บาง",
        "มัน","นี้","นั้น","ไหน","อย่าง","ใน","บน","จาก",
        "โดย","เพื่อ","กับ","และ","จริง","ดี","มาก","น้อย",
        "ใหญ่","เล็ก","วัน","ปี","คืน","คน","ผู้ชาย",
        "ผู้หญิง","เด็ก","ครอบครัว","เพื่อน","บ้าน","อาหาร",
        "น้ำ","ข้าว","รถ","โรงเรียน","พูด","ฟัง","อ่าน",
        "เขียน","คิด","เรียน","ช่วย","บอก","ถาม","ตอบ",
        "รัก","ชอบ","เวลา","ปัญหา","วิธี","ข้อมูล",
        "เมื่อ","วาน","เมื่อวาน","วันนี้","พรุ่งนี้","ตอนนี้",
        "เมื่อกี้","ก็","แต่","ยัง","แค่","ด้วย","เลย",
        "เลว","คนเลว",
    }

    def __init__(self):
        self._en_word_pattern = re.compile(r"[a-zA-Z]+")
        self._th_word_pattern = re.compile(r"[ก-๙]+")
        self._thai_unicode_pattern = re.compile(r"[\u0E01-\u0E5B]")

    # =========================
    # PUBLIC METHODS
    # =========================

    def auto_correct(self, text: str) -> Tuple[str, str]:
        if not text:
            return text, "empty_input"

        th_version = eng_to_thai(text)
        en_version = thai_to_eng(text)

        return self.get_language_decision(text, th_version, en_version)

    def score_english(self, text: str) -> float:
        if not text:
            return 0.0

        dict_score = self._dictionary_score(text, self.EN_WORDS, True)
        script_score = self._ascii_ratio(text)
        validity_score = self._token_validity(text, True)
        boundary_score = self._boundary_score(text, True)
        garbage_score = self._garbage_penalty(text, True)
        garbage_score += self._layout_noise_score(text)

        # === KEY FIX V3.1 ===
        # ถ้า ASCII แต่ไม่มี vowel → มันคือ keyboard garbage ไม่ใช่ English จริงๆ
        # ลด script_score ลงแรงถ้า vowelless ratio สูง
        vowelless_penalty = self._vowelless_penalty(text)
        script_score = script_score * (1.0 - vowelless_penalty)
        # ====================

        final = (
            0.35 * dict_score
            + 0.20 * script_score
            + 0.25 * validity_score
            + 0.10 * boundary_score
            - 0.10 * garbage_score
        )

        return max(0.0, min(1.0, final))

    def score_thai(self, text: str) -> float:
        if not text:
            return 0.0

        dict_score = self._dictionary_score(text, self.TH_WORDS, False)
        script_score = self._thai_ratio(text)
        validity_score = self._token_validity(text, False)
        boundary_score = self._boundary_score(text, False)
        garbage_score = self._garbage_penalty(text, False)

        final = (
            0.35 * dict_score
            + 0.20 * script_score
            + 0.25 * validity_score
            + 0.10 * boundary_score
            - 0.10 * garbage_score
        )

        return max(0.0, min(1.0, final))

    def get_language_decision(self, original, th_version, en_version):

        # === KEY FIX V3.1 ===
        # ถ้า original เป็น ASCII ล้วนแต่ไม่มี vowel เลย
        # → มันคือ garbage สำหรับ English ด้วย → ลด original score
        original_en_score = self.score_english(original)
        original_th_score = self.score_thai(original)

        # ถ้า original เป็น ASCII garbage → หักเพิ่ม
        vp = self._vowelless_penalty(original)
        if vp > 0.6:
            original_en_score = original_en_score * 0.5
        # ====================

        original_best = max(original_th_score, original_en_score)

        flipped_th = self.score_thai(th_version)
        flipped_en = self.score_english(en_version)
        best_flip = max(flipped_th, flipped_en)

        # Strong improvement → flip
        if best_flip > original_best + self.IMPROVEMENT_THRESHOLD:
            if flipped_th >= flipped_en:
                return th_version, "flipped_to_thai_strong"
            return en_version, "flipped_to_english_strong"

        # Smart rescue: original ต่ำ และ flip ดีกว่าชัดเจน
        if original_best < 0.45 and best_flip > original_best + 0.12:
            if flipped_th >= flipped_en:
                return th_version, "flipped_to_thai_rescue"
            return en_version, "flipped_to_english_rescue"

        return original, "keep_original"

    # =========================
    # INTERNAL SCORING
    # =========================

    def _vowelless_penalty(self, text: str) -> float:
        """
        V3.1 KEY FIX: วัด ratio ของคำ ASCII ที่ไม่มี vowel เลย
        คำเหล่านั้นคือ keyboard garbage ไม่ใช่ English จริงๆ
        mewxwfh → [mewxwfh] → ไม่มี a,e,i,o,u จริงๆ ไหม?
          'e' มีแต่ mewx ไม่ใช่คำ EN จริง → ดูที่ word level ด้วย
        
        Logic: ถ้า >60% ของ ASCII tokens ไม่อยู่ใน EN dict และมี vowel ratio ต่ำ
        → penalty สูง
        """
        words = self._en_word_pattern.findall(text.lower())
        if not words:
            return 0.0

        vowels = set("aeiou")
        
        # นับคำที่ไม่ใช่ EN dict และมี vowel น้อย (<=1 vowel ใน token ยาว >3)
        garbage_words = 0
        for w in words:
            in_dict = w in self.EN_WORDS
            vowel_count = sum(1 for c in w if c in vowels)
            vowel_ratio = vowel_count / len(w) if w else 0
            
            if not in_dict:
                # ยาว >3 ตัวแต่ vowel ratio ต่ำมาก → garbage
                if len(w) > 3 and vowel_ratio < 0.2:
                    garbage_words += 1
                # สั้น <=3 ตัวแต่ไม่มี vowel เลย
                elif len(w) <= 3 and vowel_count == 0:
                    garbage_words += 1

        return min(1.0, garbage_words / len(words))

    def _dictionary_score(self, text, vocab, english):
        words = (
            self._en_word_pattern.findall(text.lower())
            if english else
            self._th_word_pattern.findall(text)
        )

        if not words:
            return 0.0

        matched = sum(1 for w in words if w in vocab)
        return matched / len(words)

    def _ascii_ratio(self, text):
        chars = [c for c in text if not c.isspace()]
        if not chars:
            return 0.0
        return sum(c.isascii() for c in chars) / len(chars)

    def _thai_ratio(self, text):
        if not text:
            return 0.0
        thai_chars = len(self._thai_unicode_pattern.findall(text))
        return thai_chars / len(text)

    def _boundary_score(self, text, english):
        if not text:
            return 0.0

        space_ratio = text.count(" ") / len(text)

        if english:
            if 0.08 <= space_ratio <= 0.25:
                return 1.0
            return max(0.0, 1 - abs(space_ratio - 0.15) * 5)
        else:
            if space_ratio <= 0.15:
                return 1.0
            return max(0.0, 1 - (space_ratio - 0.15) * 4)

    def _token_validity(self, text, english):
        words = (
            self._en_word_pattern.findall(text.lower())
            if english else
            self._th_word_pattern.findall(text)
        )

        if not words:
            return 0.0

        valid = 0

        if english:
            for w in words:
                if (
                    any(c in "aeiou" for c in w)
                    and 2 <= len(w) <= 15
                ):
                    valid += 1
        else:
            vowels = set("าิีึุูเแโใไ็่้๊๋ัำ")
            consonants = set("กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬ")

            for w in words:
                repeated = any(w[i]==w[i+1]==w[i+2] for i in range(len(w)-2))
                if (
                    any(c in vowels for c in w)
                    and any(c in consonants for c in w)
                    and not repeated
                ):
                    valid += 1

        return valid / len(words)

    def _garbage_penalty(self, text, english):
        penalty = 0.0

        for i in range(len(text)-2):
            if text[i] == text[i+1] == text[i+2]:
                penalty += 0.3

        penalty = min(penalty, 1.0)

        symbols = sum(
            1 for c in text
            if not c.isalnum() and not c.isspace()
        )

        density = symbols / len(text) if text else 0
        if density > 0.3:
            penalty += (density - 0.3) * 2

        return min(1.0, penalty)

    def _layout_noise_score(self, text):
        if not text:
            return 0.0

        symbol_cluster = len(re.findall(r"[^\w\s]{2,}", text))

        no_vowel_words = len(
            [w for w in self._en_word_pattern.findall(text.lower())
             if len(w) > 4 and not any(c in "aeiou" for c in w)]
        )

        return min(1.0, (symbol_cluster * 0.2) + (no_vowel_words * 0.2))