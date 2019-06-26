#!/usr/bin/env python
from __future__ import print_function

"""
download albums
"""

import re
import os
import sys
import argparse
import requests
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

    try:
        login_url = config.get('clickdownloader', 'loginurl').strip('"').strip()
    except:
        sys.exit("ERROR: loginurl is mandatory")

    try:
        username = config.get('clickdownloader', 'username').strip('"').strip()
    except:
        sys.exit("ERROR: username is mandatory")

    try:
        password = config.get('clickdownloader', 'password').strip('"').strip()
    except:
        sys.exit("ERROR: password is mandatory")

    try:
        index_url = config.get('clickdownloader', 'indexurl').strip('"').strip()
    except:
        sys.exit("ERROR: indexurl is mandatory")

    try:
        debug = config.getboolean('clickdownloader', 'debug')
    except:
        debug = False

    data_login = {
                    'username': username,
                    'password': password
    }

    session = requests.Session()
    login_url_response = session.post(base_url+login_url, data=data_login)

    if debug:
        print("login_url response code: " + str(login_url_response.status_code))
        # print("login_url response text: " + str(login_url_response.text))

    numero_pagina=1
    llistat_albums=[]
    anterior_numero_albums=9999

    # obtindre llistat tots els albums
    while(anterior_numero_albums!=len(llistat_albums)):

        anterior_numero_albums = len(llistat_albums)

        # ?accio=llistar&pag=2&lloc=fotos
        index_url_response = session.get(base_url+index_url+'?accio=llistar&pag='+str(numero_pagina)+'&lloc=fotos')

        if debug:
            print("URL: "+base_url+index_url+'?accio=llistar&pag='+str(numero_pagina)+'&lloc=fotos')
            print("index_url response code: " + str(index_url_response.status_code))
            # print("index_url response text: " + str(index_url_response.text))

        pattern_url_albums = re.compile(r'<a href="([^>]*albums_fotos.php[^>]*veure[^>]*)">')

        current_list_albums = []
        for album_url in re.findall(pattern_url_albums, str(index_url_response.text)):
            if debug:
                current_list_albums.append(album_url)

        llistat_albums = llistat_albums + list(set(current_list_albums) - set(llistat_albums))
        numero_pagina=numero_pagina+1
