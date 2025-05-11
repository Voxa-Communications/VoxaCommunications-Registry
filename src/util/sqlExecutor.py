import re
from util.fileReader import FileReader
from lib.dbManager import DBManager

GlobalDBManager: DBManager = None

def set_global_db_manager(db_manager: DBManager):
    """
    Set the global DBManager
    :param db_manager: An instance of DBManager
    """
    global GlobalDBManager
    if not isinstance(db_manager, DBManager):
        raise ValueError("db_manager must be an instance of DBManager.")
    GlobalDBManager = db_manager
class SQLExecutor(FileReader):
    def __init__(self, file_name: str, DBManagerClass: DBManager):
        file_path = f"src/sql/{file_name}.sql"
        super().__init__(file_path)
        self.file_path = file_path
        self.DBManager = DBManagerClass or GlobalDBManager
        if self.DBManager is None:
            raise ValueError("DBManager is not initialized. Please provide a valid DBManager instance.")

    def execute_sql(self, params: tuple = None):
        sql_query = self.read_file()
        self._validate_query(sql_query)
        try:
            return self.DBManager.execute(sql_query, params)
        except Exception as e:
            print(f"Error executing SQL: {e}")
            raise e

    def _validate_query(self, query: str):
        if not query.strip():
            raise ValueError("SQL query is empty.")
        if not re.match(r"^[\s\S]*;$", query.strip()):
            raise ValueError("SQL query must end with a semicolon.")

    def execute_safe_sql(self, params: dict = None):
        sql_query = self.read_file()
        self._validate_query(sql_query)
        try:
            sanitized_query, sanitized_params = self._sanitize_query(sql_query, params)
            return self.DBManager.execute(sanitized_query, sanitized_params)
        except Exception as e:
            print(f"Error executing safe SQL: {e}")
            raise e

    def _sanitize_query(self, query: str, params: dict):
        if not params:
            return query, None
        sanitized_params = {}
        for key, value in params.items():
            if not re.match(r"^[a-zA-Z0-9_]+$", key):
                raise ValueError(f"Invalid parameter key: {key}")
            sanitized_params[key] = value
        return query, tuple(sanitized_params.values())

    def fetch_one(self, params: tuple = None):
        sql_query = self.read_file()
        self._validate_query(sql_query)
        try:
            return self.DBManager.fetch_one(sql_query, params)
        except Exception as e:
            print(f"Error fetching one record: {e}")
            raise e

    def fetch_all(self, params: tuple = None):
        sql_query = self.read_file()
        self._validate_query(sql_query)
        try:
            return self.DBManager.fetch_all(sql_query, params)
        except Exception as e:
            print(f"Error fetching all records: {e}")
            raise e

    def execute_script(self):
        sql_script = self.read_file()
        try:
            self.DBManager.execute_script(self.file_path)
        except Exception as e:
            print(f"Error executing SQL script: {e}")
            raise e

    def rollback(self):
        try:
            self.DBManager.rollback()
        except Exception as e:
            print(f"Error during rollback: {e}")
            raise e

    def is_connected(self):
        try:
            return self.DBManager.is_connected()
        except Exception as e:
            print(f"Error checking connection status: {e}")
            raise e

    def get_server_info(self):
        try:
            return self.DBManager.get_server_info()
        except Exception as e:
            print(f"Error fetching server info: {e}")
            raise e
    
    def using_default_db_manager(self):
        if (GlobalDBManager != None) and (self.DBManager == GlobalDBManager):
            return True
        else:
            return False