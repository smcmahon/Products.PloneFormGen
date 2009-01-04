from zope.schema import Bytes, Bool
from zope.interface import Interface
from Products.PloneFormGen import PloneFormGenMessageFactory as _

class IImportSchema(Interface):
    """Schema for form import.
    """
    upload = Bytes(
        title=_(u'Upload'),
        required=True)
    
    purge = Bool(
        title=_(u'Remove Existing Form Items?'),
        default=False,
        required=False)
    

class IFormFolderImportView(Interface):
    """Interface for import form
    """
