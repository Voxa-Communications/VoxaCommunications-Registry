import os
import datetime
from kvprocessor import KVProcessor, KVStructLoader, KVNamespaceManager
from flask import redirect, jsonify, Request, url_for, session, render_template

def handler(request: Request, struct_loader: KVStructLoader):
    # Check the request path and redirect accordingly
    struct_processor: KVProcessor = struct_loader.from_namespace("voxa.testing.registry.template")
    config_spec = struct_processor.config_spec
    i = -1
    for path in struct_processor.return_names():
        i += 1
        default = dict(config_spec[path]).get("default")
        print(request.query_string, path, default)
        if str(request.query_string.decode()).split("=")[1] == path:
            return render_template(f"{str(default)}.html") # Get the default value as defined in the KV file
    return render_template(f"default.html")
