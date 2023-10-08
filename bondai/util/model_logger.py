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
        self.tail_log_file = './logs/bondai.log'  # Dedicated log file to tail
    
    def log(self, prompt, response, function=None):
        instance_path = get_instance_dir(self.logging_dir)
        instance_path = get_instance_dir(self.logging_dir)

        # Existing logic to write to individual files
        write_file(f"{instance_path}/prompt.txt", prompt)
        if response:
            write_file(f"{instance_path}/response.txt", response)
        if function:
            f_str = json.dumps(function)
            write_file(f"{instance_path}/function.txt", f_str)

        # New logic to append to dedicated tail log file
        with open(self.tail_log_file, 'a') as f:
            f.write(f"User: {prompt}\n")
            if response:
                f.write(f"AI: {response}\n")
            if function:
                f.write(f"Function: {json.dumps(function)}\n")