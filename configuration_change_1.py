##IDEA: simulate adding a user to a group and monitor system calls. 
# Filter them to get paths to files. 
# Modify the permissions of these files in order to modify the system state. 
# Everything works in an automated manner.

import re
import os
import shutil
import random

def parse_strace_output(file):
    # Regex pattern to match file paths in system calls
    file_pattern = re.compile(r'\"(/.*?)\"')

    paths = set()
    with open(file, 'r') as f:
        for line in f:
            match = file_pattern.search(line)
            if match:
                path = match.group(1)
                paths.add(path)
    return paths

def change_permissions(path, mode):
    if os.path.exists(path):
        os.chmod(path, mode)

# Parse the strace output to get the list of file paths
strace_file = 'strace_output.txt'
critical_paths = parse_strace_output(strace_file)

# Filter paths containing "user"
user_paths = [path for path in critical_paths if "user" in path]

# Apply state changes to the random subset of paths
for path in user_paths:
    print(f"Changing permissions for: {path}")  # No permissions
    change_permissions(path, 0o000)

print("System state changes applied to a random subset of paths to potentially break the ansible program.")
