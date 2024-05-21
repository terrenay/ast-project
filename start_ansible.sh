#!/usr/bin/env bash
strace -o log.txt -f ansible-playbook playbook.yml
/bin/bash