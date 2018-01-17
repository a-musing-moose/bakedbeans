import io
import os

from setuptools import setup


NAME = 'bakedbeans'

here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

about = {}
with open(os.path.join(here, NAME, '__version__.py')) as f:
    exec(f.read(), about)

setup(
    name='bakedbeans',
    version=about['__version__'],
    author='Jonathan Moss',
    author_email='jmoss@commoncode.io',
    url='https://github.com/a-musing-moose/bakedbeans',
    license='MIT',
    packages=[NAME],
    install_requires=[
        'click~=6.7',
        'Flask~=0.12.2',
        'jsonschema~=2.6.0'
    ],
    description='Canned response HTTP server',
    long_description=long_description,
    classifiers=(
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3.6',
    ),
    entry_points={
        'console_scripts': ['baked=bakedbeans.cli:main'],
    }
)
