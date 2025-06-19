import mysql.connector
import os
from mysql.connector import Error
from util.logging import log

class DBManager:
    def __init__(self, config: dict):
        self.logger = log()
        self.logger.info("DBManager Class Initialized")
        self.connection = None
        self.cursor = None
        self.config = config
        self.connect()

    def connect(self):
        try:
            self.logger.info("Connecting to the database")
            self.connection = mysql.connector.connect(
                host=self.config.get("MYSQL_HOST"),
                port=self.config.get("MYSQL_PORT"),
                database=self.config.get("MYSQL_DATABASE"),
                user=self.config.get("MYSQL_USER"),
                password=self.config.get("MYSQL_PASSWORD"),
                # Add connection pool and timeout settings
                autocommit=False,
                connection_timeout=28800,  # 8 hours
                pool_name="voxa_pool",
                pool_size=5,
                pool_reset_session=True
                # Note: reconnect parameter is not supported with connection pooling
            )
            if self.connection.is_connected():
                self.logger.info("Connected to the database")
                self.cursor = self.connection.cursor()
            self.logger.info("Database connection routine completed")
        except Error as e:
            self.logger.error(f"Error while connecting to MySQL: {e}")
            raise e

    def _ensure_connection(self):
        """Ensure the database connection is active, reconnect if necessary."""
        try:
            if not self.connection or not self.connection.is_connected():
                self.logger.warning("Database connection lost, attempting to reconnect...")
                self.connect()
            else:
                # Ping the connection to verify it's still alive
                self.connection.ping(reconnect=True, attempts=3, delay=1)
        except Error as e:
            self.logger.warning(f"Connection ping failed, reconnecting: {e}")
            try:
                self.connect()
            except Error as reconnect_error:
                self.logger.error(f"Failed to reconnect to database: {reconnect_error}")
                raise reconnect_error
        
    def execute(self, query: str, params: tuple = None):
        try:
            self._ensure_connection()
            self.logger.info(f"Executing query: {query}")
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            self.logger.info("Query executed successfully")
            
            # Check if the query is a SELECT statement that returns results
            if query.strip().lower().startswith("select"):
                return self.cursor.fetchall()
            # For non-SELECT queries, just return affected row count
            return self.cursor.rowcount
        except Error as e:
            self.logger.error(f"Error executing query: {e}")
            # Try to reconnect once on connection errors
            if e.errno in [2006, 2013, 4031]:  # Connection lost errors
                self.logger.info("Attempting to reconnect and retry query...")
                try:
                    self.connect()
                    if params:
                        self.cursor.execute(query, params)
                    else:
                        self.cursor.execute(query)
                    self.connection.commit()
                    self.logger.info("Query executed successfully after reconnection")
                    
                    if query.strip().lower().startswith("select"):
                        return self.cursor.fetchall()
                    return self.cursor.rowcount
                except Error as retry_error:
                    self.logger.error(f"Query failed even after reconnection: {retry_error}")
                    raise retry_error
            raise e

    def fetch_one(self, query: str, params: tuple = None):
        try:
            self._ensure_connection()
            self.logger.info(f"Fetching one record with query: {query}")
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            result = self.cursor.fetchone()
            self.logger.info("Record fetched successfully")
            return result
        except Error as e:
            self.logger.error(f"Error fetching record: {e}")
            # Try to reconnect once on connection errors
            if e.errno in [2006, 2013, 4031]:  # Connection lost errors
                self.logger.info("Attempting to reconnect and retry fetch_one...")
                try:
                    self.connect()
                    if params:
                        self.cursor.execute(query, params)
                    else:
                        self.cursor.execute(query)
                    result = self.cursor.fetchone()
                    self.logger.info("Record fetched successfully after reconnection")
                    return result
                except Error as retry_error:
                    self.logger.error(f"Fetch failed even after reconnection: {retry_error}")
                    raise retry_error
            raise e

    def fetch_all(self, query: str, params: tuple = None):
        try:
            self._ensure_connection()
            self.logger.info(f"Fetching all records with query: {query}")
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            results = self.cursor.fetchall()
            self.logger.info("Records fetched successfully")
            return results
        except Error as e:
            self.logger.error(f"Error fetching records: {e}")
            # Try to reconnect once on connection errors
            if e.errno in [2006, 2013, 4031]:  # Connection lost errors
                self.logger.info("Attempting to reconnect and retry fetch_all...")
                try:
                    self.connect()
                    if params:
                        self.cursor.execute(query, params)
                    else:
                        self.cursor.execute(query)
                    results = self.cursor.fetchall()
                    self.logger.info("Records fetched successfully after reconnection")
                    return results
                except Error as retry_error:
                    self.logger.error(f"Fetch failed even after reconnection: {retry_error}")
                    raise retry_error
            raise e

    def close_connection(self):
        try:
            if self.connection and self.connection.is_connected():
                self.cursor.close()
                self.connection.close()
                self.logger.info("Database connection closed successfully")
        except Error as e:
            self.logger.error(f"Error closing the database connection: {e}")
            raise e

    def execute_script(self, script_path: str):
        try:
            self._ensure_connection()
            self.logger.info(f"Executing SQL script from file: {script_path}")
            with open(script_path, 'r') as file:
                script = file.read()
            for statement in script.split(';'):
                if statement.strip():
                    self.cursor.execute(statement)
            self.connection.commit()
            self.logger.info("SQL script executed successfully")
        except (Error, FileNotFoundError) as e:
            self.logger.error(f"Error executing SQL script: {e}")
            raise e

    def is_connected(self):
        try:
            if self.connection:
                # Use ping to check if connection is actually alive
                self.connection.ping(reconnect=False)
                status = self.connection.is_connected()
            else:
                status = False
            self.logger.info(f"Database connection status: {'Connected' if status else 'Disconnected'}")
            return status
        except Error as e:
            self.logger.error(f"Error checking connection status: {e}")
            return False

    def rollback(self):
        try:
            self.logger.info("Rolling back the current transaction")
            self.connection.rollback()
            self.logger.info("Transaction rolled back successfully")
        except Error as e:
            self.logger.error(f"Error during rollback: {e}")
            raise e

    def get_server_info(self):
        try:
            if self.connection and self.connection.is_connected():
                server_info = self.connection.get_server_info()
                self.logger.info(f"Database server info: {server_info}")
                return server_info
            else:
                self.logger.warning("Cannot fetch server info, no active connection")
                return None
        except Error as e:
            self.logger.error(f"Error fetching server info: {e}")
            raise e