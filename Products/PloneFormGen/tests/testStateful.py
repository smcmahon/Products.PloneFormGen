# Integration tests specific to save-data adapter.
#

import os, sys, email

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.PloneFormGen.tests import pfgtc
from Products.PloneFormGen.content.statefulDataAdapter import COOKIENAME

from Products.CMFCore.utils import getToolByName

# dummy class
class cd:
    pass

class FakeRequest(dict):
    
    def __init__(self, **kwargs):
        self.form = kwargs

class TestFunctions(pfgtc.PloneFormGenAnonFunctionalTestCase):
    """ test stateful data adapter """
    
    def afterSetUp(self):
        pfgtc.PloneFormGenAnonFunctionalTestCase.afterSetUp(self)
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

        # Test back-end (authenticated)
        request = FakeRequest(topic='test subject', 
                              replyto='test@test.org', 
                              comments='test comments')

        defaultval = statify.getDefaultFieldValue(self.ff1.topic, request)
        self.assertEqual(defaultval, None)

        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( errors, {} )

        self.assertEqual(statify.itemsSaved(), 1)
        statefuldata = statify.getStatefulData()
        key = statify.getKey(request)
        self.failUnless(key in statefuldata.keys())
        self.failUnless('topic' in statefuldata[key].keys())
        self.failUnless(statefuldata[key]['topic'] == 'test subject')

        defaultval = statify.getDefaultFieldValue(self.ff1.topic, request)
        self.assertEqual(defaultval, 'test subject')

        # Test front-end (anonymously)
        formfolder_url = self.ff1.absolute_url()
        self.browser.open(formfolder_url)
        self.browser.getControl(name='topic').value = 'test subject 2'
        self.browser.getControl(name='replyto').value = 'test2@test.org'
        self.browser.getControl(name='comments').value = 'test comments 2'
        self.browser.getControl(name='form_submit').click()

        statefuldata = statify.getStatefulData()
        self.assertEqual(statify.itemsSaved(), 2)

        setcookie = self.browser.headers.get('set-cookie')
        import Cookie
        c = Cookie.SmartCookie()
        c.load(setcookie)
        self.failUnless(COOKIENAME in c.keys())
        key = c[COOKIENAME].value
        self.failUnless(key in statefuldata.keys())
        self.failUnless('topic' in statefuldata[key].keys())
        self.failUnless(statefuldata[key]['topic'] == 'test subject 2')

        # from base64 import b64encode

        # Re-open the page and check values
        #self.browser.addHeader('cookie', '%s=%s' % (COOKIENAME, b64encode(key)))
        #self.browser.open(formfolder_url)

        #self.assertEqual(self.browser.getControl(name='topic').value,
        #                 'test subject 2')
        #self.assertEqual(self.browser.getControl(name='replyto').value,
        #                 'test2@test.org')
        #self.assertEqual(self.browser.getControl(name='comments').value,
        #                 'test comments 2')

if  __name__ == '__main__':
    framework()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFunctions))
    return suite

