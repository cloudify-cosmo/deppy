"""
Deppy is a dependencies management tool for projects/packages

It is used to seek for updates for your project/package dependencies, or to
show the dependencies tree for an installed package, with details about each
package in the dependencies tree, including versions conflicts, and versions
available according to the requirements of the main package and its
dependencies.

"""

import json
import os
import argparse

from joblib import Parallel, delayed

import dep_vers_module
import vers_getter
from vers_getter import \
    INFO_KEY, NAME_KEY, DEPENDENCIES_KEY, VERSIONS_KEY, LICENSE_KEY, \
    HOMEPAGE_KEY, SUMMARY_KEY, PACKAGE_KEY, RELEASES_KEY, UNKNOWN_LICENSE_STR


SETUP_FILE_NAME = 'setup.py'
RESULTS_KEY = 'results'
MODULES_KEY = 'modules'
ARGUMENTS_KEY = 'args'
TAB_SIZE = 4
TAB = ' ' * TAB_SIZE


def find_files_in_path(name, path):
    """
    return a list of file paths with the right name, in a given path

    :param name: file name to find
    :param path: path to search in
    """
    find_result = []
    for root, dirs, files in os.walk(path):
        if name in files:
            find_result.append(os.path.join(root, name))
    return find_result


def dep_tree_to_print(dep_tree, root, res='', curr_depth=0, req=''):
    margin = TAB * curr_depth
    res += '{0}Package:  {1}\n'.format(margin, root + req)
    for item in dep_tree.get(root, {}):
        if item != DEPENDENCIES_KEY:
            res += '{0}{1}:  {2}\n'.format(margin, item, dep_tree[root][item])
    for dep in dep_tree.get(root, {}).get(DEPENDENCIES_KEY, []):
        res += '\n'
        res = dep_tree_to_print(
            dep_tree, dep[PACKAGE_KEY], res, curr_depth + 1,
            dep[dep_vers_module.REQUIRED_KEY])
    return res


def seekup_result_to_print(res_dic):
    """
    return the result in a string format

    :param res_dic: a dictionary contains the results
    """

    res_str = ''
    args = res_dic[ARGUMENTS_KEY]
    results = res_dic[RESULTS_KEY]
    modules_dic = res_dic[MODULES_KEY]
    if args[SHOW_LICENSE_STR]:
        lic_dic = res_dic[LICENSE_KEY]
    else:
        lic_dic = None

    # if running with -m arg, print results grouped by modules
    if args[BY_MODULE_STR]:
        for file_path in modules_dic:
            curr_results = [result for result in results
                            if result[vers_getter.NEW_VERS_KEY] and
                            (result[vers_getter.PACKAGE_KEY],
                             result[vers_getter.REQUIRE_KEY])
                            in modules_dic[file_path]]
            if curr_results:
                res_str += 'In module:     {0}\n'.format(file_path)
                for curr_result in curr_results:
                    res_str += \
                        '     {0}{1}  -->  {2}\n'.format(
                            curr_result[vers_getter.PACKAGE_KEY],
                            curr_result[vers_getter.REQUIRE_KEY],
                            curr_result[vers_getter.NEW_VERS_KEY]
                        )
                    if args[SHOW_LICENSE_STR]:
                        res_str += '        LICENSE:  {0}\n'.format(
                            lic_dic[curr_result[vers_getter.PACKAGE_KEY]])
                res_str += '\n'

    # default - print each result with relevant modules
    else:
        for result in results:
            if result[vers_getter.NEW_VERS_KEY]:
                res_str += '{0}{1}  -->  {2}'.format(
                    result[vers_getter.PACKAGE_KEY],
                    result[vers_getter.REQUIRE_KEY],
                    result[vers_getter.NEW_VERS_KEY]
                )
                if args[SHOW_LICENSE_STR]:
                    res_str += '        LICENSE:  {0}'. \
                        format(lic_dic[result[vers_getter.PACKAGE_KEY]])
                res_str += '\n     In the following modules:\n'
                for file_path in modules_dic[
                            result[vers_getter.PACKAGE_KEY] +
                            result[vers_getter.REQUIRE_KEY]
                ]:
                    res_str += "             {0}\n".format(file_path)
                res_str += '\n'
    return res_str


def get_deps_from_path(args):
    """
    get dependencies for project(s) in a given path via setup.py files

    :param args: arguments
    """

    # get all paths of setup files in project
    paths = find_files_in_path(SETUP_FILE_NAME, args[INPUT_STR])

    if not paths:
        return ERROR_MESSAGE_NO_SETUP

    # get dependencies list of each file - in parallel
    return Parallel(n_jobs=args[MAX_JOBS_STR])(delayed(
        dep_vers_module.get_dependencies_from_file)(path) for path in paths)


def get_deps_from_url(args):
    res = dep_vers_module.get_dependencies_by_url(args[INPUT_STR])
    if res is None:
        return ERROR_MESSAGE_URL
    return [res]


def get_deps_by_package_name(args):
    """
    get dependencies for a package given by name via pipdeptree tool

    :param args: arguments
    """

    res = dep_vers_module.get_dependencies_for_package(args[INPUT_STR])
    if res is None:
        return ERROR_MESSAGE_BUILDING_DEPTREE
    if res[0] is None:
        return ERROR_MESSAGE_NO_PACKAGE_INSTALLED
    return [res]


MAIN_DESCRIPTION = 'Manage dependencies in your projects'
SEEKUP_DESCRIPTION = 'Find newer versions for project dependencies'
SHOWPACK_DESCRIPTION = 'Show info about given package'
SUBCOMMAND_STR = 'subcommand'
SEEKUP_STR = 'seekup'
SHOWPACK_STR = 'showpack'
INPUT_TYPE_ARG_STR = '-i'
INPUT_PACKAGE_STR = 'package'
INPUT_PATH_STR = 'path'
INPUT_URL_STR = 'url'
INPUT_TYPE_STR = 'input_type'
INPUTS = {
    INPUT_PACKAGE_STR: get_deps_by_package_name,
    INPUT_PATH_STR: get_deps_from_path,
    INPUT_URL_STR: get_deps_from_url
}
DEFAULT_INPUT = INPUT_PACKAGE_STR
INPUT_TYPE_HELP_STR = 'choose input type.  options:  ' \
                      '{0} (URL for setup.py file),  ' \
                      '{1} (path for project folder),  ' \
                      '{2} (name of package already installed - default)'. \
    format(*INPUTS)
PYPI_JSON_STR = 'pypy_json'
DEPTH_ARG_STR = '-dep'
DEPTH_STR = 'depth'
DEFAULT_DEPTH = -1
DEPTH_HELP_STR = 'maximum depth for dependencies tree'
VERSIONS_ARG_STR = '-ver'
VERSIONS_STR = 'versions'
VERSIONS_HELP_STR = 'get all versions available for the package'
HOMEPAGE_ARG_STR = '-hom'
HOMEPAGE_STR = 'homepage'
HOMEPAGE_HELP_STR = 'get package homepage'
SUMMARY_ARG_STR = '-sum'
SUMMARY_STR = 'summary'
SUMMARY_HELP_STR = 'get package summary'
BY_MODULE_ARG_STR = '-m'
BY_MODULE_STR = 'by_module'
BY_MODULE_HELP_STR = 'sort results by module (default: by dependencies)'
RETURN_DATA_ARG_STR = '-j'
RETURN_DATA_STR = 'json'
RETURN_DATA_HELP_STR = 'return results as json (default: print as string)'
SHOW_LICENSE_ARG_STR = '-l'
SHOW_LICENSE_STR = 'show_license'
SHOW_LICENSE_HELP_STR = 'show license for package (if known)'
STORE_CONST_ACTION = 'store_const'
MAX_JOBS_ARG_STR = '-t'
MAX_JOBS_STR = 'max_threads'
MAX_JOBS_DEFAULT = -1
MAX_JOBS_HELP_STR = 'limit the number of threads, negative for unlimited ' \
                    '(default: {0})'.format(MAX_JOBS_DEFAULT)
SOURCE_ARG_STR = '-s'
SOURCE_STR = 'source'
PYPI, PIP, GITHUB = 'pypi', 'pip', 'github'
SOURCES = {
    PYPI: vers_getter.get_versions_from_pypi,
    PIP: vers_getter.get_versions_from_pip,
    #    GITHUB: vers_getter.get_versions_from_github
}
SOURCE_DEFAULT = PYPI
SOURCE_HELP_STR = 'choose source for available versions (default: {0})'.format(
    SOURCE_DEFAULT)
INPUT_STR = 'input'
INPUT_METAVAR_STR = 'INPUT'
INPUT_HELP_STR = 'package'
SHOW_PACKAGE_INPUT_HELP_STR = 'package name'

ERROR_MESSAGE_ILLEGAL_SOURCE = \
    'Illegal source chosen. Legit sources are: {0}'.format(SOURCES.keys())
ERROR_MESSAGE_ILLEGAL_INPUT_TYPE = \
    'Illegal input type chosen.  Legit input types are: {0}'.format(
        INPUTS.keys())
ERROR_MESSAGE_NO_SETUP = 'No {0} files found in the given path'.format(
    SETUP_FILE_NAME)
ERROR_MESSAGE_NO_PACKAGE_INSTALLED = 'No package found with the given name'
ERROR_MESSAGE_NO_DEPENDENCIES = 'No dependencies found in project'
ERROR_MESSAGE_NO_VERSIONS = 'No versions found online'
ERROR_MESSAGE_BUILDING_DEPTREE = 'Error while building dependencies tree'
ERROR_MESSAGE_URL = 'Error while getting dependencies from url'
ERROR_MESSAGE_PYPI_JSON = 'Error while getting json from pypi'


def parse_args():
    """
    parse the argument and initialize mode indicators

    """

    main_parser = argparse.ArgumentParser(description=MAIN_DESCRIPTION)
    subparsers = main_parser.add_subparsers(dest=SUBCOMMAND_STR)

    seekup_parser = subparsers.add_parser(
        SEEKUP_STR, description=SEEKUP_DESCRIPTION)
    seekup_parser.add_argument(
        RETURN_DATA_ARG_STR, dest=RETURN_DATA_STR, action=STORE_CONST_ACTION,
        const=True, default=False, help=RETURN_DATA_HELP_STR)
    seekup_parser.add_argument(
        BY_MODULE_ARG_STR, dest=BY_MODULE_STR, action=STORE_CONST_ACTION,
        const=True, default=False, help=BY_MODULE_HELP_STR)
    seekup_parser.add_argument(
        SHOW_LICENSE_ARG_STR, dest=SHOW_LICENSE_STR, action=STORE_CONST_ACTION,
        const=True, default=False, help=SHOW_LICENSE_HELP_STR)
    seekup_parser.add_argument(
        INPUT_TYPE_ARG_STR, dest=INPUT_TYPE_STR, type=str,
        default=DEFAULT_INPUT, help=INPUT_TYPE_HELP_STR)
    seekup_parser.add_argument(
        SOURCE_ARG_STR, dest=SOURCE_STR, type=str, default=SOURCE_DEFAULT,
        help=SOURCE_HELP_STR)
    seekup_parser.add_argument(
        MAX_JOBS_ARG_STR, dest=MAX_JOBS_STR, type=int,
        default=MAX_JOBS_DEFAULT, help=MAX_JOBS_HELP_STR)
    seekup_parser.add_argument(
        INPUT_STR, metavar=INPUT_METAVAR_STR, type=str, help=INPUT_HELP_STR)

    showpack_parser = subparsers.add_parser(
        SHOWPACK_STR, description=SHOWPACK_DESCRIPTION)
    showpack_parser.add_argument(
        DEPTH_ARG_STR, dest=DEPTH_STR, type=int, default=DEFAULT_DEPTH,
        help=DEPTH_HELP_STR)
    showpack_parser.add_argument(
        VERSIONS_ARG_STR, dest=VERSIONS_STR, action=STORE_CONST_ACTION,
        const=True, default=False, help=VERSIONS_HELP_STR)
    showpack_parser.add_argument(
        SHOW_LICENSE_ARG_STR, dest=SHOW_LICENSE_STR, action=STORE_CONST_ACTION,
        const=True, default=False, help=SHOW_LICENSE_HELP_STR)
    showpack_parser.add_argument(
        HOMEPAGE_ARG_STR, dest=HOMEPAGE_STR, action=STORE_CONST_ACTION,
        const=True, default=False, help=HOMEPAGE_HELP_STR)
    showpack_parser.add_argument(
        SUMMARY_ARG_STR, dest=SUMMARY_STR, action=STORE_CONST_ACTION,
        const=True, default=False, help=SUMMARY_HELP_STR)
    showpack_parser.add_argument(
        MAX_JOBS_ARG_STR, dest=MAX_JOBS_STR, type=int,
        default=MAX_JOBS_DEFAULT, help=MAX_JOBS_HELP_STR)
    showpack_parser.add_argument(
        RETURN_DATA_ARG_STR, dest=RETURN_DATA_STR, action=STORE_CONST_ACTION,
        const=True, default=False, help=RETURN_DATA_HELP_STR)
    showpack_parser.add_argument(
        INPUT_STR, metavar=INPUT_METAVAR_STR, type=str,
        help=SHOW_PACKAGE_INPUT_HELP_STR)

    args = main_parser.parse_args()
    return vars(args)


def show_package(args):
    dep_tree = dep_vers_module.build_dep_tree(
        args[INPUT_STR], args[DEPTH_STR])
    if dep_tree is None:
        return ERROR_MESSAGE_BUILDING_DEPTREE

    if args[SHOW_LICENSE_STR] or args[VERSIONS_STR] or args[HOMEPAGE_STR] \
            or args[SUMMARY_STR]:
        json_list = Parallel(n_jobs=args[MAX_JOBS_STR])(
            delayed(vers_getter.get_json_from_pypi)(package_name)
            for package_name in dep_tree.keys())
        json_dic = {item[INFO_KEY][NAME_KEY].lower(): item
                    for item in json_list
                    if item is not None and INFO_KEY in item and
                    NAME_KEY in item[INFO_KEY]}
    else:
        json_dic = {}

    for pack in dep_tree:
        pack_json = json_dic.get(pack, {})
        info = pack_json.get(INFO_KEY, {})
        deps = dep_tree[pack]
        dep_tree[pack] = {
            DEPENDENCIES_KEY: deps,
            SUMMARY_KEY: info.get(SUMMARY_KEY, '')
            if args[SUMMARY_STR] else None,
            LICENSE_KEY: info.get(LICENSE_KEY, UNKNOWN_LICENSE_STR)
            if args[SHOW_LICENSE_STR] else None,
            HOMEPAGE_KEY: info.get(HOMEPAGE_KEY, '')
            if args[HOMEPAGE_STR] else None,
            VERSIONS_KEY: pack_json.get(RELEASES_KEY, {}).keys()
            if args[VERSIONS_STR] else None
        }
        dep_tree[pack] = {key: dep_tree[pack][key] for key in dep_tree[pack]
                          if dep_tree[pack][key] is not None}

    if args[RETURN_DATA_STR]:
        return json.dumps(dep_tree, indent=TAB_SIZE)
    return dep_tree_to_print(dep_tree, args[INPUT_STR])


def seekup(args):
    """
    seek upgrades for dependencies of a given project/package
    for each dependency returns the versions available and newer than the
    versions currently used

    """

    # check args
    if args[SOURCE_STR] not in SOURCES:
        return ERROR_MESSAGE_ILLEGAL_SOURCE
    if args[INPUT_TYPE_STR] not in INPUTS:
        return ERROR_MESSAGE_ILLEGAL_INPUT_TYPE

    dep_list = INPUTS[args[INPUT_TYPE_STR]](args)

    if isinstance(dep_list, basestring):
        return dep_list

    # build a dictionary of dependencies
    dep_dic = {}
    modules_dic = {}
    for sub_list in dep_list:
        for (pack, ver, op) in sub_list[0]:
            if pack not in dep_dic:
                dep_dic[pack] = []
            if op + ver not in dep_dic[pack]:
                dep_dic[pack].append(op + ver)

            # build a dictionary of dep per modules
            if args[BY_MODULE_STR]:
                dic_key = sub_list[1]
                dic_list_item = (pack, op + ver)
            else:
                dic_key = pack + op + ver
                dic_list_item = sub_list[1]
            if dic_key not in modules_dic:
                modules_dic[dic_key] = []
            modules_dic[dic_key].append(dic_list_item)

    if not dep_dic:
        return ERROR_MESSAGE_NO_DEPENDENCIES

    # get versions available from chosen source - in parallel
    vers_list = Parallel(n_jobs=args[MAX_JOBS_STR])(delayed(
        SOURCES[args[SOURCE_STR]])(key) for key in dep_dic.keys())
    # put versions available and license in a dictionaries
    vers_dic = {ver_tuple[0]: ver_tuple[1]
                for ver_tuple in vers_list if ver_tuple[1]}
    if args[SHOW_LICENSE_STR]:
        lic_dic = {ver_tuple[0]: ver_tuple[2] for ver_tuple in vers_list}
    else:
        lic_dic = None
    if not vers_dic:
        return ERROR_MESSAGE_NO_VERSIONS

    # get the new versions available for each dependency
    results = vers_getter.get_new_versions_available(dep_dic, vers_dic)

    res_dic = {
        RESULTS_KEY: results,
        MODULES_KEY: modules_dic,
    }
    if args[SHOW_LICENSE_STR]:
        res_dic[LICENSE_KEY] = lic_dic

    if args[RETURN_DATA_STR]:
        return json.dumps(res_dic, indent=TAB_SIZE)
    res_dic[ARGUMENTS_KEY] = args
    return seekup_result_to_print(res_dic)


def main():
    args = parse_args()
    func_dic = {
        SEEKUP_STR: seekup,
        SHOWPACK_STR: show_package
    }
    return func_dic[args[SUBCOMMAND_STR]](args)


if __name__ == '__main__':
    print main(),
