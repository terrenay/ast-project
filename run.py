import subprocess
import time

# Function to run Docker commands
def run_docker(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Error running command: {command}\nOutput: {result.stdout.decode()}\nError: {result.stderr.decode()}")
    else:
        print(f"Successfully ran command: {command}")

def run_docker_with_output(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Error running command: {command}\nOutput: {result.stdout.decode()}\nError: {result.stderr.decode()}")
    else:
        print(f"Successfully ran command: {command}")
        print(result.stdout.decode('utf-8'))


with open("modifications.sh", "w") as mod_file:
    mod_file.write("")
    

run_docker('docker rm ansible_run1; docker rm ansible_run2')

# First Docker run to capture system call traces
print("Running first Docker container to capture system call traces...")
run_docker('docker build -t misconfig1 -f Dockerfile.misconfig1 .')
run_docker_with_output('docker run --name ansible_run1 -v "$(pwd)/logs:/home/myuser/logs" -it misconfig1')
time.sleep(0.5)
# Analyze the trace file locally
print("Analyzing system call traces...")
subprocess.run(['python3', 'strace_analysis.py'])

# Second Docker run to execute the playbook with pre-configuration
print("Running second Docker container to execute playbook with modifications...")

run_docker('docker build -t misconfig1 -f Dockerfile.misconfig1 .')
run_docker_with_output('docker run --name ansible_run2 -v "$(pwd)/logs:/home/myuser/logs" -it misconfig1')
time.sleep(0.5)

print("Docker runs completed.")