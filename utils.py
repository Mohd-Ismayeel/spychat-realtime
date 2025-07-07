import base64
import json
from encoders.morse import encode as morse_encode, decode as morse_decode
from encoders.binary import encode as binary_encode, decode as binary_decode
from encoders.caesar import encode as caesar_encode, decode as caesar_decode
from encoders.atbash import encode as atbash_encode, decode as atbash_decode
from encoders.a1z26 import encode as a1z26_encode, decode as a1z26_decode

# Mapping method names to encoder functions
ENCODERS = {
    "morse": morse_encode,
    "binary": binary_encode,
    "caesar": caesar_encode,
    "atbash": atbash_encode,
    "a1z26": a1z26_encode
}

# Mapping method names to decoder functions
DECODERS = {
    "morse": morse_decode,
    "binary": binary_decode,
    "caesar": caesar_decode,
    "atbash": atbash_decode,
    "a1z26": a1z26_decode
}

def encode_message(method, message):
    if method not in ENCODERS:
        raise ValueError("Unknown encoding method.")
    encoded = ENCODERS[method](message)
    return encoded

def decode_message(method, encoded):
    if method not in DECODERS:
        raise ValueError("Unknown decoding method.")
    decoded = DECODERS[method](encoded)
    return decoded

def disguise_method(method_name):
    """Converts method name to disguised base64 metadata"""
    metadata = {"method": method_name}
    metadata_str = json.dumps(metadata)
    return base64.b64encode(metadata_str.encode()).decode()

def reveal_method(metadata_str):
    """Decodes base64 metadata back to method name"""
    decoded_json = base64.b64decode(metadata_str).decode()
    metadata = json.loads(decoded_json)
    return metadata["method"]
