#!/usr/bin/python
import boto3
import os
import variables
import time
from modules import prompt, index, ec2
ec2_resource = boto3.resource('ec2')
ec2_client = boto3.client('ec2')
index = index.get_hex()
project = "test"
key_pair = "test-" + index
key_pair_pem = os.environ['HOME'] + "/.ssh/" + key_pair + ".pem"
ec2_client = ec2_client
security_group = "test-" + index
security_group_desc = "Test security group"
instance_id_file = variables.source_dir + "/cache/" + project + "-instanceID.txt"
instance_tag_name = project + "-instance-" + index
index_file = variables.source_dir + "/cache/" + project + "-" + index + ".txt"
security_group_ingress_ports = [22, 80, 443]
ami_id = "ami-3e32f05e"
instance_type = "m1.small"
tags = [{
    "Key": "Name",
    "Value": instance_tag_name
}]


def environment():
    print("\n\tDeploying Linux with WordPress environment...\n")

    f = open(index_file, 'w')
    f.write(index)
    f.close()

    if os.path.isfile(key_pair_pem):
        prompt.query_yes_no("\t\tFound existing [~/.ssh/" + key_pair_pem + "]:\n"
                                                                           "\t\tDo you want to delete?")
        if True:
            prompt.query_yes_no("\t\t\tWARNING:\n"
                                "\t\t\tDeleting keypair will render hosts associated with it inaccessible!\n"
                                "\t\t\tConfirm:")
            if True:
                os.remove(key_pair_pem)
                time.sleep(1)

    print("\t\t* Creating key pair [~/.ssh/" + key_pair + ".pem]")
    new_key_pair = ec2.create_key_pair(key_pair)
    f = open(key_pair_pem, 'w')
    f.write(new_key_pair['KeyMaterial'])
    f.close()
    os.chmod(key_pair_pem, 0o400)

    print("\t\t* Creating security group [" + security_group + "]")
    new_security_group = ec2.create_security_group(security_group, security_group_desc)

    print ("\t\t\t* Allowing ports in security group [" + security_group + "]")
    for port in security_group_ingress_ports:
        new_security_group.authorize_ingress(
            GroupName=security_group,
            IpProtocol="tcp",
            FromPort=port,
            ToPort=port,
            CidrIp="0.0.0.0/0"
        )

    new_security_group.reload()
    print("\t\t* Spinning up an instance")
    instances = ec2.create_instance(ami_id, instance_type, key_pair, security_group)

    instance = instances[0]
    instance.wait_until_running()
    instance.load()

    instance_public_dns = instance.public_dns_name

    f = open(instance_id_file, 'w')
    f.write(instance.id)
    f.close()

    print("\t\t\t* Instance [" + instance.id + "] started")
    print("\t\t\t* Tagging instance")
    ec2_client.create_tags(Resources=[instance.id], Tags=tags)

    print("\t\t* Create EBS Volume and attach to instance [" + instance.id + "]")
    volume = ec2.create_volume(ec2.get_instance_availability_zone(instance.id))
    ec2.attach_volume(instance.id, volume.id, device='/dev/sdh')


def erase():
    with open(index_file, 'r') as test_index_file:
        test_index = index_file.read()
    test_index_file.close()
    test_key_pair = project + "-key-pair-" + test_index
    test_key_pair_pem = os.environ['HOME'] + "/.ssh/" + key_pair + ".pem"
    test_security_group = project + "-security-group-" + test_index

    print("\n\tTearing down Linux with WordPress environment...\n")

    print("\t\t* Deleting key pair [~/.ssh/" + test_key_pair + ".pem]")
    ec2_client.delete_key_pair(KeyName=test_key_pair)

    with open(instance_id_file, 'r') as my_file:
        instance_id = my_file.read()

    print("\t\t* Terminating instance [" + instance_id + "]")
    instance = ec2_resource.Instance(instance_id)
    instance.terminate()
    instance.wait_until_terminated()

    print("\t\t* Deleting security group [" + test_security_group + "]\n")
    ec2_client.delete_security_group(GroupName=test_security_group)
    for local_file in instance_id_file, test_key_pair_pem, index_file:
        os.remove(local_file)