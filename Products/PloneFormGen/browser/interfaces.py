from zope.interface import Interface
# Holding file for specifying new content type interfaces
from plone.theme.interfaces import IDefaultPloneLayer

class IfolderEditView(Interface):
    """ this is a marker to check the new browser stuff is installed """

class IPloneFormGenSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
       If you need to register a viewlet only for the
       "ecupublic" theme, this interface must be its layer
       (in theme/viewlets/configure.zcml).

       NB: This theme create two skins ecupublic and ecuadmin.
    """


    
