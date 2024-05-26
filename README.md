Please note that this artifact has been tested on an Ubuntu system. You need to have docker installed: https://docs.docker.com/engine/install/ubuntu/. Additionally, you need to have Python 3 installed: https://www.python.org/downloads/source/ 


# Running

Only when running the artifact for the first type, you need to build the base image once before proceeding. This might take a minute:
```bash
docker build -t ubuntu-ansible -f Dockerfile.base .
``` 

Then, to run the artifact, simply type:
```bash
python3 run.py
``` 


## What is happening

The base image `Dockerfile.base` contains a clean Ubuntu installation with some additional required packages such as Ansible and strace. The `run.py` script builds the `Dockerfile.misconfig1` image, which takes the base image, copies important files from the local working directory into the image (such as the `playbook.yml` and the `verify.py` script) and sets the entry point to `start_ansible.sh`. Then it runs the container. We provide `playbook.yml` which is an example playbook. It includes several tasks designed to modify user settings
and manage file permissions, leveraging some of Ansible’s built-in modules. The specific playbook used is just an example and it should be noted that the framework is easily
extendable to other playbooks containing different modules and system calls.

The `start_ansible.sh` script is responsible for running several processes in the correct order. First, `modifications.sh` is executed. This file is empty in the first container, but in subsequent containers it might contain instructions for modifying the initial system state. Afterwards, the Ansible playbook is executed, attached to `strace`. `strace` records all system calls issued by the playbook. The `-ff` flag ensures that system calls of spawned child processes are also recorded, while the `-ttt` flag timestamps each system call. Unfortunately, in some situations the system calls are interrupted, resulting in `unfinished` and subsequent `resume` entries in the strace log files and making analysis difficult. Therefore the `strace-log-merge` utility is executed inside the container to create a single consistent log file of all system calls. This log file is stored in the `logs` directory which is synchronized between the docker container and the local working directory. Finally, `verify.py` is executed inside the container to validate whether Ansible has correctly reconciled the desired state. If the verification script detects a violation, it writes this error into the synchronized `logs` directory.

Once the verification script finishes, the container shuts down and control is returned to the `run.py` script running locally. It starts the `strace_analysis` script which performs a system call analysis on the `logs/merged_trace.log` file. This is done by scanning each line in the system call trace for keywords such as `execve`, `useradd`, `groupadd`, `lchown`, etc. When a relevant line has been found, it is parsed into custom Python classes (called Actions) and stored in a list. For each action, one can define mutations. These specify how a given system resource corresponding to an action can be modified before the next run of the playbook. These mutations are shell commands which are written into the `modifications.sh` script by `strace_analysis.py`. This concludes the setup stage of the program.

Now, the process is repeated by building and starting a second docker container. This time, several modification are applied before executing the Ansible playbook (because `modifications.sh` is not empty anymore). 


## Expected Result

The expected result is that both docker containers pass the state reconciliation verification (i.e., the following is printed in the terminal: `Verification has passed successfully! State reconciled by Ansible.`). In the second run, the following Ansible error should be produced: `fatal: [localhost]: FAILED! => {"changed": false, "msg": "Could not recursively set attributes on /etc/foo. Original error was: 'maximum recursion depth exceeded'"}`. 


## About the expected result: Why is it interesting

In `playbook.yml`, the desired end state which Ansible must reach is (among others) to change the permissions of the `/etc/foo` directory (inside the container) to `u=rw,g=r,o=r`. The expectation is that Ansible throws an error if and only if it does not manage to reconcile parts of the state. 

The playbook is executed twice, in different containers. Before running the playbook in the second container, the script `modifications.sh` is applied (inside the container), which changes parts of the system state in a relevant way as determined by `strace_analysis.py`. Among other things, it creates an infinitely recursive symlink between `/etc/foo` and `/etc/foo2`. The expected behaviour of Ansible in this situation is that it either 
1. cannot reconcile the state, printing an error message, or 
2. reconciles the state correctly without printing an error message.

However, the inconsistency is that an Ansible error is printed (see expected result) even though it manages to reconcile the state correctly, as determined by the `verify.py` script. Therefore, the Ansible error should not appear in the first place.

## How to extend this to more system calls

If you want to use this framework to test more Ansible modules, you can follow these steps:
1. Adapt `playbook.yml` to use the modules you want to test.
2. Write a corresponding `verify.py` script to verify if the state you declare in the playbook has actually been reconciled.
3. In `strace_analysis.py`, extend the program to recognize the system calls which are relevant for your modules (if those already provided are not sufficient):
    1. Create a new class for each relevant system call, following the same structure as for example GroupAdd.
    2. Write a parse() function for your new class which takes as input a line of the system call log file, and call this function from the analyze_trace() function.
    3. Write a mutate() function for your new class which generates meaningful mutations and append those to the global mutations array.
