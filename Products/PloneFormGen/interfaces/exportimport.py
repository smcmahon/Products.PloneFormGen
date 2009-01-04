from zope.interface import Interface

class IFormFolderExportView(Interface):
    """ Browser view registered for IPloneFormGenForm
        which can be called when requesting a placeful
        export of the give form's configuration.
    """
    def __call__():
        """ Returns export data to the client
        """
