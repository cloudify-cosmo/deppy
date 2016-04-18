"""
Used to get find and manage versions available online.

"""

from distutils.version import LooseVersion
import requests
import json
import operator

import subprocess

PYPI_URL = 'https://pypi.python.org/pypi/{0}/json'
INFO_KEY = 'info'
NAME_KEY = 'name'
SUMMARY_KEY = 'summary'
LICENSE_KEY = 'license'
RELEASES_KEY = 'releases'
HOMEPAGE_KEY = 'home_page'
DEPENDENCIES_KEY = 'dependencies'
VERSIONS_KEY = 'versions'
PACKAGE_KEY = 'package'
REQUIRE_KEY = 'require'
NEW_VERS_KEY = 'new_versions_available'
UNKNOWN_LICENSE_STR = 'Unknown'
PIP_INSTALL_CMD = 'pip install {0}==-56468'
PIP_INSTALL_PREFIX = ' (from versions: '
PIP_INSTALL_SUFFIX = ')'
PIP_VERSIONS_SEPARATOR = ', '

OPS = {
    '>': operator.gt,
    '<': operator.lt,
    '>=': operator.ge,
    '<=': operator.le,
    '==': operator.eq,
    '!=': operator.ne
}


def split_required_versions(req):
    """
    return a tuple of required versions and comparison operand

    :param req: the required version and comparison operand as one string
    """

    ops = [op for op in OPS.keys() if req.startswith(op)]
    try:
        op = max(ops, key=len)
    except ValueError:
        return req, ''
    return req[len(op):], op


def compare_loose_versions(ver1, ver2, oper=None):
    """
    compare 2 versions based on their LooseVersion value

    :param ver1: version 1 (self)
    :param ver2: version 2 (other)
    :param oper: operator for comparison. if None return the cmp value
    """

    if not oper:
        return cmp(LooseVersion(ver1), LooseVersion(ver2))
    return OPS[oper](LooseVersion(ver1), LooseVersion(ver2))


def filter_newer_versions(versions, current_version):
    """
    return only the versions newer that the current version

    :param versions: list of versions to filter
    :param current_version: current version
    """

    if current_version == '':
        return versions
    return [version for version in versions if compare_loose_versions(
        version, current_version, '>')]


def get_json_from_pypi(package_name):
    """
    return the json page from pypi for the given package

    :param package_name: package name
    """

    # noinspection PyBroadException
    try:
        requests.packages.urllib3.disable_warnings()
        return json.loads(requests.get(PYPI_URL.format(package_name)).content)
    except:
        return None


def get_versions_from_pypi(package_name):
    """
    return all the versions available on pypi for a given package

    :param package_name: package name
    """

    res = get_json_from_pypi(package_name)
    if res is None:
        return package_name, [], UNKNOWN_LICENSE_STR

    if RELEASES_KEY not in res:
        releases = []
    else:
        releases = [str(ver) for ver in res[RELEASES_KEY].keys()]

    if INFO_KEY in res and LICENSE_KEY in res[INFO_KEY]:
        package_license = res[INFO_KEY][LICENSE_KEY]
    else:
        package_license = UNKNOWN_LICENSE_STR
    return package_name, releases, package_license


def get_versions_from_pip(package_name):
    """
    return all versions available by pip for a given package

    :param package_name: package name
    """

    # noinspection PyBroadException
    try:
        p = subprocess.Popen(PIP_INSTALL_CMD.format(package_name),
                             shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, close_fds=True)
        res = p.communicate()[0]
    except:
        return package_name, [], UNKNOWN_LICENSE_STR
    start = res.find(PIP_INSTALL_PREFIX) + len(PIP_INSTALL_PREFIX)
    end = res.find(PIP_INSTALL_SUFFIX, start)
    if start == end:
        return package_name, [], UNKNOWN_LICENSE_STR
    res = res[start:end]
    res = res.split(PIP_VERSIONS_SEPARATOR)
    return package_name, res, UNKNOWN_LICENSE_STR


def get_new_versions_available(my_vers, all_vers):
    """
    return list of tuples of package name, current version and a list of
    newer versions available

    does not include tuples with no newer versions available

    :param my_vers: a dictionary mapping package name to list of versions in
    current project
    :param all_vers: a dictionary mapping package name to list of versions
    available on pypi
    """

    res = []
    for my_dep in my_vers:
        if my_dep in all_vers:
            for curr_ver in my_vers[my_dep]:
                res.append({
                    PACKAGE_KEY: my_dep,
                    REQUIRE_KEY: curr_ver,
                    NEW_VERS_KEY: filter_newer_versions(
                        all_vers[my_dep], split_required_versions(curr_ver)[0])
                })
    return res
