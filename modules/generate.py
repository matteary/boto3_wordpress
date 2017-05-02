#!/usr/bin/python
import variables
import os


def install_wordpress_script():
    f = open(variables.wordpress_script, 'w')
    f.write("#!/usr/bin/python\n")
    f.write("import MySQLdb as db\n")
    f.write("import os\n")
    f.write("import shutil\n")
    f.write("import pwd, grp\n")
    f.write("import zipfile\n\n")
    f.write("shutil.move(\"/home/ubuntu/" + variables.sql_file_name + "\", \"/eph/db/" + variables.sql_file_name + "\")\n")
    f.write("os.system(\"mysql -u root -ppassword < /eph/db/website.sql\")\n\n")
    f.write("database = db.connect(user=\"root\", passwd=\"password\")\n")
    f.write("db_cursor = database.cursor()\n")
    f.write("# db_cursor.execute(\"CREATE DATABASE website\")\n")
    f.write("db_cursor.execute(\"CREATE USER \'" + variables.mysql_user + "\'@\'localhost\' IDENTIFIED BY \'" + variables.mysql_password + "'\")\n")
    f.write("db_cursor.execute(\"GRANT ALL PRIVILEGES ON website.* TO \'" + variables.mysql_user + "\'@\'localhost\'\")\n\n")
    f.write("zip_ref = zipfile.ZipFile(\"/home/ubuntu/" + variables.wordpress_file_name + "\", 'r')\n")
    f.write("zip_ref.extractall(\"/eph\")\n")
    f.write("zip_ref.close()\n\n")
    f.write("os.rename(\"/eph/wordpress\", \"/eph/website\")\n")
    f.write("uid = pwd.getpwnam(\"www-data\").pw_uid\n")
    f.write("gid = grp.getgrnam(\"www-data\").gr_gid\n")
    f.write("os.chown(\"/eph/website\", uid, gid)\n")
    f.close()


def apache_virtual_host(public_dns_name):
    f = open(variables.apache_virtual_host, 'w')
    f.write("<VirtualHost *:80>\n")
    f.write("\tServerName " + public_dns_name + "\n")
    f.write("\tServerAdmin " + variables.mysql_user + "@localhost\n")
    f.write("\tDocumentRoot \"/eph/website\"\n")
    f.write("\tErrorLog ${APACHE_LOG_DIR}/wordpress_error.log\n")
    f.write("\tCustomLog ${APACHE_LOG_DIR}/wordpress_access.log combined\n\n")
    f.write("\t<Directory \"/eph/website\">\n")
    f.write("\t\tOptions Indexes Multiviews FollowSymLinks\n")
    f.write("\t\tAllowOverride All\n")
    f.write("\t\tOrder allow,deny\n")
    f.write("\t\tAllow from all\n")
    f.write("\t\tRequire all granted\n")
    f.write("\t</Directory>\n")
    f.write("</VirtualHost>")
    f.close()


def wp_config_php():
    f = open(variables.wp_config, 'w')
    f.write("<?php\n")
    f.write("define('DB_NAME', 'website');\n")
    f.write("define('DB_USER', '" + variables.mysql_user + "');\n")
    f.write("define('DB_PASSWORD', '" + variables.mysql_password + "');\n")
    f.write("define('DB_HOST', 'localhost');\n")
    f.write("define('DB_CHARSET', 'utf8');\n")
    f.write("define('DB_COLLATE', '');\n")
    f.write("define('AUTH_KEY',         'put your unique phrase here');\n")
    f.write("define('SECURE_AUTH_KEY',  'put your unique phrase here');\n")
    f.write("define('LOGGED_IN_KEY',    'put your unique phrase here');\n")
    f.write("define('NONCE_KEY',        'put your unique phrase here');\n")
    f.write("define('AUTH_SALT',        'put your unique phrase here');\n")
    f.write("define('SECURE_AUTH_SALT', 'put your unique phrase here');\n")
    f.write("define('LOGGED_IN_SALT',   'put your unique phrase here');\n")
    f.write("define('NONCE_SALT',       'put your unique phrase here');\n")
    f.write("$table_prefix  = 'wp_';\n")
    f.write("define('WP_DEBUG', false);\n")
    f.write("if ( !defined('ABSPATH') )\n")
    f.write("\tdefine('ABSPATH', dirname(__FILE__) . '/');\n")
    f.write("require_once(ABSPATH . 'wp-settings.php');\n")
    f.write("\n")
    f.write("\n")
    f.write("\n")



