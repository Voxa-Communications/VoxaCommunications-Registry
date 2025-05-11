class kvValidationFileReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None
        self.load_file()

    def get_kv_file_from_name(self, name) -> str:
        for line in self.data.splitlines():
            line = line.strip()
            line_split = line.split(":")
            key, value = line_split[0].strip(), line_split[1].strip()
            if key == name:
                return value
        return None
    
    def load_file(self):
        try:
            with open(self.file_path, 'r') as file:
                self.data = file.read()
        except FileNotFoundError:
            print(f"File {self.file_path} not found.")