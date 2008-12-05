from zope.interface import implements
from zope.formlib import form

from Products.Five import BrowserView
from Products.Five.formlib import formbase

from Products.PloneFormGen import interfaces
from Products.PloneFormGen import PloneFormGenMessageFactory as _

from Products.GenericSetup.context import TarballExportContext, TarballImportContext
from Products.GenericSetup.interfaces import IFilesystemExporter, IFilesystemImporter

class FormFolderExportView(BrowserView):
    implements(interfaces.IFormFolderExportView)
    
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
    

class PACKAGE_HOME(formbase.Form):
    """The formlib class for importing of exported PFG form folders
    """
    implements(interfaces.IPACKAGE_HOME)
    
    form_fields = form.Fields(interfaces.IImportSchema)
    status = errors = None
    prefix = 'form'
    
    @form.action(_(u"import"))
    def action_import(self, action, data):
        ctx = TarballImportContext(self.context, data['upload'])
        IFilesystemImporter(self.context).import_(ctx, 'structure', True)
    

    