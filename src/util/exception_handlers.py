import functools
import traceback
from util.logging import log

def log_exceptions(func):
    """
    A decorator that catches exceptions, logs the stack trace, and re-raises the exception.
    Usage:
        @log_exceptions
        def your_function():
            # your code here
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = log()
        try:
            return func(*args, **kwargs)
        except Exception as e:
            stack_trace = traceback.format_exc()
            caller_info = f"{func.__module__}.{func.__name__}"
            logger.error(f"Exception in {caller_info}: {str(e)}\nStack trace:\n{stack_trace}")
            raise  # Re-raise the exception after logging
    return wrapper