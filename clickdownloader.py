#!/usr/bin/env python
from __future__ import print_function

"""
download albums
"""

import os
import sys
import argparse
from configparser import SafeConfigParser

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if __name__ == '__main__':

    try:
        config_file = sys.argv[1]
    except IndexError:
        config_file = './clickdownloader.config'

    config = SafeConfigParser()
    config.read(config_file)

    try:
        base_url = config.get('clickdownloader', 'baseurl').strip('"').strip()
    except:
        sys.exit("ERROR: baseurl is mandatory")
