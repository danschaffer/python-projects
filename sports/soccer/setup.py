from setuptools import setup, find_packages

setup(
    name="soccer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "soccer=soccer.__main__:main",
        ],
    },
) 