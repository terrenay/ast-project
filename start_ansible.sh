#!/usr/bin/env bash
strace -o strace_log.txt -f ansible-playbook playbook.yml
python3 strace_analysis.py
# bash