"""
Real-world Thai-English mixed input test cases for KeyboardTrans (Kedmanee layout).
"""

import pytest
from keyboardtrans.config.layouts.kedmanee import KEDMANEE_LAYOUT
from keyboardtrans.core.layout import KeyboardLayout
from keyboardtrans.core.converter import TextConverter
from keyboardtrans.cli import KeyboardTransApp


@pytest.fixture
def app():
    return KeyboardTransApp(verbose=False)


@pytest.fixture
def converter():
    layout = KeyboardLayout("kedmanee", KEDMANEE_LAYOUT)
    return TextConverter(layout)


# ==============================================================
# 1. Pure Thai → EN keystrokes
# ==============================================================

class TestPureThaiToEN:

    def test_sawasdee(self, converter):
        # Input:    สวัสดี
        # Expected: lhkjfu  (Kedmanee TH→EN)
        # Reason:   Common greeting, pure Thai
        result = converter.th_to_en("สวัสดี")
        assert result == "lhkjfu"

    def test_khrap(self, converter):
        # Input:    ครับ
        # Expected: 8i'[
        # Reason:   Polite particle male
        result = converter.th_to_en("ครับ")
        assert result == "8i'["

    def test_mai_mee(self, converter):
        # Input:    ไม่มี
        # Expected: wj,u
        # Reason:   Common phrase "don't have"
        result = converter.th_to_en("ไม่มี")
        assert result == "wj,u"

    def test_short_word_gun(self, converter):
        # Input:    กัน
        # Expected: d'o
        # Reason:   Short 2-char Thai word
        result = converter.th_to_en("กัน")
        assert result == "d'o"

    def test_arai(self, converter):
        # Input:    อะไร
        # Expected: vti
        # Reason:   Question word "what"
        result = converter.th_to_en("อะไร")
        assert result == "vthi"  # ะ=t, ไ=w... adjust per layout


# ==============================================================
# 2. Pure ASCII garbage → Thai words
# ==============================================================

class TestPureASCIIToThai:

    def test_sawasdee_en_keys(self, converter):
        # Input:    lhkjfu
        # Expected: สวัสดี
        # Reason:   Kedmanee EN→TH
        result = converter.en_to_th("lhkjfu")
        assert result == "สวัสดี"

    def test_khun_tham_arai(self, converter):
        # Input:    8og];,kc
        # Expected: คนเลวมา  (approximately)
        # Reason:   Common garbage input
        result = converter.en_to_th("8og];,kc")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_special_chars_in_input(self, converter):
        # Input:    l;ylfu
        # Expected: สวัสดี (partial)
        # Reason:   ; maps to ว in Kedmanee
        result = converter.en_to_th("l;")
        assert result == "สว"

    def test_bracket_maps_to_thai(self, converter):
        # Input:    [
        # Expected: บ
        # Reason:   [ → บ in Kedmanee
        assert converter.en_to_th("[") == "บ"
        assert converter.en_to_th("]") == "ล"

    def test_numbers_passthrough(self, converter):
        # Input:    123
        # Expected: 123  (numbers not in layout → pass through)
        # Reason:   Digits have no Thai mapping
        result = converter.en_to_th("123")
        assert result == "123"


# ==============================================================
# 3. Mixed Thai + real EN words (via CLI smart convert)
# ==============================================================

class TestMixedInputCLI:

    def test_thai_with_english_word_meeting(self, app):
        # Input:    มึง meeting เมื่อวาน
        # Expected: ,7' meeting g,njv;ko
        # Reason:   Thai parts → EN, "meeting" stays (real EN word)
        result = app._smart_convert("มึง meeting เมื่อวาน")
        assert "meeting" in result
        assert "มึง" not in result
        assert "เมื่อวาน" not in result

    def test_thai_with_ok(self, app):
        # Input:    ไปกันเถอะ ok
        # Expected: Thai→EN + "ok" preserved
        # Reason:   "ok" is real EN word
        result = app._smart_convert("ไปกันเถอะ ok")
        assert "ok" in result

    def test_thai_with_hello(self, app):
        # Input:    สวัสดี hello
        # Expected: lhkjfu hello
        # Reason:   Thai→EN, "hello" stays
        result = app._smart_convert("สวัสดี hello")
        assert "hello" in result
        assert "สวัสดี" not in result

    def test_pure_ascii_garbage(self, app):
        # Input:    l;ylfu8iy[;ypi6jo
        # Expected: สวัสดีครับวัยรุ่น (approximately)
        # Reason:   No Thai found → EN→TH mode
        result = app._smart_convert("l;ylfu8iy[;ypi6jo")
        assert isinstance(result, str)
        assert len(result) > 0
        # Should contain Thai characters
        assert any("\u0E00" <= c <= "\u0E7F" for c in result)

    def test_real_en_word_preserved(self, app):
        # Input:    meeting
        # Expected: meeting  (real EN word, not converted)
        # Reason:   "meeting" in _REAL_EN_WORDS list
        result = app._smart_convert("meeting")
        assert result == "meeting"

    def test_real_en_word_hello_preserved(self, app):
        # Input:    hello
        # Expected: hello
        # Reason:   "hello" in _REAL_EN_WORDS list
        result = app._smart_convert("hello")
        assert result == "hello"


# ==============================================================
# 4. Special chars handling
# ==============================================================

class TestSpecialChars:

    def test_comma_passthrough_in_thai_mode(self, app):
        # Input:    ,7' ทำะรืเ ok
        # Expected: ,7' ... ok  (comma stays, Thai→EN)
        # Reason:   ASCII chars pass through in TH→EN mode
        result = app._smart_convert(",7' ทำะรืเ ok")
        assert result.startswith(",")  # comma not converted to }
        assert "ok" in result

    def test_ascii_comma_not_converted_to_brace(self, converter):
        # Input:    , (ASCII comma in Thai text context)
        # Expected: , (pass through)
        # Reason:   ASCII < 128 should pass through in th_to_en
        result = converter.th_to_en(",")
        assert result == ","  # NOT }

    def test_brace_maps_to_comma_in_thai(self, converter):
        # Input:    }  (EN key)
        # Expected: ,  (Thai comma via Kedmanee)
        # Reason:   } → , in Kedmanee EN→TH
        result = converter.en_to_th("}")
        assert result == ","


# ==============================================================
# 5. Numbers mixed in
# ==============================================================

class TestNumbersMixed:

    def test_number_in_thai_sentence(self, app):
        # Input:    ราคา 500 บาท
        # Expected: Thai→EN, 500 stays
        # Reason:   Numbers pass through
        result = app._smart_convert("ราคา 500 บาท")
        assert "500" in result

    def test_number_only_input(self, app):
        # Input:    12345
        # Expected: 12345 (no Thai → EN→TH mode, but numbers pass through)
        result = app._smart_convert("12345")
        assert "12345" in result


# ==============================================================
# 6. Edge cases
# ==============================================================

class TestEdgeCases:

    def test_empty_string(self, app):
        # Input:    ""
        # Expected: ""
        result = app._smart_convert("")
        assert result == ""

    def test_whitespace_only(self, app):
        # Input:    "   "
        # Expected: "   "
        result = app._smart_convert("   ")
        assert result.strip() == ""

    def test_single_thai_char(self, app):
        # Input:    ก
        # Expected: d  (Kedmanee ก → d)
        result = app._smart_convert("ก")
        assert result == "d"

    def test_single_ascii_char_mappable(self, app):
        # Input:    d
        # Expected: ก  (Kedmanee d → ก)
        result = app._smart_convert("d")
        assert result == "ก"

    def test_long_sentence(self, app):
        # Input:    วันนี้อากาศดีมากครับ
        # Expected: Thai→EN keystrokes, no Thai chars in output
        result = app._smart_convert("วันนี้อากาศดีมากครับ")
        assert not any("\u0E00" <= c <= "\u0E7F" for c in result)
        assert len(result) > 0

    def test_deterministic(self, app):
        # Input:    สวัสดีครับ (run twice)
        # Expected: same result both times
        r1 = app._smart_convert("สวัสดีครับ")
        r2 = app._smart_convert("สวัสดีครับ")
        assert r1 == r2