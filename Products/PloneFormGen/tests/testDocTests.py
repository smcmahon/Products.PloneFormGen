import unittest
import doctest

from Testing import ZopeTestCase as ztc
from Products.PloneFormGen.tests.pfgtc import PloneFormGenFunctionalTestCase
from Products.PloneFormGen import HAS_PLONE30

testfiles = (
    'browser.txt',
    'ssl.txt',
    '../dollarReplace.py',
)

def test_suite():
    return unittest.TestSuite([

        ztc.FunctionalDocFileSuite(
            f, package='Products.PloneFormGen.tests',
            test_class=PloneFormGenFunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS)

            for f in testfiles
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
