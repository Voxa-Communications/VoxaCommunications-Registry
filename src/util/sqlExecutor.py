from util.fileReader import FileReader
from lib.dbManager import DBManager

class SQLExecutor(FileReader):
    def __init__(self, file_name: str, DBManagerClass: DBManager):
        file_path = f"src/sql/{file_name}.sql"
        super().__init__(file_path)
        self.file_path = file_path
        self.DBManager = DBManagerClass

    def execute_sql(self):
        sql_query = self.read_file()
        try:
            return self.DBManager.execute(sql_query)
        except Exception as e:
            print(f"Error executing SQL: {e}")
            raise e
        return None