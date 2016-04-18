
import os
import sys
import json
import copy

import mock
import yaml
import testtools

import tests_consts

from deppy import deppy
from deppy import consts
from deppy import dependencies
from helpers import cmp_elements


class TestDeppy(testtools.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestDeppy, self).__init__(*args, **kwargs)
        self.old_err = sys.stderr
        self.old_out = sys.stdout
        self.old_parallel = deppy._parallel
        self.old_inputs = copy.deepcopy(deppy.INPUTS)

    def tearDown(self):
        sys.stdout = self.old_out
        sys.stderr = self.old_err
        deppy._parallel = self.old_parallel
        deppy.INPUTS = self.old_inputs
        super(TestDeppy, self).tearDown()

    def _generic_test(self, func, expected, *func_args):
        self.assertTrue(cmp_elements(expected, func(*func_args)))

    def test_find_files_in_path(self):

        def test(expected_result, *tested_func_args):
            self._generic_test(deppy._find_files_in_path,
                               expected_result, *tested_func_args)

        expected = []
        func_args = [tests_consts.DUMMY_FILE_NAME, tests_consts.RESOURCES_PATH]
        test(expected, *func_args)

        dir_path = os.path.join(
            tests_consts.RESOURCES_PATH, tests_consts.DUMMY_DIR_NAME)
        expected = []
        func_args = [tests_consts.SETUP_FILE_NAME, dir_path]
        test(expected, *func_args)

        dir_path = '][/.[pdl2-32'
        expected = []
        func_args = [tests_consts.SETUP_FILE_NAME, dir_path]
        test(expected, *func_args)

        dir_path = os.path.join(
            tests_consts.RESOURCES_PATH, tests_consts.DIR_NAME)
        expected = [os.path.join(dir_path, tests_consts.SETUP_FILE_NAME)]
        func_args = [tests_consts.SETUP_FILE_NAME, dir_path]
        test(expected, *func_args)

        dir_path = tests_consts.RESOURCES_PATH
        expected = [
            os.path.join(dir_path, tests_consts.SETUP_FILE_NAME),
            os.path.join(dir_path, tests_consts.DIR_NAME,
                         tests_consts.SETUP_FILE_NAME)
        ]
        func_args = [tests_consts.SETUP_FILE_NAME, dir_path]
        test(expected, *func_args)

    def test_set_default_kwargs(self):

        def test(expected_results, func_kwargs, func_defaults):
            deppy._set_default_kwargs(func_kwargs, func_defaults)
            cmp_elements(expected_results, func_kwargs)

        expected = {}
        kwargs = {}
        defaults = {}
        test(expected, kwargs, defaults)

        expected = {'a': 'b'}
        kwargs = {'a': 'b'}
        defaults = {}
        test(expected, kwargs, defaults)

        expected = {'a': 'b'}
        kwargs = {}
        defaults = {'a': 'b'}
        test(expected, kwargs, defaults)

        expected = {'a': 'c'}
        kwargs = {'a': 'c'}
        defaults = {'a': 'b'}
        test(expected, kwargs, defaults)

        expected = {'a': 'a1', 'b': 'b1', 'c': 'c2'}
        kwargs = {'a': 'a1', 'b': 'b1'}
        defaults = {'b': 'b2', 'c': 'c2'}
        test(expected, kwargs, defaults)

    def test_parallel(self):

        test_resources_path = os.path.join(
            tests_consts.RESOURCES_PATH, 'to_string', 'illegitimate_licenses')

        inputs = [
            {},
            {
                'package1': 'license1'
            },
            {
                'package1': 'license1',
                'package2': 'license2'
            },
            {
                'package1': 'license1',
                'package2': 'license2',
                'package3': 'license1'
            }
        ]

        outputs = ['']
        with open(os.path.join(test_resources_path, 'output1.txt'), 'r') \
                as output_file:
            outputs.append(output_file.read())

        with open(os.path.join(test_resources_path, 'output2.txt'), 'r') \
                as output_file:
            outputs.append(output_file.read())

        with open(os.path.join(test_resources_path, 'output3.txt'), 'r') \
                as output_file:
            outputs.append(output_file.read())

        self.assertTrue(
            cmp_elements(
                outputs,
                deppy._parallel(
                    deppy._illegitimate_licenses_to_string,
                    inputs,
                    threads_num=1
                )
            )
        )

    def test_parse_args(self):

        sys.stdout = None
        sys.stderr = None

        tested_func = deppy._parse_args

        def test(expected):
            self._generic_test(tested_func, expected)

        # normal
        sys.argv = ['', consts.SEEKUP_STR, tests_consts.DUMMY_PACKAGE_NAME]
        result = {
            consts.SUBCOMMAND_STR: consts.SEEKUP_STR,
            consts.INPUT_STR: tests_consts.DUMMY_PACKAGE_NAME,
            consts.INPUT_TYPE_STR: consts.DEFAULT_INPUT,
            consts.REQUIREMENTS_STR: consts.REQUIREMENTS_DEFAULT,
            consts.SHOW_LICENSE_STR: None,
            consts.BY_MODULE_STR: False,
            consts.RETURN_DATA_STR: False,
            consts.MAX_JOBS_STR: consts.MAX_JOBS_DEFAULT
        }
        test(result)

        # defaults
        sys.argv = ['', consts.SEEKUP_STR,
                    tests_consts.DUMMY_PACKAGE_NAME,
                    consts.SHOW_LICENSE_ARG_STR,
                    consts.REQUIREMENTS_ARG_STR, '',
                    consts.INPUT_TYPE_ARG_STR, consts.DEFAULT_INPUT,
                    ]
        result = {
            consts.SUBCOMMAND_STR: consts.SEEKUP_STR,
            consts.INPUT_STR: tests_consts.DUMMY_PACKAGE_NAME,
            consts.INPUT_TYPE_STR: consts.DEFAULT_INPUT,
            consts.REQUIREMENTS_STR: '',
            consts.SHOW_LICENSE_STR: [],
            consts.BY_MODULE_STR: False,
            consts.RETURN_DATA_STR: False,
            consts.MAX_JOBS_STR: consts.MAX_JOBS_DEFAULT
        }
        test(result)

        # use all args
        num_for_test = 7
        sys.argv = ['', consts.SEEKUP_STR,
                    tests_consts.DUMMY_PACKAGE_NAME,
                    consts.INPUT_TYPE_ARG_STR, consts.DEFAULT_INPUT,
                    consts.REQUIREMENTS_ARG_STR, 'bla',
                    consts.BY_MODULE_ARG_STR,
                    consts.RETURN_DATA_ARG_STR,
                    consts.MAX_JOBS_ARG_STR, str(num_for_test),
                    consts.SHOW_LICENSE_ARG_STR, 'license1', 'license2'
                    ]
        result = {
            consts.SUBCOMMAND_STR: consts.SEEKUP_STR,
            consts.INPUT_STR: tests_consts.DUMMY_PACKAGE_NAME,
            consts.INPUT_TYPE_STR: consts.DEFAULT_INPUT,
            consts.REQUIREMENTS_STR: 'bla',
            consts.SHOW_LICENSE_STR: ['license1', 'license2'],
            consts.BY_MODULE_STR: True,
            consts.RETURN_DATA_STR: True,
            consts.MAX_JOBS_STR: num_for_test
        }
        test(result)

        # different order
        sys.argv = ['', consts.SEEKUP_STR,
                    consts.INPUT_TYPE_ARG_STR, consts.DEFAULT_INPUT,
                    tests_consts.DUMMY_PACKAGE_NAME,
                    consts.SHOW_LICENSE_ARG_STR, 'license1', 'license2',
                    consts.RETURN_DATA_ARG_STR,
                    consts.MAX_JOBS_ARG_STR, str(num_for_test),
                    consts.REQUIREMENTS_ARG_STR, 'bla',
                    consts.BY_MODULE_ARG_STR
                    ]
        result = {
            consts.SUBCOMMAND_STR: consts.SEEKUP_STR,
            consts.INPUT_STR: tests_consts.DUMMY_PACKAGE_NAME,
            consts.INPUT_TYPE_STR: consts.DEFAULT_INPUT,
            consts.REQUIREMENTS_STR: 'bla',
            consts.SHOW_LICENSE_STR: ['license1', 'license2'],
            consts.BY_MODULE_STR: True,
            consts.RETURN_DATA_STR: True,
            consts.MAX_JOBS_STR: num_for_test
        }
        test(result)

        # check all input types and sources
        for input_type in deppy.INPUTS:
            sys.argv = ['', consts.SEEKUP_STR,
                        tests_consts.DUMMY_PACKAGE_NAME,
                        consts.INPUT_TYPE_ARG_STR, input_type
                        ]
            result = {
                consts.SUBCOMMAND_STR: consts.SEEKUP_STR,
                consts.INPUT_STR: tests_consts.DUMMY_PACKAGE_NAME,
                consts.INPUT_TYPE_STR: input_type,
                consts.REQUIREMENTS_STR: consts.REQUIREMENTS_DEFAULT,
                consts.SHOW_LICENSE_STR: None,
                consts.BY_MODULE_STR: False,
                consts.RETURN_DATA_STR: False,
                consts.MAX_JOBS_STR: consts.MAX_JOBS_DEFAULT
            }
            test(result)

        # normal
        sys.argv = ['', consts.LICENSES_STR, tests_consts.DUMMY_PACKAGE_NAME]
        result = {
            consts.SUBCOMMAND_STR: consts.LICENSES_STR,
            consts.INPUT_STR: tests_consts.DUMMY_PACKAGE_NAME,
            consts.INPUT_TYPE_STR: consts.DEFAULT_INPUT,
            consts.DEPTH_STR: consts.DEFAULT_DEPTH,
            consts.REQUIREMENTS_STR: consts.REQUIREMENTS_DEFAULT,
            consts.SHOW_LICENSE_STR: None,
            consts.BY_MODULE_STR: False,
            consts.RETURN_DATA_STR: False,
            consts.MAX_JOBS_STR: consts.MAX_JOBS_DEFAULT
        }
        test(result)

        # defaults
        sys.argv = ['', consts.LICENSES_STR,
                    tests_consts.DUMMY_PACKAGE_NAME,
                    consts.SHOW_LICENSE_ARG_STR,
                    consts.INPUT_TYPE_ARG_STR, consts.DEFAULT_INPUT,
                    consts.REQUIREMENTS_ARG_STR, '',
                    consts.DEPTH_ARG_STR, str(consts.DEFAULT_DEPTH)
                    ]
        result = {
            consts.SUBCOMMAND_STR: consts.LICENSES_STR,
            consts.INPUT_STR: tests_consts.DUMMY_PACKAGE_NAME,
            consts.INPUT_TYPE_STR: consts.DEFAULT_INPUT,
            consts.DEPTH_STR: consts.DEFAULT_DEPTH,
            consts.REQUIREMENTS_STR: '',
            consts.SHOW_LICENSE_STR: [],
            consts.BY_MODULE_STR: False,
            consts.RETURN_DATA_STR: False,
            consts.MAX_JOBS_STR: consts.MAX_JOBS_DEFAULT
        }
        test(result)

        # use all args
        num_for_test = 7
        sys.argv = ['', consts.LICENSES_STR,
                    tests_consts.DUMMY_PACKAGE_NAME,
                    consts.INPUT_TYPE_ARG_STR, consts.DEFAULT_INPUT,
                    consts.DEPTH_ARG_STR, '0',
                    consts.BY_MODULE_ARG_STR,
                    consts.RETURN_DATA_ARG_STR,
                    consts.REQUIREMENTS_ARG_STR, 'bla',
                    consts.MAX_JOBS_ARG_STR, str(num_for_test),
                    consts.SHOW_LICENSE_ARG_STR, 'license1', 'license2'
                    ]
        result = {
            consts.SUBCOMMAND_STR: consts.LICENSES_STR,
            consts.INPUT_STR: tests_consts.DUMMY_PACKAGE_NAME,
            consts.INPUT_TYPE_STR: consts.DEFAULT_INPUT,
            consts.REQUIREMENTS_STR: 'bla',
            consts.DEPTH_STR: 0,
            consts.SHOW_LICENSE_STR: ['license1', 'license2'],
            consts.BY_MODULE_STR: True,
            consts.RETURN_DATA_STR: True,
            consts.MAX_JOBS_STR: num_for_test
        }
        test(result)

        # different order
        sys.argv = ['', consts.LICENSES_STR,
                    consts.INPUT_TYPE_ARG_STR, consts.DEFAULT_INPUT,
                    tests_consts.DUMMY_PACKAGE_NAME,
                    consts.REQUIREMENTS_ARG_STR, 'bla',
                    consts.SHOW_LICENSE_ARG_STR, 'license1', 'license2',
                    consts.RETURN_DATA_ARG_STR,
                    consts.DEPTH_ARG_STR, '1',
                    consts.MAX_JOBS_ARG_STR, str(num_for_test),
                    consts.BY_MODULE_ARG_STR
                    ]
        result = {
            consts.SUBCOMMAND_STR: consts.LICENSES_STR,
            consts.INPUT_STR: tests_consts.DUMMY_PACKAGE_NAME,
            consts.INPUT_TYPE_STR: consts.DEFAULT_INPUT,
            consts.DEPTH_STR: 1,
            consts.REQUIREMENTS_STR: 'bla',
            consts.SHOW_LICENSE_STR: ['license1', 'license2'],
            consts.BY_MODULE_STR: True,
            consts.RETURN_DATA_STR: True,
            consts.MAX_JOBS_STR: num_for_test
        }
        test(result)

        # check all input types and sources
        for input_type in deppy.INPUTS:
            sys.argv = ['', consts.LICENSES_STR,
                        tests_consts.DUMMY_PACKAGE_NAME,
                        consts.INPUT_TYPE_ARG_STR, input_type,
                        ]
            result = {
                consts.SUBCOMMAND_STR: consts.LICENSES_STR,
                consts.INPUT_STR: tests_consts.DUMMY_PACKAGE_NAME,
                consts.INPUT_TYPE_STR: input_type,
                consts.DEPTH_STR: consts.DEFAULT_DEPTH,
                consts.REQUIREMENTS_STR: consts.REQUIREMENTS_DEFAULT,
                consts.SHOW_LICENSE_STR: None,
                consts.BY_MODULE_STR: False,
                consts.RETURN_DATA_STR: False,
                consts.MAX_JOBS_STR: consts.MAX_JOBS_DEFAULT
            }
            test(result)

        # normal
        sys.argv = ['', consts.SHOWPACK_STR, tests_consts.DUMMY_PACKAGE_NAME]
        result = {
            consts.SUBCOMMAND_STR: consts.SHOWPACK_STR,
            consts.INPUT_STR: tests_consts.DUMMY_PACKAGE_NAME,
            consts.DEPTH_STR: consts.DEFAULT_DEPTH,
            consts.VERSIONS_STR: False,
            consts.SHOW_LICENSE_STR: None,
            consts.HOMEPAGE_STR: False,
            consts.SUMMARY_STR: False,
            consts.RETURN_DATA_STR: False,
            consts.MAX_JOBS_STR: consts.MAX_JOBS_DEFAULT
        }
        test(result)

        # all args
        sys.argv = ['', consts.SHOWPACK_STR,
                    tests_consts.DUMMY_PACKAGE_NAME,
                    consts.DEPTH_ARG_STR, str(num_for_test + 1),
                    consts.VERSIONS_ARG_STR,
                    consts.HOMEPAGE_ARG_STR,
                    consts.SUMMARY_ARG_STR,
                    consts.RETURN_DATA_ARG_STR,
                    consts.MAX_JOBS_ARG_STR, str(num_for_test),
                    consts.SHOW_LICENSE_ARG_STR
                    ]
        result = {
            consts.SUBCOMMAND_STR: consts.SHOWPACK_STR,
            consts.INPUT_STR: tests_consts.DUMMY_PACKAGE_NAME,
            consts.DEPTH_STR: num_for_test + 1,
            consts.VERSIONS_STR: True,
            consts.SHOW_LICENSE_STR: [],
            consts.HOMEPAGE_STR: True,
            consts.SUMMARY_STR: True,
            consts.RETURN_DATA_STR: True,
            consts.MAX_JOBS_STR: num_for_test
        }
        test(result)

        # different order
        sys.argv = ['', consts.SHOWPACK_STR,
                    consts.DEPTH_ARG_STR, str(num_for_test + 1),
                    consts.RETURN_DATA_ARG_STR,
                    consts.VERSIONS_ARG_STR,
                    consts.HOMEPAGE_ARG_STR,
                    consts.SHOW_LICENSE_ARG_STR, 'license',
                    consts.SUMMARY_ARG_STR,
                    consts.MAX_JOBS_ARG_STR, str(num_for_test),
                    tests_consts.DUMMY_PACKAGE_NAME,
                    ]
        result = {
            consts.SUBCOMMAND_STR: consts.SHOWPACK_STR,
            consts.INPUT_STR: tests_consts.DUMMY_PACKAGE_NAME,
            consts.DEPTH_STR: num_for_test + 1,
            consts.VERSIONS_STR: True,
            consts.SHOW_LICENSE_STR: ['license'],
            consts.HOMEPAGE_STR: True,
            consts.SUMMARY_STR: True,
            consts.RETURN_DATA_STR: True,
            consts.MAX_JOBS_STR: num_for_test
        }
        test(result)

        # illegal inputs & help messages
        bad_inputs_and_help_args = [
            ['', consts.SEEKUP_STR,
             consts.INPUT_TYPE_ARG_STR, consts.DEFAULT_INPUT,
             consts.SHOW_LICENSE_ARG_STR,
             tests_consts.DUMMY_PACKAGE_NAME,
             consts.RETURN_DATA_ARG_STR,
             consts.MAX_JOBS_ARG_STR, str(num_for_test),
             consts.BY_MODULE_ARG_STR
             ],
            ['', consts.SEEKUP_STR,
             tests_consts.DUMMY_PACKAGE_NAME, tests_consts.DUMMY_PACKAGE_NAME,
             consts.BY_MODULE_ARG_STR],
            ['', consts.SEEKUP_STR, tests_consts.DUMMY_PACKAGE_NAME, 'bla'],
            ['', consts.SEEKUP_STR, tests_consts.DUMMY_PACKAGE_NAME, '-b'],
            ['', consts.SEEKUP_STR],
            ['', consts.SEEKUP_STR, '-h'],
            ['', consts.SEEKUP_STR, '--help'],

            ['', consts.LICENSES_STR,
             consts.INPUT_TYPE_ARG_STR, consts.DEFAULT_INPUT,
             consts.SHOW_LICENSE_ARG_STR,
             tests_consts.DUMMY_PACKAGE_NAME,
             consts.RETURN_DATA_ARG_STR,
             consts.DEPTH_ARG_STR,
             consts.MAX_JOBS_ARG_STR, str(num_for_test),
             consts.BY_MODULE_ARG_STR
             ],
            ['', consts.LICENSES_STR,
             tests_consts.DUMMY_PACKAGE_NAME, tests_consts.DUMMY_PACKAGE_NAME,
             consts.BY_MODULE_ARG_STR],
            ['', consts.LICENSES_STR, tests_consts.DUMMY_PACKAGE_NAME, 'bla'],
            ['', consts.LICENSES_STR, tests_consts.DUMMY_PACKAGE_NAME, '-b'],
            ['', consts.LICENSES_STR],
            ['', consts.LICENSES_STR, '-h'],
            ['', consts.LICENSES_STR, '--help'],

            ['', consts.SHOWPACK_STR,
             consts.DEPTH_ARG_STR, str(num_for_test + 1),
             consts.RETURN_DATA_ARG_STR,
             consts.VERSIONS_ARG_STR,
             consts.HOMEPAGE_ARG_STR,
             consts.SHOW_LICENSE_ARG_STR,
             consts.SUMMARY_ARG_STR,
             consts.MAX_JOBS_ARG_STR,
             tests_consts.DUMMY_PACKAGE_NAME,
             ],
            ['', consts.SHOWPACK_STR,
             tests_consts.DUMMY_PACKAGE_NAME, tests_consts.DUMMY_PACKAGE_NAME,
             consts.SUMMARY_ARG_STR],
            ['', consts.SHOWPACK_STR, tests_consts.DUMMY_PACKAGE_NAME, 'bla'],
            ['', consts.SHOWPACK_STR, tests_consts.DUMMY_PACKAGE_NAME, '-b'],
            ['', consts.SHOWPACK_STR],
            ['', consts.SHOWPACK_STR, '-h'],
            ['', consts.SHOWPACK_STR, '--help'],

            ['', 'bla'],
            ['', ''],
            [''],
            ['', '-h'],
            ['', '--help']
        ]

        # make sure exception is thrown
        for input_args in bad_inputs_and_help_args:
            sys.argv = input_args
            try:
                tested_func()
            except AttributeError:
                pass
            else:
                self.assertTrue(False)

        sys.argv = []
        try:
            tested_func()
        except IndexError:
            pass
        else:
            self.assertTrue(False)

        sys.argv = None
        try:
            tested_func()
        except TypeError:
            pass
        else:
            self.assertTrue(False)

    def test_get_dependencies_from_path(self):

        def test(expected):
            self._generic_test(deppy._get_dependencies_from_path,
                               expected, {
                                   consts.INPUT_STR: '',
                                   consts.MAX_JOBS_STR: consts.MAX_JOBS_DEFAULT
                               })

        mocked_find_name = deppy._find_files_in_path.__name__

        # check error case
        with mock.patch.object(
                deppy, mocked_find_name, return_value=[]):
            test(expected=consts.ERROR_MESSAGE_NO_SETUP)

        # check that parallel is called with correct args
        paths = ['a', 'b', 'c']
        func_kwargs = {
            consts.INPUT_STR: 'bla',
            consts.MAX_JOBS_STR: 7
        }

        def mock_parallel(func, args, threads_num=None):
            return cmp_elements(func, dependencies.get_from_file) \
                   and cmp_elements(args, paths) \
                   and threads_num in [None, func_kwargs[consts.MAX_JOBS_STR]]

        deppy._parallel = mock_parallel

        with mock.patch.object(
                deppy, mocked_find_name, return_value=paths):
            self.assertTrue(deppy._get_dependencies_from_path(func_kwargs))

    def test_get_dependencies_from_url(self):

        def test(expected):
            self._generic_test(deppy._get_dependencies_from_url,
                               expected, {consts.INPUT_STR: ''})

        mocked_name = dependencies.get_by_url.__name__

        with mock.patch.object(deppy.dependencies, mocked_name,
                               return_value=None):
            test(expected=consts.ERROR_MESSAGE_URL)

        with mock.patch.object(deppy.dependencies, mocked_name,
                               return_value=([], '')):
            test(expected=[([], '')])

        with mock.patch.object(deppy.dependencies, mocked_name,
                               return_value=([('dep', '7', '==')], 'name')):
            test(expected=[([('dep', '7', '==')], 'name')])

        mock_return = (
            [
                ('dep1', '7', '=='),
                ('dep2', '', '')
            ],
            'name'
        )
        with mock.patch.object(deppy.dependencies, mocked_name,
                               return_value=mock_return):
            test(expected=[
                (
                    [
                        ('dep1', '7', '=='),
                        ('dep2', '', '')
                    ],
                    'name'
                )
            ])

    def test_get_dependencies_by_package_name(self):

        def test(expected):
            self._generic_test(deppy._get_dependencies_by_package_name,
                               expected,
                               {
                                   consts.INPUT_STR: 'name',
                                   consts.DEPTH_STR: ''
                               })

        mocked_name = dependencies.get_for_package.__name__

        with mock.patch.object(dependencies, mocked_name,
                               return_value=None):
            test(expected=consts.ERROR_MESSAGE_BUILDING_DEPTREE)

        with mock.patch.object(dependencies, mocked_name,
                               return_value=(None, 'name')):
            test(expected=consts.ERROR_MESSAGE_NO_PACKAGE_INSTALLED.format(
                'name'))

        with mock.patch.object(dependencies, mocked_name,
                               return_value=([], 'name')):
            test(expected=[([], 'name')])

        with mock.patch.object(deppy.dependencies, mocked_name,
                               return_value=([('dep', '7', '==')], 'name')):
            test(expected=[([('dep', '7', '==')], 'name')])

        mock_return = (
            [
                ('dep1', '7', '=='),
                ('dep2', '', '')
            ],
            'name'
        )
        with mock.patch.object(deppy.dependencies, mocked_name,
                               return_value=mock_return):
            test(expected=[(
                [
                    ('dep1', '7', '=='),
                    ('dep2', '', '')
                ],
                'name'
            )])

    def test_dependencies_tree_to_string(self):

        test_resources_path = os.path.join(
            tests_consts.RESOURCES_PATH, 'to_string', 'dependencies_tree')

        def test(expected_result, *tested_func_args):
            self._generic_test(deppy._dependencies_tree_to_string,
                               expected_result, *tested_func_args)

        expected = ''
        func_args = [{}, 'a']
        test(expected, *func_args)

        expected = ''
        func_args = [{'a': {}}, 'b']
        test(expected, *func_args)

        expected = '\nPackage:  a\n'
        func_args = [{'a': {}}, 'a']
        test(expected, *func_args)

        with open(os.path.join(test_resources_path, 'output1.txt'), 'r') \
                as output_file:
            with open(os.path.join(test_resources_path, 'input1.txt'), 'r') \
                    as input_file:
                expected = output_file.read()
                func_args = [
                    json.loads(input_file.read()),
                    'cloudify-plugins-common'
                ]
                test(expected, *func_args)

        with open(os.path.join(test_resources_path, 'output2.txt'), 'r') \
                as output_file:
            with open(os.path.join(test_resources_path, 'input2.txt'), 'r') \
                    as input_file:
                expected = output_file.read()
                func_args = [
                    json.loads(input_file.read()),
                    'cloudify-plugins-common'
                ]
                test(expected, *func_args)

        with open(os.path.join(test_resources_path, 'output3.txt'), 'r') \
                as output_file:
            with open(os.path.join(test_resources_path, 'input3.txt'), 'r') \
                    as input_file:
                expected = output_file.read()
                func_args = [
                    json.loads(input_file.read()),
                    'cloudify-plugins-common'
                ]
                test(expected, *func_args)

        with open(os.path.join(test_resources_path, 'input3.txt'), 'r') \
                as input_file:
            expected = ''
            func_args = [json.loads(input_file.read()), 'a']
            test(expected, *func_args)

    def test_illegitimate_licenses_to_string(self):

        test_resources_path = os.path.join(
            tests_consts.RESOURCES_PATH, 'to_string', 'illegitimate_licenses')

        def test(expected_result, *tested_func_args):
            self._generic_test(deppy._illegitimate_licenses_to_string,
                               expected_result, *tested_func_args)

        expected = ''
        func_args = [None]
        test(expected, *func_args)

        expected = ''
        func_args = [{}]
        test(expected, *func_args)

        with open(os.path.join(test_resources_path, 'output1.txt'), 'r') \
                as output_file:
            expected = output_file.read()
            func_args = [{'package1': 'license1'}]
            test(expected, *func_args)

        with open(os.path.join(test_resources_path, 'output2.txt'), 'r') \
                as output_file:
            expected = output_file.read()
            func_args = [{
                'package1': 'license1',
                'package2': 'license2'
            }]
            test(expected, *func_args)

        with open(os.path.join(test_resources_path, 'output3.txt'), 'r') \
                as output_file:
            expected = output_file.read()
            func_args = [{
                'package1': 'license1',
                'package2': 'license2',
                'package3': 'license1'
            }]
            test(expected, *func_args)

    def test_seekup_to_string_by_module(self):

        test_resources_path = os.path.join(
            tests_consts.RESOURCES_PATH, 'to_string', 'seekup', 'by_module')

        def test(expected_result, *tested_func_args):
            self._generic_test(deppy._seekup_to_string_by_module,
                               expected_result, *tested_func_args)

        expected = ''
        func_args = [[], {}, None]
        test(expected, *func_args)

        expected = ''
        func_args = [
            [{
                consts.PACKAGE_KEY: 'package1',
                consts.REQUIRE_KEY: '==3',
                consts.NEW_VERS_KEY: ['4', '5']
            }],
            {},
            {'package1': 'license1'}
        ]
        test(expected, *func_args)

        expected = '\nIn module:     module1\n' \
                   '     package1==3  -->  [\'4\', \'5\']\n'
        func_args = [
            [{
                consts.PACKAGE_KEY: 'package1',
                consts.REQUIRE_KEY: '==3',
                consts.NEW_VERS_KEY: ['4', '5']
            }],
            {
                'module1': [('package1', '==3')]
            },
            None
        ]
        test(expected, *func_args)

        expected = '\nIn module:     module1\n' \
                   '     package1==3  -->  [\'4\', \'5\']\n' \
                   '        LICENSE:  license1\n'
        func_args = [
            [{
                consts.PACKAGE_KEY: 'package1',
                consts.REQUIRE_KEY: '==3',
                consts.NEW_VERS_KEY: ['4', '5']
            }],
            {
                'module1': [('package1', '==3')]
            },
            {'package1': 'license1'}
        ]
        test(expected, *func_args)

        expected = ''
        func_args = [
            [{
                consts.PACKAGE_KEY: 'package1',
                consts.REQUIRE_KEY: '==3',
                consts.NEW_VERS_KEY: ['4', '5']
            }],
            {
                'module1': [('package2', '==3')]
            },
            {'package1': 'license1'}
        ]
        test(expected, *func_args)

        with open(os.path.join(test_resources_path, 'output1.txt'), 'r') \
                as output_file:
            results_dict = {
                'modules': {
                    'cloudify-plugins-common': [
                        (
                            'bottle',
                            '==0.12.7'
                        ),
                        (
                            'networkx',
                            '==1.8.1'
                        ),
                        (
                            'cloudify-rest-client',
                            '==3.3.1'
                        ),
                        (
                            'proxy-tools',
                            '==0.1.0'
                        ),
                        (
                            'jinja2',
                            '==2.7.2'
                        ),
                        (
                            'pika',
                            '==0.9.14'
                        )
                    ]
                },
                'results': [
                    {
                        'require': '==0.12.7',
                        'new_versions_available': [
                            '0.12.9',
                            '0.12.8'
                        ],
                        'package': 'bottle'
                    },
                    {
                        'require': '==3.3.1',
                        'new_versions_available': [
                            '3.4a3',
                            '3.4a2',
                            '3.4a1',
                            '3.3a4',
                            '3.3a5',
                            '3.3a6',
                            '3.3a7',
                            '3.3a1',
                            '3.3a2',
                            '3.3rc1'
                        ],
                        'package': 'cloudify-rest-client'
                    },
                    {
                        'require': '==2.7.2',
                        'new_versions_available': [
                            '2.8',
                            '2.7.3'
                        ],
                        'package': 'jinja2'
                    },
                    {
                        'require': '==1.8.1',
                        'new_versions_available': [
                            '1.9',
                            '1.10rc2',
                            '1.11rc1',
                            '1.11rc2',
                            '1.10',
                            '1.11',
                            '1.9rc1',
                            '1.9.1',
                            '1.8rc1'
                        ],
                        'package': 'networkx'
                    },
                    {
                        'require': '==0.9.14',
                        'new_versions_available': [
                            '0.10.0',
                            '0.10.0b1',
                            '0.10.0b2'
                        ],
                        'package': 'pika'
                    },
                    {
                        'require': '==0.1.0',
                        'new_versions_available': [],
                        'package': 'proxy-tools'
                    }
                ]
            }
            expected = output_file.read()
            func_args = [
                results_dict[consts.RESULTS_KEY],
                results_dict[consts.MODULES_KEY]
            ]
            test(expected, *func_args)

        with open(os.path.join(test_resources_path, 'output2.txt'), 'r') \
                as output_file:
            results_dict = {
                'modules': {
                    'cloudify-plugins-common': [
                        (
                            'bottle',
                            '==0.12.7'
                        ),
                        (
                            'networkx',
                            '==1.8.1'
                        ),
                        (
                            'cloudify-rest-client',
                            '==3.3.1'
                        ),
                        (
                            'proxy-tools',
                            '==0.1.0'
                        ),
                        (
                            'jinja2',
                            '==2.7.2'
                        ),
                        (
                            'pika',
                            '==0.9.14'
                        )
                    ]
                },
                'results': [
                    {
                        'require': '==0.12.7',
                        'new_versions_available': [
                            '0.12.9',
                            '0.12.8'
                        ],
                        'package': 'bottle'
                    },
                    {
                        'require': '==3.3.1',
                        'new_versions_available': [
                            '3.4a3',
                            '3.4a2',
                            '3.4a1',
                            '3.3a4',
                            '3.3a5',
                            '3.3a6',
                            '3.3a7',
                            '3.3a1',
                            '3.3a2',
                            '3.3rc1'
                        ],
                        'package': 'cloudify-rest-client'
                    },
                    {
                        'require': '==2.7.2',
                        'new_versions_available': [
                            '2.8',
                            '2.7.3'
                        ],
                        'package': 'jinja2'
                    },
                    {
                        'require': '==1.8.1',
                        'new_versions_available': [
                            '1.9',
                            '1.10rc2',
                            '1.11rc1',
                            '1.11rc2',
                            '1.10',
                            '1.11',
                            '1.9rc1',
                            '1.9.1',
                            '1.8rc1'
                        ],
                        'package': 'networkx'
                    },
                    {
                        'require': '==0.9.14',
                        'new_versions_available': [
                            '0.10.0',
                            '0.10.0b1',
                            '0.10.0b2'
                        ],
                        'package': 'pika'
                    },
                    {
                        'require': '==0.1.0',
                        'new_versions_available': [],
                        'package': 'proxy-tools'
                    }
                ],
                'license': {
                    'bottle': 'MIT',
                    'proxy-tools': 'MIT',
                    'jinja2': 'BSD',
                    'networkx': 'BSD',
                    'cloudify-rest-client': 'LICENSE',
                    'pika': 'BSD'
                }
            }
            expected = output_file.read()
            func_args = [
                results_dict[consts.RESULTS_KEY],
                results_dict[consts.MODULES_KEY],
                results_dict[consts.LICENSE_KEY]
            ]
            test(expected, *func_args)

    def test_seekup_to_string_by_dependency(self):

        test_resources_path = \
            os.path.join(tests_consts.RESOURCES_PATH,
                         'to_string', 'seekup', 'by_dependency')

        def test(expected_result, *tested_func_args):
            self._generic_test(deppy._seekup_to_string_by_dependency,
                               expected_result, *tested_func_args)

        expected = ''
        func_args = [[], {}, None]
        test(expected, *func_args)

        try:
            func_args = [
                [{
                    consts.PACKAGE_KEY: 'package1',
                    consts.REQUIRE_KEY: '==3',
                    consts.NEW_VERS_KEY: ['4', '5']
                }],
                {},
                {'package1': 'license1'}
            ]
            test(expected, *func_args)
        except KeyError:
            pass
        else:
            self.assertTrue(False)

        expected = '\npackage1==3  -->  [\'4\', \'5\']' \
                   '\n     In the following modules:\n' \
                   '             module1\n'
        func_args = [
            [{
                consts.PACKAGE_KEY: 'package1',
                consts.REQUIRE_KEY: '==3',
                consts.NEW_VERS_KEY: ['4', '5']
            }],
            {
                'package1==3': ['module1']
            },
            None
        ]
        test(expected, *func_args)

        expected = '\npackage1==3  -->  [\'4\', \'5\']' \
                   '        LICENSE:  license1' \
                   '\n     In the following modules:\n' \
                   '             module1\n'
        func_args = [
            [{
                consts.PACKAGE_KEY: 'package1',
                consts.REQUIRE_KEY: '==3',
                consts.NEW_VERS_KEY: ['4', '5']
            }],
            {
                'package1==3': ['module1']
            },
            {'package1': 'license1'}
        ]
        test(expected, *func_args)

        expected = ''
        func_args = [
            [],
            {
                'package1==3': ['module1']
            },
            {'package1': 'license1'}
        ]
        test(expected, *func_args)

        with open(os.path.join(test_resources_path, 'output1.txt'), 'r') \
                as output_file:
            results_dict = {
                'modules': {
                    'jinja2==2.7.2': [
                        'cloudify-plugins-common'
                    ],
                    'pika==0.9.14': [
                        'cloudify-plugins-common'
                    ],
                    'networkx==1.8.1': [
                        'cloudify-plugins-common'
                    ],
                    'proxy-tools==0.1.0': [
                        'cloudify-plugins-common'
                    ],
                    'bottle==0.12.7': [
                        'cloudify-plugins-common'
                    ],
                    'cloudify-rest-client==3.3.1': [
                        'cloudify-plugins-common'
                    ]
                },
                'results': [
                    {
                        'require': '==0.12.7',
                        'new_versions_available': [
                            '0.12.9',
                            '0.12.8'
                        ],
                        'package': 'bottle'
                    },
                    {
                        'require': '==3.3.1',
                        'new_versions_available': [
                            '3.4a3',
                            '3.4a2',
                            '3.4a1',
                            '3.3a4',
                            '3.3a5',
                            '3.3a6',
                            '3.3a7',
                            '3.3a1',
                            '3.3a2',
                            '3.3rc1'
                        ],
                        'package': 'cloudify-rest-client'
                    },
                    {
                        'require': '==2.7.2',
                        'new_versions_available': [
                            '2.8',
                            '2.7.3'
                        ],
                        'package': 'jinja2'
                    },
                    {
                        'require': '==1.8.1',
                        'new_versions_available': [
                            '1.9',
                            '1.10rc2',
                            '1.11rc1',
                            '1.11rc2',
                            '1.10',
                            '1.11',
                            '1.9rc1',
                            '1.9.1',
                            '1.8rc1'
                        ],
                        'package': 'networkx'
                    },
                    {
                        'require': '==0.9.14',
                        'new_versions_available': [
                            '0.10.0',
                            '0.10.0b1',
                            '0.10.0b2'
                        ],
                        'package': 'pika'
                    },
                    {
                        'require': '==0.1.0',
                        'new_versions_available': [],
                        'package': 'proxy-tools'
                    }
                ]
            }
            expected = output_file.read()
            func_args = [
                results_dict[consts.RESULTS_KEY],
                results_dict[consts.MODULES_KEY]
            ]
            test(expected, *func_args)

        with open(os.path.join(test_resources_path, 'output2.txt'), 'r') \
                as output_file:
            results_dict = {
                'modules': {
                    'jinja2==2.7.2': [
                        'cloudify-plugins-common'
                    ],
                    'pika==0.9.14': [
                        'cloudify-plugins-common'
                    ],
                    'networkx==1.8.1': [
                        'cloudify-plugins-common'
                    ],
                    'proxy-tools==0.1.0': [
                        'cloudify-plugins-common'
                    ],
                    'bottle==0.12.7': [
                        'cloudify-plugins-common'
                    ],
                    'cloudify-rest-client==3.3.1': [
                        'cloudify-plugins-common'
                    ]
                },
                'results': [
                    {
                        'require': '==0.12.7',
                        'new_versions_available': [
                            '0.12.9',
                            '0.12.8'
                        ],
                        'package': 'bottle'
                    },
                    {
                        'require': '==3.3.1',
                        'new_versions_available': [
                            '3.4a3',
                            '3.4a2',
                            '3.4a1',
                            '3.3a4',
                            '3.3a5',
                            '3.3a6',
                            '3.3a7',
                            '3.3a1',
                            '3.3a2',
                            '3.3rc1'
                        ],
                        'package': 'cloudify-rest-client'
                    },
                    {
                        'require': '==2.7.2',
                        'new_versions_available': [
                            '2.8',
                            '2.7.3'
                        ],
                        'package': 'jinja2'
                    },
                    {
                        'require': '==1.8.1',
                        'new_versions_available': [
                            '1.9',
                            '1.10rc2',
                            '1.11rc1',
                            '1.11rc2',
                            '1.10',
                            '1.11',
                            '1.9rc1',
                            '1.9.1',
                            '1.8rc1'
                        ],
                        'package': 'networkx'
                    },
                    {
                        'require': '==0.9.14',
                        'new_versions_available': [
                            '0.10.0',
                            '0.10.0b1',
                            '0.10.0b2'
                        ],
                        'package': 'pika'
                    },
                    {
                        'require': '==0.1.0',
                        'new_versions_available': [],
                        'package': 'proxy-tools'
                    }
                ],
                'license': {
                    'bottle': 'MIT',
                    'proxy-tools': 'MIT',
                    'jinja2': 'BSD',
                    'networkx': 'BSD',
                    'cloudify-rest-client': 'LICENSE',
                    'pika': 'BSD'
                }
            }
            expected = output_file.read()
            func_args = [
                results_dict[consts.RESULTS_KEY],
                results_dict[consts.MODULES_KEY],
                results_dict[consts.LICENSE_KEY]
            ]
            test(expected, *func_args)

    def test_licenses_to_string(self):

        def test(expected_result, *tested_func_args):
            self._generic_test(deppy._licenses_to_string,
                               expected_result, *tested_func_args)

        expected = ''
        func_args = [{}, True]
        test(expected, *func_args)

        expected = ''
        func_args = [{}, False]
        test(expected, *func_args)

        expected = 'Package: a  -->  License: [\'a1\', \'a2\']\n' \
                   'Package: b  -->  License: [\'b1\', \'b2\']\n'
        func_args = [
            {
                'a': ['a1', 'a2'],
                'b': ['b1', 'b2']
            },
            True
        ]
        test(expected, *func_args)

        expected = 'License: a  -->  Packages: [\'a1\', \'a2\']\n' \
                   'License: b  -->  Packages: [\'b1\', \'b2\']\n'
        func_args = [
            {
                'a': ['a1', 'a2'],
                'b': ['b1', 'b2']
            },
            False
        ]
        test(expected, *func_args)

    def test_licenses(self):

        def test_error(expected, **func_kwargs):
            self.assertTrue(cmp_elements(
                expected, deppy.licenses(**func_kwargs)))

        def test(expected, **func_kwargs):
            self.assertTrue(cmp_elements(
                expected, yaml.safe_load(deppy.licenses(**func_kwargs))
            ))

        def mock_input(args):
            return args['mock_input_result']

        def mock_parallel(_, packages, __):
            return [
                (package,
                 [package + '_1', package + '_2'],
                 consts.UNKNOWN
                 if package in ['package4', 'package6']
                 else package[0] + '_license')
                for package in packages
                ] if kwargs['map_return_value'] else []

        deppy.INPUTS['_mock_for_test'] = mock_input
        deppy._parallel = mock_parallel

        dependencies_failure_message = 'some_failure_message'

        kwargs = {
            consts.MAX_JOBS_STR: consts.MAX_JOBS_DEFAULT,
            consts.INPUT_TYPE_STR: '_mock_for_test',
            consts.RETURN_DATA_STR: True,
            consts.BY_MODULE_STR: False,
            consts.SHOW_LICENSE_STR: None,
            consts.INPUT_STR: None,
            'map_return_value': False,
            'mock_input_result': [
                ([('a1', '2', '=='), ('a2', '1', '>=')], 'package1', ''),
                ([('a3', '1', '=='), ('b1', '', '')], 'package4', 'lic4'),
                ([('b2', '2', '>'), ('a3', '', '')],
                 'package6', consts.UNKNOWN),
                ([('c1', '2', '>'), ('b2', '1', '==')], 'package8', ''),
                ([], 'a3', '')
            ]
        }

        licenses_to_modules = {
            'a_license': ['a1', 'a3', 'a2'],
            'p_license': ['package8', 'package1'],
            'c_license': ['c1'],
            'b_license': ['b1', 'b2'],
            'lic4': ['package4'],
            consts.UNKNOWN: ['package6']
        }

        modules_to_licenses = {
            'a1': ['a_license'],
            'a2': ['a_license'],
            'a3': ['a_license'],
            'b1': ['b_license'],
            'b2': ['b_license'],
            'c1': ['c_license'],
            'package1': ['p_license'],
            'package4': ['lic4'],
            'package6': [consts.UNKNOWN],
            'package8': ['p_license']
        }

        test_error(expected=consts.ERROR_MESSAGE_NO_INPUT)

        test_error(expected=consts.ERROR_MESSAGE_ILLEGAL_INPUT_TYPE.format(
            deppy.INPUTS.keys()), input_type='', input='')

        test_error(expected=dependencies_failure_message,
                   input_type='_mock_for_test',
                   input='', mock_input_result=dependencies_failure_message)

        test(expected={
            consts.LICENSE_KEY: {},
            consts.ILLEGITIMATE_LICENSES_KEY: {}
        },
             **kwargs)

        kwargs['map_return_value'] = True

        test(expected={
            consts.LICENSE_KEY: licenses_to_modules,
            consts.ILLEGITIMATE_LICENSES_KEY: {}
        },
            **kwargs)

        kwargs[consts.BY_MODULE_STR] = True

        test(expected={
            consts.LICENSE_KEY: modules_to_licenses,
            consts.ILLEGITIMATE_LICENSES_KEY: {}
        },
            **kwargs)

        kwargs[consts.BY_MODULE_STR] = False
        kwargs[consts.SHOW_LICENSE_STR] = ['p_license', 'c_license', 'lic4']

        test(expected={
            consts.LICENSE_KEY: licenses_to_modules,
            consts.ILLEGITIMATE_LICENSES_KEY: {
                'a_license': ['a1', 'a3', 'a2'],
                'b_license': ['b1', 'b2'],
                consts.UNKNOWN: ['package6']
            }
        },
            **kwargs)

        kwargs[consts.BY_MODULE_STR] = True

        test(expected={
            consts.LICENSE_KEY: modules_to_licenses,
            consts.ILLEGITIMATE_LICENSES_KEY: {
                'a1': ['a_license'],
                'a2': ['a_license'],
                'a3': ['a_license'],
                'b1': ['b_license'],
                'b2': ['b_license'],
                'package6': [consts.UNKNOWN]
            }
        },
            **kwargs)

    def test_show_package(self):

        def test(expected, **func_kwargs):
            self.assertTrue(cmp_elements(
                expected, deppy.show_package(**func_kwargs)))

        kwargs = {
            consts.INPUT_STR: '',
            consts.DEPTH_STR: consts.DEFAULT_DEPTH,
            consts.SHOW_LICENSE_STR: None,
            consts.HOMEPAGE_STR: False,
            consts.SUMMARY_STR: False,
            consts.VERSIONS_STR: False,
            consts.RETURN_DATA_STR: True,
            consts.MAX_JOBS_STR: consts.MAX_JOBS_DEFAULT
        }
        with mock.patch.object(dependencies, 'build_tree',
                               return_value=None):
            test(expected=consts.ERROR_MESSAGE_BUILDING_DEPTREE, **kwargs)

        with mock.patch.object(dependencies, 'build_tree',
                               return_value={}):
            test(
                expected=json.dumps(
                    {'dependencies_tree': {}}, indent=consts.TAB_SIZE),
                **kwargs
            )

        with mock.patch.object(dependencies, 'build_tree',
                               return_value={'package1': []}):
            test(
                expected=json.dumps(
                    {'dependencies_tree': {
                        'package1': {consts.DEPENDENCIES_KEY: []}
                    }},
                    indent=consts.TAB_SIZE),
                **kwargs
            )

        with mock.patch.object(dependencies, 'build_tree',
                               return_value={'package1': [], 'package2': []}):
            test(
                expected=json.dumps(
                    {'dependencies_tree': {
                        'package1': {consts.DEPENDENCIES_KEY: []},
                        'package2': {consts.DEPENDENCIES_KEY: []}
                    }},
                    indent=consts.TAB_SIZE),
                **kwargs
            )

        mock_return = {
            'package1': [{
                consts.PACKAGE_KEY: 'package2',
                consts.REQUIRE_KEY: '==7'
            }],
            'package2': []
        }
        with mock.patch.object(dependencies, 'build_tree',
                               return_value=mock_return):
            test(
                expected=json.dumps(
                    {'dependencies_tree': {
                        'package1': {consts.DEPENDENCIES_KEY: [{
                            consts.PACKAGE_KEY: 'package2',
                            consts.REQUIRE_KEY: '==7'
                        }]},
                        'package2': {consts.DEPENDENCIES_KEY: []}
                    }},
                    indent=consts.TAB_SIZE),
                **kwargs
            )

        mock_return = {
            'package1': [{
                consts.PACKAGE_KEY: 'package2',
                consts.REQUIRE_KEY: '==7'
            }]}
        with mock.patch.object(dependencies, 'build_tree',
                               return_value=mock_return):
            test(
                expected=json.dumps(
                    {'dependencies_tree': {
                        'package1': {consts.DEPENDENCIES_KEY: [{
                            consts.PACKAGE_KEY: 'package2',
                            consts.REQUIRE_KEY: '==7'
                        }]}
                    }},
                    indent=consts.TAB_SIZE),
                **kwargs
            )

        mock_return = {
            'package1': [
                {
                    consts.PACKAGE_KEY: 'package2',
                    consts.REQUIRE_KEY: '==7'
                },
                {
                    consts.PACKAGE_KEY: 'package3',
                    consts.REQUIRE_KEY: '>5'
                }
            ],
            'package2': [],
            'package3': []
        }
        with mock.patch.object(dependencies, 'build_tree',
                               return_value=mock_return):
            test(
                expected=json.dumps(
                    {'dependencies_tree': {
                        'package1': {consts.DEPENDENCIES_KEY: [
                            {
                                consts.PACKAGE_KEY: 'package2',
                                consts.REQUIRE_KEY: '==7'
                            },
                            {
                                consts.PACKAGE_KEY: 'package3',
                                consts.REQUIRE_KEY: '>5'
                            }
                        ]},
                        'package2': {consts.DEPENDENCIES_KEY: []},
                        'package3': {consts.DEPENDENCIES_KEY: []}
                    }},
                    indent=consts.TAB_SIZE),
                **kwargs
            )

        mock_return = {
            'package1': [
                {
                    consts.PACKAGE_KEY: 'package2',
                    consts.REQUIRE_KEY: '==7'
                },
                {
                    consts.PACKAGE_KEY: 'package3',
                    consts.REQUIRE_KEY: '>5'
                }
            ],
            'package2': [
                {
                    consts.PACKAGE_KEY: 'package4',
                    consts.REQUIRE_KEY: ''
                },
            ],
            'package3': [],
            'package4': []
        }
        with mock.patch.object(dependencies, 'build_tree',
                               return_value=mock_return):
            test(
                expected=json.dumps(
                    {'dependencies_tree': {
                        'package1': {consts.DEPENDENCIES_KEY: [
                            {
                                consts.PACKAGE_KEY: 'package2',
                                consts.REQUIRE_KEY: '==7'
                            },
                            {
                                consts.PACKAGE_KEY: 'package3',
                                consts.REQUIRE_KEY: '>5'
                            }
                        ]},
                        'package2': {consts.DEPENDENCIES_KEY: [
                            {
                                consts.PACKAGE_KEY: 'package4',
                                consts.REQUIRE_KEY: ''
                            }
                        ]},
                        'package3': {consts.DEPENDENCIES_KEY: []},
                        'package4': {consts.DEPENDENCIES_KEY: []}
                    }},
                    indent=consts.TAB_SIZE),
                **kwargs
            )

        def mock_parallel(_, packages, __):
            result = [{
                consts.INFO_KEY: {
                    consts.NAME_KEY: package_name,
                    consts.SUMMARY_KEY: package_name + '_sum',
                    consts.HOMEPAGE_KEY: package_name + '_home',
                    consts.LICENSE_KEY: package_name + '_license'
                },
                consts.RELEASES_KEY: {
                    package_name + '_1': [],
                    package_name + '_2': []
                }
            }
                      for package_name in packages]
            return result

        deppy._parallel = mock_parallel
        kwargs[consts.SHOW_LICENSE_STR] = []

        mock_return = {
            'package1': [
                {
                    consts.PACKAGE_KEY: 'package2',
                    consts.REQUIRE_KEY: '==7'
                },
                {
                    consts.PACKAGE_KEY: 'package3',
                    consts.REQUIRE_KEY: '>5'
                }
            ],
            'package2': [
                {
                    consts.PACKAGE_KEY: 'package4',
                    consts.REQUIRE_KEY: ''
                },
            ],
            'package3': [],
            'package4': []
        }
        with mock.patch.object(dependencies, 'build_tree',
                               return_value=mock_return):
            test(
                expected=json.dumps(
                    {
                        'dependencies_tree': {
                            'package1': {
                                consts.LICENSE_KEY: 'package1_license',
                                consts.DEPENDENCIES_KEY: [
                                    {
                                        consts.PACKAGE_KEY: 'package2',
                                        consts.REQUIRE_KEY: '==7'
                                    },
                                    {
                                        consts.PACKAGE_KEY: 'package3',
                                        consts.REQUIRE_KEY: '>5'
                                    }
                                ]
                            },
                            'package2': {
                                consts.LICENSE_KEY: 'package2_license',
                                consts.DEPENDENCIES_KEY: [
                                    {
                                        consts.PACKAGE_KEY: 'package4',
                                        consts.REQUIRE_KEY: ''
                                    }
                                ]
                            },
                            'package3': {
                                consts.LICENSE_KEY: 'package3_license',
                                consts.DEPENDENCIES_KEY: []
                            },
                            'package4': {
                                consts.LICENSE_KEY: 'package4_license',
                                consts.DEPENDENCIES_KEY: []
                            }
                        },
                        consts.ILLEGITIMATE_LICENSES_KEY: {}
                    },
                    indent=consts.TAB_SIZE),
                **kwargs
            )

        kwargs[consts.SHOW_LICENSE_STR] = ['package3_license']
        mock_return = {
            'package1': [
                {
                    consts.PACKAGE_KEY: 'package2',
                    consts.REQUIRE_KEY: '==7'
                },
                {
                    consts.PACKAGE_KEY: 'package3',
                    consts.REQUIRE_KEY: '>5'
                }
            ],
            'package2': [
                {
                    consts.PACKAGE_KEY: 'package4',
                    consts.REQUIRE_KEY: ''
                },
            ],
            'package3': [],
            'package4': []
        }
        with mock.patch.object(dependencies, 'build_tree',
                               return_value=mock_return):
            test(
                expected=json.dumps(
                    {
                        'dependencies_tree': {
                            'package1': {
                                consts.LICENSE_KEY: 'package1_license',
                                consts.DEPENDENCIES_KEY: [
                                    {
                                        consts.PACKAGE_KEY: 'package2',
                                        consts.REQUIRE_KEY: '==7'
                                    },
                                    {
                                        consts.PACKAGE_KEY: 'package3',
                                        consts.REQUIRE_KEY: '>5'
                                    }
                                ]
                            },
                            'package2': {
                                consts.LICENSE_KEY: 'package2_license',
                                consts.DEPENDENCIES_KEY: [
                                    {
                                        consts.PACKAGE_KEY: 'package4',
                                        consts.REQUIRE_KEY: ''
                                    }
                                ]
                            },
                            'package3': {
                                consts.LICENSE_KEY: 'package3_license',
                                consts.DEPENDENCIES_KEY: []
                            },
                            'package4': {
                                consts.LICENSE_KEY: 'package4_license',
                                consts.DEPENDENCIES_KEY: []
                            }
                        },
                        consts.ILLEGITIMATE_LICENSES_KEY: {
                            'package1': 'package1_license',
                            'package2': 'package2_license',
                            'package4': 'package4_license'
                        }
                    },
                    indent=consts.TAB_SIZE),
                **kwargs
            )

            kwargs[consts.HOMEPAGE_STR] = True
            kwargs[consts.SUMMARY_STR] = True
            kwargs[consts.VERSIONS_STR] = True
            kwargs[consts.SHOW_LICENSE_STR] = [
                'package1_license',
                'package2_license',
                'package3_license',
                'package4_license'
            ]

        mock_return = {
            'package1': [
                {
                    consts.PACKAGE_KEY: 'package2',
                    consts.REQUIRE_KEY: '==7'
                },
                {
                    consts.PACKAGE_KEY: 'package3',
                    consts.REQUIRE_KEY: '>5'
                }
            ],
            'package2': [
                {
                    consts.PACKAGE_KEY: 'package4',
                    consts.REQUIRE_KEY: ''
                },
            ],
            'package3': [],
            'package4': []
        }
        with mock.patch.object(dependencies, 'build_tree',
                               return_value=mock_return):
            self.assertTrue(cmp_elements(
                {
                    'dependencies_tree': {
                        'package1': {
                            consts.HOMEPAGE_KEY: 'package1_home',
                            consts.DEPENDENCIES_KEY: [
                                {
                                    consts.PACKAGE_KEY: 'package2',
                                    consts.REQUIRE_KEY: '==7'
                                },
                                {
                                    consts.PACKAGE_KEY: 'package3',
                                    consts.REQUIRE_KEY: '>5'
                                }
                            ],
                            consts.SUMMARY_KEY: 'package1_sum',
                            consts.LICENSE_KEY: 'package1_license',
                            consts.VERSIONS_KEY: [
                                'package1_1', 'package1_2'
                            ]
                        },
                        'package2': {
                            consts.HOMEPAGE_KEY: 'package2_home',
                            consts.DEPENDENCIES_KEY: [
                                {
                                    consts.PACKAGE_KEY: 'package4',
                                    consts.REQUIRE_KEY: ''
                                }
                            ],
                            consts.SUMMARY_KEY: 'package2_sum',
                            consts.LICENSE_KEY: 'package2_license',
                            consts.VERSIONS_KEY: [
                                'package2_1', 'package2_2'
                            ]
                        },
                        'package3': {
                            consts.HOMEPAGE_KEY: 'package3_home',
                            consts.DEPENDENCIES_KEY: [],
                            consts.SUMMARY_KEY: 'package3_sum',
                            consts.LICENSE_KEY: 'package3_license',
                            consts.VERSIONS_KEY: [
                                'package3_1', 'package3_2'
                            ]
                        },
                        'package4': {
                            consts.HOMEPAGE_KEY: 'package4_home',
                            consts.DEPENDENCIES_KEY: [],
                            consts.SUMMARY_KEY: 'package4_sum',
                            consts.LICENSE_KEY: 'package4_license',
                            consts.VERSIONS_KEY: [
                                'package4_1', 'package4_2'
                            ]
                        }
                    },
                    consts.ILLEGITIMATE_LICENSES_KEY: {}
                },
                yaml.safe_load(deppy.show_package(**kwargs))
            ))

    def test_seekup(self):

        def test_error(expected, **func_args):
            self.assertTrue(cmp_elements(expected,
                                         deppy.seekup(**func_args)))

        def test(expected, **func_args):
            self.assertTrue(cmp_elements(
                expected, yaml.safe_load(deppy.seekup(**func_args))))

        def mock_input(args):
            return args['mock_input_result']

        def mock_parallel(_, packages, __):
            return [
                (package,
                 [package + '_3', package + '_5'],
                 package + '_license')
                for package in packages
            ] if kwargs['map_return_value'] else []

        deppy.INPUTS['_mock_for_test'] = mock_input
        deppy._parallel = mock_parallel

        dependencies_failure_message = 'some_failure_message'

        kwargs = {
            consts.MAX_JOBS_STR: consts.MAX_JOBS_DEFAULT,
            consts.INPUT_TYPE_STR: '_mock_for_test',
            consts.RETURN_DATA_STR: True,
            consts.BY_MODULE_STR: False,
            consts.SHOW_LICENSE_STR: None,
            consts.INPUT_STR: None,
            'map_return_value': False
        }

        test_error(expected=consts.ERROR_MESSAGE_NO_INPUT)

        test_error(expected=consts.ERROR_MESSAGE_ILLEGAL_INPUT_TYPE.format(
            deppy.INPUTS.keys()),
            input_type='', input='')

        test_error(expected=dependencies_failure_message,
                   input_type='_mock_for_test',
                   input='', mock_input_result=dependencies_failure_message)

        test_error(expected=consts.ERROR_MESSAGE_NO_DEPENDENCIES,
                   input_type='_mock_for_test',
                   input='', mock_input_result=[])

        test_error(expected=consts.ERROR_MESSAGE_NO_DEPENDENCIES,
                   input_type='_mock_for_test',
                   input='',
                   mock_input_result=[
                       ([], 'a', ''), ([], 'b', ''), ([], 'c', '')])

        kwargs['mock_input_result'] = \
            [([('package2', '', '')], 'package1', '')]

        test_error(expected=consts.ERROR_MESSAGE_NO_VERSIONS, **kwargs)

        kwargs['mock_input_result'] = \
            [([('package2', '2', '==')], 'package1', '')]
        kwargs['map_return_value'] = True

        test(expected={
            consts.MODULES_KEY: {
                'package2==2': ['package1']
            },
            consts.RESULTS_KEY: [
                {
                    'require': '==2',
                    'new_versions_available': [
                        'package2_3',
                        'package2_5'
                    ],
                    'package': 'package2'
                }
            ]
            },
            **kwargs)

        kwargs['mock_input_result'] = [
            ([('package2', '2', '=='), ('package3', '1', '>=')],
             'package1', ''),
            ([('package3', '1', '=='), ('package5', '', '')],
             'package4', ''),
            ([('package7', '2', '>'), ('package2', '', '')],
             'package6', ''),
            ([('package7', '2', '>'), ('package9', '1', '==')],
             'package8', ''),
            ([], 'package10', '')
        ]

        results = [
            {
                'require': '==2',
                'new_versions_available': [
                    'package2_3',
                    'package2_5'
                ],
                'package': 'package2'
            },
            {
                'require': '>=1',
                'new_versions_available': [
                    'package3_3',
                    'package3_5'
                ],
                'package': 'package3'
            },
            {
                'require': '==1',
                'new_versions_available': [
                    'package3_3',
                    'package3_5'
                ],
                'package': 'package3'
            },
            {
                'require': '',
                'new_versions_available': [
                    'package5_3',
                    'package5_5'
                ],
                'package': 'package5'
            },
            {
                'require': '>2',
                'new_versions_available': [
                    'package7_3',
                    'package7_5'
                ],
                'package': 'package7'
            },
            {
                'require': '',
                'new_versions_available': [
                    'package2_3',
                    'package2_5'
                ],
                'package': 'package2'
            },
            {
                'require': '==1',
                'new_versions_available': [
                    'package9_3',
                    'package9_5'
                ],
                'package': 'package9'
            }
        ]

        dependencies_to_modules = {
            'package2==2': ['package1'],
            'package3>=1': ['package1'],
            'package3==1': ['package4'],
            'package5': ['package4'],
            'package7>2': ['package6', 'package8'],
            'package2': ['package6'],
            'package9==1': ['package8']
        }

        modules_to_dependencies = {
            'package1': [['package2', '==2'], ['package3', '>=1']],
            'package4': [['package3', '==1'], ['package5', '']],
            'package6': [['package7', '>2'], ['package2', '']],
            'package8': [['package7', '>2'], ['package9', '==1']]
        }

        licenses = {
            'package2': 'package2_license',
            'package3': 'package3_license',
            'package5': 'package5_license',
            'package7': 'package7_license',
            'package9': 'package9_license'
        }

        test(expected={
            consts.MODULES_KEY: dependencies_to_modules,
            consts.RESULTS_KEY: results
        },
            **kwargs)

        kwargs[consts.BY_MODULE_STR] = True

        test(expected={
            consts.MODULES_KEY: modules_to_dependencies,
            consts.RESULTS_KEY: results
        },
            **kwargs)

        kwargs[consts.SHOW_LICENSE_STR] = []
        kwargs[consts.BY_MODULE_STR] = False

        test(expected={
            consts.MODULES_KEY: dependencies_to_modules,
            consts.RESULTS_KEY: results,
            consts.LICENSE_KEY: licenses
        },
            **kwargs)

        kwargs[consts.BY_MODULE_STR] = True

        test(expected={
            consts.MODULES_KEY: modules_to_dependencies,
            consts.RESULTS_KEY: results,
            consts.LICENSE_KEY: licenses
        },
            **kwargs)

        kwargs[consts.SHOW_LICENSE_STR] = ['bla']
        kwargs[consts.BY_MODULE_STR] = False

        test(expected={
            consts.MODULES_KEY: dependencies_to_modules,
            consts.RESULTS_KEY: results,
            consts.LICENSE_KEY: licenses,
            consts.ILLEGITIMATE_LICENSES_KEY: licenses
        },
            **kwargs)

        kwargs[consts.BY_MODULE_STR] = True

        test(expected={
            consts.MODULES_KEY: modules_to_dependencies,
            consts.RESULTS_KEY: results,
            consts.LICENSE_KEY: licenses,
            consts.ILLEGITIMATE_LICENSES_KEY: licenses
        },
            **kwargs)

        kwargs[consts.SHOW_LICENSE_STR] = ['package3_license']
        kwargs[consts.BY_MODULE_STR] = False

        test(expected={
            consts.MODULES_KEY: dependencies_to_modules,
            consts.RESULTS_KEY: results,
            consts.LICENSE_KEY: licenses,
            consts.ILLEGITIMATE_LICENSES_KEY: {
                'package2': 'package2_license',
                'package5': 'package5_license',
                'package7': 'package7_license',
                'package9': 'package9_license'
            }
        },
            **kwargs)

        kwargs[consts.BY_MODULE_STR] = True

        test(expected={
            consts.MODULES_KEY: modules_to_dependencies,
            consts.RESULTS_KEY: results,
            consts.LICENSE_KEY: licenses,
            consts.ILLEGITIMATE_LICENSES_KEY: {
                'package2': 'package2_license',
                'package5': 'package5_license',
                'package7': 'package7_license',
                'package9': 'package9_license'
            }
        },
            **kwargs)

        kwargs[consts.SHOW_LICENSE_STR] = [
            'package3_license', 'package7_license'
        ]
        kwargs[consts.BY_MODULE_STR] = False

        test(expected={
            consts.MODULES_KEY: dependencies_to_modules,
            consts.RESULTS_KEY: results,
            consts.LICENSE_KEY: licenses,
            consts.ILLEGITIMATE_LICENSES_KEY: {
                'package2': 'package2_license',
                'package5': 'package5_license',
                'package9': 'package9_license'
            }
        },
            **kwargs)

        kwargs[consts.BY_MODULE_STR] = True

        test(expected={
            consts.MODULES_KEY: modules_to_dependencies,
            consts.RESULTS_KEY: results,
            consts.LICENSE_KEY: licenses,
            consts.ILLEGITIMATE_LICENSES_KEY: {
                'package2': 'package2_license',
                'package5': 'package5_license',
                'package9': 'package9_license'
            }
        },
            **kwargs)

    # def test_main(self):
    #
    #     def test(expected):
    #         self._generic_test(deppy.main, expected)
    #
    #
    #     with mock.patch.object(deppy, '_parse_args',
    #                            return_value={
    #                                consts.SUBCOMMAND_STR: consts.SHOWPACK_STR
    #                            }):
    #         with mock.patch.object(deppy, 'show_package',
    #                                return_value='showpack_called'):
    #             test(expected='showpack_called')
    #
    #     with mock.patch.object(deppy, '_parse_args',
    #                            return_value={
    #                                consts.SUBCOMMAND_STR: consts.LICENSES_STR
    #                            }):
    #         with mock.patch.object(deppy, 'licenses',
    #                                return_value='licenses_called'):
    #             test(expected='licenses_called')
    #
    #     with mock.patch.object(deppy, '_parse_args',
    #                            return_value={
    #                                consts.SUBCOMMAND_STR: 'bla'
    #                            }):
    #         try:
    #             test(expected='')
    #         except KeyError:
    #             pass
    #         else:
    #             self.assertTrue(False)
