from lib.security.structs.apiRequest import APIRequest
class APICalls:
    """
    Repersents a collection of API calls.
    """
    def __init__(self):
        self.api_calls = []

    def add_api_call(self, api_call: APIRequest):
        """
        Adds an API call to the collection.
        """
        self.api_calls.append(api_call)

    def get_api_calls(self):
        """
        Returns the list of API calls.
        """
        return self.api_calls
    def clear_api_calls(self):
        """
        Clears the list of API calls.
        """
        self.api_calls = []
    def __repr__(self):
        return f"APICalls(api_calls={self.api_calls})"
    def __str__(self):
        return f"APICalls(api_calls={self.api_calls})"
    def __len__(self):
        return len(self.api_calls)
    def __getitem__(self, index):
        return self.api_calls[index]
    def __setitem__(self, index, value):
        self.api_calls[index] = value
    def __delitem__(self, index):
        del self.api_calls[index]
    def __iter__(self):
        return iter(self.api_calls)
    def __contains__(self, item):
        return item in self.api_calls
    def __add__(self, other):
        if isinstance(other, APICalls):
            return APICalls(self.api_calls + other.api_calls)
        return NotImplemented