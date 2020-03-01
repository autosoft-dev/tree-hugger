from distutils.core import setup
from tree_hugger import __version__


setup(
name='TreeHugger',
version=__version__,
packages=['tree_hugger',],
entry_points = {
    'console_scripts': ['create_libs=tree_hugger.cli.create_libs:main'],
},
)
