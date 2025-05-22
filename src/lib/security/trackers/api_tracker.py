from lib.security.structs.apiCalls import APICalls
from lib.security.structs.apiRequest import APIRequest

global_api_tracker: APICalls = APICalls()

def set_global_api_tracker(api_calls: APICalls):
    """
    Sets the global API tracker to the given API calls.
    """
    global global_api_tracker
    global_api_tracker = api_calls

def get_global_api_tracker() -> APICalls:
    """
    Returns the global API tracker.
    """
    return global_api_tracker

def add_api_call(api_call: APIRequest):
    """
    Adds an API call to the global API tracker.
    """
    global_api_tracker.add_api_call(api_call)
    return global_api_tracker

def clear_api_calls():
    """
    Clears the global API tracker.
    """
    global_api_tracker.clear_api_calls()
    return global_api_tracker

def get_api_calls():
    """
    Returns the list of API calls from the global API tracker.
    """
    return global_api_tracker.get_api_calls()