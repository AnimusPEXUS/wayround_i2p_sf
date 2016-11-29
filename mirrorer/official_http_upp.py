#!/usr/bin/python3


import sys
import os.path
import glob
import subprocess
import random
import logging
logging.basicConfig(level='DEBUG')

import wayround_i2p.sf.sf
import wayround_i2p.utils.path
import wayround_i2p.utils.file
import wayround_i2p.utils.list


PWD = wayround_i2p.utils.path.abspath(os.path.dirname(__file__))
log_dir = wayround_i2p.utils.path.join(PWD, 'log')
list_dir = wayround_i2p.utils.path.join(PWD, 'list')
index_dir = wayround_i2p.utils.path.join(PWD, 'index')
out_dir_root = wayround_i2p.utils.path.join(PWD, 'out')
cdoi_f = 'current_download_order_is.txt'

use_proxy = False

proxy = {
    'host': '190.198.167.202',
    'port': 3128
    }

debug = False


# create log and index dir
for i in [log_dir, index_dir]:
    try:
        os.makedirs(i)
    except:
        pass

    if not os.path.isdir(i):
        print("error: can't create dir: {}".format(i))
        exit(1)

# determine which projects to update
inst_file_list = []

if len(sys.argv) > 1:
    inst_file_list = sys.argv[1:]
else:
    inst_file_list = glob.glob(wayround_i2p.utils.path.join(list_dir, '*.txt'))

# working through TOR is not fast, randomize list
random.shuffle(inst_file_list)

# download order will be saved to file
try:
    os.unlink(cdoi_f)
except:
    pass

# start processing
for i in inst_file_list:

    # we use file name without .txt as project name
    p_name = os.path.basename(i)[:-4]

    # log currently processed project in to file
    with open(cdoi_f, 'a') as f:
        f.write(
            '{} ({} of {})\n'.format(
                i,
                inst_file_list.index(i) +
                1,
                len(inst_file_list)))

    # here list of previously saved files is saved. index. to not try to save
    # previously already saved files
    index = []

    index_fn = wayround_i2p.utils.path.join(index_dir, p_name)

    # try to load index
    if os.path.isfile(index_fn):
        with open(index_fn) as f:
            index = f.read().splitlines()

    if debug:
        logging.debug("index: {}".format(index))

    # remove empty lines from index
    while '' in index:
        index.remove('')

    # determine file for logging process
    log_file = wayround_i2p.utils.path.join(log_dir, '{}.log'.format(p_name))
    log_file_old = '{}.old'.format(log_file)

    # unlink older one log
    if os.path.isfile(log_file_old):
        os.unlink(log_file_old)

    # rename existing log to old log
    if os.path.isfile(log_file):
        os.rename(log_file, log_file_old)

    # create log file
    with open(log_file, 'w'):
        pass

    # build file directory tree of project hosted on SF.net
    try:
        sf_project_tree = wayround_i2p.sf.sf.tree(p_name)
    except:
        with open(log_file, 'a') as f:
            f.write("error tree for project {}\n".format(p_name))
        continue

    if debug:
        logging.debug("sf tree: {}".format(sf_project_tree))

    # remove leading slash from sf_project_tree keys
    for j in list(sf_project_tree.keys()):
        sf_project_tree[j[1:]] = sf_project_tree[j]
        del(sf_project_tree[j])

    # read filter
    with open(i) as f:
        filter_text = f.read()

    # calculate output dir
    out_dir = wayround_i2p.utils.path.join(
        out_dir_root,
        p_name[0],
        p_name[:2],
        p_name
        )

    # try to create output dir
    try:
        os.makedirs(out_dir, exist_ok=True)
    except:
        pass

    # error if eventually output dir not exists
    if not os.path.isdir(out_dir):
        print("error: can't create dir: {}".format(out_dir))
        continue

    # remove nonexisting files from index
    for j in index[:]:
        if not os.path.isfile(wayround_i2p.utils.path.join(out_dir, j)):
            index.remove(j)

    if debug:
        logging.debug(
            "index after removing non-existsing files: {}".format(index)
            )

    # list already saved files
    files_on_disk = wayround_i2p.utils.file.files_recurcive_list(
        out_dir,
        relative_to=out_dir
        )

    if debug:
        logging.debug("files on disk: {}".format(files_on_disk))

    # filter existing files
    files_on_disk_filtered = wayround_i2p.utils.list.filter_list(
        files_on_disk,
        filter_text
        )

    if debug:
        logging.debug(
            "files on disk filtered: {}".format(files_on_disk_filtered)
            )

    # triangulate files which was filtered and need to be removed from FS
    files_on_disk_to_del = []
    for j in files_on_disk:
        if not j in files_on_disk_filtered:
            files_on_disk_to_del.append(j)

    if debug:
        logging.debug(
            "files_on_disk_to_del: {}".format(files_on_disk_to_del)
            )

    sf_project_tree_not_filtered = list(sf_project_tree.keys())
    # filter file tree loaded from SF.net with the same filter
    # sf_project_tree_filtered - passed filter and ok to be downloaded
    sf_project_tree_filtered = wayround_i2p.utils.list.filter_list(
        sf_project_tree_not_filtered,
        filter_text
        )

    if debug:
        logging.debug(
            "sf_project_tree_not_filtered: {}".format(
                sf_project_tree_not_filtered
                )
            )
        logging.debug(
            "sf_project_tree_filtered: {}".format(
                sf_project_tree_filtered
                )
            )

    # remember more files which need to be deleted
    for j in sf_project_tree_not_filtered:
        if debug:
            logging.debug(
                "is j('{}') in sf_project_tree_filtered".format(
                    j
                    )
                )
        if not j in sf_project_tree_filtered:
            files_on_disk_to_del.append(j)

    if debug:
        logging.debug(
            "files_on_disk_to_del 2: {}".format(files_on_disk_to_del)
            )

    # make some fun with delete file list
    files_on_disk_to_del = sorted(list(set(files_on_disk_to_del)))

    # finally, remove all files listed on deletion
    with open(log_file, 'a') as f:
        for j in files_on_disk_to_del:
            dst_file = wayround_i2p.utils.path.join(out_dir, j)
            if os.path.exists(dst_file):
                f.write("removing {}\n".format(j))
                wayround_i2p.utils.file.remove_if_exists(dst_file)

            while j in index:
                index.remove(j)

    # rewrite index on file system with new state
    with open(index_fn, 'w') as f:
        f.write('{}\n'.format('\n'.join(sorted(list(set(index))))))

    if debug:
        logging.debug("index state: {}".format(index))

    # download all files which bypassed filter
    for j in sorted(sf_project_tree_filtered):

        dst_file = wayround_i2p.utils.path.join(out_dir, j)
        dst_dir = os.path.dirname(dst_file)

        try:
            os.makedirs(dst_dir, exist_ok=True)
        except:
            pass

        if not os.path.isdir(dst_dir):
            print("error: can't create dir: {}".format(dst_dir))
            continue

        url = sf_project_tree[j]
        if not j in index:
            cmdl = [
                'wget',
                '--no-check-certificate',
                '-e', 'robots=off',
                '--max-redirect=100',
                '-a', log_file,
                '-c',
                '-O', dst_file,
                url]

            if debug:
                logging.debug("executing: {}".format(cmdl))

            p = subprocess.Popen(cmdl)
            res = p.wait()
            if res != 0:
                with open(log_file, 'a') as f:
                    f.write(
                        "error: can't download (some wget error): {}\n".format(
                            url
                            )
                        )
            else:
                index.append(j)
                with open(index_fn, 'a') as f:
                    f.write('{}\n'.format(j))

        else:
            with open(log_file, 'a') as f:
                f.write("already: {}\n".format(j))

    if os.path.isfile(index_fn):
        with open(index_fn) as f:
            index = f.read().splitlines()

    while '' in index:
        index.remove('')

    with open(index_fn, 'w') as f:
        f.write('{}\n'.format('\n'.join(sorted(list(set(index))))))

    with open(log_file, 'a') as f:
        f.write("======= UPP DONE HERE ======= \n")


exit(0)
