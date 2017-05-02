#!/bin/bash

# Get MySQL Server version
for i in $(aptitude search mysql-server | awk '{print $2}'); do
    if [ "${i}" == 'mysql-server-5.5' ]; then
        v_mysql_version="5.5"
    elif [ "$( echo ${v_mysql_version})" != '5.5' ] && [ "${i}" == 'mysql-server-5.6' ]; then
        v_mysql_version="5.6"
    fi
done
echo -e "\t\t\t\t- apt-get update"
apt-get update &> /dev/null
sleep 1
echo -e "\t\t\t\t- Installing updates"
apt-get upgrade -y &> /dev/null
echo -e "\t\t\t\t- Installing Apache"
apt-get install apache2 -y &> /dev/null

sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password password password'
sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password password'
echo -e "\t\t\t\t- Installing MySQL"
apt-get install mysql-server-${v_mysql_version} -y &> /dev/null
echo -e "\t\t\t\t- Installing PHP"
apt-get install php5 libapache2-mod-php5 php5-mysqlnd-ms -y &> /dev/null
sudo service apache2 reload &> /dev/null

mkdir /eph/db

# install unzip to get ready for wordpress unzip
apt-get install unzip -y &> /dev/null

# install python tools
apt-get install python-pip python-mysqldb -y &> /dev/null