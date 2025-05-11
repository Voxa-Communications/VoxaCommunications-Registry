import base64
import hashlib
# lol, we should have our own, however, we can steal from KVProcessor for now
from kvprocessor.util.warnings import deprecated

@deprecated
def compare_str(str1: str, str2: str) -> bool:
    """
    Compare two strings using SHA-256 hashing.
    """
    return compare_any(str1, str2)

def compare_any(any1: any, any2: any) -> bool:
    """
    Compare two objects using base64 encoding.
    """
    try:
        encoded_any1 = base64.b64encode(str(any1).encode()).decode()
        encoded_any2 = base64.b64encode(str(any2).encode()).decode()
        return encoded_any1 == encoded_any2
    except Exception as e:
        print(f"Error comparing objects: {e}")
        return False