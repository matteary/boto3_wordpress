import paramiko
import sys
import select
import time
from scp import SCPClient
ssh = paramiko.SSHClient()


def send_command(host, username, keypair, command):
    ssh_session = ssh_client(host, username, keypair)
    # ssh.exec_command(command)
    # print("\t\t\t\t- %s accessible" % host)
    stdin, stdout, stderr = ssh_session.exec_command(command)
    while not stdout.channel.exit_status_ready():
        if stdout.channel.recv_ready():
            r1, w1, x1 = select.select([stdout.channel], [], [], 0.0)
            if len(r1) > 0:
                print(stdout.channel.recv(1024))
    # ssh_session.close()


def scp_put(host, username, keypair, local_file, remote_path=None):
    ssh_session = ssh_client(host, username, keypair)
    scp = SCPClient(ssh_session.get_transport())
    if remote_path is None:
        scp.put(local_file)
    else:
        scp.put(local_file, remote_path=remote_path)


def ssh_client(host, username, keypair):
    i = 1
    while True:
        try:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=host, username=username, key_filename=keypair)
            # print("\t\t\t\t- %s accessible" % host)
            return ssh
        except paramiko.AuthenticationException:
            print("\t\t\t\tERROR: Authentication failed when connecting to %s" % host)
            sys.exit(1)
        except:
            # print("\t\t\t\t- %s pending (%i/60)" % (host, i))
            i += 1
            time.sleep(5)
        if i == 60:
            print("\t\tERROR: Connection to %s timed out" % host)
            sys.exit(1)
