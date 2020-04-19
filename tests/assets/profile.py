# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2008 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://babel.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://babel.edgewall.org/log/.

"""Reading and writing of files in the ``gettext`` PO (portable object)
format.

:see: `The Format of PO Files
       <http://www.gnu.org/software/gettext/manual/gettext.html#PO-Files>`_
"""

from datetime import date, datetime
import os
import re

from babel import __version__ as VERSION
from babel.messages.catalog import Catalog, Message
from babel.util import set, wraptext, LOCALTZ

__all__ = ['read_po', 'write_po']
__docformat__ = 'restructuredtext en'

def unescape(string):
    r"""Reverse `escape` the given string.

    >>> print unescape('"Say:\\n  \\"hello, world!\\"\\n"')
    Say:
      "hello, world!"
    <BLANKLINE>

    :param string: the string to unescape
    :return: the unescaped string
    :rtype: `str` or `unicode`
    """
    return string[1:-1].replace('\\\\', '\\') \
                       .replace('\\t', '\t') \
                       .replace('\\r', '\r') \
                       .replace('\\n', '\n') \
                       .replace('\\"', '\"')
