
from setuptools import setup


setup(
    name='deppy',
    version='1.0',
    author='yariv',
    author_email='yariv@gigaspaces.com',
    packages=['deppy', 'tests'],
    description='Deppy is a dependencies management tool for '
                'projects/packages.\n\n'

                'It is used to seek for updates for your project/package '
                'dependencies, or to show the dependencies tree for an '
                'installed package, with details about each package in '
                'the dependencies tree, including versions conflicts, and '
                'versions available according to the requirements of the '
                'main package and its dependencies.',
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'deppy = deppy.deppy:main'
        ]
    }
)
