
import os


DUMMY_PACKAGE_NAME = 'dummy_package_that_does_not_exist_065591'
PYPI_PACKAGE_NAME = 'pip'
LOCAL_PACKAGE_NAME = 'testtools'
DUMMY_FILE_NAME = 'dummy_file_that_does_not_exist_065591'
SETUP_FILE_NAME = 'setup_for_test_find_files_in_path.py'
DIR_NAME = 'dir_for_test_find_files_in_path'
DUMMY_DIR_NAME = 'dummy_dir_that_does_not_exist_065591'

PATH_KEY = 'path'
NAME_KEY = 'name'
REQUIRE_KEY = 'require'

RESOURCES_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'resources')
