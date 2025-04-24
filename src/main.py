import dotenv
import os
import logging
import uuid
from kvprocessor import KVProcessor, KVStructLoader, LoadEnv
from lib.dbManager import DBManager
from util.sqlExecutor import SQLExecutor
from util.logging import log
dotenv.load_dotenv()

class Main:
    def __init__(self,logger: log):
        self.Logger = logger
        self.Logger.info("Main Class Initalized")
        self.StructLoader = KVStructLoader(os.getenv("STRUCT_LOADER_URL","https://github.com/Voxa-Communications/VoxaCommunicaitons-Structures/raw/refs/heads/main/struct/config.json"))
        self.ENVKVProcessor: KVProcessor = self.StructLoader.from_namespace("voxa.registry.config")
        self.EnvConfig = LoadEnv(self.ENVKVProcessor.return_names())
        self.Logger.info(f"Loading environment variables: {self.EnvConfig.keys()}")
        ValidatedConfig = self.ENVKVProcessor.process_config(self.EnvConfig)
        self.Logger.info(f"Validated config: {ValidatedConfig}")
        self.DBManager = DBManager(self.Logger, ValidatedConfig)
    
    def Setup(self):
        # Setups up the database
        self.Logger.info("Setting up the database")
        SQLExecutor("user_table", self.DBManager).execute_sql()

if __name__ == "__main__":
    print("Initalizing")
    LogID = str(uuid.uuid4())
    logging.basicConfig(filename=f"logs/{LogID}.log", level=logging.DEBUG)
    LoggerClass = log()
    try:
        MainClass = Main(LoggerClass)
    except Exception as e:
        LoggerClass.error(f"Error in Main: {e}")
        raise e