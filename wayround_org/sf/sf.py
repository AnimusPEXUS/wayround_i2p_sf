#!/usr/bin/python3

import lxml.html
import urllib.request
import logging

import wayround_org.utils.path

SF_ADDRESS = 'https://sourceforge.net'


def listdir(project, path='/', proxy=None):
    """
    proxy - dict(host= - ip or domain and port, type= - http or https)
    result: two lists, first - directories, second - files
        (None, None) tuple means error
    """

    ret = None, None

    while path.startswith('/'):
        path = path[1:]

    while path.endswith('/'):
        path = path[:-1]

    if not path.startswith('/'):
        path = '/' + path

    if not path.endswith('/'):
        path = path + '/'

    sf_req_url = '{}/projects/{}/files{}'.format(
        SF_ADDRESS,
        project,
        path
        )
    req = urllib.request.Request(sf_req_url)

    if proxy is not None:
        req.set_proxy(proxy['host'], proxy['type'])

    page_parsed = None
    try:
        rl_f = urllib.request.urlopen(req)
        sf_page_text = rl_f.read()
        rl_f.close()
        page_parsed = lxml.html.document_fromstring(sf_page_text)
    except OSError:
        page_parsed = None

    if page_parsed is not None:
        file_list_table = page_parsed.find('.//table[@id="files_list"]')

        if file_list_table is None:
            pass
        else:

            file_list_table_tbody = file_list_table.find('tbody')

            folder_trs = file_list_table_tbody.findall('tr')

            folders = []
            files = {}

            for i in folder_trs:

                cls = i.get('class', '')

                if 'folder' in cls:
                    folders.append(
                        urllib.request.unquote(
                            i.get('title', '(error-title)')
                            )
                        )

                elif 'file' in cls:
                    a = i.find('.//a[@class="name"]')
                    if a is not None:
                        files[
                            urllib.request.unquote(
                                i.get('title', '(error-title)')
                            )
                            ] = a.get('href', None)

            ret = folders, files

    return ret


def walk(project, path='/', proxy=None):

    folders, files = listdir(project, path=path, proxy=proxy)

    if folders is None and files is None:
        raise Exception("sf.net listdir() func returned error")

    yield path, folders, files

    for i in folders:
        jo = wayround_org.utils.path.join(path, i)
        for j in walk(project, jo):
            yield j

    return


def tree(project, proxy=None):
    """
    result: dict, where keys ar full pathnames relatively to project root dir (
        but each line is started with slash!
        )
    """

    all_files = {}

    for path, dirs, files in walk(project, proxy=proxy):
        for i in files:
            all_files[wayround_org.utils.path.join(path, i)] = files[i]

    return all_files
