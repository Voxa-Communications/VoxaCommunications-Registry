import hmac

def constant_time_compare(val1, val2):
    """
    Compare two strings in constant time to prevent timing attacks
    """
    return hmac.compare_digest(str(val1), str(val2))