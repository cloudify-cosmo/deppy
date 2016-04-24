
import os

import mock
import json
import testtools

import tests_consts

from deppy import consts
from deppy import dependencies
from helpers import cmp_elements


class TestDependencies(testtools.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestDependencies, self).__init__(*args, **kwargs)
        self.old_get_from_file = dependencies.get_from_file

    def tearDown(self):
        dependencies.get_from_file = self.old_get_from_file
        super(TestDependencies, self).tearDown()

    def _generic_test(self, func, expected, *func_args):
        self.assertTrue(cmp_elements(expected, func(*func_args)))

    def test_build_tree(self):

        tested_func = dependencies.build_tree

        def test(expected_result, *tested_func_args):
            self._generic_test(tested_func, expected_result, *tested_func_args)

        expected = {}
        func_args = [tests_consts.DUMMY_PACKAGE_NAME]
        test(expected, *func_args)

        # this package must be locally installed or the test will fail
        package_name = tests_consts.LOCAL_PACKAGE_NAME

        self.assertTrue(package_name in tested_func(package_name))

        expected = {
            'a': [
                {
                    consts.PACKAGE_KEY: 'b',
                    consts.REQUIRE_KEY: '==3'
                },
                {
                    consts.PACKAGE_KEY: 'c',
                    consts.REQUIRE_KEY: '>2'
                }
            ],
            'b': [
                {
                    consts.PACKAGE_KEY: 'd',
                    consts.REQUIRE_KEY: ''
                }
            ],
            'c': [
                {
                    consts.PACKAGE_KEY: 'd',
                    consts.REQUIRE_KEY: ''
                }
            ],
            'd': [
                {
                    consts.PACKAGE_KEY: 'e',
                    consts.REQUIRE_KEY: ''
                }
            ],
            'e': []
        }
        func_args = ['a']
        mock_return = [
            {
                consts.PACKAGE_KEY: {consts.KEY_KEY: 'a'},
                consts.DEPENDENCIES_KEY: [
                    {
                        consts.KEY_KEY: 'b',
                        consts.REQUIRED_VERSION_KEY: '==3'
                    },
                    {
                        consts.KEY_KEY: 'c',
                        consts.REQUIRED_VERSION_KEY: '>2'
                    }
                ]
            },
            {
                consts.PACKAGE_KEY: {consts.KEY_KEY: 'b'},
                consts.DEPENDENCIES_KEY: [
                    {
                        consts.KEY_KEY: 'd',
                        consts.REQUIRED_VERSION_KEY: ''
                    }
                ]
            },
            {
                consts.PACKAGE_KEY: {consts.KEY_KEY: 'c'},
                consts.DEPENDENCIES_KEY: [
                    {
                        consts.KEY_KEY: 'd',
                        consts.REQUIRED_VERSION_KEY: ''
                    }
                ]
            },
            {
                consts.PACKAGE_KEY: {consts.KEY_KEY: 'd'},
                consts.DEPENDENCIES_KEY: [
                    {
                        consts.KEY_KEY: 'e',
                    }
                ]
            },
            {
                consts.PACKAGE_KEY: {consts.KEY_KEY: 'e'},
                consts.DEPENDENCIES_KEY: []
            },
            {
                consts.PACKAGE_KEY: {consts.KEY_KEY: 'f'},
                consts.DEPENDENCIES_KEY: [
                    {
                        consts.KEY_KEY: 'b',
                        consts.REQUIRED_VERSION_KEY: '==1'
                    }
                ]
            }
        ]
        with mock.patch.object(json, 'loads', return_value=mock_return):
            test(expected, *func_args)

    def test_get_from_file(self):

        def test(expected_result, *tested_func_args):
            self._generic_test(dependencies.get_from_file,
                               expected_result, *tested_func_args)

        expected = ([], 'bla', consts.UNKNOWN)
        func_args = ['bla']
        test(expected, *func_args)

        expected = (
            [
                ('requests', '2.9.1', '=='),
                ('pipdeptree', '0.6.0', '=='),
                ('joblib', '0.9.4', '==')
            ],
            'deppy',
            consts.UNKNOWN
        )
        func_args = [os.path.join(
            tests_consts.RESOURCES_PATH, 'setup_for_test_normal.py')]
        test(expected, *func_args)

        file_path = os.path.join(
            tests_consts.RESOURCES_PATH, 'setup_for_test_no_name.py')
        expected = (
            [
                ('requests', '2.9.1', '=='),
                ('pipdeptree', '0.6.0', '=='),
                ('joblib', '0.9.4', '==')
            ],
            file_path,
            consts.UNKNOWN
        )
        func_args = [file_path]
        test(expected, *func_args)

        expected = ([], 'deppy', consts.UNKNOWN)
        func_args = [os.path.join(
            tests_consts.RESOURCES_PATH, 'setup_for_test_empty.py')]
        test(expected, *func_args)

        expected = ([], 'deppy', consts.UNKNOWN)
        func_args = [os.path.join(
            tests_consts.RESOURCES_PATH, 'setup_for_test_no_requires.py')]
        test(expected, *func_args)

        expected = (
            [
                ('requests', '', ''),
                ('pipdeptree', '0.6.0', '=='),
                ('joblib', '0.9.4', '>')
            ],
            'deppy',
            'test_license'
        )
        func_args = [os.path.join(tests_consts.RESOURCES_PATH,
                                  'setup_for_test_diverse_requires.py')]
        test(expected, *func_args)

        expected = (
            [
                ('requests', '2.9.1', '=='),
                ('pipdeptree', '0.6.0', '=='),
                ('joblib', '0.9.4', '==')
            ],
            'deppy',
            consts.UNKNOWN
        )
        func_args = [os.path.join(tests_consts.RESOURCES_PATH,
                                  'setup_for_test_with_requirements.py')]
        test(expected, *func_args)

    def test_get_by_url(self):

        tested_func = dependencies.get_by_url
        mocked_name = dependencies.get_from_file.__name__

        def test(expected_result, *tested_func_args):
            self._generic_test(tested_func, expected_result, *tested_func_args)

        expected = None
        func_args = ['']
        test(expected, *func_args)

        expected = None
        func_args = ['https://github.com/cloudify-cosmo/deppy', 'bla']
        test(expected, *func_args)

        expected = (['bla1'], 'bla2', 'lic')
        func_args = ['https://github.com/cloudify-cosmo/deppy']
        mock_return = (['bla1'], 'bla2', 'lic')
        with mock.patch.object(dependencies, mocked_name,
                               return_value=mock_return):
            test(expected, *func_args)

        expected = (['bla1'], 'bla2', 'lic')
        func_args = ['https://github.com/cloudify-cosmo/deppy',
                     'https://github.com/cloudify-cosmo/deppy']
        mock_return = (['bla1'], 'bla2', 'lic')
        with mock.patch.object(dependencies, mocked_name,
                               return_value=mock_return):
            test(expected, *func_args)

        def mock_get_from_file(path):

            with open(path) as f:
                output = f.read()
            expected_path = os.path.join(
                tests_consts.RESOURCES_PATH, 'setup_for_test_normal.py')

            with open(expected_path) as f:
                expected_output = f.read()

            if cmp_elements(expected_output, output):
                return [], 'True', ''
            return [], 'False', ''

        dependencies.get_from_file = mock_get_from_file

        _, result, __ = tested_func(
            'https://raw.githubusercontent.com/cloudify-cosmo/deppy/master/'
            'tests/resources/setup_for_test_normal.py')

        self.assertEqual(result, 'True')

    def test_get_for_package(self):

        mocked_name = dependencies.build_tree.__name__

        def test(expected_result, *tested_func_args):
            self._generic_test(dependencies.get_for_package,
                               expected_result, *tested_func_args)

        # this package must be locally installed or the test will fail
        package_name = tests_consts.LOCAL_PACKAGE_NAME

        expected = (None, package_name, consts.UNKNOWN)
        func_args = [package_name]
        mock_return = {}
        with mock.patch.object(
                dependencies, mocked_name, return_value=mock_return):
            test(expected, *func_args)

        expected = ([], package_name, consts.UNKNOWN)
        func_args = [package_name]
        mock_return = {package_name: []}
        with mock.patch.object(
                dependencies, mocked_name, return_value=mock_return):
            test(expected, *func_args)

        expected = ([('a', '4', '==')], package_name, consts.UNKNOWN)
        func_args = [package_name]
        mock_return = {
            package_name: [
                {
                    consts.PACKAGE_KEY: 'a',
                    consts.REQUIRE_KEY: '==4'
                }
            ]
        }
        with mock.patch.object(
                dependencies, mocked_name, return_value=mock_return):
            test(expected, *func_args)

        expected = ([('a', '4', '=='), ('b', '3', '>=')],
                    package_name, consts.UNKNOWN)
        func_args = [package_name]
        mock_return = {
            package_name: [
                {
                    consts.PACKAGE_KEY: 'a',
                    consts.REQUIRE_KEY: '==4'
                },
                {
                    consts.PACKAGE_KEY: 'b',
                    consts.REQUIRE_KEY: '>=3'
                }
            ]
        }
        with mock.patch.object(
                dependencies, mocked_name, return_value=mock_return):
            test(expected, *func_args)

        expected = ([('a', '4', '=='), ('b', '3', '>=')],
                    package_name, consts.UNKNOWN)
        func_args = [package_name]
        mock_return = {
            package_name: [
                {
                    consts.PACKAGE_KEY: 'a',
                    consts.REQUIRE_KEY: '==4'
                },
                {
                    consts.PACKAGE_KEY: 'b',
                    consts.REQUIRE_KEY: '>=3'
                }
            ],
            'c': [
                {
                    consts.PACKAGE_KEY: 'a',
                    consts.REQUIRE_KEY: '==3'
                },
                {
                    consts.PACKAGE_KEY: 'd',
                    consts.REQUIRE_KEY: '>=3'
                }
            ]
        }
        with mock.patch.object(
                dependencies, mocked_name, return_value=mock_return):
            test(expected, *func_args)

        expected = ([('a', '', ''), ('b', '3', '>=')],
                    package_name, consts.UNKNOWN)
        func_args = [package_name]
        mock_return = {
            package_name: [
                {
                    consts.PACKAGE_KEY: 'a',
                    consts.REQUIRE_KEY: ''
                },
                {
                    consts.PACKAGE_KEY: 'b',
                    consts.REQUIRE_KEY: '>=3'
                }
            ]
        }
        with mock.patch.object(
                dependencies, mocked_name, return_value=mock_return):
            test(expected, *func_args)
