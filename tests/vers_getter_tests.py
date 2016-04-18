
import testtools

from dep_vers import vers_getter as tested_module
from helpers import cmp_elements
from mocks import mock_vers_getter


DUMMY_PACKAGE_NAME = 'dummy_package_that_doesnt_exist_065591'


class TestVersGetter(testtools.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestVersGetter, self).__init__(*args, **kwargs)
        self.func = None

    def _generic_test(self, expected, *args):
        self.assertTrue(cmp_elements(expected, self.func(*args)))

    def test_compare_loose_versions_old(self):

        self.func = func = tested_module.compare_loose_versions
        t = self._generic_test

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

        t(0, '1', '1')

    def test_compare_loose_versions_new(self):

        self.func = tested_module.compare_loose_versions
        t = self._generic_test

        t(True, '1.2', '1.3', '<')
        t(False, '1.2', '1.3', '>')
        t(True, '1.2', '1.3', '<=')
        t(False, '1.2', '1.3', '>=')
        t(False, '1.2', '1.3', '==')
        t(True, '1.2', '1.3', '!=')

        t(False, '1.4', '1.3', '<')
        t(True, '1.4', '1.3', '>')
        t(False, '1.4', '1.3', '<=')
        t(True, '1.4', '1.3', '>=')
        t(False, '1.4', '1.3', '==')
        t(True, '1.4', '1.3', '!=')

        t(False, '1.3', '1.3', '<')
        t(False, '1.3', '1.3', '>')
        t(True, '1.3', '1.3', '<=')
        t(True, '1.3', '1.3', '>=')
        t(True, '1.3', '1.3', '==')
        t(False, '1.3', '1.3', '!=')

    def test_split_required_versions(self):

        self.func = tested_module.split_required_versions
        t = self._generic_test

        ver_str = '7.5'
        for op in tested_module.OPS:
            t((ver_str, op), op + ver_str)
        t((ver_str, ''), ver_str)

    def test_filter_newer_versions(self):

        self.func = tested_module.filter_newer_versions
        t = self._generic_test

        t(['1', '2', '3'], ['1', '2', '3'], '')
        t(['1', '2', '3'], ['1', '2', '3'], '0')
        t(['2', '3'], ['1', '2', '3'], '1')
        t(['3'], ['1', '2', '3'], '2')
        t([], ['1', '2', '3'], '3')
        t(['1', '2', '3'], ['3', '2', '1'], '0')
        t(['2', '3'], ['3', '2', '1'], '1')
        t(['3'], ['3', '2', '1'], '2')
        t([], ['3', '2', '1'], '3')

        t(['1.2.2', '1.22.2', '3', '3.2'],
          ['3', '1.1', '1.2', '1.2.2', '1.22.2', '3.2'],
          '1.2.1'
          )
        t(['1.2.2', '1.22.2', '3', '3.2', '1.2.1.1'],
          ['3', '1.1', '1.2', '1.2.2', '1.22.2', '3.2', '1.2.1', '1.2.1.1'],
          '1.2.1'
          )
        t(['1.22.2', '3', '3.2'],
          ['3', '1.1', '1.2', '1.2.2', '1.22.2', '3.2'],
          '1.21.1'
          )

        t([], [], '')

        t(['3'], ['1', '2', '3'], '2')

    def test_get_new_versions_available(self):

        self.func = tested_module.get_new_versions_available
        t = self._generic_test

        t([{tested_module.PACKAGE_KEY: 'a', tested_module.REQUIRE_KEY: '2', tested_module.NEW_VERS_KEY: ['3']}],
          {'a': ['2']},
          {'a': ['1', '3']}
          )
        t([{tested_module.PACKAGE_KEY: 'a', tested_module.REQUIRE_KEY: '2', tested_module.NEW_VERS_KEY: []}],
          {'a': ['2']},
          {'a': ['2']}
          )
        t([{tested_module.PACKAGE_KEY: 'a', tested_module.REQUIRE_KEY: '2', tested_module.NEW_VERS_KEY: ['3']}],
          {'a': ['2']},
          {'a': ['1', '3'], 'b': ['4', '5']}
          )
        t([{tested_module.PACKAGE_KEY: 'a', tested_module.REQUIRE_KEY: '2', tested_module.NEW_VERS_KEY: ['3']}, {tested_module.PACKAGE_KEY: 'b', tested_module.REQUIRE_KEY: '3', tested_module.NEW_VERS_KEY: ['4', '5']}],
          {'a': ['2'], 'b': ['3']},
          {'a': ['1', '3'], 'b': ['4', '5']}
          )
        t([{tested_module.PACKAGE_KEY: 'a', tested_module.REQUIRE_KEY: '0.5', tested_module.NEW_VERS_KEY: ['1', '3']}, {tested_module.PACKAGE_KEY: 'a', tested_module.REQUIRE_KEY: '3', tested_module.NEW_VERS_KEY: []}, {tested_module.PACKAGE_KEY: 'a', tested_module.REQUIRE_KEY: '2', tested_module.NEW_VERS_KEY: ['3']}],
          {'a': ['2', '3', '0.5']},
          {'a': ['1', '3'], 'b': ['4', '5']}
          )
        t([{tested_module.PACKAGE_KEY: 'a', tested_module.REQUIRE_KEY: '2', tested_module.NEW_VERS_KEY: ['4']}, {tested_module.PACKAGE_KEY: 'b', tested_module.REQUIRE_KEY: '3', tested_module.NEW_VERS_KEY: []}],
          {'a': ['2'], 'b': ['3']},
          {'a': ['1', '4'], 'b': ['2', '1']}
          )
        t([],
          {'c': ['2']},
          {'a': ['1', '3'], 'b': ['4', '5']}
          )
        t([{tested_module.PACKAGE_KEY: 'a', tested_module.REQUIRE_KEY: '7', tested_module.NEW_VERS_KEY: []}],
          {'a': ['7']},
          {'a': ['1', '3'], 'b': ['4', '5']}
          )
        t([],
          {},
          {'a': ['1', '3'], 'b': ['4', '5']}
          )
        t([],
          {'a': ['7']},
          {}
          )
        t([],
          {},
          {}
          )

    def test_get_json_from_pypi(self):
        self.func = tested_module.get_json_from_pypi
        t = self._generic_test

        t(None, DUMMY_PACKAGE_NAME)

        package_name = 'pika'
        res = self.func(package_name)
        self.assertEqual(str(res[tested_module.INFO_KEY][tested_module.NAME_KEY]).lower(), package_name.lower())

    def test_get_versions_from_pypi(self):

        self.func = tested_module.get_versions_from_pypi
        t = self._generic_test

        t((DUMMY_PACKAGE_NAME, [], tested_module.UNKNOWN_LICENSE_STR), DUMMY_PACKAGE_NAME)

        package_name = 'pika'
        res = self.func(package_name)
        self.assertEqual(res[0], package_name)
        self.assertTrue(isinstance(res[1], list))
        for item in res[1]:
            self.assertTrue(isinstance(item, str))
        self.assertEqual(res[2], 'BSD')

        with mock_vers_getter.mock_get_json_from_pypi({}):
            t((package_name, [], tested_module.UNKNOWN_LICENSE_STR), package_name)

        with mock_vers_getter.mock_get_json_from_pypi({
            tested_module.INFO_KEY: {
                tested_module.INFO_KEY: package_name,
                tested_module.LICENSE_KEY: 'lic'
            },
            tested_module.RELEASES_KEY: {'1.4': []}
        }):
            t((package_name, ['1.4'], 'lic'), package_name)

        with mock_vers_getter.mock_get_json_from_pypi({
            tested_module.INFO_KEY: {
                tested_module.INFO_KEY: package_name,
            },
            tested_module.RELEASES_KEY: {}
        }):
            t((package_name, [], tested_module.UNKNOWN_LICENSE_STR), package_name)

        with mock_vers_getter.mock_get_json_from_pypi({
            tested_module.INFO_KEY: {
                tested_module.INFO_KEY: package_name,
                tested_module.LICENSE_KEY: tested_module.UNKNOWN_LICENSE_STR
            },
            tested_module.RELEASES_KEY: {'1.4': [], '3.7': None}
        }):
            t((package_name, ['1.4', '3.7'], tested_module.UNKNOWN_LICENSE_STR), package_name)

    def test_get_versions_from_pip(self):
        self.func = tested_module.get_versions_from_pip
        t = self._generic_test
        t((DUMMY_PACKAGE_NAME, [], tested_module.UNKNOWN_LICENSE_STR), DUMMY_PACKAGE_NAME)

        package_name = 'pika'
        res = self.func(package_name)
        self.assertEqual(res[0], package_name)
        self.assertTrue(isinstance(res[1], list))
        for item in res[1]:
            self.assertTrue(isinstance(item, str))
        self.assertEqual(res[2], tested_module.UNKNOWN_LICENSE_STR)
