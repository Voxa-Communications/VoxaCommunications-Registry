class APIRequest:
    def __init__(self, method: str, endpoint: str, headers: dict = None, body: dict = None, request_time = None):
        self.method = method
        self.endpoint = endpoint
        self.headers = headers if headers is not None else {}
        self.body = body if body is not None else {}
        self.request_time = request_time

    def __repr__(self):
        return f"APIStruct(method={self.method}, endpoint={self.endpoint}, headers={self.headers}, body={self.body})"