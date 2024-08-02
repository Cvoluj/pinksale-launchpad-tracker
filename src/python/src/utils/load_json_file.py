import json
import os

def load_json_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as json_file:
            return json.load(json_file)
        
    return None