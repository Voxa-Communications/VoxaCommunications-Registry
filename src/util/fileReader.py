import io

class FileReader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def read_file(self) -> str:
        with open(self.file_path, 'r') as file:
            return file.read()

    def read_file_as_bytes(self) -> bytes:
        with open(self.file_path, 'rb') as file:
            return file.read()

    def read_file_as_stream(self) -> io.TextIOWrapper:
        return open(self.file_path, 'r')