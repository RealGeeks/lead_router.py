import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ['--cov-config', '.coveragerc', '--cov', 'leadrouter']

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

setup(
    name='leadrouter',
    version='0.0.1',

    description='Python Client to lead_router REST Receiver',
    url='https://github.com/RealGeeks/lead_router.py',

    author='Igor Sobreira',
    author_email='igor@realgeeks.com',

    license='Closed Source',

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],

    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    install_requires=['requests', 'beanstalkc', 'click', 'pyyaml'],
    tests_require=['pytest', 'pytest-cov', 'mock', 'httpretty'],

    cmdclass={
        'test': PyTest,
    },

    entry_points={
        'console_scripts': [
            'leadrouter = leadrouter.cmd:cmd',
        ],
    },
)
