import os
import json
from datetime import datetime

def get_instance_dir(logging_dir):
    dir_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')

    path = f"{logging_dir}/{dir_name}"
    if not os.path.exists(path):
        os.makedirs(path)
    
    return path

def write_file(filename, content):
    with open(filename, 'w') as f:
        f.write(content)

class ModelLogger:
    def __init__(self, logging_dir='./logs'):
        self.logging_dir = logging_dir
    
    def log(self, prompt, response, function=None):
        instance_path = get_instance_dir(self.logging_dir)

        write_file(f"{instance_path}/prompt.txt", prompt)
        if response:
            write_file(f"{instance_path}/response.txt", response)
        if function:
            f_str = json.dumps(function)
            write_file(f"{instance_path}/function.txt", f_str)
        
