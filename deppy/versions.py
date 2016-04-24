"""Used to get find and manage versions available online.

"""

import json
import operator

import requests

from distutils.version import LooseVersion

from . import consts


OPERATORS = {
    '>': operator.gt,
    '<': operator.lt,
    '>=': operator.ge,
    '<=': operator.le,
    '==': operator.eq,
    '!=': operator.ne,
}


def split_require(require):
    """Return a tuple of required versions and comparison operand

    :param require: the required version and comparison operand as one string
    """

    ops = [op for op in OPERATORS if require.startswith(op)] + ['']
    op = max(ops, key=len)
    return require[len(op):], op


def compare(version1, version2, oper=None):
    """Compare 2 versions based on their LooseVersion value

    :param version1: version 1 (self)
    :param version2: version 2 (other)
    :param oper: operator for comparison. if None return the cmp value
    """

    if not oper:
        return cmp(LooseVersion(version1), LooseVersion(version2))
    return OPERATORS[oper](LooseVersion(version1), LooseVersion(version2))


def _filter_newer(versions, current_version):
    """Return only the versions newer than the current version

    :param versions: list of versions to filter
    :param current_version: current version
    """

    if current_version == '':
        return versions
    return [version for version in versions if compare(
        version, current_version, '>')]


def get_package_data_from_pypi(package_name):
    """Return the json page from pypi for the given package

    :param package_name: package name
    """

    try:
        requests.packages.urllib3.disable_warnings()
        return json.loads(requests.get(
            consts.PYPI_URL.format(package_name)).content)
    except BaseException:
        return None


def get_from_pypi(package_name):
    """Return all the versions available on pypi for a given package

    :param package_name: package name
    """

    result = get_package_data_from_pypi(package_name)
    if result is None:
        return package_name, [], consts.UNKNOWN_LICENSE_STR

    releases = [str(ver) for ver in result.get(consts.RELEASES_KEY, [])]

    package_license = result.get(consts.INFO_KEY, {}).get(
        consts.LICENSE_KEY, consts.UNKNOWN)
    return package_name, releases, package_license


def get_new_available(my_versions, all_versions):
    """Return list of tuples of package name, current version and a list of
    newer versions available

    does not include tuples with no newer versions available

    :param my_versions: a dictionary mapping package name to list of versions
    in current project
    :param all_versions: a dictionary mapping package name to list of versions
    available on pypi
    """

    result = []
    for my_dependency in sorted(my_versions):
        if my_dependency in all_versions:
            for current_version in my_versions[my_dependency]:
                result.append({
                    consts.PACKAGE_KEY: my_dependency,
                    consts.REQUIRE_KEY: current_version,
                    consts.NEW_VERS_KEY: _filter_newer(
                        all_versions[my_dependency],
                        split_require(current_version)[0])})
    return result
