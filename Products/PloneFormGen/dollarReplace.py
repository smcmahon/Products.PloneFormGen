#!/usr/bin/env python
# encoding: utf-8
"""
dollarReplace.py

Created by Steve McMahon on 2008-12-11.
Copyright (c) 2008, Steve McMahon. Distribution allowed under GPL2.
"""

import re

# regular expression for dollar-sign variable replacement.
# we want to find ${identifier} patterns
dollarRE = re.compile(r"\$\{(.+?)\}")

class DollarVarReplacer(object):
    """ 
    Initialize with a dictionary, then self.sub returns a string
    with all ${key} substrings replaced with values looked
    up from the dictionary.

    >>> from Products.PloneFormGen import dollarReplace

    >>> adict = {'one':'two', '_two':'three', '.two':'four'}
    >>> dvr = dollarReplace.DollarVarReplacer( adict )

    >>> dvr.sub('one one')
    'one one'

    >>> dvr.sub('one ${one}')
    'one two'

    >>> dvr.sub('one ${two}')
    'one ???'

    Skip any key beginning with _ or .
    >>> dvr.sub('one ${_two}')
    'one ???'

    >>> dvr.sub('one ${.two}')
    'one ???'

    """

    def __init__(self, adict):
        self.adict = adict

    def sub(self, s):
        return dollarRE.sub(self.repl, s)

    def repl(self, mo):
        key = mo.group(1)
        if key and key[0] not in ['_','.']:
            try:
                return self.adict[mo.group(1)]
            except KeyError:
                pass
        return '???'            

if __name__ == '__main__':
    import doctest
    doctest.testfile(__file__, verbose=True)