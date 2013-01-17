from zope.interface import Interface
from zope.schema import Bytes, Bool

from Products.PloneFormGen import PloneFormGenMessageFactory as _

class IFormFolderExportView(Interface):
    """ Browser view registered for IPloneFormGenForm
        which can be called when requesting a placeful
        export of the give form's configuration.
    """
    def __call__():
        """ Returns export data to the client
        """

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
