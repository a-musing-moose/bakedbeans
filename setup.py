from setuptools import setup


setup(
    name='bakedbeans',
    version='0.1',
    author='Jonathan Moss',
    author_email='jmoss@commoncode.io',
    packages=['bakedbeans'],
    # note the below *must* be kept in sync with requirements.txt
    install_requires=[
        'click~=6.7',
        'Flask~=0.12.2',
        'jsonschema~=2.6.0'
    ],
    description='Canned response HTTP server',
    classifiers=(
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3.6',
    ),
    entry_points='''
        [console_scripts]
        baked=bakedbeans.cli:main
    '''
)
