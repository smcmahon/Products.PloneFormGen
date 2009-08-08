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

    def testStatefulSave(self):
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

        errors = self.ff1.fgvalidate(REQUEST=request)
        self.assertEqual( errors, {} )

        self.assertEqual(statify.itemsSaved(), 1)
        statefuldata = statify.getStatefulData()
        key = statify.getKey(request)
        self.failUnless(key in statefuldata.keys())
        self.failUnless('topic' in statefuldata[key].keys())
        self.failUnless(statefuldata[key]['topic'] == 'test subject')

        # Test back-end (with another user)
        self.membership = self.portal.portal_membership
        self.membership.addMember('cesku', 'secret', ['Member'], [])
        self.login('cesku')
        
        cesku_request = FakeRequest(topic='cesku subject', 
                                    replyto='cesku@test.org', 
                                    comments='cesku comments')
                              
        defaultval = statify.getDefaultFieldValue(self.ff1.topic, request)
        self.assertEqual(defaultval, None)

        self.ff1.fgvalidate(REQUEST=cesku_request) # simulate form submit 
        statefuldata = statify.getStatefulData()
        self.failUnless('cesku' in statefuldata.keys())
        self.failUnless('topic' in statefuldata[key].keys())
        self.failUnless(statefuldata['cesku']['topic'] == 'cesku subject')
        self.assertEqual(statify.itemsSaved(), 2)
        
    def testDefaultProviderAnon(self):
        self.ff1.invokeFactory('FormStatefulDataAdapter', 'statify')
        self.failUnless('statify' in self.ff1.objectIds())
        
        statify = self.ff1.statify
        self.ff1.setActionAdapter( ('statify',) )
        self.assertEqual(self.ff1.actionAdapter, ('statify',))
        self.ff1.setDefaultFieldValueProvider( ('statify',) )
        self.assertEqual(self.ff1.defaultFieldValueProvider, ('statify',))

        # Test front-end (anonymously with cookies)
        formfolder_url = self.ff1.absolute_url()
        self.browser.open(formfolder_url)
        self.browser.getControl(name='topic').value = 'test subject 2'
        self.browser.getControl(name='replyto').value = 'test2@test.org'
        self.browser.getControl(name='comments').value = 'test comments 2'
        self.browser.getControl(name='form_submit').click()

        # Re-open the page and check values
        self.browser.open(formfolder_url)
        self.assertEqual(self.browser.getControl(name='topic').value,
                         'test subject 2')
        self.assertEqual(self.browser.getControl(name='replyto').value,
                         'test2@test.org')
        self.assertEqual(self.browser.getControl(name='comments').value,
                         'test comments 2')

if  __name__ == '__main__':
    framework()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFunctions))
    return suite

