# encoders/caesar.py

SHIFT = 3  # classic Caesar shift

def encode(text):
    result = ''
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - base + SHIFT) % 26 + base)
        else:
            result += char
    return result

def decode(cipher):
    result = ''
    for char in cipher:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - base - SHIFT) % 26 + base)
        else:
            result += char
    return result
