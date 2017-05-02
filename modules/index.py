#!/usr/bin/python
import random


def get_hex():
    return ''.join([random.choice('0123456789ABCDEF') for x in range(8)])
