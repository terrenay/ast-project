#!/usr/bin/env bash
./modifications.sh
strace -o /home/myuser/logs/strace_log.txt -f ansible-playbook playbook.yml
# bash
