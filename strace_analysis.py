import subprocess
import time

#This script runs locally and analyses the trace file in /logs.
#It modifies modifications.sh to mutate the initial system configuration
#of the next docker container in a way that's relevant to the playbook.

actions = []
mutations = []


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
        
    def parse(self):
        pass

    def mutate(self):
        pass

class UserAdd(Action):
    def __init__(self, username: str, groupname: str):
        super().__init__()
        self.username = username
        self.groupname = groupname
        self.prerequisite = GroupExists(groupname)
        
    def __str__(self):
        return f"UserAdd(username='{self.username}', groupname='{self.groupname}', prerequisite={self.prerequisite})"
    
    def parse(useradd_string: str):
        tmp = useradd_string.split('[')[1]
        tmp2 = tmp.split(']')[0]
        tmp3 = tmp2.split(',')
        groupname = tmp3[2].split('"')[1]
        username = tmp3[4].split('"')[1]
        actions.append(UserAdd(username, groupname))
    
    def mutate(self):
        # Mutation 1: Add User and add it to different group
        commands = ["groupadd randomgroup", f"useradd {self.username} -g randomgroup"]
        mutations.append(commands)
        
        # Mutation 2: Add user with a different shell
        commands = [f"useradd -m -s /bin/false {self.username}"]
        mutations.append(commands)
        
        # Mutation 3: Add user with a different home directory
        new_home_dir = f"/home/{self.username}_custom"
        commands = [f"useradd -m -d {new_home_dir} {self.username}"]
        mutations.append(commands)
        
        # Mutation 4: Add user without a home directory
        commands = [f"useradd -M {self.username}"]
        mutations.append(commands)
        
        # Mutation 5: Add user and lock the account
        commands = [f"useradd {self.username}", f"passwd -l {self.username}"]
        mutations.append(commands)

class GroupAdd(Action):
    def __init__(self, groupname: str):
        super().__init__()
        self.groupname = groupname

    def __str__(self):
        return f"GroupAdd(groupname='{self.groupname}', prerequisite={self.prerequisite})"

    def parse(group_string: str):
        tmp = group_string.split('[')[1]
        tmp2 = tmp.split(']')[0]
        tmp3 = tmp2.split(',')[1]
        tmp4 = tmp3.split('"')[1]
        return GroupAdd(tmp4)

    def mutate(self):
        # Mutation 1: Group already exists
        commands = ["groupadd " + self.groupname]
        mutations.append(commands)

class LChown(Action):
    def __init__(self, foldername: str, owner_uid: int, group_gid: int):
        super().__init__()
        self.foldername = foldername
        self.owner_uid = owner_uid
        self.group_gid = group_gid

    def __str__(self):
        return f"LChown(foldername='{self.foldername}', owner='{self.owner_uid}', group='{self.group_gid}', prerequisite={self.prerequisite})"

    def parse(lchown_string: str):
        tmp = lchown_string.split('(')[1]
        tmp2 = tmp.split(')')[0]
        tmp3 = tmp2.split(',')
        foldername = tmp3[0].split('"')[1]
        owner_uid = int(tmp3[1])
        group_gid = int(tmp3[2])
        actions.append(LChown(foldername, owner_uid, group_gid))

    def mutate(self):
        # Mutation 1: Infinitely recursive Symlinks
        commands = []
        foldername2 = self.foldername + "2"
        commands.append("mkdir " + self.foldername)
        commands.append("mkdir " + foldername2)
        commands.append(f"ln -s {self.foldername} {foldername2}")
        commands.append(f"ln -s {foldername2} {self.foldername}")
        mutations.append(commands)
        
        #Mutation 2: Change rights of folder to 000
        commands = []
        commands.append("mkdir " + self.foldername)
        commands.append(f"chmod -R 755 " + self.foldername)
        mutations.append(commands)
        
        #Mutation 3: Change ownership of folder to random user
        commands = []
        commands.append('adduser --disabled-password --gecos "" randomuser')
        commands.append('sudo chown -R randomuser:randomuser ' + self.foldername)
        mutations.append(commands)

def analyze_trace(trace_lines):
    for line in trace_lines:
        new_action = None
        if 'execve("' in line:
            if 'useradd' in line:
                new_action = UserAdd.parse(line)
            if 'groupadd' in line:
                new_action = GroupAdd.parse(line)
        if 'lchown("' in line:
            new_action = LChown.parse(line)
        if new_action is not None:
            actions.append(new_action)

print("Starting analysis")
with open("logs/merged_trace.log", 'r') as trace_lines:
    analyze_trace(trace_lines)
    for a in actions:
        print("Action: " + str(a))
        a.mutate()
    with open("modifications.sh", 'w') as mods:
        for m in mutations:
            for command in m:
                print("Writing mutations to modification.sh: " + command)
                mods.write(command + "\n")