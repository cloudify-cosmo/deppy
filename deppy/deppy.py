"""Deppy is a dependencies management tool for projects/packages

It is used to seek for updates for your project/package dependencies, or to
show the dependencies tree for an installed package, with details about each
package in the dependencies tree, including versions conflicts, and versions
available according to the requirements of the main package and its
dependencies.
"""

import os
import json
import argparse
import multiprocessing

import sys

from . import consts
from . import versions
from . import dependencies


def _find_files_in_path(name, path):
    """Return a list of file paths with the right name, in a given path.

    Search in the entire dir tree

    :param name: file name to find
    :param path: path to search in
    """
    results = []
    for abs_dir_path, _, files in os.walk(path):
        if name in files:
            results.append(os.path.join(abs_dir_path, name))
    return results


def _set_default_kwargs(kwargs, defaults):
    """Set the args, in case called with missing args (not by CLI)

    :param kwargs: func kwargs to set
    :param defaults: default values relevant for the sub-command func
    """
    for default in defaults:
        if default not in kwargs:
            kwargs[default] = defaults[default]


def _parallel(func, args, threads_num=None):
    """Initialize a pool and run a given func in parallel over different args

    :param func: the function to be executed in parallel
    :param args: iterable object containing arguments for the function
    :param threads_num: limit the number of threads, None for unlimited
    """
    pool = multiprocessing.Pool(threads_num)
    return pool.map(func, args)


def _licenses_to_string(licenses_dict, by_module):
    """Return the result (licenses dict) in a string format

    :param licenses_dict: mapping packages to licenses (or vise versa)
    :param by_module: true if the keys are packages, false if licenses
    """
    result = ''
    for lic in sorted(licenses_dict):
        if by_module:
            result += 'Package: {0}  -->  License: {1}\n'.format(
                lic, licenses_dict[lic])
        else:
            result += 'License: {0}  -->  Packages: {1}\n'.format(
                lic, licenses_dict[lic])
    return result


def _dependencies_tree_to_string(dependencies_tree,
                                 root,
                                 result='',
                                 current_depth=0,
                                 require=''):
    """Return the result (the dependencies tree) in a string format

    :param dependencies_tree: a dictionary representing the dependencies tree
    :param root: the root of the current sub-tree
    :param result: current result
    :param current_depth: depth of current root in the tree
    :param require: the require versions for this package
    (empty for root of the whole tree)
    """

    root = root.lower()
    if root not in dependencies_tree:
        return result
    margin = consts.TAB * current_depth
    result += '\n{0}Package:  {1}{2}\n'.format(margin, root, require)
    for item in sorted(dependencies_tree.get(root, {})):
        if item != consts.DEPENDENCIES_KEY:
            result += '{0}{1}:  {2}\n'.format(
                margin, item, dependencies_tree[root][item])
    for dependency in dependencies_tree.get(root, {}).get(
            consts.DEPENDENCIES_KEY, []):
        result = _dependencies_tree_to_string(
            dependencies_tree, dependency[consts.PACKAGE_KEY], result,
            current_depth + 1, dependency[consts.REQUIRE_KEY])
    return result


def _seekup_to_string_by_module(results, modules, licenses_dict=None):
    """Return the result in a string format, sorted by modules

    :param results: the results
    :param modules: a dictionary mapping modules to dependencies
    :param licenses_dict: a dictionary mapping packages to licenses
    """
    result_str = ''
    for file_path in sorted(modules):
        current_results = [result for result in results
                           if result[consts.NEW_VERS_KEY] and
                           (result[consts.PACKAGE_KEY],
                            result[consts.REQUIRE_KEY])
                           in modules[file_path]]
        if current_results:
            result_str += '\nIn module:     {0}\n'.format(file_path)
            for current_result in current_results:
                result_str += \
                    '     {0}{1}  -->  {2}\n'.format(
                        current_result[consts.PACKAGE_KEY],
                        current_result[consts.REQUIRE_KEY],
                        current_result[consts.NEW_VERS_KEY]
                    )
                if licenses_dict:
                    result_str += '        LICENSE:  {0}\n'.format(
                        licenses_dict[current_result[consts.PACKAGE_KEY]])
    return result_str


def _seekup_to_string_by_dependency(results, modules, licenses_dict=None):
    """Return the result in a string format, sorted by dependencies

    :param results: the results
    :param modules: a dictionary mapping dependencies to modules
    :param licenses_dict: a dictionary mapping packages to licenses
    """
    result_str = ''
    for result in results:
        if result[consts.NEW_VERS_KEY]:
            result_str += '\n{0}{1}  -->  {2}'.format(
                result[consts.PACKAGE_KEY],
                result[consts.REQUIRE_KEY],
                result[consts.NEW_VERS_KEY]
            )
            if licenses_dict:
                result_str += '        LICENSE:  {0}'. \
                    format(licenses_dict[result[consts.PACKAGE_KEY]])
            result_str += '\n     In the following modules:\n'
            for file_path in modules[
                        result[consts.PACKAGE_KEY] +
                        result[consts.REQUIRE_KEY]
            ]:
                result_str += '             {0}\n'.format(file_path)
    return result_str


def _illegitimate_licenses_to_string(illegitimate_licenses):
    """Return a string with the given illegitimate licenses

    :param illegitimate_licenses: illegitimate licenses
    """
    if not illegitimate_licenses:
        return ''
    result = '\n\n**********************************************************' \
             '**********************************************************\n\n' \
             'Illegitimate Licenses:\n\n'
    for pack in sorted(illegitimate_licenses):
        result += '{0}{1}:  {2}\n'.format(
            consts.TAB, pack, illegitimate_licenses[pack])
    return result


def _get_dependencies_from_path(kwargs):
    """Get dependencies for project(s) in a given path via setup.py files

    :param kwargs: arguments
    """

    # get all paths of setup files in project
    paths = _find_files_in_path(
        consts.SETUP_FILE_NAME, kwargs[consts.INPUT_STR])

    if not paths:
        return consts.ERROR_MESSAGE_NO_SETUP

    # get dependencies list of each file - in parallel
    return _parallel(
        dependencies.get_from_file, paths, kwargs[consts.MAX_JOBS_STR])


def _get_dependencies_from_url(kwargs):
    """Get dependencies from a setup.py file given by url

    :param kwargs: arguments
    """

    result = dependencies.get_by_url(
        kwargs[consts.INPUT_STR], kwargs.get(consts.REQUIREMENTS_STR))
    if result is None:
        return consts.ERROR_MESSAGE_URL
    return [result]


def _get_dependencies_by_package_name(kwargs):
    """Get dependencies for a package given by name via pipdeptree tool

    :param kwargs: arguments
    """

    result = dependencies.get_for_package(
        kwargs[consts.INPUT_STR], kwargs[consts.DEPTH_STR])
    # result is None if building a dependencies tree has failed
    if result is None:
        return consts.ERROR_MESSAGE_BUILDING_DEPTREE
    # dependencies list is None if the package is not installed
    if result[0] is None:
        return consts.ERROR_MESSAGE_NO_PACKAGE_INSTALLED.format(
            kwargs[consts.INPUT_STR])
    return [result]


INPUTS = {
    consts.INPUT_PACKAGE_STR: _get_dependencies_by_package_name,
    consts.INPUT_PATH_STR: _get_dependencies_from_path,
    consts.INPUT_URL_STR: _get_dependencies_from_url
}


def _parse_args():
    """Parse the argument and initialize mode indicators

    """

    main_parser = argparse.ArgumentParser(description=consts.MAIN_DESCRIPTION)
    subparsers = main_parser.add_subparsers(dest=consts.SUBCOMMAND_STR)

    seekup_parser = subparsers.add_parser(
        consts.SEEKUP_STR, description=consts.SEEKUP_DESCRIPTION)
    seekup_parser.add_argument(
        consts.RETURN_DATA_ARG_STR, dest=consts.RETURN_DATA_STR,
        action=consts.STORE_CONST_ACTION, const=True, default=False,
        help=consts.RETURN_DATA_HELP_STR)
    seekup_parser.add_argument(
        consts.BY_MODULE_ARG_STR, dest=consts.BY_MODULE_STR,
        action=consts.STORE_CONST_ACTION, const=True, default=False,
        help=consts.BY_MODULE_HELP_STR)
    seekup_parser.add_argument(
        consts.SHOW_LICENSE_ARG_STR, dest=consts.SHOW_LICENSE_STR,
        nargs='*', default=None, help=consts.SHOW_LICENSE_HELP_STR)
    seekup_parser.add_argument(
        consts.INPUT_TYPE_ARG_STR, dest=consts.INPUT_TYPE_STR, type=str,
        default=consts.DEFAULT_INPUT,
        help=consts.INPUT_TYPE_HELP_STR.format(*INPUTS))
    seekup_parser.add_argument(
        consts.REQUIREMENTS_ARG_STR, dest=consts.REQUIREMENTS_STR, type=str,
        default=None, help=consts.REQUIREMENTS_HELP_STR)
    seekup_parser.add_argument(
        consts.MAX_JOBS_ARG_STR, dest=consts.MAX_JOBS_STR, type=int,
        default=consts.MAX_JOBS_DEFAULT, help=consts.MAX_JOBS_HELP_STR)
    seekup_parser.add_argument(
        consts.INPUT_STR, metavar=consts.INPUT_METAVAR_STR, type=str,
        help=consts.INPUT_HELP_STR)

    showpack_parser = subparsers.add_parser(
        consts.SHOWPACK_STR, description=consts.SHOWPACK_DESCRIPTION)
    showpack_parser.add_argument(
        consts.DEPTH_ARG_STR, dest=consts.DEPTH_STR, type=int,
        default=consts.DEFAULT_DEPTH, help=consts.DEPTH_HELP_STR)
    showpack_parser.add_argument(
        consts.VERSIONS_ARG_STR, dest=consts.VERSIONS_STR,
        action=consts.STORE_CONST_ACTION, const=True, default=False,
        help=consts.VERSIONS_HELP_STR)
    showpack_parser.add_argument(
        consts.SHOW_LICENSE_ARG_STR, dest=consts.SHOW_LICENSE_STR,
        nargs='*', default=None, help=consts.SHOW_LICENSE_HELP_STR)
    showpack_parser.add_argument(
        consts.HOMEPAGE_ARG_STR, dest=consts.HOMEPAGE_STR,
        action=consts.STORE_CONST_ACTION, const=True, default=False,
        help=consts.HOMEPAGE_HELP_STR)
    showpack_parser.add_argument(
        consts.SUMMARY_ARG_STR, dest=consts.SUMMARY_STR,
        action=consts.STORE_CONST_ACTION, const=True, default=False,
        help=consts.SUMMARY_HELP_STR)
    showpack_parser.add_argument(
        consts.MAX_JOBS_ARG_STR, dest=consts.MAX_JOBS_STR, type=int,
        default=consts.MAX_JOBS_DEFAULT, help=consts.MAX_JOBS_HELP_STR)
    showpack_parser.add_argument(
        consts.RETURN_DATA_ARG_STR, dest=consts.RETURN_DATA_STR,
        action=consts.STORE_CONST_ACTION, const=True, default=False,
        help=consts.RETURN_DATA_HELP_STR)
    showpack_parser.add_argument(
        consts.INPUT_STR, metavar=consts.INPUT_METAVAR_STR, type=str,
        help=consts.SHOW_PACKAGE_INPUT_HELP_STR)

    licenses_parser = subparsers.add_parser(
        consts.LICENSES_STR, description=consts.LICENSES_DESCRIPTION)
    licenses_parser.add_argument(
        consts.RETURN_DATA_ARG_STR, dest=consts.RETURN_DATA_STR,
        action=consts.STORE_CONST_ACTION, const=True, default=False,
        help=consts.RETURN_DATA_HELP_STR)
    licenses_parser.add_argument(
        consts.BY_MODULE_ARG_STR, dest=consts.BY_MODULE_STR,
        action=consts.STORE_CONST_ACTION, const=True, default=False,
        help=consts.BY_MODULE_HELP_STR)
    licenses_parser.add_argument(
        consts.SHOW_LICENSE_ARG_STR, dest=consts.SHOW_LICENSE_STR,
        nargs='*', default=None, help=consts.SHOW_LICENSE_HELP_STR)
    licenses_parser.add_argument(
        consts.INPUT_TYPE_ARG_STR, dest=consts.INPUT_TYPE_STR, type=str,
        default=consts.DEFAULT_INPUT,
        help=consts.INPUT_TYPE_HELP_STR.format(*INPUTS))
    licenses_parser.add_argument(
        consts.DEPTH_ARG_STR, dest=consts.DEPTH_STR, type=int,
        default=consts.DEFAULT_DEPTH, help=consts.DEPTH_HELP_STR)
    licenses_parser.add_argument(
        consts.REQUIREMENTS_ARG_STR, dest=consts.REQUIREMENTS_STR, type=str,
        default=None, help=consts.REQUIREMENTS_HELP_STR)
    licenses_parser.add_argument(
        consts.MAX_JOBS_ARG_STR, dest=consts.MAX_JOBS_STR, type=int,
        default=consts.MAX_JOBS_DEFAULT, help=consts.MAX_JOBS_HELP_STR)
    licenses_parser.add_argument(
        consts.INPUT_STR, metavar=consts.INPUT_METAVAR_STR, type=str,
        help=consts.INPUT_HELP_STR)

    args = main_parser.parse_args()
    return vars(args)


def show_package(**kwargs):
    """Show package details, including dependencies and their details

    :param kwargs: arguments inserted via CLI
    """

    default_kwargs = {
        consts.INPUT_TYPE_STR: consts.DEFAULT_INPUT,
        consts.DEPTH_STR: consts.DEFAULT_DEPTH,
        consts.REQUIREMENTS_STR: consts.REQUIREMENTS_DEFAULT,
        consts.MAX_JOBS_STR: consts.MAX_JOBS_DEFAULT,
        consts.SHOW_LICENSE_STR: None,
        consts.VERSIONS_STR: False,
        consts.HOMEPAGE_STR: False,
        consts.SUMMARY_STR: False,
        consts.RETURN_DATA_STR: False
    }
    _set_default_kwargs(kwargs, default_kwargs)
    if consts.INPUT_STR not in kwargs:
        return consts.ERROR_MESSAGE_NO_INPUT

    dependencies_tree = dependencies.build_tree(
        kwargs[consts.INPUT_STR], kwargs[consts.DEPTH_STR])
    if dependencies_tree is None:
        return consts.ERROR_MESSAGE_BUILDING_DEPTREE

    if kwargs[consts.SHOW_LICENSE_STR] is not None \
            or kwargs[consts.VERSIONS_STR] \
            or kwargs[consts.HOMEPAGE_STR] \
            or kwargs[consts.SUMMARY_STR]:
        packages_list = _parallel(versions.get_package_data_from_pypi,
                                  dependencies_tree.keys(),
                                  kwargs[consts.MAX_JOBS_STR])
        packages_dict = dict(
            (item[consts.INFO_KEY][consts.NAME_KEY].lower(), item)
            for item in packages_list
            if item is not None and consts.INFO_KEY in item and
            consts.NAME_KEY in item[consts.INFO_KEY]
        )
    else:
        packages_dict = {}

    illegitimate_licenses = {}

    for pack in dependencies_tree:
        pack_dict = packages_dict.get(pack, {})
        info = pack_dict.get(consts.INFO_KEY, {})
        deps = dependencies_tree[pack]
        dependencies_tree[pack] = {
            consts.DEPENDENCIES_KEY: deps,
            consts.SUMMARY_KEY: info.get(consts.SUMMARY_KEY, consts.UNKNOWN)
            if kwargs[consts.SUMMARY_STR] else None,
            consts.LICENSE_KEY: info.get(consts.LICENSE_KEY, consts.UNKNOWN)
            if kwargs[consts.SHOW_LICENSE_STR] is not None else None,
            consts.HOMEPAGE_KEY: info.get(consts.HOMEPAGE_KEY, consts.UNKNOWN)
            if kwargs[consts.HOMEPAGE_STR] else None,
            consts.VERSIONS_KEY: pack_dict.get(consts.RELEASES_KEY, {}).keys()
            if kwargs[consts.VERSIONS_STR] else None
        }
        dependencies_tree[pack] = dict(
            (key, dependencies_tree[pack][key])
            for key in dependencies_tree[pack]
            if dependencies_tree[pack][key] is not None
        )
        if kwargs[consts.SHOW_LICENSE_STR] is not None:
            lic = info.get(consts.LICENSE_KEY, consts.UNKNOWN)
            dependencies_tree[pack][consts.LICENSE_KEY] = lic
            if kwargs[consts.SHOW_LICENSE_STR] \
                    and lic not in kwargs[consts.SHOW_LICENSE_STR]:
                illegitimate_licenses[pack] = lic

    result = {'dependencies_tree': dependencies_tree}
    if kwargs[consts.SHOW_LICENSE_STR] is not None:
        result[consts.ILLEGITIMATE_LICENSES_KEY] = illegitimate_licenses

    if kwargs[consts.RETURN_DATA_STR]:
        return json.dumps(result, indent=consts.TAB_SIZE)

    result_str = _dependencies_tree_to_string(
        dependencies_tree, kwargs[consts.INPUT_STR])
    if kwargs[consts.SHOW_LICENSE_STR] is not None:
        result_str += _illegitimate_licenses_to_string(illegitimate_licenses)

    return result_str


def seekup(**kwargs):
    """Seek upgrades for dependencies of a given project/package
    for each dependency returns the versions available and newer than the
    versions currently used

    :param kwargs: arguments inserted via CLI
    """

    # check kwargs
    default_kwargs = {
        consts.INPUT_TYPE_STR: consts.DEFAULT_INPUT,
        consts.REQUIREMENTS_STR: consts.REQUIREMENTS_DEFAULT,
        consts.MAX_JOBS_STR: consts.MAX_JOBS_DEFAULT,
        consts.SHOW_LICENSE_STR: None,
        consts.BY_MODULE_STR: False,
        consts.RETURN_DATA_STR: False
    }
    _set_default_kwargs(kwargs, default_kwargs)
    kwargs[consts.DEPTH_STR] = 0
    if consts.INPUT_STR not in kwargs:
        return consts.ERROR_MESSAGE_NO_INPUT
    if kwargs[consts.INPUT_TYPE_STR] not in INPUTS:
        return consts.ERROR_MESSAGE_ILLEGAL_INPUT_TYPE.format(INPUTS.keys())

    dependencies_list = INPUTS[kwargs[consts.INPUT_TYPE_STR]](kwargs)

    if isinstance(dependencies_list, basestring):
        return dependencies_list

    # build a dictionary of dependencies
    dependencies_dict = {}
    modules_dict = {}
    for sub_list, module, _ in dependencies_list:
        for package, version, operator in sub_list:
            if package not in dependencies_dict:
                dependencies_dict[package] = []
            if operator + version not in dependencies_dict[package]:
                dependencies_dict[package].append(operator + version)

            # build a dictionary of dep per modules
            if kwargs[consts.BY_MODULE_STR]:
                dict_key = module
                dict_list_item = package, operator + version
            else:
                dict_key = package + operator + version
                dict_list_item = module
            if dict_key not in modules_dict:
                modules_dict[dict_key] = []
            modules_dict[dict_key].append(dict_list_item)

    if not dependencies_dict:
        return consts.ERROR_MESSAGE_NO_DEPENDENCIES

    # get versions available from chosen source - in parallel
    versions_list = _parallel(versions.get_from_pypi,
                              dependencies_dict.keys(),
                              kwargs[consts.MAX_JOBS_STR])
    # put versions available and license in a dictionaries
    versions_dict = dict((name, vers)
                         for name, vers, lic in versions_list
                         if vers)

    license_dict = dict(
        (name, lic)
        for name, vers, lic in versions_list
    ) if kwargs[consts.SHOW_LICENSE_STR] is not None else None

    illegitimate_licenses = dict(
        (pack, license_dict[pack])
        for pack in license_dict
        if license_dict[pack] not in kwargs[consts.SHOW_LICENSE_STR]
    ) if kwargs[consts.SHOW_LICENSE_STR] else None

    if not versions_dict:
        return consts.ERROR_MESSAGE_NO_VERSIONS

    # get the new versions available for each dependency
    results = versions.get_new_available(
        dependencies_dict, versions_dict)

    result_dict = {
        consts.RESULTS_KEY: results,
        consts.MODULES_KEY: modules_dict,
    }
    if license_dict is not None:
        result_dict[consts.LICENSE_KEY] = license_dict
    if illegitimate_licenses is not None:
        result_dict[consts.ILLEGITIMATE_LICENSES_KEY] = illegitimate_licenses

    if kwargs[consts.RETURN_DATA_STR]:
        return json.dumps(result_dict, indent=consts.TAB_SIZE)

    if kwargs[consts.BY_MODULE_STR]:
        result_str = _seekup_to_string_by_module(
            results, modules_dict, license_dict)
    else:
        result_str = _seekup_to_string_by_dependency(
            results, modules_dict, license_dict)

    return result_str + _illegitimate_licenses_to_string(illegitimate_licenses)


def licenses(**kwargs):
    """Return licenses info about a given package and its dependencies

    :param kwargs: arguments inserted via CLI
    """

    # check kwargs
    default_kwargs = {
        consts.INPUT_TYPE_STR: consts.DEFAULT_INPUT,
        consts.MAX_JOBS_STR: consts.MAX_JOBS_DEFAULT,
        consts.DEPTH_STR: consts.DEFAULT_DEPTH,
        consts.REQUIREMENTS_STR: consts.REQUIREMENTS_DEFAULT,
        consts.SHOW_LICENSE_STR: None,
        consts.BY_MODULE_STR: False,
        consts.RETURN_DATA_STR: False
    }
    _set_default_kwargs(kwargs, default_kwargs)
    if consts.INPUT_STR not in kwargs:
        return consts.ERROR_MESSAGE_NO_INPUT
    if kwargs[consts.INPUT_TYPE_STR] not in INPUTS:
        return consts.ERROR_MESSAGE_ILLEGAL_INPUT_TYPE.format(INPUTS.keys())

    dependencies_list = INPUTS[kwargs[consts.INPUT_TYPE_STR]](kwargs)
    if isinstance(dependencies_list, basestring):
        return dependencies_list

    dependencies_dict = dict((package, lic)
                             for _, package, lic in dependencies_list)

    dependencies_set = set(pack_name for _, pack_name, __ in dependencies_list)
    for sub_list, _, __ in dependencies_list:
        for dep, ver, op in sub_list:
            dependencies_set.add(dep)

    packages = _parallel(
        versions.get_from_pypi, dependencies_set, kwargs[consts.MAX_JOBS_STR])

    licenses_dict = {}
    illegitimate_licenses = {}
    for package, dep_list, pack_license in packages:
        name = str(package)
        lic = str(pack_license)
        if lic == consts.UNKNOWN:
            lic = dependencies_dict.get(package, consts.UNKNOWN)
        key = name if kwargs[consts.BY_MODULE_STR] else lic
        value = lic if kwargs[consts.BY_MODULE_STR] else name
        if key not in licenses_dict:
            licenses_dict[key] = []
        if value not in licenses_dict[key]:
            licenses_dict[key].append(value)
        if kwargs[consts.SHOW_LICENSE_STR] \
                and lic not in kwargs[consts.SHOW_LICENSE_STR]:
            if key not in illegitimate_licenses:
                illegitimate_licenses[key] = []
            if value not in illegitimate_licenses[key]:
                illegitimate_licenses[key].append(value)

    if kwargs[consts.RETURN_DATA_STR]:
        return json.dumps({
            consts.LICENSE_KEY: licenses_dict,
            consts.ILLEGITIMATE_LICENSES_KEY: illegitimate_licenses
        }, indent=consts.TAB_SIZE)
    return _licenses_to_string(licenses_dict, kwargs[consts.BY_MODULE_STR]) \
        + _illegitimate_licenses_to_string(illegitimate_licenses)


functions_dict = {
    consts.SEEKUP_STR: seekup,
    consts.SHOWPACK_STR: show_package,
    consts.LICENSES_STR: licenses
}


def main():
    """Parse args from CLI and call func according to sub-command

    """
    kwargs = _parse_args()
    sys.stdout.write(
        functions_dict[kwargs[consts.SUBCOMMAND_STR]](**kwargs) + '\n')


if __name__ == '__main__':
    print main(),
