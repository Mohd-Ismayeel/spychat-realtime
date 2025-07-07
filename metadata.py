import hashlib

cipher_codes = {
    'morse': ('MOR', '1X1'),
    'binary': ('BIN', '2X2'),
    'caesar': ('CSR', '3X3'),
    'atbash': ('ATB', '4X4'),
    'a1z26': ('A1Z', '5X5')
}

def encrypt_metadata(method_key):
    raw_code, display_code = cipher_codes.get(method_key.lower(), ('UNK', '??'))
    hash_code = hashlib.sha256(raw_code.encode()).hexdigest()[:10]
    return hash_code, display_code  # hashed metadata, and the display label

def identify_cipher_from_metadata(received_hash):
    for method, (raw_code, display_code) in cipher_codes.items():
        hashed = hashlib.sha256(raw_code.encode()).hexdigest()[:10]
        if hashed == received_hash:
            return method, display_code
    return "unknown", "??"
