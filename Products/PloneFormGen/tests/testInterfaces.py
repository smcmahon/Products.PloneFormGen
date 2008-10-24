#
# Integration tests for interaction with GenericSetup infrastructure
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from zope.interface.verify import verifyObject, verifyClass
from Products.PloneFormGen.tests import pfgtc
from Products.PloneFormGen import interfaces, browser


class TestFormGenInterfaces(pfgtc.PloneFormGenTestCase):
    """ Some boilerplate-ish tests to confirm that that classes
        and instances confirm to the interface contracts intended.
    """
    def afterSetUp(self):
        pfgtc.PloneFormGenTestCase.afterSetUp(self)
        
        # add form folder for use in tests
        self.folder.invokeFactory('FormFolder', 'ff1')
    
    def testBrowserViewClassInterfaces(self):
        """Some basic boiler plate testing of interfaces and classes"""
        # verify IFormFolderExportView
        self.failUnless(interfaces.IFormFolderExportView.implementedBy(browser.FormFolderExportView))
        self.failUnless(verifyClass(interfaces.IFormFolderExportView, browser.FormFolderExportView))
    
    def testBrowserViewObjectsVerify(self):
        # verify views are objects of the expected class, verified implementation
        form_folder_export = self.folder.ff1.restrictedTraverse('@@export-form-folder')
        self.failUnless(isinstance(form_folder_export, browser.FormFolderExportView))
        self.failUnless(verifyObject(interfaces.IFormFolderExportView, form_folder_export))
    

if  __name__ == '__main__':
    framework()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFormGenInterfaces))
    return suite
