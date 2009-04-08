from zope.interface import Interface, Attribute

class IPloneFormGenThanksPage(Interface):
    """thanksPage interface
    """
    
    meta_type = Attribute("archetypes meta type")
    """
    Must match GS type declaration.
    """

    
