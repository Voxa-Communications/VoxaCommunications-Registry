import os
import importlib
import inspect
from typing import Optional
from kvprocessor import KVProcessor, KVStructLoader
from flask import render_template, request, redirect, url_for, jsonify, flash, session, Flask
from util.logging import log
from util.exception_handlers import log_exceptions
from lib.dynamiclibrary.loader import DynamicLibraryLoader
from lib.dynamiclibrary.structs import DynamicLibrary
from lib.security.ratelimiter.rate_lib import rate_limit, global_rate_limiter
from mysql.connector import Error as MYSQL_Error
from templates.static import handler as static_handler

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
        
        @self.app.errorhandler(429)
        def rate_limit_error(e):
            return jsonify({
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later."
            }), 429
    
    def initialize_routes(self):
        @self.app.route('/')
        def index():
            return "This is an API Server, Requires a client to interface with. Or, if you are a nerd, you can use CURL to interface with it. :)"
        
        # Configure rate limits from application config
        if self.config.get("RATE_LIMITS"):
            for endpoint, limit_config in self.config.get("RATE_LIMITS").items():
                if "limit" in limit_config and "window" in limit_config:
                    global_rate_limiter.set_rate_limit(
                        endpoint, 
                        limit_config["limit"], 
                        limit_config["window"]
                    )
        
        # Add a rate-limiting stats endpoint for admins/monitoring
        @self.app.route('/api/admin/rate_stats', methods=["GET"])
        @rate_limit(limit=20, window=60)  # Lower limit for admin endpoints
        def rate_stats():
            # Only allow access with admin token
            admin_token = request.headers.get('X-Admin-Token')
            if not admin_token or admin_token != self.config.get("ADMIN_TOKEN"):
                return jsonify({"error": "Unauthorized access"}), 401
                
            # Get stats based on query parameters
            endpoint = request.args.get('endpoint')
            user_id = request.args.get('user_id')
            ip = request.args.get('ip')
            
            # Import the stats function here to avoid circular imports
            from lib.security.ratelimiter.rate_lib import get_rate_stats
            stats = get_rate_stats(endpoint=endpoint, user_id=user_id, ip=ip)
            return jsonify(stats)
        
        @log_exceptions
        @self.app.route('/api/v1/<endpoint>', methods=["POST", "GET"])
        @rate_limit()  # Apply default rate limiting to all API endpoints
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
        
        # Special rate limits for sensitive endpoints
        # Login route - stricter rate limiting
        @self.app.route('/api/auth/login', methods=["POST"])
        @rate_limit(limit=5, window=60)  # 5 login attempts per minute
        def login():
            # Delegate to the login handler
            try:
                module_loader = DynamicLibraryLoader("api.login")
                dynamic_library: DynamicLibrary = module_loader.load_module()
                dynamic_library.set_signature('handler')
                handler_function = dynamic_library.loadattr('handler')
                return handler_function(request, struct_loader=self.struct_loader)
            except Exception as e:
                self.logger.error(f"Login error: {str(e)}")
                return jsonify({"error": "Login failed", "message": str(e)}), 500
        
        # Used for the testing templates
        @self.app.route('/static/<path:filepath>', methods=["POST", "GET"])
        @rate_limit(limit=120, window=60)  # Higher limit for static resources
        def static_api(filepath):
            try:
                self.logger.info(f"Static handler for filepath: {filepath}")
                return static_handler(filepath)
            except Exception as e:
                self.logger.error(f"Static handler error: {str(e)}")
                return jsonify({"error": f"Static resource '{filepath}' not found"}), 404

    @log_exceptions
    def run(self, debug: Optional[bool] = True, use_reloader: Optional[bool] = False):
        # Disable reloader to prevent Flask from creating two instances
        self.app.run(debug=debug, use_reloader=use_reloader, port=self.config.get("PORT", 8000))

