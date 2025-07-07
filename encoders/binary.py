# encoders/binary.py

def encode(text):
    return ' '.join(format(ord(char), '08b') for char in text)

def decode(binary_code):
    chars = binary_code.split()
    return ''.join(chr(int(b, 2)) for b in chars)
