#!/usr/bin/python
import MySQLdb as db
import os
import shutil
import pwd, grp
import zipfile

shutil.move("/home/ubuntu/website.sql", "/eph/db/website.sql")
os.system("mysql -u root -ppassword < /eph/db/website.sql")

database = db.connect(user="root", passwd="password")
db_cursor = database.cursor()
# db_cursor.execute("CREATE DATABASE website")
db_cursor.execute("CREATE USER 'matteary'@'localhost' IDENTIFIED BY 'matteary'")
db_cursor.execute("GRANT ALL PRIVILEGES ON website.* TO 'matteary'@'localhost'")

zip_ref = zipfile.ZipFile("/home/ubuntu/wordpress-4.6.1.zip", 'r')
zip_ref.extractall("/eph")
zip_ref.close()

os.rename("/eph/wordpress", "/eph/website")
uid = pwd.getpwnam("www-data").pw_uid
gid = grp.getgrnam("www-data").gr_gid
os.chown("/eph/website", uid, gid)
