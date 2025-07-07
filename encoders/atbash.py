# encoders/atbash.py

def encode(text):
    return ''.join(_atbash_char(c) for c in text)

def decode(text):
    return encode(text)  # Atbash is symmetric

def _atbash_char(c):
    if c.isalpha():
        base = ord('A') if c.isupper() else ord('a')
        return chr(base + (25 - (ord(c) - base)))
    return c
