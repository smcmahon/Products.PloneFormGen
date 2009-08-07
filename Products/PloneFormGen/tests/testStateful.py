# Integration tests specific to save-data adapter.
#

import os, sys, email

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.PloneFormGen.tests import pfgtc

from Products.CMFCore.utils import getToolByName

# dummy class
class cd:
    pass

class FakeRequest(dict):
    
    def __init__(self, **kwargs):
        self.form = kwargs

class TestFunctions(pfgtc.PloneFormGenTestCase):
    """ test stateful data adapter """
    
    def afterSetUp(self):
        pfgtc.PloneFormGenTestCase.afterSetUp(self)
        self.folder.invokeFactory('FormFolder', 'ff1')
        self.ff1 = getattr(self.folder, 'ff1')

    def testStateful(self):
        """ test save data adapter action """

        self.ff1.invokeFactory('FormStatefulDataAdapter', 'statify')
        self.failUnless('statify' in self.ff1.objectIds())

        statify = self.ff1.statify
        self.ff1.setActionAdapter( ('statify',) )
        self.assertEqual(self.ff1.actionAdapter, ('statify',))

        self.assertEqual(statify.itemsSaved(), 0)

        request = FakeRequest(topic='test subject', 
                              replyto='test@test.org', 
                              comments='test comments')

        defaultval = statify.getDefaultFieldValue(self.ff1.topic, request)
        self.assertEqual(defaultval, None)

        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( errors, {} )

        self.assertEqual(statify.itemsSaved(), 1)
        res = statify.getStatefulData()
        key = statify.getKey(request)
        self.failUnless(key in res.keys())
        self.failUnless('topic' in res[key].keys())
        self.failUnless(res[key]['topic'] == 'test subject')

        defaultval = statify.getDefaultFieldValue(self.ff1.topic, request)
        self.assertEqual(defaultval, 'test subject')


if  __name__ == '__main__':
    framework()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFunctions))
    return suite

