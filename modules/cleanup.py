#!/usr/bin/python
import os
import variables


def environment():
    with open(variables.index_file, 'r') as index_file:
        index = index_file.read()
    ec2 = variables.ec2
    ec2_client = variables.ec2_client
    key_pair = variables.project + "-key-pair-" + index
    key_pair_pem = os.environ['HOME'] + "/.ssh/" + key_pair + ".pem"
    security_group = variables.project + "-security-group-" + index

    print("\n\tTearing down Linux with WordPress environment...\n")

    print("\t\t* Deleting key pair [~/.ssh/" + key_pair + ".pem]")
    ec2_client.delete_key_pair(KeyName=key_pair)

    with open(variables.instance_id_file, 'r') as my_file:
        instance_id = my_file.read()

    print("\t\t* Terminating instance [" + instance_id + "]")
    instance = ec2.Instance(instance_id)
    instance.terminate()
    instance.wait_until_terminated()

    with open(variables.volume_id_file, 'r') as vol_file:
        volume_id = vol_file.read()
    volume = ec2.Volume(volume_id)
    print("\t\t* Deleting volume [" + volume_id + "]")
    volume.delete()

    print("\t\t* Deleting security group [" + security_group + "]")
    ec2_client.delete_security_group(GroupName=security_group)

    print("\t\t* Deleting cache files\n")
    for local_file in variables.instance_id_file, key_pair_pem, variables.index_file, variables.volume_id_file:
        os.remove(local_file)
