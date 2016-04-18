"""
Used to get the dependencies of a specific module/project/package.

"""

import json
import os
import imp
import tempfile

import requests
import setuptools
import subprocess

import shutil

import vers_getter


MODULE_NAME = 'dep_vers_module'
INSTALL_REQUIRES_ARG = 'install_requires'
NAME_ARG = 'name'
SETUP_MODULE_NAME = 'setup'
REQUIRE_VERSION_PATTERN = "=="
SETUP_TEMP_FILE_NAME = 'temp_setup_file{0}.py'
PACKAGE_KEY = 'package'
REQUIRED_KEY = 'required'
PIPDEPTREE_CMD = 'pipdeptree'
PIPDEPTREE_JSON_CMD = '{0} -j'.format(PIPDEPTREE_CMD)
PIPDEPTREE_PACKAGE_CMD = '{0} -p '.format(PIPDEPTREE_CMD)
PACKAGE_KEY_UNICODE = u'package'
KEY_KEY_UNICODE = u'key'
DEPENDENCIES_KEY_UNICODE = u'dependencies'
REQUIRED_VERSION_KEY_UNICODE = u'required_version'


def get_dependencies_from_file(path):
    """
    get list of dependencies and package name, for a given setup.py file

    if the name is unknown, return the path instead

    :param path: the setup.py file path
    """

    # get the install_requires arg
    # noinspection PyBroadException
    try:
        setup_kwargs = get_setup_kwargs(path)
    except:
        setup_kwargs = {}

    # parse requirements to list of tuples of package name and package version
    dep_list = setup_kwargs.get(INSTALL_REQUIRES_ARG, [])
    dependencies = []
    for dep in dep_list:
        for op in vers_getter.OPS:
            index = dep.find(op)
            if index >= 0:
                pack = dep[:index]
                req_tup = vers_getter.split_required_versions(dep[index:])
                dependencies.append((pack, req_tup[0], req_tup[1]))
                break
        else:
            dependencies.append((dep, '', ''))

    # return the dependencies list and the path of the original setup.py file
    return dependencies, setup_kwargs.get(NAME_ARG, path)


def get_dependencies_by_url(url):
    """
    get list of dependencies and package name, for a setup.py file given by url

    if the name is unknown, return the url instead

    :param url: the setup.py file path
    """

    tmp_dir = ''
    # noinspection PyBroadException
    try:
        tmp_dir = tempfile.mkdtemp(prefix=MODULE_NAME, suffix=str(os.getpid()))
        requests.packages.urllib3.disable_warnings()
        setup_str = requests.get(url).content
        with tempfile.NamedTemporaryFile(dir=tmp_dir) as tmp_file:
            with open(tmp_file.name, mode='w') as tmp_file2:
                tmp_file2.write(setup_str)
            res = get_dependencies_from_file(tmp_file.name)
            if res[1] == tmp_file.name:
                res = res[0], url
    except:
        res = None
    shutil.rmtree(tmp_dir, ignore_errors=True)
    return res


def get_dependencies_for_package(package_name):
    """
    get list of dependencies and package name, for a given package

    :param package_name: package name
    """

    dep_tree = build_dep_tree(package_name, 1)
    if dep_tree is None:
        return None
    if package_name not in dep_tree:
        return None, package_name
    dep_list = []
    for dep in dep_tree[package_name]:
        req = vers_getter.split_required_versions(dep[REQUIRED_KEY])
        dep_list.append((dep[PACKAGE_KEY], req[0], req[1]))
    return dep_list, package_name


def rec_build_dep_tree(dep_tree, dep_json, package_name, rec):
    """
    recursively build a dependencies tree/subtree

    :param dep_tree: the tree build so-far
    :param dep_json: the json representing pipdeptree output
    :param package_name: the package that is the root of this subtree
    :param rec: maximal depth of subtree
    """

    package_name = package_name.lower()
    if rec == 0 or package_name in dep_tree:
        return dep_tree
    for json_item in dep_json:
        try:
            curr_package = \
                str(json_item[PACKAGE_KEY_UNICODE][KEY_KEY_UNICODE]).lower()
        except KeyError:
            continue
        if curr_package == package_name:
            dep_list = []
            try:
                for dep in json_item[DEPENDENCIES_KEY_UNICODE]:
                    try:
                        dep_name = str(dep[KEY_KEY_UNICODE]).lower()
                        dep_ver = dep[REQUIRED_VERSION_KEY_UNICODE]
                        if dep_ver is None:
                            dep_ver = ''
                        else:
                            dep_ver = str(dep_ver).lower()
                        dep_list.append(
                            {PACKAGE_KEY: dep_name, REQUIRED_KEY: dep_ver})
                    except KeyError:
                        continue
            except KeyError:
                pass
            dep_tree[package_name] = dep_list
            for dep in dep_list:
                dep_tree = rec_build_dep_tree(
                    dep_tree, dep_json, dep[PACKAGE_KEY], rec - 1)
    return dep_tree


def build_dep_tree(package_name, rec=-1):
    """
    return a dictionary representing a dependencies tree with the given
    package as root, based on pipdeptree

    :param package_name: the main package (root of the tree)
    :param rec: maximal depth for the tree (negative is unlimited)
    """

    # noinspection PyBroadException
    try:
        p = subprocess.Popen(PIPDEPTREE_JSON_CMD, shell=True,
                             stdout=subprocess.PIPE, close_fds=True)
        dep_json = json.loads(p.communicate()[0])
    except:
        return None
    return rec_build_dep_tree({}, dep_json, package_name, rec)


# a dictionary for all the requirements
req_dic = {}


def mock_setup(*args, **kwargs):
    """
    Put the requirements given as an argument in dic

    :param args:
    :param kwargs:
    :return:
    """

    len(args)
    req_dic[str(os.getpid())] = kwargs


def get_setup_kwargs(path):
    """
    Return the requirements list for a given setup.py file

    :param path: the setup.py file path
    :return:
    """

    with setup_tools_mock():
        imp.load_source(SETUP_MODULE_NAME, path)

    return req_dic[str(os.getpid())]


class setup_tools_mock(object):
    def __init__(self):
        self._normal_setup = setuptools.setup

    def __enter__(self):
        setuptools.setup = mock_setup

    def __exit__(self, exc_type, exc_val, exc_tb):
        setuptools.setup = self._normal_setup
