import unittest
import doctest

from Testing import ZopeTestCase as ztc
from Products.PloneFormGen.tests.pfgtc import PloneFormGenFunctionalTestCase

def test_suite():
    return unittest.TestSuite([

        ztc.FunctionalDocFileSuite(
            'browser.txt', package='Products.PloneFormGen.tests',
            test_class=PloneFormGenFunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        ztc.FunctionalDocFileSuite(
            'browser_serverside_test.txt', package='Products.PloneFormGen.tests',
            test_class=PloneFormGenFunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
