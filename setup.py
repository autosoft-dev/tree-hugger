import pathlib
from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()


setup(
name='tree-hugger',
description="A light-weight, Extendable, high level, universal code parser built on top of tree-sitter",
long_description=README,
long_description_content_type="text/markdown",
url="https://github.com/autosoft-dev/tree-hugger",
author="CodistAI",
author_email="shubhadeep@cdist-ai.com",
include_package_data=True,
license="MIT",
classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
],
version="0.4.0",
packages=find_packages(exclude=("tests",)),
install_requires=["tree-sitter", "pygit2", "pytest", "PyYAML"],
entry_points = {
    'console_scripts': ['create_libs=tree_hugger.cli.create_libs:main'],
},
)
