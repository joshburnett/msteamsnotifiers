import re
from setuptools import setup

with open('README.md') as readme:
    long_description = readme.read()


def get_version(filename='msteamsnotifiers.py'):
    """ Extract version information stored as a tuple in source code """
    version = ''
    with open(filename, 'r') as fp:
        for line in fp:
            m = re.search("__version__ = '(.*)'", line)
            if m is not None:
                version = m.group(1)
                break
    return version


# What packages are required for this module to be executed?
REQUIRED = [
    'pymsteams',
    'friendly_traceback',
]

setup(
    name="msteamsnotifiers",
    version=get_version(),

    py_modules=["msteamsnotifiers"],

    install_requires=REQUIRED,

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],

    # metadata for upload to PyPI
    author="Josh Burnett",
    author_email="github@burnettsonline.org",
    description="Decorators for automatically notifying an MS Teams channel of events",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords="Microsoft Teams msteams channel notify message post",
    url="https://github.com/joshburnett/msteamsnotifiers",
)
