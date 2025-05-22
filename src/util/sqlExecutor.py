import re
import json
from typing import Optional, Dict, Any, List, Union
from kvprocessor import KVProcessor, KVStructLoader
from util.fileReader import FileReader
from util.kvValidationFileReader import kvValidationFileReader
from util.compareHash import compare_str, compare_str_as_json
from lib.dbManager import DBManager
from util.logging import log

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
    def __init__(self, file_name: str, DBManagerClass: Optional[DBManager] = GlobalDBManager, param_validation: Optional[bool] = True):
        file_path = f"src/sql/{file_name}.sql"
        super().__init__(file_path)
        self.file_path = file_path
        self.param_validation = param_validation
        self.DBManager = DBManagerClass or GlobalDBManager
        self.logger = log()
        self.KVStructLoader = KVStructLoader("https://github.com/Voxa-Communications/VoxaCommunicaitons-Structures/raw/refs/heads/main/struct/config.json")
        if self.DBManager is None:
            raise ValueError("DBManager is not initialized. Please provide a valid DBManager instance.")
        self.KVValidationFileReader = kvValidationFileReader("src/sql/kv_validation_files.txt")
        self.kv_namespace = self.KVValidationFileReader.get_kv_file_from_name(file_name)
        if self.kv_namespace != None:
            self.KVProcessor: KVProcessor = self.KVStructLoader.from_namespace(self.kv_namespace)

    def execute_sql(self, params: Union[tuple, List[Any]] = None):
        """
        Executes an SQL query with the given parameters.
        
        :param params: A tuple or list of parameters to use in the query.
        :return: The result of the query execution.
        """
        sql_content = self.read_file()
        self._validate_query(sql_content)
        
        # Ensure params is a tuple
        if params is not None and not isinstance(params, tuple):
            if isinstance(params, list):
                params = tuple(params)
            else:
                params = (params,)
        
        # Split the SQL content into separate statements
        # This handles multi-statement SQL files
        sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
                
        try:
            results = []
            for sql_query in sql_statements:
                # Add back the semicolon that was removed by the split
                sql_query = sql_query + ";"
                self.logger.debug(f"Executing SQL statement: {sql_query}")
                result = self.DBManager.execute(sql_query, params)
                results.append(result)
                
            # Return the last result, or combined results if needed
            return results[-1] if results else None
        except Exception as e:
            self.logger.error(f"Error executing SQL: {e}")
            raise e

    def _validate_query(self, query: str, params: Optional[Dict[str, Any]] = None):
        """
        Validates an SQL query and its parameters.
        
        :param query: The SQL query to validate.
        :param params: The parameters to validate against the KV structure.
        :raises ValueError: If the query is empty, doesn't end with a semicolon,
                          or the parameters don't match the expected format.
        """
        if not query.strip():
            raise ValueError("SQL query is empty.")
        
        # Check for SQL query syntax
        if not re.match(r"^[\s\S]*;$", query.strip()):
            raise ValueError("SQL query must end with a semicolon.")
            
        # Check for SQL injection patterns
        # self._check_sql_injection(query)
            
        # Validate parameters against KV structure if applicable
        if self.param_validation and self.kv_namespace != None and params != None:
            self.logger.info(f"Validating SQL query parameters")
            if self.KVProcessor:
                validated_config = self.KVProcessor.process_config(params)
                if not compare_str_as_json(str(json.dumps(validated_config)), str(json.dumps(params))):
                    raise ValueError("SQL query parameters do not match the expected format.")
            else:
                raise ValueError("KVProcessor is not initialized. Please provide a valid KVProcessor instance.")

    def _check_sql_injection(self, query: str):
        """
        Checks for SQL injection patterns in a query.
        
        :param query: The SQL query to check.
        :raises ValueError: If potential SQL injection is detected.
        """
        # Convert to lowercase for easier pattern matching
        query_lower = query.lower()
        
        # Check for common SQL injection patterns
        sql_injection_patterns = [
            r";\s*--",                # Comment out the rest of the query
            r";\s*\/\*",              # Multi-line comment
            r"union\s+(?:all\s+)?select", # UNION-based injection
            r"(?:select|update|delete|insert)\s+.+\s+--", # Comment after SQL keywords
            r"'\s*or\s+'1'='1",       # OR-based injection
            r"'\s*;\s*--",            # Terminate and comment
            r"drop\s+table",          # Destructive operations
            r"(?:alter|create|delete)\s+(?:user|table|database)" # More destructive operations
        ]
        
        for pattern in sql_injection_patterns:
            if re.search(pattern, query_lower):
                self.logger.warning(f"Potential SQL injection detected: {pattern}")
                raise ValueError(f"Potential SQL injection detected in query.")
                
        # Ensure proper usage of placeholders
        placeholder_count = query.count('%s')
        if placeholder_count > 0:
            self.logger.debug(f"Query contains {placeholder_count} placeholders")

    def execute_safe_sql(self, params: Union[tuple, List[Any]] = None):
        """
        Executes an SQL query with sanitized parameters.
        
        :param params: A tuple or list of parameters to use in the query.
        :return: The result of the query execution.
        """
        sql_query = self.read_file()
        self._validate_query(sql_query)
        try:
            sanitized_query, sanitized_params = self._sanitize_query(sql_query, params)
            return self.DBManager.execute(sanitized_query, sanitized_params)
        except Exception as e:
            self.logger.error(f"Error executing safe SQL: {e}")
            raise e

    def _sanitize_query(self, query: str, params: Union[tuple, List[Any]] = None):
        """
        Sanitizes a query and its parameters.
        
        :param query: The SQL query to sanitize.
        :param params: The parameters to sanitize.
        :return: A tuple containing the sanitized query and parameters.
        :raises ValueError: If a parameter is invalid.
        """
        if params is None:
            return query, None
            
        # Ensure params is a tuple
        if not isinstance(params, tuple):
            if isinstance(params, list):
                params = tuple(params)
            else:
                params = (params,)
        
        sanitized_params = []
        for value in params:
            if isinstance(value, str):
                # For string parameters, check for potential SQL injection patterns
                if any(char in value for char in "';\"\\%_"):
                    self.logger.warning(f"Potentially unsafe character in parameter: {value}")
                    # Instead of rejecting, escape the value properly
                    value = value.replace("'", "''").replace(";", "").replace("\\", "\\\\")
                    
            # Add the sanitized value to the list
            sanitized_params.append(value)
            
        return query, tuple(sanitized_params)

    def fetch_one(self, params: Union[tuple, List[Any]] = None):
        """
        Fetches a single record from the database.
        
        :param params: A tuple or list of parameters to use in the query.
        :return: A single record from the database.
        """
        sql_query = self.read_file()
        self._validate_query(sql_query)
        
        # Ensure params is a tuple
        if params is not None and not isinstance(params, tuple):
            if isinstance(params, list):
                params = tuple(params)
            else:
                params = (params,)
                
        try:
            return self.DBManager.fetch_one(sql_query, params)
        except Exception as e:
            self.logger.error(f"Error fetching one record: {e}")
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