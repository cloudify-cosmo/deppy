
import os

import testtools

from dep_vers import dep_vers_module as tested_module
from helpers import cmp_elements
from mocks import mock_dep_vers_module


DUMMY_PACKAGE_NAME = 'dummy_package_that_doesnt_exist_065591'
SOURCES_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), ('sources'))


class TestDepVersModule(testtools.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestDepVersModule, self).__init__(*args, **kwargs)
        self.func = None

    def _generic_test(self, expected, *args):
        self.assertTrue(cmp_elements(expected, self.func(*args)))

    def test_build_dep_tree(self):
        self.func = tested_module.build_dep_tree
        t = self._generic_test

        t({}, DUMMY_PACKAGE_NAME)

        package_name = 'deppy'
        res = self.func(package_name)
        self.assertTrue(package_name in res)

    def test_get_dependencies_from_file(self):
        self.func = tested_module.get_dependencies_from_file
        t = self._generic_test

        file_path = os.path.join(SOURCES_PATH, 'setup_for_test_1.py')
        t(([('requests', '2.9.1', '=='), ('pipdeptree', '0.6.0', '=='), ('joblib', '0.9.4', '==')], 'deppy'), file_path)

        file_path = os.path.join(SOURCES_PATH, 'setup_for_test_2.py')
        t(([('requests', '2.9.1', '=='), ('pipdeptree', '0.6.0', '=='), ('joblib', '0.9.4', '==')], file_path), file_path)

        file_path = os.path.join(SOURCES_PATH, 'setup_for_test_3.py')
        t(([], 'deppy'), file_path)

        file_path = os.path.join(SOURCES_PATH, 'setup_for_test_4.py')
        t(([], 'deppy'), file_path)

        file_path = os.path.join(SOURCES_PATH, 'setup_for_test_5.py')
        t(([('requests', '', ''), ('pipdeptree', '0.6.0', '=='), ('joblib', '0.9.4', '>')], 'deppy'), file_path)

    def test_get_dependencies_by_url(self):
        self.func = tested_module.get_dependencies_by_url
        t = self._generic_test

        with mock_dep_vers_module.mock_get_dependencies_from_file(([], 'bla')):
            t(([], 'bla'), 'https://github.com/cloudify-cosmo/deppy')

        with mock_dep_vers_module.mock_get_dependencies_from_file(([], None), True):
            t(([], 'https://github.com/cloudify-cosmo/deppy'), 'https://github.com/cloudify-cosmo/deppy')

    def test_get_dependencies_for_package(self):
        self.func = tested_module.get_dependencies_for_package
        t = self._generic_test

        package_name = 'pika'

        with mock_dep_vers_module.mock_build_dep_tree({}):
            t((None, package_name), package_name)

        with mock_dep_vers_module.mock_build_dep_tree({package_name: []}):
            t(([], package_name), package_name)

        with mock_dep_vers_module.mock_build_dep_tree({
            package_name: [
                {
                    tested_module.PACKAGE_KEY: 'a',
                    tested_module.REQUIRED_KEY: '==4'
                }
            ]
        }):
            t(([('a', '4', '==')], package_name), package_name)

        with mock_dep_vers_module.mock_build_dep_tree({
            package_name: [
                {
                    tested_module.PACKAGE_KEY: 'a',
                    tested_module.REQUIRED_KEY: '==4'
                },
                {
                    tested_module.PACKAGE_KEY: 'b',
                    tested_module.REQUIRED_KEY: '>=3'
                }
            ]
        }):
            t(([('a', '4', '=='), ('b', '3', '>=')], package_name), package_name)

        with mock_dep_vers_module.mock_build_dep_tree({
            package_name: [
                {
                    tested_module.PACKAGE_KEY: 'a',
                    tested_module.REQUIRED_KEY: '==4'
                },
                {
                    tested_module.PACKAGE_KEY: 'b',
                    tested_module.REQUIRED_KEY: '>=3'
                }
            ],
            'c': [
                {
                    tested_module.PACKAGE_KEY: 'a',
                    tested_module.REQUIRED_KEY: '==3'
                },
                {
                    tested_module.PACKAGE_KEY: 'd',
                    tested_module.REQUIRED_KEY: '>=3'
                }
            ]
        }):
            t(([('a', '4', '=='), ('b', '3', '>=')], package_name), package_name)

        with mock_dep_vers_module.mock_build_dep_tree({
            package_name: [
                {
                    tested_module.PACKAGE_KEY: 'a',
                    tested_module.REQUIRED_KEY: ''
                },
                {
                    tested_module.PACKAGE_KEY: 'b',
                    tested_module.REQUIRED_KEY: '>=3'
                }
            ]
        }):
            t(([('a', '', ''), ('b', '3', '>=')], package_name), package_name)
