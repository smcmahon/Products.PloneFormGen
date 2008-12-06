#
# Test PloneFormGen initialisation and set-up
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

        
class TestAdapterPaste(pfgtc.PloneFormGenTestCase):
    """Ensure content types can be created and edited"""

    adapterTypes = (
        'FormSaveDataAdapter',
        'FormMailerAdapter',
    )

    def afterSetUp(self):
        pfgtc.PloneFormGenTestCase.afterSetUp(self)
        self.folder.invokeFactory('FormFolder', 'ff1')
        self.ff1 = getattr(self.folder, 'ff1')
    
    def testPastedAdaptersAreActive(self):
        for f in self.adapterTypes:
            fname = "%s1" % f
            self.ff1.invokeFactory(f, fname)
            f1 = getattr(self.ff1, fname)
            copy = self.ff1.manage_copyObjects(fname)
            new_id = self.ff1.manage_pasteObjects(copy)[0]['new_id']
            
            self.failUnless(new_id in self.ff1.getActionAdapter())
    

if  __name__ == '__main__':
    framework()

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAdapterPaste))
    return suite
