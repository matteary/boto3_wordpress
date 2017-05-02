#!/bin/bash
# Select /device
while read -r line; do
    if [ `echo ${line} | awk '{print $4}'` == '1G' ]; then
        v_device_name="$(echo ${line} | awk '{print $1}')"
        v_target_dev="/dev/${v_device_name}"
    fi
done < <(lsblk | sed -n '1!p')

mkdir /ebs &> /dev/null

# to create the partitions programatically (rather than manually)
# we're going to simulate the manual input to fdisk
# The sed script strips off all the comments so that we can
# document what we're doing in-line with the actual commands
# Note that a blank line (commented as "defualt" will send a empty
# line terminated with a newline to take the fdisk default.
sed -e 's/\s*\([\+0-9a-zA-Z]*\).*/\1/' << EOF | fdisk ${v_target_dev} &> /dev/null
  o # clear the in memory partition table
  n # new partition
  p # primary partition
  1 # partition number 1
    # default - start at beginning of disk
    # default - end at ending of disk
  p # print the in-memory partition table
  w # write the partition table
  q # and we're done
EOF

sleep 3

mkfs.ext4 ${v_target_dev}1 &> /dev/null

echo -e "${v_target_dev}1\t/ebs\text4\tdefaults\t0 0" >> /etc/fstab

sleep 3

# fix ephemeral mapping
mkdir /eph &> /dev/null
sed -i "s|$(grep \"/dev/xvde\" /etc/fstab)||g" /etc/fstab
echo -e "/dev/xvde\t/eph\tauto\tdefaults,nobootwait,comment=cloudconfig\t0 2" >> /etc/fstab

mount -a &> /dev/null
