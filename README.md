To create the containers and run the playbook, do the following:

    docker build -t ubuntu-ansible -f Dockerfile.base .
    docker build -t misconfig1 -f Dockerfile.misconfig1 .
    docker run -v playbook.yml:/home/myuser/playbook -it misconfig1


To verify if the playbook worked, do the following:

    docker exec -it misconfig1 /bin/bash
    groups myuser

The user returned by whoami should be root (otherwise the playbook fails because a non-root user is not allowed to change user groups). The user myuser should be part of mygroup, if the playbook executed correctly.