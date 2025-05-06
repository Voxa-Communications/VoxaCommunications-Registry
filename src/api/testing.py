import os
import datetime
from kvprocessor import KVProcessor, KVStructLoader, KVNamespaceManager
from flask import redirect, jsonify, Request, url_for, session, render_template

def handler(request: Request, struct_loader: KVStructLoader):
    # Check the request path and redirect accordingly
    struct_processor: KVProcessor = struct_loader.from_namespace("voxa.testing.registry.template")
    config_spec = struct_processor.config_spec
    for path in struct_processor.return_names():
        print(request.query_string, path)
        if request.query_string == bytes(path, 'utf-8'):
            return render_template(f"src/templates/{str(dict(config_spec[path]).get("default"))}.html") # Get the default value as defined in the KV file
