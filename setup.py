from setuptools import setup, find_packages

setup(
    name="climesync",
    version="0.1",
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
