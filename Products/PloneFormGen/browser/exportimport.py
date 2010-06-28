from zope.interface import implements
from zope.formlib import form
from zope.component import getMultiAdapter

from Products.Five import BrowserView
try:
    from Products.Five.formlib import formbase
except: # Zope2.13 compatibility
    from five.formlib import formbase

from Products.statusmessages.interfaces import IStatusMessage

from Products.PloneFormGen import interfaces
from Products.PloneFormGen import PloneFormGenMessageFactory as _

from Products.GenericSetup.context import TarballExportContext, TarballImportContext
from Products.GenericSetup.interfaces import IFilesystemExporter, IFilesystemImporter

class FormFolderExportView(BrowserView):
    """See ..interfaces.exportimport.IFormFolderExportView
    """
    implements(interfaces.IFormFolderExportView)
    
    def __call__(self):
        """See ..interfaces.exportimport.IFormFolderExportView.__call__
        """
        ctx = TarballExportContext(self.context)
        
        self.request.RESPONSE.setHeader('Content-type', 'application/x-gzip')
        self.request.RESPONSE.setHeader('Content-disposition',
                           'attachment; filename=%s' % ctx.getArchiveFilename())
        
        # export the structure treating the current form as our root context
        IFilesystemExporter(self.context).export(ctx, 'structure', True)
        
        return ctx.getArchive()
    

class FormFolderImportView(formbase.Form):
    """The formlib class for importing of exported PFG form folders
    """
    implements(interfaces.IFormFolderImportView)
    
    form_fields = form.Fields(interfaces.IImportSchema)
    status = errors = None
    prefix = 'form'
    
    @form.action(_(u"import"))
    def action_import(self, action, data):
        if data.get('purge', False) == True:
            # user has requested removal of existing fields
            self.context.manage_delObjects(ids=self.context.objectIds())
        
        ctx = TarballImportContext(self.context, data['upload'])
        IFilesystemImporter(self.context).import_(ctx, 'structure', True)
        
        message = _(u'Form imported.')
        IStatusMessage(self.request).addStatusMessage(message, type='info')
        
        url = getMultiAdapter((self.context, self.request), name='absolute_url')()
        self.request.response.redirect(url)
        
        return ''
    

