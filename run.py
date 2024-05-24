import subprocess
import time
import os
import glob

#This script is the main driver of the whole program.

# Function to run Docker commands
def run_command(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Error running command: {command}\nOutput: {result.stdout.decode()}\nError: {result.stderr.decode()}")
    else:
        print(f"Successfully ran command: {command}")

def run_command_with_output(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Error running command: {command}\nOutput: {result.stdout.decode()}\nError: {result.stderr.decode()}")
    else:
        print(f"Successfully ran command: {command}")
        print(result.stdout.decode('utf-8'))

def run_docker(container_name):
    command = f'docker run --name {container_name} -v "$(pwd)/logs:/home/myuser/logs" -it misconfig1'
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Error running command: {command}\nOutput: {result.stdout.decode()}\nError: {result.stderr.decode()}")
    else:
        print(f"Successfully ran command: {command}")
        output = result.stdout.decode('utf-8')
        print(output)
        if "fatal: [localhost]: FAILED!" in output:
            print("Ansible threw an error. This might be an actual bug or it might\
                  be due to a mutation changing some of Ansible's requirements.")
            exit()

def remove_strace_logs():
    files = glob.glob("logs/strace_log*")
    for f in files:
        os.remove(f)

def remove_containers():
    run_command('docker rm ansible_run1; docker rm ansible_run2')


def main():
    with open("modifications.sh", "w") as mod_file:
        mod_file.write("")
    
    remove_containers()

    # First Docker run to capture system call traces
    print("Running first Docker container to capture system call traces...")
    run_command('docker build -t misconfig1 -f Dockerfile.misconfig1 .')
    run_docker("ansible_run1")
    time.sleep(0.3)
    remove_strace_logs()
    time.sleep(0.3)
    # Analyze the trace file locally
    print("Analyzing system call traces...")
    subprocess.run(['python3', 'strace_analysis.py'])

    # Second Docker run to execute the playbook with pre-configuration
    print("Running second Docker container to execute playbook with modifications...")

    run_command('docker build -t misconfig1 -f Dockerfile.misconfig1 .')
    run_docker("ansible_run2")
    time.sleep(0.3)
    remove_strace_logs()
    time.sleep(0.3)

    print("Docker runs completed.")

if __name__ == "__main__":
    try:
        main()
    finally:
        remove_strace_logs()
        remove_containers()
