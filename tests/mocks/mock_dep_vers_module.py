
from dep_vers import dep_vers_module as mocked_module


class mock_get_dependencies_from_file(object):
    def __init__(self, res, return_arg=False):
        self.get_dependencies_from_file_return_arg = return_arg
        self.get_dependencies_from_file_res = res
        self.original_get_dependencies_from_file = mocked_module.get_dependencies_from_file

    def __enter__(self):
        mocked_module.get_dependencies_from_file = self.mock_get_dependencies_from_file_func

    def __exit__(self, exc_type, exc_val, exc_tb):
        mocked_module.get_dependencies_from_file = self.original_get_dependencies_from_file

    def mock_get_dependencies_from_file_func(self, *args, **kwargs):
        if self.get_dependencies_from_file_return_arg:
            return self.get_dependencies_from_file_res[0], args[0]
        return self.get_dependencies_from_file_res


class mock_build_dep_tree(object):
    def __init__(self, res):
        self.original_build_dep_tree = mocked_module.build_dep_tree
        self.build_dep_tree_res = res

    def __enter__(self):
        mocked_module.build_dep_tree = self.mock_build_dep_tree_func

    def mock_build_dep_tree_func(self, *args, **kwargs):
        return self.build_dep_tree_res

    def __exit__(self, exc_type, exc_val, exc_tb):
        mocked_module.build_dep_tree = self.original_build_dep_tree
