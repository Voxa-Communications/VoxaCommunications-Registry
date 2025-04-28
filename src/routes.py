import os
import importlib
from lib.dynamicLibrary import DynamicLibraryLoader, DynamicLibrary
from flask import render_template, request, redirect, url_for, jsonify, flash, session, Flask

class Routes:
    def __init__(self, app: Flask, config: dict):
        self.app: Flask = app
        self.config: dict = config
    
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
                module = dynamic_library.module

                # Check if the module has a 'handler' function
                if hasattr(module, 'handler'):
                    handler_function = getattr(module, 'handler')
                    return handler_function(request)
                else:
                    return jsonify({"error": "Handler function not found in module"}), 404
            except ModuleNotFoundError:
                return jsonify({"error": f"Endpoint '{endpoint}' not found"}), 404

    def run(self):
        self.app.run(debug=True, port=self.config.get("PORT", 8000))

