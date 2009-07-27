import os, os.path
import unittest
import doctest

from Testing import ZopeTestCase as ztc
from Products.PloneFormGen.tests.pfgtc import PloneFormGenFunctionalTestCase


testfiles = os.listdir(os.path.dirname(__file__))
testfiles = [n for n in testfiles if n.endswith('.txt')]

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
