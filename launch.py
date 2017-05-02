#!/usr/bin/python
# The following packages are required for this tool to work:
#  * boto3    (AWS Tools)
#  * Fabric   (SSH Client)
from __future__ import print_function
import sys
import getopt
import os
import variables
from modules import help, deploy, cleanup, test

if len(sys.argv) == 1:
    print(help.help_msg())
    sys.exit(2)
elif len(sys.argv) >= 3:
    print(help.help_msg())
    sys.exit(2)


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hdcte", ["help", "deploy", "cleanup", "test", "erase-test"])
    except getopt.GetoptError:
        help.help_msg()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            help.help_msg()
            sys.exit()
        elif opt in ("-d", "--deploy"):
            deploy.environment()
        elif opt in ("-c", "--cleanup"):
            cleanup.environment()
        elif opt in ("-t", "--test"):
            test.environment()
        elif opt in ("-e", "--erase-test"):
            test.erase()

if __name__ == "__main__":
    main(sys.argv[1:])
