import re
import json
from typing import Optional, Dict, Any
from kvprocessor import KVProcessor, KVStructLoader
from util.fileReader import FileReader
from util.kvValidationFileReader import kvValidationFileReader
from util.compareHash import compare_str, compare_str_as_json
from lib.dbManager import DBManager

GlobalDBManager: DBManager = None

def set_global_db_manager(db_manager: DBManager):
    """
    Set the global DBManager instance.
    :param db_manager: An instance of DBManager.
    """
    global GlobalDBManager
    if not isinstance(db_manager, DBManager):
        raise ValueError("db_manager must be an instance of DBManager.")
    GlobalDBManager = db_manager
    print("Global DBManager set successfully.")

class SQLExecutor(FileReader):
    def __init__(self, file_name: str, DBManagerClass: DBManager, param_validation: Optional[bool] = True):
        file_path = f"src/sql/{file_name}.sql"
        super().__init__(file_path)
        self.file_path = file_path
        self.param_validation = param_validation
        self.DBManager = DBManagerClass or GlobalDBManager
        self.KVStructLoader = KVStructLoader("https://github.com/Voxa-Communications/VoxaCommunicaitons-Structures/raw/refs/heads/main/struct/config.json")
        if self.DBManager is None:
            raise ValueError("DBManager is not initialized. Please provide a valid DBManager instance.")
        self.KVValidationFileReader = kvValidationFileReader("src/sql/kv_validation_files.txt")
        self.kv_namespace = self.KVValidationFileReader.get_kv_file_from_name(file_name)
        if self.kv_namespace != None:
            self.KVProcessor: KVProcessor = self.KVStructLoader.from_namespace(self.kv_namespace)

    def execute_sql(self, params: tuple = None):
        sql_query = self.read_file()
        self._validate_query(sql_query)
        try:
            return self.DBManager.execute(sql_query, params)
        except Exception as e:
            print(f"Error executing SQL: {e}")
            raise e

    def _validate_query(self, query: str, params: Optional[Dict[str,any]] = None):
        if not query.strip():
            raise ValueError("SQL query is empty.")
        if not re.match(r"^[\s\S]*;$", query.strip()):
            raise ValueError("SQL query must end with a semicolon.")
        if self.param_validation and self.kv_namespace != None and params != None:
            print(f"Validating SQL query paramaters")
            if self.KVProcessor:
                validated_config = self.KVProcessor.process_config(params)
                if not compare_str_as_json(str(json.dumps(validated_config)), str(json.dumps(params))):
                    raise ValueError("SQL query parameters do not match the expected format.")
            else:
                raise ValueError("KVProcessor is not initialized. Please provide a valid KVProcessor instance.")

    def execute_safe_sql(self, params: tuple = None):
        sql_query = self.read_file()
        self._validate_query(sql_query)
        try:
            sanitized_query, sanitized_params = self._sanitize_query(sql_query, params)
            return self.DBManager.execute(sanitized_query, sanitized_params)
        except Exception as e:
            print(f"Error executing safe SQL: {e}")
            raise e

    def _sanitize_query(self, query: str, params: tuple = None):
        if not params:
            return query, None
        sanitized_params = []
        for value in params:
            if not re.match(r"^[a-zA-Z0-9_]+$", value):
                raise ValueError(f"Invalid parameter key: {value}")
            sanitized_params.append(value)
        return query, tuple(sanitized_params)

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