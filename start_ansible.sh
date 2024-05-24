#!/usr/bin/env bash
#This script is the first thing executed in the container.
./modifications.sh
strace -o /home/myuser/logs/strace_log -ff -ttt ansible-playbook playbook.yml
strace-log-merge logs/strace_log > logs/merged_trace.log
python3 verify.py
