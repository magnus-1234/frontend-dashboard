
import logging
import sys

# Ensure stdout handles UTF-8
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class MockAutoTranslate:
    def _contains_non_ascii(self, text: str) -> bool:
        """Check if the text contains any non-ASCII characters (likely non-English script)"""
        return any(ord(c) > 127 for c in text)

    def test_logic(self, content, min_text_length=10):
        text = content.strip()
        effective_min_length = min_text_length
        contains_non_ascii = self._contains_non_ascii(content)
        
        if contains_non_ascii:
            effective_min_length = 2
            
        is_skipped = len(text) < effective_min_length
        
        # Use repr to avoid encoding issues in some environments if utf-8 wrap doesn't work
        print(f"Text: {repr(content)} (len={len(text)}) | Non-ASCII: {contains_non_ascii} | Effective Min: {effective_min_length} | Skipped: {is_skipped}")
        return not is_skipped

# Test cases
translator = MockAutoTranslate()

print("--- Testing Translation Logic ---")
translator.test_logic("สวัสดีค่า") # Thai (9 chars) - Should NOT be skipped
translator.test_logic("Hello")    # English (5 chars) - Should be skipped
translator.test_logic("Hi! 👋")    # English + Emoji (4 chars) - Should NOT be skipped
translator.test_logic("How are you doing today?") # English (24 chars) - Should NOT be skipped
translator.test_logic("Ok") # English (2 chars) - Should be skipped
translator.test_logic("ค่า") # Thai short (3 chars) - Should NOT be skipped
translator.test_logic("A") # Literal single char - Should be skipped
print("--- End of Test ---")
