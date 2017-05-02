import boto3
# import variables
ec2 = boto3.resource('ec2')
client = boto3.client('ec2')


def attach_volume(instance_id, volume_id, device):
    response = client.attach_volume(
        InstanceId=instance_id,
        VolumeId=volume_id,
        Device=device
        )
    return response


def get_instance_name(instance_id):
    instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    for instance in instances:
        for tag in instance.tags:
            if instance.id == instance_id:
                if tag['Key'] == 'Name':
                    return tag['Value']
                else:
                    return 0


def create_instance(ami_id, instance_type, key_pair, security_group_id):
    instance = ec2.create_instances(
        ImageId=ami_id,
        MinCount=1,
        MaxCount=1,
        InstanceType=instance_type,
        KeyName=key_pair,
        SecurityGroupIds=[security_group_id]
        )
    return instance


def create_instance_with_ephemeral(ami_id, instance_type, key_pair, security_group_id, dev_name):
    instance = ec2.create_instances(
        ImageId=ami_id,
        MinCount=1,
        MaxCount=1,
        InstanceType=instance_type,
        BlockDeviceMappings=[{
            "DeviceName": dev_name,
            "VirtualName": "ephemeral0"
            }],
        KeyName=key_pair,
        SecurityGroupIds=[security_group_id]
        )
    return instance


def create_security_group(name, description):
    security_group = ec2.create_security_group(
        GroupName=name,
        Description=description
        )
    return security_group


def create_key_pair(key_name):
    response = client.create_key_pair(KeyName=key_name)
    return response


def get_instance_subnet_id(instance_id):
    response = client.describe_instances(InstanceIds=[instance_id])
    return response['Reservations'][0]['Instances'][0]['SubnetId']


def get_instance_availability_zone(instance_id):
    response = client.describe_instances(InstanceIds=[instance_id])
    return response['Reservations'][0]['Instances'][0]['Placement']['AvailabilityZone']


def create_volume(availability_zone):
    response = ec2.create_volume(
        Size=1,
        VolumeType="standard",
        AvailabilityZone=availability_zone
        )
    return response


def get_volume_state(volume_id):
    volume = ec2.Volume(volume_id)
    volume.reload()
    return volume.state
