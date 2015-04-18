#
# Test PloneFormGen event-handler functionality
#

from Products.PloneFormGen.tests import pfgtc


class TestAdapterPaste(pfgtc.PloneFormGenTestCase):
    """Ensure content types can be created and edited"""

    adapterTypes = (
        'FormSaveDataAdapter',
        'FormMailerAdapter',
        'FormCustomScriptAdapter',
    )

    def setUp(self):
        pfgtc.PloneFormGenTestCase.setUp(self)
        self.folder.invokeFactory('FormFolder', 'ff1')
        self.ff1 = getattr(self.folder, 'ff1')

    def testPastedAdaptersAreActive(self):
        self.loginAsPortalOwner() # creating a FormCustomScriptAdapter requires elevated permissions
        for f in self.adapterTypes:
            fname = "%s1" % f
            self.ff1.invokeFactory(f, fname)
            f1 = getattr(self.ff1, fname)
            copy = self.ff1.manage_copyObjects(fname)
            new_id = self.ff1.manage_pasteObjects(copy)[0]['new_id']

            self.failUnless(new_id in self.ff1.getActionAdapter())

    def testActiveAdaptersNotDuplicatedOnFormCopy(self):
        self.loginAsPortalOwner()
        copy = self.folder.manage_copyObjects('ff1')
        new_id = self.folder.manage_pasteObjects(copy)[0]['new_id']
        ff2 = getattr(self.folder, new_id)
        active_adapters = ff2.getActionAdapter()
        self.assertEqual(active_adapters, ('mailer',))

    def testTempFactoryAdaptersNotActivatedOnForm(self):
        self.loginAsPortalOwner() # creating a FormCustomScriptAdapter requires elevated permissions
        adapter_count = len(self.ff1.getActionAdapter())
        for f in self.adapterTypes:
            temp_adapter = self.ff1.restrictedTraverse('portal_factory/%s/%s_tmp' % (f,f))
        # temporary objects shouldn't be active on the form folder
        self.assertEqual(adapter_count, len(self.ff1.getActionAdapter()))
