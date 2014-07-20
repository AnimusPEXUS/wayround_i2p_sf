#!/usr/bin/python3

import lxml.html

import org.wayround.utils.path

SF_ADDRESS = 'http://sourceforge.net/'


def listdir(project, path='/'):

    ret = None

    while path.startswith('/'):
        path = path[1:]

    while path.endswith('/'):
        path = path[:-1]

    if not path.startswith('/'):
        path = '/' + path

    if not path.endswith('/'):
        path = path + '/'

    page_parsed = lxml.html.parse(
        'http://sourceforge.net/projects/{}/files{}'.format(
            project,
            path
            )
        )

    file_list_table = page_parsed.find('//table[@id="files_list"]')

    if file_list_table is None:
        pass
    else:

        file_list_table_tbody = file_list_table.find('tbody')

        folder_trs = file_list_table_tbody.findall('tr')

        folders = []
        files = {}

        for i in folder_trs:
            if 'folder' in i.get('class', ''):
                folders.append(i.get('title', '(error-title)'))

            elif 'file' in i.get('class', ''):
                a = i.find('.//a[@class="name"]')
                if a is not None:
                    files[
                        i.get('title', '(error-title)')] = a.get('href', None)

        ret = folders, files

    return ret


def walk(project, path='/'):

    folders, files = listdir(project, path=path)

    yield path, folders, files

    for i in folders:
        jo = org.wayround.utils.path.join(path, i)
        for j in walk(project, jo):
            yield j

    return


def tree(project):

    all_files = {}

    for path, dirs, files in walk(project):
        for i in files:
            all_files[org.wayround.utils.path.join(path, i)] = files[i]

    return all_files
