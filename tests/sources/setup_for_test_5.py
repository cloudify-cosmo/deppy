
from setuptools import setup

install_requires = [
    'joblib>0.9.4',
    'requests',
    'pipdeptree==0.6.0',
]

setup(
    name='deppy',
    version='1.0',
    author='yariv',
    author_email='yariv@gigaspaces.com',
    packages=['dep_vers', 'tests'],
    description='Deppy is a dependencies management tool for '
                'projects/packages.\n\n'

                'It is used to seek for updates for your project/package '
                'dependencies, or to show the dependencies tree for an '
                'installed package, with details about each package in '
                'the dependencies tree, including versions conflicts, and '
                'versions available according to the requirements of the '
                'main package and its dependencies.',
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'deppy = dep_vers.dep_vers_project:main'
        ]
    }
)
