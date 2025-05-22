import os
import datetime
from kvprocessor import KVProcessor, KVStructLoader, KVNamespaceManager
from flask import redirect, jsonify, Request, url_for, session, render_template

def handler(request: Request, struct_loader: KVStructLoader):
    # Check the request path and redirect accordingly
    struct_processor: KVProcessor = struct_loader.from_namespace("voxa.testing.registry.template")
    config_spec = struct_processor.config_spec
    for path in struct_processor.return_names():
        default = dict(config_spec[path]).get("default")
        print(request.query_string, path, default)
        # Request example: http://127.0.0.1:8000/api/v1/testing?template=login
        query_param = request.args.get('template')  # Replace 'param' with the actual query parameter name
        if query_param == path:
            return render_template(f"{str(default)}.html") # Get the default value as defined in the KV file
    return render_template(f"default.html")
