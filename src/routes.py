import os
import importlib
import inspect
from typing import Optional
from kvprocessor import KVProcessor, KVStructLoader
from flask import render_template, request, redirect, url_for, jsonify, flash, session, Flask
from util.logging import log
from templates.static import handler as static_handler
from lib.dynamicLibrary import DynamicLibraryLoader, DynamicLibrary
from mysql.connector import Error as MYSQL_Error

class Routes:
    def __init__(self, app: Flask, config: dict, struct_loader: KVStructLoader):
        self.app: Flask = app
        self.config: dict = config
        self.struct_loader: KVStructLoader = struct_loader
        self.logger = log()

    def error_handling(self):
        @self.app.errorhandler(404)
        def page_not_found(e):
            return jsonify({"error": "Page not found"}), 404

        @self.app.errorhandler(500)
        def internal_server_error(e):
            return jsonify({"error": "Internal server error"}), 500
        
        @self.app.errorhandler(MYSQL_Error)
        def mysql_error(e):
            return jsonify({"error": "MySQL error", "message": str(e)}), 500
    
    def initialize_routes(self):
        @self.app.route('/')
        def index():
            return "This is an API Server, Requires a client to interface with. Or, if you are a nerd, you can use CURL to interface with it. :)"
        
        @self.app.route('/api/v1/<endpoint>', methods=["POST", "GET"])
        def dynamic_api(endpoint):
            try:
                # Construct the module path dynamically
                module_name = f"api.{endpoint}"
                module_loader = DynamicLibraryLoader(module_name)

                dynamic_library: DynamicLibrary = module_loader.load_module()

                # Check if the module has a 'handler' function
                dynamic_library.set_signature('handler')
                handler_function = dynamic_library.loadattr('handler')
                if handler_function:
                    self.logger.info(f"Handler function found in module {module_name}")
                    # Check if the handler function accepts 'struct_loader' parameter
                    param_names = dynamic_library.param_names()
                    
                    # If the function accepts more than one parameter or has **kwargs
                    if len(param_names) > 1 or any(p.kind == inspect.Parameter.VAR_KEYWORD for p in dynamic_library.param_values()):
                        return handler_function(request, struct_loader=self.struct_loader)
                    else:
                        # The function only accepts the request parameter
                        return handler_function(request)
                else:
                    self.logger.error(f"Handler function not found in module {module_name}")
                    return jsonify({"error": "Handler function not found in module"}), 404
            except ModuleNotFoundError as e:
                self.logger.error(f"Module not found: {str(e)}")
                return jsonify({"error": f"Endpoint '{endpoint}' not found"}), 404
        
        # Used for the testing templates
        @self.app.route('/static/<path:filepath>', methods=["POST", "GET"])
        def static_api(filepath):
            try:
                self.logger.info(f"Static handler for filepath: {filepath}")
                return static_handler(filepath)
            except Exception as e:
                self.logger.error(f"Static handler error: {str(e)}")
                return jsonify({"error": f"Static resource '{filepath}' not found"}), 404

    def run(self, debug: Optional[bool] = True, use_reloader: Optional[bool] = False):
        # Disable reloader to prevent Flask from creating two instances
        self.app.run(debug=debug, use_reloader=use_reloader, port=self.config.get("PORT", 8000))

