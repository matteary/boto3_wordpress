#!/usr/bin/python
import os
import variables


def create_key_pair_pem(text):
    f = open(variables.key_pair_pem, 'w')
    f.write(text)
    f.close()
    os.chmod(variables.key_pair_pem, 0o400)
