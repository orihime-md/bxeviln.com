"""Hacker-themed (but safe) text tools: encoding, hashing, ciphers."""

import base64
import binascii
import hashlib
import string

class ToolError(Exception):
    pass

def _validate_text(text: str) -> str:
    if not text or not text.strip():
        raise ToolError("Send me some text first, e.g. /encode Hello world")
    return text.strip()

def cmd_encode(text: str) -> str:
    """Base64 encode."""
    text = _validate_text(text)
    encoded = base64.b64encode(text.encode()).decode()
    return f"[Base64 ENCODED]\n\n{encoded}"

def cmd_decode(text: str) -> str:
    """Base64 decode."""
    text = _validate_text(text)
    try:
        decoded = base64.b64decode(text, validate=True).decode()
    except (binascii.Error, UnicodeDecodeError):
        raise ToolError("That doesn't look like valid Base64.")
    return f"[Base64 DECODED]\n\n{decoded}"

def cmd_hex(text: str) -> str:
    """Hex encode."""
    text = _validate_text(text)
    return f"[HEX DUMP]\n\n{text.encode().hex(' ')}"

def cmd_unhex(text: str) -> str:
    """Hex decode."""
    text = _validate_text(text).replace(" ", "").replace("0x", "")
    try:
        decoded = bytes.fromhex(text).decode()
    except (ValueError, UnicodeDecodeError):
        raise ToolError("That doesn't look like valid hex.")
    return f"[HEX DECODED]\n\n{decoded}"

def cmd_hash(text: str) -> str:
    """SHA-256 / SHA-1 / MD5 fingerprints of the text."""
    text = _validate_text(text)
    data = text.encode()
    return (
        "[HASH FINGERPRINTS]\n\n"
        f"SHA-256: {hashlib.sha256(data).hexdigest()}\n"
        f"SHA-1:   {hashlib.sha1(data).hexdigest()}\n"
        f"MD5:     {hashlib.md5(data).hexdigest()}"
    )

def cmd_binary(text: str) -> str:
    """Binary encode."""
    text = _validate_text(text)
    bits = " ".join(format(b, "08b") for b in text.encode())
    return f"[BINARY]\n\n{bits}"

def cmd_rot13(text: str) -> str:
    """Classic ROT13 letter rotation cipher."""
    text = _validate_text(text)
    out = []
    for ch in text:
        if ch in string.ascii_lowercase:
            out.append(string.ascii_lowercase[(string.ascii_lowercase.index(ch) + 13) % 26])
        elif ch in string.ascii_uppercase:
            out.append(string.ascii_uppercase[(string.ascii_uppercase.index(ch) + 13) % 26])
        else:
            out.append(ch)
    return f"[ROT13]\n\n{''.join(out)}"

def cmd_caesar(text: str) -> str:
    """Caesar shift by 3 (pass a number prefix like '5 hello' to choose shift)."""
    text = _validate_text(text)
    shift = 3
    parts = text.split(None, 1)
    if len(parts) == 2 and parts[0].lstrip("-").isdigit():
        shift = int(parts[0]) % 26
        text = parts[1].strip()
    out = []
    for ch in text:
        if ch in string.ascii_lowercase:
            out.append(string.ascii_lowercase[(string.ascii_lowercase.index(ch) + shift) % 26])
        elif ch in string.ascii_uppercase:
            out.append(string.ascii_uppercase[(string.ascii_uppercase.index(ch) + shift) % 26])
        else:
            out.append(ch)
    return f"[CAESAR shift={shift}]\n\n{''.join(out)}"

def cmd_fakecredentials(text: str) -> str:
    """Generate a hacker-movie style alias (purely fictional, for fun)."""
    text = _validate_text(text)
    seed = hashlib.sha256(text.lower().encode()).hexdigest()
    handles = ["zer0day", "gh0st", "n1ghtcr4wler", "v3nd3tta", "bl4ckf1re", "spectre", "d4rkpuls3", "k3rn3l"]
    suffixes = ["x7", "_404", ".exe", "_1337", "typhoon", "protocol", "_nx", "cipher"]
    handle = handles[int(seed[:4], 16) % len(handles)] + suffixes[int(seed[4:8], 16) % len(suffixes)]
    clearance = ["LEVEL 5 // COSMIC", "LEVEL 4 // TALON", "LEVEL 7 // BLACKOUT", "LEVEL 3 // UMBRA"]
    return (
        "[IDENTITY GENERATED]\n\n"
        f"HANDLE: {handle}\n"
        f"CLEARANCE: {clearance[int(seed[8:12], 16) % len(clearance)]}\n"
        f"SESSION KEY: {seed[:16].upper()}\n"
        f"TRACE: MASKED"
    )
