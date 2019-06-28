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

debug = False

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def download_file_by_url(local_filename, url):
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    # f.flush()
    return local_filename

def getAlbum(session, base_url, album_id):
    global debug, base_downloads
    # /students/albums_fotos.php?accio=veure&id=1441
    album_response = session.get(base_url+'/students/albums_fotos.php?accio=veure&id='+album_id)
    if debug:
        eprint("album response code: " + str(album_response.status_code))
        # eprint("album response text: " + str(album_response.text))

    # <div><h2 class="Gran head_news_interior"><strong>...</strong></h2></div>
    pattern_get_nom_album = re.compile(r'<div><h2 class="Gran head_news_interior"><strong>([^<]*)<')
    titol_album = re.findall(pattern_get_nom_album, str(album_response.text))[0]
    # if debug:
    #     eprint("nom album: "+titol_album)

    # <a class="boto_vermell_petit" href="...zip">Descarregar àlbum</a>
    pattern_get_url_download = re.compile(r'<a class="boto_vermell_petit" href="([^"]*)">')
    try:
        album_url_download = base_url+'/students/'+re.findall(pattern_get_url_download, str(album_response.text))[0]
    except:
        album_url_download = ''

    # if debug:
    #     eprint("URL DOWNLOAD: "+album_url_download)

    if debug:
        eprint("nom album: "+titol_album +" URL DOWNLOAD: "+album_url_download)

    # TODO: friendlier name
    filename = album_url_download.split('/')[-1]

    # actual download
    if album_url_download and not os.path.isfile(base_downloads+'/'+filename):
        download_file_by_url(base_downloads+'/'+filename, album_url_download)

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

    try:
        once = config.getboolean('clickdownloader', 'once')
    except:
        once = False

    try:
        base_downloads = config.get('clickdownloader', 'basedownloads')
    except:
        base_downloads = '.'

    data_login = {
                    'username': username,
                    'password': password
    }

    session = requests.Session()
    login_url_response = session.post(base_url+login_url, data=data_login)

    if debug:
        eprint("login_url response code: " + str(login_url_response.status_code))
        # eprint("login_url response text: " + str(login_url_response.text))

    numero_pagina=1
    llistat_albums=[]
    anterior_numero_albums=9999

    # obtindre llistat tots els albums
    while(anterior_numero_albums!=len(llistat_albums)):

        anterior_numero_albums = len(llistat_albums)

        # ?accio=llistar&pag=2&lloc=fotos
        index_url_response = session.get(base_url+index_url+'?accio=llistar&pag='+str(numero_pagina)+'&lloc=fotos')

        if debug:
            eprint("URL: "+base_url+index_url+'?accio=llistar&pag='+str(numero_pagina)+'&lloc=fotos')
            eprint("index_url response code: " + str(index_url_response.status_code))
            # eprint("index_url response text: " + str(index_url_response.text))

        pattern_url_albums = re.compile(r'<a href="([^>]*albums_fotos.php[^>]*veure[^>]*)">')

        current_list_albums = []
        for album_url in re.findall(pattern_url_albums, str(index_url_response.text)):
            if debug:
                current_list_albums.append(album_url)

        llistat_albums = llistat_albums + list(set(current_list_albums) - set(llistat_albums))
        numero_pagina=numero_pagina+1

        if once:
            break

    # albums_fotos.php?accio=veure&id=1434
    pattern_get_id_albums = re.compile(r'id=([0-9]*)')

    for album_url in llistat_albums:
        album_id = re.findall(pattern_get_id_albums, album_url)[0]
        getAlbum(session, base_url, album_id)

        # keepalive
        index_url_response = session.get(base_url+index_url+'?accio=llistar&pag=1&lloc=fotos')
