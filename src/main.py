import dotenv
import os
import logging
import uuid
import io
import time
from flask import Flask
from routes import Routes
from colorama import init, Fore, Style, Back
from kvprocessor import KVProcessor, KVStructLoader, LoadEnv
from lib.dbManager import DBManager
from util.sqlExecutor import SQLExecutor, GlobalDBManager as SQLExecutorGlobalDBManager
from util.logging import log
dotenv.load_dotenv()
init(autoreset=True)
FLAG_FILE = "flag.txt"

class Main:
    def __init__(self,logger: log):
        self.Logger = logger
        self.FirstRun = True
        self.Logger.info("Main Class Initalized")
        self.StructLoader = KVStructLoader(os.getenv("STRUCT_LOADER_URL","https://github.com/Voxa-Communications/VoxaCommunicaitons-Structures/raw/refs/heads/main/struct/config.json"))
        self.ENVKVProcessor: KVProcessor = self.StructLoader.from_namespace("voxa.registry.config")
        self.EnvConfig = LoadEnv(self.ENVKVProcessor.return_names())
        self.Logger.info(f"Loading environment variables: {self.EnvConfig.keys()}")
        self.ValidatedConfig = self.ENVKVProcessor.process_config(self.EnvConfig)
        self.Logger.info(f"Validated config: {self.ValidatedConfig}")
        self.App = Flask(__name__)
        self.App.config["SECRET_KEY"] = self.ValidatedConfig.get("KEY")
        self.Routes = Routes(self.App, self.ValidatedConfig)
        self.DBManager = DBManager(self.ValidatedConfig)
        SQLExecutorGlobalDBManager = self.DBManager
    
    def Setup(self):
        # Setups up the database
        if self.FirstRun:
            self.Logger.info(Fore.YELLOW + "Setting up the database" + Style.RESET_ALL)
            with io.open(FLAG_FILE, "w") as f:
                self.Logger.info(Fore.YELLOW + "Creating flag file" + Style.RESET_ALL)
                f.write(f"Inital Run: {time.ctime()}")
            SQLExecutor("user_table", self.DBManager).execute_sql()
        else:
            self.Logger.info(Fore.GREEN + "Database already setup" + Style.RESET_ALL)

if __name__ == "__main__":
    print(Fore.GREEN + "Initalizing")
    LogID = str(uuid.uuid4())
    logging.basicConfig(filename=f"logs/{LogID}.log", level=logging.DEBUG)
    LoggerClass = log()
    try:
        MainClass = Main(LoggerClass)
        if os.path.exists(FLAG_FILE):
            LoggerClass.info(Fore.YELLOW + "Flag file exists, not running setup" + Style.RESET_ALL)
            MainClass.FirstRun = False
        MainClass.Setup()
        LoggerClass.info(Fore.GREEN + "Starting Flask" + Style.RESET_ALL)
        MainClass.Routes.initialize_routes()
        MainClass.Routes.run()
    except Exception as e:
        LoggerClass.error(f"{Fore.RED}Error in Main: {e}{Style.RESET_ALL}")
        raise e
    print(Fore.RED + "Program Ended")