# encoders/a1z26.py

def encode(text):
    result = []
    for char in text.upper():
        if char.isalpha():
            result.append(str(ord(char) - ord('A') + 1))
        elif char == ' ':
            result.append('0')  # Use 0 as space separator
    return '-'.join(result)

def decode(code):
    parts = code.split('-')
    result = ''
    for part in parts:
        if part == '0':
            result += ' '
        elif part.isdigit() and 1 <= int(part) <= 26:
            result += chr(int(part) - 1 + ord('A'))
    return result
