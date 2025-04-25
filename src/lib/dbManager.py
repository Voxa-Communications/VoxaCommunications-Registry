import mysql.connector
import os
from mysql.connector import Error
from util.logging import log

class DBManager:
    def __init__(self, logger: log, config: dict):
        self.logger = logger
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