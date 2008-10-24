from zope.interface import implements
from Products.Five import BrowserView
from Products.PloneFormGen.interfaces import IFormFolderExportView
from Products.GenericSetup.tests.common import DummyExportContext

class FormFolderExportView(BrowserView):
    implements(IFormFolderExportView)
    
    def __call__(self):
        """ See IFormFolderExportView.
        """
        return DummyExportContext(self.context)
        

        