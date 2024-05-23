
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


def analyze_trace(trace_lines):
    for line in trace_lines:
        if 'execve("' in line:
            if 'useradd' in line:
                parse_useradd(line)
            if 'groupadd' in line:
                parse_groupadd(line)

print("Starting analysis")
with open("strace_log.txt", 'r') as trace_lines:
    analyze_trace(trace_lines)
    for a in actions:
        print(a)