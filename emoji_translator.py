#!/usr/bin/env python3
"""
Emoji Translator
Usage:
    python emoji_translator.py
Type a sentence and get an emoji translation.
"""

import re

# Basic word -> emoji mapping. Extend this to your taste.
WORD_EMOJI = {
    "i": "👁️",
    "me": "🙋",
    "you": "🫵",
    "love": "❤️",
    "like": "👍",
    "hate": "💔",
    "happy": "😄",
    "sad": "😢",
    "pizza": "🍕",
    "coffee": "☕",
    "tea": "🍵",
    "cat": "🐱",
    "dog": "🐶",
    "money": "💰",
    "party": "🎉",
    "dance": "💃",
    "sleep": "😴",
    "music": "🎵",
    "fire": "🔥",
    "star": "⭐",
    "moon": "🌙",
    "sun": "☀️",
    "phone": "📱",
    "computer": "💻",
    "code": "💻",
    "study": "📚",
    "book": "📖",
    "car": "🚗",
    "bike": "🚲",
    "work": "🏢",
    "yes": "✅",
    "no": "❌",
    "maybe": "🤷",
    "hello": "👋",
    "hi": "👋",
    "bye": "👋",
    "thanks": "🙏",
    "thank": "🙏",
    "wow": "😲",
    "what": "❓",
    "why": "❓",
    "who": "👤",
    "where": "📍",
    "when": "⏰",
    "ok": "👌"
}

# A few multi-word patterns (longer patterns should go first)
PHRASE_EMOJI = {
    "i love you": "❤️💋",
    "good night": "🌙😴",
    "good morning": "☀️🌅",
    "i am": "🙋‍♂️ is",
    "happy birthday": "🎂🎉"
}

# Helper to transform a single letter into a regional indicator emoji (A -> 🇦)
def letter_to_regional(letter):
    # Only work for a-z
    if not letter.isalpha():
        return letter
    base = ord('🇦')  # regional indicator A
    # ord('🇦') is a single codepoint; we can compute offset from 'A'
    offset = ord(letter.upper()) - ord('A')
    return chr(base + offset)

# For digits, map to keycap emojis
DIGIT_KEYCAP = {
    '0': '0️⃣', '1': '1️⃣', '2': '2️⃣', '3': '3️⃣', '4': '4️⃣',
    '5': '5️⃣', '6': '6️⃣', '7': '7️⃣', '8': '8️⃣', '9': '9️⃣'
}

# Tokenization regex: words or punctuation
TOKEN_RE = re.compile(r"\w+|[^\w\s]", flags=re.UNICODE)

def translate_token(token):
    lower = token.lower()

    # Exact phrase handled elsewhere; here single token
    if lower in WORD_EMOJI:
        return WORD_EMOJI[lower]

    # If token is all digits: map each digit
    if token.isdigit():
        return "".join(DIGIT_KEYCAP.get(d, d) for d in token)

    # If token is a single letter -> regional indicator
    if len(token) == 1 and token.isalpha():
        return letter_to_regional(token)

    # Multi-letter fallback: try to convert each letter (strip non-alpha)
    letters = []
    for ch in token:
        if ch.isalpha():
            letters.append(letter_to_regional(ch))
        elif ch.isdigit():
            letters.append(DIGIT_KEYCAP.get(ch, ch))
        else:
            # Keep other characters like -, _
            letters.append(ch)
    return "".join(letters)

def apply_phrase_mapping(text):
    # Apply phrase mappings greedily (longest first)
    lowered = text.lower()
    # Sort by length descending to match longer phrases first
    for phrase in sorted(PHRASE_EMOJI.keys(), key=len, reverse=True):
        pattern = re.compile(re.escape(phrase), flags=re.IGNORECASE)
        # Replace phrase in the original text preserving case is hard; simple replace:
        lowered = pattern.sub(PHRASE_EMOJI[phrase], lowered)
    return lowered

def translate_sentence(sentence):
    # First apply phrase mapping to catch multi-word emojis
    # We'll translate by tokenizing original sentence, but we need a way to keep
    # phrase replacements. An easier approach: do phrase replacements on a lowered copy,
    # then tokenize original sentence and use the lowered copy for lookups.
    lowered = sentence.lower()
    for phrase in sorted(PHRASE_EMOJI.keys(), key=len, reverse=True):
        lowered = re.sub(re.escape(phrase), PHRASE_EMOJI[phrase], lowered, flags=re.IGNORECASE)

    # Tokenize original sentence to preserve punctuation spacing
    tokens = TOKEN_RE.findall(sentence)
    translated = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        # Check if current position starts a mapped phrase (match in lowered string)
        # For simplicity, we check sequences of tokens joined by spaces
        matched_phrase = None
        max_phrase_len = 0
        for phrase in PHRASE_EMOJI:
            phrase_tokens = phrase.split()
            L = len(phrase_tokens)
            if i + L <= len(tokens):
                candidate = " ".join(t.lower() for t in tokens[i:i+L])
                if candidate == phrase:
                    if L > max_phrase_len:
                        matched_phrase = phrase
                        max_phrase_len = L
        if matched_phrase:
            translated.append(PHRASE_EMOJI[matched_phrase])
            i += max_phrase_len
            continue

        # Else regular token mapping
        if tok.isalpha() or tok.isdigit() or (len(tok) == 1 and not tok.isalnum()):
            translated.append(translate_token(tok))
        else:
            # punctuation or mixed token: try to map word parts
            translated.append(translate_token(tok))
        i += 1

    # Join tokens with a space, but remove spaces before punctuation
    out = " ".join(translated)
    out = re.sub(r'\s+([?.!,:;])', r'\1', out)
    return out

def interactive_mode():
    print("Emoji Translator — type 'quit' or 'exit' to stop.")
    while True:
        try:
            text = input("\nEnter sentence: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye 👋")
            break
        if not text:
            continue
        if text.lower() in ("quit", "exit"):
            print("bye 👋")
            break
        print("→", translate_sentence(text))

if __name__ == "__main__":
    # Quick demo examples
    examples = [
        "I love pizza!",
        "Good night, sleepy cat.",
        "Hello, can you call me at 12345?",
        "Do you like coffee or tea?",
        "Dance party!"
    ]
    print("Demo translations:")
    for ex in examples:
        print(f"{ex} -> {translate_sentence(ex)}")

    print("\n--- Interactive mode ---")
    interactive_mode()
