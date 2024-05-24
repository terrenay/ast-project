import subprocess

#This script is executed inside the container after the ansible playbook has
#finished. 

def get_command_stdout(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Verify: Error running command: {command}\nOutput: {result.stdout.decode()}\nError: {result.stderr.decode()}")
        exit(-1522975)
    else:
        return result.stdout.decode('utf-8')

print("Executing verify.py inside the container...")

groups_of_myuser = get_command_stdout("groups myuser")
if not "mygroup" in groups_of_myuser:
    print("myuser is not in mygroup!")
    exit(-1522975)

print("Verification has passed successfully! State reconciled by Ansible.")