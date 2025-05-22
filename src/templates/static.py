import os
from flask import send_from_directory, current_app, abort
import traceback

def handler(filepath: str):
    """
    Serves static files from the templates directory.
    
    Args:
        filepath: Path to the static file relative to the templates directory
                 e.g. 'js/jsonForm.js', 'css/main.css'
    
    Returns:
        The requested static file if found, or a 404 error if not found
    """
    print(f"Static handler for filepath: {filepath}")
    
    try:
        # Get the absolute path to the templates directory
        templates_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Templates directory: {templates_dir}")
        
        # Split the filepath into directory and filename
        parts = filepath.split('/')
        filename = parts[-1]
        subdir = '/'.join(parts[:-1]) if len(parts) > 1 else ''
        
        print(f"Subdir: '{subdir}', Filename: '{filename}'")
        
        # Construct the full directory path
        if subdir:
            directory = os.path.join(templates_dir, subdir)
        else:
            directory = templates_dir
            
        print(f"Looking for file in directory: {directory}")
        
        # Check if the directory exists
        if not os.path.exists(directory):
            print(f"Directory does not exist: {directory}")
            abort(404)
        
        # Check if the file exists
        full_path = os.path.join(directory, filename)
        print(f"Full path: {full_path}")
        
        if not os.path.isfile(full_path):
            print(f"File not found: {full_path}")
            # List directory contents to help debug
            print(f"Directory contents: {os.listdir(directory)}")
            abort(404)
        
        print(f"File found, serving: {full_path}")
        return send_from_directory(directory, filename)
    except Exception as e:
        print(f"Error in static handler: {str(e)}")
        print(traceback.format_exc())
        abort(500)