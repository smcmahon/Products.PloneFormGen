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

    def testConditionalFieldsets(self):
        self.ff1.invokeFactory('FormSelectionField', 'question', 
                               title='Do you want to see fieldset 1?')
        question = self.ff1.question
        question.setFgVocabulary(['Yes', 'No', ])

        self.ff1.invokeFactory('FieldsetFolder', 'fieldset1')
        fieldset1 = self.ff1.fieldset1
        fieldset1.setConditionalField(question.getId())
        fieldset1.setConditionalFieldValue('Yes')

        fieldset1.invokeFactory('FormStringField', 'fieldset1question',
                                title='How do you like fieldset 1?')
        fieldset1question = fieldset1.fieldset1question

        request = FakeRequest()
        activeids = self.ff1.activeFieldIds(request)
        self.failUnless('question' in activeids)
        self.failIf('fieldset1' in activeids)
        self.failIf('fieldset1question' in activeids)
        self.failIf(self.ff1.canSubmitForm(request))

        request = FakeRequest(question='Yes', form_continue='Continue')
        activeids = self.ff1.activeFieldIds(request)
        self.failUnless('fieldset1' in activeids)
        self.failUnless('fieldset1question' in activeids)
        self.failUnless(self.ff1.canSubmitForm(request))

        request = FakeRequest(question='No', form_continue='Continue')
        activeids = self.ff1.activeFieldIds(request)
        self.failIf('fieldset1' in activeids)
        self.failIf('fieldset1question' in activeids)
        self.failUnless(self.ff1.canSubmitForm(request))

        # Visit the form and check conditional fieldsets are hidden
        #formfolder_url = self.ff1.absolute_url()
        #self.browser.open(formfolder_url)

        #self.browser.getControl(name='topic').value = 'test subject 2'
        #self.browser.getControl(name='replyto').value = 'test2@test.org'
        #self.browser.getControl(name='comments').value = 'test comments 2'
        #self.browser.getControl(name='form_submit').click()

        # Re-open the page and check values
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

