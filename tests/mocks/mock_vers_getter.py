
from dep_vers import vers_getter as mocked_module


class mock_get_json_from_pypi(object):
    def __init__(self, res):
        self.get_json_from_pypi_res = res
        self.original_get_json_from_pypi = mocked_module.get_json_from_pypi

    def __enter__(self):
        mocked_module.get_json_from_pypi = self.mock_get_json_from_pypi_func

    def __exit__(self, exc_type, exc_val, exc_tb):
        mocked_module.get_json_from_pypi = self.original_get_json_from_pypi

    def mock_get_json_from_pypi_func(self, *args, **kwargs):
        return self.get_json_from_pypi_res
