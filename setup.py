import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="climesync",
    version="0.1.0",
    author="OSU Open Source Lab",
    author_email="support@osuosl.org",
    url="https://github.com/osuosl/climesync",
    license="Apache Version 2.0",
    description="Climesync - CLI Frontend for the OSUOSL TimeSync API",
    long_description=read("README.md"),

    keywords="timesync pymesync cli frontend",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 2.7"
    ],

    packages=find_packages(),
    install_requires = [
        "pymesync"
    ],
    scripts=["climesync.py"],
    entry_points={
        "console_scripts": [
            "climesync = climesync:main"
        ]
    },
    test_suite="testing"
)
