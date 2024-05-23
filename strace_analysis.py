##IDEA: simulate adding a user to a group and monitor system calls. 
# Filter them to get paths to files. 
# Modify the permissions of these files in order to modify the system state. 
# Everything works in an automated manner.

import re
import os
import shutil
import random

actions = []


class Fact:
    pass

class GroupExists(Fact):
    def __init__(self, groupname: str):
        self.groupname = groupname
    
    def __str__(self):
        return f"GroupExists(groupname='{self.groupname}')"


class Action:
    def __init__(self):
        self.prerequisite: Fact = None

class UserAdd(Action):
    def __init__(self, username: str, groupname: str):
        super().__init__()
        self.username = username
        self.groupname = groupname
        self.prerequisite = GroupExists(groupname)
        
    def __str__(self):
        return f"UserAdd(username='{self.username}', groupname='{self.groupname}', prerequisite={self.prerequisite})"

class GroupAdd(Action):
    def __init__(self, groupname: str):
        super().__init__()
        self.groupname = groupname

    def __str__(self):
        return f"GroupAdd(groupname='{self.groupname}', prerequisite={self.prerequisite})"


#currently only works for groupadd program
def get_group_name(group_string: str):
    # print(string)
    tmp = group_string.split('[')[1]
    # print(tmp)
    tmp2 = tmp.split(']')[0]
    # print(tmp2)
    tmp3 = tmp2.split(',')[1]
    # print(tmp3)
    tmp4 = tmp3.split('"')[1]
    actions.append(GroupAdd(tmp4))

#currently only works for useradd program
def get_username_groupname(useradd_string: str):
    if not 'useradd' in useradd_string:
        print("currently not supported")
        exit()
    # print(string)
    tmp = useradd_string.split('[')[1]
    # print(tmp)
    tmp2 = tmp.split(']')[0]
    # print(tmp2)
    tmp3 = tmp2.split(',')
    # print(tmp3)
    groupname = tmp3[2].split('"')[1]
    username = tmp3[4].split('"')[1]
    actions.append(UserAdd(username, groupname))


def extract_parameters(trace_lines):
    file_operations = []
    env_variables = []
    services = []
    users = []
    groups = []
    processes = []

    for line in trace_lines:
        # Extract file operations
        if 'open' in line or 'openat' in line or 'fopen' in line:
            match = re.search(r'open(at)?\((.*)\)', line)
            if match:
                params = match.group(2).split(',')
                file_operations.append(params[0].strip())

        # Extract environment variables
        if 'setenv' in line or 'putenv' in line:
            match = re.search(r'(setenv|putenv)\((.*)\)', line)
            if match:
                params = match.group(2).split(',')
                env_variables.append(params[0].strip())

        # Extract service operations
        if 'systemctl' in line or 'service' in line:
            match = re.search(r'(systemctl|service)\s+(\w+)', line)
            if match:
                services.append(match.group(2).strip())

        # Extract user operations
        # if 'user' in line or 'useradd' in line or 'userdel' in line:
        #     # users.append(line)
        #     match = re.search(r'(useradd|userdel|usermod)\s+(\w+)', line)
        #     if match:
        #         users.append(match.group().strip())
        if 'execve("' in line:
            if 'usermod' in line or 'useradd' in line or 'userdel' in line:
                users.append(line)
            if 'groupadd' in line or 'groupdel' in line or 'groupmod' in line:
                groups.append(line)

        # Extract group operations
        # if 'group' in line or 'groupadd' in line or 'groupdel' in line:
            # groups.append(line)
            # match = re.search(r'(groupadd|groupdel|group)\s+(\w+)', line)
            # if match:
            #     groups.append(match.group().strip())

    return file_operations, env_variables, services, users, groups, processes

print("Starting analysis")
with open("strace_log.txt", 'r') as trace_lines:
    file_operations, env_variables, services, users, groups, processes = extract_parameters(trace_lines)
    # print("File operations:")
    # print(file_operations)
    # print("env variables:")
    # print(env_variables)
    # print("services:")
    # print(services)
    # print("Users:")
    for u in users:
        get_username_groupname(u)
    print("groups:")
    for g in groups:
        # print(type(g))
        get_group_name(g)
        # print(g)
    print("\nprocesses:\n")
    for p in processes:
        print(p)
    print("Actions:")
    for a in actions:
        print(a)