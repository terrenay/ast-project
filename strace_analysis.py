import subprocess

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

class GroupAdd(Action):
    def __init__(self, groupname: str):
        super().__init__()
        self.groupname = groupname

    def __str__(self):
        return f"GroupAdd(groupname='{self.groupname}', prerequisite={self.prerequisite})"

    def mutate(self):
        command = "groupadd " + self.groupname
        mutations.append(command)

class LChown(Action):
    def __init__(self, filename: str, owner_uid: int, group_gid: int):
        super().__init__()
        self.filename = filename
        self.owner_uid = owner_uid
        self.group_gid = group_gid

    def __str__(self):
        return f"LChown(filename='{self.filename}', owner='{self.owner_uid}', group='{self.group_gid}', prerequisite={self.prerequisite})"

    def mutate(self):
        command = "mkdir " + self.filename
        mutations.append(command)
        filename2 = self.filename + "2"
        command2 = "mkdir " + filename2
        mutations.append(command2)
        command3 = f"ln -s {self.filename} {filename2}"
        command4 = f"ln -s {filename2} {self.filename}"
        mutations.append(command3)
        mutations.append(command4)

def parse_groupadd(group_string: str):
    tmp = group_string.split('[')[1]
    tmp2 = tmp.split(']')[0]
    tmp3 = tmp2.split(',')[1]
    tmp4 = tmp3.split('"')[1]
    actions.append(GroupAdd(tmp4))

def parse_useradd(useradd_string: str):
    tmp = useradd_string.split('[')[1]
    tmp2 = tmp.split(']')[0]
    tmp3 = tmp2.split(',')
    groupname = tmp3[2].split('"')[1]
    username = tmp3[4].split('"')[1]
    actions.append(UserAdd(username, groupname))

def parse_lchown(lchown_string: str):
    tmp = lchown_string.split('(')[1]
    tmp2 = tmp.split(')')[0]
    tmp3 = tmp2.split(',')
    filename = tmp3[0].split('"')[1]
    owner_uid = int(tmp3[1])
    group_gid = int(tmp3[2])
    actions.append(LChown(filename, owner_uid, group_gid))


def analyze_trace(trace_lines):
    for line in trace_lines:
        if 'execve("' in line:
            if 'useradd' in line:
                parse_useradd(line)
            if 'groupadd' in line:
                parse_groupadd(line)
        if 'lchown("' in line:
            # print(line)
            parse_lchown(line)

print("Starting analysis")
with open("logs/strace_log.txt", 'r') as trace_lines:
    analyze_trace(trace_lines)
    for a in actions:
        print("Mutating " + str(a))
        a.mutate()
    with open("modifications.sh", 'w') as mods:
        for m in mutations:
            print("Writing mutations to modification.sh: " + m)
            mods.write(m + "\n")