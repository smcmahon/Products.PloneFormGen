from zope.interface import implements
from Products.Five import BrowserView
from Products.PloneFormGen.interfaces import IFormFolderExportView

from Products.GenericSetup.context import TarballExportContext
from Products.GenericSetup.interfaces import IFilesystemExporter

class FormFolderExportView(BrowserView):
    implements(IFormFolderExportView)
    
    def __call__(self):
        """ See IFormFolderExportView.
        """
        ctx = TarballExportContext(self.context)
        
        self.request.RESPONSE.setHeader('Content-type', 'application/x-gzip')
        self.request.RESPONSE.setHeader('Content-disposition',
                           'attachment; filename=%s' % ctx.getArchiveFilename())
        
        # export the structure treating the current form as our root context
        IFilesystemExporter(self.context).export(ctx, 'structure', True)
        
        return ctx.getArchive()
    
