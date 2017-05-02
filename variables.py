#!/usr/bin/python
import os
import boto3
from modules import index

# Global
index = index.get_hex()
ec2 = boto3.resource('ec2')
ec2_client = boto3.client('ec2')
project = "linux-and-wordpress"
source_dir = os.path.dirname(os.path.abspath(__file__))
index_file = source_dir + "/cache/" + "index.txt"

# EC2
instance_type = "m1.small"
security_group = project + "-security-group-" + index
security_group_desc = "My " + project + " Security Group"
security_group_ingress_ports = [22, 80, 443]
instance_id_file = source_dir + "/cache/" + project + "-instanceID.txt"
instance_tag_name = project + "-instance-" + index
ami_id = "ami-3e32f05e"

# Storage
device_name_ephemeral = "/dev/sde"
device_name_ebs = "/dev/sdg"
volume_id_file = source_dir + "/cache/" + project + "-volumeID.txt"
mount_ebs_script_name = "create_part.sh"
mount_ebs_script = source_dir + "/files/" + mount_ebs_script_name

# Apache Install
apache_virtual_host_name = "wordpress.conf"
apache_virtual_host = source_dir + "/cache/" + apache_virtual_host_name
wp_config_name = "wp-config.php"
wp_config = source_dir + "/cache/" + wp_config_name
wordpress_file_name = "wordpress-4.6.1.zip"
wordpress_file = source_dir + "/files/" + wordpress_file_name
wordpress_script_name = "install_wordpress.py"
wordpress_script = source_dir + "/cache/" + wordpress_script_name
install_lamp_script_name = "install_lamp.sh"
install_lamp_script = source_dir + "/files/" + install_lamp_script_name
ssh_user = "ubuntu"
install_apache = [
    "sudo apt-get upgrade -y"
    "sudo apt-get install apache2 -y"
]

# MySQL
mysql_user = os.environ['USER']
mysql_password = os.environ['USER']
sql_file_name = "website.sql"
sql_file = source_dir + "/files/" + sql_file_name

# Key Pair
key_pair = project + "-key-pair-" + index
key_pair_pem = os.environ['HOME'] + "/.ssh/" + key_pair + ".pem"

# Tags
instance_tags = [{
    "Key": "Name",
    "Value": instance_tag_name
}]

# User Data
user_data = """
#!/bin/bash
sudo apt-get update
"""
