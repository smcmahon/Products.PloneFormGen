import unittest
import doctest
from plone.testing import layered

from Products.PloneFormGen.tests.pfgtc import PFG_FUNCTIONAL_TESTING

testfiles = (
    'browser.txt',
    'attachment.txt',
    'ssl.txt',
    'serverside_field.txt',
    '../dollarReplace.py',
)

def test_suite():
    return unittest.TestSuite([

        layered(doctest.DocFileSuite(
            f, package='Products.PloneFormGen.tests',
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
        layer=PFG_FUNCTIONAL_TESTING)

            for f in testfiles
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
