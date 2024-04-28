To create the containers and run the playbook, do the following:

    docker build -t ubuntu-ansible -f Dockerfile.base .
    docker build -t misconfig1 -f Dockerfile.misconfig1 .
    docker run -v playbook.yml:/home/myuser/playbook -it misconfig1 sh -c "ansible-playbook -vvv playbook.yml; /bin/bash"

The -v flag mounts the local playbook into the container so it can be executed. The -it flag is required to later establish a connection to the container via "docker exec". 
The "sh -c" spawns a shell in the container and executes first the ansible-playbook command and then the /bin/bash command. Without the /bin/bash command, the container would die as soon as the playbook has finished executing, which would make it impossible to connect to it via "docker exec" later on.


To verify if the playbook worked, do the following:

    docker ps

this gives you the container ID of the running misconfig1 instance. Then:

    docker exec -it <container-id> /bin/bash
    groups myuser

The user returned by whoami should be root (otherwise the playbook fails because a non-root user is not allowed to change user groups). The user myuser should be part of mygroup, if the playbook executed correctly.