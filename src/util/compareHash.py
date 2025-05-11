import base64
import hashlib
import json
# lol, we should have our own, however, we can steal from KVProcessor for now
from kvprocessor.util.warnings import deprecated

@deprecated
def compare_str(str1: str, str2: str) -> bool:
    """
    Compare two strings using SHA-256 hashing.
    """
    return compare_any(str1, str2)

@deprecated
def compare_str_as_json(str1: str, str2: str) -> bool:
    """
    Compare two strings as JSON objects using SHA-256 hashing.
    """
    try:
        json_obj1 = json.loads(str1)
        json_obj2 = json.loads(str2)
        return compare_any(json.dumps(json_obj1, sort_keys=True), json.dumps(json_obj2, sort_keys=True))
    except json.JSONDecodeError:
        print("Error decoding JSON strings.")
        return False

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