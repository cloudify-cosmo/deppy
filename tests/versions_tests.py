
import mock
import testtools

import tests_consts

from deppy import consts
from deppy import versions
from helpers import cmp_elements


class TestVersions(testtools.TestCase):

    def _generic_test(self, func, expected, *func_args):
        self.assertTrue(cmp_elements(expected, func(*func_args)))

    def test_compare_old(self):

        func = versions.compare

        self.assertEqual(func('7', '7'), 0)
        self.assertEqual(func('7', '6'), 1)
        self.assertEqual(func('5', '6'), -1)

        self.assertEqual(func('7.5', '7.5'), 0)
        self.assertEqual(func('7.7', '7.6'), 1)
        self.assertEqual(func('7.4', '7.9'), -1)

        self.assertEqual(func('7.7', '6.6'), 1)
        self.assertEqual(func('6.4', '7.9'), -1)
        self.assertEqual(func('9.4', '7.6'), 1)
        self.assertEqual(func('7.4', '8.1'), -1)
        self.assertEqual(func('5.5', '4.5'), 1)
        self.assertEqual(func('1.3', '2.3'), -1)

        self.assertEqual(func('13', '13'), 0)
        self.assertEqual(func('13', '12'), 1)
        self.assertEqual(func('12', '13'), -1)

        self.assertEqual(func('7.51', '7.51'), 0)
        self.assertEqual(func('7.71', '7.61'), 1)
        self.assertEqual(func('7.41', '7.91'), -1)

        self.assertEqual(func('7.71', '6.61'), 1)
        self.assertEqual(func('6.41', '7.91'), -1)
        self.assertEqual(func('9.41', '7.61'), 1)
        self.assertEqual(func('7.41', '8.11'), -1)
        self.assertEqual(func('5.51', '4.51'), 1)
        self.assertEqual(func('1.31', '2.31'), -1)

        self.assertEqual(func('71.5', '71.5'), 0)
        self.assertEqual(func('71.7', '71.6'), 1)
        self.assertEqual(func('71.4', '71.9'), -1)

        self.assertEqual(func('71.7', '61.6'), 1)
        self.assertEqual(func('61.4', '71.9'), -1)
        self.assertEqual(func('91.4', '71.6'), 1)
        self.assertEqual(func('71.4', '81.1'), -1)
        self.assertEqual(func('51.5', '41.5'), 1)
        self.assertEqual(func('11.3', '21.3'), -1)

        self.assertEqual(func('7.5.3', '7.5.3'), 0)
        self.assertEqual(func('7.5.7', '7.5.6'), 1)
        self.assertEqual(func('7.5.4', '7.5.9'), -1)

        self.assertEqual(func('7.7.7', '6.6.6'), 1)
        self.assertEqual(func('6.5.4', '7.5.9'), -1)
        self.assertEqual(func('6.5.4', '7.8.9'), -1)
        self.assertEqual(func('9.5.4', '7.8.5'), 1)
        self.assertEqual(func('7.6.4', '8.2.1'), -1)
        self.assertEqual(func('5.5.5', '4.5.5'), 1)
        self.assertEqual(func('1.3.3', '2.3.3'), -1)

        self.assertEqual(func('71.51', '71.51'), 0)
        self.assertEqual(func('71.71', '71.61'), 1)
        self.assertEqual(func('71.41', '71.91'), -1)

        self.assertEqual(func('71.71', '61.61'), 1)
        self.assertEqual(func('61.41', '71.91'), -1)
        self.assertEqual(func('91.41', '71.61'), 1)
        self.assertEqual(func('71.41', '81.11'), -1)
        self.assertEqual(func('51.51', '41.51'), 1)
        self.assertEqual(func('11.31', '21.31'), -1)

        self.assertEqual(func('17.5.3', '17.5.3'), 0)
        self.assertEqual(func('17.5.7', '17.5.6'), 1)
        self.assertEqual(func('17.5.4', '17.5.9'), -1)

        self.assertEqual(func('17.7.7', '16.6.6'), 1)
        self.assertEqual(func('16.5.4', '17.5.9'), -1)
        self.assertEqual(func('16.5.4', '17.8.9'), -1)
        self.assertEqual(func('19.5.4', '17.8.5'), 1)
        self.assertEqual(func('17.6.4', '18.2.1'), -1)
        self.assertEqual(func('15.5.5', '14.5.5'), 1)
        self.assertEqual(func('11.3.3', '12.3.3'), -1)

        self.assertEqual(func('7.15.3', '7.15.3'), 0)
        self.assertEqual(func('7.15.7', '7.15.6'), 1)
        self.assertEqual(func('7.15.4', '7.15.9'), -1)

        self.assertEqual(func('7.17.7', '6.16.6'), 1)
        self.assertEqual(func('6.15.4', '7.15.9'), -1)
        self.assertEqual(func('6.15.4', '7.18.9'), -1)
        self.assertEqual(func('9.15.4', '7.18.5'), 1)
        self.assertEqual(func('7.16.4', '8.12.1'), -1)
        self.assertEqual(func('5.15.5', '4.15.5'), 1)
        self.assertEqual(func('1.13.3', '2.13.3'), -1)

        self.assertEqual(func('7.5.13', '7.5.13'), 0)
        self.assertEqual(func('7.5.17', '7.5.16'), 1)
        self.assertEqual(func('7.5.14', '7.5.19'), -1)

        self.assertEqual(func('7.7.17', '6.6.16'), 1)
        self.assertEqual(func('6.5.14', '7.5.19'), -1)
        self.assertEqual(func('6.5.14', '7.8.19'), -1)
        self.assertEqual(func('9.5.14', '7.8.15'), 1)
        self.assertEqual(func('7.6.14', '8.2.11'), -1)
        self.assertEqual(func('5.5.15', '4.5.15'), 1)
        self.assertEqual(func('1.3.13', '2.3.13'), -1)

        self.assertEqual(func('17.5.3', '7.5.3'), 1)
        self.assertEqual(func('7.15.3', '7.5.3'), 1)
        self.assertEqual(func('7.5.13', '7.5.3'), 1)
        self.assertEqual(func('17.5.7', '7.5.6'), 1)
        self.assertEqual(func('7.15.7', '7.5.6'), 1)
        self.assertEqual(func('7.5.17', '7.5.6'), 1)
        self.assertEqual(func('17.5.4', '7.5.9'), 1)
        self.assertEqual(func('7.15.4', '7.5.9'), 1)
        self.assertEqual(func('7.5.14', '7.5.9'), 1)

        self.assertEqual(func('17.7.7', '6.6.6'), 1)
        self.assertEqual(func('7.17.7', '6.6.6'), 1)
        self.assertEqual(func('7.7.17', '6.6.6'), 1)
        self.assertEqual(func('16.5.4', '7.5.9'), 1)
        self.assertEqual(func('6.15.4', '7.5.9'), -1)
        self.assertEqual(func('6.5.14', '7.5.9'), -1)
        self.assertEqual(func('16.5.4', '7.8.9'), 1)
        self.assertEqual(func('6.15.4', '7.8.9'), -1)
        self.assertEqual(func('6.5.14', '7.8.9'), -1)
        self.assertEqual(func('19.5.4', '7.8.5'), 1)
        self.assertEqual(func('9.15.4', '7.8.5'), 1)
        self.assertEqual(func('9.5.14', '7.8.5'), 1)
        self.assertEqual(func('17.6.4', '8.2.1'), 1)
        self.assertEqual(func('7.16.4', '8.2.1'), -1)
        self.assertEqual(func('7.6.14', '8.2.1'), -1)
        self.assertEqual(func('15.5.5', '4.5.5'), 1)
        self.assertEqual(func('5.15.5', '4.5.5'), 1)
        self.assertEqual(func('5.5.15', '4.5.5'), 1)
        self.assertEqual(func('11.3.3', '2.3.3'), 1)
        self.assertEqual(func('1.13.3', '2.3.3'), -1)
        self.assertEqual(func('1.3.13', '2.3.3'), -1)

        self.assertEqual(func('7.5.3', '17.5.3'), -1)
        self.assertEqual(func('7.5.3', '7.15.3'), -1)
        self.assertEqual(func('7.5.3', '7.5.13'), -1)
        self.assertEqual(func('7.5.7', '17.5.6'), -1)
        self.assertEqual(func('7.5.7', '7.15.6'), -1)
        self.assertEqual(func('7.5.7', '7.5.16'), -1)
        self.assertEqual(func('7.5.4', '17.5.9'), -1)
        self.assertEqual(func('7.5.4', '7.15.9'), -1)
        self.assertEqual(func('7.5.4', '7.5.19'), -1)

        self.assertEqual(func('7.7.7', '16.6.6'), -1)
        self.assertEqual(func('7.7.7', '6.16.6'), 1)
        self.assertEqual(func('7.7.7', '6.6.16'), 1)
        self.assertEqual(func('6.5.4', '17.5.9'), -1)
        self.assertEqual(func('6.5.4', '7.15.9'), -1)
        self.assertEqual(func('6.5.4', '7.5.19'), -1)
        self.assertEqual(func('6.5.4', '17.8.9'), -1)
        self.assertEqual(func('6.5.4', '7.18.9'), -1)
        self.assertEqual(func('6.5.4', '7.8.19'), -1)
        self.assertEqual(func('9.5.4', '17.8.5'), -1)
        self.assertEqual(func('9.5.4', '7.18.5'), 1)
        self.assertEqual(func('9.5.4', '7.8.15'), 1)
        self.assertEqual(func('7.6.4', '18.2.1'), -1)
        self.assertEqual(func('7.6.4', '8.12.1'), -1)
        self.assertEqual(func('7.6.4', '8.2.11'), -1)
        self.assertEqual(func('5.5.5', '14.5.5'), -1)
        self.assertEqual(func('5.5.5', '4.15.5'), 1)
        self.assertEqual(func('5.5.5', '4.5.15'), 1)
        self.assertEqual(func('1.3.3', '12.3.3'), -1)
        self.assertEqual(func('1.3.3', '2.13.3'), -1)
        self.assertEqual(func('1.3.3', '2.3.13'), -1)

        self.assertEqual(func('1.13.3', '1.13.13'), -1)
        self.assertEqual(func('1.13.13', '1.13.13'), 0)
        self.assertEqual(func('13.13.13', '13.13.13'), 0)
        self.assertEqual(func('13.13.13', '13.12.13'), 1)
        self.assertEqual(func('13.13.15', '13.13.13'), 1)
        self.assertEqual(func('13.13.15', '113.13.13'), -1)

    def test_compare_new(self):

        def test(expected_result, *tested_func_args):
            self._generic_test(versions.compare,
                               expected_result, *tested_func_args)

        test(True, '1.2', '1.3', '<')
        test(False, '1.2', '1.3', '>')
        test(True, '1.2', '1.3', '<=')
        test(False, '1.2', '1.3', '>=')
        test(False, '1.2', '1.3', '==')
        test(True, '1.2', '1.3', '!=')

        test(False, '1.4', '1.3', '<')
        test(True, '1.4', '1.3', '>')
        test(False, '1.4', '1.3', '<=')
        test(True, '1.4', '1.3', '>=')
        test(False, '1.4', '1.3', '==')
        test(True, '1.4', '1.3', '!=')

        test(False, '1.3', '1.3', '<')
        test(False, '1.3', '1.3', '>')
        test(True, '1.3', '1.3', '<=')
        test(True, '1.3', '1.3', '>=')
        test(True, '1.3', '1.3', '==')
        test(False, '1.3', '1.3', '!=')

        test(False, '1.3.2', '1.3.2', '<')
        test(False, '1.3.2', '1.3.2', '>')
        test(True, '1.3.2', '1.3.2', '<=')
        test(True, '1.3.2', '1.3.2', '>=')
        test(True, '1.3.2', '1.3.2', '==')
        test(False, '1.3.2', '1.3.2', '!=')

        test(True, '1.3.2', '1.3.5', '<')
        test(False, '1.3.2', '1.3.5', '>')
        test(True, '1.3.2', '1.3.5', '<=')
        test(False, '1.3.2', '1.3.5', '>=')
        test(False, '1.3.2', '1.3.5', '==')
        test(True, '1.3.2', '1.3.5', '!=')

        test(False, '1.4.2', '1.3.5', '<')
        test(True, '1.4.2', '1.3.5', '>')
        test(False, '1.4.2', '1.3.5', '<=')
        test(True, '1.4.2', '1.3.5', '>=')
        test(False, '1.4.2', '1.3.5', '==')
        test(True, '1.4.2', '1.3.5', '!=')

    def test_split_require(self):

        def test(expected_result, *tested_func_args):
            self._generic_test(versions.split_require,
                               expected_result, *tested_func_args)

        ver_str = '7.5'
        for op in versions.OPERATORS:
            expected = (ver_str, op)
            func_args = [op + ver_str]
            test(expected, *func_args)
        expected = (ver_str, '')
        func_args = [ver_str]
        test(expected, *func_args)

    def test_filter_newer(self):

        def test(expected_result, *tested_func_args):
            self._generic_test(versions._filter_newer,
                               expected_result, *tested_func_args)

        expected = ['1', '2', '3']
        func_args = [['1', '2', '3'], '']
        test(expected, *func_args)

        expected = ['1', '2', '3']
        func_args = [['1', '2', '3'], '0']
        test(expected, *func_args)

        expected = ['2', '3']
        func_args = [['1', '2', '3'], '1']
        test(expected, *func_args)

        expected = ['3']
        func_args = [['1', '2', '3'], '2']
        test(expected, *func_args)

        expected = []
        func_args = [['1', '2', '3'], '3']
        test(expected, *func_args)

        expected = ['1', '2', '3']
        func_args = [['3', '2', '1'], '0']
        test(expected, *func_args)

        expected = ['2', '3']
        func_args = [['3', '2', '1'], '1']
        test(expected, *func_args)

        expected = ['3']
        func_args = [['3', '2', '1'], '2']
        test(expected, *func_args)

        expected = []
        func_args = [['3', '2', '1'], '3']
        test(expected, *func_args)

        expected = ['1.2.2', '1.22.2', '3', '3.2']
        func_args = [['3', '1.1', '1.2', '1.2.2', '1.22.2', '3.2'], '1.2.1']
        test(expected, *func_args)

        expected = ['1.2.2', '1.22.2', '3', '3.2', '1.2.1.1']
        func_args = [
            ['3', '1.1', '1.2', '1.2.2', '1.22.2', '3.2', '1.2.1', '1.2.1.1'],
            '1.2.1'
        ]
        test(expected, *func_args)

        expected = ['1.22.2', '3', '3.2']
        func_args = [['3', '1.1', '1.2', '1.2.2', '1.22.2', '3.2'], '1.21.1']
        test(expected, *func_args)

        expected = []
        func_args = [[], '']
        test(expected, *func_args)

        expected = ['3']
        func_args = [['1', '2', '3'], '2']
        test(expected, *func_args)

    def test_get_new_available(self):

        def test(expected_result, *tested_func_args):
            self._generic_test(versions.get_new_available,
                               expected_result, *tested_func_args)

        expected = [{
            consts.PACKAGE_KEY: 'a',
            consts.REQUIRE_KEY: '2',
            consts.NEW_VERS_KEY: ['3']
        }]
        func_args = [{'a': ['2']}, {'a': ['1', '3']}]
        test(expected, *func_args)

        expected = [{
            consts.PACKAGE_KEY: 'a',
            consts.REQUIRE_KEY: '2',
            consts.NEW_VERS_KEY: []
        }]
        func_args = [{'a': ['2']}, {'a': ['2']}]
        test(expected, *func_args)

        expected = [{
            consts.PACKAGE_KEY: 'a',
            consts.REQUIRE_KEY: '2',
            consts.NEW_VERS_KEY: ['3']
        }]
        func_args = [{'a': ['2']}, {'a': ['1', '3'], 'b': ['4', '5']}]
        test(expected, *func_args)

        expected = [
            {
                consts.PACKAGE_KEY: 'a',
                consts.REQUIRE_KEY: '2',
                consts.NEW_VERS_KEY: ['3']
            },
            {
                consts.PACKAGE_KEY: 'b',
                consts.REQUIRE_KEY: '3',
                consts.NEW_VERS_KEY: ['4', '5']
            }
        ]
        func_args = [{'a': ['2'], 'b': ['3']},
                     {'a': ['1', '3'], 'b': ['4', '5']}]
        test(expected, *func_args)

        expected = [
            {
                consts.PACKAGE_KEY: 'a',
                consts.REQUIRE_KEY: '0.5',
                consts.NEW_VERS_KEY: ['1', '3']
            },
            {
                consts.PACKAGE_KEY: 'a',
                consts.REQUIRE_KEY: '3',
                consts.NEW_VERS_KEY: []
            },
            {
                consts.PACKAGE_KEY: 'a',
                consts.REQUIRE_KEY: '2',
                consts.NEW_VERS_KEY: ['3']
            }
        ]
        func_args = [{'a': ['2', '3', '0.5']},
                     {'a': ['1', '3'], 'b': ['4', '5']}]
        test(expected, *func_args)

        expected = [
            {
                consts.PACKAGE_KEY: 'a',
                consts.REQUIRE_KEY: '2',
                consts.NEW_VERS_KEY: ['4']
            },
            {
                consts.PACKAGE_KEY: 'b',
                consts.REQUIRE_KEY: '3',
                consts.NEW_VERS_KEY: []
            }
        ]
        func_args = [{'a': ['2'], 'b': ['3']},
                     {'a': ['1', '4'], 'b': ['2', '1']}]
        test(expected, *func_args)

        expected = []
        func_args = [{'c': ['2']}, {'a': ['1', '3'], 'b': ['4', '5']}]
        test(expected, *func_args)

        expected = [{
            consts.PACKAGE_KEY: 'a',
            consts.REQUIRE_KEY: '7',
            consts.NEW_VERS_KEY: []
        }]
        func_args = [{'a': ['7']}, {'a': ['1', '3'], 'b': ['4', '5']}]
        test(expected, *func_args)

        expected = []
        func_args = [{}, {'a': ['1', '3'], 'b': ['4', '5']}]
        test(expected, *func_args)

        expected = []
        func_args = [{'a': ['7']}, {}]
        test(expected, *func_args)

        expected = []
        func_args = [{}, {}]
        test(expected, *func_args)

    def test_get_package_data_from_pypi(self):

        tested_func = versions.get_package_data_from_pypi

        def test(expected_result, *tested_func_args):
            self._generic_test(tested_func, expected_result, *tested_func_args)

        expected = None
        func_args = [tests_consts.DUMMY_PACKAGE_NAME]
        test(expected, *func_args)

        package_name = tests_consts.PYPI_PACKAGE_NAME
        func_result = tested_func(package_name)
        self.assertEqual(
            str(func_result[consts.INFO_KEY][consts.NAME_KEY]).lower(),
            package_name.lower()
        )

    def test_get_from_pypi(self):

        tested_func = versions.get_from_pypi
        mocked_name = versions.get_package_data_from_pypi.__name__

        def test(expected_result, *tested_func_args):
            self._generic_test(tested_func, expected_result, *tested_func_args)

        expected = (
            tests_consts.DUMMY_PACKAGE_NAME, [], consts.UNKNOWN_LICENSE_STR)
        func_args = [tests_consts.DUMMY_PACKAGE_NAME]
        test(expected, *func_args)

        package_name = tests_consts.PYPI_PACKAGE_NAME
        func_result = tested_func(package_name)
        self.assertEqual(func_result[0], package_name)
        self.assertTrue(isinstance(func_result[1], list))
        for item in func_result[1]:
            self.assertTrue(isinstance(item, str))
        self.assertEqual(func_result[2], 'MIT')

        expected = (package_name, [], consts.UNKNOWN_LICENSE_STR)
        func_args = [package_name]
        mock_return = {}
        with mock.patch.object(
                versions, mocked_name, return_value=mock_return):
            test(expected, *func_args)

        expected = (package_name, ['1.4'], 'lic')
        func_args = [package_name]
        mock_return = {
            consts.INFO_KEY: {
                consts.INFO_KEY: package_name,
                consts.LICENSE_KEY: 'lic'
            },
            consts.RELEASES_KEY: {'1.4': []}
        }
        with mock.patch.object(
                versions, mocked_name, return_value=mock_return):
            test(expected, *func_args)

        expected = (package_name, [], consts.UNKNOWN_LICENSE_STR)
        func_args = [package_name]
        mock_return = {
            consts.INFO_KEY: {
                consts.INFO_KEY: package_name,
            },
            consts.RELEASES_KEY: {}
        }
        with mock.patch.object(
                versions, mocked_name, return_value=mock_return):
            test(expected, *func_args)

        expected = (package_name, ['1.4', '3.7'], consts.UNKNOWN_LICENSE_STR)
        func_args = [package_name]
        mock_return = {
            consts.INFO_KEY: {
                consts.INFO_KEY: package_name,
                consts.LICENSE_KEY: consts.UNKNOWN_LICENSE_STR
            },
            consts.RELEASES_KEY: {'1.4': [], '3.7': None}
        }
        with mock.patch.object(
                versions, mocked_name, return_value=mock_return):
            test(expected, *func_args)
