#!/usr/bin/python
import os
import variables
import time
from modules import ssh, prompt, misc, generate
from modules import ec2 as ec2_module

# from scp import SCPClient

ec2 = variables.ec2
ec2_client = variables.ec2_client
key_pair_pem = variables.key_pair_pem


def environment():
    if not os.path.isdir(variables.source_dir + "/cache"):
        os.mkdir(variables.source_dir + "/cache", 0o755)

    print("\n\tDeploying Linux with WordPress environment...\n")

    f = open(variables.index_file, 'w')
    f.write(variables.index)
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

    print("\t\t* Creating key pair [~/.ssh/" + variables.key_pair + ".pem]")
    key_pair = ec2_module.create_key_pair(variables.key_pair)
    misc.create_key_pair_pem(key_pair['KeyMaterial'])

    print("\t\t* Creating security group [" + variables.security_group + "]")
    security_group = ec2_module.create_security_group(variables.security_group, variables.security_group_desc)

    time.sleep(1)

    print ("\t\t\t* Allowing ports in security group [" + variables.security_group + "]")
    for port in variables.security_group_ingress_ports:
        security_group.authorize_ingress(
            GroupName=variables.security_group,
            IpProtocol="tcp",
            FromPort=port,
            ToPort=port,
            CidrIp="0.0.0.0/0"
        )

    security_group.reload()

    print("\t\t* Spinning up an instance")
    # instances = ec2_module.create_instance(variables.ami_id,
    #                                        variables.instance_type,
    #                                        variables.key_pair,
    #                                        security_group.group_id
    #                                        )

    instances = ec2_module.create_instance_with_ephemeral(variables.ami_id,
                                                          variables.instance_type,
                                                          variables.key_pair,
                                                          security_group.group_id,
                                                          variables.device_name_ephemeral
                                                          )

    instance = instances[0]
    instance.wait_until_running()
    instance.load()

    instance_public_dns = instance.public_dns_name

    f = open(variables.instance_id_file, 'w')
    f.write(instance.id)
    f.close()

    print("\t\t\t* Instance [" + instance.id + "] started")
    print("\t\t\t* Tagging instance")
    ec2_client.create_tags(Resources=[instance.id], Tags=variables.instance_tags)

    # print("\t\t\t* Waiting for instance")
    # time.sleep(10)
    print("\t\t\t* Create EBS Volume and attach to instance [" + instance.id + "]")
    volume = ec2_module.create_volume(ec2_module.get_instance_availability_zone(instance.id))
    f = open(variables.volume_id_file, 'w')
    f.write(volume.id)
    f.close()

    # Wait for volume to be created
    while ec2_module.get_volume_state(volume.id) != 'available':
        print("\t\t\t\t- Volume [" + volume.id + "] is " + ec2_module.get_volume_state(volume.id))
        time.sleep(3)
    print("\t\t\t\t- Volume [" + volume.id + "] is " + ec2_module.get_volume_state(volume.id))

    # Attach volume to instance
    ec2_module.attach_volume(instance.id, volume.id, variables.device_name_ebs)

    generate.install_wordpress_script()
    generate.apache_virtual_host(instance_public_dns)
    generate.wp_config_php()

    v_my_files = [variables.mount_ebs_script + ' ' + variables.mount_ebs_script_name + ' mount',
                  variables.install_lamp_script + ' ' + variables.install_lamp_script_name + ' lamp',
                  variables.wordpress_file + ' ' + variables.wordpress_file_name + ' wordpress-binaries',
                  variables.sql_file + ' ' + variables.sql_file_name + ' sql',
                  variables.wordpress_script + ' ' + variables.wordpress_script_name + ' wordpress',
                  variables.wp_config + ' ' + variables.wp_config_name + ' wp-config',
                  variables.apache_virtual_host + ' ' + variables.apache_virtual_host_name + ' apache']

    for v_my_file in v_my_files:
        ssh.scp_put(instance_public_dns, variables.ssh_user, variables.key_pair_pem, v_my_file.split()[0])
        if v_my_file.split()[2] == 'mount':
            print("\t\t\t* Mounting volumes")
        elif v_my_file.split()[2] == 'lamp':
            print("\t\t\t* Installing LAMP (this will take a few minutes)")
        elif v_my_file.split()[2] == 'wordpress':
            print("\t\t\t* Installing WordPress")
        if v_my_file.split()[2] == 'wp-config':
            ssh.send_command(instance_public_dns, variables.ssh_user, variables.key_pair_pem,
                             "sudo mv ~/" + variables.wp_config_name + " /eph/website/ &> /dev/null")
        if v_my_file.split()[2] == 'apache':
            ssh.send_command(instance_public_dns, variables.ssh_user, variables.key_pair_pem,
                             "sudo mv ~/" + variables.apache_virtual_host_name + " /etc/apache2/sites-available/")
            ssh.send_command(instance_public_dns, variables.ssh_user, variables.key_pair_pem,
                             "sudo a2ensite wordpress.conf &> /dev/null")
            ssh.send_command(instance_public_dns, variables.ssh_user, variables.key_pair_pem,
                             "sudo service apache2 reload &> /dev/null")
        if v_my_file.split()[2] == 'mount' \
                or v_my_file.split()[2] == 'lamp' \
                or v_my_file.split()[2] == 'wordpress':
            ssh.send_command(instance_public_dns, variables.ssh_user, variables.key_pair_pem,
                             "sudo chmod +x ~/" + v_my_file.split()[1])
            ssh.send_command(instance_public_dns, variables.ssh_user, variables.key_pair_pem,
                             "sudo ~/" + v_my_file.split()[1])

    # # Place volume mount script in instance and execute
    # ssh.scp_put(instance_public_dns, variables.ssh_user, variables.key_pair_pem, variables.mount_ebs_script)
    # ssh.send_command(instance_public_dns, variables.ssh_user, variables.key_pair_pem,
    #                  "sudo chmod +x ~/" + variables.mount_ebs_script_name)
    # ssh.send_command(instance_public_dns, variables.ssh_user, variables.key_pair_pem,
    #                  "sudo ~/" + variables.mount_ebs_script_name + " &> /dev/null")
    #
    # # Place LAMP install script in instance and execute
    # print("\t\t\t* Installing LAMP (this will take a few minutes)")
    # ssh.scp_put(instance_public_dns, variables.ssh_user, variables.key_pair_pem, variables.install_lamp_script)
    # ssh.send_command(instance_public_dns, variables.ssh_user, variables.key_pair_pem,
    #                  "sudo chmod +x ~/" + variables.install_lamp_script_name)
    # ssh.send_command(instance_public_dns, variables.ssh_user, variables.key_pair_pem,
    #                  "sudo ~/" + variables.install_lamp_script_name)
    #
    # # Place WordPress install script in instance and execute
    # print("\t\t\t* Installing WordPress")
    #     ssh.scp_put(instance_public_dns, variables.ssh_user, variables.key_pair_pem, variables.wordpress_file)
    # ssh.scp_put(instance_public_dns, variables.ssh_user, variables.key_pair_pem, variables.wordpress_script)
    # ssh.send_command(instance_public_dns, variables.ssh_user, variables.key_pair_pem,
    #                  "sudo chmod +x ~/" + variables.wordpress_script_name)
    # ssh.send_command(instance_public_dns, variables.ssh_user, variables.key_pair_pem,
    #                  "sudo ~/" + variables.wordpress_script_name)

    print("\n\tYou can now access via\n")
    print("HTTP: http://" + instance_public_dns)
    print("SSH: ssh -i ~/.ssh/" + variables.key_pair + ".pem" + " ubuntu@" + instance_public_dns + "\n")
