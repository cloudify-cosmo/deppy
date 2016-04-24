"""Used to get the dependencies of a specific module/project/package.

"""

import os
import sys
import imp
import json
import shutil
import tempfile
import cStringIO
import setuptools
import subprocess

import requests

from . import consts
from . import versions


def get_from_file(path):
    """Get list of dependencies and package name, for a given setup.py file

    if the name is unknown, return the path instead

    handles only single-operator requires, not >=3, <=4

    :param path: the setup.py file path
    """
    setup_kwargs = _get_setup_kwargs(path)

    # parse requirements to list of tuples of package name and package version
    dependencies_list = setup_kwargs.get(consts.INSTALL_REQUIRES_ARG, [])
    dependencies = []
    for dependency in dependencies_list:
        for oper in versions.OPERATORS:
            index = dependency.find(oper)
            if index >= 0:
                package_name = dependency[:index]
                version, require_operator = \
                    versions.split_require(dependency[index:])
                dependencies.append((package_name, version, require_operator))
                break
        else:
            dependencies.append((dependency, '', ''))

    # return the dependencies list and the path of the original setup.py file
    return dependencies, \
        setup_kwargs.get(consts.NAME_ARG, path), \
        setup_kwargs.get(consts.LICENSE_KEY, consts.UNKNOWN)


def get_by_url(url, req_url=None):
    """Get list of dependencies and package name, for a given setup.py file url

    if the name is unknown, return the url instead

    :param url: the setup.py file url
    :param req_url: the requirements.txt file url
    """

    tmp_dir = ''
    try:
        tmp_dir = tempfile.mkdtemp(
            prefix=os.path.basename(os.path.dirname(__file__)),
            suffix=str(os.getpid())
        )
        setup_path = os.path.join(tmp_dir, consts.SETUP_FILE_NAME)
        requests.packages.urllib3.disable_warnings()
        setup_str = requests.get(url).content
        with open(setup_path, mode='w') as tmp_setup:
            tmp_setup.write(setup_str)
        if req_url:
            req_path = os.path.join(tmp_dir, consts.REQUIREMENTS_FILE_NAME)
            req_str = requests.get(req_url).content
            with open(req_path, mode='w') as tmp_req:
                tmp_req.write(req_str)
        dependencies, package_name, lic = get_from_file(tmp_setup.name)
        if package_name == tmp_setup.name:
            package_name = url
        result = dependencies, package_name, lic
    except Exception:
        result = None
    shutil.rmtree(tmp_dir, ignore_errors=True)
    return result


def get_for_package(package_name, depth=0):
    """Get list of dependencies and package name, for locally installed package

    :param package_name: package name
    :param depth: depth of dependencies tree
    """

    dependencies_tree = build_tree(package_name, depth)
    if dependencies_tree is None:
        return None
    if package_name not in dependencies_tree:
        return None, package_name, consts.UNKNOWN
    dependencies_list = []
    for dependency in dependencies_tree[package_name]:
        version, operator = versions.split_require(
            dependency[consts.REQUIRE_KEY])
        dependencies_list.append((
            dependency[consts.PACKAGE_KEY], version, operator))
    return dependencies_list, package_name, consts.UNKNOWN


def _rec_build_tree(dependencies_tree, dependencies_dict, package_name, depth):
    """Recursively build a dependencies tree/subtree

    :param dependencies_tree: the tree build so-far
    :param dependencies_dict: pipdeptree output
    :param package_name: the package that is the root of this subtree
    :param depth: maximal depth of subtree
    """

    package_name = package_name.lower()
    if package_name in dependencies_tree:
        return dependencies_tree
    for dictionary_item in dependencies_dict:
        try:
            current_package = str(
                dictionary_item[consts.PACKAGE_KEY]
                [consts.KEY_KEY]).lower()
        except KeyError:
            continue
        if current_package == package_name:
            dependencies_list = []
            for dependency in dictionary_item.get(
                    consts.DEPENDENCIES_KEY, []):
                if consts.KEY_KEY in dependency:
                    required_package_name = str(
                        dependency[consts.KEY_KEY]).lower()
                    version = dependency.get(
                        consts.REQUIRED_VERSION_KEY, '')
                    if version is None:
                        version = ''
                    else:
                        version = str(version).lower()
                    dependencies_list.append({
                        consts.PACKAGE_KEY: required_package_name,
                        consts.REQUIRE_KEY: version
                    })
            dependencies_tree[package_name] = dependencies_list
            if depth != 0:
                for dependency in dependencies_list:
                    dependencies_tree = _rec_build_tree(
                        dependencies_tree, dependencies_dict,
                        dependency[consts.PACKAGE_KEY], depth - 1)
    return dependencies_tree


def build_tree(package_name, depth=-1):
    """Return a dictionary representing a dependencies tree with the given
    package as root, based on pipdeptree

    :param package_name: the main package (root of the tree)
    :param depth: maximal depth for the tree (negative is unlimited)
    """

    try:
        dependencies_dict = json.loads(subprocess.Popen(
            consts.PIPDEPTREE_JSON_CMD, shell=True,
            stdout=subprocess.PIPE, close_fds=True).communicate()[0])
    except Exception:
        return None
    return _rec_build_tree(
        {}, dependencies_dict, package_name, depth)


def _get_setup_kwargs(path):
    """Return the requirements list for a given setup.py file

    :param path: the setup.py file path
    :return:
    """

    with setup_tools_mock() as setup:
        imp.load_source(consts.SETUP_MODULE_NAME, path)
    return setup.output


class setup_tools_mock(object):

    def __init__(self):
        self._normal_setup = setuptools.setup
        self.output = {}

    def __enter__(self):
        setuptools.setup = self._mock_setup
        self._mute_std()
        return self

    def __exit__(self, *_):
        self._unmute_std()
        setuptools.setup = self._normal_setup
        return True

    def _mock_setup(self, *_, **kwargs):
        """Put the requirements given as an argument in dic

        :param args:
        :param kwargs:
        :return:
        """
        self.output.update(kwargs)

    def _mute_std(self):
        """Replace stdout and stderr with dummies, to run setup.py silently

        """
        self.old_out = sys.stdout
        sys.stdout = cStringIO.StringIO()
        self.old_err = sys.stderr
        sys.stderr = cStringIO.StringIO()
        self.sys = os.system
        os.system = cStringIO.StringIO()

    def _unmute_std(self):
        """Restore stdout and stderr

        """
        sys.stdout = self.old_out
        sys.stderr = self.old_err
        os.system = self.sys
