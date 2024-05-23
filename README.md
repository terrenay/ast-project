To create the containers and run the playbook, do the following:

    docker build -t ubuntu-ansible -f Dockerfile.base .
    docker build -t misconfig1 -f Dockerfile.misconfig1 .
    docker run -it misconfig1

The -it flag is required to later establish a connection to the container via "docker exec". When the container starts, the start_ansible.sh script is executed in the /home/myuser directory inside the container. The script first executes the playbook attached to strace to monitor its system calls and logs them into a txt file. Then it runs the python script to analyze the system call trace and find out what it does and what system resources it could change. 

To verify if the playbook worked, do the following:

    docker ps

this gives you the container ID of the running misconfig1 instance. Then:

    docker exec -it <container-id> /bin/bash
    groups myuser

The user returned by whoami should be root (otherwise the playbook fails because a non-root user is not allowed to change user groups). The user myuser should be part of mygroup, if the playbook executed correctly.