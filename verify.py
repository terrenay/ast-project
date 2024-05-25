import subprocess

#This script is executed inside the container after the ansible playbook has
#finished. 

def get_command_stdout(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Verify: Error running command: {command}\nOutput: {result.stdout.decode()}\nError: {result.stderr.decode()}")
        exit()
    else:
        return result.stdout.decode('utf-8')
    
def exit_with_error(msg):
    with open("logs/error.txt", 'w') as file:
        file.write("Verify: " + msg)
    exit()



def main():
    print("Executing verify.py inside the container...")

    groups_of_myuser = get_command_stdout("groups myuser")
    if not "mygroup" in groups_of_myuser:
        exit_with_error("myuser is not in mygroup or mygroup does not exist!")
        
    ls_output = get_command_stdout("ls -la /etc/foo")
    # print("Verify: Output of ls_output: ")
    ls_output_split = ls_output.split()
    # print(ls_output_split)
    permissions = ls_output_split[2]
    user = ls_output_split[4]
    # print(f"Owner: {user}")
    group = ls_output_split[5]
    if user != "myuser":
        exit_with_error("myuser is not owner of foo directory!")
    if group != "mygroup":
        exit_with_error("mygroup is not group of foo directory!")
    if permissions != "drw-r--r--":
        exit_with_error("Incorrect permissions of /etc/foo directory")

    # print(ls_output)
    print("Verification has passed successfully! State reconciled by Ansible.")


if __name__ == "__main__":
    main()