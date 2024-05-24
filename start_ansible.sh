#!/usr/bin/env bash
./modifications.sh
strace -o /home/myuser/logs/strace_log -ff -ttt ansible-playbook playbook.yml
strace-log-merge logs/strace_log > logs/merged_trace.log
# bash
