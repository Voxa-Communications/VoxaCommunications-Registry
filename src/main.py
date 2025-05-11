import dotenv
import os
import logging
import uuid
import io
import time
from flask import Flask
from routes import Routes
from colorama import init, Fore, Style
from kvprocessor import KVProcessor, KVStructLoader, LoadEnv
from lib.dbManager import DBManager
from util.sqlExecutor import SQLExecutor, set_global_db_manager
from util.logging import log
from util.usefulJSON import JsonFromKeys

# Load environment variables and initialize colorama
dotenv.load_dotenv()
init(autoreset=True)

# Constants
FLAG_FILE = "flag.txt"

class Main:
    def __init__(self, logger: log):
        self.logger = logger
        self.first_run = True
        self.logger.info("Main class initialized.")

        # Load and validate configuration
        struct_loader_url = os.getenv(
            "STRUCT_LOADER_URL",
            "https://github.com/Voxa-Communications/VoxaCommunicaitons-Structures/raw/refs/heads/main/struct/config.json"
        )
        self.struct_loader = KVStructLoader(struct_loader_url)
        self.env_kv_processor: KVProcessor = self.struct_loader.from_namespace("voxa.registry.config")
        self.env_config = LoadEnv(self.env_kv_processor.return_names())
        self.logger.info(f"Loading environment variables: {list(self.env_config.keys())}")
        self.validated_config = self.env_kv_processor.process_config(self.env_config)
        self.logger.info(f"Validated configuration: {self.validated_config}")

        # Initialize Flask app and components
        self.app = Flask(__name__)
        self.app.config["SECRET_KEY"] = self.validated_config.get("KEY")
        self.routes = Routes(self.app, self.validated_config)
        self.db_manager = DBManager(JsonFromKeys(self.struct_loader.from_namespace("voxa.api.db.registrydb_config").return_names(),self.validated_config))
        set_global_db_manager(self.db_manager)

    def setup_database(self):
        """Sets up the database on the first run."""
        if self.first_run:
            self.logger.info(Fore.YELLOW + "Setting up the database." + Style.RESET_ALL)
            with io.open(FLAG_FILE, "w") as flag_file:
                self.logger.info(Fore.YELLOW + "Creating flag file." + Style.RESET_ALL)
                flag_file.write(f"Initial Run: {time.ctime()}")
            SQLExecutor("user_table", self.db_manager).execute_sql()
        else:
            self.logger.info(Fore.GREEN + "Database already set up." + Style.RESET_ALL)

if __name__ == "__main__":
    print(Fore.GREEN + "Initializing application...")

    # Configure logging
    log_id = str(uuid.uuid4())
    logging.basicConfig(filename=f"logs/{log_id}.log", level=logging.DEBUG)
    logger_instance = log()

    try:
        # Initialize main application class
        main_app = Main(logger_instance)

        # Check for flag file to determine if setup is needed
        if os.path.exists(FLAG_FILE):
            logger_instance.info(Fore.YELLOW + "Flag file exists. Skipping setup." + Style.RESET_ALL)
            main_app.first_run = False

        # Set up the database if needed
        main_app.setup_database()

        # Start the Flask application
        logger_instance.info(Fore.GREEN + "Starting Flask application." + Style.RESET_ALL)
        main_app.routes.initialize_routes()
        main_app.routes.run()

    except Exception as error:
        logger_instance.error(f"{Fore.RED}Error in Main: {error}{Style.RESET_ALL}")
        raise error

    print(Fore.RED + "Application terminated.")