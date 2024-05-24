#!/usr/bin/env bash
./modifications.sh
strace -o /home/myuser/logs/strace_log -ff -ttt ansible-playbook playbook.yml
# bash
