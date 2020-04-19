"""
If you know what an abstract syntax tree (AST) is, you'll see that this module
is pretty much that. The classes represent syntax elements like functions and
imports.

This is the "business logic" part of the parser. There's a lot of logic here
that makes it easier for Jedi (and other libraries to deal with a Python syntax
tree.

By using `get_code` on a module, you can get back the 1-to-1 representation of
the input given to the parser. This is important if you are using refactoring.

The easiest way to play with this module is to use :class:`parsing.Parser`.
:attr:`parsing.Parser.module` holds an instance of :class:`Module`:

>>> from jedi._compatibility import u
>>> from jedi.parser import Parser, load_grammar
>>> parser = Parser(load_grammar(), u('import os'), 'example.py')
>>> submodule = parser.module
>>> submodule
<Module: example.py@1-1>

Any subclasses of :class:`Scope`, including :class:`Module` has an attribute
:attr:`imports <Scope.imports>`:

>>> submodule.imports
[<ImportName: import os@1,0>]

See also :attr:`Scope.subscopes` and :attr:`Scope.statements`.
"""
import os
import re
from inspect import cleandoc
from itertools import chain
import textwrap

from jedi._compatibility import (Python3Method, encoding, is_py3, utf8_repr,
                                 literal_eval, use_metaclass, unicode)
from jedi import cache


def is_node(node, *symbol_names):
    try:
        type = node.type
    except AttributeError:
        return False
    else:
        return type in symbol_names
