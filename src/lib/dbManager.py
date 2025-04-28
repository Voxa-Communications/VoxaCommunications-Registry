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
                password=self.config.get("MYSQL_PASSWORD")
            )
            if self.connection.is_connected():
                self.logger.info("Connected to the database")
                self.cursor = self.connection.cursor()
            self.logger.info("Database connection routine completed")
        except Error as e:
            self.logger.error(f"Error while connecting to MySQL: {e}")
            raise e
        
    def execute(self, query: str, params: tuple = None):
        try:
            self.logger.info(f"Executing query: {query}")
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            self.logger.info("Query executed successfully")
        except Error as e:
            self.logger.error(f"Error executing query: {e}")
            raise e
        return self.cursor.fetchall()

    def fetch_one(self, query: str, params: tuple = None):
        try:
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
            raise e

    def fetch_all(self, query: str, params: tuple = None):
        try:
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
            status = self.connection.is_connected() if self.connection else False
            self.logger.info(f"Database connection status: {'Connected' if status else 'Disconnected'}")
            return status
        except Error as e:
            self.logger.error(f"Error checking connection status: {e}")
            raise e

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